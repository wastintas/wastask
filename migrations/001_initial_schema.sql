-- Migration: 001_initial_schema.sql
-- Description: Create initial WasTask database schema
-- Created: 2025-07-01

-- Create projects table
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

-- Create project technologies table
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

-- Create project features table
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

-- Create tasks table
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

-- Create task dependencies table
CREATE TABLE IF NOT EXISTS wastask_task_dependencies (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    depends_on_task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, depends_on_task_id)
);

-- Create task tags table
CREATE TABLE IF NOT EXISTS wastask_task_tags (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(task_id, tag)
);

-- Create setup commands table
CREATE TABLE IF NOT EXISTS wastask_setup_commands (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    command_type VARCHAR(50),
    command_text TEXT NOT NULL,
    execution_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create project risks table
CREATE TABLE IF NOT EXISTS wastask_project_risks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    risk_description TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create clarification questions table
CREATE TABLE IF NOT EXISTS wastask_clarification_questions (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES wastask_projects(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_wastask_projects_status ON wastask_projects(status);
CREATE INDEX IF NOT EXISTS idx_wastask_projects_created_at ON wastask_projects(created_at);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_project_id ON wastask_tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_status ON wastask_tasks(status);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_priority ON wastask_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_wastask_project_technologies_project_id ON wastask_project_technologies(project_id);
CREATE INDEX IF NOT EXISTS idx_wastask_project_features_project_id ON wastask_project_features(project_id);