-- WasTask Database Schema - Updated Version
-- Compatible with current WasTask analysis system

-- Drop existing incompatible tables if they exist
DROP TABLE IF EXISTS task_dependencies CASCADE;
DROP TABLE IF EXISTS task_tags CASCADE;
DROP TABLE IF EXISTS setup_commands CASCADE;
DROP TABLE IF EXISTS project_risks CASCADE;
DROP TABLE IF EXISTS clarification_questions CASCADE;
DROP TABLE IF EXISTS project_technologies CASCADE;
DROP TABLE IF EXISTS project_features CASCADE;

-- Create new analysis-compatible tables
CREATE TABLE IF NOT EXISTS wastask_projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    original_prd TEXT,
    enhanced_prd TEXT,
    prd_quality_before DECIMAL(3,1),
    prd_quality_after DECIMAL(3,1),
    complexity_score DECIMAL(3,1),
    timeline VARCHAR(100),
    total_hours INTEGER,
    package_manager VARCHAR(20) DEFAULT 'pnpm',
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de tecnologias recomendadas
CREATE TABLE IF NOT EXISTS wastask_project_technologies (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    category VARCHAR(100),
    technology VARCHAR(100),
    version VARCHAR(50),
    reason TEXT,
    confidence DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de features identificadas
CREATE TABLE IF NOT EXISTS wastask_project_features (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    complexity VARCHAR(20) DEFAULT 'MEDIUM',
    estimated_effort INTEGER DEFAULT 8,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de tarefas geradas
CREATE TABLE IF NOT EXISTS wastask_tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium',
    estimated_hours INTEGER DEFAULT 8,
    complexity VARCHAR(20) DEFAULT 'medium',
    category VARCHAR(100),
    status VARCHAR(50) DEFAULT 'todo',
    assigned_to VARCHAR(100),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de dependências entre tarefas
CREATE TABLE IF NOT EXISTS wastask_task_dependencies (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    depends_on_task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id)
);

-- Tabela de tags para tarefas
CREATE TABLE IF NOT EXISTS wastask_task_tags (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, tag)
);

-- Tabela de comandos de setup
CREATE TABLE IF NOT EXISTS wastask_setup_commands (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    command_type VARCHAR(50), -- 'setup', 'install', 'environment'
    command_text TEXT NOT NULL,
    execution_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de riscos identificados
CREATE TABLE IF NOT EXISTS wastask_project_risks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    risk_description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de questões de clarificação
CREATE TABLE IF NOT EXISTS wastask_clarification_questions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX IF NOT EXISTS idx_wastask_projects_status ON wastask_projects(status);
CREATE INDEX IF NOT EXISTS idx_wastask_projects_created_at ON wastask_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_project_id ON wastask_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_status ON wastask_tasks(status);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_priority ON wastask_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_wastask_project_technologies_project_id ON wastask_project_technologies(project_id);
CREATE INDEX IF NOT EXISTS idx_wastask_project_features_project_id ON wastask_project_features(project_id);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_wastask_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_wastask_projects_updated_at ON wastask_projects;
CREATE TRIGGER update_wastask_projects_updated_at BEFORE UPDATE ON wastask_projects
    FOR EACH ROW EXECUTE FUNCTION update_wastask_updated_at_column();

DROP TRIGGER IF EXISTS update_wastask_tasks_updated_at ON wastask_tasks;
CREATE TRIGGER update_wastask_tasks_updated_at BEFORE UPDATE ON wastask_tasks
    FOR EACH ROW EXECUTE FUNCTION update_wastask_updated_at_column();

-- Comentários para documentação
COMMENT ON TABLE wastask_projects IS 'Projetos analisados pelo WasTask';
COMMENT ON TABLE wastask_project_technologies IS 'Tecnologias recomendadas para cada projeto';
COMMENT ON TABLE wastask_project_features IS 'Features identificadas no PRD';
COMMENT ON TABLE wastask_tasks IS 'Tarefas geradas automaticamente';
COMMENT ON TABLE wastask_setup_commands IS 'Comandos de setup para o projeto';