#!/usr/bin/env python3
"""
PRD Enhancer para WasTask
Usa IA real para melhorar PRDs fracos e fazer perguntas inteligentes
"""
import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class PRDQuality:
    """Análise da qualidade do PRD"""
    score: float  # 0-10
    weaknesses: List[str]
    missing_sections: List[str]
    suggestions: List[str]
    is_weak: bool

@dataclass
class PRDEnhancement:
    """Resultado do melhoramento do PRD"""
    original_prd: str
    enhanced_prd: str
    clarification_questions: List[str]
    suggested_features: List[str]
    technology_hints: List[str]
    quality_before: float
    quality_after: float

class PRDEnhancer:
    """Sistema de melhoramento de PRDs usando IA"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.use_anthropic = bool(os.getenv('ANTHROPIC_API_KEY'))
        
    async def analyze_prd_quality(self, prd_content: str) -> PRDQuality:
        """Analisar qualidade do PRD"""
        
        # Critérios de qualidade
        quality_indicators = {
            'length': len(prd_content.split()) >= 500,  # Pelo menos 500 palavras
            'sections': self._has_standard_sections(prd_content),
            'features': self._has_detailed_features(prd_content),
            'technical_specs': self._has_technical_specs(prd_content),
            'user_stories': self._has_user_stories(prd_content),
            'acceptance_criteria': self._has_acceptance_criteria(prd_content),
            'non_functional': self._has_non_functional_requirements(prd_content)
        }
        
        # Calcular score
        score = sum(quality_indicators.values()) / len(quality_indicators) * 10
        
        # Identificar fraquezas
        weaknesses = []
        missing_sections = []
        
        if not quality_indicators['length']:
            weaknesses.append("PRD muito curto - falta detalhamento")
        if not quality_indicators['sections']:
            missing_sections.extend(["Objetivos", "Funcionalidades", "Requisitos Técnicos"])
        if not quality_indicators['features']:
            weaknesses.append("Features descritas de forma muito vaga")
        if not quality_indicators['technical_specs']:
            missing_sections.append("Especificações Técnicas")
        if not quality_indicators['user_stories']:
            missing_sections.append("User Stories")
        if not quality_indicators['acceptance_criteria']:
            weaknesses.append("Faltam critérios de aceitação")
        if not quality_indicators['non_functional']:
            missing_sections.append("Requisitos Não-Funcionais")
        
        # Sugestões
        suggestions = []
        if score < 5:
            suggestions.extend([
                "Adicionar mais detalhes sobre cada funcionalidade",
                "Incluir user stories com personas definidas",
                "Especificar requisitos técnicos e de performance",
                "Detalhar fluxos de usuário principais"
            ])
        elif score < 7:
            suggestions.extend([
                "Expandir critérios de aceitação",
                "Adicionar considerações de segurança",
                "Incluir métricas de sucesso"
            ])
        
        return PRDQuality(
            score=score,
            weaknesses=weaknesses,
            missing_sections=missing_sections,
            suggestions=suggestions,
            is_weak=score < 6.0
        )
    
    async def enhance_prd(self, prd_content: str) -> PRDEnhancement:
        """Melhorar PRD usando IA"""
        
        print("🔍 Analyzing PRD quality...")
        quality_before = await self.analyze_prd_quality(prd_content)
        
        if not quality_before.is_weak:
            print(f"✅ PRD quality is good ({quality_before.score:.1f}/10) - no enhancement needed")
            return PRDEnhancement(
                original_prd=prd_content,
                enhanced_prd=prd_content,
                clarification_questions=[],
                suggested_features=[],
                technology_hints=[],
                quality_before=quality_before.score,
                quality_after=quality_before.score
            )
        
        print(f"⚠️ PRD quality is low ({quality_before.score:.1f}/10) - enhancing with AI...")
        
        # Usar IA para melhorar
        if self.api_key:
            enhanced_prd = await self._enhance_with_ai(prd_content, quality_before)
            questions = await self._generate_clarification_questions(prd_content)
            features = await self._suggest_missing_features(prd_content)
            tech_hints = await self._suggest_technologies(enhanced_prd)
        else:
            print("⚠️ No AI API key found - using rule-based enhancement")
            enhanced_prd = self._enhance_with_rules(prd_content, quality_before)
            questions = self._generate_basic_questions(prd_content)
            features = self._suggest_basic_features(prd_content)
            tech_hints = self._suggest_basic_technologies(prd_content)
        
        # Analisar qualidade após melhoramento
        quality_after = await self.analyze_prd_quality(enhanced_prd)
        
        return PRDEnhancement(
            original_prd=prd_content,
            enhanced_prd=enhanced_prd,
            clarification_questions=questions,
            suggested_features=features,
            technology_hints=tech_hints,
            quality_before=quality_before.score,
            quality_after=quality_after.score
        )
    
    async def _enhance_with_ai(self, prd_content: str, quality: PRDQuality) -> str:
        """Melhorar PRD usando IA (Claude ou OpenAI)"""
        
        prompt = f"""
