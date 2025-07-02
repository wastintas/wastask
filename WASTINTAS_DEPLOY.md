# 🚀 Deploy WasTask - wastintas.com.br

## 🎯 Configuração Específica

### Domínios Configurados
- **Principal**: `wastasks.wastintas.com.br`
- **Interface Web**: `web.wastasks.wastintas.com.br` (opcional)

### DNS Necessário
Configure no seu provedor de DNS:
```
CNAME wastasks.wastintas.com.br     → wastintas.com.br
CNAME web.wastasks.wastintas.com.br → wastintas.com.br  (opcional)
```

## 📦 Deploy no Portainer

### 1. Acessar Portainer
- URL: `https://portainer.wastintas.com.br` (ou seu endereço)
- Login com suas credenciais

### 2. Criar Stack
1. **Stacks** → **Add stack**
2. **Nome**: `wastask-production`
3. **Method**: `Web editor`
4. **Colar conteúdo** de `portainer-traefik-stack.yml`

### 3. Configurar Environment Variables
Na seção **Environment variables**:
1. Clicar em **Advanced mode**
2. Colar o conteúdo de `wastintas.env`
3. **IMPORTANTE**: Alterar as senhas padrão!

```env
# MUDE ESTAS SENHAS!
POSTGRES_PASSWORD=SuaSenhaPostgreSQLSuperSegura2024
REDIS_PASSWORD=SuaSenhaRedisSuperSegura2024
SECRET_KEY=SuaChaveSecretaDeMinimo32CaracteresAqui
```

### 4. Deploy
- Clicar **Deploy the stack**
- Aguardar containers iniciarem (1-2 minutos)

## 🔍 Verificação

### 1. Status dos Containers
No Portainer, verificar se todos estão "running":
- ✅ `wastask-postgres`
- ✅ `wastask-redis` 
- ✅ `wastask-api`

### 2. Teste de Conectividade
```bash
# Verificar se responde
curl -I https://wastasks.wastintas.com.br/health
# Deve retornar: HTTP/2 200

# Verificar SSL
curl -I https://wastasks.wastintas.com.br
# Deve ter certificado Let's Encrypt válido
```

### 3. Interface Web
Acessar: `https://wastasks.wastintas.com.br`
- Deve carregar a interface do WasTask
- Testar upload de PRD
- Verificar estatísticas

## 🔧 Configuração de API

### Para usar APIs de LLM:

1. **Anthropic (Recomendado)**:
   - Criar conta em https://console.anthropic.com
   - Gerar API key
   - Adicionar `ANTHROPIC_API_KEY=sk-ant-...` no Portainer

2. **OpenAI (Alternativa)**:
   - Criar conta em https://platform.openai.com
   - Gerar API key
   - Adicionar `OPENAI_API_KEY=sk-...` no Portainer

3. **Atualizar Stack**:
   - Editar variáveis no Portainer
   - **Redeploy** o stack

## 📊 Monitoramento

### Via Portainer
- **Containers** → Ver logs em tempo real
- **Stats** → CPU, RAM, Network
- **Console** → Executar comandos

### Via API
```bash
# Estatísticas
curl https://wastasks.wastintas.com.br/api/stats

# Projetos
curl https://wastasks.wastintas.com.br/api/projects

# Health check
curl https://wastasks.wastintas.com.br/health
```

### Comandos Úteis
```bash
# Conectar no container da API
docker exec -it wastask-api bash

# Ver logs
docker logs -f wastask-api

# Executar comandos WasTask
python wastask.py db stats
python wastask.py db list
```

## 🔒 Segurança

### 1. Firewall
```bash
# Apenas portas necessárias
ufw allow 22    # SSH
ufw allow 80    # HTTP (Traefik)
ufw allow 443   # HTTPS (Traefik)
ufw enable
```

### 2. Basic Auth (Opcional)
Para proteção adicional:
```bash
# Gerar hash
htpasswd -nb admin suasenha

# Adicionar ao Portainer:
BASIC_AUTH_USERS=admin:$$2y$$10$$hash-gerado-aqui
```

### 3. Rate Limiting
Já configurado no stack:
- 50 requests/minuto por IP
- Proteção DDoS via Traefik

## 💾 Backup

### Backup Automático do PostgreSQL
```bash
# Script de backup
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec wastask-postgres pg_dump -U wastask wastask > /backup/wastask_$DATE.sql
find /backup -name "wastask_*.sql" -mtime +7 -delete
```

### Agendar no cron
```bash
# Backup diário às 2:00
0 2 * * * /root/backup-wastask.sh
```

## 🚨 Troubleshooting

### Container não inicia
```bash
# Ver logs detalhados
docker logs wastask-api --tail 50

# Verificar variáveis
docker exec wastask-api env | grep -E "DATABASE|SECRET"
```

### Erro de SSL
```bash
# Verificar Traefik
docker logs traefik --tail 50

# Testar DNS
nslookup wastasks.wastintas.com.br
```

### Performance
```bash
# Monitorar recursos
docker stats

# Otimizar PostgreSQL se necessário
docker exec -it wastask-postgres psql -U wastask -d wastask -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  SELECT pg_reload_conf();
"
```

## 📞 Suporte

Para issues ou dúvidas:
1. Verificar logs dos containers
2. Testar conectividade de rede
3. Confirmar configuração DNS
4. Validar variáveis de ambiente

---

## ✅ Checklist Final

- [ ] DNS configurado para `wastasks.wastintas.com.br`
- [ ] Stack deployado no Portainer
- [ ] Senhas alteradas no `.env`
- [ ] Containers rodando (postgres, redis, api)
- [ ] HTTPS funcionando com Let's Encrypt
- [ ] Interface web acessível
- [ ] API key configurada (Anthropic/OpenAI)
- [ ] Health check retorna 200
- [ ] Backup configurado

**🎉 WasTask rodando em produção em `https://wastasks.wastintas.com.br`!**