"""
Stack Definition Agent - Intelligent Technology Stack Recommendation System

This agent analyzes project requirements from PRDs and automatically recommends
the optimal technology stack based on project characteristics, requirements,
complexity, and best practices.
"""
import re
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import asyncio

class ProjectType(Enum):
    """Types of projects that can be analyzed"""
    WEB_APP = "web_application"
    MOBILE_APP = "mobile_application"
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_application"
    MICROSERVICE = "microservice"
    DATA_PIPELINE = "data_pipeline"
    AI_ML = "ai_ml_project"
    ECOMMERCE = "ecommerce"
    CMS = "content_management"
    REAL_TIME = "real_time_application"

class ComplexityLevel(Enum):
    """Project complexity levels"""
    SIMPLE = "simple"      # 1-3 months, small team
    MEDIUM = "medium"      # 3-6 months, medium team
    COMPLEX = "complex"    # 6-12 months, large team
    ENTERPRISE = "enterprise"  # 12+ months, multiple teams

@dataclass
class TechnologyRecommendation:
    """A technology recommendation with justification"""
    category: str
    technology: str
    version: str
    confidence: float  # 0.0 to 1.0
    reason: str
    pros: List[str]
    cons: List[str]
    alternatives: List[str]
    learning_curve: str  # easy, medium, hard
    community_size: str  # small, medium, large
    maturity: str       # experimental, stable, mature, legacy

@dataclass
class StackRecommendation:
    """Complete stack recommendation"""
    project_type: ProjectType
    complexity: ComplexityLevel
    frontend: Optional[TechnologyRecommendation]
    backend: Optional[TechnologyRecommendation]
    database: TechnologyRecommendation
    deployment: TechnologyRecommendation
    additional_tools: List[TechnologyRecommendation]
    estimated_setup_time: str
    team_size_recommendation: str
    total_confidence: float
    warnings: List[str]
    next_steps: List[str]

