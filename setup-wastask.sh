#!/bin/bash

# WasTask Setup Script for VPS
# Execute: chmod +x setup-wastask.sh && ./setup-wastask.sh

echo "🚀 Setting up WasTask on VPS..."
echo "================================"

# Create directory
echo "📁 Creating /opt/wastask directory..."
mkdir -p /opt/wastask
cd /opt/wastask

# Create requirements.txt
echo "📦 Creating requirements.txt..."
cat > requirements.txt << 'REQUIREMENTS_EOF'
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
REQUIREMENTS_EOF

# Create webapp.py
echo "🐍 Creating webapp.py..."
cat > webapp.py << 'WEBAPP_EOF'
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json

app = FastAPI(
    title="WasTask API", 
    description="AI-powered project management system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wastask-api", "version": "1.0.0"}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 WasTask - wastasks.wastintas.com.br</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; 
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
                max-width: 600px;
                width: 90%;
            }
            .header h1 { 
                font-size: 2.5rem; 
                margin-bottom: 10px;
                color: #667eea;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            }
            .status {
                background: #f0f8ff;
                border: 2px solid #667eea;
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
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin: 20px 0;
            }
            .feature {
                background: #f8f9ff;
                padding: 16px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
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
                <h3>✅ Sistema Online e Funcionando!</h3>
                <p><strong>Domínio:</strong> wastasks.wastintas.com.br</p>
                <p><strong>Servidor:</strong> 31.97.240.19</p>
                <p><strong>Status:</strong> Pronto para uso</p>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h4>📊 Analytics</h4>
                    <p>Estatísticas em tempo real</p>
                </div>
                <div class="feature">
                    <h4>🔍 API</h4>
                    <p>RESTful API completa</p>
                </div>
                <div class="feature">
                    <h4>🚀 Deploy</h4>
                    <p>Rodando com Docker Swarm</p>
                </div>
                <div class="feature">
                    <h4>🔒 SSL</h4>
                    <p>HTTPS via Let's Encrypt</p>
                </div>
            </div>
            
            <div>
                <a href="/docs" class="btn">📚 API Documentation</a>
                <a href="/api/stats" class="btn">📊 Estatísticas</a>
                <a href="/health" class="btn">🔍 Health Check</a>
            </div>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            <p><em>WasTask deploy realizado com sucesso via Docker Swarm!</em></p>
            <p><small>Powered by FastAPI + PostgreSQL + Redis</small></p>
        </div>
    </body>
    </html>
    """

@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "status": "success",
        "stats": {
            "total_projects": 0,
            "total_tasks": 0,
            "completed_tasks": 0,
            "active_projects": 0,
            "uptime": "Online"
        },
        "system": {
            "server": "31.97.240.19",
            "domain": "wastasks.wastintas.com.br",
            "version": "1.0.0",
            "environment": "production"
        },
        "message": "WasTask API funcionando perfeitamente!"
    }

@app.post("/api/analyze")
async def analyze_prd(file: UploadFile = File(...)):
    """Analyze PRD file"""
    if not file.filename.endswith(('.md', '.txt')):
        raise HTTPException(status_code=400, detail="Apenas arquivos .md e .txt são aceitos")
    
    return {
        "status": "success", 
        "message": "Endpoint de análise de PRD está funcionando",
        "filename": file.filename,
        "size": "Unknown",
        "note": "Funcionalidade completa será implementada em breve"
    }

@app.get("/api/projects")
async def list_projects():
    """List all projects"""
    return {
        "status": "success",
        "projects": [],
        "message": "Endpoint de projetos funcionando"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
WEBAPP_EOF

# Create .env file
echo "⚙️ Creating .env configuration..."
cat > .env << 'ENV_EOF'
# WasTask Environment Configuration
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
ENV_EOF

# Create uploads and logs directories
echo "📁 Creating additional directories..."
mkdir -p uploads logs

# Set proper permissions
echo "🔒 Setting permissions..."
chmod -R 755 /opt/wastask
chmod +x webapp.py

# Display structure
echo ""
echo "✅ WasTask setup completed!"
echo "=========================="
echo "📁 Created files in /opt/wastask:"
ls -la /opt/wastask

echo ""
echo "📋 Next steps:"
echo "1. Deploy the Portainer stack using 'portainer-vps-stack.yml'"
echo "2. Access https://wastasks.wastintas.com.br"
echo "3. Check health at https://wastasks.wastintas.com.br/health"
echo ""
echo "🎉 Ready for deployment!"