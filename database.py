"""
WasTask Database Setup with SQLAlchemy
Configuração completa do banco de dados
"""
import os
from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4, UUID

from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.sql import func

from core.models import TaskStatus, TaskPriority, ProjectStatus

# Base para os modelos
Base = declarative_base()

class ProjectDB(Base):
    """Modelo de Projeto para o banco"""
    __tablename__ = "projects"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False)
    github_repo = Column(String(200))
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relacionamentos
    tasks = relationship("TaskDB", back_populates="project")

class TaskDB(Base):
    """Modelo de Tarefa para o banco"""
    __tablename__ = "tasks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    project_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    assignee_id = Column(PGUUID(as_uuid=True))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    project = relationship("ProjectDB", back_populates="tasks")

class ConversaDB(Base):
    """Modelo de Conversa com IA para o banco"""
    __tablename__ = "conversas"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    projeto_id = Column(PGUUID(as_uuid=True), ForeignKey("projects.id"))
    usuario_id = Column(PGUUID(as_uuid=True), nullable=False)
    pergunta = Column(Text, nullable=False)
    resposta = Column(Text, nullable=False)
    agent_type = Column(String(50), default="coordinator")
    created_at = Column(DateTime(timezone=True), default=func.now())

class DatabaseManager:
    """Gerenciador do banco de dados"""
    
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv(
            "DATABASE_URL", 
            "postgresql://wastask:password@127.0.0.1:5433/wastask"
        )
        
        # Criar engine
        self.engine = create_engine(self.database_url, echo=True)
        
        # Session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Criar todas as tabelas"""
        Base.metadata.create_all(bind=self.engine)
        print("✅ Tabelas criadas com sucesso!")
        
    def get_session(self) -> Session:
        """Obter sessão do banco"""
        return self.SessionLocal()
        
    def criar_projeto(self, name: str, description: str, owner_id: str) -> ProjectDB:
        """Criar projeto no banco"""
        with self.get_session() as session:
            projeto = ProjectDB(
                name=name,
                description=description,
                owner_id=UUID(owner_id)
            )
            session.add(projeto)
            session.commit()
            session.refresh(projeto)
            return projeto
    
    def criar_tarefa(self, title: str, description: str, project_id: str, 
                     creator_id: str, priority: TaskPriority = TaskPriority.MEDIUM) -> TaskDB:
        """Criar tarefa no banco"""
        with self.get_session() as session:
            tarefa = TaskDB(
                title=title,
                description=description,
                project_id=UUID(project_id),
                creator_id=UUID(creator_id),
                priority=priority
            )
            session.add(tarefa)
            session.commit()
            session.refresh(tarefa)
            return tarefa
    
    def listar_projetos(self, owner_id: str = None) -> List[ProjectDB]:
        """Listar projetos"""
        with self.get_session() as session:
            query = session.query(ProjectDB)
            if owner_id:
                query = query.filter(ProjectDB.owner_id == UUID(owner_id))
            return query.all()
    
    def listar_tarefas(self, project_id: str = None) -> List[TaskDB]:
        """Listar tarefas"""
        with self.get_session() as session:
            query = session.query(TaskDB)
            if project_id:
                query = query.filter(TaskDB.project_id == UUID(project_id))
            return query.all()
    
    def salvar_conversa(self, projeto_id: str, usuario_id: str, 
                       pergunta: str, resposta: str, agent_type: str = "coordinator") -> ConversaDB:
        """Salvar conversa com IA"""
        with self.get_session() as session:
            conversa = ConversaDB(
                projeto_id=UUID(projeto_id) if projeto_id else None,
                usuario_id=UUID(usuario_id),
                pergunta=pergunta,
                resposta=resposta,
                agent_type=agent_type
            )
            session.add(conversa)
            session.commit()
            session.refresh(conversa)
            return conversa
    
    def get_stats(self) -> dict:
        """Obter estatísticas do banco"""
        with self.get_session() as session:
            total_projetos = session.query(ProjectDB).count()
            total_tarefas = session.query(TaskDB).count()
            total_conversas = session.query(ConversaDB).count()
            
            # Tarefas por status
            tarefas_pending = session.query(TaskDB).filter(TaskDB.status == TaskStatus.PENDING).count()
            tarefas_progress = session.query(TaskDB).filter(TaskDB.status == TaskStatus.IN_PROGRESS).count()
            tarefas_completed = session.query(TaskDB).filter(TaskDB.status == TaskStatus.COMPLETED).count()
            
            return {
                "projetos": total_projetos,
                "tarefas": total_tarefas,
                "conversas": total_conversas,
                "tarefas_pendentes": tarefas_pending,
                "tarefas_em_progresso": tarefas_progress,
                "tarefas_concluidas": tarefas_completed
            }


# Instância global
db = DatabaseManager()