#!/usr/bin/env python3
"""
Insert subtasks for task expansion
"""
import asyncio
import json
from database_manager import connect_and_run

async def insert_subtasks_for_task(task_id: int, subtasks_json_file: str):
    """Insert subtasks from JSON file"""
    
    # Load subtasks from JSON
    with open(subtasks_json_file, 'r') as f:
        subtasks = json.load(f)
    
    async def insert_operation(db):
        # First, get the parent task info
        parent_query = """
        SELECT project_id, expansion_level 
        FROM wastask_tasks 
        WHERE id = $1
        """
        parent = await db.pool.fetchrow(parent_query, task_id)
        
        if not parent:
            print(f"❌ Task {task_id} not found")
            return
        
        project_id = parent['project_id']
        parent_level = parent['expansion_level']
        
        # Insert each subtask
        insert_query = """
        INSERT INTO wastask_tasks (
            project_id, title, description, priority, estimated_hours,
            complexity, category, status, parent_task_id, expansion_level,
            is_expanded
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        RETURNING id
        """
        
        subtask_ids = []
        for subtask in subtasks:
            subtask_id = await db.pool.fetchval(
                insert_query,
                project_id,
                subtask['title'],
                subtask['description'],
                subtask['priority'],
                subtask['estimated_hours'],
                subtask['complexity'],
                subtask['category'],
                'todo',  # status
                task_id,  # parent_task_id
                parent_level + 1,  # expansion_level
                False  # is_expanded
            )
            subtask_ids.append(subtask_id)
            print(f"✅ Created subtask {subtask_id}: {subtask['title']}")
        
        # Mark parent task as expanded
        update_query = "UPDATE wastask_tasks SET is_expanded = true WHERE id = $1"
        await db.pool.execute(update_query, task_id)
        
        print(f"\n🎉 Successfully created {len(subtask_ids)} subtasks for task {task_id}")
        return subtask_ids
    
    return await connect_and_run(insert_operation)

async def main():
    task_id = 17  # Monitoring and logging task
    json_file = "expand_task_17.json"
    
    print(f"📝 Inserting subtasks for task {task_id}...")
    await insert_subtasks_for_task(task_id, json_file)

if __name__ == "__main__":
    asyncio.run(main())