#!/usr/bin/env python3
"""
WasTask - Sistema de Templates de Projetos
Templates dinâmicos para diferentes tipos de projetos
"""
from enum import Enum
from typing import List, Dict, Tuple
from dataclasses import dataclass
from core.models import TaskPriority

class ProjectType(Enum):
    """Tipos de projetos disponíveis"""
    ELEARNING = "e-learning"
    ECOMMERCE = "e-commerce"
    WEBAPP = "web-app"
    MOBILE_APP = "mobile-app"
    AI_ML = "ai-ml"
    FINTECH = "fintech"
    HEALTHCARE = "healthcare"
    GAMING = "gaming"
    CUSTOM = "custom"

@dataclass
class ProjectTemplate:
    """Template de projeto com sugestões"""
    type: ProjectType
    name_suggestions: List[str]
    description_template: str
    typical_features: List[str]
    suggested_task_count: int
    complexity_level: str

class ProjectTemplateManager:
    """Gerenciador de templates de projetos"""
    
    def __init__(self):
        self.templates = self._create_templates()
    
    def _create_templates(self) -> Dict[ProjectType, ProjectTemplate]:
        """Criar todos os templates disponíveis"""
        return {
            ProjectType.ELEARNING: ProjectTemplate(
                type=ProjectType.ELEARNING,
                name_suggestions=[
                    "Plataforma de E-learning",
                    "Academia Virtual",
                    "EduTech Platform",
                    "Learning Management System",
                    "Universidade Digital"
                ],
                description_template="Sistema completo de ensino online com funcionalidades de {features}",
                typical_features=[
                    "gestão de cursos", "videoaulas", "avaliações", "certificados",
                    "fóruns", "gamificação", "analytics", "mobile app"
                ],
                suggested_task_count=12,
                complexity_level="Alta"
            ),
            
            ProjectType.ECOMMERCE: ProjectTemplate(
                type=ProjectType.ECOMMERCE,
                name_suggestions=[
                    "Loja Virtual",
                    "E-commerce Platform",
                    "Marketplace Digital",
                    "Shopping Online",
                    "Boutique Digital"
                ],
                description_template="Plataforma de comércio eletrônico com {features}",
                typical_features=[
                    "catálogo de produtos", "carrinho de compras", "pagamentos",
                    "gestão de estoque", "logística", "analytics", "mobile app", "admin panel"
                ],
                suggested_task_count=15,
                complexity_level="Alta"
            ),
            
            ProjectType.WEBAPP: ProjectTemplate(
                type=ProjectType.WEBAPP,
                name_suggestions=[
                    "Aplicação Web",
                    "Sistema Web",
                    "Portal Online",
                    "Plataforma Digital",
                    "Dashboard Interativo"
                ],
                description_template="Aplicação web moderna com {features}",
                typical_features=[
                    "interface responsiva", "autenticação", "dashboard", "API REST",
                    "banco de dados", "notificações", "relatórios", "integrations"
                ],
                suggested_task_count=10,
                complexity_level="Média"
            ),
            
            ProjectType.MOBILE_APP: ProjectTemplate(
                type=ProjectType.MOBILE_APP,
                name_suggestions=[
                    "App Mobile",
                    "Aplicativo Móvel",
                    "Mobile Solution",
                    "Smartphone App",
                    "Cross-platform App"
                ],
                description_template="Aplicativo móvel nativo/híbrido com {features}",
                typical_features=[
                    "UI/UX mobile", "offline mode", "push notifications", "camera integration",
                    "GPS/location", "social login", "app store deployment", "analytics"
                ],
                suggested_task_count=8,
                complexity_level="Média"
            ),
            
            ProjectType.AI_ML: ProjectTemplate(
                type=ProjectType.AI_ML,
                name_suggestions=[
                    "Sistema de IA",
                    "Plataforma ML",
                    "AI Assistant",
                    "Machine Learning Platform",
                    "Intelligent System"
                ],
                description_template="Sistema inteligente baseado em IA com {features}",
                typical_features=[
                    "modelos de ML", "processamento de dados", "APIs de IA", "training pipeline",
                    "model deployment", "monitoring", "data visualization", "MLOps"
                ],
                suggested_task_count=14,
                complexity_level="Muito Alta"
            ),
            
            ProjectType.FINTECH: ProjectTemplate(
                type=ProjectType.FINTECH,
                name_suggestions=[
                    "Plataforma Financeira",
                    "FinTech Solution",
                    "Sistema Bancário",
                    "Carteira Digital",
                    "Investment Platform"
                ],
                description_template="Solução financeira digital com {features}",
                typical_features=[
                    "transações seguras", "KYC/compliance", "dashboard financeiro", "APIs bancárias",
                    "criptografia", "auditoria", "relatórios regulatórios", "mobile banking"
                ],
                suggested_task_count=18,
                complexity_level="Muito Alta"
            ),
            
            ProjectType.HEALTHCARE: ProjectTemplate(
                type=ProjectType.HEALTHCARE,
                name_suggestions=[
                    "Sistema de Saúde",
                    "HealthTech Platform",
                    "Telemedicina",
                    "Prontuário Eletrônico",
                    "Health Management"
                ],
                description_template="Sistema de saúde digital com {features}",
                typical_features=[
                    "prontuário eletrônico", "telemedicina", "agendamentos", "prescrições digitais",
                    "LGPD/HIPAA compliance", "integração com equipamentos", "analytics médicos", "mobile health"
                ],
                suggested_task_count=16,
                complexity_level="Muito Alta"
            ),
            
            ProjectType.GAMING: ProjectTemplate(
                type=ProjectType.GAMING,
                name_suggestions=[
                    "Jogo Digital",
                    "Game Platform",
                    "Gaming Experience",
                    "Interactive Game",
                    "Mobile Game"
                ],
                description_template="Experiência de jogo interativa com {features}",
                typical_features=[
                    "gameplay mechanics", "graphics engine", "multiplayer", "achievements",
                    "in-app purchases", "social features", "analytics", "cross-platform"
                ],
                suggested_task_count=12,
                complexity_level="Alta"
            ),
            
            ProjectType.CUSTOM: ProjectTemplate(
                type=ProjectType.CUSTOM,
                name_suggestions=[
                    "Projeto Personalizado",
                    "Solução Customizada",
                    "Sistema Específico",
                    "Aplicação Única",
                    "Custom Solution"
                ],
                description_template="Solução personalizada desenvolvida especificamente para {features}",
                typical_features=[
                    "requisitos específicos", "integrações customizadas", "workflow único",
                    "interface personalizada", "regras de negócio específicas"
                ],
                suggested_task_count=8,
                complexity_level="Variável"
            )
        }
    
    def get_template(self, project_type: ProjectType) -> ProjectTemplate:
        """Obter template por tipo"""
        return self.templates.get(project_type)
    
    def list_types(self) -> List[Tuple[str, str]]:
        """Listar tipos disponíveis"""
        return [(t.value, self.templates[t].complexity_level) for t in ProjectType]
    
    def get_suggestions(self, project_type: ProjectType) -> Dict:
        """Obter sugestões para um tipo de projeto"""
        template = self.templates.get(project_type)
        if not template:
            return {}
        
        return {
            "name_suggestions": template.name_suggestions,
            "features": template.typical_features,
            "suggested_tasks": template.suggested_task_count,
            "complexity": template.complexity_level,
            "description_template": template.description_template
        }

# Instância global
template_manager = ProjectTemplateManager()