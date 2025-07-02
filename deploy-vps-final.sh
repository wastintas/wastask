#!/bin/bash

echo "🚀 Deploy final do Wastask na VPS"
echo "================================="

# 1. Fazer upload do arquivo via SCP
echo "📤 Enviando configuração para VPS..."
scp -i ~/.ssh/id_ed25519_walter wastask-vps-final.yml root@31.97.240.19:/tmp/

# 2. SSH para a VPS e executar deploy
echo "🔧 Executando deploy via SSH..."
ssh -i ~/.ssh/id_ed25519_walter root@31.97.240.19 << 'EOF'
    echo "📋 Parando serviços antigos..."
    docker stack rm wastask 2>/dev/null || echo "Nenhum stack anterior"
    
    echo "⏱️ Aguardando limpeza..."
    sleep 10
    
    echo "🚀 Deployando nova versão..."
    docker stack deploy -c /tmp/wastask-vps-final.yml wastask
    
    echo "📊 Status do deploy:"
    docker stack ps wastask
    
    echo "✅ Deploy concluído!"
    echo "🌐 Acesse: https://wastasks.wastintas.com.br"
    echo "📚 Docs: https://wastasks.wastintas.com.br/docs"
EOF

echo "🎯 Deploy finalizado! Aguarde alguns minutos para tudo inicializar."