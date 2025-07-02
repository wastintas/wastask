"""
Stack Definition Agent API endpoints
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, Dict, Any
from pydantic import BaseModel

from api.auth import get_current_user
from agents.stack_definition.agent import StackDefinitionAgent

router = APIRouter()

# Initialize the agent
stack_agent = StackDefinitionAgent()


class PRDAnalysisRequest(BaseModel):
    """Request model for PRD analysis"""
    prd_content: str
    constraints: Optional[Dict[str, Any]] = None


class TechnologyRecommendationResponse(BaseModel):
    """Response model for technology recommendations"""
    category: str
    technology: str
    version: str
    confidence: float
    reason: str
    pros: list[str]
    cons: list[str]
    alternatives: list[str]
    learning_curve: str
    community_size: str
    maturity: str


class StackRecommendationResponse(BaseModel):
    """Response model for complete stack recommendations"""
    project_type: str
    complexity: str
    frontend: Optional[Dict[str, Any]]
    backend: Optional[Dict[str, Any]]
    database: Dict[str, Any]
    deployment: Dict[str, Any]
    additional_tools: list[Dict[str, Any]]
    estimated_setup_time: str
    team_size_recommendation: str
    total_confidence: float
    warnings: list[str]
    next_steps: list[str]


@router.post("/analyze", response_model=Dict[str, Any])
async def analyze_prd_and_recommend_stack(
    request: PRDAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a PRD (Product Requirements Document) and recommend optimal technology stack
    """
    try:
        # Call the Stack Definition Agent
        recommendation = await stack_agent.analyze_prd_and_recommend_stack(
            prd_content=request.prd_content,
            constraints=request.constraints
        )
        
        # Convert dataclass to dict for JSON response
        def tech_rec_to_dict(tech_rec):
            if tech_rec is None:
                return None
            return {
                "category": tech_rec.category,
                "technology": tech_rec.technology,
                "version": tech_rec.version,
                "confidence": tech_rec.confidence,
                "reason": tech_rec.reason,
                "pros": tech_rec.pros,
                "cons": tech_rec.cons,
                "alternatives": tech_rec.alternatives,
                "learning_curve": tech_rec.learning_curve,
                "community_size": tech_rec.community_size,
                "maturity": tech_rec.maturity
            }
        
        return {
            "project_type": recommendation.project_type.value,
            "complexity": recommendation.complexity.value,
            "frontend": tech_rec_to_dict(recommendation.frontend),
            "backend": tech_rec_to_dict(recommendation.backend),
            "database": tech_rec_to_dict(recommendation.database),
            "deployment": tech_rec_to_dict(recommendation.deployment),
            "additional_tools": [tech_rec_to_dict(tool) for tool in recommendation.additional_tools],
            "estimated_setup_time": recommendation.estimated_setup_time,
            "team_size_recommendation": recommendation.team_size_recommendation,
            "total_confidence": recommendation.total_confidence,
            "warnings": recommendation.warnings,
            "next_steps": recommendation.next_steps,
            "analysis_timestamp": "2024-01-01T00:00:00Z"  # Would use actual timestamp
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze PRD: {str(e)}"
        )


