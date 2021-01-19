import os
import shutil
from typing import Union, List, Optional
from interface import IDatabase, IGroup, IEntry
import command


class Database(IDatabase):
    def __init__(self, path: str, password: str = None, key_file: str = None):
        """

        :param path: Path to the database file
        :param password: [optional] Password to open the database
        :param key_file: [optional] Path to the key-file to open the database
        """
        assert os.path.exists(path), 'Database at {} does not exist.'.format(path)
        self._path = os.path.abspath(path)
        self._password = password
        self._key_file = os.path.abspath(key_file) if key_file is not None else None

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

    def create(self, decryption_time: int = None):
        """
        Create the database file.

        :param decryption_time: Target decryption time in MS for the database
        :raise IOError: If the database file already exists
        """
        command.CreateDatabaseCommand(self, decryption_time).execute()

    def exists(self) -> bool:
        return os.path.exists(self._path)

    def get_info(self) -> dict:
        return command.DatabaseInfoCommand(self).execute()

    def create_group(self, path: str) -> IGroup:
        """
        Create a new group.

        :param path: Path of the group to create.
        :return: The newly created group.
        """
        group = Group(path, self)
        group.create()
        return group

    def remove_group(self, group: Union[str, IGroup]):
        """
        Remove a group.

        :param group: Group or path of the group to remove.
        """
        group = group if isinstance(group, IGroup) else Group(group, self)
        group.remove()

    def create_entry(self, title: str, password: Union[str, command.GeneratePasswordConfig] = None,
                     username: str = None, url: str = None) -> IEntry:
        """
        Create a new entry.

        :param title: Path of the entry to create.
        :param password:
        :param username:
        :param url:
        :return: The newly created entry.
        """
        entry = Entry(title, self)
        if password is not None:
            entry.set_password(password)
        if username is not None:
            entry.set_username(username)
        if url is not None:
            entry.set_url(url)
        entry.create()
        return entry

    def remove_entry(self, entry: Union[str, IEntry]):
        """
        Remove an entry.

        :param entry: Entry object or title of the entry to remove.
        """
        entry = entry if isinstance(entry, IEntry) else Entry(entry, self)
        entry.remove()

    def get_entries(self) -> List[IEntry]:
        """
        Get all entries.

        :return: List of entries.
        """
        paths = command.ListEntriesCommand(self).execute()
        return [Entry(path, self) for path in paths]

    def find_entries(self, term: str) -> List[IEntry]:
        """
        Find entries by search term.

        :param term: Search term.
        :return: List of entries matching the search term.
        """
        paths = command.LocateEntriesCommand(self, term=term).execute()
        return [Entry(path, self) for path in paths]

    def compare(self, database_from: IDatabase):
        """
        Compare this and another database.
        (The changes that would be necessary if another database is merged into this database.)

        :param database_from:
        """
        return command.MergeDatabaseCommand(self, database_from).execute(dry_run=True)

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

    def export_to(self, target_path: str, format: str = None):
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
    def __init__(self, title: str, parent: Union[IDatabase, IGroup]):
        if isinstance(parent, IDatabase):
            self._database = parent
            self._group = None
        elif isinstance(parent, IGroup):
            self._database = parent.get_database()
            self._group = parent
        else:
            raise ValueError

        assert len(title) > 0
        self._title = title

    def get_database(self) -> IDatabase:
        return self._database

    def get_group(self) -> Optional[IGroup]:
        return self._group

    def get_title(self) -> str:
        return self._title

    def get_path(self) -> str:
        if self._group is None:
            return self._title
        else:
            return self._group.get_path() + self._database.separator + self._title

    def create(self):
        command.CreateGroupCommand(self._database, self).execute()

    def remove(self):
        command.RemoveGroupCommand(self._database, self).execute()


class Entry(IEntry):
    def __init__(self, title: str, parent: Union[IDatabase, IGroup]):
        if isinstance(parent, IDatabase):
            self._database = parent
            self._group = None
        elif isinstance(parent, IGroup):
            self._database = parent.get_database()
            self._group = parent
        else:
            raise ValueError
        self._title = title
        self._username = None
        self._url = None
        self._password = None
        self._generate_password = None

    def get_database(self) -> IDatabase:
        return self._database

    def get_group(self) -> Optional[IGroup]:
        return self._group

    def get_title(self) -> str:
        return self._title

    def get_path(self) -> str:
        if self._group is None:
            return self._title
        else:
            return self._group.get_path() + self._database.separator + self._title

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

    def create(self):
        command.CreateEntryCommand(self._database, self).execute()

    def clip(self, attribute: str = None, timeout: int = None):
        command.ClipEntryCommand(
            database=self._database,
            entry=self,
            attribute=attribute,
            timeout=timeout
        ).execute()

    def move(self, group: IGroup):
        command.MoveEntryCommand(self._database, self, group).execute()
        self._group = group

    def remove(self):
        command.RemoveEntryCommand(self._database, self).execute()
