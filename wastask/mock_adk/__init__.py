"""
Mock Google ADK implementation for development/testing
"""
__version__ = "1.0.0"

from .agent import Agent, LlmAgent, FunctionTool
from .session import Session

__all__ = ["Agent", "LlmAgent", "FunctionTool", "Session"]
