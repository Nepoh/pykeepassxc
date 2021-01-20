import os
import shutil
from typing import Optional
from interface import IDatabase
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

    def get_info(self) -> dict:
        return command.DatabaseInfoCommand(self).execute()

    def compare(self, database_from: IDatabase):
        return command.CompareDatabaseCommand(self, database_from).execute()

    def export(self, format: str = None) -> str:
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
