from abc import ABC, abstractmethod
from typing import Any, Union, Optional, List
import command


class ICommand(ABC):
    @abstractmethod
    def execute(self, check: bool = True) -> Any:
        pass


class IDatabase(ABC):
    separator = '/'

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
    def create(self, decryption_time: int = None):
        """
        Create the database file.

        :param decryption_time: Target decryption time in MS for the database
        :raise IOError: If the database file already exists
        """
        pass

    @abstractmethod
    def exists(self) -> bool:
        """
        Check whether the database file exists.

        :return: Whether the database file exists.
        """
        pass

    @abstractmethod
    def get_info(self) -> dict:
        """

        :return:
        """
        pass

    @abstractmethod
    def create_group(self, path: str) -> IGroup:
        """
        Create a new group.

        :param path: Path of the group to create.
        :return: The newly created group.
        """
        pass

    @abstractmethod
    def remove_group(self, group: Union[str, IGroup]):
        """
        Remove a group.

        :param group: Group or path of the group to remove.
        """
        pass

    @abstractmethod
    def create_entry(self, path: str, password: Union[str, command.GeneratePasswordConfig] = None,
                     username: str = None, url: str = None) -> IEntry:
        """
        Create a new entry.

        :param path: Path of the entry to create.
        :param password:
        :param username:
        :param url:
        :return: The newly created entry.
        """
        pass

    @abstractmethod
    def remove_entry(self, entry: Union[str, IEntry]):
        """
        Remove an entry.

        :param entry: Entry or path of the entry to remove.
        """
        pass

    @abstractmethod
    def get_entries(self) -> List[IEntry]:
        """
        Get all entries.

        :return: List of entries.
        """
        pass

    @abstractmethod
    def find_entries(self, term: str) -> List[IEntry]:
        """
        Find entries by search term.

        :param term: Search term.
        :return: List of entries matching the search term.
        """
        pass

    @abstractmethod
    def compare(self, database_from: IDatabase):
        """
        Compare this and another database.
        (The changes that would be necessary if another database is merged into this database.)

        :param database_from:
        """
        pass

    @abstractmethod
    def merge(self, database_from: IDatabase):
        """
        Merge another database into this database.

        :param database_from:
        """
        pass

    @abstractmethod
    def import_from(self, path: str):
        """
        Import the contents of an XML file.

        :param path: Path of the XML file.
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
        :return:
        """
        pass

    @abstractmethod
    def copy_to(self, target_path: str):
        """
        Copy the database file to another location.

        :param target_path:
        """
        pass


class IGroup(ABC):
    @abstractmethod
    def get_database(self) -> IDatabase:
        pass

    @abstractmethod
    def get_group(self) -> Optional[IGroup]:
        pass

    @abstractmethod
    def get_path(self) -> str:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def remove(self):
        pass


class IEntry(ABC):
    @abstractmethod
    def get_database(self) -> IDatabase:
        pass

    @abstractmethod
    def get_group(self) -> Optional[IGroup]:
        pass

    @abstractmethod
    def get_path(self) -> str:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def set_username(self, username: str):
        pass

    @abstractmethod
    def get_username(self) -> Optional[str]:
        pass

    @abstractmethod
    def set_url(self, url: str):
        pass

    @abstractmethod
    def get_url(self) -> Optional[str]:
        pass

    @abstractmethod
    def set_password(self, password: Union[str, command.GeneratePasswordConfig]):
        """

        :param password:
        :return:
        """
        pass

    @abstractmethod
    def get_password(self) -> Optional[str]:
        """

        :return:
        """
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def clip(self, attribute: str = None, timeout: int = None):
        """

        :param attribute:
        :param timeout:
        :return:
        """
        pass

    @abstractmethod
    def move(self, group: IGroup):
        """
        Move this entry to a group.

        :param group:
        """
        pass

    @abstractmethod
    def remove(self):
        """
        Remove this entry from the database.
        """
        pass
