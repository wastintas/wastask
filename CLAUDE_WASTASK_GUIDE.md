# Guia para Instruir o Claude a Usar o Wastask

## 🚀 Instruções Básicas

### 1. Análise de PRD
```
"Analise este PRD usando o Wastask: [caminho/para/prd.md]"
"Use o Wastask para avaliar a qualidade deste PRD e gerar tarefas"
```

**O que o Claude fará:**
```bash
printf "1\n1\n" | uv run python wastask_simple.py [arquivo_prd]
```

### 2. Expandir Tarefas Complexas
```
"Expanda as tarefas complexas do projeto X usando o Wastask"
"Quebre a tarefa Y em subtarefas menores"
```

**O que o Claude fará:**
1. Identificar tarefas com >8 horas ou alta complexidade
2. Gerar subtarefas apropriadas (3-7 por tarefa)
3. Inserir no banco de dados

### 3. Gerar Código Automático
```
"Use o Wastask para gerar código para a tarefa Z"
"Implemente a funcionalidade X usando o code generator do Wastask"
```

## 📋 Comandos Prontos para Copiar

### Análise Completa de PRD
```
Por favor:
1. Use o Wastask para analisar o arquivo docs/meu_prd.md
2. Salve a análise em JSON
3. Mostre um resumo das tarefas geradas
4. Identifique tarefas que precisam ser expandidas
```

### Expansão Inteligente de Tarefas
```
Por favor:
1. Liste as tarefas do projeto que podem ser expandidas
2. Para cada tarefa >8h, gere subtarefas detalhadas
3. Cada subtarefa deve ter 1-4 horas
4. Insira as subtarefas no banco
```

### Geração de Código
```
Por favor:
1. Selecione uma tarefa específica para implementar
2. Use o contexto do projeto para gerar código
3. Aplique os quality gates (lint, test, build)
4. Mostre o código gerado
```

## 🎯 Melhores Práticas

### 1. Seja Específico com o Contexto
```
"Analise o PRD do sistema de e-commerce focando em:
- Integração com pagamentos
- Gestão de estoque
- Use React + Node.js como stack"
```

### 2. Defina Critérios Claros
```
"Ao expandir tarefas:
- Máximo 4 horas por subtarefa
- Foque em implementação, não documentação
- Mantenha a mesma stack tecnológica"
```

### 3. Peça Validações
```
"Após gerar as tarefas:
- Verifique se todas têm estimativas realistas
- Confirme que as dependências estão corretas
- Valide a complexidade atribuída"
```

## 🔧 Fluxos Completos

### Fluxo 1: PRD → Projeto Completo
```
1. "Analise o PRD usando Wastask"
2. "Salve no banco de dados"
3. "Expanda todas as tarefas complexas"
4. "Gere os comandos de setup do projeto"
5. "Crie a estrutura inicial do código"
```

### Fluxo 2: Tarefa → Implementação
```
1. "Selecione a tarefa de autenticação"
2. "Expanda em subtarefas técnicas"
3. "Gere o código para cada subtarefa"
4. "Execute os testes"
5. "Prepare o commit"
```

## 💡 Dicas Avançadas

### Customização de Análise
```
"Configure o Wastask para:
- Preferir tarefas menores (2-4h)
- Usar TypeScript strict mode
- Incluir testes em cada tarefa"
```

### Integração com Workflow
```
"Ao analisar PRDs:
1. Sempre gere issues do GitHub
2. Crie um board de projeto
3. Estime sprints de 2 semanas"
```

### Modo Interativo
```
"Vamos trabalhar juntos:
1. Você analisa o PRD
2. Eu reviso as tarefas
3. Você ajusta baseado no meu feedback
4. Repetimos até ficar perfeito"
```

## ⚡ Comandos Rápidos

- **Análise rápida**: "wastask analyze [arquivo]"
- **Ver tarefas**: "wastask task tree [project_id]"
- **Expandir tudo**: "wastask expand-all [project_id]"
- **Status geral**: "wastask db stats"

## 🤖 Prompt Mágico Completo

```
Você é um especialista em gestão de projetos usando o Wastask. Por favor:

1. Analise o PRD em [caminho/arquivo.md]
2. Use o Wastask para:
   - Avaliar qualidade (meta: 8+/10)
   - Gerar 30-50 tarefas organizadas
   - Estimar 4-12 semanas de trabalho
3. Para cada tarefa >8h:
   - Expanda em 3-5 subtarefas
   - Cada subtarefa: 2-4 horas
   - Mantenha dependências claras
4. Gere comandos de setup para:
   - Ambiente de desenvolvimento
   - Estrutura do projeto
   - Dependências necessárias
5. Prepare para implementação:
   - Ordene por prioridade
   - Agrupe em sprints
   - Identifique caminho crítico

Mostre um resumo executivo ao final.
```

## 📊 Monitoramento

### Verificar Progresso
```
"Mostre:
- Total de tarefas criadas vs completadas
- Tarefas expandidas vs pendentes
- Estimativa de horas restantes
- Próximos passos recomendados"
```

### Relatório de Qualidade
```
"Gere um relatório mostrando:
- Qualidade do PRD original vs melhorado
- Cobertura de funcionalidades
- Riscos identificados
- Recomendações técnicas"
```

## 🎓 Exemplos de Sucesso

### Exemplo 1: PRD Simples
```
User: "Analise o PRD do sistema de blog usando Wastask"
Claude: [Executa análise, gera 15 tarefas, estima 3 semanas]
User: "Expanda a tarefa de comentários"
Claude: [Gera 4 subtarefas específicas de 2-3h cada]
```

### Exemplo 2: Sistema Complexo
```
User: "Use o Wastask no PRD do e-commerce completo"
Claude: [Analisa, melhora PRD de 7→9/10, gera 45 tarefas]
User: "Foque primeiro no módulo de pagamentos"
Claude: [Filtra 8 tarefas de pagamento, expande cada uma]
```

---

## 🚨 Lembre-se Sempre

1. **O Wastask já está instalado** em `/Volumes/www/tmp/adk/wastask`
2. **Use `uv run`** para executar comandos Python
3. **O banco PostgreSQL** deve estar rodando
4. **Eu (Claude) posso gerar** subtarefas e código diretamente
5. **Salve análises importantes** em JSON para reusar

Este guia está salvo em: `/Volumes/www/tmp/adk/wastask/CLAUDE_WASTASK_GUIDE.md`