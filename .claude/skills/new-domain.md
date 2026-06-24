Scaffolda um módulo completo de domínio para o projeto backoffice-saas-agents seguindo a arquitetura em 4 camadas (Clean Architecture).

## Argumento

O usuário passa o nome do domínio como argumento. Exemplos: `document`, `billing`, `user`, `subscription`.

Se o argumento não foi fornecido, pergunte o nome do domínio antes de continuar.

## O que criar

Crie os seguintes arquivos dentro de `src/`:

### `infrastructure/connection_{domínio}.py`

- Classe `Connection{Domínio}` com método estático `connect()`
- Carrega credenciais via `os.getenv()` com `load_dotenv()`
- Valida que as variáveis de ambiente não são `None` com `raise ValueError`
- Retorna o cliente configurado (SDK, requests session, DB client, etc.)

### `service/{domínio}_service.py`

- Funções ou classe com a lógica de domínio
- Usa `Connection{Domínio}.connect()` para obter o cliente
- Cada função tem um propósito único (ex: `classify_service`, `ocr_service`)
- Adiciona `logging.info()` para resultados relevantes
- Não sabe de HTTP nem de usecases

### `usecase/{domínio}_usecase.py`

- Função `{domínio}_usecase(...)` que orquestra os serviços
- Chama os métodos do service na ordem correta
- Adiciona `logging.info()` após cada etapa importante
- Retorna os dados necessários para o controller (não objetos HTTP)

### `controller/api/{domínio}_route.py`

- `APIRouter` com `prefix="/{domínio}"` e `tags=["{Domínio}"]`
- Endpoint principal `POST /` para processamento
- Validação de `content_type` com HTTP 415 para tipos não suportados
- Gerenciamento de arquivo temporário com `tempfile` + `aiofiles`
- Limpeza do arquivo temporário no bloco `finally`
- Resposta com campos relevantes do resultado
- Tratamento de exceções com HTTP 500

### Registrar em `src/main.py`

- Importar o router criado
- `app.include_router(router, prefix="/{domínio}", tags=["{Domínio}"])`

## Exemplo de estrutura gerada para domínio `document`

```
src/
├── main.py                                    ← atualizado
├── controller/api/document_route.py           ← novo
├── usecase/document_usecase.py                ← novo
├── service/document_service.py                ← novo
└── infrastructure/connection_document.py      ← novo
```

## Após criar os arquivos

1. Informe o usuário dos arquivos criados
2. Liste as variáveis de ambiente necessárias no `.env`
3. Lembre que é preciso:
   - Executar `/check` para validar tipos e testes
   - Adicionar as variáveis de ambiente no `.env` e `.env.example`
