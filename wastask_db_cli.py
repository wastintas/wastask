#!/usr/bin/env python3
"""
WasTask Database CLI
Interface de linha de comando para gerenciar o banco de dados WasTask
"""
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from database_manager import WasTaskDatabase, connect_and_run

async def setup_database():
    """Configurar banco de dados"""
    print("🚀 Setting up WasTask Database...")
    
    async def setup(db):
        await db.create_schema()
        print("✅ Database schema created successfully!")
        
        # Testar conexão
        stats = await db.get_project_stats()
        print(f"📊 Database ready - {stats}")
    
    await connect_and_run(setup)

async def import_analysis_result(json_file: str):
    """Importar resultado de análise do JSON"""
    print(f"📥 Importing analysis from: {json_file}")
    
    if not Path(json_file).exists():
        print(f"❌ File not found: {json_file}")
        return
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        async def import_data(db):
            project_id = await db.save_project_analysis(results)
            print(f"✅ Analysis imported with Project ID: {project_id}")
            return project_id
        
        project_id = await connect_and_run(import_data)
        print(f"🎯 Project '{results['project']['name']}' saved successfully!")
        
    except Exception as e:
        print(f"❌ Error importing analysis: {e}")

async def list_projects():
    """Listar todos os projetos"""
    print("📋 WasTask Projects")
    print("=" * 60)
    
    async def list_all(db):
        projects = await db.list_projects()
        
        if not projects:
            print("No projects found.")
            return
        
        for project in projects:
            created = project['created_at'].strftime('%Y-%m-%d %H:%M')
            print(f"🎯 [{project['id']:2d}] {project['name']}")
            print(f"    📝 {project['description'][:80]}...")
            print(f"    📊 Complexity: {project['complexity_score']:.1f}/10")
            print(f"    ⏱️  Timeline: {project['timeline']}")
            print(f"    📅 Created: {created}")
            print(f"    🔄 Status: {project['status']}")
            print()
    
    await connect_and_run(list_all)

async def show_project_details(project_id: int):
    """Mostrar detalhes de um projeto"""
    print(f"📋 Project Details - ID: {project_id}")
    print("=" * 60)
    
    async def get_details(db):
        project_data = await db.get_project(project_id)
        
        if not project_data:
            print(f"❌ Project {project_id} not found")
            return
        
        project = project_data['project']
        
        # Informações básicas
        print(f"🎯 Project: {project['name']}")
        print(f"📝 Description: {project['description']}")
        print(f"📊 Complexity: {project['complexity_score']:.1f}/10")
        print(f"⏱️ Timeline: {project['timeline']}")
        print(f"📈 Total Hours: {project['total_hours']}h")
        print(f"📦 Package Manager: {project['package_manager']}")
        print(f"🔄 Status: {project['status']}")
        
        # PRD Enhancement
        if project.get('prd_quality_before'):
            print(f"✨ PRD Quality: {project['prd_quality_before']:.1f}/10 → {project['prd_quality_after']:.1f}/10")
        
        # Tecnologias
        technologies = project_data['technologies']
        if technologies:
            print(f"\n🛠️ Technologies ({len(technologies)}):")
            for tech in technologies:
                confidence = "🟢" if tech['confidence'] > 0.8 else "🟡" if tech['confidence'] > 0.6 else "🔴"
                print(f"  {confidence} {tech['technology']} v{tech['version']} ({tech['category']})")
        
        # Features
        features = project_data['features']
        if features:
            print(f"\n🎯 Features ({len(features)}):")
            for feature in features:
                priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(feature['priority'], "⚪")
                print(f"  {priority_emoji} {feature['name']} ({feature['estimated_effort']} SP)")
        
        # Tarefas por status
        tasks = project_data['tasks']
        if tasks:
            task_counts = {}
            for task in tasks:
                status = task['status']
                task_counts[status] = task_counts.get(status, 0) + 1
            
            print(f"\n📝 Tasks ({len(tasks)} total):")
            for status, count in task_counts.items():
                emoji = {"todo": "⏳", "in_progress": "🚧", "completed": "✅"}.get(status, "📋")
                print(f"  {emoji} {status.replace('_', ' ').title()}: {count}")
        
        # Riscos
        risks = project_data['risks']
        if risks:
            print(f"\n⚠️ Risks:")
            for risk in risks:
                print(f"  • {risk}")
        
        # Questões de clarificação
        questions = project_data['questions']
        if questions:
            pending_questions = [q for q in questions if q['status'] == 'pending']
            if pending_questions:
                print(f"\n❓ Pending Questions ({len(pending_questions)}):")
                for q in pending_questions[:5]:
                    print(f"  • {q['question']}")
    
    await connect_and_run(get_details, project_id)

