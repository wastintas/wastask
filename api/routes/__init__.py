"""API routes module."""

# Import all routers to make them available
from . import health, projects, tasks, auth

__all__ = ["health", "projects", "tasks", "auth"]
