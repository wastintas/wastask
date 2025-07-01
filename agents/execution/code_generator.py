#!/usr/bin/env python3
"""
WasTask - Code Generation Engine
Motor para gerar código real usando documentação atualizada
"""
import os
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from rich.console import Console
from rich.panel import Panel

from wastask.mock_adk import LlmAgent
from integrations.context7_client import context7_client, StackKnowledge

console = Console()

class CodeLanguage(Enum):
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript" 
    PYTHON = "python"
    SQL = "sql"
    DOCKERFILE = "dockerfile"
    YAML = "yaml"
    JSON = "json"

@dataclass
class GeneratedFile:
    """Arquivo gerado pelo sistema"""
    path: str
    content: str
    language: CodeLanguage
    description: str
    
@dataclass
class QualityCheck:
    """Resultado de verificação de qualidade"""
    name: str
    passed: bool
    output: str
    execution_time: float

@dataclass
class CodeGenerationResult:
    """Resultado da geração de código"""
    files: List[GeneratedFile]
    quality_checks: List[QualityCheck]
    success: bool
    commit_message: str

class CodeGenerationEngine:
    """Motor de geração de código com quality gates"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.stack_knowledge: Optional[StackKnowledge] = None
        
        # Agente especializado em geração de código
        self.code_agent = LlmAgent(
            name="code_generator",
            model="claude-3-5-sonnet",
            description="Especialista em geração de código com melhores práticas"
        )
        
        # Quality checks disponíveis
        self.quality_checks = {
            "build": self._check_build,
            "lint": self._check_lint,
            "typecheck": self._check_typecheck,
            "test": self._check_test,
            "format": self._check_format
        }
    
    async def initialize_with_stack(self, technologies: List[str]):
        """Inicializar com conhecimento da stack"""
        console.print("🔍 Initializing Code Generator with stack knowledge...")
        
        self.stack_knowledge = await context7_client.build_stack_knowledge(technologies)
        console.print(f"📚 Loaded documentation for {len(technologies)} technologies")
    
    async def generate_subtask_code(self, 
                                  subtask_description: str,
                                  files_to_modify: List[str] = None,
                                  relevant_technologies: List[str] = None) -> CodeGenerationResult:
        """Gerar código para uma subtask específica"""
        
        console.print(Panel(
            f"💻 Generating code for subtask:\n{subtask_description}",
            title="Code Generation",
            border_style="blue"
        ))
        
        # 1. Preparar contexto com documentação atualizada
        context = await self._prepare_generation_context(
            subtask_description, 
            relevant_technologies or []
        )
        
        # 2. Gerar código usando IA
        generated_files = await self._generate_code_with_ai(
            subtask_description,
            context,
            files_to_modify or []
        )
        
        # 3. Aplicar mudanças no projeto
        await self._apply_code_changes(generated_files)
        
        # 4. Executar quality checks
        quality_results = await self._run_quality_checks()
        
        # 5. Gerar mensagem de commit
        commit_message = await self._generate_commit_message(
            subtask_description,
            generated_files,
            quality_results
        )
        
        success = all(check.passed for check in quality_results)
        
        return CodeGenerationResult(
            files=generated_files,
            quality_checks=quality_results,
            success=success,
            commit_message=commit_message
        )
    
    async def _prepare_generation_context(self, 
                                        subtask_description: str,
                                        relevant_technologies: List[str]) -> str:
        """Preparar contexto com documentação atualizada"""
        
        if not self.stack_knowledge:
            return f"Task: {subtask_description}\n\nNo stack documentation available."
        
        # Obter documentação relevante
        tech_context = context7_client.get_combined_context(
            self.stack_knowledge, 
            relevant_technologies
        )
        
        # Analisar projeto atual
        project_context = await self._analyze_current_project()
        
        context = f"""
# Current Task
{subtask_description}

# Technology Documentation
{tech_context}

# Current Project Context
{project_context}

# Generation Guidelines
- Follow the latest best practices from the documentation above
- Ensure code is production-ready and well-structured
- Include proper error handling and validation
- Add appropriate TypeScript types if applicable
- Follow the existing project patterns and conventions
- Ensure code is testable and maintainable
"""
        
        return context
    
    async def _generate_code_with_ai(self, 
                                   subtask_description: str,
                                   context: str,
                                   files_to_modify: List[str]) -> List[GeneratedFile]:
        """Gerar código usando IA com contexto atualizado"""
        
        prompt = f"""
{context}

