from abc import ABC, abstractmethod


class ConnectionDatabase(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute_query(self, query: str, params: dict = None):
        pass

    @abstractmethod
    def fetch_all(self, query: str, params: dict = None):
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        pass

    @abstractmethod
    def get_session(self):
        pass
