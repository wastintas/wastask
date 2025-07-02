#!/bin/bash

echo "🔄 Atualizando Wastask na VPS do GitHub..."
echo "=========================================="

# Parar stack atual
echo "⏹️  Parando stack atual..."
docker stack rm wastask
sleep 15

# Limpar diretório anterior
echo "🧹 Limpando código anterior..."
cd /opt
rm -rf wastask-github

# Clonar repositório atualizado
echo "📥 Clonando repositório do GitHub..."
git clone https://github.com/wastintas/wastask.git wastask-github
cd wastask-github

# Verificar se arquivo existe
if [ ! -f "deploy-github-simple.yml" ]; then
    echo "❌ Arquivo deploy-github-simple.yml não encontrado!"
    echo "📋 Arquivos disponíveis:"
    ls -la deploy-*
    exit 1
fi

# Deploy novo stack
echo "🚀 Fazendo deploy do novo stack..."
docker stack deploy -c deploy-github-simple.yml wastask

# Aguardar inicialização
echo "⏳ Aguardando serviços subirem..."
sleep 30

# Verificar status
echo "📊 Status dos serviços:"
docker service ls | grep wastask

echo ""
echo "✅ Deploy concluído!"
echo "🌐 Acesse: https://wastasks.wastintas.com.br"
echo "🔍 Health: https://wastasks.wastintas.com.br/health"
echo ""
echo "📋 Para ver logs: docker service logs wastask_wastask-api -f"