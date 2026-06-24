Gera testes unitários para um módulo do projeto backoffice-saas-agents.

## Argumento

O usuário passa o alvo do teste. Exemplos:
- `src/service/document_service.py`
- `src/usecase/document_usecase.py`

Se não passou argumento, pergunte qual arquivo ou função deseja testar.

## Antes de escrever qualquer teste

1. Leia o arquivo alvo por completo
2. Identifique a camada: `controller`, `usecase`, `service` ou `infrastructure`
3. Leia as dependências diretas (o que o arquivo importa e chama)
4. Verifique se já existe `tests/test_{domínio}.py` — se sim, leia para seguir o padrão de fixtures

## O que testar por camada

### `service/`
- **Happy path** — entrada válida, retorno esperado
- **Erros de SDK/cliente** — mocke o cliente da infrastructure para lançar exceção
- Mock: `Connection{Domínio}.connect()` retornando `MagicMock()`

### `usecase/`
- **Happy path** — serviços retornam valores esperados, usecase orquestra corretamente
- **Falha em etapa intermediária** — um dos serviços lança exceção
- Mock: todas as funções de service importadas no usecase

### `controller/api/`
- Use `TestClient` do FastAPI
- **Happy path** — upload de arquivo válido, retorna JSON esperado
- **Tipo inválido** — `content_type` errado retorna HTTP 415
- **Erro interno** — usecase lança exceção, retorna HTTP 500
- Mock: a função de usecase chamada pelo endpoint

## Padrões obrigatórios

### Estrutura do arquivo de teste

```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

class TestNomeDaClasse:
    @pytest.fixture
    def mock_client(self):
        return MagicMock()

    def test_método_happy_path(self, mock_client):
        with patch("src.service.{domínio}_service.Connection{Domínio}.connect", return_value=mock_client):
            mock_client.some_method.return_value = {"result": "ok"}
            result = some_function(input)
        assert result["field"] == expected_value

    def test_método_raises_on_client_error(self, mock_client):
        with patch("src.service.{domínio}_service.Connection{Domínio}.connect", return_value=mock_client):
            mock_client.some_method.side_effect = Exception("SDK error")
            with pytest.raises(Exception):
                some_function(input)
```

### Regras

- Use `AsyncMock` para dependências async, `MagicMock` para síncronas
- Nunca acesse serviços externos reais — mocke a infrastructure
- Um `assert` por comportamento — não empilhe múltiplos asserts em um único teste
- Nomes de teste descrevem o comportamento: `test_classify_raises_when_client_fails`
- Use `pytest.mark.asyncio` ou configure `asyncio_mode = "auto"` no `pyproject.toml`

## Após gerar os testes

Execute para confirmar que passam:

```bash
pytest tests/test_{domínio}.py -v --tb=short
```

Se algum falhar, corrija antes de entregar.
