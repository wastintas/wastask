#!/usr/bin/env python3
"""
WasTask - Gerador Inteligente de Tarefas
Sistema que analisa projetos e gera tarefas verdadeiramente customizadas
"""
import re
import random
from typing import List, Tuple, Dict, Set
from dataclasses import dataclass
from core.models import TaskPriority
from wastask.mock_adk import LlmAgent

@dataclass
class ProjectAnalysis:
    """Análise completa do projeto"""
    keywords: Set[str]
    domain: str
    complexity_indicators: List[str]
    technology_stack: List[str]
    business_requirements: List[str]
    technical_requirements: List[str]
    estimated_complexity: str

class IntelligentTaskGenerator:
    """Gerador que analisa o projeto e cria tarefas específicas"""
    
    def __init__(self):
        self.ia_agent = LlmAgent(
            name="intelligent_task_gen",
            model="gpt-4-task-analysis",
            description="Analista especialista em decomposição inteligente de projetos"
        )
        
        # Base de conhecimento para análise
        self.tech_patterns = {
            'web': ['website', 'portal', 'dashboard', 'web app', 'browser', 'html', 'css', 'javascript'],
            'mobile': ['app', 'mobile', 'android', 'ios', 'smartphone', 'tablet', 'aplicativo'],
            'ai_ml': ['inteligência artificial', 'machine learning', 'ai', 'ml', 'algoritmo', 'dados', 'predição'],
            'ecommerce': ['loja', 'venda', 'produto', 'compra', 'carrinho', 'pagamento', 'checkout'],
            'finance': ['financeiro', 'banco', 'pagamento', 'transação', 'carteira', 'investimento'],
            'health': ['saúde', 'médico', 'hospital', 'paciente', 'prontuário', 'telemedicina'],
            'education': ['educação', 'ensino', 'curso', 'aprendizado', 'estudante', 'professor'],
            'game': ['jogo', 'game', 'jogador', 'gaming', 'entretenimento', 'diversão']
        }
        
        # Palavras que indicam complexidade
        self.complexity_indicators = {
            'high': ['enterprise', 'corporativo', 'escala', 'milhões', 'global', 'distribuído', 'microservices'],
            'medium': ['sistema', 'plataforma', 'integração', 'api', 'dashboard', 'relatórios'],
            'low': ['simples', 'básico', 'pequeno', 'local', 'mvp', 'protótipo']
        }
    
    def analyze_project(self, name: str, description: str) -> ProjectAnalysis:
        """Analisar projeto detalhadamente"""
        text = f"{name} {description}".lower()
        words = re.findall(r'\w+', text)
        keywords = set(words)
        
        # Detectar domínio
        domain_scores = {}
        for domain, patterns in self.tech_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text)
            if score > 0:
                domain_scores[domain] = score
        
        primary_domain = max(domain_scores.keys(), key=lambda k: domain_scores[k]) if domain_scores else 'custom'
        
        # Analisar complexidade
        complexity_score = 0
        complexity_indicators = []
        
        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    complexity_indicators.append(indicator)
                    if level == 'high':
                        complexity_score += 3
                    elif level == 'medium':
                        complexity_score += 2
                    else:
                        complexity_score += 1
        
        if complexity_score >= 8:
            complexity = "Muito Alta"
        elif complexity_score >= 5:
            complexity = "Alta"
        elif complexity_score >= 2:
            complexity = "Média"
        else:
            complexity = "Baixa"
        
        # Extrair tecnologias mencionadas
        tech_stack = []
        tech_keywords = ['react', 'vue', 'angular', 'python', 'java', 'node', 'php', 'django', 'flask', 
                        'mysql', 'postgres', 'mongodb', 'redis', 'docker', 'aws', 'azure', 'gcp']
        
        for tech in tech_keywords:
            if tech in text:
                tech_stack.append(tech)
        
        # Extrair requisitos de negócio
        business_patterns = [
            r'usuario[s]?', r'cliente[s]?', r'venda[s]?', r'pagamento[s]?', r'relatório[s]?',
            r'dashboard', r'admin', r'gestão', r'controle', r'monitoramento'
        ]
        
        business_requirements = []
        for pattern in business_patterns:
            if re.search(pattern, text):
                business_requirements.append(pattern.replace(r'[s]?', '').replace(r'\b', ''))
        
        # Requisitos técnicos
        technical_requirements = []
        if 'api' in text or 'integração' in text:
            technical_requirements.append('APIs e Integrações')
        if 'banco' in text or 'database' in text or 'dados' in text:
            technical_requirements.append('Banco de Dados')
        if 'segurança' in text or 'autenticação' in text:
            technical_requirements.append('Segurança e Autenticação')
        if 'mobile' in text or 'app' in text:
            technical_requirements.append('Mobile/Responsive')
        
        return ProjectAnalysis(
            keywords=keywords,
            domain=primary_domain,
            complexity_indicators=complexity_indicators,
            technology_stack=tech_stack,
            business_requirements=business_requirements,
            technical_requirements=technical_requirements,
            estimated_complexity=complexity
        )
    
    def generate_custom_tasks(self, name: str, description: str, num_tasks: int = 8) -> List[Tuple[str, TaskPriority]]:
        """Gerar tarefas completamente customizadas baseadas na análise"""
        
        # Analisar projeto
        analysis = self.analyze_project(name, description)
        
        # Gerar tarefas base obrigatórias
        base_tasks = self._generate_base_tasks(name, analysis)
        
        # Gerar tarefas específicas do domínio
        domain_tasks = self._generate_domain_specific_tasks(name, analysis)
        
        # Gerar tarefas baseadas nos requisitos
        requirement_tasks = self._generate_requirement_tasks(name, analysis)
        
        # Combinar e priorizar
        all_tasks = base_tasks + domain_tasks + requirement_tasks
        
        # Selecionar as melhores tarefas
        selected_tasks = self._select_best_tasks(all_tasks, num_tasks)
        
        # Atribuir prioridades inteligentes
        prioritized_tasks = self._assign_intelligent_priorities(selected_tasks, analysis)
        
        return prioritized_tasks
    
    def _generate_base_tasks(self, project_name: str, analysis: ProjectAnalysis) -> List[str]:
        """Gerar tarefas base obrigatórias"""
        tasks = [
            f"📋 Análise detalhada de requisitos para {project_name}",
            f"🎨 Design da arquitetura e estrutura do {project_name}",
        ]
        
        # Adicionar tarefas baseadas na complexidade
        if analysis.estimated_complexity in ["Alta", "Muito Alta"]:
            tasks.extend([
                f"📐 Modelagem detalhada da arquitetura de {project_name}",
                f"📊 Planejamento de escalabilidade para {project_name}",
            ])
        
        return tasks
    
    def _generate_domain_specific_tasks(self, project_name: str, analysis: ProjectAnalysis) -> List[str]:
        """Gerar tarefas específicas do domínio detectado"""
        domain_tasks = {
            'web': [
                f"🌐 Desenvolvimento da interface web do {project_name}",
                f"⚡ Implementação do frontend responsivo para {project_name}",
                f"🔗 Criação das APIs REST do {project_name}",
                f"📱 Otimização mobile da interface do {project_name}",
            ],
            'mobile': [
                f"📱 Desenvolvimento nativo do app {project_name}",
                f"🎨 Design de UX/UI mobile para {project_name}",
                f"🔔 Sistema de notificações push do {project_name}",
                f"📶 Implementação de modo offline no {project_name}",
            ],
            'ai_ml': [
                f"🧠 Desenvolvimento do modelo de IA para {project_name}",
                f"📊 Pipeline de processamento de dados do {project_name}",
                f"🔬 Treinamento e validação do modelo {project_name}",
                f"⚡ Deploy e otimização do modelo em produção",
            ],
            'ecommerce': [
                f"🛒 Sistema de carrinho de compras do {project_name}",
                f"💳 Integração de pagamentos para {project_name}",
                f"📦 Gestão de estoque e produtos do {project_name}",
                f"🚚 Sistema de logística e entregas",
            ],
            'finance': [
                f"🔒 Implementação de segurança financeira no {project_name}",
                f"💱 Sistema de transações seguras",
                f"📊 Dashboard financeiro e relatórios",
                f"⚖️ Conformidade regulatória e auditoria",
            ],
            'health': [
                f"🏥 Módulo de prontuário eletrônico para {project_name}",
                f"👨‍⚕️ Sistema de gestão médica",
                f"🔒 Conformidade LGPD/HIPAA para dados médicos",
                f"📱 App móvel para pacientes",
            ],
            'education': [
                f"📚 Plataforma de conteúdo educacional do {project_name}",
                f"🎓 Sistema de avaliações e certificações",
                f"👨‍🏫 Portal do professor/instrutor",
                f"📈 Analytics de aprendizado e progresso",
            ],
            'game': [
                f"🎮 Mecânicas de gameplay do {project_name}",
                f"🎨 Sistema de gráficos e renderização",
                f"🏆 Sistema de conquistas e progressão",
                f"👥 Funcionalidades multiplayer",
            ]
        }
        
        return domain_tasks.get(analysis.domain, [
            f"⚙️ Desenvolvimento das funcionalidades core do {project_name}",
            f"🔧 Implementação das regras de negócio específicas",
        ])
    
    def _generate_requirement_tasks(self, project_name: str, analysis: ProjectAnalysis) -> List[str]:
        """Gerar tarefas baseadas nos requisitos identificados"""
        tasks = []
        
        # Tarefas baseadas nos requisitos técnicos
        for req in analysis.technical_requirements:
            if req == 'APIs e Integrações':
                tasks.append(f"🔗 Desenvolvimento e documentação das APIs do {project_name}")
            elif req == 'Banco de Dados':
                tasks.append(f"💾 Modelagem e implementação do banco de dados")
            elif req == 'Segurança e Autenticação':
                tasks.append(f"🔐 Sistema de autenticação e segurança")
            elif req == 'Mobile/Responsive':
                tasks.append(f"📱 Adaptação responsiva e mobile do {project_name}")
        
        # Tarefas baseadas na stack tecnológica
        if 'docker' in analysis.technology_stack:
            tasks.append(f"🐳 Containerização com Docker do {project_name}")
        
        if any(cloud in analysis.technology_stack for cloud in ['aws', 'azure', 'gcp']):
            tasks.append(f"☁️ Deploy em cloud e configuração de infraestrutura")
        
        # Tarefas baseadas nos requisitos de negócio
        if 'admin' in analysis.business_requirements:
            tasks.append(f"⚙️ Painel administrativo do {project_name}")
        
        if 'relatório' in analysis.business_requirements:
            tasks.append(f"📊 Sistema de relatórios e analytics")
        
        return tasks
    
    def _select_best_tasks(self, all_tasks: List[str], num_tasks: int) -> List[str]:
        """Selecionar as melhores tarefas evitando duplicações"""
        # Remover duplicações e tarefas muito similares
        unique_tasks = []
        seen_keywords = set()
        
        for task in all_tasks:
            # Extrair palavras-chave da tarefa
            task_keywords = set(re.findall(r'\w+', task.lower()))
            task_keywords.discard('de')  # Remover preposições
            task_keywords.discard('do')
            task_keywords.discard('da')
            
            # Verificar se já temos tarefa similar
            similarity = len(task_keywords.intersection(seen_keywords))
            if similarity < 3:  # Menos de 3 palavras em comum
                unique_tasks.append(task)
                seen_keywords.update(task_keywords)
        
        # Selecionar até o número solicitado
        return unique_tasks[:num_tasks]
    
    def _assign_intelligent_priorities(self, tasks: List[str], analysis: ProjectAnalysis) -> List[Tuple[str, TaskPriority]]:
        """Atribuir prioridades baseadas no contexto e análise"""
        prioritized = []
        
        for i, task in enumerate(tasks):
            task_lower = task.lower()
            
            # Prioridade CRITICAL - Segurança e conformidade
            if any(word in task_lower for word in ['segurança', 'conformidade', 'lgpd', 'hipaa', 'pci']):
                priority = TaskPriority.CRITICAL
            
            # Prioridade HIGH - Requisitos base e arquitetura
            elif any(word in task_lower for word in ['análise', 'arquitetura', 'requisitos', 'modelagem']):
                priority = TaskPriority.HIGH
            
            # Prioridade HIGH - Core do projeto
            elif any(word in task_lower for word in ['core', 'principal', 'base', 'essencial']):
                priority = TaskPriority.HIGH
            
            # Primeiras tarefas são mais importantes
            elif i < len(tasks) * 0.3:
                priority = TaskPriority.HIGH
            
            # Prioridade LOW - Features secundárias
            elif any(word in task_lower for word in ['analytics', 'relatório', 'otimização', 'mobile']):
                priority = TaskPriority.LOW
            
            # Resto é MEDIUM
            else:
                priority = TaskPriority.MEDIUM
            
            prioritized.append((task, priority))
        
        return prioritized
    
    def explain_analysis(self, analysis: ProjectAnalysis) -> str:
        """Explicar a análise realizada"""
        explanation = f"""
🔍 **Análise do Projeto:**

📊 **Domínio Detectado:** {analysis.domain.title()}
⚡ **Complexidade Estimada:** {analysis.estimated_complexity}

🛠️ **Stack Tecnológica:** {', '.join(analysis.technology_stack) if analysis.technology_stack else 'Não especificada'}

📋 **Requisitos de Negócio:** {', '.join(analysis.business_requirements) if analysis.business_requirements else 'Genéricos'}

🔧 **Requisitos Técnicos:** {', '.join(analysis.technical_requirements) if analysis.technical_requirements else 'Básicos'}

💡 **Indicadores de Complexidade:** {', '.join(analysis.complexity_indicators) if analysis.complexity_indicators else 'Nenhum específico'}
        """
        return explanation.strip()

# Instância global
intelligent_generator = IntelligentTaskGenerator()