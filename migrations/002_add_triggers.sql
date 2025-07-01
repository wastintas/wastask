-- Migration: 002_add_triggers.sql
-- Description: Add triggers for automatic timestamp updates
-- Created: 2025-07-01

-- Create function for updating timestamps
CREATE OR REPLACE FUNCTION update_wastask_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for projects table
DROP TRIGGER IF EXISTS update_wastask_projects_updated_at ON wastask_projects;
CREATE TRIGGER update_wastask_projects_updated_at 
    BEFORE UPDATE ON wastask_projects
    FOR EACH ROW 
    EXECUTE FUNCTION update_wastask_updated_at_column();

-- Add triggers for tasks table
DROP TRIGGER IF EXISTS update_wastask_tasks_updated_at ON wastask_tasks;
CREATE TRIGGER update_wastask_tasks_updated_at 
    BEFORE UPDATE ON wastask_tasks
    FOR EACH ROW 
    EXECUTE FUNCTION update_wastask_updated_at_column();