class StackDefinitionAgent:
    """
    Intelligent agent for technology stack definition and recommendation
    """
    
    def __init__(self):
        self.technology_knowledge = self._load_technology_knowledge()
        self.compatibility_matrix = self._load_compatibility_matrix()
        self.project_patterns = self._load_project_patterns()
    
    async def analyze_prd_and_recommend_stack(
        self, 
        prd_content: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> StackRecommendation:
        """
        Main method: Analyze PRD content and recommend optimal technology stack
        """
        # Step 1: Analyze PRD to extract requirements
        requirements = await self._analyze_prd_requirements(prd_content)
        
        # Step 2: Determine project type and complexity
        project_type = self._determine_project_type(requirements)
        complexity = self._determine_complexity(requirements)
        
        # Step 3: Apply constraints (budget, timeline, team experience)
        filtered_options = self._apply_constraints(constraints or {})
        
        # Step 4: Generate technology recommendations
        recommendations = await self._generate_recommendations(
            project_type, complexity, requirements, filtered_options
        )
        
        # Step 5: Validate compatibility and optimize
        optimized_stack = self._optimize_stack_compatibility(recommendations, project_type, complexity)
        
        return optimized_stack
    
    async def _analyze_prd_requirements(self, prd_content: str) -> Dict[str, Any]:
        """Extract technical requirements from PRD content"""
        requirements = {
            'features': [],
            'non_functional': {},
            'integrations': [],
            'platforms': [],
            'scale_requirements': {},
            'security_requirements': [],
            'performance_requirements': {},
            'technology_mentions': [],
            'user_base': 'unknown',
            'real_time': False,
            'offline_support': False,
            'international': False,
            'mobile_required': False,
            'admin_panel': False,
            'analytics': False,
            'payments': False,
            'notifications': False,
            'file_uploads': False,
            'search': False,
            'social_features': False
        }
        
        prd_lower = prd_content.lower()
        
        # Detect project characteristics
        requirements['mobile_required'] = any(keyword in prd_lower for keyword in [
            'mobile app', 'ios', 'android', 'react native', 'flutter', 'mobile'
        ])
        
        requirements['real_time'] = any(keyword in prd_lower for keyword in [
            'real-time', 'realtime', 'live', 'websocket', 'chat', 'notification'
        ])
        
        requirements['ecommerce'] = any(keyword in prd_lower for keyword in [
            'ecommerce', 'e-commerce', 'shop', 'cart', 'payment', 'order', 'product'
        ])
        
        requirements['admin_panel'] = any(keyword in prd_lower for keyword in [
            'admin', 'dashboard', 'management', 'control panel'
        ])
        
        requirements['analytics'] = any(keyword in prd_lower for keyword in [
            'analytics', 'metrics', 'tracking', 'reports', 'statistics'
        ])
        
        requirements['payments'] = any(keyword in prd_lower for keyword in [
            'payment', 'stripe', 'paypal', 'billing', 'subscription'
        ])
        
        requirements['file_uploads'] = any(keyword in prd_lower for keyword in [
            'upload', 'file', 'image', 'document', 'attachment'
        ])
        
        requirements['search'] = any(keyword in prd_lower for keyword in [
            'search', 'elasticsearch', 'filter', 'query'
        ])
        
        requirements['international'] = any(keyword in prd_lower for keyword in [
            'international', 'multi-language', 'i18n', 'localization', 'global'
        ])
        
        # Extract scale indicators
        if any(word in prd_lower for word in ['million', 'millions', 'large scale']):
            requirements['scale_requirements']['expected_users'] = 'high'
        elif any(word in prd_lower for word in ['thousand', 'thousands', 'medium scale']):
            requirements['scale_requirements']['expected_users'] = 'medium'
        else:
            requirements['scale_requirements']['expected_users'] = 'low'
        
        # Extract mentioned technologies
        tech_patterns = [
            r'\b(react|vue|angular|svelte)\b',
            r'\b(node\.?js|python|java|go|rust|php)\b',
            r'\b(postgresql|mysql|mongodb|redis)\b',
            r'\b(aws|gcp|azure|docker|kubernetes)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, prd_lower)
            requirements['technology_mentions'].extend(matches)
        
        return requirements
    
    def _determine_project_type(self, requirements: Dict[str, Any]) -> ProjectType:
        """Determine the primary project type based on requirements"""
        
        if requirements.get('ecommerce'):
            return ProjectType.ECOMMERCE
        
        if requirements.get('mobile_required'):
            return ProjectType.MOBILE_APP
        
        if requirements.get('real_time'):
            return ProjectType.REAL_TIME
        
        if 'api' in str(requirements).lower():
            return ProjectType.API_SERVICE
        
        # Default to web application
        return ProjectType.WEB_APP
    
    def _determine_complexity(self, requirements: Dict[str, Any]) -> ComplexityLevel:
        """Determine project complexity based on requirements"""
        complexity_score = 0
        
        # Base features (each adds 1 point)
        features = [
            requirements.get('admin_panel', False),
            requirements.get('analytics', False),
            requirements.get('payments', False),
            requirements.get('file_uploads', False),
            requirements.get('search', False),
            requirements.get('real_time', False),
            requirements.get('international', False),
            requirements.get('mobile_required', False)
        ]
        
        complexity_score += sum(features)
        
        # Scale requirements (adds 2-4 points)
        scale = requirements.get('scale_requirements', {}).get('expected_users', 'low')
        if scale == 'high':
            complexity_score += 4
        elif scale == 'medium':
            complexity_score += 2
        
        # Technology mentions (established tech reduces complexity)
        tech_mentions = len(requirements.get('technology_mentions', []))
        if tech_mentions > 5:
            complexity_score += 2
        
        # Determine complexity level
        if complexity_score <= 2:
            return ComplexityLevel.SIMPLE
        elif complexity_score <= 5:
            return ComplexityLevel.MEDIUM
        elif complexity_score <= 8:
            return ComplexityLevel.COMPLEX
        else:
            return ComplexityLevel.ENTERPRISE
    
    def _apply_constraints(self, constraints: Dict[str, Any]) -> Dict[str, List[str]]:
        """Apply project constraints to filter technology options"""
        filtered = {
            'frontend': [],
            'backend': [],
            'database': [],
            'deployment': []
        }
        
        budget = constraints.get('budget', 'medium')  # low, medium, high
        timeline = constraints.get('timeline_months', 6)
        team_experience = constraints.get('team_experience', {})
        
        # Budget-based filtering
        if budget == 'low':
            # Prefer open-source, low-cost options
            filtered['deployment'] = ['vercel', 'netlify', 'heroku']
            filtered['database'] = ['postgresql', 'mysql', 'sqlite']
        elif budget == 'high':
            # Can afford premium services
            filtered['deployment'] = ['aws', 'gcp', 'azure']
            filtered['database'] = ['postgresql', 'mysql', 'mongodb', 'dynamodb']
        
        # Timeline-based filtering
        if timeline <= 3:
            # Prefer proven, rapid development tools
            filtered['frontend'] = ['react', 'vue', 'next.js']
            filtered['backend'] = ['node.js', 'python', 'express']
        
        return filtered
    
    async def _generate_recommendations(
        self,
        project_type: ProjectType,
        complexity: ComplexityLevel,
        requirements: Dict[str, Any],
        constraints: Dict[str, List[str]]
    ) -> Dict[str, TechnologyRecommendation]:
        """Generate technology recommendations for each category"""
        
        recommendations = {}
        
        # Frontend recommendations
        if project_type != ProjectType.API_SERVICE:
            recommendations['frontend'] = self._recommend_frontend(
                project_type, complexity, requirements, constraints
            )
        
        # Backend recommendations
        recommendations['backend'] = self._recommend_backend(
            project_type, complexity, requirements, constraints
        )
        
        # Database recommendations
        recommendations['database'] = self._recommend_database(
            project_type, complexity, requirements, constraints
        )
        
        # Deployment recommendations
        recommendations['deployment'] = self._recommend_deployment(
            project_type, complexity, requirements, constraints
        )
        
        # Additional tools
        recommendations['additional'] = self._recommend_additional_tools(
            project_type, complexity, requirements
        )
        
        return recommendations
    
    def _recommend_frontend(
        self, 
        project_type: ProjectType, 
        complexity: ComplexityLevel,
        requirements: Dict[str, Any],
        constraints: Dict[str, List[str]]
    ) -> TechnologyRecommendation:
        """Recommend frontend technology"""
        
        if project_type == ProjectType.MOBILE_APP:
            return TechnologyRecommendation(
                category="mobile_frontend",
                technology="React Native",
                version="0.72+",
                confidence=0.85,
                reason="Cross-platform development with single codebase",
                pros=[
                    "Single codebase for iOS and Android",
                    "Large community and ecosystem",
                    "Good performance for most use cases",
                    "Easy for React developers to learn"
                ],
                cons=[
                    "Some platform-specific features require native code",
                    "Bundle size can be large",
                    "Performance not as good as native"
                ],
                alternatives=["Flutter", "Native iOS/Android"],
                learning_curve="medium",
                community_size="large",
                maturity="mature"
            )
        
        # For web applications
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            return TechnologyRecommendation(
                category="frontend",
                technology="React",
                version="18.x",
                confidence=0.90,
                reason="Excellent for complex applications with rich ecosystem",
                pros=[
                    "Largest ecosystem and community",
                    "Excellent tooling and DevEx",
                    "Great performance with modern features",
                    "Strong TypeScript support",
                    "Abundant learning resources"
                ],
                cons=[
                    "Steeper learning curve",
                    "Rapid ecosystem changes",
                    "Setup complexity for beginners"
                ],
                alternatives=["Vue.js", "Angular", "Svelte"],
                learning_curve="medium",
                community_size="large",
                maturity="mature"
            )
        
        # For simpler projects
        return TechnologyRecommendation(
            category="frontend",
            technology="Vue.js",
            version="3.x",
            confidence=0.85,
            reason="Great balance of simplicity and power for medium projects",
            pros=[
                "Gentle learning curve",
                "Excellent documentation",
                "Good performance",
                "Progressive adoption",
                "Great developer experience"
            ],
            cons=[
                "Smaller ecosystem than React",
                "Less job market demand",
                "Fewer third-party components"
            ],
            alternatives=["React", "Svelte", "Alpine.js"],
            learning_curve="easy",
            community_size="medium",
            maturity="mature"
        )
    
    def _recommend_backend(
        self, 
        project_type: ProjectType, 
        complexity: ComplexityLevel,
        requirements: Dict[str, Any],
        constraints: Dict[str, List[str]]
    ) -> TechnologyRecommendation:
        """Recommend backend technology"""
        
        if requirements.get('real_time') or project_type == ProjectType.REAL_TIME:
            return TechnologyRecommendation(
                category="backend",
                technology="Node.js",
                version="18 LTS",
                confidence=0.88,
                reason="Excellent for real-time applications with WebSocket support",
                pros=[
                    "Great for real-time applications",
                    "Single language (JavaScript) across stack",
                    "Excellent WebSocket support",
                    "Large ecosystem (npm)",
                    "Good performance for I/O intensive apps"
                ],
                cons=[
                    "Single-threaded can be limiting",
                    "Not ideal for CPU-intensive tasks",
                    "Callback complexity (though improved with async/await)"
                ],
                alternatives=["Python (FastAPI)", "Go", "Java (Spring Boot)"],
                learning_curve="easy",
                community_size="large",
                maturity="mature"
            )
        
        if complexity == ComplexityLevel.ENTERPRISE:
            return TechnologyRecommendation(
                category="backend",
                technology="Python",
                version="3.11+",
                confidence=0.92,
                reason="Excellent for enterprise applications with rich ecosystem",
                pros=[
                    "Rich ecosystem for all use cases",
                    "Excellent for data processing and AI",
                    "Great frameworks (Django, FastAPI)",
                    "Easy to read and maintain",
                    "Strong typing with modern Python",
                    "Excellent testing tools"
                ],
                cons=[
                    "Can be slower than compiled languages",
                    "GIL limitations for CPU-bound tasks",
                    "Packaging complexity"
                ],
                alternatives=["Java", "Go", "C#"],
                learning_curve="easy",
                community_size="large",
                maturity="mature"
            )
        
        # Default recommendation
        return TechnologyRecommendation(
            category="backend",
            technology="Node.js",
            version="18 LTS",
            confidence=0.85,
            reason="Great balance of simplicity and performance",
            pros=[
                "Single language across stack",
                "Fast development",
                "Great for APIs and web services",
                "Excellent package ecosystem"
            ],
            cons=[
                "Single-threaded limitations",
                "Not ideal for CPU-intensive tasks"
            ],
            alternatives=["Python", "Go", "TypeScript"],
            learning_curve="easy",
            community_size="large",
            maturity="mature"
        )
    
    def _recommend_database(
        self, 
        project_type: ProjectType, 
        complexity: ComplexityLevel,
        requirements: Dict[str, Any],
        constraints: Dict[str, List[str]]
    ) -> TechnologyRecommendation:
        """Recommend database technology"""
        
        scale = requirements.get('scale_requirements', {}).get('expected_users', 'low')
        
        if scale == 'high' or complexity == ComplexityLevel.ENTERPRISE:
            return TechnologyRecommendation(
                category="database",
                technology="PostgreSQL",
                version="15+",
                confidence=0.95,
                reason="Best choice for high-scale, complex applications",
                pros=[
                    "ACID compliance and reliability",
                    "Excellent performance at scale",
                    "Rich feature set (JSON, full-text search)",
                    "Strong ecosystem and tooling",
                    "Great for complex queries",
                    "Excellent backup and replication"
                ],
                cons=[
                    "More complex setup than simple databases",
                    "Requires database administration knowledge",
                    "Can be overkill for simple applications"
                ],
                alternatives=["MySQL", "MongoDB", "CockroachDB"],
                learning_curve="medium",
                community_size="large",
                maturity="mature"
            )
        
        if project_type in [ProjectType.ECOMMERCE, ProjectType.CMS]:
            return TechnologyRecommendation(
                category="database",
                technology="PostgreSQL",
                version="15+",
                confidence=0.90,
                reason="Excellent for structured data and complex transactions",
                pros=[
                    "ACID transactions for payments",
                    "Excellent data integrity",
                    "Rich querying capabilities",
                    "Great performance"
                ],
                cons=[
                    "More setup complexity",
                    "Requires SQL knowledge"
                ],
                alternatives=["MySQL", "SQLite"],
                learning_curve="medium",
                community_size="large",
                maturity="mature"
            )
        
        # Default for simpler projects
        return TechnologyRecommendation(
            category="database",
            technology="SQLite",
            version="3.42+",
            confidence=0.80,
            reason="Perfect for simple to medium applications",
            pros=[
                "Zero setup and configuration",
                "Perfect for development",
                "Great performance for small to medium data",
                "ACID compliant",
                "Single file database"
            ],
            cons=[
                "Limited concurrent writes",
                "Not suitable for high-traffic applications",
                "Limited built-in networking"
            ],
            alternatives=["PostgreSQL", "MySQL"],
            learning_curve="easy",
            community_size="large",
            maturity="mature"
        )
    
    def _recommend_deployment(
        self, 
        project_type: ProjectType, 
        complexity: ComplexityLevel,
        requirements: Dict[str, Any],
        constraints: Dict[str, List[str]]
    ) -> TechnologyRecommendation:
        """Recommend deployment platform"""
        
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            return TechnologyRecommendation(
                category="deployment",
                technology="AWS",
                version="Current",
                confidence=0.88,
                reason="Most comprehensive cloud platform for complex applications",
                pros=[
                    "Most comprehensive service offering",
                    "Excellent scaling capabilities",
                    "Strong security features",
                    "Global presence",
                    "Mature ecosystem"
                ],
                cons=[
                    "Complex pricing model",
                    "Steep learning curve",
                    "Can be expensive",
                    "Vendor lock-in potential"
                ],
                alternatives=["Google Cloud", "Azure", "DigitalOcean"],
                learning_curve="hard",
                community_size="large",
                maturity="mature"
            )
        
        # For simpler projects
        return TechnologyRecommendation(
            category="deployment",
            technology="Vercel",
            version="Current",
            confidence=0.85,
            reason="Excellent for frontend and full-stack applications",
            pros=[
                "Zero-config deployments",
                "Excellent developer experience",
                "Great performance with edge network",
                "Easy integration with Git",
                "Generous free tier"
            ],
            cons=[
                "Limited backend capabilities",
                "Can be expensive for high traffic",
                "Vendor lock-in"
            ],
            alternatives=["Netlify", "Railway", "Heroku"],
            learning_curve="easy",
            community_size="medium",
            maturity="stable"
        )
    
    def _recommend_additional_tools(
        self,
        project_type: ProjectType,
        complexity: ComplexityLevel,
        requirements: Dict[str, Any]
    ) -> List[TechnologyRecommendation]:
        """Recommend additional tools and services"""
        
        tools = []
        
        # State management for complex frontends
        if complexity in [ComplexityLevel.COMPLEX, ComplexityLevel.ENTERPRISE]:
            tools.append(TechnologyRecommendation(
                category="state_management",
                technology="Zustand",
                version="4.x",
                confidence=0.85,
                reason="Modern, simple state management",
                pros=["Simple API", "TypeScript support", "Small bundle"],
                cons=["Less ecosystem than Redux"],
                alternatives=["Redux Toolkit", "Recoil"],
                learning_curve="easy",
                community_size="medium",
                maturity="stable"
            ))
        
        # Authentication
        if not requirements.get('simple_auth', True):
            tools.append(TechnologyRecommendation(
                category="authentication",
                technology="Auth0",
                version="Current",
                confidence=0.80,
                reason="Comprehensive authentication service",
                pros=["Complete auth solution", "Great security", "Easy integration"],
                cons=["Can be expensive", "Third-party dependency"],
                alternatives=["Firebase Auth", "Supabase Auth", "Custom JWT"],
                learning_curve="easy",
                community_size="large",
                maturity="mature"
            ))
        
        # Real-time communication
        if requirements.get('real_time'):
            tools.append(TechnologyRecommendation(
                category="real_time",
                technology="Socket.io",
                version="4.x",
                confidence=0.90,
                reason="Reliable real-time communication",
                pros=["Fallback support", "Room management", "Great documentation"],
                cons=["Can be overkill for simple use cases"],
                alternatives=["Native WebSockets", "Pusher"],
                learning_curve="medium",
                community_size="large",
                maturity="mature"
            ))
        
        return tools
    
    def _optimize_stack_compatibility(
        self, 
        recommendations: Dict[str, TechnologyRecommendation],
        project_type: ProjectType,
        complexity: ComplexityLevel
    ) -> StackRecommendation:
        """Optimize the stack for compatibility and create final recommendation"""
        
        # Calculate total confidence
        confidences = []
        for key, rec in recommendations.items():
            if isinstance(rec, list):
                # Handle additional tools which is a list
                for tool in rec:
                    if hasattr(tool, 'confidence'):
                        confidences.append(tool.confidence)
            elif rec and hasattr(rec, 'confidence'):
                confidences.append(rec.confidence)
        
        total_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Generate warnings
        warnings = []
        if total_confidence < 0.7:
            warnings.append("Overall confidence is low - consider simpler alternatives")
        
        # Generate next steps
        next_steps = [
            "Set up development environment",
            "Create project structure",
            "Configure chosen technologies",
            "Set up CI/CD pipeline",
            "Begin implementation of core features"
        ]
        
        return StackRecommendation(
            project_type=project_type,
            complexity=complexity,
            frontend=recommendations.get('frontend'),
            backend=recommendations.get('backend'),
            database=recommendations['database'],
            deployment=recommendations['deployment'],
            additional_tools=recommendations.get('additional', []),
            estimated_setup_time="2-3 days",
            team_size_recommendation="2-4 developers",
            total_confidence=total_confidence,
            warnings=warnings,
            next_steps=next_steps
        )
    
    def _load_technology_knowledge(self) -> Dict[str, Any]:
        """Load technology knowledge base"""
        # In a real implementation, this would load from a comprehensive database
        return {
            "frontend": {
                "react": {"popularity": 0.95, "learning_curve": "medium", "ecosystem": "large"},
                "vue": {"popularity": 0.80, "learning_curve": "easy", "ecosystem": "medium"},
                "angular": {"popularity": 0.70, "learning_curve": "hard", "ecosystem": "large"}
            },
            "backend": {
                "nodejs": {"popularity": 0.90, "learning_curve": "easy", "ecosystem": "large"},
                "python": {"popularity": 0.85, "learning_curve": "easy", "ecosystem": "large"},
                "java": {"popularity": 0.75, "learning_curve": "hard", "ecosystem": "large"}
            }
        }
    
    def _load_compatibility_matrix(self) -> Dict[str, List[str]]:
        """Load technology compatibility matrix"""
        return {
            "react": ["nodejs", "python", "java", "go"],
            "vue": ["nodejs", "python", "php"],
            "nodejs": ["postgresql", "mongodb", "redis"],
            "python": ["postgresql", "mysql", "redis"]
        }
    
    def _load_project_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common project patterns and their optimal stacks"""
        return {
            "ecommerce": {
                "frontend": "react",
                "backend": "nodejs",
                "database": "postgresql",
                "deployment": "aws"
            },
            "blog": {
                "frontend": "vue",
                "backend": "nodejs", 
                "database": "sqlite",
                "deployment": "vercel"
            }
        }