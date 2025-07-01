#!/usr/bin/env python3
"""
WasTask - PRD Analysis Agent
Agente especializado em análise de Product Requirements Documents
"""
import re
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from wastask.mock_adk import LlmAgent
from integrations.context7_client import context7_client

console = Console()

class ProjectComplexity(Enum):
    SIMPLE = "simple"
    MEDIUM = "medium" 
    COMPLEX = "complex"
    ENTERPRISE = "enterprise"

@dataclass
class Feature:
    """Feature identificada no PRD"""
    name: str
    description: str
    priority: str  # HIGH, MEDIUM, LOW
    complexity: ProjectComplexity
    estimated_effort: int  # story points
    dependencies: List[str]
    
@dataclass
class TechnologyRecommendation:
    """Recomendação de tecnologia"""
    category: str  # frontend, backend, database, etc.
    technology: str
    version: str
    reason: str
    confidence: float  # 0-1

@dataclass
class ProjectSuggestion:
    """Sugestão de melhoria para o projeto"""
    type: str  # improvement, clarification, risk
    title: str
    description: str
    impact: str  # HIGH, MEDIUM, LOW
    effort: str  # LOW, MEDIUM, HIGH

@dataclass
class PRDAnalysisResult:
    """Resultado completo da análise do PRD"""
    project_name: str
    project_description: str
    features: List[Feature]
    technology_recommendations: List[TechnologyRecommendation]
    suggestions: List[ProjectSuggestion]
    clarifications_needed: List[str]
    estimated_timeline: str
    complexity_score: float
    risk_factors: List[str]

