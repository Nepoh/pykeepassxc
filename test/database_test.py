import logging
import os
import unittest

from abc import ABC
from xml.etree import ElementTree
from entity import Database

logging.basicConfig(level=logging.DEBUG)


class AbstractDatabaseTest(unittest.TestCase, ABC):
    def setUp(self):
        self.database = None
        self.database_file = None
        raise NotImplementedError

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


class CompareDatabaseTest(unittest.TestCase):
    def setUp(self):
        self.database_1 = Database('assets/new.kdbx', password='1234')
        self.database_2 = Database('assets/merge.kdbx', password='merge')

    def test_compare(self):
        changes = self.database_1.compare(self.database_2)
        self.assertSetEqual(
            changes,
            {'Creating missing Test entry [898c7067a74e4aada0d2a3cf590f8c2a]',
             'Adding custom data KPXC_DECRYPTION_TIME_PREFERENCE [1000]',
             'Adding custom data FDO_SECRETS_EXPOSED_GROUP [{00000000-0000-0000-0000-000000000000}]'}
        )


class CompareKeyfileDatabaseTest(CompareDatabaseTest):
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


class CompareIdenticalDatabaseTest(CompareDatabaseTest):
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