Generate production-ready code for this subtask: {subtask_description}

Files to consider/modify: {files_to_modify if files_to_modify else "Create new files as needed"}

Requirements:
1. Follow the latest documentation patterns shown above
2. Generate complete, working code (not snippets)
3. Include proper imports and dependencies
4. Add error handling and validation
5. Follow TypeScript strict mode if applicable
6. Include JSDoc/comments for complex logic

Respond with a JSON structure:
{{
  "files": [
    {{
      "path": "relative/path/to/file.ts",
      "content": "complete file content here",
      "language": "typescript", 
      "description": "What this file does"
    }}
  ]
}}
"""
        
        console.print("🧠 AI generating code with updated documentation...")
        
        result = await self.code_agent.run(prompt)
        
        try:
            # Parse AI response (simplificado para demo)
            # Em produção, seria um parser mais robusto
            import json
            import re
            
            # Extrair JSON da resposta
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', result.content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Fallback: tentar parse direto
                data = json.loads(result.content)
            
            generated_files = []
            for file_data in data.get("files", []):
                generated_files.append(GeneratedFile(
                    path=file_data["path"],
                    content=file_data["content"],
                    language=CodeLanguage(file_data["language"]),
                    description=file_data["description"]
                ))
            
            console.print(f"✅ Generated {len(generated_files)} files")
            return generated_files
            
        except Exception as e:
            console.print(f"❌ Error parsing AI response: {e}")
            
            # Fallback: gerar arquivo básico
            return [GeneratedFile(
                path="generated_placeholder.ts",
                content=f"// Generated for: {subtask_description}\n// TODO: Implement functionality\n",
                language=CodeLanguage.TYPESCRIPT,
                description="Placeholder file due to parsing error"
            )]
    
    async def _apply_code_changes(self, generated_files: List[GeneratedFile]):
        """Aplicar mudanças de código no projeto"""
        
        for file in generated_files:
            file_path = self.project_root / file.path
            
            # Criar diretórios se necessário
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Escrever arquivo
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
            
            console.print(f"📝 {file.path} - {file.description}")
    
    async def _run_quality_checks(self) -> List[QualityCheck]:
        """Executar todas as verificações de qualidade"""
        
        console.print("🧪 Running quality checks...")
        
        results = []
        
        # Executar cada check
        for check_name, check_func in self.quality_checks.items():
            console.print(f"  🔍 {check_name}...")
            result = await check_func()
            results.append(result)
            
            if result.passed:
                console.print(f"  ✅ {check_name} - PASSED")
            else:
                console.print(f"  ❌ {check_name} - FAILED")
                if result.output:
                    console.print(f"       {result.output}")
        
        return results
    
    async def _check_build(self) -> QualityCheck:
        """Verificar se o build passa"""
        import time
        start_time = time.time()
        
        try:
            # Detectar tipo de projeto e comando de build
            if (self.project_root / "package.json").exists():
                cmd = ["npm", "run", "build"]
            elif (self.project_root / "pyproject.toml").exists():
                cmd = ["python", "-m", "build"]
            else:
                return QualityCheck("build", True, "No build command detected", 0)
            
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos max
            )
            
            execution_time = time.time() - start_time
            
            return QualityCheck(
                "build",
                result.returncode == 0,
                result.stderr if result.returncode != 0 else "Build successful",
                execution_time
            )
            
        except subprocess.TimeoutExpired:
            return QualityCheck("build", False, "Build timeout", 300)
        except Exception as e:
            return QualityCheck("build", False, f"Build error: {e}", time.time() - start_time)
    
    async def _check_lint(self) -> QualityCheck:
        """Verificar linting"""
        import time
        start_time = time.time()
        
        try:
            if (self.project_root / "package.json").exists():
                # Tentar ESLint
                result = subprocess.run(
                    ["npm", "run", "lint"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                return QualityCheck("lint", True, "No linter configured", 0)
            
            execution_time = time.time() - start_time
            
            return QualityCheck(
                "lint",
                result.returncode == 0,
                result.stdout + result.stderr if result.returncode != 0 else "Lint clean",
                execution_time
            )
            
        except Exception as e:
            return QualityCheck("lint", False, f"Lint error: {e}", time.time() - start_time)
    
    async def _check_typecheck(self) -> QualityCheck:
        """Verificar TypeScript"""
        import time
        start_time = time.time()
        
        try:
            if (self.project_root / "tsconfig.json").exists():
                result = subprocess.run(
                    ["npx", "tsc", "--noEmit"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
            else:
                return QualityCheck("typecheck", True, "No TypeScript config", 0)
            
            execution_time = time.time() - start_time
            
            return QualityCheck(
                "typecheck",
                result.returncode == 0,
                result.stdout + result.stderr if result.returncode != 0 else "Types valid",
                execution_time
            )
            
        except Exception as e:
            return QualityCheck("typecheck", False, f"TypeCheck error: {e}", time.time() - start_time)
    
    async def _check_test(self) -> QualityCheck:
        """Executar testes"""
        import time
        start_time = time.time()
        
        try:
            if (self.project_root / "package.json").exists():
                result = subprocess.run(
                    ["npm", "test", "--", "--passWithNoTests"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
            else:
                return QualityCheck("test", True, "No tests configured", 0)
            
            execution_time = time.time() - start_time
            
            return QualityCheck(
                "test",
                result.returncode == 0,
                result.stdout + result.stderr if result.returncode != 0 else "All tests passed",
                execution_time
            )
            
        except Exception as e:
            return QualityCheck("test", False, f"Test error: {e}", time.time() - start_time)
    
    async def _check_format(self) -> QualityCheck:
        """Verificar formatação"""
        import time
        start_time = time.time()
        
        try:
            if (self.project_root / "package.json").exists():
                result = subprocess.run(
                    ["npx", "prettier", "--check", "."],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                return QualityCheck("format", True, "No formatter configured", 0)
            
            execution_time = time.time() - start_time
            
            return QualityCheck(
                "format",
                result.returncode == 0,
                result.stdout + result.stderr if result.returncode != 0 else "Format clean",
                execution_time
            )
            
        except Exception as e:
            return QualityCheck("format", False, f"Format error: {e}", time.time() - start_time)
    
    async def _analyze_current_project(self) -> str:
        """Analisar estado atual do projeto"""
        
        analysis = []
        
        # Estrutura de pastas
        if self.project_root.exists():
            analysis.append("## Project Structure")
            for item in self.project_root.iterdir():
                if not item.name.startswith('.'):
                    analysis.append(f"- {item.name}")
        
        # Configurações detectadas
        configs = []
        if (self.project_root / "package.json").exists():
            configs.append("Node.js/NPM project")
        if (self.project_root / "tsconfig.json").exists():
            configs.append("TypeScript configured")
        if (self.project_root / "Dockerfile").exists():
            configs.append("Docker ready")
        
        if configs:
            analysis.append("\n## Detected Configuration")
            analysis.extend([f"- {config}" for config in configs])
        
        return "\n".join(analysis)
    
    async def _generate_commit_message(self, 
                                     subtask_description: str,
                                     files: List[GeneratedFile],
                                     quality_results: List[QualityCheck]) -> str:
        """Gerar mensagem de commit inteligente"""
        
        # Tipo de commit baseado na descrição
        commit_type = "feat"
        if "fix" in subtask_description.lower() or "bug" in subtask_description.lower():
            commit_type = "fix"
        elif "test" in subtask_description.lower():
            commit_type = "test"
        elif "refactor" in subtask_description.lower():
            commit_type = "refactor"
        elif "docs" in subtask_description.lower():
            commit_type = "docs"
        
        # Resumo do que foi feito
        file_count = len(files)
        file_types = list(set(f.language.value for f in files))
        
        # Status dos quality checks
        passed_checks = [q.name for q in quality_results if q.passed]
        failed_checks = [q.name for q in quality_results if not q.passed]
        
        # Gerar mensagem estruturada
        title = f"{commit_type}: {subtask_description[:50]}"
        if len(subtask_description) > 50:
            title += "..."
        
        body_parts = [
            f"- Generated {file_count} files ({', '.join(file_types)})",
            f"- Files: {', '.join([f.path for f in files[:3]])}{'...' if len(files) > 3 else ''}",
        ]
        
        if passed_checks:
            body_parts.append(f"✅ Quality checks passed: {', '.join(passed_checks)}")
        
        if failed_checks:
            body_parts.append(f"❌ Quality checks failed: {', '.join(failed_checks)}")
        
        body_parts.append("🤖 Generated with WasTask AI")
        
        return f"{title}\n\n" + "\n".join(body_parts)

# Instância global
code_generator = CodeGenerationEngine()