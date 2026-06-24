from src.infrastructure.postgresql.connection_database import ConnectionDatabase
from src.infrastructure.postgresql.connection import ConnectPostgreSQL


class ConnectionDatabaseFactory:
    _registry: dict[str, type[ConnectionDatabase]] = {
        "postgresql": ConnectPostgreSQL,
    }

    @staticmethod
    def create_connection_database(database: str = "postgresql", **kwargs) -> ConnectionDatabase:
        cls = ConnectionDatabaseFactory._registry.get(database)
        if cls is None:
            raise ValueError(f"type of database '{database}' not supported")
        return cls(**kwargs)
