import os
import shutil
from pykeepassxc import command


class Database:
    def __init__(self, path: str, password: str, key_file: str = None, yubikey_slot: str = None):
        self.__path = path
        self.__password = password
        self.__key_file = key_file
        self.__yubikey_slot = yubikey_slot

    def get_path(self) -> str:
        return self.__path

    def get_password(self) -> str:
        return self.__password

    def has_key_file(self) -> bool:
        return self.__key_file is not None

    def get_key_file(self) -> str:
        return self.__key_file

    def has_yubikey_slot(self) -> bool:
        return self.__yubikey_slot is not None

    def get_yubikey_slot(self) -> str:
        return self.__yubikey_slot

    def export(self, format: str = 'xml') -> str:
        """
        Exports the content of a database in the specified format.
        WARNING: Passwords are extracted in plaintext!
        :param format: The output format ('xml' or 'csv')
        :return:
        """
        # in earlier versions "export" was called "extract"
        cmd = command.DatabaseCommand(self, ['export', '--format', format])
        return cmd.run()

    def export_to(self, path: str, format: str = 'xml'):
        """
        Exports the content of a database in the specified format and writes it to a file.
        WARNING: Passwords are extracted in plaintext!
        :param path:
        :param format: The output format ('xml' or 'csv')
        :return:
        """
        if os.path.exists(path):
            raise IOError('File at {} already exists.'.format(path))
        content = self.export(format=format)
        with open(path, 'w') as f:
            f.write(content)
        with open(path, 'r') as f:
            exported_content = f.read()
        if not exported_content == content:
            os.remove(path)
            raise IOError

    def copy_to(self, path: str):
        """

        :param path:
        """
        if os.path.exists(path):
            raise IOError('File at {} already exists.'.format(path))
        shutil.copyfile(self.__path, path)
        with open(self.__path, 'r') as f:
            source_content = f.read()
        with open(path, 'r') as f:
            target_content = f.read()
        if not source_content == target_content:
            os.remove(path)
            raise IOError
