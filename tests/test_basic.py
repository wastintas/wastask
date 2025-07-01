"""
Basic tests for WasTask functionality
"""
import pytest
from datetime import datetime, timezone

from wastask.core.models import Project, Task, User, TaskStatus, ProjectStatus
from wastask.config.settings import settings


def test_settings_load():
    """Test that settings load correctly"""
    assert settings.app_name == "WasTask"
    assert settings.version == "0.1.0"
    assert settings.adk_model_default is not None


def test_user_model():
    """Test User model creation and validation"""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User"
    )
    
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_admin is False
    assert isinstance(user.created_at, datetime)


def test_project_model():
    """Test Project model creation and validation"""
    project = Project(
        name="Test Project",
        description="A test project",
        owner_id="550e8400-e29b-41d4-a716-446655440000",
        status=ProjectStatus.PLANNING
    )
    
    assert project.name == "Test Project"
    assert project.status == ProjectStatus.PLANNING
    assert isinstance(project.created_at, datetime)


def test_task_model():
    """Test Task model creation and validation"""
    task = Task(
        title="Test Task",
        description="A test task",
        project_id="550e8400-e29b-41d4-a716-446655440000",
        creator_id="550e8400-e29b-41d4-a716-446655440001",
        status=TaskStatus.PENDING
    )
    
    assert task.title == "Test Task"
    assert task.status == TaskStatus.PENDING
    assert task.priority.value == "medium"  # default priority
    assert isinstance(task.created_at, datetime)


def test_model_routing_config():
    """Test model routing configuration"""
    config = settings.model_routing_config
    
    assert "simple" in config
    assert "balanced" in config
    assert "complex" in config
    
    for tier, tier_config in config.items():
        assert "model" in tier_config
        assert "max_cost_per_request" in tier_config
        assert "use_cases" in tier_config


def test_database_config():
    """Test database configuration"""
    db_config = settings.database_config
    
    assert "url" in db_config
    assert "echo" in db_config
    assert "pool_size" in db_config
    assert "max_overflow" in db_config


def test_redis_config():
    """Test Redis configuration"""
    redis_config = settings.redis_config
    
    assert "url" in redis_config
    assert "decode_responses" in redis_config
    assert redis_config["decode_responses"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])