# 🚀 Deploy do WasTask no Portainer + Traefik

## 📋 Pré-requisitos

1. **VPS com Portainer funcionando**
2. **Traefik configurado** com:
   - Network `WasNet` criada
   - Let's Encrypt funcionando
   - Entrypoints `web` (80) e `websecure` (443)

## 🔧 Passo a Passo

### 1. Preparar Arquivos na VPS

Conecte na sua VPS e crie a estrutura:

```bash
# Conectar na VPS
ssh user@sua-vps.com

# Criar diretório do projeto
mkdir -p /opt/wastask
cd /opt/wastask

# Baixar arquivos do projeto
# (ou usar git clone se tiver repositório)
```

### 2. Configurar Environment Variables

Copie o arquivo `env.example` e configure:

```bash
cp env.example .env
nano .env
```

**Configure obrigatoriamente:**
```bash
# Seu domínio
WASTASK_DOMAIN=wastask.seudominio.com

# Senhas seguras
POSTGRES_PASSWORD=sua_senha_postgres_super_segura
REDIS_PASSWORD=sua_senha_redis_super_segura
SECRET_KEY=sua_chave_secreta_de_pelo_menos_32_caracteres

# Pelo menos uma API de LLM
ANTHROPIC_API_KEY=sk-ant-api-key-aqui
# ou
OPENAI_API_KEY=sk-openai-key-aqui
```

### 3. Criar Stack no Portainer

1. **Acessar Portainer**: `https://portainer.seudominio.com`
2. **Ir em Stacks** → **Add stack**
3. **Nome**: `wastask`
4. **Method**: `Web editor`
5. **Colar** o conteúdo de `portainer-traefik-stack.yml`
6. **Environment variables**: 
   - Clicar em **Advanced mode**
   - Colar o conteúdo do seu `.env`
7. **Deploy the stack**

### 4. Configurar DNS

No seu provedor de DNS, crie os registros:

```
A     wastask.seudominio.com     → IP_DA_VPS
A     web.wastask.seudominio.com → IP_DA_VPS  (opcional)
```

### 5. Verificar Deploy

Aguarde 1-2 minutos e teste:

```bash
# Verificar se está rodando
curl -I https://wastask.seudominio.com/health

# Deve retornar: HTTP/2 200
```

## 🔍 Monitoramento

### Via Portainer

1. **Containers**: Verificar se todos estão "running"
2. **Logs**: Clicar em cada container para ver logs
3. **Stats**: Monitorar CPU/RAM/Network

### Via API

```bash
# Status da aplicação
curl https://wastask.seudominio.com/api/stats

# Verificar projetos
curl https://wastask.seudominio.com/api/projects
```

## 🛠️ Comandos Úteis

### Executar comandos WasTask

```bash
# Conectar no container
docker exec -it wastask-api bash

# Executar comandos
python wastask.py db stats
python wastask.py db list
python wastask.py prd analyze /app/uploads/exemplo.md
```

### Backup do Banco

```bash
# Backup automático
docker exec wastask-postgres pg_dump -U wastask wastask > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20231201.sql | docker exec -i wastask-postgres psql -U wastask -d wastask
```

### Logs em Tempo Real

```bash
# Todos os serviços
docker-compose -f /opt/wastask/docker-compose.yml logs -f

# Apenas API
docker logs -f wastask-api

# Apenas PostgreSQL
docker logs -f wastask-postgres
```

## 🔒 Segurança

### 1. Basic Auth (Opcional)

Para adicionar proteção adicional:

```bash
# Gerar usuário/senha
htpasswd -nb admin suasenha

# Resultado: admin:$2y$10$...
# Copiar e adicionar ao .env:
BASIC_AUTH_USERS=admin:$$2y$$10$$...
```

Depois atualizar o stack no Portainer.

### 2. Firewall

```bash
# Permitir apenas portas necessárias
ufw allow 22    # SSH
ufw allow 80    # HTTP (Traefik)
ufw allow 443   # HTTPS (Traefik)
ufw enable
```

### 3. SSL/TLS

O Traefik cuida automaticamente dos certificados Let's Encrypt.

## 📊 Interface Web (Opcional)

O stack inclui uma interface web simples. Para ativar:

1. **Criar pasta web**:
```bash
mkdir -p /opt/wastask/web
```

2. **Adicionar arquivos HTML/CSS/JS**

3. **Configurar domínio**: `web.wastask.seudominio.com`

## 🆘 Troubleshooting

### Container não inicia

```bash
# Ver logs detalhados
docker logs wastask-api --tail 50

# Verificar configuração
docker exec wastask-api env | grep -E 'DATABASE|SECRET|API'
```

### Erro de conexão com banco

```bash
# Testar conexão
docker exec wastask-api pg_isready -h postgres -U wastask -d wastask

# Ver logs do PostgreSQL
docker logs wastask-postgres --tail 20
```

### Certificado SSL não funciona

```bash
# Verificar Traefik
docker logs traefik --tail 50

# Verificar DNS
nslookup wastask.seudominio.com
```

### Performance

```bash
# Monitorar recursos
docker stats

# Otimizar PostgreSQL (opcional)
docker exec -it wastask-postgres psql -U wastask -d wastask -c "
  ALTER SYSTEM SET shared_buffers = '256MB';
  ALTER SYSTEM SET effective_cache_size = '1GB';
  SELECT pg_reload_conf();
"
```

## 🔄 Atualizações

Para atualizar o WasTask:

1. **Fazer backup** do banco
2. **Atualizar** os arquivos do projeto
3. **Redeployar** o stack no Portainer
4. **Verificar** se tudo funciona

## 📱 Uso via API

### Analisar PRD via API

```bash
# Upload e análise
curl -X POST \
  -H "Content-Type: multipart/form-data" \
  -F "file=@meu_prd.md" \
  https://wastask.seudominio.com/api/analyze
```

### Ver projetos

```bash
curl https://wastask.seudominio.com/api/projects
```

### Expandir tarefas

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"task_id": 5}' \
  https://wastask.seudominio.com/api/expand
```

---

## 🎉 Resultado Final

Após o deploy, você terá:

- ✅ **WasTask rodando 24/7** em `https://wastask.seudominio.com`
- ✅ **SSL automático** via Let's Encrypt
- ✅ **Banco PostgreSQL** com backup automático
- ✅ **Redis** para cache e sessões
- ✅ **Rate limiting** e proteção DDoS
- ✅ **Logs centralizados** no Portainer
- ✅ **Monitoramento** em tempo real
- ✅ **Escalabilidade** via Docker Swarm (futuro)

**Agora você pode usar o WasTask de qualquer lugar, através da API ou interface web!**