async def show_database_stats():
    """Mostrar estatísticas do banco"""
    print("📊 WasTask Database Statistics")
    print("=" * 40)
    
    async def get_stats(db):
        stats = await db.get_project_stats()
        
        print(f"🎯 Total Projects: {stats['total_projects']}")
        print(f"📝 Total Tasks: {stats['total_tasks']}")
        print(f"✅ Completed Tasks: {stats['completed_tasks']}")
        print(f"🚧 Active Projects: {stats['active_projects']}")
        
        if stats['avg_complexity']:
            print(f"📊 Average Complexity: {stats['avg_complexity']:.1f}/10")
        
        # Calcular taxa de conclusão
        if stats['total_tasks'] > 0:
            completion_rate = (stats['completed_tasks'] / stats['total_tasks']) * 100
            print(f"📈 Task Completion Rate: {completion_rate:.1f}%")
    
    await connect_and_run(get_stats)

async def update_task_status_cmd(task_id: int, status: str, assigned_to: str = None):
    """Atualizar status de tarefa"""
    valid_statuses = ['todo', 'in_progress', 'completed', 'blocked']
    
    if status not in valid_statuses:
        print(f"❌ Invalid status. Use: {', '.join(valid_statuses)}")
        return
    
    async def update_status(db):
        await db.update_task_status(task_id, status, assigned_to)
        print(f"✅ Task {task_id} updated to '{status}'")
        
        if assigned_to:
            print(f"👤 Assigned to: {assigned_to}")
    
    await connect_and_run(update_status)

async def run_analysis_and_save(prd_file: str):
    """Executar análise de PRD e salvar no banco automaticamente"""
    print(f"🚀 Analyzing PRD and saving to database: {prd_file}")
    
    # Importar e executar análise
    from wastask_simple import analyze_prd_file
    
    try:
        # Executar análise
        results = await analyze_prd_file(prd_file, verbose=True, interactive=False)
        
        if not results:
            print("❌ Analysis failed")
            return
        
        # Salvar no banco
        async def save_results(db):
            project_id = await db.save_project_analysis(results)
            print(f"💾 Results saved to database with Project ID: {project_id}")
            
            # Mostrar resumo
            project = results['project']
            stats = results['statistics']
            print(f"\n📋 Analysis Summary:")
            print(f"   🎯 Project: {project['name']}")
            print(f"   📝 Tasks: {stats['total_tasks']}")
            print(f"   ⏱️ Hours: {stats['total_hours']}h")
            print(f"   💾 Database ID: {project_id}")
            
            return project_id
        
        project_id = await connect_and_run(save_results)
        print(f"✅ Complete! Project saved with ID: {project_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def print_usage():
    """Mostrar instruções de uso"""
    print("""
🚀 WasTask Database CLI

Usage:
  python wastask_db_cli.py <command> [options]

Commands:
  setup                     - Setup database schema
  list                      - List all projects
  show <project_id>         - Show project details
  stats                     - Show database statistics
  import <json_file>        - Import analysis result from JSON
  analyze <prd_file>        - Analyze PRD and save to database
  update-task <id> <status> [assigned_to] - Update task status

Examples:
  python wastask_db_cli.py setup
  python wastask_db_cli.py analyze prd_exemplo.md
  python wastask_db_cli.py list
  python wastask_db_cli.py show 1
  python wastask_db_cli.py update-task 5 in_progress john@example.com
  python wastask_db_cli.py stats
""")

async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "setup":
            await setup_database()
        
        elif command == "list":
            await list_projects()
        
        elif command == "show":
            if len(sys.argv) < 3:
                print("❌ Project ID required. Usage: show <project_id>")
                sys.exit(1)
            project_id = int(sys.argv[2])
            await show_project_details(project_id)
        
        elif command == "stats":
            await show_database_stats()
        
        elif command == "import":
            if len(sys.argv) < 3:
                print("❌ JSON file required. Usage: import <json_file>")
                sys.exit(1)
            await import_analysis_result(sys.argv[2])
        
        elif command == "analyze":
            if len(sys.argv) < 3:
                print("❌ PRD file required. Usage: analyze <prd_file>")
                sys.exit(1)
            await run_analysis_and_save(sys.argv[2])
        
        elif command == "update-task":
            if len(sys.argv) < 4:
                print("❌ Task ID and status required. Usage: update-task <id> <status> [assigned_to]")
                sys.exit(1)
            task_id = int(sys.argv[2])
            status = sys.argv[3]
            assigned_to = sys.argv[4] if len(sys.argv) > 4 else None
            await update_task_status_cmd(task_id, status, assigned_to)
        
        else:
            print(f"❌ Unknown command: {command}")
            print_usage()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())