#!/usr/bin/env python3
"""
WasTask - Demo do Gerador Inteligente
Demonstração das capacidades de análise e geração inteligente de tarefas
"""
import sys
import os
import asyncio
import uuid
import subprocess
from pathlib import Path

# Adicionar path atual
sys.path.insert(0, os.path.abspath('..'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
import time

console = Console()

# Importar módulos
from ai_engine.intelligent_task_generator import intelligent_generator
from wastask.mock_adk import LlmAgent

class WasTaskIntelligentDemo:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        
        # IA Agent
        self.ia_agent = LlmAgent(
            name="intelligent_demo",
            model="wastask-intelligent",
            description="Demo do sistema inteligente"
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
    
    def testar_analise_inteligente(self):
        """Testar análise de diferentes tipos de projetos"""
        console.print("\\n[bold cyan]🧠 Testando Análise Inteligente de Projetos[/bold cyan]")
        
        projetos_teste = [
            {
                "name": "EcoMarket - Marketplace Verde",
                "description": "Plataforma de e-commerce sustentável com produtos ecológicos, sistema de pagamentos, carrinho de compras, gestão de estoque, dashboard administrativo e app mobile. Integração com AWS e Docker."
            },
            {
                "name": "MedAssist - Prontuário Digital",
                "description": "Sistema de saúde com telemedicina, prontuário eletrônico, agendamento de consultas, prescrições digitais, conformidade LGPD, integração com equipamentos médicos e app para pacientes."
            },
            {
                "name": "EduTech AI - Plataforma de Ensino",
                "description": "Sistema de educação online com inteligência artificial, machine learning para recomendações, videoaulas, avaliações automáticas, analytics de aprendizado e algoritmos de personalização."
            }
        ]
        
        for i, projeto in enumerate(projetos_teste, 1):
            console.print(f"\\n[bold green]📋 Teste {i}: {projeto['name']}[/bold green]")
            console.print(f"[dim]{projeto['description']}[/dim]")
            
            # Análise
            with console.status("🔍 Analisando projeto..."):
                analysis = intelligent_generator.analyze_project(projeto['name'], projeto['description'])
            
            # Mostrar análise
            table = Table(title=f"🔍 Análise: {projeto['name']}")
            table.add_column("Aspecto", style="cyan")
            table.add_column("Resultado", style="green")
            
            table.add_row("Domínio", analysis.domain.title())
            table.add_row("Complexidade", analysis.estimated_complexity)
            table.add_row("Stack Técnica", ", ".join(analysis.technology_stack) if analysis.technology_stack else "Não detectada")
            table.add_row("Req. Técnicos", ", ".join(analysis.technical_requirements) if analysis.technical_requirements else "Básicos")
            table.add_row("Req. Negócio", ", ".join(analysis.business_requirements) if analysis.business_requirements else "Genéricos")
            
            console.print(table)
            
            # Gerar tarefas customizadas
            console.print(f"\\n[bold blue]🤖 Tarefas Geradas pela IA:[/bold blue]")
            tarefas = intelligent_generator.generate_custom_tasks(projeto['name'], projeto['description'], 8)
            
            for j, (tarefa, prioridade) in enumerate(tarefas, 1):
                priority_emoji = {
                    "CRITICAL": "🔴",
                    "HIGH": "🟠", 
                    "MEDIUM": "🟡",
                    "LOW": "🟢"
                }
                emoji = priority_emoji.get(prioridade.value, "⚪")
                console.print(f"  {j}. {emoji} {tarefa}")
            
            if i < len(projetos_teste):
                time.sleep(2)  # Pausa automática
    
    def testar_comparacao(self):
        """Comparar geração tradicional vs inteligente"""
        console.print("\\n[bold cyan]⚖️ Comparação: Templates vs IA Inteligente[/bold cyan]")
        
        projeto_teste = {
            "name": "SmartFinance - FinTech Crypto",
            "description": "Plataforma financeira com criptomoedas, blockchain, trading automatizado, machine learning para análise de risco, conformidade regulatória, segurança bancária e mobile banking."
        }
        
        console.print(f"\\n[bold]📋 Projeto de Teste:[/bold] {projeto_teste['name']}")
        console.print(f"[dim]{projeto_teste['description']}[/dim]")
        
        # Geração inteligente
        console.print("\\n[bold green]🧠 Geração Inteligente (Análise + Customização):[/bold green]")
        tarefas_inteligentes = intelligent_generator.generate_custom_tasks(
            projeto_teste['name'], 
            projeto_teste['description'], 
            10
        )
        
        for i, (tarefa, prioridade) in enumerate(tarefas_inteligentes, 1):
            priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
            emoji = priority_emoji.get(prioridade.value, "⚪")
            console.print(f"  {i}. {emoji} {tarefa}")
        
        console.print("\\n[bold blue]📊 Vantagens da Geração Inteligente:[/bold blue]")
        console.print("  ✅ Análise automática do contexto")
        console.print("  ✅ Detecção de tecnologias mencionadas")
        console.print("  ✅ Identificação de requisitos específicos")
        console.print("  ✅ Priorização baseada no domínio")
        console.print("  ✅ Tarefas completamente customizadas")
        console.print("  ✅ Evita duplicações e redundâncias")
    
    async def salvar_projeto_inteligente(self):
        """Salvar um projeto gerado inteligentemente no banco"""
        if not self.db:
            return
        
        console.print("\\n[bold cyan]💾 Salvando Projeto Inteligente no PostgreSQL[/bold cyan]")
        
        projeto_demo = {
            "name": "GreenTech IoT - Agricultura Inteligente",
            "description": "Sistema IoT para agricultura sustentável com sensores, machine learning para predição de safras, dashboard web, app mobile, APIs REST, integração com drones, banco de dados temporal e conformidade ambiental."
        }
        
        # Criar projeto
        projeto = self.db.criar_projeto(
            projeto_demo['name'], 
            projeto_demo['description'], 
            self.usuario_id
        )
        console.print(f"✅ Projeto criado: {projeto.name}")
        
        # Gerar tarefas
        tarefas_geradas = intelligent_generator.generate_custom_tasks(
            projeto_demo['name'], 
            projeto_demo['description'], 
            12
        )
        
        # Salvar no banco
        console.print("💾 Salvando tarefas...")
        for titulo, prioridade in track(tarefas_geradas, description="Salvando..."):
            self.db.criar_tarefa(
                title=titulo,
                description=f"Tarefa gerada pelo sistema inteligente do WasTask",
                project_id=str(projeto.id),
                creator_id=self.usuario_id,
                priority=prioridade
            )
            time.sleep(0.1)
        
        console.print(f"✅ {len(tarefas_geradas)} tarefas salvas no PostgreSQL!")
        
        # Estatísticas
        stats = self.db.get_stats()
        console.print(f"\\n📊 Total no sistema: {stats['projetos']} projetos, {stats['tarefas']} tarefas")
    
    async def executar_demo_inteligente(self):
        """Demo completo do sistema inteligente"""
        console.print(Panel(
            "[bold blue]🧠 WasTask - Demo Sistema Inteligente[/bold blue]\\n\\n"
            "[cyan]Análise automática e geração customizada de tarefas[/cyan]\\n"
            "[yellow]✨ Powered by AI Analysis ✨[/yellow]",
            expand=False
        ))
        
        # 1. Testar análise inteligente
        self.testar_analise_inteligente()
        
        # 2. Comparação
        self.testar_comparacao()
        
        # 3. Integração com PostgreSQL
        if self.verificar_postgres() and self.conectar_banco():
            await self.salvar_projeto_inteligente()
        
        console.print(f"\\n[bold green]🎉 Demo do Sistema Inteligente Concluído![/bold green]")
        console.print(f"🧠 Sistema analisa contexto automaticamente")
        console.print(f"⚡ Gera tarefas completamente customizadas")
        console.print(f"🎯 Priorização inteligente baseada no domínio")

async def main():
    """Função principal"""
    try:
        demo = WasTaskIntelligentDemo()
        await demo.executar_demo_inteligente()
    except KeyboardInterrupt:
        console.print("\\n👋 Demo interrompido")
    except Exception as e:
        console.print(f"\\n❌ Erro inesperado: {e}")

if __name__ == '__main__':
    asyncio.run(main())