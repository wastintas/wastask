# 🌐 Configuração da Rede WasNet

## ✅ Confirmar que a Rede WasNet Existe

Antes de fazer o deploy do WasTask, confirme que a rede `WasNet` existe e está configurada corretamente:

### 1. Verificar Redes Existentes

No Portainer:
1. **Networks** → **Browse**
2. Procure por `WasNet`
3. Deve estar listada como `external` ou `bridge`

Ou via SSH na VPS:
```bash
docker network ls | grep WasNet
```

### 2. Se a Rede NÃO Existir

Crie a rede `WasNet`:

```bash
# Criar rede bridge padrão
docker network create WasNet

# Ou rede bridge com configuração customizada
docker network create \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  WasNet
```

### 3. Verificar Traefik na WasNet

Confirme que o Traefik está conectado à rede WasNet:

```bash
# Ver redes do container do Traefik
docker inspect traefik | grep -A 10 "Networks"

# Ou conectar Traefik à WasNet se necessário
docker network connect WasNet traefik
```

## 🔧 Configuração Recomendada

Se você tem controle total sobre a rede, esta é a configuração ideal:

### docker-compose.yml do Traefik (exemplo)
```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v3.0
    container_name: traefik
    restart: unless-stopped
    command:
      - "--api.dashboard=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--certificatesresolvers.letsencrypt.acme.email=your@email.com"
      - "--certificatesresolvers.letsencrypt.acme.storage=/acme.json"
      - "--certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./acme.json:/acme.json
    networks:
      - WasNet
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.traefik.rule=Host(`traefik.yourdomain.com`)"
      - "traefik.http.routers.traefik.entrypoints=websecure"
      - "traefik.http.routers.traefik.tls.certresolver=letsencrypt"
      - "traefik.http.routers.traefik.service=api@internal"

networks:
  WasNet:
    driver: bridge
```

## 🚦 Teste de Conectividade

Após criar/confirmar a rede WasNet:

```bash
# Criar container de teste
docker run --rm --network WasNet alpine ping -c 4 traefik

# Verificar se Traefik responde
curl -I http://traefik.yourdomain.com
```

## ⚠️ Troubleshooting

### Erro: "network WasNet not found"
```bash
# Criar a rede
docker network create WasNet

# Verificar criação
docker network inspect WasNet
```

### Traefik não roteia para WasTask
```bash
# Verificar se Traefik está na rede WasNet
docker network inspect WasNet | grep traefik

# Conectar Traefik à WasNet se necessário
docker network connect WasNet traefik
docker restart traefik
```

### Containers não se comunicam
```bash
# Verificar conectividade entre containers
docker exec -it wastask-api ping traefik
docker exec -it traefik ping wastask-api
```

## 📋 Checklist Final

Antes de fazer deploy do WasTask:

- [ ] Rede `WasNet` existe
- [ ] Traefik está conectado à `WasNet`
- [ ] Traefik responde em HTTP/HTTPS
- [ ] DNS dos domínios está configurado
- [ ] Let's Encrypt funciona
- [ ] Portas 80/443 estão abertas

## 🔄 Alternativa: Usar Rede Existente

Se sua rede Traefik tem outro nome, você pode:

1. **Opção 1**: Mudar no stack do WasTask
```yaml
networks:
  sua-rede-traefik:  # em vez de WasNet
    external: true
```

2. **Opção 2**: Criar alias
```bash
# Não recomendado, mas possível
docker network connect --alias WasNet sua-rede-traefik
```

---

**✅ Com a rede WasNet configurada corretamente, o WasTask vai se conectar automaticamente ao Traefik e ficar acessível via HTTPS com certificado SSL!**