# 🚀 Deploy Wastask via GitHub - Guia Completo

## 1. Criar Repositório no GitHub

1. Acesse: https://github.com/wastintas
2. Clique em **"New repository"**
3. Nome: `wastask`
4. Descrição: `AI-powered project management system`
5. Marque como **Public** (ou Private se preferir)
6. **NÃO** inicialize com README (já temos código)
7. Clique em **"Create repository"**

## 2. Fazer Push do Código Local

Execute no terminal local:

```bash
# Adicionar remote do GitHub
git remote add origin https://github.com/wastintas/wastask.git

# Push para GitHub
git push -u origin main
```

## 3. Deploy na VPS via GitHub

### Opção A: Comando Manual na VPS

```bash
# SSH na VPS
ssh -i ~/.ssh/id_ed25519_walter root@31.97.240.19

# Parar stack atual (se houver)
docker stack rm wastask

# Clonar repositório
cd /opt
rm -rf wastask-github
git clone https://github.com/wastintas/wastask.git wastask-github
cd wastask-github

# Deploy com GitHub
docker stack deploy -c deploy-github-vps.yml wastask
```

### Opção B: Script Automatizado

Crie este script na VPS:

```bash
#!/bin/bash
# /opt/update-wastask.sh

echo "🔄 Atualizando Wastask do GitHub..."

# Parar serviços
docker stack rm wastask
sleep 10

# Atualizar código
cd /opt
rm -rf wastask-github
git clone https://github.com/wastintas/wastask.git wastask-github
cd wastask-github

# Iniciar novamente
docker stack deploy -c deploy-github-vps.yml wastask

echo "✅ Wastask atualizado!"
docker service ls | grep wastask
```

## 4. Benefícios do Deploy via GitHub

- ✅ **Versionamento**: Histórico completo de mudanças
- ✅ **Deploy Automático**: Simples `git push` + script
- ✅ **Rollback Fácil**: Voltar para versões anteriores
- ✅ **Colaboração**: Outros devs podem contribuir
- ✅ **CI/CD**: Automação futura de testes/deploy
- ✅ **Backup**: Código seguro no GitHub

## 5. Workflow de Desenvolvimento

```bash
# Desenvolvimento local
git add .
git commit -m "Nova funcionalidade"
git push origin main

# Deploy na VPS
ssh root@31.97.240.19 '/opt/update-wastask.sh'
```

## 6. URLs Importantes

- **Repositório**: https://github.com/wastintas/wastask
- **Aplicação**: https://wastasks.wastintas.com.br
- **API Docs**: https://wastasks.wastintas.com.br/docs
- **Health Check**: https://wastasks.wastintas.com.br/health

## 7. Comandos Úteis na VPS

```bash
# Ver logs
docker service logs wastask_wastask-api -f

# Ver status dos serviços
docker service ls | grep wastask

# Restart apenas a API
docker service update --force wastask_wastask-api

# Ver informações detalhadas
docker service ps wastask_wastask-api
```