"""
Complete task management endpoints with authentication
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from database_manager import get_db_pool
from api.auth import get_current_user

router = APIRouter()


# Pydantic models
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"  # low, medium, high
    estimated_hours: Optional[int] = None
    project_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # todo, in_progress, completed, blocked
    priority: Optional[str] = None
    estimated_hours: Optional[int] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: str
    priority: str
    project_id: int
    estimated_hours: Optional[int]
    created_at: str
    updated_at: Optional[str]


@router.get("/", response_model=List[dict])
async def list_tasks(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[str] = Query(None, description="Filter by task status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tasks"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    current_user: dict = Depends(get_current_user)
):
    """List tasks with optional filtering."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            t.id, t.title, t.description, t.status, t.priority,
            t.project_id, t.estimated_hours, t.created_at, t.updated_at,
            p.name as project_name
        FROM wastask_tasks t
        JOIN wastask_projects p ON t.project_id = p.id
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
        return [dict(row) for row in rows]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new task."""
    pool = await get_db_pool()
    
    # Verify project exists
    async with pool.acquire() as conn:
        project_exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM wastask_projects WHERE id = $1)",
            task.project_id
        )
        
        if not project_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {task.project_id} not found"
            )
        
        # Create task
        query = """
            INSERT INTO wastask_tasks (
                title, description, status, priority, 
                project_id, estimated_hours
            )
            VALUES ($1, $2, 'todo', $3, $4, $5)
            RETURNING id, title, description, status, priority, 
                      project_id, estimated_hours, created_at
        """
        
        try:
            row = await conn.fetchrow(
                query,
                task.title,
                task.description,
                task.priority,
                task.project_id,
                task.estimated_hours
            )
            return dict(row)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create task: {str(e)}"
            )


@router.get("/{task_id}", response_model=dict)
async def get_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific task by ID."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            t.id, t.title, t.description, t.status, t.priority,
            t.project_id, t.estimated_hours, t.created_at, t.updated_at,
            p.name as project_name,
            p.status as project_status
        FROM wastask_tasks t
        JOIN wastask_projects p ON t.project_id = p.id
        WHERE t.id = $1
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, task_id)
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )
        
        return dict(row)


@router.put("/{task_id}", response_model=dict)
async def update_task(
    task_id: int,
    updates: TaskUpdate,
    current_user: dict = Depends(get_current_user)
):
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
        update_fields.append(f"estimated_hours = ${param_count}")
        params.append(updates.estimated_hours)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    query = f"""
        UPDATE wastask_tasks
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
async def delete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Delete a task."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        result = await conn.execute(
            "DELETE FROM wastask_tasks WHERE id = $1",
            task_id
        )
        
        if result.split()[-1] == '0':
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found"
            )


@router.post("/{task_id}/complete", response_model=dict)
async def complete_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark a task as completed."""
    pool = await get_db_pool()
    
    query = """
        UPDATE wastask_tasks
        SET status = 'completed', updated_at = CURRENT_TIMESTAMP
        WHERE id = $1 AND status != 'completed'
        RETURNING id, title, status, updated_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, task_id)
        
        if not row:
            # Check if task exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM wastask_tasks WHERE id = $1)",
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


@router.post("/{task_id}/start", response_model=dict)
async def start_task(
    task_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Mark a task as in progress."""
    pool = await get_db_pool()
    
    query = """
        UPDATE wastask_tasks
        SET status = 'in_progress', updated_at = CURRENT_TIMESTAMP
        WHERE id = $1 AND status = 'todo'
        RETURNING id, title, status, updated_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, task_id)
        
        if not row:
            # Check if task exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM wastask_tasks WHERE id = $1)",
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
                    detail=f"Task {task_id} cannot be started (current status is not 'todo')"
                )
        
        return dict(row)


@router.get("/stats/summary", response_model=dict)
async def get_task_stats(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    current_user: dict = Depends(get_current_user)
):
    """Get task statistics."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            COUNT(*) as total_tasks,
            COUNT(CASE WHEN status = 'todo' THEN 1 END) as todo_tasks,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
            COUNT(CASE WHEN status = 'blocked' THEN 1 END) as blocked_tasks,
            COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority_tasks,
            COUNT(CASE WHEN priority = 'medium' THEN 1 END) as medium_priority_tasks,
            COUNT(CASE WHEN priority = 'low' THEN 1 END) as low_priority_tasks,
            AVG(estimated_hours) as avg_estimated_hours
        FROM wastask_tasks
        WHERE ($1::int IS NULL OR project_id = $1)
    """
    
    async with pool.acquire() as conn:
        stats = await conn.fetchrow(query, project_id)
        
        total = stats['total_tasks']
        completion_rate = round(
            (stats['completed_tasks'] / total * 100) if total > 0 else 0, 1
        )
        
        return {
            "total_tasks": total,
            "completion_rate": completion_rate,
            "by_status": {
                "todo": stats['todo_tasks'],
                "in_progress": stats['in_progress_tasks'],
                "completed": stats['completed_tasks'],
                "blocked": stats['blocked_tasks']
            },
            "by_priority": {
                "high": stats['high_priority_tasks'],
                "medium": stats['medium_priority_tasks'],
                "low": stats['low_priority_tasks']
            },
            "avg_estimated_hours": float(stats['avg_estimated_hours']) if stats['avg_estimated_hours'] else 0,
            "timestamp": datetime.utcnow().isoformat()
        }