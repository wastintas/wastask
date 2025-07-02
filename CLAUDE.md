# Wastask - Referência Rápida para Claude

## Localização
- **Path**: `/Volumes/www/tmp/adk/wastask`
- **Executar com**: `uv run python [comando]`

## Comandos Principais

### 1. Analisar PRD
```bash
# Análise interativa
printf "1\n1\n" | uv run python wastask_simple.py docs/arquivo.md

# Salvar em JSON
printf "1\n1\n" | uv run python wastask.py prd analyze docs/arquivo.md --output json --no-interactive
```

### 2. Gerenciar Tarefas
```bash
# Ver árvore de tarefas
uv run python wastask.py task tree [project_id]

# Expandir uma tarefa
uv run python wastask.py task expand [task_id]

# Expandir todas
uv run python wastask.py task expand-all [project_id]
```

### 3. Banco de Dados
```bash
# Ver projetos
uv run python wastask.py db list

# Detalhes do projeto
uv run python wastask.py db show [project_id]

# Estatísticas
uv run python wastask.py db stats
```

## Processo de Expansão Manual

Quando litellm não estiver disponível, eu (Claude) posso gerar as subtarefas:

1. **Identificar tarefa para expandir**:
   - Tarefas com >8 horas
   - Tarefas com complexidade "high"
   - Tarefas com palavras-chave: implement, develop, create, build

2. **Gerar JSON de subtarefas**:
```json
[
  {
    "title": "Ação específica",
    "description": "Descrição detalhada",
    "estimated_hours": 2-4,
    "complexity": "low|medium|high",
    "priority": "high|medium|low",
    "category": "backend|frontend|database|testing",
    "depends_on": []
  }
]
```

3. **Inserir no banco**:
```bash
# Criar arquivo JSON com subtarefas
# Executar: uv run python insert_subtasks.py
```

## Critérios de Qualidade

### Para PRDs (0-10):
- Objetivos claros
- Escopo definido
- Requisitos técnicos
- Casos de uso
- Critérios de aceitação

### Para Tarefas:
- Título específico e acionável
- Estimativa realista (1-8h)
- Categoria apropriada
- Dependências identificadas
- Testável e mensurável

## Stack Padrão Recomendada
- Frontend: React Router v7 + Shadcn/ui
- Backend: Node.js + Express
- Database: PostgreSQL + Drizzle ORM
- Validação: Zod
- Testes: Vitest + Playwright
- Deploy: Docker

## Notas Importantes
1. Sempre use `pnpm` como gerenciador de pacotes
2. O banco PostgreSQL precisa estar rodando
3. As análises são salvas como `[nome_projeto]_analysis.json`
4. Tarefas expandidas são marcadas com 📂
5. Subtarefas têm expansion_level > 0