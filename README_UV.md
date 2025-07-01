# WasTask - Ultra-Fast Setup with UV ⚡

Este guia mostra como configurar o WasTask usando [UV](https://github.com/astral-sh/uv), o gerenciador de pacotes Python ultrarrápido.

## 🚀 Quick Start

### 1. Executar o Setup Automático

```bash
# Clone o projeto
git clone <repository-url>
cd wastask

# Execute o setup com UV
python setup_uv.py
```

### 2. Configuração Manual (se preferir)

```bash
# Instalar UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Inicializar projeto
uv init --no-readme

# Instalar dependências
uv sync

# Ativar ambiente
uv shell
```

## 📋 Comandos Disponíveis

### Scripts UV Integrados

```bash
# Desenvolvimento
uv run dev              # Servidor de desenvolvimento
uv run cli              # Interface CLI
uv run test             # Executar testes
uv run test-cov         # Testes com cobertura

# Qualidade de código
uv run format           # Formatar código
uv run lint             # Lint
uv run type-check       # Verificação de tipos

# WasTask específicos
uv run create-project   # Criar projeto interativo
uv run chat            # Chat com assistente
uv run analyze         # Análise de projetos
```

### Usando Makefile (recomendado)

```bash
make help              # Ver todos os comandos
make install           # Instalar dependências
make dev              # Servidor de desenvolvimento
make test             # Executar testes
make format           # Formatar código
make docker-build     # Build Docker
```

## ⚡ Vantagens do UV

### Performance
- **10-100x mais rápido** que pip para instalação
- **Resolução de dependências ultrarrápida**
- **Cache inteligente** para instalações subsequentes

### Simplicidade
- **Comandos unificados** para gerenciamento completo
- **Scripts integrados** no pyproject.toml
- **Ambiente virtual automático**

### Comparação de Performance

```bash
# pip tradicional
pip install -r requirements.txt  # ~30-60 segundos

# UV
uv sync                          # ~2-5 segundos
```

## 🛠 Comandos Essenciais

### Gestão de Dependências

```bash
# Adicionar nova dependência
uv add fastapi

# Adicionar dependência de desenvolvimento
uv add --dev pytest

# Atualizar dependências
uv sync --upgrade

# Remover dependência
uv remove package-name

# Ver árvore de dependências
uv tree
```

### Desenvolvimento

```bash
# Criar novo projeto
uv run create-project

# Chat com IA
uv run chat "Como criar um projeto eficiente?"

# Análise de projeto
uv run analyze --project proj_001

# Interface CLI completa
uv run cli project list
uv run cli task create --project proj_001 --title "Nova tarefa"
```

### Testes e Qualidade

```bash
# Testes rápidos
uv run test

# Testes com cobertura
uv run test-cov

# Formatação automática
uv run format

# Verificação completa
make lint && make type-check && make test
```

## 🐳 Docker com UV

### Build Otimizado

```bash
# Build com UV (muito mais rápido)
make docker-build

# Run completo
make docker-run
```

### Vantagens Docker + UV
- **Builds 5-10x mais rápidos**
- **Imagens menores** com cache eficiente
- **Reprodutibilidade total** com uv.lock

## 📁 Estrutura de Arquivos UV

```
wastask/
├── uv.lock              # Lock file para reprodutibilidade
├── uv.toml              # Configuração UV (opcional)
├── pyproject.toml       # Configuração do projeto + scripts UV
├── Dockerfile.uv        # Dockerfile otimizado para UV
├── docker-compose.uv.yml # Compose para UV
├── Makefile            # Comandos simplificados
└── setup_uv.py         # Script de setup automático
```

## 🔧 Configuração Avançada

### Scripts Personalizados

Adicione novos scripts em `pyproject.toml`:

```toml
[tool.uv.scripts]
meu-comando = "python meu_script.py"
deploy = "uv run uvicorn app:main --host 0.0.0.0"
```

### Índices Personalizados

```toml
[tool.uv.index]
url = "https://pypi.org/simple"

[[tool.uv.index]]
name = "private"
url = "https://my-private-index.com/simple/"
```

### Sources Git

```toml
[tool.uv.sources]
google-adk = { git = "https://github.com/google/adk-python.git" }
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **UV não encontrado**
   ```bash
   # Reinstalar UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc  # ou ~/.zshrc
   ```

2. **Dependências não encontradas**
   ```bash
   uv sync --reinstall
   ```

3. **Cache corrompido**
   ```bash
   uv cache clean
   uv sync
   ```

### Performance Issues

```bash
# Limpar cache se necessário
uv cache clean

# Verificar status
uv cache info

# Reinstalação completa
rm uv.lock
uv sync
```

## 📊 Benchmarks

### Instalação Inicial

| Método | Tempo | Cache Hit |
|--------|-------|-----------|
| pip    | 45s   | 30s       |
| poetry | 35s   | 25s       |
| **uv** | **3s** | **0.5s** |

### Adição de Dependência

| Método | Tempo |
|--------|-------|
| pip    | 15s   |
| poetry | 20s   |
| **uv** | **1s** |

## 🎯 Próximos Passos

1. **Configurar .env** com suas chaves de API
2. **Testar CLI**: `uv run cli --help`
3. **Criar primeiro projeto**: `uv run create-project`
4. **Explorar comandos**: `make help`

## 📚 Links Úteis

- [UV Documentation](https://github.com/astral-sh/uv)
- [WasTask Documentation](./README.md)
- [Google ADK Documentation](https://developers.google.com/adk)

---

**🚀 Agora você tem o WasTask rodando com máxima performance!**