#!/usr/bin/env python3
"""
Test Task Expansion with Direct Database Query
"""
import asyncio
import json
from database_manager import connect_and_run

async def get_expandable_tasks():
    """Get tasks that can be expanded"""
    
    async def query_tasks(db):
        query = """
        SELECT id, title, description, estimated_hours, complexity, category, priority, 
               project_id, is_expanded, expansion_level
        FROM wastask_tasks 
        WHERE project_id = 1 
          AND is_expanded = false 
          AND expansion_level = 0
          AND (estimated_hours > 8 OR complexity = 'high')
        ORDER BY estimated_hours DESC
        LIMIT 5
        """
        
        tasks = await db.pool.fetch(query)
        return [dict(task) for task in tasks]
    
    return await connect_and_run(query_tasks)

async def main():
    print("🔍 Buscando tarefas que podem ser expandidas...")
    tasks = await get_expandable_tasks()
    
    if not tasks:
        print("❌ Nenhuma tarefa expandível encontrada")
        return
    
    print(f"\n📋 Encontradas {len(tasks)} tarefas expandíveis:\n")
    
    for task in tasks:
        print(f"ID: {task['id']}")
        print(f"   Título: {task['title']}")
        print(f"   Horas: {task['estimated_hours']}h")
        print(f"   Complexidade: {task['complexity']}")
        print(f"   Categoria: {task['category']}")
        print(f"   Expandida: {'Sim' if task['is_expanded'] else 'Não'}")
        print("-" * 60)
    
    # Escolher a primeira tarefa para expandir
    if tasks:
        task_to_expand = tasks[0]
        print(f"\n🎯 Tarefa selecionada para expansão: {task_to_expand['title']}")
        print(f"\nCONTEXTO PARA EXPANSÃO:")
        print(json.dumps(task_to_expand, indent=2))

if __name__ == "__main__":
    asyncio.run(main())