Você é um especialista em análise de requisitos de software. Recebeu este PRD que precisa ser melhorado:

=== PRD ORIGINAL ===
{prd_content}

=== PROBLEMAS IDENTIFICADOS ===
Fraquezas: {', '.join(quality.weaknesses)}
Seções faltando: {', '.join(quality.missing_sections)}

=== TAREFA ===
Reescreva este PRD de forma muito mais detalhada e profissional, seguindo estas diretrizes:

1. **Estrutura Padrão**: Use seções como Visão, Objetivos, Funcionalidades, Requisitos Técnicos, User Stories
2. **Detalhamento**: Expanda cada funcionalidade com sub-itens específicos
3. **User Stories**: Crie personas e histórias de usuário realistas
4. **Requisitos Técnicos**: Sugira tecnologias apropriadas baseadas no contexto
5. **Critérios de Aceitação**: Para cada funcionalidade principal
6. **Requisitos Não-Funcionais**: Performance, segurança, escalabilidade

IMPORTANTE: 
- Mantenha o escopo original, apenas detalhe melhor
- Use markdown com estrutura hierárquica
- Seja específico e técnico onde apropriado
- Inclua métricas mensuráveis quando possível

Responda APENAS com o PRD melhorado em markdown:
"""
        
        try:
            if self.use_anthropic:
                enhanced = await self._call_anthropic_api(prompt)
            else:
                enhanced = await self._call_openai_api(prompt)
            
            return enhanced
        except Exception as e:
            print(f"⚠️ AI enhancement failed: {e}")
            return self._enhance_with_rules(prd_content, quality)
    
    async def _generate_clarification_questions(self, prd_content: str) -> List[str]:
        """Gerar perguntas de clarificação com IA"""
        
        prompt = f"""
Baseado neste PRD, gere 5-8 perguntas específicas e inteligentes que um analista faria para esclarecer requisitos:

{prd_content}

As perguntas devem ser:
- Específicas ao domínio do projeto
- Técnicas quando apropriado  
- Focadas em aspectos não cobertos no PRD
- Úteis para definir escopo e arquitetura

Formato: Uma pergunta por linha, começando com "❓"

Exemplo:
❓ Qual o volume esperado de usuários simultâneos?
❓ Precisa integrar com sistemas legados existentes?
"""
        
        try:
            if self.use_anthropic:
                response = await self._call_anthropic_api(prompt)
            else:
                response = await self._call_openai_api(prompt)
            
            questions = [line.strip().replace('❓', '').strip() 
                        for line in response.split('\n') 
                        if line.strip().startswith('❓')]
            return questions[:8]  # Máximo 8 perguntas
            
        except:
            return self._generate_basic_questions(prd_content)
    
    async def _suggest_missing_features(self, prd_content: str) -> List[str]:
        """Sugerir features que podem estar faltando"""
        
        prompt = f"""
Analise este PRD e sugira 3-5 funcionalidades importantes que provavelmente estão faltando:

{prd_content}

Considere:
- Funcionalidades comuns do tipo de sistema descrito
- Aspectos de segurança e compliance
- Features de administração e configuração
- Integrações típicas
- Funcionalidades de suporte e monitoramento

Formato: Uma sugestão por linha com emoji e descrição breve

Exemplo:
🔐 Sistema de auditoria e logs de ações dos usuários
📊 Dashboard administrativo com métricas operacionais
"""
        
        try:
            if self.use_anthropic:
                response = await self._call_anthropic_api(prompt)
            else:
                response = await self._call_openai_api(prompt)
            
            features = [line.strip() for line in response.split('\n') 
                       if line.strip() and ('🔐' in line or '📊' in line or '⚙️' in line or '🔄' in line or '📱' in line)]
            return features[:5]
            
        except:
            return self._suggest_basic_features(prd_content)
    
    async def _suggest_technologies(self, prd_content: str) -> List[str]:
        """Sugerir tecnologias baseadas no PRD melhorado"""
        
        prompt = f"""
Baseado neste PRD, sugira as tecnologias mais apropriadas:

{prd_content}

Sugira:
- Framework frontend mais adequado
- Backend/API technology  
- Banco de dados apropriado
- Ferramentas de deploy/infraestrutura
- Bibliotecas/frameworks específicos

Formato: "Categoria: Tecnologia - Razão"

