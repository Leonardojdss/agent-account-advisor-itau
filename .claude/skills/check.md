Executa o pipeline de qualidade completo do projeto backoffice-saas-agents e exibe um resumo dos resultados.

## Passos em ordem

### 1. Formatação

```bash
ruff format --check .
```

Se falhar, pergunte ao usuário se quer aplicar a formatação automaticamente (`ruff format .`).

### 2. Linting

```bash
ruff check .
```

Mostre apenas os erros — não os warnings de estilo já corrigíveis com `--fix`.

Se houver erros corrigíveis automaticamente, pergunte se quer aplicar (`ruff check --fix .`).

### 3. Verificação de tipos

```bash
mypy src/ --ignore-missing-imports
```

Agrupe os erros por arquivo. Destaque erros de tipo em funções async e nas camadas `service` e `infrastructure`, pois são os mais comuns de falso negativo.

### 4. Testes com cobertura

```bash
pytest tests/ -v --tb=short --cov=src --cov-report=term-missing
```

### 5. Resumo final

Exiba uma tabela com o status de cada etapa:

| Etapa       | Status | Detalhes |
|-------------|--------|----------|
| Formatação  | ✓ / ✗  | ...      |
| Linting     | ✓ / ✗  | N erros  |
| Tipos       | ✓ / ✗  | N erros  |
| Testes      | ✓ / ✗  | N/N passaram, X% cobertura |

Se todos passarem: informe que o código está pronto para commit.
Se algum falhar: liste os erros críticos e sugira a ordem de correção (tipos > lint > testes).
