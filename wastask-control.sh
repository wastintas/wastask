#!/bin/bash

# WasTask Control Script
# Controla PostgreSQL e WasTask de forma simples

POSTGRES_CONTAINER="postgres-wastask"
POSTGRES_DATA_VOLUME="wastask-data"

show_help() {
    echo "🚀 WasTask Control Panel"
    echo ""
    echo "Comandos:"
    echo "  ./wastask-control.sh start    - Iniciar PostgreSQL"
    echo "  ./wastask-control.sh stop     - Parar PostgreSQL"
    echo "  ./wastask-control.sh status   - Ver status"
    echo "  ./wastask-control.sh restart  - Reiniciar PostgreSQL"
    echo "  ./wastask-control.sh clean    - Parar e limpar tudo"
    echo "  ./wastask-control.sh help     - Mostrar esta ajuda"
    echo ""
    echo "Após 'start', use comandos do WasTask normalmente:"
    echo "  uv run python wastask.py db list"
    echo "  uv run python wastask.py prd analyze docs/exemplo.md"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker não está instalado"
        exit 1
    fi
}

start_postgres() {
    echo "🚀 Iniciando PostgreSQL para WasTask..."
    
    # Verificar se já está rodando
    if docker ps --format "table {{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        echo "✅ PostgreSQL já está rodando"
        return
    fi
    
    # Verificar se container existe mas está parado
    if docker ps -a --format "table {{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        echo "🔄 Reiniciando container existente..."
        docker start $POSTGRES_CONTAINER
    else
        echo "📦 Criando novo container PostgreSQL..."
        docker run -d \
            --name $POSTGRES_CONTAINER \
            -e POSTGRES_USER=wastask \
            -e POSTGRES_PASSWORD=wastask123 \
            -e POSTGRES_DB=wastask \
            -p 5432:5432 \
            -v $POSTGRES_DATA_VOLUME:/var/lib/postgresql/data \
            postgres:16-alpine
    fi
    
    echo "⏳ Aguardando PostgreSQL inicializar..."
    sleep 5
    
    # Verificar se setup inicial é necessário
    if [ ! -f ".wastask_initialized" ]; then
        echo "🔧 Executando setup inicial do banco..."
        uv run python wastask.py db setup 2>/dev/null || echo "⚠️ Setup pode precisar ser executado manualmente"
        touch .wastask_initialized
    fi
    
    echo "✅ WasTask pronto para uso!"
    echo ""
    echo "Exemplos de uso:"
    echo "  uv run python wastask.py db stats"
    echo "  uv run python wastask.py db list"
}

stop_postgres() {
    echo "🛑 Parando PostgreSQL..."
    
    if docker ps --format "table {{.Names}}" | grep -q "^${POSTGRES_CONTAINER}$"; then
        docker stop $POSTGRES_CONTAINER
        echo "✅ PostgreSQL parado"
    else
        echo "ℹ️ PostgreSQL já estava parado"
    fi
}

show_status() {
    echo "📊 Status do WasTask:"
    echo ""
    
    # Status do Docker
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "^${POSTGRES_CONTAINER}"; then
        echo "🟢 PostgreSQL: Rodando"
        
        # Mostrar estatísticas se disponível
        echo ""
        echo "📈 Estatísticas do banco:"
        uv run python wastask.py db stats 2>/dev/null || echo "   (execute 'start' para ver estatísticas)"
    else
        if docker ps -a --format "table {{.Names}}\t{{.Status}}" | grep -q "^${POSTGRES_CONTAINER}"; then
            echo "🟡 PostgreSQL: Parado"
        else
            echo "⚫ PostgreSQL: Não criado"
        fi
    fi
    
    # Status dos dados
    if docker volume ls | grep -q $POSTGRES_DATA_VOLUME; then
        echo "💾 Volume de dados: Existente"
    else
        echo "💾 Volume de dados: Não criado"
    fi
    
    echo ""
    echo "💡 Use './wastask-control.sh start' para iniciar"
}

restart_postgres() {
    echo "🔄 Reiniciando PostgreSQL..."
    stop_postgres
    sleep 2
    start_postgres
}

clean_all() {
    echo "🧹 Limpando tudo..."
    echo "⚠️ ATENÇÃO: Isso vai remover TODOS os dados!"
    read -p "Tem certeza? (y/N): " confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo "🛑 Parando container..."
        docker stop $POSTGRES_CONTAINER 2>/dev/null || true
        
        echo "🗑️ Removendo container..."
        docker rm $POSTGRES_CONTAINER 2>/dev/null || true
        
        echo "💾 Removendo volume de dados..."
        docker volume rm $POSTGRES_DATA_VOLUME 2>/dev/null || true
        
        echo "🧹 Removendo arquivo de inicialização..."
        rm -f .wastask_initialized
        
        echo "✅ Limpeza concluída"
    else
        echo "❌ Operação cancelada"
    fi
}

# Main
check_docker

case "${1:-help}" in
    start)
        start_postgres
        ;;
    stop)
        stop_postgres
        ;;
    status)
        show_status
        ;;
    restart)
        restart_postgres
        ;;
    clean)
        clean_all
        ;;
    help|*)
        show_help
        ;;
esac