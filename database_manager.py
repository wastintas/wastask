#!/usr/bin/env python3
"""
WasTask Database Manager
Gerencia a persistência de dados das análises de PRD e tarefas geradas
"""
import asyncio
import asyncpg
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class WasTaskDatabase:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or self._get_default_connection()
        self.pool = None
    
    def _get_default_connection(self) -> str:
        """Configuração padrão de conexão com PostgreSQL"""
        return "postgresql://wastask:WastasksDB2024!@postgres:5432/wastask"
    
    async def initialize(self):
        """Inicializar pool de conexões"""
        self.pool = await asyncpg.create_pool(self.connection_string)
        print("✅ Database connection pool created")
    
    async def create_schema(self):
        """Criar schema do banco de dados usando migrations"""
        from migrations.migration_manager import MigrationManager
        
        migration_manager = MigrationManager(self.connection_string)
        try:
            await migration_manager.initialize()
            await migration_manager.migrate()
        finally:
            await migration_manager.close()
        
        print("✅ Database schema created successfully")
    
    async def save_project_analysis(self, results: Dict[str, Any]) -> int:
        """Salvar análise completa de projeto no banco"""
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Salvar projeto principal
                project_id = await self._save_project(conn, results)
                
                # 2. Salvar tecnologias
                await self._save_technologies(conn, project_id, results.get('technologies', []))
                
                # 3. Salvar features
                await self._save_features(conn, project_id, results.get('features', []))
                
                # 4. Salvar tarefas
                await self._save_tasks(conn, project_id, results.get('tasks', []))
                
                # 5. Salvar comandos de setup
                await self._save_setup_commands(conn, project_id, results.get('setup_commands', {}))
                
                # 6. Salvar riscos
                await self._save_risks(conn, project_id, results.get('complexity', {}).get('risks', []))
                
                # 7. Salvar questões de clarificação
                if 'prd_enhancement' in results:
                    questions = results['prd_enhancement'].get('clarification_questions', [])
                    await self._save_clarification_questions(conn, project_id, questions)
        
        print(f"✅ Project analysis saved with ID: {project_id}")
        return project_id
    
    async def _save_project(self, conn, results: Dict[str, Any]) -> int:
        """Salvar dados principais do projeto"""
        project = results['project']
        complexity = results.get('complexity', {})
        prd_enhancement = results.get('prd_enhancement', {})
        stats = results.get('statistics', {})
        
        query = """
        INSERT INTO wastask_projects (
            name, description, original_prd, enhanced_prd,
            prd_quality_before, prd_quality_after,
            complexity_score, timeline, total_hours, package_manager, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
        """
        
        project_id = await conn.fetchval(
            query,
            project['name'],
            project['description'],
            prd_enhancement.get('original_prd', ''),
            prd_enhancement.get('enhanced_prd', ''),
            prd_enhancement.get('original_quality', 0),
            prd_enhancement.get('enhanced_quality', 0),
            complexity.get('score', 0),
            complexity.get('timeline', ''),
            stats.get('total_hours', 0),
            results.get('package_manager', 'pnpm'),
            'analyzed'
        )
        
        return project_id
    
    async def _save_technologies(self, conn, project_id: int, technologies: List[Dict]):
        """Salvar tecnologias recomendadas"""
        if not technologies:
            return
        
        query = """
        INSERT INTO wastask_project_technologies (
            project_id, category, technology, version, reason, confidence
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        for tech in technologies:
            await conn.execute(
                query,
                project_id,
                tech.get('category', ''),
                tech.get('technology', ''),
                tech.get('version', ''),
                tech.get('reason', ''),
                tech.get('confidence', 0.0)
            )
    
    async def _save_features(self, conn, project_id: int, features: List[Dict]):
        """Salvar features identificadas"""
        if not features:
            return
        
        query = """
        INSERT INTO wastask_project_features (
            project_id, name, description, priority, complexity, estimated_effort
        ) VALUES ($1, $2, $3, $4, $5, $6)
        """
        
        for feature in features:
            await conn.execute(
                query,
                project_id,
                feature.get('name', ''),
                feature.get('description', ''),
                feature.get('priority', 'MEDIUM'),
                feature.get('complexity', 'MEDIUM'),
                feature.get('estimated_effort', 8)
            )
    
    async def _save_tasks(self, conn, project_id: int, tasks: List[Dict]):
        """Salvar tarefas geradas"""
        if not tasks:
            return
        
        # Salvar tarefas
        task_query = """
        INSERT INTO wastask_tasks (
            project_id, title, description, priority, estimated_hours, 
            complexity, category, status
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING id
        """
        
        task_ids = {}
        
        for task in tasks:
            task_id = await conn.fetchval(
                task_query,
                project_id,
                task.get('title', ''),
                task.get('description', ''),
                task.get('priority', 'medium'),
                task.get('estimated_hours', 8),
                task.get('complexity', 'medium'),
                task.get('category', ''),
                'todo'
            )
            
            # Mapear ID original para ID do banco
            original_id = task.get('id')
            if original_id:
                task_ids[original_id] = task_id
            
            # Salvar tags
            tags = task.get('tags', [])
            if tags:
                tag_query = "INSERT INTO wastask_task_tags (task_id, tag) VALUES ($1, $2)"
                for tag in tags:
                    await conn.execute(tag_query, task_id, tag)
        
        # Salvar dependências (se existirem)
        for task in tasks:
            dependencies = task.get('dependencies', [])
            if dependencies and task.get('id') in task_ids:
                task_id = task_ids[task['id']]
                dep_query = "INSERT INTO wastask_task_dependencies (task_id, depends_on_task_id) VALUES ($1, $2)"
                
                for dep_id in dependencies:
                    if dep_id in task_ids:
                        await conn.execute(dep_query, task_id, task_ids[dep_id])
    
    async def _save_setup_commands(self, conn, project_id: int, setup_commands: Dict):
        """Salvar comandos de setup"""
        if not setup_commands:
            return
        
        query = """
        INSERT INTO wastask_setup_commands (project_id, command_type, command_text, execution_order)
        VALUES ($1, $2, $3, $4)
        """
        
        order = 0
        for cmd_type, commands in setup_commands.items():
            if isinstance(commands, list):
                for cmd in commands:
                    await conn.execute(query, project_id, cmd_type, cmd, order)
                    order += 1
            elif isinstance(commands, dict):
                for key, value in commands.items():
                    cmd_text = f"{key}: {value}"
                    await conn.execute(query, project_id, cmd_type, cmd_text, order)
                    order += 1
    
    async def _save_risks(self, conn, project_id: int, risks: List[str]):
        """Salvar riscos identificados"""
        if not risks:
            return
        
        query = "INSERT INTO wastask_project_risks (project_id, risk_description) VALUES ($1, $2)"
        
        for risk in risks:
            await conn.execute(query, project_id, risk)
    
    async def _save_clarification_questions(self, conn, project_id: int, questions: List[str]):
        """Salvar questões de clarificação"""
        if not questions:
            return
        
        query = "INSERT INTO wastask_clarification_questions (project_id, question) VALUES ($1, $2)"
        
        for question in questions:
            await conn.execute(query, project_id, question)
    
    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Recuperar projeto completo por ID"""
        async with self.pool.acquire() as conn:
            # Dados principais do projeto
            project_query = "SELECT * FROM wastask_projects WHERE id = $1"
            project = await conn.fetchrow(project_query, project_id)
            
            if not project:
                return None
            
            # Tecnologias
            tech_query = "SELECT * FROM wastask_project_technologies WHERE project_id = $1 ORDER BY confidence DESC"
            technologies = await conn.fetch(tech_query, project_id)
            
            # Features
            features_query = "SELECT * FROM wastask_project_features WHERE project_id = $1"
            features = await conn.fetch(features_query, project_id)
            
            # Tarefas
            tasks_query = "SELECT * FROM wastask_tasks WHERE project_id = $1 ORDER BY priority DESC, created_at"
            tasks = await conn.fetch(tasks_query, project_id)
            
            # Comandos de setup
            setup_query = "SELECT * FROM wastask_setup_commands WHERE project_id = $1 ORDER BY execution_order"
            setup_commands = await conn.fetch(setup_query, project_id)
            
            # Riscos
            risks_query = "SELECT risk_description FROM wastask_project_risks WHERE project_id = $1"
            risks = await conn.fetch(risks_query, project_id)
            
            # Questões
            questions_query = "SELECT * FROM wastask_clarification_questions WHERE project_id = $1"
            questions = await conn.fetch(questions_query, project_id)
            
            return {
                'project': dict(project),
                'technologies': [dict(t) for t in technologies],
                'features': [dict(f) for f in features],
                'tasks': [dict(t) for t in tasks],
                'setup_commands': [dict(s) for s in setup_commands],
                'risks': [r['risk_description'] for r in risks],
                'questions': [dict(q) for q in questions]
            }
    
    async def list_projects(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Listar projetos"""
        query = """
        SELECT id, name, description, complexity_score, timeline, 
               status, created_at, updated_at
        FROM wastask_projects 
        ORDER BY created_at DESC 
        LIMIT $1
        """
        
        async with self.pool.acquire() as conn:
            projects = await conn.fetch(query, limit)
            return [dict(p) for p in projects]
    
    async def update_task_status(self, task_id: int, status: str, assigned_to: str = None):
        """Atualizar status de tarefa"""
        query = """
        UPDATE wastask_tasks 
        SET status = $1, assigned_to = $2,
            started_at = CASE WHEN $1 = 'in_progress' AND started_at IS NULL THEN CURRENT_TIMESTAMP ELSE started_at END,
            completed_at = CASE WHEN $1 = 'completed' THEN CURRENT_TIMESTAMP ELSE NULL END
        WHERE id = $3
        """
        
        async with self.pool.acquire() as conn:
            await conn.execute(query, status, assigned_to, task_id)
    
    async def get_project_stats(self) -> Dict[str, Any]:
        """Estatísticas gerais"""
        queries = {
            'total_projects': "SELECT COUNT(*) FROM wastask_projects",
            'total_tasks': "SELECT COUNT(*) FROM wastask_tasks",
            'completed_tasks': "SELECT COUNT(*) FROM wastask_tasks WHERE status = 'completed'",
            'active_projects': "SELECT COUNT(*) FROM wastask_projects WHERE status != 'completed'",
            'avg_complexity': "SELECT AVG(complexity_score) FROM wastask_projects WHERE complexity_score > 0"
        }
        
        stats = {}
        async with self.pool.acquire() as conn:
            for key, query in queries.items():
                result = await conn.fetchval(query)
                stats[key] = result or 0
        
        return stats
    
    async def close(self):
        """Fechar pool de conexões"""
        if self.pool:
            await self.pool.close()
            print("✅ Database connections closed")


# Função utilitária para conectar e executar operações
async def connect_and_run(operation, *args, **kwargs):
    """Conectar ao banco e executar operação"""
    db = WasTaskDatabase()
    try:
        await db.initialize()
        result = await operation(db, *args, **kwargs)
        return result
    finally:
        await db.close()


# Singleton instance
_db_pool = None

async def init_database_pool(connection_string: str = None):
    """Initialize the database pool singleton"""
    global _db_pool
    if _db_pool is None:
        connection_string = connection_string or "postgresql://wastask:WastasksDB2024!@postgres:5432/wastask"
        _db_pool = await asyncpg.create_pool(connection_string)
        print("✅ Database connection pool created")
    return _db_pool

async def get_db_pool():
    """Get the database pool instance"""
    global _db_pool
    if _db_pool is None:
        await init_database_pool()
    return _db_pool

async def close_database_pool():
    """Close the database pool"""
    global _db_pool
    if _db_pool:
        await _db_pool.close()
        _db_pool = None
        print("✅ Database connection pool closed")

# Exemplo de uso
async def example_usage():
    """Exemplo de como usar o database manager"""
    
    # Dados de exemplo (simulando resultado do wastask_simple.py)
    sample_results = {
        'project': {
            'name': 'Sistema de Vendas',
            'description': 'Sistema para gerenciar vendas da empresa'
        },
        'technologies': [
            {
                'category': 'frontend_framework',
                'technology': 'React',
                'version': '18.3.0',
                'reason': 'Modern component-based architecture',
                'confidence': 0.85
            }
        ],
        'features': [
            {
                'name': 'Cadastro de clientes',
                'description': 'Sistema de cadastro de clientes',
                'priority': 'HIGH',
                'complexity': 'MEDIUM',
                'estimated_effort': 8
            }
        ],
        'tasks': [
            {
                'id': 1,
                'title': 'Setup inicial do projeto',
                'description': 'Configurar estrutura inicial',
                'priority': 'high',
                'estimated_hours': 4,
                'complexity': 'low',
                'category': 'setup',
                'tags': ['setup', 'initial']
            }
        ],
        'complexity': {
            'score': 6.5,
            'timeline': '4-6 weeks',
            'risks': ['Integration complexity']
        },
        'statistics': {
            'total_hours': 120
        },
        'package_manager': 'pnpm',
        'prd_enhancement': {
            'original_prd': 'PRD original...',
            'enhanced_prd': 'PRD melhorado...',
            'original_quality': 3.0,
            'enhanced_quality': 7.5,
            'clarification_questions': ['Quantos usuários?', 'Mobile necessário?']
        }
    }
    
    async def save_example(db):
        project_id = await db.save_project_analysis(sample_results)
        print(f"Project saved with ID: {project_id}")
        
        # Listar projetos
        projects = await db.list_projects()
        print(f"Total projects: {len(projects)}")
        
        # Estatísticas
        stats = await db.get_project_stats()
        print(f"Database stats: {stats}")
        
        return project_id
    
    project_id = await connect_and_run(save_example)
    print(f"Example completed. Project ID: {project_id}")


if __name__ == '__main__':
    asyncio.run(example_usage())