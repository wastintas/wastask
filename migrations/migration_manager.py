#!/usr/bin/env python3
"""
WasTask Migration Manager
Sistema de controle de versão para o banco de dados
"""
import asyncio
import asyncpg
import os
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

class MigrationManager:
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or "postgresql://wastask:password@localhost:5433/wastask"
        self.migrations_dir = Path(__file__).parent
        self.pool = None
    
    async def initialize(self):
        """Inicializar conexão e tabela de migrations"""
        self.pool = await asyncpg.create_pool(self.connection_string)
        await self._create_migrations_table()
    
    async def close(self):
        """Fechar conexões"""
        if self.pool:
            await self.pool.close()
    
    async def _create_migrations_table(self):
        """Criar tabela para controlar migrations executadas"""
        query = """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            checksum VARCHAR(64)
        )
        """
        async with self.pool.acquire() as conn:
            await conn.execute(query)
    
    async def get_executed_migrations(self) -> List[str]:
        """Listar migrations já executadas"""
        query = "SELECT migration_name FROM schema_migrations ORDER BY migration_name"
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [row['migration_name'] for row in rows]
    
    def get_available_migrations(self) -> List[Tuple[str, Path]]:
        """Listar migrations disponíveis no diretório"""
        migrations = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            if file.name != "migration_manager.py":
                migrations.append((file.stem, file))
        return migrations
    
    def _calculate_checksum(self, content: str) -> str:
        """Calcular checksum do conteúdo da migration"""
        import hashlib
        return hashlib.sha256(content.encode()).hexdigest()
    
    async def execute_migration(self, migration_name: str, migration_path: Path):
        """Executar uma migration específica"""
        content = migration_path.read_text(encoding='utf-8')
        checksum = self._calculate_checksum(content)
        
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # Executar SQL da migration
                await conn.execute(content)
                
                # Registrar execução
                await conn.execute(
                    "INSERT INTO schema_migrations (migration_name, checksum) VALUES ($1, $2)",
                    migration_name, checksum
                )
        
        print(f"✅ Migration executed: {migration_name}")
    
    async def migrate(self):
        """Executar todas as migrations pendentes"""
        executed = await self.get_executed_migrations()
        available = self.get_available_migrations()
        
        pending = [(name, path) for name, path in available if name not in executed]
        
        if not pending:
            print("✅ No pending migrations")
            return
        
        print(f"🔄 Executing {len(pending)} pending migrations...")
        
        for migration_name, migration_path in pending:
            try:
                await self.execute_migration(migration_name, migration_path)
            except Exception as e:
                print(f"❌ Migration failed: {migration_name}")
                print(f"   Error: {e}")
                raise
        
        print(f"✅ All migrations completed successfully!")
    
    async def rollback(self, target_migration: str = None):
        """Rollback migrations (placeholder - implementar conforme necessário)"""
        print("⚠️ Rollback functionality not implemented yet")
        print("   For now, use manual SQL scripts for rollbacks")
    
    async def status(self):
        """Mostrar status das migrations"""
        executed = await self.get_executed_migrations()
        available = self.get_available_migrations()
        
        print("📊 Migration Status")
        print("=" * 50)
        
        for migration_name, migration_path in available:
            status = "✅ EXECUTED" if migration_name in executed else "⏳ PENDING"
            print(f"{status} {migration_name}")
        
        pending_count = len([name for name, _ in available if name not in executed])
        print(f"\n📋 Summary: {len(executed)} executed, {pending_count} pending")

async def main():
    """CLI para o migration manager"""
    import sys
    
    if len(sys.argv) < 2:
        print("""
🔄 WasTask Migration Manager

Usage:
  python migration_manager.py <command>

Commands:
  migrate  - Execute all pending migrations
  status   - Show migration status
  rollback - Rollback migrations (not implemented)

Examples:
  python migration_manager.py migrate
  python migration_manager.py status
""")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    manager = MigrationManager()
    
    try:
        await manager.initialize()
        
        if command == "migrate":
            await manager.migrate()
        elif command == "status":
            await manager.status()
        elif command == "rollback":
            await manager.rollback()
        else:
            print(f"❌ Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    finally:
        await manager.close()

if __name__ == '__main__':
    asyncio.run(main())