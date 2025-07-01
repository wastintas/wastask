#!/usr/bin/env python3
"""
Teste do modo interativo real - simular escolhas do usuário
"""
import subprocess
import sys

def test_interactive_mode():
    """Testar modo interativo com entradas simuladas"""
    
    print("🧪 Testando WasTask Modo Interativo")
    print("=" * 50)
    print()
    
    # Simular entrada do usuário: 1 (React Router v7) e 1 (pnpm)
    inputs = "1\n1\n"
    
    try:
        # Executar com entrada simulada
        result = subprocess.run([
            sys.executable, 
            "wastask_simple.py", 
            "bling_integration_prd.md", 
            "--verbose"
        ], 
        input=inputs, 
        text=True, 
        capture_output=True,
        timeout=30
        )
        
        print("📋 Output do WasTask:")
        print("-" * 30)
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Warnings/Errors:")
            print(result.stderr)
            
        print("-" * 30)
        print(f"✅ Exit code: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - o processo demorou muito")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_interactive_mode()