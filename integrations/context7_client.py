#!/usr/bin/env python3
"""
WasTask - Context7 Integration Client
Cliente para buscar documentação sempre atualizada das tecnologias
"""
import asyncio
import aiohttp
import hashlib
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

console = Console()

@dataclass
class TechnologyDoc:
    """Documentação de uma tecnologia"""
    name: str
    version: str
    content: str
    last_updated: datetime
    hash: str
    source_url: str
    
@dataclass
class StackKnowledge:
    """Base de conhecimento da stack tecnológica"""
    technologies: Dict[str, TechnologyDoc]
    last_refresh: datetime
    
class Context7Client:
    """Cliente para integração com Context7"""
    
    def __init__(self, cache_dir: str = ".wastask/context7_cache"):
        self.base_url = os.getenv("CONTEXT7_API_URL", "https://api.context7.com/v1")
        self.api_key = os.getenv("CONTEXT7_API_KEY")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache em memória para sessão atual
        self.memory_cache: Dict[str, TechnologyDoc] = {}
        
    async def fetch_technology_docs(self, tech_name: str, version: str = "latest") -> Optional[TechnologyDoc]:
        """Buscar documentação atualizada de uma tecnologia"""
        
        cache_key = f"{tech_name}@{version}"
        
        # 1. Verificar cache em memória
        if cache_key in self.memory_cache:
            doc = self.memory_cache[cache_key]
            if self._is_cache_valid(doc):
                console.print(f"📚 {tech_name}@{version} - Using memory cache")
                return doc
        
        # 2. Verificar cache em disco
        cached_doc = await self._load_from_disk_cache(cache_key)
        if cached_doc and self._is_cache_valid(cached_doc):
            self.memory_cache[cache_key] = cached_doc
            console.print(f"📚 {tech_name}@{version} - Using disk cache")
            return cached_doc
        
        # 3. Buscar da API Context7
        try:
            doc = await self._fetch_from_context7(tech_name, version)
            if doc:
                # Salvar nos caches
                await self._save_to_disk_cache(cache_key, doc)
                self.memory_cache[cache_key] = doc
                console.print(f"📚 {tech_name}@{version} - Fetched from Context7 ✅")
                return doc
        except Exception as e:
            console.print(f"⚠️ Error fetching {tech_name}@{version}: {e}")
        
        # 4. Fallback para documentação local/mock
        return await self._get_fallback_docs(tech_name, version)
    
    async def _fetch_from_context7(self, tech_name: str, version: str) -> Optional[TechnologyDoc]:
        """Buscar documentação da API Context7"""
        
        if not self.api_key:
            console.print("⚠️ CONTEXT7_API_KEY not set, using fallback docs")
            return None
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}/docs/{tech_name}"
        params = {"version": version}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return TechnologyDoc(
                        name=tech_name,
                        version=data.get("version", version),
                        content=data.get("content", ""),
                        last_updated=datetime.fromisoformat(data.get("last_updated")),
                        hash=self._generate_hash(data.get("content", "")),
                        source_url=data.get("source_url", "")
                    )
                else:
                    console.print(f"❌ Context7 API error: {response.status}")
                    return None
    
    async def _get_fallback_docs(self, tech_name: str, version: str) -> TechnologyDoc:
        """Documentação fallback quando Context7 não está disponível"""
        
        fallback_docs = {
            "react": """
# React Documentation (Fallback)

## React 18.3.0 Best Practices

### Project Structure
```
src/
├── components/     # Reusable components
├── pages/         # Page components
├── hooks/         # Custom hooks
├── utils/         # Utility functions
├── types/         # TypeScript types
└── styles/        # Global styles
```

### Key Features
- React 18 Concurrent Features
- Automatic Batching
- Suspense for Data Fetching
- React Server Components (experimental)

### Best Practices
- Use functional components with hooks
- Implement proper error boundaries
- Optimize with React.memo for expensive components
- Use React.lazy for code splitting
""",
            
            "typescript": """
# TypeScript Documentation (Fallback)

## TypeScript 5.6.0 Configuration

### tsconfig.json
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "module": "ESNext",
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "declaration": true,
    "outDir": "./dist"
  }
}
```

### Key Features
- Improved type inference
- Better error messages
- Enhanced performance
- New utility types
""",
            
            "nodejs": """
# Node.js Documentation (Fallback)

## Node.js 20 LTS Best Practices

### Project Structure
```
src/
├── controllers/   # Route handlers
├── middleware/    # Express middleware
├── models/        # Data models
├── routes/        # Route definitions
├── services/      # Business logic
└── utils/         # Utilities
```

### Key Features
- ES Modules support
- Built-in test runner
- Improved performance
- Better security defaults
""",
            
            "postgresql": """
# PostgreSQL Documentation (Fallback)

## PostgreSQL 16 Best Practices

### Schema Design
- Use appropriate data types
- Implement proper indexing strategy
- Use foreign keys for referential integrity
- Consider partitioning for large tables

### Performance Tips
- Use EXPLAIN ANALYZE for query optimization
- Implement connection pooling
- Regular VACUUM and ANALYZE
- Monitor query performance
""",
            
            "docker": """
# Docker Documentation (Fallback)

## Docker Best Practices

### Multi-stage Builds
```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "start"]
```

### Optimization
- Use alpine images when possible
- Minimize layers
- Use .dockerignore
- Don't run as root
"""
        }
        
        content = fallback_docs.get(tech_name.lower(), f"# {tech_name} Documentation\n\nNo specific documentation available.")
        
        return TechnologyDoc(
            name=tech_name,
            version=version,
            content=content,
            last_updated=datetime.now(),
            hash=self._generate_hash(content),
            source_url="fallback://local"
        )
    
    async def build_stack_knowledge(self, technologies: List[str]) -> StackKnowledge:
        """Construir base de conhecimento para uma stack"""
        
        console.print(f"🔍 Building knowledge base for {len(technologies)} technologies...")
        
        knowledge = {}
        
        # Buscar docs de todas as tecnologias em paralelo
        tasks = [
            self.fetch_technology_docs(tech) 
            for tech in technologies
        ]
        
        docs = await asyncio.gather(*tasks, return_exceptions=True)
        
        for tech, doc in zip(technologies, docs):
            if isinstance(doc, TechnologyDoc):
                knowledge[tech] = doc
                console.print(f"  ✅ {tech} - Documentation loaded")
            else:
                console.print(f"  ❌ {tech} - Failed to load: {doc}")
        
        stack_knowledge = StackKnowledge(
            technologies=knowledge,
            last_refresh=datetime.now()
        )
        
        console.print(f"📚 Knowledge base built with {len(knowledge)} technologies")
        return stack_knowledge
    
    async def refresh_stack_knowledge(self, stack: StackKnowledge, max_age_hours: int = 24) -> StackKnowledge:
        """Atualizar conhecimento se necessário"""
        
        if datetime.now() - stack.last_refresh < timedelta(hours=max_age_hours):
            console.print("📚 Stack knowledge is still fresh")
            return stack
        
        console.print("🔄 Refreshing stack knowledge...")
        
        technologies = list(stack.technologies.keys())
        return await self.build_stack_knowledge(technologies)
    
    def get_technology_context(self, stack: StackKnowledge, tech_name: str) -> str:
        """Obter contexto específico de uma tecnologia"""
        
        if tech_name in stack.technologies:
            doc = stack.technologies[tech_name]
            return f"""
# {doc.name} v{doc.version} Documentation

Last Updated: {doc.last_updated.strftime("%Y-%m-%d %H:%M")}
Source: {doc.source_url}

{doc.content}
"""
        else:
            return f"# {tech_name}\n\nNo documentation available for {tech_name}"
    
    def get_combined_context(self, stack: StackKnowledge, relevant_techs: List[str] = None) -> str:
        """Obter contexto combinado de múltiplas tecnologias"""
        
        if relevant_techs is None:
            relevant_techs = list(stack.technologies.keys())
        
        contexts = []
        for tech in relevant_techs:
            if tech in stack.technologies:
                contexts.append(self.get_technology_context(stack, tech))
        
        return "\n\n---\n\n".join(contexts)
    
    def _is_cache_valid(self, doc: TechnologyDoc, max_age_hours: int = 24) -> bool:
        """Verificar se cache ainda é válido"""
        return datetime.now() - doc.last_updated < timedelta(hours=max_age_hours)
    
    def _generate_hash(self, content: str) -> str:
        """Gerar hash do conteúdo"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def _load_from_disk_cache(self, cache_key: str) -> Optional[TechnologyDoc]:
        """Carregar do cache em disco"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                
                return TechnologyDoc(
                    name=data["name"],
                    version=data["version"],
                    content=data["content"],
                    last_updated=datetime.fromisoformat(data["last_updated"]),
                    hash=data["hash"],
                    source_url=data["source_url"]
                )
            except Exception as e:
                console.print(f"⚠️ Error loading cache for {cache_key}: {e}")
        
        return None
    
    async def _save_to_disk_cache(self, cache_key: str, doc: TechnologyDoc):
        """Salvar no cache em disco"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            data = {
                "name": doc.name,
                "version": doc.version,
                "content": doc.content,
                "last_updated": doc.last_updated.isoformat(),
                "hash": doc.hash,
                "source_url": doc.source_url
            }
            
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            console.print(f"⚠️ Error saving cache for {cache_key}: {e}")

# Instância global
context7_client = Context7Client()