# Opções de Deploy do Wastask

## 🤔 Situação Atual

**Não**, o sistema NÃO precisa ficar rodando sempre na sua máquina. Atualmente:
- É executado sob demanda (quando você chama os comandos)
- O banco PostgreSQL é o único que precisa estar ativo durante o uso
- Não há servidor web ou processo daemon rodando

## 📦 Opção 1: Uso Local Sob Demanda (Atual)

### Como funciona:
```bash
# Iniciar PostgreSQL quando precisar
docker start postgres-wastask

# Usar o Wastask
uv run python wastask.py [comando]

# Parar PostgreSQL quando terminar
docker stop postgres-wastask
```

### Prós:
- ✅ Não consome recursos quando não está em uso
- ✅ Controle total sobre quando executar
- ✅ Ideal para uso pessoal ocasional

### Contras:
- ❌ Precisa iniciar PostgreSQL manualmente
- ❌ Não acessível remotamente
- ❌ Sem interface web

## 🐳 Opção 2: Docker Compose (Recomendado)

Vamos criar um setup completo com Docker:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: wastask
      POSTGRES_PASSWORD: wastask123
      POSTGRES_DB: wastask
    volumes:
      - wastask_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U wastask"]
      interval: 10s
      timeout: 5s
      retries: 5

  wastask-api:
    build: .
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql://wastask:wastask123@postgres:5432/wastask
      SECRET_KEY: your-secret-key-here
    ports:
      - "8000:8000"
    volumes:
      - ./:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

volumes:
  wastask_data:
```

### Como usar:
```bash
# Iniciar tudo
docker-compose up -d

# Parar tudo
docker-compose down

# Ver logs
docker-compose logs -f
```

## ☁️ Opção 3: Deploy em Nuvem

### 3.1 Railway/Render (Mais Fácil)
```bash
# railway.app ou render.com
# Upload do projeto e deploy automático
# PostgreSQL incluído
# ~$5-10/mês
```

### 3.2 VPS (Digital Ocean, Linode)
```bash
# Script de instalação
#!/bin/bash
apt update && apt upgrade -y
apt install -y python3.11 postgresql-14
# ... resto da configuração
```

### 3.3 Serverless (AWS Lambda + RDS)
- API Gateway + Lambda para endpoints
- RDS PostgreSQL para banco
- S3 para arquivos
- ~$10-50/mês dependendo do uso

## 🖥️ Opção 4: Interface Web Local

Vamos criar uma interface web simples:

```python
# webapp.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import subprocess
import json

app = FastAPI(title="WasTask Web")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>WasTask</title>
            <style>
                body { font-family: Arial; margin: 40px; }
                .button { 
                    background: #4CAF50; 
                    color: white; 
                    padding: 10px 20px; 
                    border: none; 
                    cursor: pointer; 
                    margin: 5px;
                }
                .output { 
                    background: #f4f4f4; 
                    padding: 20px; 
                    margin-top: 20px; 
                    white-space: pre-wrap; 
                }
            </style>
        </head>
        <body>
            <h1>🚀 WasTask Control Panel</h1>
            
            <h2>Análise de PRD</h2>
            <input type="file" id="prdFile" accept=".md,.txt">
            <button class="button" onclick="analyzePRD()">Analisar PRD</button>
            
            <h2>Gerenciamento</h2>
            <button class="button" onclick="listProjects()">Listar Projetos</button>
            <button class="button" onclick="showStats()">Estatísticas</button>
            
            <div id="output" class="output"></div>
            
            <script>
                async function analyzePRD() {
                    const file = document.getElementById('prdFile').files[0];
                    if (!file) {
                        alert('Selecione um arquivo!');
                        return;
                    }
                    
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    document.getElementById('output').textContent = JSON.stringify(result, null, 2);
                }
                
                async function listProjects() {
                    const response = await fetch('/api/projects');
                    const result = await response.json();
                    document.getElementById('output').textContent = JSON.stringify(result, null, 2);
                }
                
                async function showStats() {
                    const response = await fetch('/api/stats');
                    const result = await response.json();
                    document.getElementById('output').textContent = JSON.stringify(result, null, 2);
                }
            </script>
        </body>
    </html>
    """

@app.post("/api/analyze")
async def analyze_prd(file: UploadFile):
    # Salvar arquivo temporário
    content = await file.read()
    temp_path = f"/tmp/{file.filename}"
    
    with open(temp_path, "wb") as f:
        f.write(content)
    
    # Executar análise
    result = subprocess.run(
        ["uv", "run", "python", "wastask_simple.py", temp_path],
        capture_output=True,
        text=True
    )
    
    return {"output": result.stdout, "error": result.stderr}

@app.get("/api/projects")
async def list_projects():
    result = subprocess.run(
        ["uv", "run", "python", "wastask.py", "db", "list"],
        capture_output=True,
        text=True
    )
    return {"output": result.stdout}

@app.get("/api/stats")
async def show_stats():
    result = subprocess.run(
        ["uv", "run", "python", "wastask.py", "db", "stats"],
        capture_output=True,
        text=True
    )
    return {"output": result.stdout}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Executar interface web:
```bash
# Instalar dependências
uv pip install fastapi uvicorn python-multipart

# Rodar servidor
uv run python webapp.py

# Acessar: http://localhost:8000
```

## 🚀 Opção 5: Script de Automação

```bash
#!/bin/bash
# wastask-start.sh

echo "🚀 Iniciando WasTask..."

# Verificar se PostgreSQL está rodando
if ! docker ps | grep -q postgres-wastask; then
    echo "📦 Iniciando PostgreSQL..."
    docker run -d --name postgres-wastask \
        -e POSTGRES_USER=wastask \
        -e POSTGRES_PASSWORD=wastask123 \
        -e POSTGRES_DB=wastask \
        -p 5432:5432 \
        postgres:16-alpine
    
    echo "⏳ Aguardando PostgreSQL iniciar..."
    sleep 5
fi

echo "✅ PostgreSQL rodando"

# Verificar se precisa setup inicial
if [ ! -f ".wastask_initialized" ]; then
    echo "🔧 Executando setup inicial..."
    uv run python wastask.py db setup
    touch .wastask_initialized
fi

echo "✅ WasTask pronto para uso!"
echo ""
echo "Comandos disponíveis:"
echo "  wastask analyze <prd_file>    - Analisar PRD"
echo "  wastask db list              - Listar projetos"
echo "  wastask task tree <id>       - Ver tarefas"
echo ""
echo "Para parar PostgreSQL: docker stop postgres-wastask"
```

## 📋 Recomendação

Para seu caso, sugiro:

1. **Desenvolvimento**: Use Docker Compose (Opção 2)
   - Fácil ligar/desligar
   - Ambiente isolado
   - Pronto para deploy

2. **Uso Pessoal**: Script de automação (Opção 5)
   - Um comando para iniciar tudo
   - Para quando terminar
   - Sem consumo de recursos constante

3. **Produção**: Deploy em nuvem (Opção 3)
   - Sempre disponível
   - Acessível de qualquer lugar
   - Backup automático

## 🛑 Como Parar Tudo

```bash
# Parar PostgreSQL
docker stop postgres-wastask

# Remover container (mantém dados)
docker rm postgres-wastask

# Remover TUDO (incluindo dados)
docker rm -f postgres-wastask
docker volume rm postgres-wastask-data
```

O importante é: **você tem controle total** sobre quando e como executar o sistema!