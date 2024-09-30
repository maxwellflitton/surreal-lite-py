"""
Tests the creation of migrations from docstrings, lists, and files.
"""
import os
from typing import List
from unittest import TestCase, main

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import get_latest_version
from sblpy.migrations.migrations import Migration


class TestDbMigration(TestCase):

    def setUp(self):
        self.queries: List[str] = []
        self.connection = SurrealSyncConnection(
            "localhost",
            8000,
            "root",
            "root"
        )
        self.queries = ["DELETE user;", "DELETE _sbl_migrations;"]
        self.expected_sql = "CREATE user:tobie SET name = 'Tobie'; CREATE user:jaime SET name = 'Jaime';"

    def tearDown(self):
        for query in self.queries:
            self.connection.query(query)
        self.connection.socket.close()

    def test_from_docstring(self):
        query = """
        CREATE user:tobie SET name = 'Tobie';
        CREATE user:jaime SET name = 'Jaime';
        """
        migration = Migration.from_docstring(query)
        self.assertEqual(self.expected_sql, migration.sql)
        query = """


                CREATE user:tobie SET name = 'Tobie';

                CREATE user:jaime SET name = 'Jaime';


                """
        migration = Migration.from_docstring(query)
        self.assertEqual(self.expected_sql, migration.sql)
        migration.run(self.connection)
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 2)
        self.assertEqual(
            [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
            outcome
        )
        latest_version = get_latest_version(
            self.connection.host,
            self.connection.port,
            self.connection.user,
            self.connection.password
        )
        self.assertEqual(latest_version, 1)

    def test_from_list(self):
        query = [
            "CREATE user:tobie SET name = 'Tobie';",
            "",
            "CREATE user:jaime SET name = 'Jaime'"
        ]
        migration = Migration.from_list(query)
        self.assertEqual(self.expected_sql, migration.sql)
        migration.run(self.connection)
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 2)
        self.assertEqual(
            [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
            outcome
        )
        latest_version = get_latest_version(
            self.connection.host,
            self.connection.port,
            self.connection.user,
            self.connection.password
        )
        self.assertEqual(latest_version, 1)

    def test_from_file(self):
        current_file_path = os.path.abspath(__file__)

        # Get the directory of the current file
        directory = os.path.dirname(current_file_path)
        file_path = os.path.join(directory, "test.sql")
        migration = Migration.from_file(str(file_path))
        expected_sql = (""
                        "CREATE user:tobie SET name = 'Tobie'; "
                        "CREATE user:jaime SET name = 'Jaime'; "
                        "CREATE user:three SET name = 'Three';"
                        )
        self.assertEqual(expected_sql, migration.sql)
        migration.run(self.connection)
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 3)


if __name__ == '__main__':
    main()