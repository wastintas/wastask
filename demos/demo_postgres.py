#!/usr/bin/env python3
"""
WasTask - Demo com PostgreSQL
Demonstração usando banco de dados real
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
from rich.progress import track
import time

console = Console()

# Importar módulos
from core.models import TaskPriority
from wastask.mock_adk import LlmAgent

class WasTaskPostgresDemo:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        
        # IA Agent
        self.ia_agent = LlmAgent(
            name="postgres_assistant",
            model="wastask-postgres",
            description="Assistente com PostgreSQL"
        )
        
        # Database manager (será inicializado depois)
        self.db = None
    
    def verificar_docker(self):
        """Verificar se Docker está disponível"""
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                console.print("✅ Docker está disponível")
                return True
            else:
                console.print("❌ Docker não encontrado")
                return False
        except FileNotFoundError:
            console.print("❌ Docker não instalado")
            return False
    
    def verificar_postgres_container(self):
        """Verificar se container PostgreSQL está rodando"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=wastask-postgres", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            return "wastask-postgres" in result.stdout
        except:
            return False
    
    def iniciar_postgres(self):
        """Iniciar container PostgreSQL"""
        console.print("\n[bold cyan]🐘 Configurando PostgreSQL...[/bold cyan]")
        
        if self.verificar_postgres_container():
            console.print("✅ Container PostgreSQL já está rodando")
            return True
        
        try:
            # Comando para iniciar PostgreSQL
            console.print("🚀 Iniciando container PostgreSQL...")
            
            cmd = [
                "docker", "run", "-d",
                "--name", "wastask-postgres",
                "-e", "POSTGRES_DB=wastask",
                "-e", "POSTGRES_USER=wastask", 
                "-e", "POSTGRES_PASSWORD=password",
                "-p", "5433:5432",
                "-v", f"{os.getcwd()}/init.sql:/docker-entrypoint-initdb.d/init.sql",
                "postgres:15-alpine"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ Container PostgreSQL iniciado!")
                console.print("⏳ Aguardando PostgreSQL ficar pronto...")
                time.sleep(5)  # Aguardar inicialização
                return True
            else:
                console.print(f"❌ Erro ao iniciar PostgreSQL: {result.stderr}")
                return False
        except Exception as e:
            console.print(f"❌ Erro: {e}")
            return False
    
    def conectar_banco(self):
        """Conectar ao banco e criar tabelas"""
        try:
            from database import DatabaseManager
            
            console.print("🔌 Conectando ao PostgreSQL...")
            
            # Criar manager do banco (porta 5433 para evitar conflito com PostgreSQL local)
            self.db = DatabaseManager("postgresql://wastask:password@127.0.0.1:5433/wastask")
            
            # Criar tabelas
            console.print("📊 Criando tabelas...")
            self.db.create_tables()
            
            console.print("✅ Conectado ao PostgreSQL com sucesso!")
            return True
            
        except Exception as e:
            console.print(f"❌ Erro ao conectar: {e}")
            console.print("💡 Certifique-se que o PostgreSQL está rodando: docker ps")
            return False
    
    def criar_projeto_banco(self, nome, descricao):
        """Criar projeto no banco PostgreSQL"""
        console.print(f"\n[bold cyan]🏗️ Criando projeto no PostgreSQL: '{nome}'[/bold cyan]")
        
        try:
            projeto = self.db.criar_projeto(nome, descricao, self.usuario_id)
            
            console.print(f"✅ Projeto salvo no PostgreSQL!")
            console.print(f"🆔 ID: {projeto.id}")
            console.print(f"📅 Criado: {projeto.created_at}")
            
            return projeto
            
        except Exception as e:
            console.print(f"❌ Erro ao criar projeto: {e}")
            return None
    
    def criar_tarefas_banco(self, projeto_id, lista_tarefas):
        """Criar tarefas no PostgreSQL"""
        console.print(f"\n[bold cyan]⚡ Criando tarefas no PostgreSQL...[/bold cyan]")
        
        tarefas_criadas = []
        
        for titulo, prioridade in track(lista_tarefas, description="Salvando no PostgreSQL..."):
            try:
                tarefa = self.db.criar_tarefa(
                    title=titulo,
                    description=f"Tarefa criada via WasTask PostgreSQL Demo",
                    project_id=str(projeto_id),
                    creator_id=self.usuario_id,
                    priority=prioridade
                )
                tarefas_criadas.append(tarefa)
                time.sleep(0.1)  # Efeito visual
                
            except Exception as e:
                console.print(f"⚠️ Erro ao criar tarefa '{titulo}': {e}")
        
        console.print(f"✅ {len(tarefas_criadas)} tarefas salvas no PostgreSQL!")
        return tarefas_criadas
    
    async def salvar_conversa_banco(self, projeto_id, pergunta, resposta):
        """Salvar conversa no banco"""
        try:
            conversa = self.db.salvar_conversa(
                projeto_id=str(projeto_id) if projeto_id else None,
                usuario_id=self.usuario_id,
                pergunta=pergunta,
                resposta=resposta,
                agent_type="coordinator"
            )
            console.print("💬 Conversa salva no PostgreSQL!")
            return conversa
        except Exception as e:
            console.print(f"⚠️ Erro ao salvar conversa: {e}")
            return None
    
    def mostrar_dados_banco(self):
        """Mostrar dados do banco"""
        console.print(f"\n[bold cyan]📊 Dados no PostgreSQL[/bold cyan]")
        
        try:
            # Obter estatísticas
            stats = self.db.get_stats()
            
            # Tabela de estatísticas
            table = Table(title="📈 Estatísticas do Banco")
            table.add_column("Métrica", style="cyan")
            table.add_column("Quantidade", style="bold green")
            table.add_column("Status", style="yellow")
            
            table.add_row("Projetos", str(stats["projetos"]), "🏗️ Ativos")
            table.add_row("Tarefas Total", str(stats["tarefas"]), "📋 Criadas")
            table.add_row("Tarefas Pendentes", str(stats["tarefas_pendentes"]), "⏳ Aguardando")
            table.add_row("Tarefas em Progresso", str(stats["tarefas_em_progresso"]), "🔄 Andamento")
            table.add_row("Tarefas Concluídas", str(stats["tarefas_concluidas"]), "✅ Finalizadas")
            table.add_row("Conversas IA", str(stats["conversas"]), "💬 Registradas")
            
            console.print(table)
            
            # Listar projetos
            projetos = self.db.listar_projetos()
            if projetos:
                console.print(f"\n[bold green]🏗️ Projetos no Banco:[/bold green]")
                for projeto in projetos[-3:]:  # Últimos 3
                    console.print(f"  • {projeto.name} (ID: {str(projeto.id)[:8]}...)")
            
            # Listar tarefas recentes
            tarefas = self.db.listar_tarefas()
            if tarefas:
                console.print(f"\n[bold green]⚡ Tarefas Recentes:[/bold green]")
                for tarefa in tarefas[-5:]:  # Últimas 5
                    console.print(f"  • {tarefa.title} ({tarefa.priority.value})")
            
            return stats
            
        except Exception as e:
            console.print(f"❌ Erro ao consultar banco: {e}")
            return {}
    
    def mostrar_comandos_banco(self):
        """Mostrar comandos para interagir com o banco"""
        console.print(f"\n[bold cyan]💻 Comandos PostgreSQL[/bold cyan]")
        
        console.print(f"[bold]Docker:[/bold]")
        console.print(f"  docker ps                          # Ver containers")
        console.print(f"  docker logs wastask-postgres       # Ver logs do PostgreSQL")
        console.print(f"  docker exec -it wastask-postgres psql -U wastask -d wastask  # Conectar ao banco")
        
        console.print(f"\n[bold]SQL Direto:[/bold]")
        console.print(f"  SELECT * FROM projects;            # Ver projetos")
        console.print(f"  SELECT * FROM tasks;               # Ver tarefas")
        console.print(f"  SELECT * FROM conversas;           # Ver conversas")
        console.print(f"  SELECT COUNT(*) FROM tasks WHERE status = 'pending';  # Contar pendentes")
        
        console.print(f"\n[bold]Conexão Externa:[/bold]")
        console.print(f"  Host: 127.0.0.1")
        console.print(f"  Porta: 5433 (Docker container)")
        console.print(f"  Database: wastask")
        console.print(f"  User: wastask")
        console.print(f"  Password: password")
    
    async def executar_demo_postgres(self):
        """Demo completo com PostgreSQL"""
        console.print(Panel(
            "[bold blue]🐘 WasTask - Demo PostgreSQL[/bold blue]\n\n"
            "[cyan]Dados salvos em banco de dados real[/cyan]\n"
            "[yellow]✨ PostgreSQL + Docker ✨[/yellow]",
            expand=False
        ))
        
        # 1. Verificar Docker
        if not self.verificar_docker():
            console.print("❌ Docker é necessário para esta demo")
            return
        
        # 2. Iniciar PostgreSQL
        if not self.iniciar_postgres():
            console.print("❌ Falha ao iniciar PostgreSQL")
            return
        
        # 3. Conectar ao banco
        if not self.conectar_banco():
            console.print("❌ Falha ao conectar ao banco")
            return
        
        # 4. Mostrar estado inicial
        console.print(f"\n[bold]📊 Estado inicial do banco...[/bold]")
        stats_inicial = self.mostrar_dados_banco()
        
        # 5. Criar projeto
        projeto = self.criar_projeto_banco(
            "Plataforma de E-learning",
            "Sistema completo de ensino online com IA"
        )
        
        if not projeto:
            return
        
        # 6. Criar tarefas
        tarefas_exemplo = [
            ("🎓 Análise pedagógica e requisitos", TaskPriority.HIGH),
            ("👨‍🏫 Sistema de gestão de professores", TaskPriority.HIGH),
            ("👨‍🎓 Portal do aluno", TaskPriority.HIGH),
            ("📚 Biblioteca de conteúdos", TaskPriority.MEDIUM),
            ("🎥 Sistema de videoaulas", TaskPriority.MEDIUM),
            ("📝 Avaliações e quizzes", TaskPriority.MEDIUM),
            ("🤖 IA para recomendações", TaskPriority.LOW),
            ("📊 Analytics de aprendizado", TaskPriority.LOW),
            ("📱 App mobile", TaskPriority.LOW),
            ("🔒 Segurança e LGPD", TaskPriority.HIGH)
        ]
        
        tarefas_criadas = self.criar_tarefas_banco(projeto.id, tarefas_exemplo)
        
        # 7. Conversa com IA
        console.print(f"\n[bold cyan]🤖 Conversando com IA...[/bold cyan]")
        
        pergunta = "Como estruturar uma plataforma de e-learning moderna?"
        
        with console.status("🧠 IA analisando..."):
            time.sleep(1.5)
            resposta_ia = await self.ia_agent.run(pergunta)
        
        # Salvar conversa no banco
        await self.salvar_conversa_banco(projeto.id, pergunta, resposta_ia.content)
        
        console.print(f"[bold]👤 Pergunta:[/bold] {pergunta}")
        console.print(f"[bold blue]🤖 IA:[/bold blue] {resposta_ia.content[:100]}...")
        
        # 8. Mostrar dados finais
        console.print(f"\n[bold green]🎉 Demo PostgreSQL Concluído![/bold green]")
        
        stats_final = self.mostrar_dados_banco()
        self.mostrar_comandos_banco()
        
        # Comparação
        if stats_inicial and stats_final:
            novos_projetos = stats_final["projetos"] - stats_inicial.get("projetos", 0)
            novas_tarefas = stats_final["tarefas"] - stats_inicial.get("tarefas", 0)
            novas_conversas = stats_final["conversas"] - stats_inicial.get("conversas", 0)
            
            console.print(f"\n[bold yellow]📈 Criado nesta sessão:[/bold yellow]")
            console.print(f"  • {novos_projetos} projeto(s)")
            console.print(f"  • {novas_tarefas} tarefa(s)")
            console.print(f"  • {novas_conversas} conversa(s)")
        
        console.print(f"\n[bold cyan]✨ Todos os dados estão salvos no PostgreSQL![/bold cyan]")
        console.print(f"🔄 Execute novamente para ver persistência funcionando!")


async def main():
    """Função principal"""
    try:
        demo = WasTaskPostgresDemo()
        await demo.executar_demo_postgres()
    except KeyboardInterrupt:
        console.print("\n👋 Demo interrompido")
    except Exception as e:
        console.print(f"\n❌ Erro inesperado: {e}")


if __name__ == '__main__':
    # Adicionar dependência do SQLAlchemy
    try:
        import sqlalchemy
        import psycopg2
    except ImportError:
        console.print("📦 Instalando dependências do PostgreSQL...")
        os.system("uv add sqlalchemy psycopg2-binary")
        console.print("✅ Dependências instaladas!")
    
    asyncio.run(main())