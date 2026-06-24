Gera e valida uma migration Alembic para o projeto backoffice-saas-agents.

## Argumento

O usuário pode passar uma descrição curta da migration. Exemplo: `add subscription table` ou `add index to tenant email`.

Se não passou, derive a descrição a partir das mudanças detectadas nos modelos.

## Passos a executar

### 1. Verifique o estado atual

```bash
git diff src/ --name-only
```

Identifique quais arquivos `models.py` ou de infraestrutura foram alterados.

### 2. Gere a migration

```bash
alembic revision --autogenerate -m "{descrição}"
```

### 3. Inspecione o arquivo gerado

Leia o arquivo criado em `alembic/versions/` e verifique:
- O `upgrade()` contém todas as mudanças esperadas
- O `downgrade()` está implementado e é o inverso correto
- Não há operações destrutivas inesperadas (ex: `drop_table` quando só era esperado `add_column`)
- Tipos de coluna estão corretos para o banco alvo

### 4. Reporte ao usuário

Mostre:
- Caminho do arquivo gerado
- Conteúdo das funções `upgrade()` e `downgrade()`
- Qualquer divergência entre o esperado e o gerado

### 5. Aplique somente após confirmação

Só execute `alembic upgrade head` **após confirmação explícita do usuário**.

## Erros comuns a verificar

- `autogenerate` não detecta mudanças → verificar se `target_metadata = Base.metadata` está no `alembic/env.py` e se o modelo importa a `Base` correta
- Colunas `server_default` geradas como `sa.text()` → ajustar manualmente se necessário
- Índices duplicados → checar se o índice já existe em migration anterior
