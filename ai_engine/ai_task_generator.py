#!/usr/bin/env python3
"""
WasTask - Gerador de Tarefas com IA
Sistema inteligente para gerar tarefas baseadas no contexto do projeto
"""
import random
from typing import List, Tuple, Dict
from core.models import TaskPriority
from project_templates import ProjectType, template_manager
from wastask.mock_adk import LlmAgent

class AITaskGenerator:
    """Gerador inteligente de tarefas usando IA"""
    
    def __init__(self):
        self.ia_agent = LlmAgent(
            name="task_generator",
            model="wastask-task-gen",
            description="Especialista em decomposição de projetos em tarefas"
        )
        self.priority_distribution = {
            TaskPriority.CRITICAL: 0.1,  # 10%
            TaskPriority.HIGH: 0.3,      # 30%
            TaskPriority.MEDIUM: 0.45,   # 45%
            TaskPriority.LOW: 0.15       # 15%
        }
    
    def generate_tasks_for_project(self, 
                                 project_name: str, 
                                 project_description: str,
                                 project_type: ProjectType = None,
                                 num_tasks: int = None) -> List[Tuple[str, TaskPriority]]:
        """
        Gerar tarefas inteligentes para um projeto
        
        Args:
            project_name: Nome do projeto
            project_description: Descrição detalhada
            project_type: Tipo do projeto (opcional)
            num_tasks: Número de tarefas (opcional, usa sugestão do template)
        
        Returns:
            Lista de (título_tarefa, prioridade)
        """
        
        # Usar template se fornecido
        if project_type:
            template = template_manager.get_template(project_type)
            if not num_tasks:
                num_tasks = template.suggested_task_count
        else:
            # Inferir tipo baseado na descrição
            project_type = self._infer_project_type(project_description)
            template = template_manager.get_template(project_type) if project_type else None
            if not num_tasks:
                num_tasks = template.suggested_task_count if template else 8
        
        # Gerar tarefas usando IA
        tasks = self._generate_ai_tasks(
            project_name, 
            project_description, 
            project_type,
            num_tasks
        )
        
        # Distribuir prioridades inteligentemente
        tasks_with_priorities = self._assign_smart_priorities(tasks, project_type)
        
        return tasks_with_priorities
    
    def _infer_project_type(self, description: str) -> ProjectType:
        """Inferir tipo do projeto baseado na descrição"""
        description_lower = description.lower()
        
        keywords_map = {
            ProjectType.ELEARNING: ["ensino", "educação", "curso", "learning", "aula", "estudante", "professor"],
            ProjectType.ECOMMERCE: ["loja", "venda", "produto", "compra", "ecommerce", "carrinho", "pagamento"],
            ProjectType.WEBAPP: ["web", "site", "portal", "dashboard", "sistema", "plataforma"],
            ProjectType.MOBILE_APP: ["mobile", "app", "smartphone", "android", "ios", "aplicativo"],
            ProjectType.AI_ML: ["ia", "inteligência", "machine learning", "ml", "ai", "algoritmo", "dados"],
            ProjectType.FINTECH: ["financeiro", "banco", "pagamento", "fintech", "carteira", "investimento"],
            ProjectType.HEALTHCARE: ["saúde", "médico", "hospital", "telemedicina", "prontuário", "healthcare"],
            ProjectType.GAMING: ["jogo", "game", "gaming", "jogador", "entretenimento"]
        }
        
        for project_type, keywords in keywords_map.items():
            if any(keyword in description_lower for keyword in keywords):
                return project_type
        
        return ProjectType.CUSTOM
    
    def _generate_ai_tasks(self, 
                          project_name: str, 
                          project_description: str,
                          project_type: ProjectType,
                          num_tasks: int) -> List[str]:
        """Gerar tarefas usando IA mock (simulação inteligente)"""
        
        # Base de tarefas por tipo de projeto
        task_templates = {
            ProjectType.ELEARNING: [
                "📋 Análise de requisitos e pesquisa pedagógica",
                "🎨 Design da interface e experiência do usuário",
                "👨‍🏫 Sistema de gestão de professores e instrutores",
                "👨‍🎓 Portal do estudante e área de aprendizado",
                "📚 Biblioteca de conteúdos e materiais didáticos",
                "🎥 Sistema de videoaulas e streaming",
                "📝 Módulo de avaliações e exercícios",
                "🏆 Sistema de certificações e badges",
                "💬 Fórums de discussão e chat",
                "📊 Analytics de aprendizado e relatórios",
                "📱 Aplicativo mobile para estudantes",
                "🔒 Segurança e conformidade com LGPD",
                "🤖 IA para recomendações personalizadas",
                "💳 Sistema de pagamentos e assinaturas",
                "🌍 Suporte multi-idioma e acessibilidade"
            ],
            ProjectType.ECOMMERCE: [
                "📋 Análise de mercado e requisitos de negócio",
                "🏪 Catálogo de produtos e categorização",
                "🛒 Carrinho de compras e wishlist",
                "💳 Sistema de pagamentos integrado",
                "📦 Gestão de estoque e inventário",
                "🚚 Sistema de logística e entregas",
                "👤 Gestão de usuários e perfis",
                "🎨 Design responsivo e UX/UI",
                "📊 Dashboard administrativo",
                "💬 Sistema de avaliações e reviews",
                "🔍 Busca avançada e filtros",
                "📱 App mobile para compras",
                "🔒 Segurança e conformidade PCI DSS",
                "📈 Analytics de vendas e marketing",
                "🤖 Sistema de recomendações",
                "📧 Marketing por email automatizado",
                "🎁 Sistema de cupons e promoções"
            ],
            ProjectType.WEBAPP: [
                "📋 Levantamento de requisitos funcionais",
                "🎨 Prototipação e design da interface",
                "⚙️ Arquitetura do sistema e tecnologias",
                "🔐 Sistema de autenticação e autorização",
                "📊 Dashboard principal e navegação",
                "💾 Modelagem e configuração do banco de dados",
                "🔗 Desenvolvimento da API REST",
                "📱 Interface responsiva e mobile-first",
                "🔍 Sistema de busca e filtros",
                "📈 Relatórios e analytics",
                "🔔 Sistema de notificações",
                "⚡ Otimização de performance",
                "🧪 Testes automatizados",
                "🚀 Deploy e CI/CD"
            ],
            ProjectType.MOBILE_APP: [
                "📋 Especificação de requisitos mobile",
                "🎨 Design da interface mobile (UI/UX)",
                "📱 Desenvolvimento para iOS/Android",
                "🔐 Autenticação e segurança mobile",
                "💾 Banco de dados local e sincronização",
                "🔔 Push notifications",
                "📷 Integração com câmera e galeria",
                "🗺️ Integração com GPS e mapas",
                "👥 Login social e compartilhamento",
                "📶 Modo offline e cache",
                "🧪 Testes em dispositivos reais",
                "🏪 Publicação nas app stores"
            ],
            ProjectType.AI_ML: [
                "📋 Definição do problema e objetivos",
                "📊 Coleta e preparação dos dados",
                "🔍 Análise exploratória dos dados",
                "🧠 Seleção e treinamento do modelo",
                "⚡ Pipeline de processamento de dados",
                "🔧 Feature engineering e seleção",
                "📈 Validação e métricas do modelo",
                "🚀 Deploy do modelo em produção",
                "📡 APIs para consumo do modelo",
                "📊 Monitoramento e drift detection",
                "🔄 Sistema de retreinamento automático",
                "🎯 Interface para predições",
                "📋 Documentação técnica e científica",
                "🔒 Segurança e privacidade dos dados"
            ],
            ProjectType.FINTECH: [
                "📋 Análise regulatória e compliance",
                "🔒 Arquitetura de segurança financeira",
                "🆔 KYC e verificação de identidade",
                "💳 Sistema de transações seguras",
                "🏦 Integração com APIs bancárias",
                "📊 Dashboard financeiro e relatórios",
                "🔐 Criptografia e proteção de dados",
                "📱 App mobile para operações",
                "⚖️ Sistema de auditoria e logs",
                "📈 Analytics de risco e fraude",
                "💱 Processamento de pagamentos",
                "📋 Relatórios regulatórios",
                "🤖 IA para detecção de fraudes",
                "🔔 Alertas e notificações de segurança",
                "🌍 Suporte multi-moeda",
                "📞 Atendimento ao cliente integrado",
                "🧪 Testes de penetração e segurança"
            ],
            ProjectType.HEALTHCARE: [
                "📋 Análise de requisitos médicos",
                "🏥 Prontuário eletrônico do paciente",
                "👨‍⚕️ Sistema de gestão médica",
                "📅 Agendamento de consultas",
                "💊 Prescrições digitais",
                "🎥 Telemedicina e consultas remotas",
                "🔒 Conformidade LGPD/HIPAA",
                "📊 Relatórios médicos e estatísticas",
                "💾 Integração com equipamentos médicos",
                "📱 App para pacientes",
                "🚨 Alertas médicos e emergências",
                "💳 Sistema de cobrança e convênios",
                "📈 Analytics de saúde populacional",
                "🔐 Segurança de dados médicos"
            ],
            ProjectType.GAMING: [
                "📋 Concept e game design document",
                "🎨 Arte conceitual e assets visuais",
                "🎮 Mecânicas de gameplay core",
                "🖼️ Engine gráfica e rendering",
                "🎵 Sistema de áudio e música",
                "👥 Multiplayer e networking",
                "🏆 Sistema de achievements",
                "💰 In-app purchases e monetização",
                "📱 Adaptação para mobile",
                "🌐 Features sociais e leaderboards",
                "📈 Analytics de gameplay",
                "🧪 Playtesting e balanceamento"
            ],
            ProjectType.CUSTOM: [
                "📋 Análise detalhada de requisitos",
                "🎨 Design da solução customizada",
                "⚙️ Arquitetura do sistema",
                "💾 Modelagem de dados específica",
                "🔗 Integrações customizadas",
                "🔐 Segurança e autenticação",
                "📊 Interface e experiência do usuário",
                "🧪 Testes e validação"
            ]
        }
        
        # Obter templates para o tipo
        available_tasks = task_templates.get(project_type, task_templates[ProjectType.CUSTOM])
        
        # Selecionar tarefas baseado no contexto
        if num_tasks >= len(available_tasks):
            # Se pediu mais tarefas do que temos, usar todas + algumas genéricas
            selected_tasks = available_tasks.copy()
            generic_tasks = [
                "📋 Documentação técnica do projeto",
                "🧪 Testes de integração",
                "⚡ Otimização de performance",
                "🔒 Auditoria de segurança",
                "📊 Monitoramento e observabilidade"
            ]
            selected_tasks.extend(generic_tasks[:num_tasks - len(available_tasks)])
        else:
            # Selecionar as mais relevantes
            selected_tasks = available_tasks[:num_tasks]
        
        # Personalizar baseado no projeto
        personalized_tasks = []
        for task in selected_tasks:
            # Substituir termos genéricos pelo contexto do projeto
            personalized_task = task.replace("sistema", project_name.lower())
            personalized_task = personalized_task.replace("plataforma", project_name.lower())
            personalized_tasks.append(personalized_task)
        
        return personalized_tasks[:num_tasks]
    
    def _assign_smart_priorities(self, 
                               tasks: List[str], 
                               project_type: ProjectType) -> List[Tuple[str, TaskPriority]]:
        """Atribuir prioridades inteligentes baseadas no tipo e conteúdo"""
        
        high_priority_keywords = [
            "requisitos", "análise", "arquitetura", "segurança", "autenticação",
            "banco de dados", "api", "core", "principal"
        ]
        
        critical_priority_keywords = [
            "segurança", "compliance", "lgpd", "hipaa", "pci", "criptografia"
        ]
        
        low_priority_keywords = [
            "documentação", "analytics", "relatórios", "otimização", "mobile app",
            "notificações", "email"
        ]
        
        tasks_with_priorities = []
        
        for i, task in enumerate(tasks):
            task_lower = task.lower()
            
            # Tarefas críticas (segurança, compliance)
            if any(keyword in task_lower for keyword in critical_priority_keywords):
                priority = TaskPriority.CRITICAL
            
            # Primeiras tarefas tendem a ser mais importantes
            elif i < len(tasks) * 0.3:  # Primeiros 30%
                if any(keyword in task_lower for keyword in high_priority_keywords):
                    priority = TaskPriority.HIGH
                else:
                    priority = TaskPriority.MEDIUM
            
            # Tarefas de baixa prioridade
            elif any(keyword in task_lower for keyword in low_priority_keywords):
                priority = TaskPriority.LOW
            
            # Distribuição baseada em posição
            else:
                if i < len(tasks) * 0.5:  # Primeiros 50%
                    priority = TaskPriority.MEDIUM
                else:
                    priority = TaskPriority.LOW
            
            tasks_with_priorities.append((task, priority))
        
        return tasks_with_priorities
    
    def generate_project_suggestions(self, project_type: ProjectType) -> Dict:
        """Gerar sugestões completas para um tipo de projeto"""
        template = template_manager.get_template(project_type)
        if not template:
            return {}
        
        # Escolher nome aleatório
        suggested_name = random.choice(template.name_suggestions)
        
        # Gerar descrição
        features_sample = random.sample(template.typical_features, 
                                      min(4, len(template.typical_features)))
        suggested_description = template.description_template.format(
            features=", ".join(features_sample)
        )
        
        return {
            "name": suggested_name,
            "description": suggested_description,
            "type": project_type,
            "suggested_tasks": template.suggested_task_count,
            "complexity": template.complexity_level,
            "features": template.typical_features
        }

# Instância global
ai_task_generator = AITaskGenerator()