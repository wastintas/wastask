#!/usr/bin/env python3
"""
WasTask CLI - Comando principal para análise de PRDs
Uso: python wastask_cli.py analyze-prd <arquivo_prd>
"""
import asyncio
import sys
import os
from pathlib import Path
import json
import click
from datetime import datetime

# Adicionar path atual
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.progress import track
import time

# Imports dos agentes
from agents.analysis.prd_analyzer import prd_analyzer
from ai_engine.intelligent_task_generator import IntelligentTaskGenerator
from database import create_connection, init_database

console = Console()

@click.group()
def cli():
    """WasTask - AI-powered PRD to Tasks Generator"""
    pass

@cli.command()
@click.argument('prd_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output format: json, db, console', default='console')
@click.option('--project-name', help='Override project name')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
async def analyze_prd(prd_file, output, project_name, verbose):
    """Analisar PRD e gerar tarefas automaticamente"""
    
    console.print(Panel(
        f"[bold blue]🚀 WasTask PRD Analyzer[/bold blue]\n\n"
        f"[cyan]File: {prd_file}[/cyan]\n"
        f"[yellow]Analyzing and generating tasks automatically...[/yellow]",
        expand=False
    ))
    
    try:
        # 1. Ler arquivo PRD
        console.print("📄 Reading PRD file...")
        prd_content = Path(prd_file).read_text(encoding='utf-8')
        
        if verbose:
            console.print(f"   • File size: {len(prd_content)} characters")
            console.print(f"   • Estimated reading time: {len(prd_content.split())} words")
        
        # 2. Análise completa do PRD
        console.print("🔍 Analyzing PRD with AI...")
        analysis_result = await prd_analyzer.analyze_prd(prd_content)
        
        # 3. Gerar tarefas inteligentes
        console.print("🧠 Generating intelligent tasks...")
        task_generator = IntelligentTaskGenerator()
        
        # Usar o nome do projeto ou override
        final_project_name = project_name or analysis_result.project_name
        
        # Criar descrição baseada na análise
        project_description = f"""
{analysis_result.project_description}

Complexity: {analysis_result.complexity_score:.1f}/10
Timeline: {analysis_result.estimated_timeline}
Features: {len(analysis_result.features)}
Story Points: {sum(f.estimated_effort for f in analysis_result.features)}

Tech Stack:
{chr(10).join([f"- {tech.category}: {tech.technology} v{tech.version}" for tech in analysis_result.technology_recommendations])}
"""
        
        # Calcular número de tarefas baseado na complexidade
        total_story_points = sum(f.estimated_effort for f in analysis_result.features)
        num_tasks = min(50, max(10, total_story_points // 2))  # Entre 10-50 tarefas
        
        if verbose:
            console.print(f"   • Generating {num_tasks} tasks based on {total_story_points} story points")
        
        # Gerar tarefas
        generated_tasks = task_generator.generate_custom_tasks(
            name=final_project_name,
            description=project_description,
            num_tasks=num_tasks
        )
        
        # 4. Processar e estruturar resultados
        console.print("📊 Processing results...")
        
        project_data = {
            'name': final_project_name,
            'description': analysis_result.project_description,
            'prd_file': str(prd_file),
            'analysis': {
                'complexity_score': analysis_result.complexity_score,
                'estimated_timeline': analysis_result.estimated_timeline,
                'total_features': len(analysis_result.features),
                'total_story_points': total_story_points,
                'features': [
                    {
                        'name': f.name,
                        'description': f.description,
                        'priority': f.priority,
                        'complexity': f.complexity.value,
                        'effort': f.estimated_effort,
                        'dependencies': f.dependencies
                    } for f in analysis_result.features
                ],
                'technology_recommendations': [
                    {
                        'category': t.category,
                        'technology': t.technology,
                        'version': t.version,
                        'reason': t.reason,
                        'confidence': t.confidence
                    } for t in analysis_result.technology_recommendations
                ],
                'suggestions': [
                    {
                        'type': s.type,
                        'title': s.title,
                        'description': s.description,
                        'impact': s.impact,
                        'effort': s.effort
                    } for s in analysis_result.suggestions
                ],
                'clarifications_needed': analysis_result.clarifications_needed,
                'risk_factors': analysis_result.risk_factors
            },
            'generated_tasks': [
                {
                    'title': task['title'],
                    'description': task['description'],
                    'priority': task['priority'],
                    'estimated_hours': task['estimated_hours'],
                    'complexity': task['complexity'],
                    'tags': task['tags'],
                    'dependencies': task.get('dependencies', [])
                } for task in generated_tasks
            ],
            'generated_at': datetime.now().isoformat(),
            'total_tasks': len(generated_tasks)
        }
        
        # 5. Output baseado na opção escolhida
        if output == 'json':
            output_file = f"{final_project_name.lower().replace(' ', '_')}_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            console.print(f"✅ Results saved to: {output_file}")
            
        elif output == 'db':
            console.print("💾 Saving to database...")
            conn = await create_connection()
            await init_database(conn)
            
            # Salvar projeto
            project_id = await conn.fetchval("""
                INSERT INTO projects (name, description, status, metadata)
                VALUES ($1, $2, 'planning', $3)
                RETURNING id
            """, final_project_name, analysis_result.project_description, json.dumps(project_data['analysis']))
            
            # Salvar tarefas
            for task_data in generated_tasks:
                await conn.execute("""
                    INSERT INTO tasks (project_id, title, description, status, priority, estimated_hours, metadata)
                    VALUES ($1, $2, $3, 'todo', $4, $5, $6)
                """, project_id, task_data['title'], task_data['description'], 
                    task_data['priority'], task_data['estimated_hours'], json.dumps(task_data))
            
            await conn.close()
            console.print(f"✅ Project saved to database with ID: {project_id}")
            
        else:  # console output
            await _display_console_results(project_data, verbose)
        
        # 6. Summary
        console.print(Panel(
            f"[bold green]✅ PRD Analysis Complete![/bold green]\n\n"
            f"[cyan]Project: {final_project_name}[/cyan]\n"
            f"[yellow]Tasks Generated: {len(generated_tasks)}[/yellow]\n"
            f"[blue]Complexity: {analysis_result.complexity_score:.1f}/10[/blue]\n"
            f"[magenta]Timeline: {analysis_result.estimated_timeline}[/magenta]",
            title="🎉 Success",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(Panel(
            f"[bold red]❌ Error analyzing PRD[/bold red]\n\n"
            f"[red]{str(e)}[/red]",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

async def _display_console_results(project_data, verbose):
    """Exibir resultados no console"""
    
    analysis = project_data['analysis']
    tasks = project_data['generated_tasks']
    
    console.print("\n" + "="*60)
    console.print("📋 PROJECT ANALYSIS RESULTS")
    console.print("="*60)
    
    console.print(f"🎯 **Project**: {project_data['name']}")
    console.print(f"📊 **Complexity**: {analysis['complexity_score']:.1f}/10")
    console.print(f"⏱️ **Timeline**: {analysis['estimated_timeline']}")
    console.print(f"🎮 **Features**: {analysis['total_features']}")
    console.print(f"📈 **Story Points**: {analysis['total_story_points']}")
    
    if verbose:
        console.print(f"\n🎯 **Features Identified:**")
        for feature in analysis['features']:
            priority_emoji = "🔴" if feature['priority'] == "HIGH" else "🟡" if feature['priority'] == "MEDIUM" else "🟢"
            console.print(f"  {priority_emoji} **{feature['name']}** ({feature['effort']} SP)")
            console.print(f"     {feature['description']}")
        
        console.print(f"\n🛠️ **Technology Stack:**")
        for tech in analysis['technology_recommendations']:
            confidence_emoji = "🟢" if tech['confidence'] > 0.8 else "🟡"
            console.print(f"  {confidence_emoji} **{tech['category']}**: {tech['technology']} v{tech['version']}")
    
    console.print(f"\n📝 **Generated Tasks ({len(tasks)} total):**")
    
    # Agrupar tarefas por prioridade
    high_priority = [t for t in tasks if t['priority'] == 'high']
    medium_priority = [t for t in tasks if t['priority'] == 'medium']
    low_priority = [t for t in tasks if t['priority'] == 'low']
    
    if high_priority:
        console.print(f"\n🔴 **High Priority ({len(high_priority)} tasks):**")
        for task in high_priority[:5]:  # Show top 5
            console.print(f"  • **{task['title']}** ({task['estimated_hours']}h)")
            if verbose:
                console.print(f"    {task['description'][:100]}...")
    
    if medium_priority:
        console.print(f"\n🟡 **Medium Priority ({len(medium_priority)} tasks):**")
        for task in medium_priority[:3]:  # Show top 3
            console.print(f"  • **{task['title']}** ({task['estimated_hours']}h)")
    
    if low_priority:
        console.print(f"\n🟢 **Low Priority ({len(low_priority)} tasks):**")
        for task in low_priority[:2]:  # Show top 2
            console.print(f"  • **{task['title']}** ({task['estimated_hours']}h)")
    
    # Estatísticas finais
    total_hours = sum(t['estimated_hours'] for t in tasks)
    console.print(f"\n📊 **Task Statistics:**")
    console.print(f"  • Total Hours: {total_hours}h ({total_hours//40} weeks @ 40h/week)")
    console.print(f"  • High Priority: {len(high_priority)} tasks")
    console.print(f"  • Medium Priority: {len(medium_priority)} tasks") 
    console.print(f"  • Low Priority: {len(low_priority)} tasks")
    
    if analysis['clarifications_needed']:
        console.print(f"\n❓ **Clarifications Needed:**")
        for clarification in analysis['clarifications_needed']:
            console.print(f"  • {clarification}")

@cli.command()
@click.argument('project_name')
def list_tasks(project_name):
    """Listar tarefas de um projeto"""
    console.print(f"📋 Tasks for project: {project_name}")
    # TODO: Implement database query

@cli.command()
def list_projects():
    """Listar todos os projetos"""
    console.print("📁 All projects:")
    # TODO: Implement database query

# Wrapper para async commands
def async_command(f):
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

# Apply async wrapper
analyze_prd = async_command(analyze_prd)

if __name__ == '__main__':
    cli()