@router.get("/technologies", response_model=Dict[str, Any])
async def get_supported_technologies(
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of supported technologies by category
    """
    return {
        "frontend": {
            "web": ["React", "Vue.js", "Angular", "Svelte", "Next.js", "Nuxt.js"],
            "mobile": ["React Native", "Flutter", "Native iOS", "Native Android"]
        },
        "backend": {
            "languages": ["Node.js", "Python", "Java", "Go", "Rust", "PHP", "C#"],
            "frameworks": ["Express.js", "FastAPI", "Django", "Spring Boot", "Gin", "Laravel"]
        },
        "database": {
            "relational": ["PostgreSQL", "MySQL", "SQLite"],
            "nosql": ["MongoDB", "Redis", "DynamoDB"],
            "search": ["Elasticsearch", "Algolia"]
        },
        "deployment": {
            "cloud": ["AWS", "Google Cloud", "Azure"],
            "platform": ["Vercel", "Netlify", "Heroku", "Railway"],
            "containerization": ["Docker", "Kubernetes"]
        },
        "tools": {
            "state_management": ["Redux", "Zustand", "Recoil", "Vuex", "Pinia"],
            "authentication": ["Auth0", "Firebase Auth", "Supabase Auth", "JWT"],
            "real_time": ["Socket.io", "WebSockets", "Pusher", "WebRTC"],
            "monitoring": ["Sentry", "LogRocket", "DataDog", "New Relic"]
        }
    }


@router.get("/project-types", response_model=Dict[str, Any])
async def get_supported_project_types(
    current_user: dict = Depends(get_current_user)
):
    """
    Get list of supported project types and their characteristics
    """
    return {
        "web_application": {
            "description": "Traditional web applications with frontend and backend",
            "typical_features": ["User authentication", "Database interactions", "API endpoints"],
            "complexity_range": ["simple", "enterprise"]
        },
        "mobile_application": {
            "description": "Native or cross-platform mobile applications",
            "typical_features": ["Platform-specific UIs", "Device APIs", "App stores"],
            "complexity_range": ["medium", "enterprise"]
        },
        "api_service": {
            "description": "Backend API services and microservices",
            "typical_features": ["RESTful/GraphQL APIs", "Authentication", "Data processing"],
            "complexity_range": ["simple", "complex"]
        },
        "ecommerce": {
            "description": "E-commerce platforms and online stores",
            "typical_features": ["Product catalog", "Payment processing", "Order management"],
            "complexity_range": ["medium", "enterprise"]
        },
        "real_time_application": {
            "description": "Applications requiring real-time communication",
            "typical_features": ["WebSockets", "Live updates", "Chat functionality"],
            "complexity_range": ["medium", "complex"]
        },
        "data_pipeline": {
            "description": "Data processing and analytics applications",
            "typical_features": ["Data ingestion", "ETL processes", "Analytics"],
            "complexity_range": ["complex", "enterprise"]
        }
    }


@router.post("/validate-stack", response_model=Dict[str, Any])
async def validate_technology_stack(
    stack: Dict[str, str],
    current_user: dict = Depends(get_current_user)
):
    """
    Validate compatibility between chosen technologies
    """
    try:
        # Get compatibility matrix from agent
        compatibility_matrix = stack_agent._load_compatibility_matrix()
        
        issues = []
        warnings = []
        score = 100
        
        # Check frontend-backend compatibility
        frontend = stack.get("frontend", "").lower()
        backend = stack.get("backend", "").lower()
        
        if frontend and backend:
            if frontend in compatibility_matrix:
                if backend not in compatibility_matrix[frontend]:
                    issues.append(f"{frontend} and {backend} may have integration challenges")
                    score -= 20
        
        # Check database compatibility
        database = stack.get("database", "").lower()
        if backend and database:
            if backend in compatibility_matrix:
                if database not in compatibility_matrix[backend]:
                    warnings.append(f"{backend} with {database} requires additional setup")
                    score -= 10
        
        # Overall assessment
        if score >= 90:
            assessment = "Excellent"
        elif score >= 70:
            assessment = "Good"
        elif score >= 50:
            assessment = "Fair"
        else:
            assessment = "Poor"
        
        return {
            "compatibility_score": score,
            "assessment": assessment,
            "issues": issues,
            "warnings": warnings,
            "recommendations": [
                "Consider using established patterns",
                "Review documentation for integration guides",
                "Plan for additional setup time if using uncommon combinations"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate stack: {str(e)}"
        )


@router.get("/examples", response_model=Dict[str, Any])
async def get_stack_examples(
    project_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Get example technology stacks for different project types
    """
    examples = {
        "web_application": {
            "simple": {
                "name": "Simple Web App",
                "frontend": "Vue.js",
                "backend": "Node.js",
                "database": "SQLite",
                "deployment": "Vercel"
            },
            "complex": {
                "name": "Enterprise Web App", 
                "frontend": "React",
                "backend": "Python",
                "database": "PostgreSQL",
                "deployment": "AWS"
            }
        },
        "ecommerce": {
            "medium": {
                "name": "E-commerce Store",
                "frontend": "Next.js",
                "backend": "Node.js",
                "database": "PostgreSQL",
                "deployment": "Vercel",
                "additional": ["Stripe", "Redis"]
            }
        },
        "mobile_application": {
            "medium": {
                "name": "Cross-platform Mobile App",
                "frontend": "React Native",
                "backend": "Python",
                "database": "PostgreSQL",
                "deployment": "AWS"
            }
        },
        "api_service": {
            "simple": {
                "name": "REST API",
                "backend": "FastAPI",
                "database": "PostgreSQL",
                "deployment": "Railway"
            }
        }
    }
    
    if project_type:
        return examples.get(project_type, {})
    
    return examples