#!/bin/bash
# Comandos para executar via SSH na sua VPS

echo "🚀 Preparando WasTask na VPS..."

# Criar diretório do projeto
sudo mkdir -p /opt/wastask
cd /opt/wastask

# Baixar arquivos do WasTask (você vai fazer upload manual ou usar estes comandos)
echo "📥 Baixando código do WasTask..."

# Opção 1: Se você tiver o código em um repositório
# git clone https://github.com/seuusuario/wastask.git .

# Opção 2: Criar estrutura básica aqui mesmo
cat > requirements.txt << 'EOF'
# WasTask Dependencies
click>=8.0.0
rich>=13.0.0
asyncpg>=0.28.0
databases[postgresql]>=0.8.0
httpx>=0.24.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
pydantic>=2.0.0
aiofiles>=23.0.0
fastapi>=0.100.0
uvicorn>=0.20.0
python-multipart>=0.0.6
EOF

# Criar webapp.py simplificado
cat > webapp.py << 'EOF'
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import tempfile
import asyncio
from pathlib import Path

app = FastAPI(
    title="WasTask API", 
    description="AI-powered project management system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wastask-api"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 WasTask - AI Project Management</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; 
                margin: 0;
                color: #333;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                background: white;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 500px;
            }
            .header h1 { 
                font-size: 2.5rem; 
                margin-bottom: 10px;
                color: #667eea;
            }
            .status {
                background: #f0f8ff;
                border: 1px solid #667eea;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                text-decoration: none;
                display: inline-block;
                margin: 8px;
                font-weight: 500;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 WasTask</h1>
                <p>AI-powered Project Management System</p>
            </div>
            
            <div class="status">
                <h3>✅ Sistema Funcionando!</h3>
                <p><strong>Domínio:</strong> wastasks.wastintas.com.br</p>
                <p><strong>Status:</strong> Online e pronto para uso</p>
            </div>
            
            <div>
                <a href="/docs" class="btn">📚 API Documentation</a>
                <a href="/api/stats" class="btn">📊 Statistics</a>
                <a href="/health" class="btn">🔍 Health Check</a>
            </div>
            
            <hr style="margin: 30px 0;">
            <p><em>WasTask está rodando com sucesso na sua VPS!</em></p>
        </div>
    </body>
    </html>
    """

@app.get("/api/stats")
async def get_stats():
    return {
        "status": "success",
        "stats": {
            "total_projects": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "active_projects": 0
        },
        "message": "WasTask API funcionando perfeitamente!",
        "version": "1.0.0"
    }

@app.post("/api/analyze")
async def analyze_prd(file: UploadFile = File(...)):
    return {
        "status": "success", 
        "message": "PRD analysis endpoint ready",
        "filename": file.filename,
        "note": "Full analysis functionality will be implemented"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Criar arquivo de configuração
cat > .env << 'EOF'
# WasTask Configuration
DATABASE_URL=postgresql://wastask:WastasksDB2024!@postgres:5432/wastask
REDIS_URL=redis://:WastasksRedis2024!@redis:6379/0
SECRET_KEY=WastasksJWT2024SuperSecretKey32CharsMin!
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
BASE_URL=https://wastasks.wastintas.com.br
COST_OPTIMIZATION_ENABLED=true
MAX_DAILY_COST_USD=25.0
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=60
EOF

# Definir permissões corretas
sudo chown -R root:root /opt/wastask
sudo chmod -R 755 /opt/wastask

echo "✅ WasTask preparado em /opt/wastask"
echo ""
echo "Próximos passos:"
echo "1. Use o stack 'portainer-vps-stack.yml' no Portainer"
echo "2. O código será montado de /opt/wastask"
echo "3. Acesse https://wastasks.wastintas.com.br"