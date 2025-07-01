"""
Core data models for WasTask
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict


class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class User(BaseModel):
    """User model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    full_name: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    github_username: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Project(BaseModel):
    """Project model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.PLANNING
    owner_id: UUID
    github_repo: Optional[str] = None  # Format: "owner/repo"
    settings: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Task(BaseModel):
    """Task model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    project_id: UUID
    assignee_id: Optional[UUID] = None
    creator_id: UUID
    parent_task_id: Optional[UUID] = None  # For sub-tasks
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    github_issue_number: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class TaskDependency(BaseModel):
    """Task dependency model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    task_id: UUID  # The task that depends on another
    depends_on_task_id: UUID  # The task that must be completed first
    dependency_type: str = "blocks"  # blocks, relates_to, subtask_of
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentSession(BaseModel):
    """Agent session model for tracking conversations"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    project_id: Optional[UUID] = None
    agent_type: str  # coordinator, planning, tasks, github, analytics
    context: Dict[str, Any] = Field(default_factory=dict)
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectMember(BaseModel):
    """Project membership model"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    user_id: UUID
    role: str = "member"  # owner, admin, member, viewer
    permissions: List[str] = Field(default_factory=list)
    joined_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GitHubIntegration(BaseModel):
    """GitHub integration settings"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    repository: str  # Format: "owner/repo"
    access_token: str  # Encrypted
    webhook_secret: Optional[str] = None  # Encrypted
    sync_enabled: bool = True
    sync_settings: Dict[str, Any] = Field(default_factory=dict)
    last_sync: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Request/Response models for API
class CreateProjectRequest(BaseModel):
    """Request model for creating a project"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    github_repo: Optional[str] = None


class UpdateProjectRequest(BaseModel):
    """Request model for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    github_repo: Optional[str] = None


class CreateTaskRequest(BaseModel):
    """Request model for creating a task"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    assignee_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    estimated_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)


class UpdateTaskRequest(BaseModel):
    """Request model for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee_id: Optional[UUID] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    """Request model for chat with agent"""
    message: str = Field(..., min_length=1, max_length=10000)
    project_id: Optional[UUID] = None
    agent_type: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat with agent"""
    response: str
    agent_type: str
    suggestions: List[str] = Field(default_factory=list)
    actions: List[Dict[str, Any]] = Field(default_factory=list)