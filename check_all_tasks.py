#!/usr/bin/env python3
"""
Check all tasks in the database
"""
import asyncio
from database_manager import connect_and_run

async def check_all_tasks():
    """Check all tasks"""
    
    async def query_tasks(db):
        # Verificar quantas tarefas existem
        count_query = "SELECT COUNT(*) as total FROM wastask_tasks WHERE project_id = 1"
        count = await db.pool.fetchval(count_query)
        print(f"📊 Total de tarefas no projeto 1: {count}")
        
        # Buscar tarefas com alta complexidade ou muitas horas
        query = """
        SELECT id, title, estimated_hours, complexity, is_expanded, expansion_level 
        FROM wastask_tasks 
        WHERE project_id = 1
        ORDER BY estimated_hours DESC
        LIMIT 10
        """
        
        tasks = await db.pool.fetch(query)
        return [dict(task) for task in tasks]
    
    return await connect_and_run(query_tasks)

async def main():
    print("🔍 Verificando todas as tarefas...")
    tasks = await check_all_tasks()
    
    print(f"\n📋 Top 10 tarefas por horas estimadas:\n")
    
    for task in tasks:
        exp_status = "✅ Expandida" if task['is_expanded'] else "❌ Não expandida"
        print(f"ID: {task['id']} | {task['estimated_hours']}h | {task['complexity']} | {exp_status} | Nível: {task['expansion_level']}")
        print(f"   {task['title']}")
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(main())