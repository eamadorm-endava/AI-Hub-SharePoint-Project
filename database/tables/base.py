from abc import ABC, abstractmethod


class Table(ABC):
    @abstractmethod
    def _generate_id(self, **kargs) -> str:
        pass

    @abstractmethod
    def _id_in_table(self, **kargs) -> bool:
        pass

    @abstractmethod
    def _insert_row(self, **kargs) -> str:
        """
        Main logic to insert a row in the table database
        """
        pass

    @abstractmethod
    def add_row(self, **kargs) -> any:
        """
        Orchestrator Function to insert a row in the table database. It might include
        other steps such as _generate_id, _id_in_table, and other helper functions
        """
        pass
