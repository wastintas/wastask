#!/bin/bash

echo "🔍 Verificando endpoints do Wastask..."
echo "======================================"

BASE_URL="https://wastasks.wastintas.com.br"

echo ""
echo "📋 Testando todos os endpoints possíveis:"

# Lista de endpoints para testar
endpoints=(
    "/"
    "/health" 
    "/docs"
    "/openapi.json"
    "/api/v1/health"
    "/api/health"
    "/projects"
    "/api/projects"
    "/api/v1/projects"
    "/tasks"
    "/api/tasks"
    "/api/v1/tasks"
    "/stats"
    "/api/stats"
    "/api/v1/stats"
    "/analyze"
    "/api/analyze"
    "/api/v1/analyze"
    "/auth/login"
    "/api/auth/login"
)

for endpoint in "${endpoints[@]}"; do
    echo -n "Testing $endpoint ... "
    status=$(curl -k -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    if [ "$status" = "200" ]; then
        echo "✅ $status"
    elif [ "$status" = "404" ]; then
        echo "❌ $status (Not Found)"
    elif [ "$status" = "422" ]; then
        echo "⚠️ $status (Validation Error - endpoint exists)"
    elif [ "$status" = "405" ]; then
        echo "⚠️ $status (Method Not Allowed - endpoint exists)"
    else
        echo "❓ $status"
    fi
done

echo ""
echo "🔍 Verificando logs do container..."
echo "=================================="