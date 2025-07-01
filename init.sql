-- WasTask Database Initialization
-- Criação do banco e configurações iniciais

-- Extensões do PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar usuário administrador se não existir
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'wastask_admin') THEN
        CREATE ROLE wastask_admin WITH LOGIN PASSWORD 'admin123';
    END IF;
END
$$;

-- Dar permissões
GRANT ALL PRIVILEGES ON DATABASE wastask TO wastask_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wastask_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO wastask_admin;

-- Comentários nas tabelas (serão criadas pelo SQLAlchemy)
COMMENT ON SCHEMA public IS 'WasTask - Sistema de Gestão de Projetos com IA';

-- Configurações de performance
ALTER DATABASE wastask SET timezone TO 'UTC';
ALTER DATABASE wastask SET log_statement TO 'all';
ALTER DATABASE wastask SET log_min_duration_statement TO 1000;