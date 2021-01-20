from abc import ABC, abstractmethod
from typing import Any, Optional


class ICommand(ABC):
    @abstractmethod
    def execute(self, check: bool = True) -> Any:
        pass


class IDatabase(ABC):
    @abstractmethod
    def get_path(self) -> str:
        pass

    @abstractmethod
    def has_password(self) -> bool:
        pass

    @abstractmethod
    def get_password(self) -> Optional[str]:
        pass

    @abstractmethod
    def has_key_file(self) -> bool:
        pass

    @abstractmethod
    def get_key_file(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """

        :return:
        """
        pass

    @abstractmethod
    def export(self, format: str = None) -> str:
        """
        Exports the content of a database in the specified format.
        WARNING: Passwords are extracted in plaintext!

        :param format: The output format ('xml' or 'csv')
        :return:
        """
        pass

    @abstractmethod
    def export_to(self, target_path: str, format: str = 'xml'):
        """
        Exports the content of a database in the specified format and writes it to a file.
        WARNING: Passwords are extracted in plaintext!

        :param target_path:
        :param format: The output format ('xml' or 'csv')
        """
        pass

    @abstractmethod
    def copy_to(self, target_path: str):
        """
        Copy the database file to another location.

        :param target_path:
        """
        pass
