#!/usr/bin/env python3
"""
Setup PostgreSQL para WasTask
Script para configurar PostgreSQL com Docker
"""
import subprocess
import time
import sys
from rich.console import Console

console = Console()

def executar_comando(cmd, descricao):
    """Executar comando e mostrar resultado"""
    console.print(f"🔧 {descricao}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"✅ {descricao} - Sucesso!")
            return True, result.stdout
        else:
            console.print(f"❌ {descricao} - Erro: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        console.print(f"❌ {descricao} - Exceção: {e}")
        return False, str(e)

def main():
    console.print("🐘 [bold blue]Configurando PostgreSQL para WasTask[/bold blue]")
    
    # 1. Parar container existente se houver
    console.print("\n📦 Gerenciando containers...")
    executar_comando("docker stop wastask-postgres 2>/dev/null || true", "Parando container existente")
    executar_comando("docker rm wastask-postgres 2>/dev/null || true", "Removendo container existente")
    
    # 2. Iniciar PostgreSQL
    cmd_postgres = """
    docker run -d \\
      --name wastask-postgres \\
      -e POSTGRES_DB=wastask \\
      -e POSTGRES_USER=wastask \\
      -e POSTGRES_PASSWORD=password \\
      -p 5433:5432 \\
      postgres:15-alpine
    """
    
    sucesso, output = executar_comando(cmd_postgres, "Iniciando PostgreSQL")
    if not sucesso:
        sys.exit(1)
    
    # 3. Aguardar PostgreSQL ficar pronto
    console.print("\n⏳ Aguardando PostgreSQL ficar pronto...")
    for i in range(30):  # 30 tentativas
        sucesso, _ = executar_comando(
            "docker exec wastask-postgres pg_isready -U wastask -d wastask",
            f"Verificando PostgreSQL (tentativa {i+1})"
        )
        if sucesso:
            console.print("✅ PostgreSQL está pronto!")
            break
        time.sleep(2)
    else:
        console.print("❌ Timeout aguardando PostgreSQL")
        sys.exit(1)
    
    # 4. Criar estrutura inicial
    console.print("\n🏗️ Configurando banco...")
    
    sql_commands = [
        "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";",
        "CREATE SCHEMA IF NOT EXISTS public;",
        "GRANT ALL ON SCHEMA public TO wastask;",
    ]
    
    for sql in sql_commands:
        executar_comando(
            f"docker exec wastask-postgres psql -U wastask -d wastask -c \"{sql}\"",
            f"Executando SQL"
        )
    
    # 5. Verificar conexão
    console.print("\n🔍 Verificando configuração...")
    sucesso, output = executar_comando(
        "docker exec wastask-postgres psql -U wastask -d wastask -c \"SELECT version();\"",
        "Testando conexão"
    )
    
    if sucesso:
        console.print("\n🎉 [bold green]PostgreSQL configurado com sucesso![/bold green]")
        console.print("\n📋 [bold]Informações de conexão:[/bold]")
        console.print("  Host: 127.0.0.1")
        console.print("  Porta: 5433 (Docker)")
        console.print("  Database: wastask")
        console.print("  Usuário: wastask")
        console.print("  Senha: password")
        console.print("  URL: postgresql://wastask:password@127.0.0.1:5433/wastask")
        
        console.print("\n💻 [bold]Comandos úteis:[/bold]")
        console.print("  docker ps                                    # Ver containers rodando")
        console.print("  docker logs wastask-postgres                # Ver logs")
        console.print("  docker exec -it wastask-postgres psql -U wastask -d wastask  # Conectar ao banco")
        console.print("  uv run python demo_postgres.py             # Executar demo")
        
        console.print("\n🚀 [bold cyan]Agora você pode executar:[/bold cyan]")
        console.print("  uv run python demo_postgres.py")
    else:
        console.print("❌ Falha na configuração")
        sys.exit(1)

if __name__ == '__main__':
    main()