"""
Configuration settings for WasTask
"""
import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="WASTASK_",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "WasTask"
    version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=4, env="WORKERS")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    allowed_hosts: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")
    database_pool_size: int = Field(default=20, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    redis_cache_ttl: int = Field(default=3600, env="REDIS_CACHE_TTL")  # 1 hour
    
    # Google ADK
    adk_model_default: str = Field(default="gemini-2.0-flash", env="ADK_MODEL_DEFAULT")
    adk_model_complex: str = Field(default="claude-3.5-sonnet", env="ADK_MODEL_COMPLEX")
    adk_model_simple: str = Field(default="gemini-flash", env="ADK_MODEL_SIMPLE")
    adk_temperature: float = Field(default=0.1, env="ADK_TEMPERATURE")
    adk_max_tokens: int = Field(default=4000, env="ADK_MAX_TOKENS")
    
    # LLM Configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # GitHub Integration
    github_app_id: Optional[str] = Field(default=None, env="GITHUB_APP_ID")
    github_private_key: Optional[str] = Field(default=None, env="GITHUB_PRIVATE_KEY")
    github_webhook_secret: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    github_default_token: Optional[str] = Field(default=None, env="GITHUB_DEFAULT_TOKEN")
    
    # Rate Limiting
    rate_limit_requests: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    rate_limit_window: int = Field(default=60, env="RATE_LIMIT_WINDOW")  # seconds
    
    # Cost Management
    cost_optimization_enabled: bool = Field(default=True, env="COST_OPTIMIZATION_ENABLED")
    max_daily_cost_usd: float = Field(default=50.0, env="MAX_DAILY_COST_USD")
    semantic_cache_enabled: bool = Field(default=True, env="SEMANTIC_CACHE_ENABLED")
    semantic_cache_similarity_threshold: float = Field(default=0.95, env="SEMANTIC_CACHE_SIMILARITY_THRESHOLD")
    
    # Monitoring
    enable_telemetry: bool = Field(default=True, env="ENABLE_TELEMETRY")
    sentry_dsn: Optional[str] = Field(default=None, env="SENTRY_DSN")
    prometheus_enabled: bool = Field(default=False, env="PROMETHEUS_ENABLED")
    
    # Agent Configuration
    agent_session_timeout: int = Field(default=1800, env="AGENT_SESSION_TIMEOUT")  # 30 minutes
    max_agent_memory: int = Field(default=50, env="MAX_AGENT_MEMORY")  # messages
    agent_retry_attempts: int = Field(default=3, env="AGENT_RETRY_ATTEMPTS")
    
    # File Storage
    upload_max_size: int = Field(default=10 * 1024 * 1024, env="UPLOAD_MAX_SIZE")  # 10MB
    allowed_file_types: List[str] = Field(
        default=["txt", "md", "json", "csv", "pdf"],
        env="ALLOWED_FILE_TYPES"
    )
    
    @property
    def database_config(self) -> dict:
        """Database configuration dictionary"""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
        }
    
    @property
    def redis_config(self) -> dict:
        """Redis configuration dictionary"""
        return {
            "url": self.redis_url,
            "decode_responses": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {},
            "health_check_interval": 30,
        }
    
    @property
    def model_routing_config(self) -> dict:
        """Model routing configuration"""
        return {
            "simple": {
                "model": self.adk_model_simple,
                "max_cost_per_request": 0.01,
                "use_cases": ["simple_queries", "status_updates", "basic_parsing"]
            },
            "balanced": {
                "model": self.adk_model_default,
                "max_cost_per_request": 0.05,
                "use_cases": ["general_tasks", "moderate_complexity", "planning"]
            },
            "complex": {
                "model": self.adk_model_complex,
                "max_cost_per_request": 0.20,
                "use_cases": ["complex_planning", "deep_analysis", "code_review"]
            }
        }


# Global settings instance
settings = Settings()


class PromptTemplates:
    """Centralized prompt templates"""
    
    COORDINATOR_SYSTEM = """
    You are the WasTask Coordinator, an AI project management assistant.
    
    Your responsibilities:
    - Analyze user requests and route to appropriate specialized agents
    - Maintain project context and user preferences
    - Provide high-level guidance and project insights
    - Coordinate between different agents for complex workflows
    
    Available agents:
    - planning_agent: Project planning, task decomposition, timeline creation
    - task_agent: Task management, status updates, assignment coordination
    - github_agent: GitHub integration, issue sync, PR management
    - analytics_agent: Progress reports, metrics, performance analysis
    
    Always be helpful, professional, and focused on project success.
    """
    
    TASK_DECOMPOSITION = """
    Analyze the following project or task and break it down into actionable items:

    PROJECT/TASK: {input}

    Follow this structured approach:

    1. SCOPE ANALYSIS:
       - Main objective: [Clear definition]
       - Success criteria: [Measurable outcomes]
       - Constraints: [Limitations and dependencies]

    2. TASK BREAKDOWN:
       Create a hierarchical structure:
       - Level 1: Major phases/milestones
       - Level 2: Specific tasks per phase
       - Level 3: Sub-tasks if needed

    3. ESTIMATIONS:
       - Time estimates (hours/days)
       - Complexity level (1-5)
       - Required skills/roles

    4. DEPENDENCIES:
       - Which tasks must be completed first
       - External dependencies
       - Potential blockers

    5. PRIORITIZATION:
       - Critical path items
       - Quick wins
       - Nice-to-have features

    Format output as structured JSON for easy processing.
    """
    
    GITHUB_INTEGRATION = """
    You are the GitHub Integration Agent for WasTask.
    
    Your capabilities:
    - Create and update GitHub issues
    - Sync task status with issue status
    - Generate pull request templates
    - Monitor repository activity
    - Create project boards and milestones
    
    When processing requests:
    1. Validate repository access and permissions
    2. Maintain consistency between WasTask and GitHub
    3. Use appropriate labels and metadata
    4. Follow repository conventions and standards
    5. Handle rate limits gracefully
    
    Always confirm actions before making changes to repositories.
    """


# Export commonly used configurations
__all__ = [
    "Settings",
    "settings",
    "PromptTemplates",
]