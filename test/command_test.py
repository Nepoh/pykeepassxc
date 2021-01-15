import logging
import os
import shutil
import tempfile
import unittest
from abc import ABC, abstractmethod
import command
from interface import ICommand

logging.basicConfig(level=logging.DEBUG)


class AbstractCommandTest(unittest.TestCase, ABC):
    def setUp(self):
        self.command = self.create_command()

    @abstractmethod
    def create_command(self) -> ICommand:
        pass

    def test_exe_environment_variable(self):
        original = os.environ.get('KEEPASSXC_CLI_EXE')
        os.environ['KEEPASSXC_CLI_EXE'] = 'nonexisting'
        with self.assertRaises(FileNotFoundError) as context:
            self.command.execute()
        if original is None:
            del os.environ['KEEPASSXC_CLI_EXE']
        else:
            os.environ['KEEPASSXC_CLI_EXE'] = original


class AbstractDatabaseCommandTest(unittest.TestCase, ABC):
    def setUp(self):
        super().setUp()
        temp_dir = tempfile.gettempdir()
        self.copy_database_file('test.kdbx', temp_dir)

    @staticmethod
    def copy_database_file(source_file_path: str, target_dir_path: str) -> str:
        temp_path = os.path.join(target_dir_path, os.path.basename(source_file_path))
        shutil.copy2(source_file_path, temp_path)
        return temp_path


class GeneratePasswordCommandTest(AbstractCommandTest):
    def create_command(self):
        return command.GeneratePasswordCommand()

    def test_output(self):
        output = self.command.execute()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)


class GenerateDicewareCommandTest(AbstractCommandTest):
    def create_command(self):
        return command.GenerateDicewareCommand()

    def test_output(self):
        output = self.command.execute()
        self.assertIsInstance(output, str)
        self.assertGreater(len(output), 0)


class EstimatePasswordCommandTest(AbstractCommandTest):
    def create_command(self):
        return command.EstimatePasswordCommand('1234')

    def test_output(self):
        output = self.command.execute()
        self.assertDictEqual(output, {'length': 4, 'entropy': 2.0, 'log10': 0.602})


class CreateDatabaseCommandTest(AbstractDatabaseCommandTest):
    pass


del AbstractCommandTest
del AbstractDatabaseCommandTest
