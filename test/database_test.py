import logging
import os
import secrets
import tempfile
import unittest
from abc import ABC
from xml.etree import ElementTree
from entity import Database

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


class AbstractDatabaseTest(unittest.TestCase, ABC):
    def setUp(self):
        self.database = None
        self.database_file = None
        raise NotImplementedError

    def test_exists(self):
        self.assertTrue(self.database.exists())

    def test_get_path(self):
        self.assertEqual(
            self.database.get_path(),
            os.path.join(os.getcwd(), self.database_file)
        )

    def test_get_info(self):
        self.assertSetEqual(
            set(self.database.get_info().keys()),
            {"uuid", "name", "description", "cipher", "kdf"}
        )

    def test_export(self):
        self.database.export()

    def test_export_csv(self):
        self.database.export(format='csv')

    def test_export_xml(self):
        self.assertValidXml(
            self.database.export(format='xml')
        )

    def assertValidXml(self, data: str):
        ElementTree.fromstring(data)


class PasswordDatabaseTest(AbstractDatabaseTest):
    def setUp(self):
        self.database_file = 'assets/password.kdbx'
        self.password = '1234'
        self.database = Database(self.database_file, password=self.password)

    def test_has_password(self):
        self.assertTrue(self.database.has_password())

    def test_get_password(self):
        self.assertEqual(
            self.database.get_password(),
            self.password
        )

    def test_has_key_file(self):
        self.assertFalse(self.database.has_key_file())

    def test_get_key_file(self):
        self.assertIsNone(self.database.get_key_file())


class KeyFileDatabaseTest(AbstractDatabaseTest):
    def setUp(self):
        self.database_file = 'assets/keyfile.kdbx'
        self.key_file = 'assets/keyfile.key'
        self.database = Database(self.database_file, key_file=self.key_file)

    def test_has_password(self):
        self.assertFalse(self.database.has_password())

    def test_get_password(self):
        self.assertIsNone(self.database.get_password())

    def test_has_key_file(self):
        self.assertTrue(self.database.has_key_file())

    def test_get_key_file(self):
        self.assertEqual(
            self.database.get_key_file(),
            os.path.join(os.getcwd(), self.key_file)
        )


class PasswordAndKeyFileDatabaseTest(AbstractDatabaseTest):
    def setUp(self):
        self.database_file = 'assets/password_keyfile.kdbx'
        self.password = '1234'
        self.key_file = 'assets/password_keyfile.key'
        self.database = Database(self.database_file, password=self.password, key_file=self.key_file)

    def test_has_password(self):
        self.assertTrue(self.database.has_password())

    def test_get_password(self):
        self.assertEqual(
            self.database.get_password(),
            self.password
        )

    def test_has_key_file(self):
        self.assertTrue(self.database.has_key_file())

    def test_get_key_file(self):
        self.assertEqual(
            self.database.get_key_file(),
            os.path.join(os.getcwd(), self.key_file)
        )


class UnicodePasswordDatabaseTest(AbstractDatabaseTest):
    def setUp(self):
        self.database_file = 'assets/password_unicode.kdbx'
        self.password = 'passwörter123&'
        self.database = Database(self.database_file, password=self.password)

    def test_exists(self):
        self.assertTrue(self.database.exists())

    def test_get_info(self):
        self.assertSetEqual(
            set(self.database.get_info().keys()),
            {"uuid", "name", "description", "cipher", "kdf"}
        )

        self.assertEqual(
            self.database.get_info().get('name'),
            "Passwörter"
        )

    def test_export_xml(self):
        self.assertIn('<DatabaseName>Passwörter</DatabaseName>', self.database.export(format='xml'))


class DatabasePairTest(unittest.TestCase):
    def setUp(self):
        self.database_1 = Database('assets/new.kdbx', password='1234')
        self.database_2 = Database('assets/merge.kdbx', password='merge')

    def test_exists(self):
        self.assertTrue(self.database_1.exists())
        self.assertTrue(self.database_2.exists())

    def test_compare(self):
        changes = self.database_1.compare(self.database_2)
        self.assertSetEqual(
            changes,
            {'Creating missing Test entry [898c7067a74e4aada0d2a3cf590f8c2a]',
             'Adding custom data KPXC_DECRYPTION_TIME_PREFERENCE [1000]',
             'Adding custom data FDO_SECRETS_EXPOSED_GROUP [{00000000-0000-0000-0000-000000000000}]'}
        )


class KeyfileDatabasePairTest(DatabasePairTest):
    def setUp(self):
        self.database_file_1 = 'assets/keyfile.kdbx'
        self.key_file_1 = 'assets/keyfile.key'
        self.database_1 = Database(self.database_file_1, key_file=self.key_file_1)

        self.database_file_2 = 'assets/keyfile_2.kdbx'
        self.key_file_2 = 'assets/keyfile_2.key'
        self.database_2 = Database(self.database_file_2, key_file=self.key_file_2)

    def test_compare(self):
        changes = self.database_1.compare(self.database_2)
        self.assertSetEqual(
            changes,
            {'Merge Entry/Entry 2 with alien on top under Root',
             'Synchronizing from newer source Entry [a81dc75e22344e92b27e78b2af04f251]'}
        )


class IdenticalDatabasePairTest(DatabasePairTest):
    def setUp(self):
        self.database_1 = Database('assets/merge.kdbx', password='merge')
        self.database_2 = Database('assets/merge.kdbx', password='merge')

    def test_compare(self):
        changes = self.database_1.compare(self.database_2)
        self.assertSetEqual(
            changes,
            {'Merge Test entry/Test entry with local on top/under Root'}
        )


del AbstractDatabaseTest