Exemplo:
Frontend: React + TypeScript - Aplicação complexa com estado
Backend: Node.js + Express - API REST rápida
Database: PostgreSQL - Dados relacionais com ACID
"""
        
        try:
            if self.use_anthropic:
                response = await self._call_anthropic_api(prompt)
            else:
                response = await self._call_openai_api(prompt)
            
            tech_lines = [line.strip() for line in response.split('\n') 
                         if ':' in line and '-' in line]
            return tech_lines[:6]
            
        except:
            return self._suggest_basic_technologies(prd_content)
    
    async def _call_anthropic_api(self, prompt: str) -> str:
        """Chamar API da Anthropic (Claude)"""
        
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01'
        }
        
        data = {
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 3000,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['content'][0]['text']
                else:
                    raise Exception(f"Anthropic API error: {response.status}")
    
    async def _call_openai_api(self, prompt: str) -> str:
        """Chamar API da OpenAI"""
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': 'gpt-4',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'max_tokens': 3000,
            'temperature': 0.3
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f"OpenAI API error: {response.status}")
    
    # Métodos fallback baseados em regras
    def _enhance_with_rules(self, prd_content: str, quality: PRDQuality) -> str:
        """Melhorar PRD usando regras predefinidas"""
        
        enhanced = f"""# {self._extract_project_title(prd_content)}

## 1. Visão do Projeto

{self._generate_vision_section(prd_content)}

## 2. Objetivos

{self._generate_objectives_section(prd_content)}

## 3. Funcionalidades Principais

{self._expand_features_section(prd_content)}

## 4. Requisitos Técnicos

{self._generate_technical_requirements(prd_content)}

## 5. User Stories

{self._generate_user_stories(prd_content)}

## 6. Critérios de Aceitação

{self._generate_acceptance_criteria(prd_content)}

## 7. Requisitos Não-Funcionais

{self._generate_non_functional_requirements(prd_content)}

---

*PRD melhorado automaticamente pelo WasTask PRD Enhancer*
"""
        return enhanced
    
    def _generate_basic_questions(self, prd_content: str) -> List[str]:
        """Gerar perguntas básicas baseadas em regras"""
        
        questions = [
            "Qual o número esperado de usuários concurrent?",
            "Precisa de aplicativo mobile ou apenas web?",
            "Quais integrações com sistemas externos são necessárias?",
            "Qual o orçamento disponível para desenvolvimento?",
            "Existe prazo específico para entrega?",
            "Quais são os requisitos de segurança e compliance?",
            "Precisa suportar múltiplos idiomas?"
        ]
        
        # Personalizar baseado no conteúdo
        content_lower = prd_content.lower()
        specific_questions = []
        
        if 'vendas' in content_lower or 'ecommerce' in content_lower:
            specific_questions.extend([
                "Quais métodos de pagamento devem ser suportados?",
                "Precisa integrar com ERP existente?",
                "Qual o volume esperado de transações por dia?"
            ])
        
        if 'usuario' in content_lower or 'login' in content_lower:
            specific_questions.extend([
                "Precisa de autenticação social (Google, Facebook)?",
                "Quais níveis de permissão são necessários?",
                "Precisa de recuperação de senha?"
            ])
        
        return questions + specific_questions
    
    def _suggest_basic_features(self, prd_content: str) -> List[str]:
        """Sugerir features básicas baseadas em regras"""
        
        content_lower = prd_content.lower()
        features = []
        
        # Features comuns
        if 'usuario' in content_lower:
            features.extend([
                "🔐 Sistema de recuperação de senha",
                "👤 Perfil de usuário editável",
                "🔔 Sistema de notificações"
            ])
        
        if 'admin' in content_lower:
            features.extend([
                "📊 Dashboard administrativo",
                "📋 Logs de auditoria",
                "⚙️ Configurações do sistema"
            ])
        
        if 'vendas' in content_lower or 'produto' in content_lower:
            features.extend([
                "📈 Relatórios de vendas",
                "💰 Integração com pagamentos",
                "📱 Interface mobile responsiva"
            ])
        
        return features[:5]
    
    def _suggest_basic_technologies(self, prd_content: str) -> List[str]:
        """Sugerir tecnologias básicas baseadas em regras"""
        
        content_lower = prd_content.lower()
        
        technologies = [
            "Frontend: React + TypeScript - Interface moderna e tipada",
            "Backend: Node.js + Express - API REST eficiente",
            "Database: PostgreSQL - Dados relacionais confiáveis"
        ]
        
        if 'mobile' in content_lower or 'app' in content_lower:
            technologies.append("Mobile: React Native - Aplicativo multiplataforma")
        
        if 'tempo real' in content_lower or 'chat' in content_lower:
            technologies.append("Real-time: Socket.io - Comunicação em tempo real")
        
        if 'pagamento' in content_lower:
            technologies.append("Payments: Stripe API - Processamento de pagamentos")
        
        return technologies
    
    # Métodos auxiliares para análise de qualidade
    def _has_standard_sections(self, content: str) -> bool:
        sections = ['objetivo', 'funcionalidade', 'requisito', 'feature']
        return any(section in content.lower() for section in sections)
    
    def _has_detailed_features(self, content: str) -> bool:
        # Verificar se tem ao menos 3 features descritas com mais de uma linha cada
        lines = content.split('\n')
        feature_lines = [line for line in lines if any(marker in line for marker in ['- ', '* ', '1. ', '2. '])]
        return len(feature_lines) >= 3
    
    def _has_technical_specs(self, content: str) -> bool:
        tech_words = ['api', 'database', 'frontend', 'backend', 'tecnologia', 'framework']
        return any(word in content.lower() for word in tech_words)
    
    def _has_user_stories(self, content: str) -> bool:
        story_markers = ['como um', 'as a', 'persona', 'usuário', 'user']
        return any(marker in content.lower() for marker in story_markers)
    
    def _has_acceptance_criteria(self, content: str) -> bool:
        criteria_markers = ['critério', 'acceptance', 'deve', 'quando', 'então']
        return any(marker in content.lower() for marker in criteria_markers)
    
    def _has_non_functional_requirements(self, content: str) -> bool:
        nfr_words = ['performance', 'segurança', 'escalabilidade', 'disponibilidade', 'usabilidade']
        return any(word in content.lower() for word in nfr_words)
    
    # Métodos auxiliares para geração de seções
    def _extract_project_title(self, content: str) -> str:
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#') and len(line.strip()) > 1:
                return line.replace('#', '').strip()
        return "Sistema de Software"
    
    def _generate_vision_section(self, content: str) -> str:
        return f"Desenvolver um sistema eficiente que atenda às necessidades identificadas no documento original, proporcionando uma solução robusta e escalável."
    
    def _generate_objectives_section(self, content: str) -> str:
        return """- Implementar todas as funcionalidades identificadas no escopo
