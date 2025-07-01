-- Create users table for authentication
CREATE TABLE IF NOT EXISTS wastask_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_wastask_users_username ON wastask_users(username);
CREATE INDEX IF NOT EXISTS idx_wastask_users_email ON wastask_users(email);
CREATE INDEX IF NOT EXISTS idx_wastask_users_active ON wastask_users(is_active);

-- Create trigger to update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_wastask_users_updated_at 
    BEFORE UPDATE ON wastask_users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default admin user (password: admin123)
INSERT INTO wastask_users (username, email, hashed_password, full_name, is_admin)
VALUES (
    'admin',
    'admin@wastask.ai',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
    'WasTask Administrator',
    TRUE
) ON CONFLICT (username) DO NOTHING;