from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from src.config.settings import settings
from src.infrastructure.postgresql.connection_database import ConnectionDatabase


class ConnectPostgreSQL(ConnectionDatabase):

    def __init__(self):
        connection_string = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        self.engine: Engine = create_engine(connection_string, echo=False, future=True)
        self.conn: Connection | None = None
        self._session_factory = sessionmaker(bind=self.engine)

    def connect(self):
        try:
            self.conn = self.engine.connect()
            return self.conn
        except SQLAlchemyError as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return None

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params: dict = None):
        if not self.conn:
            self.connect()
        try:
            if params is None:
                params = {}
            result = self.conn.execute(text(query), params)
            self.conn.commit()
            return result
        except SQLAlchemyError as e:
            print(f"Erro ao executar query: {e}")
            return None

    def fetch_all(self, query: str, params: dict = None):
        result = self.execute_query(query, params)
        if result:
            return result.fetchall()
        return []

    def test_connection(self) -> bool:
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            print(f"Falha no teste de conexão: {e}")
            return False

    def get_session(self):
        return self._session_factory()
