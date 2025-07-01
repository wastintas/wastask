"""
Mock Agent implementation
"""
import asyncio
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass


@dataclass
class ToolResult:
    content: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class FunctionTool:
    def __init__(self, func: Callable):
        self.func = func
        self.name = func.__name__
        self.description = func.__doc__ or f"Tool: {func.__name__}"
    
    def execute(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class Agent:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    async def run(self, message: str, **kwargs) -> ToolResult:
        # Mock implementation
        return ToolResult(content=f"Mock response for: {message}")


class LlmAgent(Agent):
    def __init__(
        self, 
        name: str, 
        model: str = "mock-model",
        description: str = "",
        instruction: str = "",
        tools: List[FunctionTool] = None,
        temperature: float = 0.1,
        max_tokens: int = 4000,
        **kwargs
    ):
        super().__init__(name, description)
        self.model = model
        self.instruction = instruction
        self.tools = tools or []
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    async def run(self, message: str, context: Dict[str, Any] = None, session: Any = None) -> ToolResult:
        # Mock intelligent response based on message content
        message_lower = message.lower()
        
        if "create" in message_lower and "project" in message_lower:
            return ToolResult(
                content="I can help you create a new project. Let me gather the requirements and create a structured plan.",
                metadata={"action": "create_project"}
            )
        elif "list" in message_lower and "project" in message_lower:
            return ToolResult(
                content="Here are your projects:\n- Sample Project (active)\n- Demo Project (planning)",
                metadata={"action": "list_projects"}
            )
        elif "task" in message_lower:
            return ToolResult(
                content="I can help you manage tasks. Would you like to create, update, or list tasks?",
                metadata={"action": "task_management"}
            )
        elif "analyze" in message_lower:
            return ToolResult(
                content="Project Analysis:\n- Total tasks: 10\n- Completed: 3 (30%)\n- In progress: 4\n- Pending: 3\n\nRecommendations:\n- Focus on completing in-progress tasks\n- Review pending task priorities",
                metadata={"action": "analyze"}
            )
        else:
            return ToolResult(
                content=f"I understand you want to know about: {message}\n\nAs your AI project management assistant, I can help with:\n- Creating and managing projects\n- Task planning and decomposition\n- Progress analysis\n- GitHub integration\n\nHow can I assist you today?",
                metadata={"action": "general_help"}
            )
