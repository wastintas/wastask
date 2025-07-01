"""
Simplified project management endpoints that work with current database structure
"""
from fastapi import APIRouter, HTTPException, status, Query, Depends
from typing import List, Optional
from datetime import datetime

from database_manager import get_db_pool
from api.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_projects(
    status: Optional[str] = Query(None, description="Filter by project status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of projects to return"),
    offset: int = Query(0, ge=0, description="Number of projects to skip")
):
    """List all projects with optional filtering."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            id, name, description, complexity_score, 
            timeline, status, created_at
        FROM wastask_projects
        WHERE ($1::text IS NULL OR status = $1)
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, status, limit, offset)
        return [dict(row) for row in rows]


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: int):
    """Get a specific project by ID with task count."""
    pool = await get_db_pool()
    
    # Get project details
    project_query = """
        SELECT 
            id, name, description, complexity_score, 
            timeline, status, created_at, total_hours
        FROM wastask_projects
        WHERE id = $1
    """
    
    async with pool.acquire() as conn:
        project = await conn.fetchrow(project_query, project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Get task count
        task_count_query = """
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks
            FROM wastask_tasks
            WHERE project_id = $1
        """
        
        task_stats = await conn.fetchrow(task_count_query, project_id)
        
        result = dict(project)
        result['task_count'] = task_stats['total_tasks']
        result['completed_tasks'] = task_stats['completed_tasks']
        result['progress'] = round(
            (task_stats['completed_tasks'] / task_stats['total_tasks'] * 100) 
            if task_stats['total_tasks'] > 0 else 0, 1
        )
        
        return result


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(
    name: str, 
    description: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new project."""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO wastask_projects (name, description, status)
        VALUES ($1, $2, 'planning')
        RETURNING id, name, description, status, created_at
    """
    
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(query, name, description or "")
            return dict(row)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create project: {str(e)}"
            )


@router.get("/{project_id}/tasks", response_model=List[dict])
async def get_project_tasks(project_id: int):
    """Get all tasks for a project."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            id, title, description, status, priority,
            estimated_hours, created_at
        FROM wastask_tasks
        WHERE project_id = $1
        ORDER BY 
            CASE priority 
                WHEN 'high' THEN 1 
                WHEN 'medium' THEN 2 
                WHEN 'low' THEN 3 
            END,
            created_at DESC
    """
    
    async with pool.acquire() as conn:
        # Check project exists
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM wastask_projects WHERE id = $1)",
            project_id
        )
        
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        rows = await conn.fetch(query, project_id)
        return [dict(row) for row in rows]


@router.get("/{project_id}/technologies", response_model=List[dict])
async def get_project_technologies(project_id: int):
    """Get technologies for a project."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            category, technology, version, reason, confidence
        FROM wastask_project_technologies
        WHERE project_id = $1
        ORDER BY confidence DESC
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, project_id)
        return [dict(row) for row in rows]