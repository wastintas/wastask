#!/usr/bin/env python3
"""
WasTask - Demo Dinâmico com IA
Demonstração do sistema totalmente dinâmico com geração inteligente de projetos e tarefas
"""
import sys
import os
import asyncio
import uuid
import subprocess
from pathlib import Path

# Adicionar path atual
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.progress import track
import time

console = Console()

# Importar módulos
from templates.project_templates import ProjectType, template_manager
from ai_engine.intelligent_task_generator import intelligent_generator
from wastask.mock_adk import LlmAgent

class WasTaskDynamicDemo:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        
        # IA Agent
        self.ia_agent = LlmAgent(
            name="dynamic_assistant",
            model="wastask-dynamic",
            description="Assistente dinâmico para criação de projetos"
        )
        
        # Database manager (será inicializado depois)
        self.db = None
    
    def verificar_postgres(self):
        """Verificar se PostgreSQL está disponível"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=wastask-postgres", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            return "wastask-postgres" in result.stdout
        except:
            return False
    
    def conectar_banco(self):
        """Conectar ao banco PostgreSQL"""
        try:
            from database import DatabaseManager
            
            console.print("🔌 Conectando ao PostgreSQL...")
            self.db = DatabaseManager("postgresql://wastask:password@127.0.0.1:5433/wastask")
            self.db.create_tables()
            console.print("✅ Conectado ao PostgreSQL!")
            return True
            
        except Exception as e:
            console.print(f"❌ Erro ao conectar: {e}")
            console.print("💡 Execute: docker run -d --name wastask-postgres -e POSTGRES_DB=wastask -e POSTGRES_USER=wastask -e POSTGRES_PASSWORD=password -p 5433:5432 postgres:15-alpine")
            return False
    
    def mostrar_tipos_projeto(self):
        """Mostrar tipos de projeto disponíveis"""
        console.print("\\n[bold cyan]📋 Tipos de Projeto Disponíveis[/bold cyan]")
        
        table = Table(title="🎯 Templates Inteligentes")
        table.add_column("Opção", style="cyan", width=8)
        table.add_column("Tipo", style="bold green", width=20)
        table.add_column("Complexidade", style="yellow", width=15)
        table.add_column("Tarefas Sugeridas", style="blue", width=18)
        
        tipos = list(ProjectType)
        for i, project_type in enumerate(tipos, 1):
            template = template_manager.get_template(project_type)
            table.add_row(
                str(i),
                project_type.value.replace("-", " ").title(),
                template.complexity_level,
                str(template.suggested_task_count)
            )
        
        console.print(table)
        return tipos
    
    def escolher_tipo_projeto(self):
        """Interface para escolha do tipo de projeto"""
        tipos = self.mostrar_tipos_projeto()
        
        while True:
            try:
                choice = IntPrompt.ask(
                    "\\n[bold]Escolha o tipo de projeto",
                    default=1,
                    show_default=True
                )
                if 1 <= choice <= len(tipos):
                    return tipos[choice - 1]
                else:
                    console.print(f"❌ Escolha entre 1 e {len(tipos)}")
            except:
                console.print("❌ Digite um número válido")
    
    def configurar_projeto(self, project_type: ProjectType):
        """Configurar projeto interativamente"""
        console.print(f"\\n[bold cyan]⚙️ Configurando Projeto: {project_type.value.title()}[/bold cyan]")
        
        # Obter sugestões da IA
        suggestions = template_manager.get_suggestions(project_type)
        
        # Nome do projeto
        suggested_name = random.choice(suggestions['name_suggestions'])
        console.print(f"\\n[bold]💡 Sugestão:[/bold] {suggested_name}")
        nome = Prompt.ask(
            "[bold]Nome do projeto[/bold]",
            default=suggested_name
        )
        
        # Descrição
        features_sample = random.sample(suggestions['features'], min(3, len(suggestions['features'])))
        suggested_desc = suggestions['description_template'].format(features=", ".join(features_sample))
        console.print(f"\\n[bold]💡 Sugestão:[/bold] {suggested_desc}")
        descricao = Prompt.ask(
            "[bold]Descrição do projeto[/bold]",
            default=suggested_desc
        )
        
        # Número de tarefas
        num_tarefas = IntPrompt.ask(
            f"[bold]Quantas tarefas gerar?[/bold]",
            default=suggestions['suggested_tasks'],
            show_default=True
        )
        
        # Confirmação
        console.print(f"\\n[bold green]📋 Resumo do Projeto:[/bold green]")
        console.print(f"  • Nome: {nome}")
        console.print(f"  • Tipo: {project_type.value}")
        console.print(f"  • Descrição: {descricao}")
        console.print(f"  • Tarefas: {num_tarefas}")
        console.print(f"  • Complexidade: {suggestions['complexity']}")
        
        # Mostrar análise inteligente
        analysis = intelligent_generator.analyze_project(nome, descricao)
        console.print(f"\\n[bold blue]🔍 Análise Inteligente:[/bold blue]")
        console.print(f"  • Domínio: {analysis.domain.title()}")
        console.print(f"  • Complexidade IA: {analysis.estimated_complexity}")
        if analysis.technology_stack:
            console.print(f"  • Stack: {', '.join(analysis.technology_stack)}")
        
        if Confirm.ask("\\n[bold]Confirma a criação?[/bold]", default=True):
            return nome, descricao, num_tarefas
        else:
            return None, None, None
    
    def criar_projeto_dinamico(self, nome: str, descricao: str, project_type: ProjectType, num_tarefas: int):
        """Criar projeto no banco com geração dinâmica"""
        console.print(f"\\n[bold cyan]🏗️ Criando projeto: '{nome}'[/bold cyan]")
        
        try:
            projeto = self.db.criar_projeto(nome, descricao, self.usuario_id)
            console.print(f"✅ Projeto criado!")
            console.print(f"🆔 ID: {str(projeto.id)[:8]}...")
            console.print(f"📅 Criado: {projeto.created_at}")
            return projeto
            
        except Exception as e:
            console.print(f"❌ Erro ao criar projeto: {e}")
            return None
    
    def gerar_tarefas_ia(self, projeto, project_type: ProjectType, num_tarefas: int):
        """Gerar tarefas usando IA"""
        console.print(f"\\n[bold cyan]🤖 Gerando tarefas com IA...[/bold cyan]")
        
        with console.status("🧠 IA analisando projeto e gerando tarefas customizadas..."):
            time.sleep(2)  # Simular processamento
            
            # Gerar tarefas usando IA inteligente
            tarefas_geradas = intelligent_generator.generate_custom_tasks(
                name=projeto.name,
                description=projeto.description,
                num_tasks=num_tarefas
            )
            
            # Mostrar análise detalhada
            analysis = intelligent_generator.analyze_project(projeto.name, projeto.description)
        
        console.print(f"✅ {len(tarefas_geradas)} tarefas customizadas geradas!")
        
        # Mostrar explicação da análise
        console.print("\\n[bold blue]🔍 Análise da IA:[/bold blue]")
        console.print(f"  • Domínio detectado: {analysis.domain.title()}")
        console.print(f"  • Complexidade: {analysis.estimated_complexity}")
        if analysis.technical_requirements:
            console.print(f"  • Requisitos técnicos: {', '.join(analysis.technical_requirements)}")
        if analysis.technology_stack:
            console.print(f"  • Stack detectada: {', '.join(analysis.technology_stack)}")
        
        
        # Mostrar preview das tarefas
        console.print("\\n[bold green]📋 Tarefas Geradas:[/bold green]")
        for i, (titulo, prioridade) in enumerate(tarefas_geradas[:5], 1):
            priority_emoji = {
                "CRITICAL": "🔴",
                "HIGH": "🟠", 
                "MEDIUM": "🟡",
                "LOW": "🟢"
            }
            emoji = priority_emoji.get(prioridade.value, "⚪")
            console.print(f"  {i}. {emoji} {titulo}")
        
        if len(tarefas_geradas) > 5:
            console.print(f"  ... e mais {len(tarefas_geradas) - 5} tarefas")
        
        return tarefas_geradas
    
    def salvar_tarefas_banco(self, projeto_id, tarefas_geradas):
        """Salvar tarefas no PostgreSQL"""
        console.print(f"\\n[bold cyan]💾 Salvando tarefas no PostgreSQL...[/bold cyan]")
        
        tarefas_criadas = []
        
        for titulo, prioridade in track(tarefas_geradas, description="Salvando no banco..."):
            try:
                tarefa = self.db.criar_tarefa(
                    title=titulo,
                    description=f"Tarefa gerada automaticamente pela IA do WasTask",
                    project_id=str(projeto_id),
                    creator_id=self.usuario_id,
                    priority=prioridade
                )
                tarefas_criadas.append(tarefa)
                time.sleep(0.05)  # Efeito visual
                
            except Exception as e:
                console.print(f"⚠️ Erro ao salvar '{titulo}': {e}")
        
        console.print(f"✅ {len(tarefas_criadas)} tarefas salvas!")
        return tarefas_criadas
    
    async def conversa_ia_contexto(self, projeto):
        """Conversa contextual com IA sobre o projeto"""
        console.print(f"\\n[bold cyan]🤖 Conversa com IA sobre o projeto[/bold cyan]")
        
        pergunta = f"Como você recomenda estruturar o projeto '{projeto.name}'? Quais são os principais desafios?"
        
        with console.status("🧠 IA analisando..."):
            time.sleep(1.5)
            resposta_ia = await self.ia_agent.run(pergunta)
        
        # Salvar conversa
        try:
            await self.salvar_conversa_banco(projeto.id, pergunta, resposta_ia.content)
        except:
            pass
        
        console.print(f"[bold]👤 Pergunta:[/bold] {pergunta}")
        console.print(f"[bold blue]🤖 IA:[/bold blue] {resposta_ia.content}")
    
    async def salvar_conversa_banco(self, projeto_id, pergunta, resposta):
        """Salvar conversa no banco"""
        try:
            self.db.salvar_conversa(
                projeto_id=str(projeto_id),
                usuario_id=self.usuario_id,
                pergunta=pergunta,
                resposta=resposta,
                agent_type="dynamic_assistant"
            )
            console.print("💬 Conversa salva!")
        except Exception as e:
            console.print(f"⚠️ Erro ao salvar conversa: {e}")
    
    def mostrar_estatisticas_finais(self):
        """Mostrar estatísticas do banco"""
        console.print(f"\\n[bold cyan]📊 Estatísticas Finais[/bold cyan]")
        
        try:
            stats = self.db.get_stats()
            
            table = Table(title="📈 Status do Sistema")
            table.add_column("Métrica", style="cyan")
            table.add_column("Quantidade", style="bold green")
            table.add_column("Status", style="yellow")
            
            table.add_row("Projetos", str(stats["projetos"]), "🏗️ Ativos")
            table.add_row("Tarefas Total", str(stats["tarefas"]), "📋 Criadas")
            table.add_row("Tarefas Pendentes", str(stats["tarefas_pendentes"]), "⏳ Aguardando")
            table.add_row("Tarefas Críticas", str(stats.get("tarefas_criticas", 0)), "🔴 Urgentes")
            table.add_row("Conversas IA", str(stats["conversas"]), "💬 Registradas")
            
            console.print(table)
            
        except Exception as e:
            console.print(f"❌ Erro ao obter estatísticas: {e}")
    
    async def executar_demo_dinamico(self):
        """Demo completo dinâmico"""
        console.print(Panel(
            "[bold blue]🚀 WasTask - Demo Dinâmico com IA[/bold blue]\\n\\n"
            "[cyan]Sistema inteligente de geração de projetos[/cyan]\\n"
            "[yellow]✨ Totalmente configurável pela IA ✨[/yellow]",
            expand=False
        ))
        
        # 1. Verificar PostgreSQL
        if not self.verificar_postgres():
            console.print("❌ PostgreSQL não encontrado. Inicie com:")
            console.print("docker run -d --name wastask-postgres -e POSTGRES_DB=wastask -e POSTGRES_USER=wastask -e POSTGRES_PASSWORD=password -p 5433:5432 postgres:15-alpine")
            return
        
        # 2. Conectar ao banco
        if not self.conectar_banco():
            return
        
        # 3. Escolher tipo de projeto
        project_type = self.escolher_tipo_projeto()
        
        # 4. Configurar projeto
        nome, descricao, num_tarefas = self.configurar_projeto(project_type)
        if not nome:
            console.print("❌ Criação cancelada")
            return
        
        # 5. Criar projeto
        projeto = self.criar_projeto_dinamico(nome, descricao, project_type, num_tarefas)
        if not projeto:
            return
        
        # 6. Gerar tarefas com IA
        tarefas_geradas = self.gerar_tarefas_ia(projeto, project_type, num_tarefas)
        
        # 7. Salvar no banco
        tarefas_criadas = self.salvar_tarefas_banco(projeto.id, tarefas_geradas)
        
        # 8. Conversa contextual
        await self.conversa_ia_contexto(projeto)
        
        # 9. Estatísticas finais
        self.mostrar_estatisticas_finais()
        
        console.print(f"\\n[bold green]🎉 Projeto '{nome}' criado com sucesso![/bold green]")
        console.print(f"📊 {len(tarefas_criadas)} tarefas geradas pela IA")
        console.print(f"💾 Todos os dados salvos no PostgreSQL")
        console.print(f"🔄 Execute novamente para criar outro projeto!")

async def main():
    """Função principal"""
    try:
        demo = WasTaskDynamicDemo()
        await demo.executar_demo_dinamico()
    except KeyboardInterrupt:
        console.print("\\n👋 Demo interrompido")
    except Exception as e:
        console.print(f"\\n❌ Erro inesperado: {e}")

if __name__ == '__main__':
    asyncio.run(main())