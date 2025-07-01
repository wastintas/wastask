"""
Task management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
import json

from database_manager import get_db_pool
from core.models import Task, CreateTaskRequest, UpdateTaskRequest

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip")
):
    """List tasks with optional filtering."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            t.id, t.title, t.description, t.status, t.priority,
            t.project_id, t.estimated_duration, t.dependencies,
            t.created_at, t.updated_at,
            p.name as project_name
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE ($1::int IS NULL OR t.project_id = $1)
          AND ($2::text IS NULL OR t.status = $2)
          AND ($3::text IS NULL OR t.priority = $3)
        ORDER BY 
            CASE t.priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            t.created_at DESC
        LIMIT $4 OFFSET $5
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, project_id, status, priority, limit, offset)
        
        tasks = []
        for row in rows:
            task = dict(row)
            # Parse JSON fields
            if task['dependencies']:
                task['dependencies'] = json.loads(task['dependencies'])
            tasks.append(task)
        
        return tasks


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(task: CreateTaskRequest, project_id: int):
    """Create a new task for a project."""
    pool = await get_db_pool()
    
    # Verify project exists
    async with pool.acquire() as conn:
        project_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1)",
            project_id
        )
        
        if not project_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Create task
        query = """
            INSERT INTO tasks (
                title, description, status, priority, 
                project_id, estimated_duration
            )
            VALUES ($1, $2, 'pending', $3, $4, $5)
            RETURNING id, title, description, status, priority, 
                      project_id, estimated_duration, created_at
        """
        
        try:
            row = await conn.fetchrow(
                query,
                task.title,
                task.description,
                task.priority or 'medium',
                project_id,
                task.estimated_hours
            )
            return dict(row)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create task: {str(e)}"
            )


@router.get("/{task_id}", response_model=dict)
async def get_task(task_id: int):
    """Get a specific task by ID."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            t.id, t.title, t.description, t.status, t.priority,
            t.project_id, t.estimated_duration, t.dependencies,
            t.created_at, t.updated_at,
            p.name as project_name,
            p.status as project_status
        FROM tasks t
        JOIN projects p ON t.project_id = p.id
        WHERE t.id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, task_id)
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        task = dict(row)
        # Parse JSON fields
        if task['dependencies']:
            task['dependencies'] = json.loads(task['dependencies'])
        
        return task


@router.put("/{task_id}", response_model=dict)
async def update_task(task_id: int, updates: UpdateTaskRequest):
    """Update a task."""
    pool = await get_db_pool()
    
    # Build dynamic update query
    update_fields = []
    params = [task_id]
    param_count = 2
    
    if updates.title is not None:
        update_fields.append(f"title = ${param_count}")
        params.append(updates.title)
        param_count += 1
    
    if updates.description is not None:
        update_fields.append(f"description = ${param_count}")
        params.append(updates.description)
        param_count += 1
    
    if updates.status is not None:
        update_fields.append(f"status = ${param_count}")
        params.append(updates.status)
        param_count += 1
    
    if updates.priority is not None:
        update_fields.append(f"priority = ${param_count}")
        params.append(updates.priority)
        param_count += 1
    
    if updates.estimated_hours is not None:
        update_fields.append(f"estimated_duration = ${param_count}")
        params.append(updates.estimated_hours)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    query = f"""
        UPDATE tasks
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING id, title, description, status, priority, updated_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return dict(row)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int):
    """Delete a task."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM tasks WHERE id = $1",
            task_id
        )
        
        if result.split()[-1] == '0':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )


@router.post("/{task_id}/complete", response_model=dict)
async def complete_task(task_id: int):
    """Mark a task as completed."""
    pool = await get_db_pool()
    
    query = """
        UPDATE tasks
        SET status = 'completed', updated_at = CURRENT_TIMESTAMP
        WHERE id = $1 AND status != 'completed'
        RETURNING id, title, status, updated_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, task_id)
        
        if not row:
            # Check if task exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM tasks WHERE id = $1)",
                task_id
            )
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Task {task_id} not found"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Task {task_id} is already completed"
                )
        
        return dict(row)


@router.get("/project/{project_id}", response_model=List[dict])
async def get_project_tasks(
    project_id: int,
    status: Optional[str] = Query(None, description="Filter by status")
):
    """Get all tasks for a specific project."""
    pool = await get_db_pool()
    
    # Verify project exists
    async with pool.acquire() as conn:
        project_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1)",
            project_id
        )
        
        if not project_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Get tasks
        query = """
            SELECT 
                id, title, description, status, priority,
                estimated_duration, dependencies, created_at, updated_at
            FROM tasks
            WHERE project_id = $1
              AND ($2::text IS NULL OR status = $2)
            ORDER BY 
                CASE priority 
                    WHEN 'high' THEN 1 
                    WHEN 'medium' THEN 2 
                    WHEN 'low' THEN 3 
                END,
                created_at DESC
        """
        
        rows = await conn.fetch(query, project_id, status)
        
        tasks = []
        for row in rows:
            task = dict(row)
            if task['dependencies']:
                task['dependencies'] = json.loads(task['dependencies'])
            tasks.append(task)
        
        return tasks