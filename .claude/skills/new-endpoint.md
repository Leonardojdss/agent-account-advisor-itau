Adiciona um novo endpoint a um router FastAPI existente no projeto backoffice-saas-agents.

## Argumentos esperados

O usuário pode passar: `{domínio} {método} {path} [descrição]`

Exemplos:
- `document GET /documents/{id}/summary Retorna resumo do documento`
- `user POST /users/{id}/deactivate Desativa uma conta`

Se algum argumento estiver faltando, pergunte antes de continuar.

## O que fazer

1. **Leia o controller existente** em `src/controller/api/{domínio}_route.py` para entender os padrões usados
2. **Leia o usecase** em `src/usecase/{domínio}_usecase.py` para entender o fluxo atual
3. **Leia o service** em `src/service/{domínio}_service.py` para entender os métodos disponíveis

### Adicione o método no service (se necessário)

Em `src/service/{domínio}_service.py`:
- Implemente a lógica de negócio do novo endpoint
- Use a infraestrutura em `src/infrastructure/` para conexões externas
- Não acesse HTTP nem usecase — apenas lógica de domínio

### Adicione ou atualize o usecase

Em `src/usecase/{domínio}_usecase.py`:
- Orquestre os serviços necessários para o novo fluxo
- Adicione `logging.info()` nos pontos de resultado intermediário
- Não retorne objetos HTTP — retorne dados puros

### Adicione o endpoint no controller

Em `src/controller/api/{domínio}_route.py`:
- Insira o endpoint na posição lógica (agrupe por recurso)
- Valide `content_type` quando receber arquivos (retorne HTTP 415 se inválido)
- Gerencie arquivos temporários com `tempfile` + `aiofiles` + limpeza no `finally`
- Use `response_model`, `status_code` correto
- Trate exceções com `HTTPException` e retorne HTTP 500 para erros inesperados

### Adicione o teste

Em `tests/test_{domínio}.py`:
- Teste o happy path
- Teste pelo menos um caso de erro (415, 404, 500)

## Após as alterações

Informe: arquivos modificados, se adicionou novo serviço ou usecase, e se há dependência de nova variável de ambiente.
