#!/usr/bin/env python3
"""
WasTask Simple CLI - Análise de PRD sem dependências externas
Uso: python wastask_simple.py <arquivo_prd>
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict, Any
from doc_fetcher import fetch_tech_documentation
from prd_enhancer import prd_enhancer

def extract_basic_info(prd_content: str) -> Dict[str, str]:
    """Extrair informações básicas do PRD"""
    lines = prd_content.split('\n')
    
    # Tentar encontrar o título
    title = "Unknown Project"
    for line in lines[:10]:
        if line.startswith('# '):
            title = line[2:].strip()
            if ' - ' in title:
                title = title.split(' - ')[0]
            break
    
    # Extrair descrição (primeiro parágrafo após título)
    description = "Project extracted from PRD"
    in_content = False
    for line in lines:
        if line.startswith('## ') and 'overview' in line.lower():
            in_content = True
            continue
        if in_content and line.strip() and not line.startswith('#'):
            description = line.strip()
            break
    
    return {
        "name": title,
        "description": description
    }

def identify_features(prd_content: str) -> List[Dict[str, Any]]:
    """Identificar features no PRD usando análise de texto"""
    features = []
    lines = prd_content.split('\n')
    
    current_section = ""
    feature_keywords = ['feature', 'functionality', 'system', 'management', 'interface', 'api', 'service']
    
    for line in lines:
        # Detectar seções
        if line.startswith('### '):
            current_section = line[4:].strip()
            
            # Verificar se é uma feature
            if any(keyword in current_section.lower() for keyword in feature_keywords):
                # Determinar prioridade baseada em palavras-chave
                priority = "MEDIUM"
                if any(word in current_section.lower() for word in ['core', 'main', 'primary', 'essential']):
                    priority = "HIGH"
                elif any(word in current_section.lower() for word in ['optional', 'nice', 'future', 'enhancement']):
                    priority = "LOW"
                
                # Determinar complexidade baseada no contexto
                complexity = "MEDIUM"
                if any(word in current_section.lower() for word in ['auth', 'payment', 'real-time', 'multiplayer', 'sync']):
                    complexity = "COMPLEX"
                elif any(word in current_section.lower() for word in ['ui', 'display', 'list', 'view']):
                    complexity = "SIMPLE"
                
                # Estimar esforço
                effort_map = {"SIMPLE": 5, "MEDIUM": 8, "COMPLEX": 13}
                effort = effort_map.get(complexity, 8)
                
                features.append({
                    "name": current_section,
                    "description": f"Implementation of {current_section.lower()}",
                    "priority": priority,
                    "complexity": complexity,
                    "estimated_effort": effort,
                    "dependencies": []
                })
    
    # Se não encontrou features em seções, procurar em listas
    if not features:
        in_features_section = False
        for line in lines:
            if any(word in line.lower() for word in ['feature', 'functionality', 'requirement']):
                in_features_section = True
                continue
            
            if in_features_section and line.strip().startswith('- '):
                feature_name = line.strip()[2:].strip()
                if len(feature_name) > 5:  # Filter out short items
                    features.append({
                        "name": feature_name,
                        "description": f"Implementation of {feature_name.lower()}",
                        "priority": "MEDIUM",
                        "complexity": "MEDIUM", 
                        "estimated_effort": 8,
                        "dependencies": []
                    })
    
    return features[:10]  # Limit to 10 features

def analyze_complexity(prd_content: str, features: List[Dict]) -> Dict[str, Any]:
    """Analisar complexidade do projeto"""
    content_lower = prd_content.lower()
    
    # Indicadores de complexidade
    complexity_indicators = {
        "has_auth": any(word in content_lower for word in ['auth', 'login', 'register', 'user']),
        "has_database": any(word in content_lower for word in ['database', 'data', 'store', 'save']),
        "has_api": any(word in content_lower for word in ['api', 'endpoint', 'service', 'backend']),
        "has_realtime": any(word in content_lower for word in ['real-time', 'live', 'socket', 'sync']),
        "has_payment": any(word in content_lower for word in ['payment', 'pay', 'money', 'billing']),
        "has_mobile": any(word in content_lower for word in ['mobile', 'app', 'ios', 'android']),
        "has_multiplayer": any(word in content_lower for word in ['multiplayer', 'multi-user', 'collaborative'])
    }
    
    # Calcular score
    base_score = len(features) * 0.5
    complexity_bonus = sum(complexity_indicators.values()) * 1.5
    complexity_score = min(10, base_score + complexity_bonus)
    
    # Estimar timeline
    total_effort = sum(f.get('estimated_effort', 8) for f in features)
    weeks = max(4, total_effort // 8)
    timeline = f"{weeks}-{weeks + 2} weeks"
    
    # Identificar riscos
    risks = []
    if complexity_indicators["has_payment"]:
        risks.append("Payment integration complexity")
    if complexity_indicators["has_realtime"]:
        risks.append("Real-time synchronization challenges")
    if complexity_indicators["has_multiplayer"]: 
        risks.append("Multiplayer scalability requirements")
    if total_effort > 60:
        risks.append("Large project scope")
    
    return {
        "score": complexity_score,
        "timeline": timeline,
        "risks": risks,
        "total_effort": total_effort
    }

def recommend_technologies(prd_content: str, features: List[Dict]) -> List[Dict[str, Any]]:
    """Recomendar stack tecnológica baseada no que está especificado no PRD"""
    content_lower = prd_content.lower()
    recommendations = []
    
    # Detectar tecnologias específicas mencionadas no PRD
    tech_patterns = {
        # Frontend frameworks
        "react router v7": ("fullstack_framework", "React Router v7", "latest", "Full-stack React framework (Remix successor)", 0.95),
        "react-router v7": ("fullstack_framework", "React Router v7", "latest", "Full-stack React framework (Remix successor)", 0.95),
        "remix": ("fullstack_framework", "Remix", "latest", "Full-stack React framework", 0.9),
        "react": ("frontend_framework", "React", "18.3.0", "Component-based UI library", 0.85),
        
        # UI Libraries
        "shadcn/ui": ("ui_library", "Shadcn/ui", "latest", "Modern React component library", 0.95),
        "shadcn-ui": ("ui_library", "Shadcn/ui", "latest", "Modern React component library", 0.95),
        "tailwind": ("styling", "Tailwind CSS", "latest", "Utility-first CSS framework", 0.9),
        
        # Validation
        "zod": ("validation", "Zod", "latest", "TypeScript-first schema validation", 0.95),
        
        # Database/ORM
        "drizzle orm": ("orm", "Drizzle ORM", "latest", "TypeScript-first ORM", 0.95),
        "drizzle": ("orm", "Drizzle ORM", "latest", "TypeScript-first ORM", 0.95),
        "postgresql": ("database", "PostgreSQL", "16.0", "Reliable relational database", 0.9),
        "postgres": ("database", "PostgreSQL", "16.0", "Reliable relational database", 0.9),
        
        # Routing patterns
        "remix flat routes": ("routing_pattern", "Remix Flat Routes", "latest", "File-based routing pattern", 0.95),
        "flat routes": ("routing_pattern", "Remix Flat Routes", "latest", "File-based routing pattern", 0.95),
        
        # Other common technologies
        "node.js": ("backend", "Node.js", "20.0.0", "JavaScript runtime", 0.8),
        "nodejs": ("backend", "Node.js", "20.0.0", "JavaScript runtime", 0.8),
        "typescript": ("language", "TypeScript", "5.0+", "Type-safe JavaScript", 0.9),
        "express": ("backend_framework", "Express", "latest", "Minimal Node.js framework", 0.8),
        "jwt": ("authentication", "JWT", "latest", "JSON Web Tokens", 0.85),
        "bcrypt": ("security", "bcrypt", "latest", "Password hashing", 0.9),
        "docker": ("deployment", "Docker", "latest", "Containerization", 0.85),
    }
    
    # Procurar por tecnologias específicas no texto
    detected_techs = {}
    has_fullstack_framework = False
    
    for pattern, (category, tech, version, reason, confidence) in tech_patterns.items():
        if pattern in content_lower:
            # Se já temos uma tech nesta categoria, usar a de maior confiança
            if category not in detected_techs or detected_techs[category][4] < confidence:
                detected_techs[category] = (category, tech, version, reason, confidence)
                
            # Marcar se temos um framework full-stack
            if category == "fullstack_framework":
                has_fullstack_framework = True
    
    # NÃO remover automaticamente - deixar para o modo interativo decidir
    
    # Converter para lista de recomendações
    for category, tech, version, reason, confidence in detected_techs.values():
        recommendations.append({
            "category": category,
            "technology": tech,
            "version": version,
            "reason": reason,
            "confidence": confidence
        })
    
    # Se não encontrou tecnologias específicas, usar fallbacks
    if not recommendations:
        # Frontend fallback
        if any(word in content_lower for word in ['web', 'browser', 'ui', 'interface']):
            recommendations.append({
                "category": "frontend_framework",
                "technology": "React",
                "version": "18.3.0",
                "reason": "Modern component-based architecture",
                "confidence": 0.7
            })
        
        # Backend fallback
        if any(word in content_lower for word in ['api', 'server', 'backend']):
            recommendations.append({
                "category": "backend", 
                "technology": "Node.js",
                "version": "20.0.0",
                "reason": "JavaScript ecosystem",
                "confidence": 0.7
            })
        
        # Database fallback
        if any(word in content_lower for word in ['data', 'store', 'user', 'save']):
            recommendations.append({
                "category": "database",
                "technology": "PostgreSQL", 
                "version": "16.0",
                "reason": "Reliable relational database",
                "confidence": 0.8
            })
    
    return recommendations

def generate_tasks(project_name: str, features: List[Dict], complexity_analysis: Dict) -> List[Dict[str, Any]]:
    """Gerar tarefas baseadas nas features"""
    tasks = []
    
    # Task templates baseados no tipo de projeto
    task_templates = {
        "setup": [
            "Project foundation and setup",
            "Development environment configuration", 
            "CI/CD pipeline setup"
        ],
        "frontend": [
            "UI/UX design and layout",
            "Component library creation",
            "Responsive design implementation",
            "Frontend routing setup"
        ],
        "backend": [
            "API design and documentation",
            "Database schema design",
            "Authentication system",
            "API endpoints implementation"
        ],
        "features": [],  # Will be populated from actual features
        "testing": [
            "Unit tests implementation",
            "Integration tests setup", 
            "E2E testing framework",
            "Performance testing"
        ],
        "deployment": [
            "Production deployment setup",
            "Monitoring and logging",
            "Security audit",
            "Documentation finalization"
        ]
    }
    
    # Add feature-specific tasks
    for feature in features:
        task_templates["features"].extend([
            f"{feature['name']} - Core implementation",
            f"{feature['name']} - Testing and validation",
            f"{feature['name']} - UI integration"
        ])
    
    # Generate tasks from templates
    task_id = 1
    for category, task_list in task_templates.items():
        for task_title in task_list:
            
            # Determine priority
            priority = "medium"
            if category in ["setup", "backend"] or "core" in task_title.lower():
                priority = "high"
            elif category in ["testing", "deployment"]:
                priority = "low"
            
            # Estimate hours
            hours = 8  # default
            if category == "setup":
                hours = 4
            elif "implementation" in task_title.lower():
                hours = 12
            elif "testing" in task_title.lower():
                hours = 6
            
            # Determine complexity
            complexity = "medium"
            if any(word in task_title.lower() for word in ['auth', 'payment', 'real-time']):
                complexity = "high"
            elif any(word in task_title.lower() for word in ['setup', 'config', 'ui']):
                complexity = "low"
            
            tasks.append({
                "id": task_id,
                "title": task_title,
                "description": f"Implement {task_title.lower()} for {project_name}",
                "priority": priority,
                "estimated_hours": hours,
                "complexity": complexity,
                "category": category,
                "tags": [category, complexity],
                "dependencies": []
            })
            task_id += 1
    
    return tasks

def detect_package_manager(prd_content: str) -> str:
    """Detectar gerenciador de pacotes preferido"""
    content_lower = prd_content.lower()
    
    # Procurar por menções específicas
    if any(word in content_lower for word in ['pnpm', 'pnpm install']):
        return "pnpm"
    elif any(word in content_lower for word in ['yarn', 'yarn add', 'yarn install']):
        return "yarn"
    elif any(word in content_lower for word in ['bun', 'bun add', 'bun install']):
        return "bun"
    elif any(word in content_lower for word in ['npm', 'npm install']):
        return "npm"
    
    # Default moderno
    return "pnpm"

def ask_clarification(question: str, options: List[str] = None) -> str:
    """Fazer pergunta interativa quando não estiver explícito"""
    print(f"\n❓ {question}")
    
    if options:
        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")
        
        while True:
            try:
                choice = input("\nEscolha (número): ").strip()
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    return options[idx]
                else:
                    print("❌ Opção inválida. Tente novamente.")
            except (ValueError, KeyboardInterrupt):
                print("❌ Entrada inválida. Tente novamente.")
    else:
        return input("Resposta: ").strip()

def _display_prd_comparison(original: str, enhanced: str):
    """Mostrar comparação entre PRD original e melhorado"""
    
    console.print("\n" + "="*80)
    console.print("📋 PRD COMPARISON - BEFORE vs AFTER")
    console.print("="*80)
    
    # Estatísticas
    orig_words = len(original.split())
    enhanced_words = len(enhanced.split())
    orig_lines = len([line for line in original.split('\n') if line.strip()])
    enhanced_lines = len([line for line in enhanced.split('\n') if line.strip()])
    
    console.print(f"\n📊 Statistics:")
    console.print(f"   Words: {orig_words} → {enhanced_words} (+{enhanced_words - orig_words})")
    console.print(f"   Lines: {orig_lines} → {enhanced_lines} (+{enhanced_lines - orig_lines})")
    
    # PRD Original
    console.print(f"\n📄 ORIGINAL PRD:")
    console.print("-" * 50)
    print(original)
    
    console.print(f"\n✨ ENHANCED PRD:")
    console.print("-" * 50)
    print(enhanced)
    console.print("-" * 50)

def _save_prd_comparison(original: str, enhanced: str, project_name: str):
    """Salvar comparação em arquivos"""
    
    safe_name = project_name.lower().replace(' ', '_').replace('/', '_')
    
    # Salvar PRD original
    orig_file = f"{safe_name}_original.md"
    with open(orig_file, 'w', encoding='utf-8') as f:
        f.write(f"# {project_name} - Original PRD\n\n")
        f.write(original)
    
    # Salvar PRD melhorado
    enhanced_file = f"{safe_name}_enhanced.md"
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(f"# {project_name} - Enhanced PRD\n\n")
        f.write(enhanced)
    
    # Salvar comparação
    comparison_file = f"{safe_name}_comparison.md"
    with open(comparison_file, 'w', encoding='utf-8') as f:
        f.write(f"# {project_name} - PRD Comparison\n\n")
        f.write(f"## Original PRD ({len(original.split())} words)\n\n")
        f.write("```markdown\n")
        f.write(original)
        f.write("\n```\n\n")
        f.write(f"## Enhanced PRD ({len(enhanced.split())} words)\n\n")
        f.write("```markdown\n")
        f.write(enhanced)
        f.write("\n```\n\n")
        f.write(f"## Improvement Summary\n\n")
        f.write(f"- **Words**: {len(original.split())} → {len(enhanced.split())}\n")
        orig_lines = len(original.split('\n'))
        enhanced_lines = len(enhanced.split('\n'))
        f.write(f"- **Lines**: {orig_lines} → {enhanced_lines}\n")
        f.write(f"- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    return orig_file, enhanced_file, comparison_file

async def generate_setup_commands_with_docs(technologies: List[Dict], package_manager: str) -> Dict[str, Any]:
    """Gerar comandos de instalação baseados nas documentações reais"""
    
    print("📚 Fetching documentation from official sources...")
    
    # Buscar documentações oficiais
    tech_docs = await fetch_tech_documentation(technologies)
    
    commands = {
        "setup": [],
        "install": [],
        "scripts": {},
        "environment": [],
        "config_files": {},
        "documentation_sources": {}
    }
    
    # Coletar comandos das documentações reais
    all_deps = set()
    all_dev_deps = set()
    
    for tech in technologies:
        tech_key = tech["technology"].lower().replace(" ", "-").replace("/", "-")
        
        if tech_key in tech_docs:
            doc = tech_docs[tech_key]
            commands["documentation_sources"][tech["technology"]] = doc.documentation_url
            
            # Comandos de instalação específicos
            if doc.install_commands:
                commands["setup"].extend(doc.install_commands)
            
            # Comandos de setup
            if doc.setup_commands:
                commands["setup"].extend(doc.setup_commands)
            
            # Dependências
            all_deps.update(doc.dependencies)
            all_dev_deps.update(doc.dev_dependencies)
            
            # Scripts
            commands["scripts"].update(doc.scripts)
            
            # Arquivos de configuração
            commands["config_files"].update(doc.config_files)
            
            # Setup de ambiente
            if doc.environment_setup:
                commands["environment"].extend(doc.environment_setup)
        else:
            print(f"⚠️ No documentation found for {tech['technology']}")
    
    # Gerar comandos de instalação com gerenciador escolhido
    if all_deps:
        deps_list = list(all_deps)
        if package_manager == "npm":
            commands["install"].append(f"npm install {' '.join(deps_list)}")
        else:
            commands["install"].append(f"{package_manager} add {' '.join(deps_list)}")
    
    if all_dev_deps:
        dev_deps_list = list(all_dev_deps)
        if package_manager == "npm":
            commands["install"].append(f"npm install --save-dev {' '.join(dev_deps_list)}")
        else:
            commands["install"].append(f"{package_manager} add -D {' '.join(dev_deps_list)}")
    
    # Remover duplicatas e ordenar
    commands["setup"] = list(dict.fromkeys(commands["setup"]))  # Remove duplicatas mantendo ordem
    commands["install"] = list(dict.fromkeys(commands["install"]))
    commands["environment"] = list(dict.fromkeys(commands["environment"]))
    
    return commands

async def analyze_prd_file(prd_file: str, verbose: bool = False, interactive: bool = True) -> Dict[str, Any]:
    """Função principal de análise"""
    
    print("🚀 WasTask - PRD Analysis")
    print("=" * 50)
    
    # 1. Ler arquivo
    print(f"📄 Reading: {prd_file}")
    try:
        prd_content = Path(prd_file).read_text(encoding='utf-8')
        if verbose:
            print(f"   • File size: {len(prd_content)} characters")
            print(f"   • Word count: {len(prd_content.split())} words")
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return {}
    
    # 2. Melhorar PRD se necessário
    print("🧠 Analyzing and enhancing PRD quality...")
    enhancement = await prd_enhancer.enhance_prd(prd_content)
    
    if enhancement.quality_before < enhancement.quality_after:
        print(f"   ✅ PRD enhanced: {enhancement.quality_before:.1f}/10 → {enhancement.quality_after:.1f}/10")
        prd_content = enhancement.enhanced_prd  # Usar PRD melhorado
        
        if interactive and enhancement.clarification_questions:
            print(f"\n❓ Questions to clarify requirements:")
            for i, question in enumerate(enhancement.clarification_questions[:5], 1):
                print(f"   {i}. {question}")
            
            if enhancement.suggested_features:
                print(f"\n💡 Suggested additional features:")
                for feature in enhancement.suggested_features[:3]:
                    print(f"   • {feature}")
            
            should_continue = ask_clarification(
                "Continue with enhanced PRD?", 
                ["Yes, use enhanced PRD", "No, use original PRD", "Show PRD comparison"]
            )
            
            if should_continue.startswith("Show"):
                _display_prd_comparison(enhancement.original_prd, enhancement.enhanced_prd)
                should_continue = ask_clarification(
                    "After seeing comparison, which PRD to use?",
                    ["Use enhanced PRD", "Use original PRD"]
                )
            
            if should_continue.startswith("No") or should_continue.startswith("Use original"):
                prd_content = enhancement.original_prd
                print("   📋 Using original PRD")
            else:
                print("   ✨ Using AI-enhanced PRD")
    else:
        print(f"   ✅ PRD quality is good ({enhancement.quality_before:.1f}/10)")
    
    # 3. Extrair informações básicas
    print("🔍 Extracting project information...")
    basic_info = extract_basic_info(prd_content)
    print(f"   • Project: {basic_info['name']}")
    
    # 4. Identificar features
    print("🎯 Identifying features...")
    features = identify_features(prd_content)
    print(f"   • Found {len(features)} features")
    
    # 5. Analisar complexidade
    print("📊 Analyzing complexity...")
    complexity_analysis = analyze_complexity(prd_content, features)
    print(f"   • Complexity score: {complexity_analysis['score']:.1f}/10")
    print(f"   • Timeline: {complexity_analysis['timeline']}")
    
    # 6. Recomendar tecnologias
    print("🛠️ Recommending technologies...")
    tech_recommendations = recommend_technologies(prd_content, features)
    print(f"   • {len(tech_recommendations)} technology recommendations")
    
    # 6.1 Clarificações interativas (se habilitado)
    if interactive:
        # Verificar se tem full-stack + backend
        has_fullstack = any(t["category"] == "fullstack_framework" for t in tech_recommendations)
        has_backend = any(t["category"] == "backend" for t in tech_recommendations)
        
        if has_fullstack and has_backend:
            choice = ask_clarification(
                "Detectamos React Router v7 (full-stack) + Node.js backend. Como prefere?",
                [
                    "Apenas React Router v7 (full-stack completo)",
                    "React Router v7 + API backend separada",
                    "Apenas frontend React + API Node.js separada"
                ]
            )
            
            if choice.startswith("Apenas React Router v7"):
                # Remover backend separado
                tech_recommendations = [t for t in tech_recommendations if t["category"] != "backend"]
            elif choice.startswith("Apenas frontend"):
                # Remover full-stack, manter backend
                tech_recommendations = [t for t in tech_recommendations if t["category"] != "fullstack_framework"]
        
        # Detectar gerenciador de pacotes
        detected_pm = detect_package_manager(prd_content)
        if detected_pm == "pnpm":  # Se não foi explícito, perguntar
            pm_choice = ask_clarification(
                "Qual gerenciador de pacotes prefere?",
                ["pnpm (recomendado)", "npm", "yarn", "bun"]
            )
            detected_pm = pm_choice.split()[0].lower()
    else:
        detected_pm = detect_package_manager(prd_content)
    
    # 6.2 Gerar comandos de setup com documentações reais
    print("⚙️ Generating setup commands from official documentation...")
    setup_commands = await generate_setup_commands_with_docs(tech_recommendations, detected_pm)
    
    # 7. Gerar tarefas
    print("📝 Generating tasks...")
    tasks = generate_tasks(basic_info['name'], features, complexity_analysis)
    print(f"   • Generated {len(tasks)} tasks")
    
    # 8. Compilar resultados
    results = {
        'project': basic_info,
        'prd_enhancement': {
            'original_quality': enhancement.quality_before,
            'enhanced_quality': enhancement.quality_after,
            'was_enhanced': enhancement.quality_before < enhancement.quality_after,
            'original_prd': enhancement.original_prd,
            'enhanced_prd': enhancement.enhanced_prd,
            'clarification_questions': enhancement.clarification_questions,
            'suggested_features': enhancement.suggested_features,
            'technology_hints': enhancement.technology_hints
        },
        'features': features,
        'complexity': complexity_analysis,
        'technologies': tech_recommendations,
        'setup_commands': setup_commands,
        'package_manager': detected_pm,
        'tasks': tasks,
        'generated_at': datetime.now().isoformat(),
        'statistics': {
            'total_features': len(features),
            'total_tasks': len(tasks),
            'total_hours': sum(t['estimated_hours'] for t in tasks),
            'high_priority_tasks': len([t for t in tasks if t['priority'] == 'high']),
            'medium_priority_tasks': len([t for t in tasks if t['priority'] == 'medium']),
            'low_priority_tasks': len([t for t in tasks if t['priority'] == 'low'])
        }
    }
    
    return results

def display_results(results: Dict[str, Any], verbose: bool = False):
    """Exibir resultados no console"""
    
    if not results:
        return
    
    print("\n" + "=" * 60)
    print("📋 ANALYSIS RESULTS")
    print("=" * 60)
    
    # Project info
    project = results['project']
    stats = results['statistics']
    complexity = results['complexity']
    
    print(f"🎯 Project: {project['name']}")
    print(f"📝 Description: {project['description']}")
    
    # PRD Enhancement info
    if 'prd_enhancement' in results:
        enhancement = results['prd_enhancement']
        if enhancement['was_enhanced']:
            print(f"✨ PRD Enhanced: {enhancement['original_quality']:.1f}/10 → {enhancement['enhanced_quality']:.1f}/10")
        else:
            print(f"📋 PRD Quality: {enhancement['original_quality']:.1f}/10 (good)")
    
    print(f"📊 Complexity: {complexity['score']:.1f}/10")
    print(f"⏱️ Timeline: {complexity['timeline']}")
    print(f"📈 Total Hours: {stats['total_hours']}h ({stats['total_hours']//40} weeks)")
    
    # Features
    if verbose and results['features']:
        print(f"\n🎯 Features ({len(results['features'])}):")
        for feature in results['features']:
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(feature['priority'], "⚪")
            print(f"  {priority_emoji} {feature['name']} ({feature['estimated_effort']} SP)")
    
    # Technologies
    if results['technologies']:
        print(f"\n🛠️ Recommended Technologies:")
        for tech in results['technologies']:
            confidence_emoji = "🟢" if tech['confidence'] > 0.8 else "🟡" if tech['confidence'] > 0.6 else "🔴"
            print(f"  {confidence_emoji} {tech['category']}: {tech['technology']} v{tech['version']}")
    
    # Tasks summary
    print(f"\n📝 Generated Tasks ({stats['total_tasks']} total):")
    print(f"  🔴 High Priority: {stats['high_priority_tasks']} tasks")
    print(f"  🟡 Medium Priority: {stats['medium_priority_tasks']} tasks") 
    print(f"  🟢 Low Priority: {stats['low_priority_tasks']} tasks")
    
    # Show sample tasks
    high_tasks = [t for t in results['tasks'] if t['priority'] == 'high'][:3]
    if high_tasks:
        print(f"\n🔴 Sample High Priority Tasks:")
        for task in high_tasks:
            print(f"  • {task['title']} ({task['estimated_hours']}h)")
    
    # Setup Commands
    if 'setup_commands' in results:
        setup = results['setup_commands']
        pm = results.get('package_manager', 'npm')
        
        print(f"\n🚀 Setup Commands (using {pm} - from official docs):")
        
        if setup['setup']:
            print(f"  📦 Project Setup:")
            for cmd in setup['setup']:
                print(f"    {cmd}")
        
        if setup['install']:
            print(f"  📥 Install Dependencies:")
            for cmd in setup['install']:
                print(f"    {cmd}")
        
        if setup['environment']:
            print(f"  🐳 Environment Setup:")
            for cmd in setup['environment']:
                print(f"    {cmd}")
        
        if setup['scripts'] and verbose:
            print(f"  📝 Package.json Scripts:")
            for script, command in setup['scripts'].items():
                print(f"    \"{script}\": \"{command}\"")
        
        if setup.get('config_files') and verbose:
            print(f"  📄 Configuration Files Generated:")
            for filename in setup['config_files'].keys():
                print(f"    {filename}")
        
        if setup.get('documentation_sources') and verbose:
            print(f"  📚 Documentation Sources:")
            for tech, url in setup['documentation_sources'].items():
                print(f"    {tech}: {url}")
    
    # Risks
    if complexity['risks']:
        print(f"\n⚠️ Risk Factors:")
        for risk in complexity['risks']:
            print(f"  • {risk}")
    
    print(f"\n✅ Analysis complete! Ready for development.")

async def main():
    """Função principal"""
    if len(sys.argv) < 2:
        print("Usage: python wastask_simple.py <prd_file> [--verbose] [--json] [--no-interactive] [--save-prd-comparison]")
        sys.exit(1)
    
    prd_file = sys.argv[1]
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    json_output = "--json" in sys.argv
    interactive = "--no-interactive" not in sys.argv
    save_comparison = "--save-prd-comparison" in sys.argv
    
    if not Path(prd_file).exists():
        print(f"❌ File not found: {prd_file}")
        sys.exit(1)
    
    try:
        # Analisar PRD
        results = await analyze_prd_file(prd_file, verbose, interactive)
        
        if not results:
            print("❌ Analysis failed")
            sys.exit(1)
        
        # Salvar comparação PRD se solicitado
        if save_comparison and 'prd_enhancement' in results:
            enhancement = results['prd_enhancement']
            if enhancement['was_enhanced']:
                orig_file, enhanced_file, comparison_file = _save_prd_comparison(
                    enhancement['original_prd'], 
                    enhancement['enhanced_prd'], 
                    results['project']['name']
                )
                print(f"\n📄 PRD comparison saved:")
                print(f"   • Original: {orig_file}")
                print(f"   • Enhanced: {enhanced_file}")
                print(f"   • Comparison: {comparison_file}")
        
        # Output
        if json_output:
            output_file = f"{results['project']['name'].lower().replace(' ', '_')}_analysis.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Results saved to: {output_file}")
        else:
            display_results(results, verbose)
            
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        if verbose:
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(main())