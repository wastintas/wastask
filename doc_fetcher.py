#!/usr/bin/env python3
"""
Documentation Fetcher para WasTask
Busca informações atualizadas das documentações oficiais
"""
import asyncio
import aiohttp
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import time

@dataclass
class TechDoc:
    """Documentação de uma tecnologia"""
    name: str
    version: str
    install_commands: List[str]
    setup_commands: List[str]
    config_files: Dict[str, str]
    scripts: Dict[str, str]
    dependencies: List[str]
    dev_dependencies: List[str]
    environment_setup: List[str]
    documentation_url: str
    last_updated: str

class DocumentationFetcher:
    """Buscador de documentações oficiais"""
    
    def __init__(self):
        self.cache_dir = Path("./doc_cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_duration = 24 * 60 * 60  # 24 horas em segundos
        
        # URLs das documentações oficiais
        self.doc_sources = {
            "react-router-v7": {
                "urls": [
                    "https://reactrouter.com/start/framework/installation",
                    "https://reactrouter.com/start/tutorial"
                ],
                "fallback": self._get_react_router_v7_fallback()
            },
            "shadcn-ui": {
                "urls": [
                    "https://ui.shadcn.com/docs/installation",
                    "https://ui.shadcn.com/docs/installation/next"
                ],
                "fallback": self._get_shadcn_fallback()
            },
            "zod": {
                "urls": [
                    "https://zod.dev/",
                    "https://github.com/colinhacks/zod#installation"
                ],
                "fallback": self._get_zod_fallback()
            },
            "drizzle-orm": {
                "urls": [
                    "https://orm.drizzle.team/docs/get-started-postgresql",
                    "https://orm.drizzle.team/docs/installation-and-db-connection/postgresql"
                ],
                "fallback": self._get_drizzle_fallback()
            },
            "postgresql": {
                "urls": [
                    "https://www.postgresql.org/docs/current/installation.html"
                ],
                "fallback": self._get_postgresql_fallback()
            },
            "typescript": {
                "urls": [
                    "https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html"
                ],
                "fallback": self._get_typescript_fallback()
            }
        }
    
    async def fetch_documentation(self, tech_name: str) -> TechDoc:
        """Buscar documentação de uma tecnologia"""
        
        # Verificar cache primeiro
        cached_doc = self._get_cached_doc(tech_name)
        if cached_doc:
            return cached_doc
        
        # Buscar online
        try:
            doc = await self._fetch_online_doc(tech_name)
            if doc:
                self._cache_doc(tech_name, doc)
                return doc
        except Exception as e:
            print(f"⚠️ Error fetching {tech_name} docs online: {e}")
        
        # Fallback para documentação local
        return self._get_fallback_doc(tech_name)
    
    def _get_cached_doc(self, tech_name: str) -> Optional[TechDoc]:
        """Verificar se temos doc em cache válida"""
        cache_file = self.cache_dir / f"{tech_name}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            # Verificar se cache não expirou
            cache_time = data.get('cached_at', 0)
            if time.time() - cache_time > self.cache_duration:
                return None
            
            return TechDoc(**data['doc'])
        except:
            return None
    
    def _cache_doc(self, tech_name: str, doc: TechDoc):
        """Salvar doc no cache"""
        cache_file = self.cache_dir / f"{tech_name}.json"
        
        data = {
            'cached_at': time.time(),
            'doc': {
                'name': doc.name,
                'version': doc.version,
                'install_commands': doc.install_commands,
                'setup_commands': doc.setup_commands,
                'config_files': doc.config_files,
                'scripts': doc.scripts,
                'dependencies': doc.dependencies,
                'dev_dependencies': doc.dev_dependencies,
                'environment_setup': doc.environment_setup,
                'documentation_url': doc.documentation_url,
                'last_updated': doc.last_updated
            }
        }
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    async def _fetch_online_doc(self, tech_name: str) -> Optional[TechDoc]:
        """Buscar documentação online"""
        if tech_name not in self.doc_sources:
            return None
        
        source = self.doc_sources[tech_name]
        
        async with aiohttp.ClientSession() as session:
            for url in source["urls"]:
                try:
                    async with session.get(url, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            return self._parse_documentation(tech_name, content, url)
                except:
                    continue
        
        return None
    
    def _parse_documentation(self, tech_name: str, content: str, url: str) -> TechDoc:
        """Parse da documentação HTML/Markdown"""
        
        # Por enquanto, usar fallbacks inteligentes baseados no tech_name
        # TODO: Implementar parsing real do HTML/Markdown
        
        fallback_doc = self._get_fallback_doc(tech_name)
        fallback_doc.documentation_url = url
        fallback_doc.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
        
        return fallback_doc
    
    def _get_fallback_doc(self, tech_name: str) -> TechDoc:
        """Obter documentação fallback"""
        if tech_name in self.doc_sources:
            return self.doc_sources[tech_name]["fallback"]
        
        # Fallback genérico
        return TechDoc(
            name=tech_name,
            version="latest",
            install_commands=[f"npm install {tech_name}"],
            setup_commands=[],
            config_files={},
            scripts={},
            dependencies=[tech_name],
            dev_dependencies=[],
            environment_setup=[],
            documentation_url="",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_react_router_v7_fallback(self) -> TechDoc:
        """Documentação fallback para React Router v7"""
        return TechDoc(
            name="React Router v7",
            version="7.0.0",
            install_commands=[
                "npx create-react-router@latest my-app"
            ],
            setup_commands=[
                "cd my-app",
                "npm install"
            ],
            config_files={
                "vite.config.ts": '''import { defineConfig } from "vite";
import { reactRouter } from "@react-router/dev/vite";

export default defineConfig({
  plugins: [reactRouter()],
});''',
                "app/root.tsx": '''import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";

export default function App() {
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <Outlet />
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}'''
            },
            scripts={
                "dev": "react-router dev",
                "build": "react-router build",
                "start": "react-router-serve ./build/server/index.js",
                "typecheck": "tsc"
            },
            dependencies=[
                "react",
                "react-dom", 
                "@react-router/node",
                "@react-router/serve"
            ],
            dev_dependencies=[
                "@react-router/dev",
                "@types/react",
                "@types/react-dom",
                "typescript",
                "vite"
            ],
            environment_setup=[],
            documentation_url="https://reactrouter.com/start/framework/installation",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_shadcn_fallback(self) -> TechDoc:
        """Documentação fallback para Shadcn/ui"""
        return TechDoc(
            name="Shadcn/ui",
            version="latest",
            install_commands=[
                "npx shadcn@latest init"
            ],
            setup_commands=[
                "npx shadcn@latest add button",
                "npx shadcn@latest add input",
                "npx shadcn@latest add card"
            ],
            config_files={
                "components.json": '''{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": false,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "~/components",
    "utils": "~/lib/utils"
  }
}''',
                "tailwind.config.js": '''module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [require("tailwindcss-animate")],
}'''
            },
            scripts={},
            dependencies=[
                "class-variance-authority",
                "clsx", 
                "tailwind-merge",
                "@radix-ui/react-slot"
            ],
            dev_dependencies=[
                "tailwindcss",
                "tailwindcss-animate",
                "autoprefixer",
                "postcss"
            ],
            environment_setup=[],
            documentation_url="https://ui.shadcn.com/docs/installation",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_zod_fallback(self) -> TechDoc:
        """Documentação fallback para Zod"""
        return TechDoc(
            name="Zod",
            version="latest",
            install_commands=[],
            setup_commands=[],
            config_files={
                "lib/schemas.ts": '''import { z } from "zod";

export const userSchema = z.object({
  id: z.string(),
  email: z.string().email(),
  name: z.string().min(1),
});

export type User = z.infer<typeof userSchema>;'''
            },
            scripts={},
            dependencies=["zod"],
            dev_dependencies=[],
            environment_setup=[],
            documentation_url="https://zod.dev/",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_drizzle_fallback(self) -> TechDoc:
        """Documentação fallback para Drizzle ORM"""
        return TechDoc(
            name="Drizzle ORM",
            version="latest",
            install_commands=[],
            setup_commands=[],
            config_files={
                "drizzle.config.ts": '''import { defineConfig } from "drizzle-kit";

export default defineConfig({
  dialect: "postgresql",
  schema: "./app/db/schema.ts",
  out: "./drizzle",
  dbCredentials: {
    url: process.env.DATABASE_URL!,
  },
});''',
                "app/db/schema.ts": '''import { pgTable, text, timestamp, uuid } from "drizzle-orm/pg-core";

export const users = pgTable("users", {
  id: uuid("id").defaultRandom().primaryKey(),
  email: text("email").notNull().unique(),
  name: text("name").notNull(),
  createdAt: timestamp("created_at").defaultNow(),
});''',
                "app/db/index.ts": '''import { drizzle } from "drizzle-orm/postgres-js";
import postgres from "postgres";
import * as schema from "./schema";

const client = postgres(process.env.DATABASE_URL!);
export const db = drizzle(client, { schema });'''
            },
            scripts={
                "db:generate": "drizzle-kit generate",
                "db:migrate": "drizzle-kit migrate", 
                "db:studio": "drizzle-kit studio"
            },
            dependencies=[
                "drizzle-orm",
                "postgres"
            ],
            dev_dependencies=[
                "drizzle-kit",
                "@types/pg"
            ],
            environment_setup=[
                "# Create .env file with:",
                "DATABASE_URL=postgresql://user:password@localhost:5432/dbname"
            ],
            documentation_url="https://orm.drizzle.team/docs/get-started-postgresql",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_postgresql_fallback(self) -> TechDoc:
        """Documentação fallback para PostgreSQL"""
        return TechDoc(
            name="PostgreSQL",
            version="16",
            install_commands=[],
            setup_commands=[],
            config_files={},
            scripts={},
            dependencies=[],
            dev_dependencies=[],
            environment_setup=[
                "# Using Docker (recommended):",
                "docker run -d --name postgres \\",
                "  -e POSTGRES_USER=myuser \\", 
                "  -e POSTGRES_PASSWORD=mypassword \\",
                "  -e POSTGRES_DB=mydb \\",
                "  -p 5432:5432 \\",
                "  postgres:16-alpine",
                "",
                "# Alternative: Local installation",
                "# macOS: brew install postgresql@16",
                "# Ubuntu: sudo apt install postgresql-16"
            ],
            documentation_url="https://www.postgresql.org/docs/current/",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def _get_typescript_fallback(self) -> TechDoc:
        """Documentação fallback para TypeScript"""
        return TechDoc(
            name="TypeScript",
            version="5.0+",
            install_commands=[],
            setup_commands=[],
            config_files={
                "tsconfig.json": '''{
  "include": ["**/*.ts", "**/*.tsx"],
  "compilerOptions": {
    "lib": ["DOM", "DOM.Iterable", "ES6"],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  }
}'''
            },
            scripts={
                "typecheck": "tsc --noEmit"
            },
            dependencies=[],
            dev_dependencies=["typescript", "@types/react", "@types/react-dom"],
            environment_setup=[],
            documentation_url="https://www.typescriptlang.org/docs/",
            last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
        )

# Instância global
doc_fetcher = DocumentationFetcher()

async def fetch_tech_documentation(technologies: List[Dict[str, Any]]) -> Dict[str, TechDoc]:
    """Buscar documentação para lista de tecnologias"""
    docs = {}
    
    for tech in technologies:
        tech_key = tech["technology"].lower().replace(" ", "-").replace("/", "-")
        
        print(f"📚 Fetching documentation for {tech['technology']}...")
        doc = await doc_fetcher.fetch_documentation(tech_key)
        docs[tech_key] = doc
    
    return docs