- Garantir alta qualidade e performance do sistema
- Proporcionar experiência de usuário intuitiva
- Estabelecer base sólida para evoluções futuras"""
    
    def _expand_features_section(self, content: str) -> str:
        # Extrair features mencionadas e expandir
        features_found = []
        for line in content.split('\n'):
            if any(marker in line for marker in ['- ', '* ', '1. ', '2. ', '3. ']):
                feature = line.strip().lstrip('- *123456789. ')
                if len(feature) > 5:
                    features_found.append(feature)
        
        if not features_found:
            return "### Funcionalidade Principal\n- Sistema core conforme especificado no documento original"
        
        expanded = ""
        for i, feature in enumerate(features_found, 1):
            expanded += f"### {i}. {feature}\n"
            expanded += f"Implementação completa de {feature.lower()} com todas as funcionalidades necessárias.\n\n"
        
        return expanded
    
    def _generate_technical_requirements(self, content: str) -> str:
        return """- **Arquitetura**: Aplicação web moderna e responsiva
- **Performance**: Tempo de resposta < 2 segundos
- **Escalabilidade**: Suporte a crescimento de usuários
- **Segurança**: Implementação de boas práticas de segurança
- **Manutenibilidade**: Código limpo e bem documentado"""
    
    def _generate_user_stories(self, content: str) -> str:
        return """**Como um usuário do sistema**, eu quero acessar as funcionalidades principais para que eu possa realizar minhas tarefas de forma eficiente.

**Como um administrador**, eu quero gerenciar o sistema para que eu possa manter sua operação adequada.

**Como um usuário final**, eu quero uma interface intuitiva para que eu possa usar o sistema sem dificuldades."""
    
    def _generate_acceptance_criteria(self, content: str) -> str:
        return """- Todas as funcionalidades especificadas devem estar implementadas
- Sistema deve passar em todos os testes de qualidade
- Interface deve ser responsiva em diferentes dispositivos
- Performance deve atender aos requisitos especificados
- Segurança deve estar de acordo com as melhores práticas"""
    
    def _generate_non_functional_requirements(self, content: str) -> str:
        return """### Performance
- Tempo de carregamento inicial: < 3 segundos
- Tempo de resposta das operações: < 2 segundos

### Segurança
- Autenticação segura
- Proteção contra ataques comuns (XSS, CSRF, SQL Injection)
- Criptografia de dados sensíveis

### Escalabilidade
- Suporte a aumento de usuários e dados
- Arquitetura preparada para crescimento

### Usabilidade
- Interface intuitiva e responsiva
- Compatibilidade com navegadores modernos
- Acessibilidade (WCAG 2.1)"""

# Instância global
prd_enhancer = PRDEnhancer()