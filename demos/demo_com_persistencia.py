#!/usr/bin/env python3
"""
WasTask - Demo com Persistência
Demonstração que salva dados em arquivos JSON
"""
import sys
import os
import asyncio
import uuid
import json
from datetime import datetime
from pathlib import Path

# Adicionar path atual
sys.path.insert(0, os.path.abspath('.'))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import time

console = Console()

# Importar módulos funcionais
from core.models import Project, Task, TaskPriority, TaskStatus
from wastask.mock_adk import LlmAgent

class WasTaskComPersistencia:
    def __init__(self):
        self.usuario_id = str(uuid.uuid4())
        self.data_dir = Path("wastask_data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Arquivos de dados
        self.projetos_file = self.data_dir / "projetos.json"
        self.tarefas_file = self.data_dir / "tarefas.json"
        self.sessoes_file = self.data_dir / "sessoes.json"
        
        # Carregar dados existentes
        self.projetos = self.carregar_dados(self.projetos_file)
        self.tarefas = self.carregar_dados(self.tarefas_file)
        self.sessoes = self.carregar_dados(self.sessoes_file)
        
        # IA Agent
        self.ia_agent = LlmAgent(
            name="assistente_persistencia",
            model="wastask-persistent",
            description="Assistente com persistência de dados"
        )
    
    def carregar_dados(self, arquivo):
        """Carregar dados de arquivo JSON"""
        if arquivo.exists():
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                console.print(f"📁 Carregados {len(dados)} itens de {arquivo.name}")
                return dados
            except Exception as e:
                console.print(f"⚠️ Erro ao carregar {arquivo.name}: {e}")
                return []
        return []
    
    def salvar_dados(self, dados, arquivo):
        """Salvar dados em arquivo JSON"""
        try:
            with open(arquivo, 'w', encoding='utf-8') as f:
                json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
            console.print(f"💾 Salvos {len(dados)} itens em {arquivo.name}")
            return True
        except Exception as e:
            console.print(f"❌ Erro ao salvar {arquivo.name}: {e}")
            return False
    
    def projeto_para_dict(self, projeto):
        """Converter projeto para dicionário serializável"""
        return {
            "id": str(projeto.id),
            "name": projeto.name,
            "description": projeto.description,
            "status": projeto.status.value,
            "owner_id": projeto.owner_id,
            "github_repo": projeto.github_repo,
            "created_at": projeto.created_at.isoformat(),
            "updated_at": projeto.updated_at.isoformat()
        }
    
    def tarefa_para_dict(self, tarefa):
        """Converter tarefa para dicionário serializável"""
        return {
            "id": str(tarefa.id),
            "title": tarefa.title,
            "description": tarefa.description,
            "status": tarefa.status.value,
            "priority": tarefa.priority.value,
            "project_id": str(tarefa.project_id),
            "creator_id": tarefa.creator_id,
            "assignee_id": tarefa.assignee_id,
            "estimated_hours": tarefa.estimated_hours,
            "actual_hours": tarefa.actual_hours,
            "created_at": tarefa.created_at.isoformat(),
            "updated_at": tarefa.updated_at.isoformat(),
            "completed_at": tarefa.completed_at.isoformat() if tarefa.completed_at else None
        }
    
    def criar_projeto_persistente(self, nome, descricao):
        """Criar projeto e salvar no disco"""
        console.print(f"\n[bold cyan]💾 Criando projeto persistente: '{nome}'[/bold cyan]")
        
        # Criar projeto
        projeto = Project(
            name=nome,
            description=descricao,
            owner_id=self.usuario_id
        )
        
        # Converter para dicionário
        projeto_dict = self.projeto_para_dict(projeto)
        
        # Adicionar à lista
        self.projetos.append(projeto_dict)
        
        # Salvar no arquivo
        if self.salvar_dados(self.projetos, self.projetos_file):
            console.print(f"✅ Projeto '{nome}' salvo permanentemente!")
            console.print(f"📂 Local: {self.projetos_file.absolute()}")
            console.print(f"🆔 ID: {projeto_dict['id']}")
        
        return projeto, projeto_dict
    
    def criar_tarefas_persistentes(self, projeto_id, lista_tarefas):
        """Criar múltiplas tarefas e salvar"""
        console.print(f"\n[bold cyan]💾 Criando tarefas persistentes...[/bold cyan]")
        
        tarefas_criadas = []
        
        for titulo, prioridade in lista_tarefas:
            # Criar tarefa
            tarefa = Task(
                title=titulo,
                description=f"Tarefa persistente para projeto {projeto_id}",
                project_id=projeto_id,
                creator_id=self.usuario_id,
                priority=prioridade
            )
            
            # Converter para dict
            tarefa_dict = self.tarefa_para_dict(tarefa)
            
            # Adicionar à lista
            self.tarefas.append(tarefa_dict)
            tarefas_criadas.append(tarefa_dict)
        
        # Salvar todas as tarefas
        if self.salvar_dados(self.tarefas, self.tarefas_file):
            console.print(f"✅ {len(lista_tarefas)} tarefas salvas permanentemente!")
            console.print(f"📂 Local: {self.tarefas_file.absolute()}")
        
        return tarefas_criadas
    
    async def salvar_conversa_ia(self, projeto_id, pergunta, resposta):
        """Salvar conversa com IA"""
        conversa = {
            "id": str(uuid.uuid4()),
            "projeto_id": projeto_id,
            "usuario_id": self.usuario_id,
            "pergunta": pergunta,
            "resposta": resposta,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sessoes.append(conversa)
        
        if self.salvar_dados(self.sessoes, self.sessoes_file):
            console.print("💬 Conversa salva no histórico!")
        
        return conversa
    
    def listar_dados_salvos(self):
        """Listar todos os dados salvos"""
        console.print(f"\n[bold cyan]📊 Dados Salvos no Sistema[/bold cyan]")
        
        # Verificar arquivos
        arquivos_info = []
        
        for arquivo, dados, nome in [
            (self.projetos_file, self.projetos, "Projetos"),
            (self.tarefas_file, self.tarefas, "Tarefas"),
            (self.sessoes_file, self.sessoes, "Conversas IA")
        ]:
            if arquivo.exists():
                tamanho = arquivo.stat().st_size
                arquivos_info.append((nome, len(dados), f"{tamanho} bytes", str(arquivo)))
            else:
                arquivos_info.append((nome, 0, "0 bytes", "Não existe"))
        
        # Tabela de arquivos
        table = Table(title="💾 Arquivos de Dados")
        table.add_column("Tipo", style="cyan")
        table.add_column("Registros", style="green")
        table.add_column("Tamanho", style="yellow")
        table.add_column("Local", style="dim")
        
        for nome, count, tamanho, local in arquivos_info:
            table.add_row(nome, str(count), tamanho, local)
        
        console.print(table)
        
        # Mostrar conteúdo se houver
        if self.projetos:
            console.print(f"\n[bold green]📋 Projetos Salvos:[/bold green]")
            for projeto in self.projetos[-3:]:  # Últimos 3
                console.print(f"  • {projeto['name']} (ID: {projeto['id'][:8]}...)")
        
        if self.tarefas:
            console.print(f"\n[bold green]⚡ Tarefas Salvas:[/bold green]")
            for tarefa in self.tarefas[-5:]:  # Últimas 5
                console.print(f"  • {tarefa['title']} (Prioridade: {tarefa['priority']})")
        
        return len(self.projetos), len(self.tarefas), len(self.sessoes)
    
    def mostrar_localizacao_dados(self):
        """Mostrar onde os dados estão salvos"""
        console.print(f"\n[bold cyan]📂 Localização dos Dados[/bold cyan]")
        
        console.print(f"[bold]Diretório principal:[/bold] {self.data_dir.absolute()}")
        console.print(f"[bold]Projetos:[/bold] {self.projetos_file}")
        console.print(f"[bold]Tarefas:[/bold] {self.tarefas_file}")
        console.print(f"[bold]Conversas:[/bold] {self.sessoes_file}")
        
        # Comandos para visualizar
        console.print(f"\n[bold yellow]💻 Comandos para visualizar:[/bold yellow]")
        console.print(f"  cat {self.projetos_file}")
        console.print(f"  cat {self.tarefas_file}")
        console.print(f"  cat {self.sessoes_file}")
        console.print(f"  ls -la {self.data_dir}/")
    
    async def executar_demo_persistencia(self):
        """Demo completo com persistência"""
        console.print(Panel(
            "[bold blue]💾 WasTask - Demo com Persistência[/bold blue]\n\n"
            "[cyan]Os dados serão salvos em arquivos JSON[/cyan]\n"
            "[yellow]✨ Tudo fica gravado no disco! ✨[/yellow]",
            expand=False
        ))
        
        # 1. Mostrar dados existentes
        console.print(f"\n[bold]🔍 Verificando dados existentes...[/bold]")
        proj_count, task_count, conv_count = self.listar_dados_salvos()
        
        # 2. Criar novo projeto
        projeto, projeto_dict = self.criar_projeto_persistente(
            "Sistema de Gestão Hospitalar",
            "Plataforma completa para gestão de hospitais e clínicas"
        )
        
        # 3. Criar tarefas
        tarefas_exemplo = [
            ("📋 Análise de requisitos médicos", TaskPriority.HIGH),
            ("🏥 Modelagem do sistema hospitalar", TaskPriority.HIGH),
            ("👨‍⚕️ Módulo de gestão de médicos", TaskPriority.HIGH),
            ("🏨 Módulo de gestão de leitos", TaskPriority.MEDIUM),
            ("💊 Sistema de farmácia integrado", TaskPriority.MEDIUM),
            ("📊 Dashboard administrativo", TaskPriority.MEDIUM),
            ("🔒 Sistema de segurança LGPD", TaskPriority.HIGH),
            ("📱 App mobile para pacientes", TaskPriority.LOW),
            ("🧪 Testes e validação", TaskPriority.MEDIUM),
            ("📚 Documentação técnica", TaskPriority.LOW)
        ]
        
        tarefas_salvas = self.criar_tarefas_persistentes(projeto.id, tarefas_exemplo)
        
        # 4. Conversa com IA
        console.print(f"\n[bold cyan]🤖 Conversando com IA sobre o projeto...[/bold cyan]")
        
        pergunta = "Como organizar o desenvolvimento de um sistema hospitalar?"
        
        with console.status("🧠 IA analisando..."):
            time.sleep(1.5)
            resposta_ia = await self.ia_agent.run(pergunta)
        
        # Salvar conversa
        await self.salvar_conversa_ia(str(projeto.id), pergunta, resposta_ia.content)
        
        console.print(f"[bold]👤 Pergunta:[/bold] {pergunta}")
        console.print(f"[bold blue]🤖 IA:[/bold blue] {resposta_ia.content[:100]}...")
        
        # 5. Mostrar resumo final
        console.print(f"\n[bold green]🎉 Demo de Persistência Concluído![/bold green]")
        
        # Dados finais
        self.listar_dados_salvos()
        self.mostrar_localizacao_dados()
        
        console.print(f"\n[bold yellow]✨ Agora seus dados estão salvos permanentemente![/bold yellow]")
        console.print(f"📊 Total criado nesta sessão:")
        console.print(f"  • 1 projeto novo")
        console.print(f"  • {len(tarefas_exemplo)} tarefas")
        console.print(f"  • 1 conversa com IA")
        
        console.print(f"\n[bold cyan]🔄 Execute novamente para ver dados persistindo![/bold cyan]")


async def main():
    """Função principal"""
    demo = WasTaskComPersistencia()
    await demo.executar_demo_persistencia()


if __name__ == '__main__':
    asyncio.run(main())