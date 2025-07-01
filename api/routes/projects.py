"""
Project management endpoints
"""
from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import json

from database_manager import get_db_pool
from core.models import Project, CreateProjectRequest, UpdateProjectRequest

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
            timeline, status, 
            created_at
        FROM wastask_projects
        WHERE ($1::text IS NULL OR status = $1)
        ORDER BY created_at DESC
        LIMIT $2 OFFSET $3
    """
    
    async with pool.acquire() as conn:
        rows = await conn.fetch(query, status, limit, offset)
        
        return [dict(row) for row in rows]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_project(project: CreateProjectRequest):
    """Create a new project."""
    pool = await get_db_pool()
    
    query = """
        INSERT INTO projects (name, description, status)
        VALUES ($1, $2, 'planning')
        RETURNING id, name, description, status, created_at
    """
    
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow(query, project.name, project.description)
            return dict(row)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create project: {str(e)}"
            )


@router.get("/{project_id}", response_model=dict)
async def get_project(project_id: int):
    """Get a specific project by ID."""
    pool = await get_db_pool()
    
    query = """
        SELECT 
            p.id, p.name, p.description, p.complexity_score, 
            p.estimated_timeline, p.tech_stack, p.status, 
            p.created_at, p.prd_analysis,
            COUNT(DISTINCT t.id) as task_count,
            COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) as completed_tasks
        FROM wastask_projects p
        LEFT JOIN tasks t ON p.id = t.project_id
        WHERE p.id = $1
        GROUP BY p.id
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, project_id)
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        project = dict(row)
        # Parse JSON fields
        if project['tech_stack']:
            project['tech_stack'] = json.loads(project['tech_stack'])
        if project['prd_analysis']:
            project['prd_analysis'] = json.loads(project['prd_analysis'])
        
        # Calculate progress
        if project['task_count'] > 0:
            project['progress'] = round(
                (project['completed_tasks'] / project['task_count']) * 100, 1
            )
        else:
            project['progress'] = 0
        
        return project


@router.put("/{project_id}", response_model=dict)
async def update_project(project_id: int, updates: UpdateProjectRequest):
    """Update a project."""
    pool = await get_db_pool()
    
    # Build dynamic update query
    update_fields = []
    params = [project_id]
    param_count = 2
    
    if updates.name is not None:
        update_fields.append(f"name = ${param_count}")
        params.append(updates.name)
        param_count += 1
    
    if updates.description is not None:
        update_fields.append(f"description = ${param_count}")
        params.append(updates.description)
        param_count += 1
    
    if updates.status is not None:
        update_fields.append(f"status = ${param_count}")
        params.append(updates.status)
        param_count += 1
    
    if not update_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update"
        )
    
    query = f"""
        UPDATE projects
        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING id, name, description, status, updated_at
    """
    
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, *params)
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        return dict(row)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int):
    """Delete a project and all its tasks."""
    pool = await get_db_pool()
    
    async with pool.acquire() as conn:
        # Start transaction
        async with conn.transaction():
            # Check if project exists
            exists = await conn.fetchval(
                "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1)",
                project_id
            )
            
            if not exists:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Project {project_id} not found"
                )
            
            # Delete tasks first (due to foreign key)
            await conn.execute("DELETE FROM tasks WHERE project_id = $1", project_id)
            
            # Delete project
            await conn.execute("DELETE FROM projects WHERE id = $1", project_id)


@router.get("/{project_id}/stats", response_model=dict)
async def get_project_stats(project_id: int):
    """Get detailed statistics for a project."""
    pool = await get_db_pool()
    
    # Check project exists
    async with pool.acquire() as conn:
        exists = await conn.fetchval(
            "SELECT EXISTS(SELECT 1 FROM projects WHERE id = $1)",
            project_id
        )
        
        if not exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Get task statistics
        stats_query = """
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending_tasks,
                COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks,
                COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority_tasks,
                COUNT(CASE WHEN priority = 'medium' THEN 1 END) as medium_priority_tasks,
                COUNT(CASE WHEN priority = 'low' THEN 1 END) as low_priority_tasks,
                AVG(CASE WHEN status = 'completed' AND estimated_duration IS NOT NULL 
                    THEN estimated_duration END) as avg_task_duration
            FROM tasks
            WHERE project_id = $1
        """
        
        stats = await conn.fetchrow(stats_query, project_id)
        
        return {
            "project_id": project_id,
            "task_statistics": dict(stats),
            "completion_rate": round(
                (stats['completed_tasks'] / stats['total_tasks'] * 100) 
                if stats['total_tasks'] > 0 else 0, 1
            ),
            "timestamp": datetime.utcnow().isoformat()
        }