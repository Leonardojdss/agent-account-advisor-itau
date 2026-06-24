import json
import logging
import re

from langchain_core.tools import tool

from src.infrastructure.postgresql.connection_database_factory import ConnectionDatabaseFactory

logger = logging.getLogger(__name__)

FORBIDDEN_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXEC|EXECUTE)\b",
    re.IGNORECASE,
)


def _validate_select_only(query: str) -> None:
    stripped = query.strip().rstrip(";").strip()
    if not stripped.upper().startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    if FORBIDDEN_PATTERNS.search(stripped):
        raise ValueError("Forbidden SQL keyword detected. Only SELECT queries are allowed.")


@tool
def search_database_schema(query: str = "", limit: int = 10) -> str:
    """Search the database schema (tables, columns, types) to understand table structures.
    Use this tool FIRST before writing SELECT queries.

    Args:
        query: Optional filter for table or column name (substring match)
        limit: Maximum number of results to return
    """
    logger.info("[Tool:Schema] Consultando schema do banco - filtro='%s' | limit=%d", query, limit)

    db = ConnectionDatabaseFactory.create_connection_database("postgresql")
    schema_query = """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
    """
    params: dict = {}
    if query:
        schema_query += " AND (table_name ILIKE :filter OR column_name ILIKE :filter)"
        params["filter"] = f"%{query}%"
    schema_query += " ORDER BY table_name, ordinal_position LIMIT :limit"
    params["limit"] = limit

    try:
        rows = db.fetch_all(schema_query, params)
        if not rows:
            logger.info("[Tool:Schema] Nenhum resultado encontrado.")
            return "No schema information found matching the query."
        logger.info("[Tool:Schema] %d colunas encontradas.", len(rows))
        result_lines = ["TABLE | COLUMN | TYPE | NULLABLE"]
        for row in rows:
            result_lines.append(f"{row[0]} | {row[1]} | {row[2]} | {row[3]}")
        return "\n".join(result_lines)
    except Exception as e:
        logger.error("[Tool:Schema] Erro ao consultar schema: %s", e)
        return f"Error querying schema: {e}"
    finally:
        db.close()


@tool
def select_database(query: str, params: str = "{}") -> str:
    """Execute a SELECT query against the banking database.
    ONLY SELECT statements are allowed. Any write operation will be rejected.

    Args:
        query: A valid SQL SELECT statement
        params: JSON string of query parameters (optional)
    """
    logger.info("[Tool:Select] Query recebida: '%s'", query[:120])

    try:
        _validate_select_only(query)
    except ValueError as e:
        logger.warning("[Tool:Select] Query BLOQUEADA: %s", e)
        return f"BLOCKED: {e}"

    try:
        query_params = json.loads(params) if params else {}
    except json.JSONDecodeError:
        query_params = {}

    db = ConnectionDatabaseFactory.create_connection_database("postgresql")
    try:
        rows = db.fetch_all(query, query_params)
        if not rows:
            logger.info("[Tool:Select] Query retornou 0 resultados.")
            return "Query returned no results."
        logger.info("[Tool:Select] Query retornou %d linha(s).", len(rows))
        result_lines = []
        for row in rows:
            result_lines.append(" | ".join(str(col) for col in row))
        return f"Results ({len(rows)} rows):\n" + "\n".join(result_lines)
    except Exception as e:
        logger.error("[Tool:Select] Erro na execução da query: %s", e)
        return f"Database error: {e}"
    finally:
        db.close()
