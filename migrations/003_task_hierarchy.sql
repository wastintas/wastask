-- Migration: 003_task_hierarchy.sql
-- Description: Add task hierarchy support for task expansion
-- Created: 2025-07-01

-- Add hierarchy fields to tasks table
ALTER TABLE wastask_tasks 
ADD COLUMN IF NOT EXISTS parent_task_id INTEGER REFERENCES wastask_tasks(id) ON DELETE CASCADE,
ADD COLUMN IF NOT EXISTS expansion_level INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS is_expanded BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS original_estimate_hours INTEGER; -- Store original estimate before expansion

-- Add constraint to prevent circular references (a task cannot be parent of itself)
ALTER TABLE wastask_tasks 
ADD CONSTRAINT check_no_self_reference 
CHECK (parent_task_id != id);

-- Update original estimates for existing tasks (copy current estimate)
UPDATE wastask_tasks 
SET original_estimate_hours = estimated_hours 
WHERE original_estimate_hours IS NULL;

-- Add indexes for hierarchy queries
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_parent ON wastask_tasks(parent_task_id);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_expansion_level ON wastask_tasks(expansion_level);
CREATE INDEX IF NOT EXISTS idx_wastask_tasks_expanded ON wastask_tasks(is_expanded);

-- Add comments for documentation
COMMENT ON COLUMN wastask_tasks.parent_task_id IS 'Reference to parent task for hierarchy';
COMMENT ON COLUMN wastask_tasks.expansion_level IS '0=original, 1=first expansion, 2=second expansion, etc.';
COMMENT ON COLUMN wastask_tasks.is_expanded IS 'TRUE if this task has been broken down into subtasks';
COMMENT ON COLUMN wastask_tasks.original_estimate_hours IS 'Original estimate before any expansions';