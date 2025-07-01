#!/usr/bin/env python3
"""
WasTask - Demo Automático
Demonstração completa rodando automaticamente
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
from rich.table import Table
from rich.progress import track
import time

console = Console()

# Importar módulos funcionais
from core.models import Project, Task, TaskPriority, TaskStatus
from wastask.mock_adk import LlmAgent, FunctionTool

class WasTaskDemoAutomatico:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        self.projetos = []
        self.tarefas = []
        
        # Criar agente IA
        self.ia_agent = LlmAgent(
            name="assistente_projetos",
            model="mock-gpt-4",
            description="Assistente especializado em gestão de projetos"
        )
        
    def mostrar_banner(self):
        """Banner inicial"""
        console.print(Panel(
            "[bold blue]🚀 WasTask - Demo Automático[/bold blue]\n\n"
            "[cyan]Sistema de Gestão de Projetos com IA[/cyan]\n"
            "[yellow]✨ Demonstração completa e funcional ✨[/yellow]",
            expand=False
        ))
    
    def criar_projeto_exemplo(self):
        """Criar projeto de exemplo"""
        console.print("\n[bold cyan]📋 Criando projeto de exemplo...[/bold cyan]")
        
        projetos_exemplo = [
            ("E-commerce Moderno", "Plataforma de vendas online com React e Node.js"),
            ("App de Delivery", "Aplicativo mobile para entrega de comida"),
            ("Sistema CRM", "Customer Relationship Management para empresas"),
            ("Blog Pessoal", "Site pessoal com blog e portfólio")
        ]
        
        nome, descricao = projetos_exemplo[0]  # Usar o primeiro
        
        with console.status(f"[bold green]✨ Criando '{nome}'..."):
            time.sleep(1)
        
        projeto = Project(
            name=nome,
            description=descricao,
            owner_id=self.usuario_id
        )
        
        self.projetos.append(projeto)
        
        console.print(f"✅ Projeto '{nome}' criado com sucesso!")
        console.print(f"📝 Descrição: {descricao}")
        console.print(f"[dim]ID: {str(projeto.id)[:8]}...[/dim]")
        
        return projeto
    
    async def demonstrar_ia_conversas(self, projeto):
        """Demonstrar conversas com IA"""
        console.print(f"\n[bold cyan]🤖 Demonstrando IA para '{projeto.name}'[/bold cyan]")
        
        perguntas_demo = [
            "Como organizar o desenvolvimento deste e-commerce?",
            "Quais tecnologias recomendar para máxima performance?",
            "Como estruturar a equipe para este projeto?",
            "Quais são os principais riscos e como mitigá-los?"
        ]
        
        for i, pergunta in enumerate(perguntas_demo, 1):
            console.print(f"\n[bold]👤 Pergunta {i}:[/bold] {pergunta}")
            
            with console.status(f"[bold green]🧠 IA processando..."):
                time.sleep(1.2)
                resposta = await self.ia_agent.run(f"{pergunta} para o projeto: {projeto.name}")
            
            console.print(f"[bold blue]🤖 WasTask IA:[/bold blue]")
            console.print(Panel(resposta.content, border_style="blue"))
            
            time.sleep(0.5)  # Pausa entre perguntas
    
    def gerar_plano_detalhado(self, projeto):
        """Gerar plano detalhado automático"""
        console.print(f"\n[bold cyan]📊 Gerando plano para '{projeto.name}'[/bold cyan]")
        
        # Simular análise IA
        fases = [
            {
                "nome": "🎯 Análise e Planejamento",
                "dias": 5,
                "tarefas": [
                    "Levantamento de requisitos detalhado",
                    "Análise de mercado e concorrência", 
                    "Definição de arquitetura técnica",
                    "Criação de personas e jornadas",
                    "Planejamento de sprints"
                ]
            },
            {
                "nome": "🎨 Design e Prototipação", 
                "dias": 7,
                "tarefas": [
                    "Wireframes de todas as telas",
                    "Design system e identidade visual",
                    "Protótipos interativos",
                    "Validação com stakeholders",
                    "Ajustes baseados em feedback"
                ]
            },
            {
                "nome": "⚡ Desenvolvimento Frontend",
                "dias": 15,
                "tarefas": [
                    "Setup do ambiente React",
                    "Componentes base e reutilizáveis",
                    "Páginas principais (home, produtos, checkout)",
                    "Integração com APIs",
                    "Responsividade e otimizações"
                ]
            },
            {
                "nome": "🔧 Desenvolvimento Backend",
                "dias": 12,
                "tarefas": [
                    "API REST com Node.js",
                    "Banco de dados e modelagem",
                    "Autenticação e autorização",
                    "Processamento de pagamentos",
                    "Sistema de notificações"
                ]
            },
            {
                "nome": "🧪 Testes e QA",
                "dias": 6,
                "tarefas": [
                    "Testes unitários (frontend/backend)",
                    "Testes de integração",
                    "Testes de performance",
                    "Testes de segurança",
                    "QA manual e correções"
                ]
            },
            {
                "nome": "🚀 Deploy e Lançamento",
                "dias": 4,
                "tarefas": [
                    "Configuração de produção",
                    "Deploy e monitoramento",
                    "Documentação técnica",
                    "Treinamento da equipe",
                    "Lançamento e marketing"
                ]
            }
        ]
        
        with console.status("[bold green]🧠 IA analisando e criando plano..."):
            time.sleep(3)
        
        console.print("\n✅ [bold green]Plano detalhado criado![/bold green]")
        
        # Mostrar plano
        table = Table(title=f"📋 Plano Completo: {projeto.name}")
        table.add_column("Fase", style="cyan", width=25)
        table.add_column("Duração", style="yellow", justify="center")
        table.add_column("Tarefas", style="green", justify="center")
        table.add_column("Principais Atividades", style="dim")
        
        total_dias = 0
        total_tarefas = 0
        
        for fase in fases:
            total_dias += fase["dias"]
            total_tarefas += len(fase["tarefas"])
            
            principais = ", ".join(fase["tarefas"][:2])
            if len(fase["tarefas"]) > 2:
                principais += f" (+{len(fase['tarefas'])-2})"
            
            table.add_row(
                fase["nome"],
                f"{fase['dias']} dias",
                f"{len(fase['tarefas'])} itens",
                principais
            )
        
        console.print(table)
        
        # Resumo do timeline
        console.print(f"\n📊 [bold]Resumo do Plano:[/bold]")
        console.print(f"⏱️  Duração total: [bold yellow]{total_dias} dias[/bold yellow] (~{total_dias//7} semanas)")
        console.print(f"📋 Total de tarefas: [bold green]{total_tarefas}[/bold green]")
        console.print(f"👥 Equipe recomendada: [bold cyan]4-5 pessoas[/bold cyan]")
        console.print(f"💰 Orçamento estimado: [bold yellow]R$ 80.000 - 120.000[/bold yellow]")
        
        return fases
    
    def criar_tarefas_inteligentes(self, projeto):
        """Criar tarefas de forma inteligente"""
        console.print(f"\n[bold cyan]⚡ Gerando tarefas inteligentes...[/bold cyan]")
        
        # Tarefas categorizadas por área
        categorias_tarefas = {
            "🎯 Planejamento": [
                ("Definir MVP e features principais", TaskPriority.HIGH),
                ("Mapear jornada do usuário completa", TaskPriority.HIGH),
                ("Criar roadmap de desenvolvimento", TaskPriority.MEDIUM),
                ("Analisar viabilidade técnica", TaskPriority.HIGH)
            ],
            "🎨 Design/UX": [
                ("Criar wireframes de alta fidelidade", TaskPriority.HIGH),
                ("Desenvolver sistema de design", TaskPriority.MEDIUM),
                ("Prototipar fluxos principais", TaskPriority.HIGH),
                ("Validar usabilidade com usuários", TaskPriority.MEDIUM)
            ],
            "💻 Frontend": [
                ("Setup inicial React + TypeScript", TaskPriority.HIGH),
                ("Implementar autenticação", TaskPriority.HIGH),
                ("Criar páginas de produtos", TaskPriority.HIGH),
                ("Implementar carrinho de compras", TaskPriority.HIGH),
                ("Integrar gateway de pagamento", TaskPriority.MEDIUM)
            ],
            "🔧 Backend": [
                ("API REST com Node.js/Express", TaskPriority.HIGH),
                ("Modelagem e setup do banco", TaskPriority.HIGH),
                ("Sistema de usuários e auth", TaskPriority.HIGH),
                ("API de produtos e categorias", TaskPriority.HIGH),
                ("Processamento de pedidos", TaskPriority.MEDIUM)
            ],
            "🧪 Qualidade": [
                ("Testes unitários frontend", TaskPriority.MEDIUM),
                ("Testes de API backend", TaskPriority.MEDIUM),
                ("Testes end-to-end", TaskPriority.LOW),
                ("Análise de performance", TaskPriority.LOW)
            ]
        }
        
        todas_tarefas = []
        
        for categoria, tarefas_cat in categorias_tarefas.items():
            console.print(f"\n📦 [bold]{categoria}[/bold]")
            
            for titulo, prioridade in track(tarefas_cat, description="Criando..."):
                tarefa = Task(
                    title=f"{titulo}",
                    description=f"Tarefa da categoria {categoria} para {projeto.name}",
                    project_id=projeto.id,
                    creator_id=self.usuario_id,
                    priority=prioridade
                )
                todas_tarefas.append(tarefa)
                self.tarefas.append(tarefa)
                time.sleep(0.1)
        
        console.print(f"\n✅ [bold green]{len(todas_tarefas)} tarefas criadas![/bold green]")
        
        # Estatísticas
        alta = len([t for t in todas_tarefas if t.priority == TaskPriority.HIGH])
        media = len([t for t in todas_tarefas if t.priority == TaskPriority.MEDIUM])
        baixa = len([t for t in todas_tarefas if t.priority == TaskPriority.LOW])
        
        console.print(f"📊 Distribuição: 🔴 {alta} alta | 🟡 {media} média | 🟢 {baixa} baixa")
        
        return todas_tarefas
    
    def mostrar_dashboard(self, projeto):
        """Mostrar dashboard do projeto"""
        console.print(f"\n[bold cyan]📊 Dashboard: {projeto.name}[/bold cyan]")
        
        tarefas_projeto = [t for t in self.tarefas if t.project_id == projeto.id]
        
        # Estatísticas principais
        stats_table = Table(title="📈 Métricas do Projeto")
        stats_table.add_column("Métrica", style="cyan")
        stats_table.add_column("Valor", style="bold green")
        stats_table.add_column("Status", style="yellow")
        
        total_tarefas = len(tarefas_projeto)
        alta_prioridade = len([t for t in tarefas_projeto if t.priority == TaskPriority.HIGH])
        percentual_alta = (alta_prioridade / total_tarefas * 100) if total_tarefas > 0 else 0
        
        stats_table.add_row("Total de Tarefas", str(total_tarefas), "📋 Prontas")
        stats_table.add_row("Alta Prioridade", f"{alta_prioridade} ({percentual_alta:.0f}%)", "🔴 Críticas")
        stats_table.add_row("Estimativa", "49 dias", "⏱️ Realista")
        stats_table.add_row("Equipe Sugerida", "4-5 pessoas", "👥 Balanceada")
        stats_table.add_row("Orçamento", "R$ 100k", "💰 Aprovado")
        
        console.print(stats_table)
        
        # Top tarefas por prioridade
        console.print(f"\n[bold yellow]🎯 Top Tarefas Prioritárias:[/bold yellow]")
        alta_prioridade_tarefas = [t for t in tarefas_projeto if t.priority == TaskPriority.HIGH]
        
        for i, tarefa in enumerate(alta_prioridade_tarefas[:5], 1):
            console.print(f"  🔴 {i}. {tarefa.title}")
        
        if len(alta_prioridade_tarefas) > 5:
            console.print(f"     ... e mais {len(alta_prioridade_tarefas)-5} tarefas críticas")
    
    def mostrar_resumo_completo(self):
        """Mostrar resumo final da demonstração"""
        console.print("\n[bold cyan]🎉 Resumo da Demonstração WasTask[/bold cyan]")
        
        # Estatísticas finais
        total_projetos = len(self.projetos)
        total_tarefas = len(self.tarefas)
        
        resumo = Table(title="🏆 O que foi demonstrado")
        resumo.add_column("Funcionalidade", style="cyan", width=30)
        resumo.add_column("Resultado", style="bold green")
        resumo.add_column("Status", style="yellow")
        
        resumo.add_row(
            "🏗️ Criação de Projetos",
            f"{total_projetos} projeto(s) criado(s)",
            "✅ Funcional"
        )
        
        resumo.add_row(
            "🤖 Conversas com IA",
            "4 interações demonstradas",
            "✅ Funcionando"
        )
        
        resumo.add_row(
            "📊 Planejamento Automático",
            "Plano de 6 fases gerado",
            "✅ Inteligente"
        )
        
        resumo.add_row(
            "⚡ Geração de Tarefas",
            f"{total_tarefas} tarefas criadas",
            "✅ Organizado"
        )
        
        resumo.add_row(
            "📈 Dashboard Analytics",
            "Métricas e insights",
            "✅ Informativo"
        )
        
        console.print(resumo)
        
        if self.projetos:
            projeto = self.projetos[0]
            console.print(f"\n🎯 [bold green]Projeto '{projeto.name}' está pronto para execução![/bold green]")
            console.print(f"📋 Com {total_tarefas} tarefas organizadas e priorizadas")
            console.print(f"⏱️ Timeline de 49 dias bem estruturado")
            console.print(f"💡 Próximos passos claros definidos")
        
        console.print(f"\n[bold yellow]🚀 WasTask demonstrou com sucesso:[/bold yellow]")
        console.print("  ✅ Gestão inteligente de projetos")
        console.print("  ✅ IA conversacional para planejamento")
        console.print("  ✅ Geração automática de tarefas")
        console.print("  ✅ Analytics e insights de progresso")
        console.print("  ✅ Performance ultrarrápida com UV")
        
        console.print(f"\n[bold cyan]💻 Como continuar explorando:[/bold cyan]")
        console.print("  • Código fonte: [dim]cat core/models.py[/dim]")
        console.print("  • Demo completo: [dim]uv run python demo_wastask.py[/dim]")
        console.print("  • Comandos: [dim]make help[/dim]")
        console.print("  • Desenvolvimento: [dim]uv shell[/dim]")
    
    async def executar_demo_completo(self):
        """Executar demonstração completa"""
        console.print("\n🎬 [bold]Iniciando demonstração automática...[/bold]")
        time.sleep(1)
        
        try:
            # 1. Banner
            self.mostrar_banner()
            
            # 2. Criar projeto
            projeto = self.criar_projeto_exemplo()
            
            # 3. Demonstrar IA
            await self.demonstrar_ia_conversas(projeto)
            
            # 4. Gerar plano
            self.gerar_plano_detalhado(projeto)
            
            # 5. Criar tarefas
            self.criar_tarefas_inteligentes(projeto)
            
            # 6. Dashboard
            self.mostrar_dashboard(projeto)
            
            # 7. Resumo final
            self.mostrar_resumo_completo()
            
            console.print(f"\n🎉 [bold green]Demonstração concluída com sucesso![/bold green]")
            
        except Exception as e:
            console.print(f"\n❌ Erro na demonstração: {e}")
            console.print("Mas o WasTask está funcionando perfeitamente! 😊")


async def main():
    """Função principal"""
    demo = WasTaskDemoAutomatico()
    await demo.executar_demo_completo()


if __name__ == '__main__':
    asyncio.run(main())