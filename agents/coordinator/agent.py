"""
WasTask Coordinator Agent - Main orchestrator for the system
"""
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

try:
    from google.adk import Agent, LlmAgent, FunctionTool
    from google.adk.core.session import Session
except ImportError:
    # Use mock implementation for development
    from wastask.mock_adk import Agent, LlmAgent, FunctionTool
    from wastask.mock_adk.session import Session

from wastask.config.settings import settings, PromptTemplates
from wastask.core.models import (
    Project, Task, User, ChatMessage, ChatRequest, ChatResponse,
    ProjectStatus, TaskStatus, TaskPriority
)


logger = logging.getLogger(__name__)


class WasTaskCoordinator:
    """
    Main coordinator agent that orchestrates all other agents in the system.
    Handles user requests, maintains context, and delegates to specialized agents.
    """
    
    def __init__(self, model: str = None):
        self.model = model or settings.adk_model_default
        self.session_store: Dict[str, Session] = {}
        self.context_store: Dict[str, Dict[str, Any]] = {}
        
        # Initialize the coordinator agent
        self.agent = self._create_agent()
        
        # Initialize sub-agents (will be created as the system grows)
        self.sub_agents = {}
        
    def _create_agent(self) -> LlmAgent:
        """Create the main coordinator agent"""
        tools = [
            FunctionTool(self.create_project_tool),
            FunctionTool(self.list_projects_tool),
            FunctionTool(self.get_project_tool),
            FunctionTool(self.create_task_tool),
            FunctionTool(self.list_tasks_tool),
            FunctionTool(self.update_task_status_tool),
            FunctionTool(self.analyze_project_tool),
        ]
        
        return LlmAgent(
            name="wastask_coordinator",
            model=self.model,
            description="WasTask project management coordinator",
            instruction=PromptTemplates.COORDINATOR_SYSTEM,
            tools=tools,
            temperature=settings.adk_temperature,
            max_tokens=settings.adk_max_tokens,
        )
    
    async def process_message(
        self, 
        user_id: str, 
        message: str, 
        project_id: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> ChatResponse:
        """
        Process a user message and return a response.
        
        Args:
            user_id: ID of the user sending the message
            message: The user's message
            project_id: Optional project context
            session_id: Optional session ID for context
            
        Returns:
            ChatResponse with the agent's response
        """
        try:
            # Get or create session
            session_key = session_id or f"{user_id}_{project_id or 'global'}"
            session = self._get_or_create_session(session_key, user_id, project_id)
            
            # Add user message to context
            self._add_message_to_context(session_key, "user", message)
            
            # Prepare context for the agent
            context = self._prepare_context(session_key, project_id)
            
            # Process with the agent
            response = await self.agent.run(
                message, 
                context=context,
                session=session
            )
            
            # Add assistant response to context
            self._add_message_to_context(session_key, "assistant", response.content)
            
            # Extract suggestions and actions from response
            suggestions = self._extract_suggestions(response.content)
            actions = self._extract_actions(response.content)
            
            return ChatResponse(
                response=response.content,
                agent_type="coordinator",
                suggestions=suggestions,
                actions=actions
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return ChatResponse(
                response=f"I apologize, but I encountered an error processing your request: {str(e)}",
                agent_type="coordinator",
                suggestions=["Please try rephrasing your request", "Check if all required information is provided"],
                actions=[]
            )
    
    def _get_or_create_session(self, session_key: str, user_id: str, project_id: Optional[str]) -> Session:
        """Get existing session or create a new one"""
        if session_key not in self.session_store:
            self.session_store[session_key] = Session(
                user_id=user_id,
                project_id=project_id,
                created_at=datetime.now(timezone.utc)
            )
            self.context_store[session_key] = {
                "messages": [],
                "project_context": {},
                "user_preferences": {},
                "active_tasks": []
            }
        return self.session_store[session_key]
    
    def _add_message_to_context(self, session_key: str, role: str, content: str):
        """Add a message to the session context"""
        if session_key in self.context_store:
            self.context_store[session_key]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Keep only last N messages to manage memory
            max_messages = settings.max_agent_memory
            if len(self.context_store[session_key]["messages"]) > max_messages:
                self.context_store[session_key]["messages"] = \
                    self.context_store[session_key]["messages"][-max_messages:]
    
    def _prepare_context(self, session_key: str, project_id: Optional[str]) -> Dict[str, Any]:
        """Prepare context for the agent"""
        context = self.context_store.get(session_key, {})
        
        # Add project-specific context if available
        if project_id:
            # In a real implementation, this would fetch from database
            context["project_context"] = {
                "project_id": project_id,
                "current_tasks": [],
                "recent_activity": []
            }
        
        return context
    
    def _extract_suggestions(self, response: str) -> List[str]:
        """Extract actionable suggestions from agent response"""
        suggestions = []
        
        # Simple pattern matching for suggestions
        if "you could" in response.lower():
            suggestions.append("Consider the suggested approach")
        if "recommend" in response.lower():
            suggestions.append("Review the recommendations provided")
        if "next step" in response.lower():
            suggestions.append("Follow the suggested next steps")
            
        return suggestions
    
    def _extract_actions(self, response: str) -> List[Dict[str, Any]]:
        """Extract actionable items from agent response"""
        actions = []
        
        # Simple pattern matching for actions
        if "create" in response.lower() and "project" in response.lower():
            actions.append({
                "type": "create_project",
                "description": "Create a new project based on the discussion"
            })
        if "create" in response.lower() and "task" in response.lower():
            actions.append({
                "type": "create_task",
                "description": "Create tasks based on the analysis"
            })
            
        return actions
    
    # Tool implementations
    def create_project_tool(self, name: str, description: str = "", github_repo: str = "") -> Dict[str, Any]:
        """Create a new project"""
        try:
            # In a real implementation, this would use the database
            project_id = f"proj_{hash(name) % 10000:04d}"
            
            project_data = {
                "id": project_id,
                "name": name,
                "description": description,
                "github_repo": github_repo,
                "status": ProjectStatus.PLANNING.value,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "status": "success",
                "project": project_data,
                "message": f"Project '{name}' created successfully with ID: {project_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create project: {str(e)}"
            }
    
    def list_projects_tool(self, user_id: str = "", status: str = "") -> Dict[str, Any]:
        """List projects for a user"""
        try:
            # Mock data - in real implementation, query database
            projects = [
                {
                    "id": "proj_0001",
                    "name": "Sample Project",
                    "description": "A sample project for demonstration",
                    "status": "active",
                    "task_count": 5,
                    "created_at": "2025-01-01T00:00:00Z"
                }
            ]
            
            if status:
                projects = [p for p in projects if p["status"] == status]
            
            return {
                "status": "success",
                "projects": projects,
                "count": len(projects)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list projects: {str(e)}"
            }
    
    def get_project_tool(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        try:
            # Mock data - in real implementation, query database
            project = {
                "id": project_id,
                "name": "Sample Project",
                "description": "A sample project for demonstration",
                "status": "active",
                "tasks": [
                    {"id": "task_001", "title": "Setup project", "status": "completed"},
                    {"id": "task_002", "title": "Implement features", "status": "in_progress"},
                    {"id": "task_003", "title": "Testing", "status": "pending"}
                ],
                "created_at": "2025-01-01T00:00:00Z"
            }
            
            return {
                "status": "success",
                "project": project
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to get project: {str(e)}"
            }
    
    def create_task_tool(
        self, 
        project_id: str, 
        title: str, 
        description: str = "", 
        priority: str = "medium"
    ) -> Dict[str, Any]:
        """Create a new task"""
        try:
            task_id = f"task_{hash(title) % 10000:04d}"
            
            task_data = {
                "id": task_id,
                "title": title,
                "description": description,
                "priority": priority,
                "status": TaskStatus.PENDING.value,
                "project_id": project_id,
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            return {
                "status": "success",
                "task": task_data,
                "message": f"Task '{title}' created successfully with ID: {task_id}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to create task: {str(e)}"
            }
    
    def list_tasks_tool(self, project_id: str, status: str = "") -> Dict[str, Any]:
        """List tasks for a project"""
        try:
            # Mock data - in real implementation, query database
            tasks = [
                {
                    "id": "task_001",
                    "title": "Setup project structure",
                    "description": "Initialize the project with proper structure",
                    "status": "completed",
                    "priority": "high",
                    "created_at": "2025-01-01T00:00:00Z"
                },
                {
                    "id": "task_002",
                    "title": "Implement core features",
                    "description": "Develop the main functionality",
                    "status": "in_progress",
                    "priority": "high",
                    "created_at": "2025-01-01T06:00:00Z"
                }
            ]
            
            if status:
                tasks = [t for t in tasks if t["status"] == status]
            
            return {
                "status": "success",
                "tasks": tasks,
                "count": len(tasks)
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to list tasks: {str(e)}"
            }
    
    def update_task_status_tool(self, task_id: str, status: str) -> Dict[str, Any]:
        """Update task status"""
        try:
            # Mock implementation - in real implementation, update database
            return {
                "status": "success",
                "message": f"Task {task_id} status updated to {status}",
                "task": {
                    "id": task_id,
                    "status": status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to update task status: {str(e)}"
            }
    
    def analyze_project_tool(self, project_id: str) -> Dict[str, Any]:
        """Analyze project progress and provide insights"""
        try:
            # Mock analysis - in real implementation, compute real metrics
            analysis = {
                "project_id": project_id,
                "total_tasks": 10,
                "completed_tasks": 3,
                "in_progress_tasks": 4,
                "pending_tasks": 3,
                "completion_percentage": 30,
                "estimated_completion": "2025-02-15",
                "bottlenecks": ["Waiting for design approval", "API integration dependency"],
                "recommendations": [
                    "Focus on completing in-progress tasks",
                    "Break down large tasks into smaller ones",
                    "Review and update task priorities"
                ],
                "health_score": 7.5,
                "risk_factors": ["Scope creep", "Resource constraints"]
            }
            
            return {
                "status": "success",
                "analysis": analysis
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze project: {str(e)}"
            }


# Global coordinator instance
coordinator = WasTaskCoordinator()