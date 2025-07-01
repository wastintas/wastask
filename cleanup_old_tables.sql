-- WasTask Database Cleanup Script
-- Remove old orphaned tables that are not compatible with current system

-- Drop old tables (UUID-based with ENUMs)
DROP TABLE IF EXISTS conversas CASCADE;
DROP TABLE IF EXISTS tasks CASCADE;  -- Old tasks table with UUID
DROP TABLE IF EXISTS projects CASCADE; -- Old projects table with UUID

-- Drop old ENUMs if they exist
DROP TYPE IF EXISTS projectstatus CASCADE;
DROP TYPE IF EXISTS taskstatus CASCADE;
DROP TYPE IF EXISTS taskpriority CASCADE;

-- Drop old functions if they exist
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;

-- Verify cleanup - show remaining tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE'
ORDER BY table_name;