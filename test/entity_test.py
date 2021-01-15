import logging
import os
import secrets
import tempfile
import unittest
from entity import Database, Group, Entry

logging.basicConfig(level=logging.DEBUG)


class CreateDatabaseTest(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.gettempdir()

        self.database_path = os.path.join(temp_dir, 'test_create.kdbx')
        self.assertFalse(os.path.exists(self.database_path))

        self.keyfile_path = os.path.join(temp_dir, 'test_create.key')
        with open(self.keyfile_path, 'wb') as f:
            f.write(secrets.token_bytes(100))

    def tearDown(self):
        if os.path.exists(self.database_path):
            os.remove(self.database_path)
        os.remove(self.keyfile_path)

    def test_create_database_with_password(self):
        database = Database(self.database_path, password='1234')
        database.create()
        self.assertTrue(os.path.exists(self.database_path))

    def test_create_database_with_keyfile(self):
        database = Database(self.database_path, key_file=self.keyfile_path)
        database.create()
        self.assertTrue(os.path.exists(self.database_path))

    def test_create_database_with_password_and_keyfile(self):
        database = Database(self.database_path, password='1234', key_file=self.keyfile_path)
        database.create()
        self.assertTrue(os.path.exists(self.database_path))

    def test_create_database_without_key_fails(self):
        database = Database(self.database_path)
        with self.assertRaises(Exception):
            database.create()


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        self.database_file = 'pw.kdbx'
        self.password = '1234'
        self.database = Database(self.database_file, password=self.password)

    def test_get_path(self):
        self.assertEqual(
            self.database.get_path(),
            os.path.join(os.getcwd(), self.database_file)
        )

    def test_has_password(self):
        self.assertTrue(self.database.has_password())

    def test_get_password(self):
        self.assertEqual(
            self.password,
            os.path.join(os.getcwd(), self.database_file)
        )

    def test_get_info(self):
        self.assertEqual(
            self.database.get_info(),
        )
