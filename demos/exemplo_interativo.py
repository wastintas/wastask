#!/usr/bin/env python3
"""
WasTask - Exemplo Interativo Simples
Demonstração prática das funcionalidades
"""
import sys
import os
import asyncio
import uuid
from datetime import datetime

# Adicionar path atual
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.progress import track
import time

console = Console()

# Importar módulos do WasTask
from core.models import Project, Task, TaskPriority, TaskStatus
from agents.coordinator.agent import coordinator
from agents.planning.agent import planning_agent

class WasTaskDemo:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        self.projetos = []
        self.tarefas = []
        
    def mostrar_banner(self):
        """Mostrar banner inicial"""
        console.print(Panel(
            "[bold blue]🚀 WasTask - Demo Interativo[/bold blue]\n\n"
            "[cyan]Sistema de Gestão de Projetos com IA[/cyan]\n"
            "[dim]Pressione Ctrl+C para sair a qualquer momento[/dim]",
            expand=False
        ))
    
    async def criar_projeto_interativo(self):
        """Criar projeto com input do usuário"""
        console.print("\n[bold cyan]📋 Vamos criar um projeto![/bold cyan]")
        
        nome = Prompt.ask("Nome do projeto", default="Meu Projeto Incrível")
        descricao = Prompt.ask("Descrição breve", default="Um projeto revolucionário")
        
        # Simular processamento
        with console.status("[bold green]Criando projeto..."):
            time.sleep(1)
        
        projeto = Project(
            name=nome,
            description=descricao,
            owner_id=self.usuario_id
        )
        
        self.projetos.append(projeto)
        
        console.print(f"✅ Projeto '{nome}' criado com sucesso!")
        console.print(f"[dim]ID: {projeto.id}[/dim]")
        
        return projeto
    
    async def conversar_com_ia(self, projeto):
        """Conversa interativa com IA"""
        console.print(f"\n[bold cyan]💬 Conversando com IA sobre '{projeto.name}'[/bold cyan]")
        
        mensagens_exemplo = [
            f"Olá! Preciso de ajuda com o projeto '{projeto.name}'. {projeto.description}",
            "Quais seriam as principais tarefas para este projeto?",
            "Como você sugere organizar as prioridades?",
            "Qual seria um cronograma realista?"
        ]
        
        console.print("\n[yellow]Escolha uma pergunta ou digite a sua:[/yellow]")
        for i, msg in enumerate(mensagens_exemplo, 1):
            console.print(f"  {i}. {msg}")
        
        escolha = Prompt.ask("\nSua escolha (1-4 ou digite sua pergunta)", default="1")
        
        if escolha.isdigit() and 1 <= int(escolha) <= 4:
            mensagem = mensagens_exemplo[int(escolha) - 1]
        else:
            mensagem = escolha
        
        console.print(f"\n[bold]Você:[/bold] {mensagem}")
        
        # Processar com IA
        with console.status("[bold green]🤖 IA pensando..."):
            response = await coordinator.process_message(
                user_id=self.usuario_id,
                message=mensagem,
                project_id=str(projeto.id)
            )
        
        console.print(f"\n[bold blue]🤖 WasTask IA:[/bold blue]")
        console.print(Panel(response.response, border_style="blue"))
        
        if response.suggestions:
            console.print("\n[yellow]💡 Sugestões:[/yellow]")
            for suggestion in response.suggestions:
                console.print(f"  • {suggestion}")
        
        return response
    
    async def criar_plano_automatico(self, projeto):
        """Criar plano automático para o projeto"""
        console.print(f"\n[bold cyan]📊 Gerando plano automático para '{projeto.name}'[/bold cyan]")
        
        duracao = Prompt.ask("Duração máxima (dias)", default="30")
        equipe = Prompt.ask("Tamanho da equipe", default="2")
        
        with console.status("[bold green]🧠 IA criando plano detalhado..."):
            result = await planning_agent.create_project_plan(
                project_description=f"{projeto.name}: {projeto.description}",
                constraints={"max_duration_days": int(duracao)},
                preferences={"team_size": int(equipe), "methodology": "agile"}
            )
        
        if result['status'] == 'success':
            plan = result['plan']
            
            console.print("\n✅ [bold green]Plano criado com sucesso![/bold green]")
            
            # Mostrar resumo do plano
            table = Table(title=f"📋 Plano: {plan['project_summary']['title']}")
            table.add_column("Fase", style="cyan")
            table.add_column("Duração", style="yellow")
            table.add_column("Tarefas", style="green")
            
            for i, fase in enumerate(plan['phases'], 1):
                table.add_row(
                    f"{i}. {fase['name']}",
                    f"{fase['duration_days']} dias",
                    f"{len(fase.get('tasks', []))} tarefas"
                )
            
            console.print(table)
            
            # Mostrar timeline
            timeline = plan['timeline']
            console.print(f"\n⏱️  [bold]Timeline Total:[/bold] {timeline['total_duration_days']} dias")
            console.print(f"📅 Início: {timeline['start_date']}")
            console.print(f"🏁 Fim: {timeline['end_date']}")
            
            return plan
        else:
            console.print(f"❌ Erro ao criar plano: {result.get('message', 'Erro desconhecido')}")
            return None
    
    def criar_tarefas_rapidas(self, projeto):
        """Criar algumas tarefas rapidamente"""
        console.print(f"\n[bold cyan]⚡ Criando tarefas para '{projeto.name}'[/bold cyan]")
        
        tarefas_exemplo = [
            ("Configurar ambiente de desenvolvimento", TaskPriority.HIGH),
            ("Criar estrutura básica do projeto", TaskPriority.HIGH),
            ("Implementar funcionalidades principais", TaskPriority.MEDIUM),
            ("Escrever testes", TaskPriority.MEDIUM),
            ("Documentar o projeto", TaskPriority.LOW)
        ]
        
        for titulo, prioridade in track(tarefas_exemplo, description="Criando tarefas..."):
            tarefa = Task(
                title=titulo,
                description=f"Tarefa relacionada ao projeto {projeto.name}",
                project_id=projeto.id,
                creator_id=self.usuario_id,
                priority=prioridade
            )
            self.tarefas.append(tarefa)
            time.sleep(0.2)  # Efeito visual
        
        console.print(f"✅ {len(tarefas_exemplo)} tarefas criadas!")
        
        # Mostrar tarefas
        self.mostrar_tarefas(projeto)
    
    def mostrar_tarefas(self, projeto):
        """Mostrar tarefas do projeto"""
        tarefas_projeto = [t for t in self.tarefas if t.project_id == projeto.id]
        
        if not tarefas_projeto:
            console.print("📭 Nenhuma tarefa encontrada")
            return
        
        table = Table(title=f"📋 Tarefas do Projeto: {projeto.name}")
        table.add_column("Tarefa", style="cyan")
        table.add_column("Prioridade", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("Criada", style="dim")
        
        for tarefa in tarefas_projeto:
            cor_prioridade = {
                TaskPriority.HIGH: "red",
                TaskPriority.MEDIUM: "yellow", 
                TaskPriority.LOW: "green"
            }
            
            table.add_row(
                tarefa.title,
                f"[{cor_prioridade[tarefa.priority]}]{tarefa.priority.value}[/]",
                tarefa.status.value,
                tarefa.created_at.strftime("%H:%M")
            )
        
        console.print(table)
    
    def mostrar_resumo(self):
        """Mostrar resumo final"""
        console.print("\n[bold cyan]📊 Resumo da Sessão[/bold cyan]")
        
        resumo_table = Table(title="🎯 O que você criou hoje")
        resumo_table.add_column("Item", style="cyan")
        resumo_table.add_column("Quantidade", style="bold green")
        resumo_table.add_column("Detalhes", style="dim")
        
        resumo_table.add_row(
            "Projetos", 
            str(len(self.projetos)),
            ", ".join([p.name for p in self.projetos]) if self.projetos else "Nenhum"
        )
        
        resumo_table.add_row(
            "Tarefas",
            str(len(self.tarefas)),
            f"Distribuídas em {len(self.projetos)} projeto(s)"
        )
        
        console.print(resumo_table)
        
        console.print(f"\n[bold green]🎉 Parabéns! Você testou o WasTask com sucesso![/bold green]")
        console.print("\n[yellow]💡 Próximos passos:[/yellow]")
        console.print("  • Explore mais funcionalidades com: uv run python demo_wastask.py")
        console.print("  • Veja comandos disponíveis: make help")
        console.print("  • Desenvolva suas próprias funcionalidades!")
    
    async def executar_demo(self):
        """Executar demo completo"""
        try:
            self.mostrar_banner()
            
            # 1. Criar projeto
            projeto = await self.criar_projeto_interativo()
            
            # 2. Perguntar o que fazer
            console.print(f"\n[yellow]O que você gostaria de fazer com '{projeto.name}'?[/yellow]")
            
            opcoes = {
                "1": "💬 Conversar com IA sobre o projeto",
                "2": "📊 Gerar plano automático completo",
                "3": "⚡ Criar tarefas rapidamente",
                "4": "🎯 Fazer tudo acima",
                "5": "🏁 Finalizar demo"
            }
            
            for key, desc in opcoes.items():
                console.print(f"  {key}. {desc}")
            
            escolha = Prompt.ask("\nSua escolha", choices=list(opcoes.keys()), default="4")
            
            if escolha == "1" or escolha == "4":
                await self.conversar_com_ia(projeto)
            
            if escolha == "2" or escolha == "4":
                await self.criar_plano_automatico(projeto)
            
            if escolha == "3" or escolha == "4":
                self.criar_tarefas_rapidas(projeto)
            
            # Perguntar se quer continuar
            if escolha != "5":
                if Confirm.ask("\n🔄 Quer testar mais alguma coisa?"):
                    await self.conversar_com_ia(projeto)
            
            self.mostrar_resumo()
            
        except KeyboardInterrupt:
            console.print("\n\n👋 Demo interrompido. Até logo!")
        except Exception as e:
            console.print(f"\n❌ Erro inesperado: {e}")
            console.print("Mas não se preocupe, o WasTask está funcionando!")


async def main():
    """Função principal"""
    demo = WasTaskDemo()
    await demo.executar_demo()


if __name__ == '__main__':
    asyncio.run(main())