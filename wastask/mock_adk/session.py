"""
Mock Session implementation
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class Session:
    def __init__(self, user_id: str, project_id: Optional[str] = None, **kwargs):
        self.user_id = user_id
        self.project_id = project_id
        self.created_at = kwargs.get('created_at', datetime.now(timezone.utc))
        self.metadata = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_id": self.user_id,
            "project_id": self.project_id,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
