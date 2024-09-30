from unittest import TestCase, main

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import get_all_versions, get_latest_version, bump_version, lower_version


class TestDbProcesses(TestCase):

    def setUp(self):
        self.host = "localhost"
        self.port = 8000
        self.user = "root"
        self.password = "root"
        self.connection = SurrealSyncConnection(
            self.host,
            self.port,
            self.user,
            self.password
        )
        self.queries = ["DELETE _sbl_migrations;"]
        self.connection.query("CREATE _sbl_migrations:1 SET version = 1, applied_at = time::now();")
        self.connection.query("CREATE _sbl_migrations:2 SET version = 2, applied_at = time::now();")
        self.connection.query("CREATE _sbl_migrations:3 SET version = 3, applied_at = time::now();")

    def tearDown(self):
        for query in self.queries:
            self.connection.query(query)
        self.connection.socket.close()

    def test_get_all_versions(self):
        outcome = get_all_versions(
            self.host,
            self.port,
            self.user,
            self.password
        )
        self.assertEqual(len(outcome), 3)
        self.assertEqual(outcome[0]["version"], 1)
        self.assertEqual(outcome[1]["version"], 2)
        self.assertEqual(outcome[2]["version"], 3)

    def test_get_latest_version(self):
        outcome = get_latest_version(
            self.host,
            self.port,
            self.user,
            self.password
        )
        self.assertEqual(outcome, 3)

    def test_bump_version(self):
        bump_version(
            self.host,
            self.port,
            self.user,
            self.password
        )
        outcome = get_all_versions(
            self.host,
            self.port,
            self.user,
            self.password
        )
        self.assertEqual(len(outcome), 4)
        self.assertEqual(outcome[0]["version"], 1)
        self.assertEqual(outcome[1]["version"], 2)
        self.assertEqual(outcome[2]["version"], 3)
        self.assertEqual(outcome[3]["version"], 4)

    def test_lower_version(self):
        lower_version(
            self.host,
            self.port,
            self.user,
            self.password
        )
        outcome = get_all_versions(
            self.host,
            self.port,
            self.user,
            self.password
        )
        self.assertEqual(len(outcome), 2)
        self.assertEqual(outcome[0]["version"], 1)
        self.assertEqual(outcome[1]["version"], 2)


if __name__ == '__main__':
    main()
