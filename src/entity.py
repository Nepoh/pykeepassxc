import os
import shutil
from typing import Union, List, Optional
from interface import IDatabase, IGroup, IEntry
import command


class Database(IDatabase):
    def __init__(self, path: str, password: str = None, key_file: str = None, yubikey_slot: str = None):
        self._path = os.path.abspath(path)
        self._password = password
        self._key_file = key_file
        self._yubikey_slot = yubikey_slot

    def get_path(self) -> str:
        return self._path

    def has_password(self) -> bool:
        return self._password is not None

    def get_password(self) -> Optional[str]:
        return self._password

    def has_key_file(self) -> bool:
        return self._key_file is not None

    def get_key_file(self) -> Optional[str]:
        return self._key_file

    def has_yubikey_slot(self) -> bool:
        return self._yubikey_slot is not None

    def get_yubikey_slot(self) -> Optional[str]:
        return self._yubikey_slot

    def create(self, decryption_time: int = None):
        """
        Create the database file.

        :param decryption_time: Target decryption time in MS for the database
        :raise IOError: If the database file already exists
        """
        command.CreateDatabaseCommand(self, decryption_time).execute()

    def exists(self) -> bool:
        """
        Check whether the database file exists.

        :return: Whether the database file exists.
        """
        return os.path.exists(self._path)

    def get_info(self) -> dict:
        """

        :return:
        """
        return command.DatabaseInfoCommand(self).execute()

    def create_group(self, path: str) -> IGroup:
        """
        Create a new group.

        :param path: Path of the group to create.
        :return: The newly created group.
        """
        group = Group(self, path)
        command.CreateGroupCommand(self, group)
        return group

    def remove_group(self, group: Union[str, IGroup]):
        """
        Remove a group.

        :param group: Group or path of the group to remove.
        """
        group = group if isinstance(group, IGroup) else Group(self, group)
        command.RemoveGroupCommand(self, group).execute()

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
        entry = Entry(self, path, password, username, url)
        command.CreateEntryCommand(self, entry).execute()
        return entry

    def remove_entry(self, entry: Union[str, IEntry]):
        """
        Remove an entry.

        :param entry: Entry or path of the entry to remove.
        """
        entry = entry if isinstance(entry, IEntry) else Entry(self, entry)
        command.RemoveEntryCommand(self, entry).execute()

    def get_entries(self) -> List[IEntry]:
        """
        Get all entries.

        :return: List of entries.
        """
        paths = command.ListEntriesCommand(self).execute()
        return [Entry(self, path) for path in paths]

    def find_entries(self, term: str) -> List[IEntry]:
        """
        Find entries by search term.

        :param term: Search term.
        :return: List of entries matching the search term.
        """
        paths = command.LocateEntriesCommand(self, term=term).execute()
        return [Entry(self, path) for path in paths]

    def merge(self, database_from: IDatabase):
        """
        Merge another database into this database.

        :param database_from:
        """
        command.MergeDatabaseCommand(self, database_from).execute()

    def import_from(self, path: str):
        """
        Import the contents of an XML file.

        :param path: Path of the XML file.
        """
        command.ImportDatabaseCommand(self, path).execute()

    def export(self, format: str = None) -> str:
        """
        Exports the content of a database in the specified format.
        WARNING: Passwords are extracted in plaintext!

        :param format: The output format ('xml' or 'csv')
        :return:
        """
        return command.ExportDatabaseCommand(self, format).execute()

    def export_to(self, target_path: str, format: str = 'xml'):
        """
        Exports the content of a database in the specified format and writes it to a file.
        WARNING: Passwords are extracted in plaintext!

        :param target_path:
        :param format: The output format ('xml' or 'csv')
        :return:
        """
        if os.path.exists(target_path):
            raise IOError('File at {} already exists.'.format(target_path))
        content = self.export(format=format)
        with open(target_path, 'w') as f:
            f.write(content)
        with open(target_path, 'r') as f:
            exported_content = f.read()
        if not exported_content == content:
            os.remove(target_path)
            raise IOError

    def copy_to(self, target_path: str):
        """
        Copy the database file to another location.

        :param target_path:
        """
        if os.path.exists(target_path):
            raise IOError('File at {} already exists.'.format(target_path))
        shutil.copyfile(self._path, target_path)
        with open(self._path, 'r') as f:
            source_content = f.read()
        with open(target_path, 'r') as f:
            target_content = f.read()
        if not source_content == target_content:
            os.remove(target_path)
            raise IOError


class Group(IGroup):
    def __init__(self, database: IDatabase, path: str):
        self._database = database
        self._path = path

    def get_path(self) -> str:
        return self._path

    def get_name(self) -> str:
        # last path element
        return self._path.split('/')[-1]

    def remove(self):
        command.RemoveGroupCommand(self._database, self).execute()


class Entry(IEntry):
    def __init__(self, database: IDatabase, path: str):
        self._database = database
        self._path = path
        self._username = None
        self._url = None
        self._password = None
        self._generate_password = None

    def get_path(self) -> str:
        return self._path

    def get_name(self) -> str:
        # last path element
        return self._path.split('/')[-1]

    def set_username(self, username: str):
        self._username = username

    def get_username(self) -> Union[str, None]:
        return self._username

    def set_url(self, url: str):
        self._url = url

    def get_url(self) -> Union[str, None]:
        return self._url

    def set_password(self, password: Union[str, command.GeneratePasswordConfig]):
        if isinstance(password, str):
            self._password = password
        elif isinstance(password, command.GeneratePasswordConfig):
            self._generate_password = password
        else:
            raise ValueError

    def get_password(self) -> Union[str, None]:
        return self._password

    def clip(self, attribute: str = None, timeout: int = None):
        command.ClipEntryCommand(
            database=self._database,
            entry=self,
            attribute=attribute,
            timeout=timeout
        ).execute()

    def move(self, group: IGroup):
        """
        Move this entry to a group.

        :param group:
        """
        command.MoveEntryCommand(self._database, self, group).execute()

    def remove(self):
        """
        Remove this entry from the database.
        """
        command.RemoveEntryCommand(self._database, self).execute()