class PRDAnalyzer:
    """Agente especializado em análise de PRDs"""
    
    def __init__(self):
        self.analysis_agent = LlmAgent(
            name="prd_analyzer",
            model="claude-3-5-sonnet",
            description="Especialista em análise de Product Requirements Documents"
        )
        
        self.improvement_agent = LlmAgent(
            name="product_advisor", 
            model="claude-3-5-sonnet",
            description="Consultor de produto especializado em melhorias e otimizações"
        )
    
    async def analyze_prd(self, prd_content: str) -> PRDAnalysisResult:
        """Analisar PRD completo e retornar insights"""
        
        console.print(Panel(
            "🔍 Analyzing Product Requirements Document...",
            title="PRD Analysis",
            border_style="blue"
        ))
        
        # 1. Análise básica do documento
        basic_info = await self._extract_basic_info(prd_content)
        
        # 2. Identificar features
        features = await self._identify_features(prd_content)
        
        # 3. Analisar complexidade e esforço
        complexity_analysis = await self._analyze_complexity(prd_content, features)
        
        # 4. Recomendar tecnologias
        tech_recommendations = await self._recommend_technologies(prd_content, features)
        
        # 5. Gerar sugestões de melhoria
        suggestions = await self._generate_suggestions(prd_content, features)
        
        # 6. Identificar clarificações necessárias
        clarifications = await self._identify_clarifications(prd_content, features, tech_recommendations)
        
        result = PRDAnalysisResult(
            project_name=basic_info["name"],
            project_description=basic_info["description"],
            features=features,
            technology_recommendations=tech_recommendations,
            suggestions=suggestions,
            clarifications_needed=clarifications,
            estimated_timeline=complexity_analysis["timeline"],
            complexity_score=complexity_analysis["score"],
            risk_factors=complexity_analysis["risks"]
        )
        
        await self._display_analysis_summary(result)
        
        return result
    
    async def _extract_basic_info(self, prd_content: str) -> Dict[str, str]:
        """Extrair informações básicas do PRD"""
        
        prompt = f"""
Analyze this PRD and extract basic project information:

{prd_content}

Extract:
1. Project name (if not explicit, suggest one based on content)
2. One-sentence project description
3. Main objective/vision
4. Target audience

Respond in JSON format:
{{
  "name": "Project Name",
  "description": "Brief description",
  "objective": "Main objective",
  "audience": "Target audience"
}}
"""
        
        result = await self.analysis_agent.run(prompt)
        
        try:
            import json
            return json.loads(result.content)
        except:
            # Fallback parsing
            return {
                "name": "Extracted Project",
                "description": "Project extracted from PRD",
                "objective": "To be defined",
                "audience": "General users"
            }
    
    async def _identify_features(self, prd_content: str) -> List[Feature]:
        """Identificar features no PRD"""
        
        prompt = f"""
Analyze this PRD and identify all features/functionalities:

{prd_content}

For each feature, determine:
1. Name and description
2. Priority (HIGH/MEDIUM/LOW)
3. Complexity (SIMPLE/MEDIUM/COMPLEX/ENTERPRISE)
4. Estimated story points (1-21 scale)
5. Dependencies on other features

Respond in JSON format:
{{
  "features": [
    {{
      "name": "User Authentication",
      "description": "User login, registration, password reset",
      "priority": "HIGH",
      "complexity": "MEDIUM",
      "estimated_effort": 8,
      "dependencies": ["Database Setup"]
    }}
  ]
}}
"""
        
        result = await self.analysis_agent.run(prompt)
        
        try:
            import json
            data = json.loads(result.content)
            
            features = []
            for feature_data in data.get("features", []):
                features.append(Feature(
                    name=feature_data["name"],
                    description=feature_data["description"],
                    priority=feature_data["priority"],
                    complexity=ProjectComplexity(feature_data["complexity"].lower()),
                    estimated_effort=feature_data["estimated_effort"],
                    dependencies=feature_data.get("dependencies", [])
                ))
            
            return features
            
        except Exception as e:
            console.print(f"⚠️ Error parsing features: {e}")
            return []
    
    async def _analyze_complexity(self, prd_content: str, features: List[Feature]) -> Dict[str, Any]:
        """Analisar complexidade geral do projeto"""
        
        total_story_points = sum(f.estimated_effort for f in features)
        feature_count = len(features)
        
        # Calcular complexidade baseada em indicadores
        complexity_indicators = {
            "high_complexity_features": len([f for f in features if f.complexity in [ProjectComplexity.COMPLEX, ProjectComplexity.ENTERPRISE]]),
            "total_story_points": total_story_points,
            "feature_count": feature_count,
            "has_integrations": "integra" in prd_content.lower() or "api" in prd_content.lower(),
            "has_payments": "payment" in prd_content.lower() or "pagamento" in prd_content.lower(),
            "has_auth": "auth" in prd_content.lower() or "login" in prd_content.lower(),
            "has_realtime": "realtime" in prd_content.lower() or "real-time" in prd_content.lower()
        }
        
        # Score de complexidade (0-10)
        complexity_score = min(10, (
            complexity_indicators["total_story_points"] / 10 +
            complexity_indicators["high_complexity_features"] * 2 +
            complexity_indicators["feature_count"] / 5 +
            sum([
                complexity_indicators["has_integrations"],
                complexity_indicators["has_payments"],
                complexity_indicators["has_auth"],
                complexity_indicators["has_realtime"]
            ])
        ))
        
        # Estimativa de timeline
        weeks_estimate = max(4, total_story_points / 8)  # Assumindo 8 SP por semana
        timeline = f"{int(weeks_estimate)}-{int(weeks_estimate * 1.5)} weeks"
        
        # Identificar riscos
        risks = []
        if complexity_indicators["has_payments"]:
            risks.append("Payment integration complexity and compliance")
        if complexity_indicators["has_realtime"]:
            risks.append("Real-time features require complex infrastructure")
        if total_story_points > 80:
            risks.append("Large project scope may require team scaling")
        if complexity_indicators["high_complexity_features"] > 3:
            risks.append("Multiple complex features increase delivery risk")
        
        return {
            "score": complexity_score,
            "timeline": timeline,
            "risks": risks,
            "indicators": complexity_indicators
        }
    
    async def _recommend_technologies(self, prd_content: str, features: List[Feature]) -> List[TechnologyRecommendation]:
        """Recomendar stack tecnológica baseada no PRD"""
        
        prompt = f"""
Based on this PRD and features, recommend the best technology stack:

PRD Content:
{prd_content}

Features:
{[f.name + ": " + f.description for f in features]}

Consider:
1. Project requirements and scale
2. Team typical expertise
3. Modern best practices
4. Performance requirements
5. Scalability needs

Recommend technologies for:
- Frontend framework
- Backend framework/language
- Database
- Authentication
- Hosting/deployment
- Additional tools (cache, queues, etc.)

Respond in JSON format:
{{
  "recommendations": [
    {{
      "category": "frontend",
      "technology": "React",
      "version": "18.3.0",
      "reason": "Component-based, large ecosystem, TypeScript support",
      "confidence": 0.9
    }}
  ]
}}
"""
        
        result = await self.analysis_agent.run(prompt)
        
        try:
            import json
            data = json.loads(result.content)
            
            recommendations = []
            for rec_data in data.get("recommendations", []):
                recommendations.append(TechnologyRecommendation(
                    category=rec_data["category"],
                    technology=rec_data["technology"],
                    version=rec_data["version"],
                    reason=rec_data["reason"],
                    confidence=rec_data["confidence"]
                ))
            
            return recommendations
            
        except Exception as e:
            console.print(f"⚠️ Error parsing tech recommendations: {e}")
            # Fallback recommendations
            return [
                TechnologyRecommendation("frontend", "React", "18.3.0", "Popular and well-supported", 0.8),
                TechnologyRecommendation("backend", "Node.js", "20.0.0", "JavaScript ecosystem", 0.8),
                TechnologyRecommendation("database", "PostgreSQL", "16.0", "Reliable and feature-rich", 0.9)
            ]
    
    async def _generate_suggestions(self, prd_content: str, features: List[Feature]) -> List[ProjectSuggestion]:
        """Gerar sugestões de melhoria para o projeto"""
        
        prompt = f"""
Analyze this PRD and features to suggest improvements:

PRD: {prd_content}

Features: {[f.name for f in features]}

Suggest improvements in these categories:
1. Missing features that would add value
2. Architecture considerations
3. User experience improvements  
4. Performance optimizations
5. Security considerations
6. Scalability preparations

For each suggestion, provide:
- Type (improvement/clarification/risk)
- Title and description
- Impact (HIGH/MEDIUM/LOW)
- Implementation effort (LOW/MEDIUM/HIGH)

Respond in JSON format:
{{
  "suggestions": [
    {{
      "type": "improvement",
      "title": "Add caching layer",
      "description": "Implement Redis caching for better performance",
      "impact": "MEDIUM", 
      "effort": "MEDIUM"
    }}
  ]
}}
"""
        
        result = await self.improvement_agent.run(prompt)
        
        try:
            import json
            data = json.loads(result.content)
            
            suggestions = []
            for sug_data in data.get("suggestions", []):
                suggestions.append(ProjectSuggestion(
                    type=sug_data["type"],
                    title=sug_data["title"],
                    description=sug_data["description"],
                    impact=sug_data["impact"],
                    effort=sug_data["effort"]
                ))
            
            return suggestions
            
        except Exception as e:
            console.print(f"⚠️ Error parsing suggestions: {e}")
            return []
    
    async def _identify_clarifications(self, 
                                     prd_content: str, 
                                     features: List[Feature],
                                     tech_recommendations: List[TechnologyRecommendation]) -> List[str]:
        """Identificar clarificações necessárias"""
        
        clarifications = []
        
        # Verificar se tecnologias estão claras
        frontend_techs = [r for r in tech_recommendations if r.category == "frontend"]
        if not frontend_techs or any(r.confidence < 0.7 for r in frontend_techs):
            clarifications.append("Frontend framework preference - React, Vue.js, or Angular?")
        
        backend_techs = [r for r in tech_recommendations if r.category == "backend"]
        if not backend_techs or any(r.confidence < 0.7 for r in backend_techs):
            clarifications.append("Backend technology preference - Node.js, Python, Java, or other?")
        
        db_techs = [r for r in tech_recommendations if r.category == "database"]
        if not db_techs:
            clarifications.append("Database preference - PostgreSQL, MongoDB, or other?")
        
        # Verificar features ambíguas
        auth_features = [f for f in features if "auth" in f.name.lower()]
        if auth_features:
            clarifications.append("Authentication method - JWT, OAuth2, or custom?")
        
        payment_features = [f for f in features if "payment" in f.name.lower()]
        if payment_features:
            clarifications.append("Payment providers - Stripe, PayPal, or other?")
        
        # Verificar deployment
        if "deploy" not in prd_content.lower() and "host" not in prd_content.lower():
            clarifications.append("Deployment preference - AWS, GCP, Azure, or other?")
        
        return clarifications
    
    async def _display_analysis_summary(self, result: PRDAnalysisResult):
        """Exibir resumo da análise"""
        
        console.print(Panel(
            f"📋 **{result.project_name}**\n\n{result.project_description}",
            title="Project Overview",
            border_style="green"
        ))
        
        # Features table
        features_table = Table(title="🔍 Identified Features")
        features_table.add_column("Feature", style="cyan")
        features_table.add_column("Priority", style="yellow")
        features_table.add_column("Complexity", style="red")
        features_table.add_column("Story Points", style="green")
        
        for feature in result.features:
            features_table.add_row(
                feature.name,
                feature.priority,
                feature.complexity.value.title(),
                str(feature.estimated_effort)
            )
        
        console.print(features_table)
        
        # Technology recommendations
        if result.technology_recommendations:
            console.print("\n🛠️ **Technology Recommendations:**")
            for tech in result.technology_recommendations:
                confidence_emoji = "🟢" if tech.confidence > 0.8 else "🟡" if tech.confidence > 0.6 else "🔴"
                console.print(f"  {confidence_emoji} **{tech.category.title()}**: {tech.technology} v{tech.version}")
                console.print(f"     {tech.reason}")
        
        # Suggestions
        if result.suggestions:
            console.print(f"\n💡 **Suggestions ({len(result.suggestions)} total):**")
            for sug in result.suggestions[:3]:  # Show top 3
                impact_emoji = "🔴" if sug.impact == "HIGH" else "🟡" if sug.impact == "MEDIUM" else "🟢"
                console.print(f"  {impact_emoji} **{sug.title}**: {sug.description}")
        
        # Project stats
        console.print(f"\n📊 **Project Statistics:**")
        console.print(f"  • Complexity Score: {result.complexity_score:.1f}/10")
        console.print(f"  • Estimated Timeline: {result.estimated_timeline}")
        console.print(f"  • Total Features: {len(result.features)}")
        console.print(f"  • Total Story Points: {sum(f.estimated_effort for f in result.features)}")
        
        if result.clarifications_needed:
            console.print(f"\n❓ **Clarifications Needed ({len(result.clarifications_needed)}):**")
            for clarification in result.clarifications_needed:
                console.print(f"  • {clarification}")

# Instância global
prd_analyzer = PRDAnalyzer()