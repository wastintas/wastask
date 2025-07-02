#!/usr/bin/env python3
"""
WasTask Web API
FastAPI web application for WasTask
"""
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import json
import os
import tempfile
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

app = FastAPI(
    title="WasTask API", 
    description="AI-powered project management system",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "wastask-api"}

# Static files (se existir pasta static/)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    """Interface web simples"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 WasTask - AI Project Management</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; 
                color: #333;
            }
            .container { 
                max-width: 1200px; 
                margin: 0 auto; 
                padding: 20px;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 40px;
            }
            .header h1 { 
                font-size: 3rem; 
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .header p { 
                font-size: 1.2rem; 
                opacity: 0.9;
            }
            .cards {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            .card {
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            .card:hover { transform: translateY(-4px); }
            .card h3 { 
                color: #667eea; 
                margin-bottom: 16px;
                font-size: 1.3rem;
            }
            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 8px;
                padding: 20px;
                text-align: center;
                background: #f8f9ff;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                border-color: #764ba2;
                background: #f0f2ff;
            }
            .upload-area input[type="file"] {
                display: none;
            }
            .btn {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                font-size: 1rem;
                font-weight: 500;
                transition: all 0.3s ease;
                margin: 8px 4px;
            }
            .btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
            }
            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            .output {
                background: #1a1a1a;
                color: #00ff00;
                padding: 20px;
                border-radius: 8px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                white-space: pre-wrap;
                max-height: 400px;
                overflow-y: auto;
                margin-top: 20px;
                border: 1px solid #333;
            }
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                display: inline-block;
                margin-right: 10px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin: 20px 0;
            }
            .stat-item {
                background: #f8f9ff;
                padding: 16px;
                border-radius: 8px;
                text-align: center;
                border-left: 4px solid #667eea;
            }
            .stat-value {
                font-size: 2rem;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 4px;
            }
            .stat-label {
                color: #666;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 WasTask</h1>
                <p>AI-powered Project Management System</p>
            </div>
            
            <div class="cards">
                <div class="card">
                    <h3>📄 Analisar PRD</h3>
                    <div class="upload-area" onclick="document.getElementById('prdFile').click()">
                        <p>📎 Clique para selecionar arquivo PRD</p>
                        <p style="font-size: 0.9rem; color: #666; margin-top: 8px;">
                            Formatos: .md, .txt
                        </p>
                        <input type="file" id="prdFile" accept=".md,.txt" onchange="handleFileSelect(this)">
                    </div>
                    <div id="fileName" style="margin: 8px 0; font-weight: 500; color: #667eea;"></div>
                    <button class="btn" onclick="analyzePRD()" id="analyzeBtn" disabled>
                        🔍 Analisar PRD
                    </button>
                </div>
                
                <div class="card">
                    <h3>📊 Estatísticas</h3>
                    <div class="stats" id="statsContainer">
                        <div class="stat-item">
                            <div class="stat-value" id="totalProjects">-</div>
                            <div class="stat-label">Projetos</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="totalTasks">-</div>
                            <div class="stat-label">Tarefas</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="completedTasks">-</div>
                            <div class="stat-label">Concluídas</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="completionRate">-</div>
                            <div class="stat-label">Taxa Conclusão</div>
                        </div>
                    </div>
                    <button class="btn" onclick="loadStats()">📈 Atualizar</button>
                </div>
                
                <div class="card">
                    <h3>🗂️ Projetos</h3>
                    <div id="projectsList">
                        <p style="color: #666;">Clique em "Listar Projetos" para ver</p>
                    </div>
                    <button class="btn" onclick="listProjects()">📋 Listar Projetos</button>
                    <button class="btn" onclick="expandAllTasks()" id="expandBtn" disabled>
                        🔄 Expandir Tarefas
                    </button>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <span>Processando...</span>
            </div>
            
            <div id="output" class="output" style="display: none;"></div>
        </div>
        
        <script>
            let selectedProjectId = null;
            
            function showLoading(show) {
                document.getElementById('loading').style.display = show ? 'block' : 'none';
            }
            
            function showOutput(content) {
                const output = document.getElementById('output');
                output.style.display = 'block';
                output.textContent = content;
                output.scrollTop = output.scrollHeight;
            }
            
            function handleFileSelect(input) {
                const file = input.files[0];
                const fileName = document.getElementById('fileName');
                const analyzeBtn = document.getElementById('analyzeBtn');
                
                if (file) {
                    fileName.textContent = `📄 ${file.name}`;
                    analyzeBtn.disabled = false;
                } else {
                    fileName.textContent = '';
                    analyzeBtn.disabled = true;
                }
            }
            
            async function analyzePRD() {
                const fileInput = document.getElementById('prdFile');
                const file = fileInput.files[0];
                
                if (!file) {
                    alert('Selecione um arquivo PRD primeiro!');
                    return;
                }
                
                showLoading(true);
                
                try {
                    const formData = new FormData();
                    formData.append('file', file);
                    
                    const response = await fetch('/api/analyze', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        showOutput(`✅ Análise concluída!\\n\\n${JSON.stringify(result, null, 2)}`);
                        loadStats(); // Atualizar estatísticas
                        listProjects(); // Atualizar lista de projetos
                    } else {
                        showOutput(`❌ Erro na análise:\\n${result.detail || 'Erro desconhecido'}`);
                    }
                } catch (error) {
                    showOutput(`❌ Erro de conexão: ${error.message}`);
                } finally {
                    showLoading(false);
                }
            }
            
            async function listProjects() {
                showLoading(true);
                
                try {
                    const response = await fetch('/api/projects');
                    const result = await response.json();
                    
                    if (response.ok && result.projects) {
                        const projectsList = document.getElementById('projectsList');
                        const expandBtn = document.getElementById('expandBtn');
                        
                        if (result.projects.length === 0) {
                            projectsList.innerHTML = '<p style="color: #666;">Nenhum projeto encontrado</p>';
                            expandBtn.disabled = true;
                        } else {
                            projectsList.innerHTML = result.projects.map(p => 
                                `<div style="padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 4px 0; cursor: pointer;" 
                                      onclick="selectProject(${p.id}, this)">
                                    <strong>${p.name}</strong><br>
                                    <small style="color: #666;">${p.status} | ${p.complexity_score}/10</small>
                                </div>`
                            ).join('');
                            
                            if (result.projects.length > 0) {
                                selectedProjectId = result.projects[0].id;
                                expandBtn.disabled = false;
                            }
                        }
                        
                        showOutput(`📋 Projetos carregados:\\n${JSON.stringify(result, null, 2)}`);
                    } else {
                        showOutput(`❌ Erro ao listar projetos:\\n${JSON.stringify(result, null, 2)}`);
                    }
                } catch (error) {
                    showOutput(`❌ Erro de conexão: ${error.message}`);
                } finally {
                    showLoading(false);
                }
            }
            
            function selectProject(projectId, element) {
                // Remove seleção anterior
                document.querySelectorAll('#projectsList > div').forEach(div => {
                    div.style.background = '';
                    div.style.borderColor = '#ddd';
                });
                
                // Marca novo selecionado
                element.style.background = '#f0f2ff';
                element.style.borderColor = '#667eea';
                
                selectedProjectId = projectId;
                document.getElementById('expandBtn').disabled = false;
            }
            
            async function expandAllTasks() {
                if (!selectedProjectId) {
                    alert('Selecione um projeto primeiro!');
                    return;
                }
                
                showLoading(true);
                
                try {
                    const response = await fetch(`/api/expand-all/${selectedProjectId}`, {
                        method: 'POST'
                    });
                    
                    const result = await response.json();
                    showOutput(`🔄 Expansão de tarefas:\\n${JSON.stringify(result, null, 2)}`);
                    
                    if (response.ok) {
                        loadStats(); // Atualizar estatísticas
                    }
                } catch (error) {
                    showOutput(`❌ Erro de conexão: ${error.message}`);
                } finally {
                    showLoading(false);
                }
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const result = await response.json();
                    
                    if (response.ok && result.stats) {
                        const stats = result.stats;
                        document.getElementById('totalProjects').textContent = stats.total_projects || 0;
                        document.getElementById('totalTasks').textContent = stats.total_tasks || 0;
                        document.getElementById('completedTasks').textContent = stats.completed_tasks || 0;
                        
                        const rate = stats.total_tasks > 0 ? 
                            Math.round((stats.completed_tasks / stats.total_tasks) * 100) : 0;
                        document.getElementById('completionRate').textContent = rate + '%';
                    }
                } catch (error) {
                    console.error('Erro ao carregar estatísticas:', error);
                }
            }
            
            // Carregar estatísticas na inicialização
            loadStats();
        </script>
    </body>
    </html>
    """

@app.post("/api/analyze")
async def analyze_prd(file: UploadFile = File(...)):
    """Analisar PRD enviado"""
    if not file.filename.endswith(('.md', '.txt')):
        raise HTTPException(status_code=400, detail="Apenas arquivos .md e .txt são aceitos")
    
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(mode="wb", suffix=f"_{file.filename}", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        temp_path = tmp.name
    
    try:
        # Executar análise do Wastask
        process = await asyncio.create_subprocess_exec(
            "python", "wastask.py", "prd", "analyze", temp_path, "--output", "json", "--no-interactive",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            cwd="."
        )
        
        # Enviar inputs para o processo
        stdout, stderr = await process.communicate(input=b"1\\n1\\n")
        
        if process.returncode == 0:
            # Buscar arquivo JSON gerado
            project_name = file.filename.replace('.md', '').replace('.txt', '').replace(' ', '_').lower()
            json_files = list(Path('.').glob(f"*{project_name}*analysis.json"))
            
            if json_files:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    analysis_result = json.load(f)
                
                return {
                    "status": "success",
                    "message": "PRD analisado com sucesso",
                    "filename": file.filename,
                    "analysis": analysis_result
                }
            else:
                return {
                    "status": "partial_success", 
                    "message": "Análise executada, mas arquivo JSON não encontrado",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Erro na análise: {stderr.decode()}"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    finally:
        # Limpar arquivo temporário
        os.unlink(temp_path)

@app.get("/api/projects")
async def list_projects():
    """Listar todos os projetos"""
    try:
        process = await asyncio.create_subprocess_exec(
            "python", "wastask.py", "db", "list",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="."
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # Simular parsing da saída (idealmente seria uma API JSON)
            output = stdout.decode()
            
            # Por enquanto, retorna a saída bruta
            return {
                "status": "success",
                "projects": [],  # Seria parseado da saída
                "raw_output": output
            }
        else:
            raise HTTPException(status_code=500, detail=stderr.decode())
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    """Obter estatísticas do sistema"""
    try:
        process = await asyncio.create_subprocess_exec(
            "python", "wastask.py", "db", "stats",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="."
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            output = stdout.decode()
            
            # Parse básico das estatísticas
            stats = {
                "total_projects": 0,
                "total_tasks": 0, 
                "completed_tasks": 0,
                "active_projects": 0
            }
            
            # Tentar extrair números da saída
            import re
            numbers = re.findall(r'(\d+)', output)
            if len(numbers) >= 4:
                stats = {
                    "total_projects": int(numbers[0]),
                    "total_tasks": int(numbers[1]),
                    "completed_tasks": int(numbers[2]),
                    "active_projects": int(numbers[3]) if len(numbers) > 3 else 0
                }
            
            return {
                "status": "success",
                "stats": stats,
                "raw_output": output
            }
        else:
            raise HTTPException(status_code=500, detail=stderr.decode())
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/expand-all/{project_id}")
async def expand_all_tasks(project_id: int):
    """Expandir todas as tarefas de um projeto"""
    try:
        process = await asyncio.create_subprocess_exec(
            "python", "wastask.py", "task", "expand-all", str(project_id),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="."
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "status": "success",
                "message": "Tarefas expandidas com sucesso",
                "project_id": project_id,
                "output": stdout.decode()
            }
        else:
            raise HTTPException(status_code=500, detail=stderr.decode())
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)