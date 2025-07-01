#!/usr/bin/env python3
"""
Demo do modo interativo do WasTask
Mostra como o sistema faz perguntas inteligentes
"""

def demo_interactive_questions():
    """Demonstrar as perguntas que o WasTask faria"""
    
    print("🚀 WasTask - Demo Modo Interativo")
    print("=" * 50)
    print()
    
    print("📄 Analisando PRD do Bling Integration...")
    print("   • Detectadas tecnologias: React Router v7, Node.js, Shadcn/ui, Zod, Drizzle")
    print()
    
    # Pergunta 1: Conflito Full-stack vs Backend
    print("❓ Detectamos React Router v7 (full-stack) + Node.js backend. Como prefere?")
    print("   1. Apenas React Router v7 (full-stack completo)")
    print("   2. React Router v7 + API backend separada") 
    print("   3. Apenas frontend React + API Node.js separada")
    print()
    print("👤 Usuário escolhe: 1 (React Router v7 full-stack)")
    print("✅ Removendo Node.js backend separado...")
    print()
    
    # Pergunta 2: Gerenciador de pacotes
    print("❓ Qual gerenciador de pacotes prefere?")
    print("   1. pnpm (recomendado)")
    print("   2. npm")
    print("   3. yarn") 
    print("   4. bun")
    print()
    print("👤 Usuário escolhe: 1 (pnpm)")
    print("✅ Configurando comandos para pnpm...")
    print()
    
    # Resultado
    print("🚀 Comandos de Setup Gerados:")
    print()
    print("📦 Project Setup:")
    print("    npx create-react-router@latest bling-connect")
    print("    cd bling-connect")
    print("    npx shadcn-ui@latest init")
    print()
    print("📥 Install Dependencies:")
    print("    pnpm add @radix-ui/react-icons zod drizzle-orm drizzle-kit pg")
    print("    pnpm add -D @types/pg drizzle-kit")
    print()
    print("🐳 Environment Setup:")
    print("    docker run -d --name postgres \\")
    print("      -e POSTGRES_PASSWORD=password \\")
    print("      -p 5432:5432 postgres:16")
    print()
    print("📝 Package.json Scripts:")
    print("    {")
    print('      "dev": "remix vite:dev",')
    print('      "build": "remix vite:build",')
    print('      "db:generate": "drizzle-kit generate",')
    print('      "db:migrate": "drizzle-kit migrate"')
    print("    }")
    print()
    
    # Stack final
    print("🛠️ Stack Final (após clarificações):")
    print("   🟢 React Router v7 (full-stack)")
    print("   🟢 Shadcn/ui (UI components)")
    print("   🟢 Zod (validation)")
    print("   🟢 Drizzle ORM (database)")
    print("   🟢 PostgreSQL (database)")
    print("   🟢 TypeScript (language)")
    print("   ❌ Node.js backend (removido - usando full-stack)")
    print()
    
    print("✅ Pronto para desenvolvimento!")
    print()
    print("💡 O que o WasTask fez:")
    print("   • Detectou conflito entre full-stack e backend")
    print("   • Perguntou qual abordagem preferir")
    print("   • Removeu tecnologias conflitantes")
    print("   • Gerou comandos específicos para a stack escolhida")
    print("   • Criou scripts otimizados para as tecnologias")

if __name__ == "__main__":
    demo_interactive_questions()