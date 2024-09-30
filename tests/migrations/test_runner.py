from unittest import TestCase, main

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import get_latest_version, bump_version
from sblpy.migrations.migrations import Migration
from sblpy.migrations.runner import MigrationRunner


class TestMigrationRunner(TestCase):

    def setUp(self):
        self.connection = SurrealSyncConnection(
            "localhost",
            8000,
            "root",
            "root"
        )
        self.queries = ["DELETE user;", "DELETE _sbl_migrations;"]
        self.up_migrations = [
            Migration.from_docstring("CREATE user:one SET name = 'one';"),
            Migration.from_docstring("CREATE user:two SET name = 'two';"),
            Migration.from_docstring("CREATE user:three SET name = 'three';"),
            Migration.from_docstring("CREATE user:four SET name = 'four';"),
            Migration.from_docstring("CREATE user:five SET name = 'five';"),
            Migration.from_docstring("CREATE user:six SET name = 'six';"),
            Migration.from_docstring("CREATE user:seven SET name = 'seven';"),
            Migration.from_docstring("CREATE user:eight SET name = 'eight';"),
            Migration.from_docstring("CREATE user:nine SET name = 'nine';"),
            Migration.from_docstring("CREATE user:ten SET name = 'ten';")
        ]
        self.down_migrations = [
            Migration.from_docstring("DELETE user:one;"),
            Migration.from_docstring("DELETE user:two;"),
            Migration.from_docstring("DELETE user:three;"),
            Migration.from_docstring("DELETE user:four;"),
            Migration.from_docstring("DELETE user:five;"),
            Migration.from_docstring("DELETE user:six;"),
            Migration.from_docstring("DELETE user:seven;"),
            Migration.from_docstring("DELETE user:eight;"),
            Migration.from_docstring("DELETE user:nine;"),
            Migration.from_docstring("DELETE user:ten;")
        ]

    def tearDown(self):
        for query in self.queries:
            self.connection.query(query)
        self.connection.socket.close()

    def test_run(self):
        runner = MigrationRunner(
            self.up_migrations,
            self.down_migrations,
            self.connection
        )
        runner.run()
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 10)
        latest_version = get_latest_version(
            self.connection.host,
            self.connection.port,
            self.connection.user,
            self.connection.password
        )
        self.assertEqual(latest_version, 10)

    def test_run_half(self):
        for i in range(5):
            bump_version(
                self.connection.host,
                self.connection.port,
                self.connection.user,
                self.connection.password
            )

        runner = MigrationRunner(
            self.up_migrations,
            self.down_migrations,
            self.connection
        )
        self.assertEqual(runner.version, 5)
        runner.run()
        outcome = self.connection.query("SELECT * FROM user;")
        print(len(outcome))
        self.assertEqual(len(outcome), 6)

    def test_bump(self):
        for i in range(5):
            bump_version(
                self.connection.host,
                self.connection.port,
                self.connection.user,
                self.connection.password
            )
        runner = MigrationRunner(
            self.up_migrations,
            self.down_migrations,
            self.connection
        )
        self.assertEqual(runner.version, 5)

        runner.increment()

        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 1)
        self.assertEqual(outcome[0]["name"], "six")

        latest_version = get_latest_version(
            self.connection.host,
            self.connection.port,
            self.connection.user,
            self.connection.password
        )
        self.assertEqual(latest_version, 6)
        self.assertEqual(runner.version, 6)
        self.assertEqual(runner.index, 5)

    def test_decrement(self):
        self.connection.query("CREATE user:four SET name = 'five';")
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 1)

        for i in range(5):
            bump_version(
                self.connection.host,
                self.connection.port,
                self.connection.user,
                self.connection.password
            )
        runner = MigrationRunner(
            self.up_migrations,
            self.down_migrations,
            self.connection
        )
        # self.assertEqual(runner.version, 5)
        #
        # print(runner.down_migrations[runner.index].sql)
        #
        # runner.decrement()
        #
        # outcome = self.connection.query("SELECT * FROM user;")
        # print(outcome)
        # self.assertEqual(len(outcome), 0)
        #
        # latest_version = get_latest_version(
        #     self.connection.host,
        #     self.connection.port,
        #     self.connection.user,
        #     self.connection.password
        # )
        # self.assertEqual(latest_version, 4)
        # self.assertEqual(runner.version, 4)
        # self.assertEqual(runner.index, 3)


if __name__ == '__main__':
    main()
