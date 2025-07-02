#!/bin/bash

echo "🧪 Testando Wastask API completa em wastasks.wastintas.com.br"
echo "=============================================================="

# Teste 1: Health Check
echo ""
echo "1️⃣ Testando Health Check..."
curl -k -s https://wastasks.wastintas.com.br/health | jq . || echo "Erro no health check"

# Teste 2: Página principal
echo ""
echo "2️⃣ Testando página principal..."
curl -k -s https://wastasks.wastintas.com.br/ | head -20

# Teste 3: Documentação da API
echo ""
echo "3️⃣ Testando documentação da API..."
curl -k -s https://wastasks.wastintas.com.br/docs | head -10

# Teste 4: Listar projetos
echo ""
echo "4️⃣ Testando listagem de projetos..."
curl -k -s https://wastasks.wastintas.com.br/api/projects | jq . || echo "Erro ao listar projetos"

# Teste 5: Estatísticas
echo ""
echo "5️⃣ Testando estatísticas..."
curl -k -s https://wastasks.wastintas.com.br/api/stats | jq . || echo "Erro nas estatísticas"

# Teste 6: Upload de PRD (simulado)
echo ""
echo "6️⃣ Testando upload de PRD..."
echo "Criando arquivo de teste..."
cat > /tmp/test_prd.md << 'EOF'
# Sistema de E-commerce

## Objetivos
Desenvolver plataforma de e-commerce com carrinho de compras.

## Funcionalidades
- Cadastro de produtos
- Sistema de pagamento
- Gestão de pedidos
- Relatórios de vendas

## Tecnologias
- Frontend: React
- Backend: Node.js
- Database: MongoDB
EOF

# Upload do arquivo via POST
curl -k -X POST https://wastasks.wastintas.com.br/api/analyze \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/tmp/test_prd.md" | jq . || echo "Erro no upload"

echo ""
echo "✅ Teste da API concluído!"
echo ""
echo "Para acessar a interface web: https://wastasks.wastintas.com.br"
echo "Para acessar a documentação: https://wastasks.wastintas.com.br/docs"