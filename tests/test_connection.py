from typing import List
from unittest import TestCase, main

from sblpy.connection import SurrealSyncConnection


class TestSurrealSyncConnection(TestCase):

    def setUp(self):
        self.queries: List[str] = []
        self.connection = SurrealSyncConnection(
            "localhost",
            8000,
            "root",
            "root"
        )

    def tearDown(self):
        for query in self.queries:
            self.connection.query(query)
        self.connection.socket.close()

    def test___init__(self):
        self.assertEqual(self.connection.url, "ws://localhost:8000/rpc")
        self.assertEqual(self.connection.user, "root")
        self.assertEqual(self.connection.password, "root")
        self.assertEqual(self.connection.namespace, "default")
        self.assertEqual(self.connection.database, "default")
        self.assertIsNotNone(self.connection.socket)
        self.assertIsNotNone(self.connection.id)
        self.assertIsNotNone(self.connection.token)

    def test_query(self):
        self.queries = ["DELETE user;"]
        self.connection.query("CREATE user:tobie SET name = 'Tobie';")
        self.connection.query("CREATE user:jaime SET name = 'Jaime';")
        outcome = self.connection.query("SELECT * FROM user;")

        self.assertEqual(len(outcome), 2)
        self.assertEqual(
            [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
            outcome
        )

    def test_query_error(self):
        self.queries = ["DELETE user;"]
        self.connection.query("CREATE user:tobie SET name = 'Tobie';")
        with self.assertRaises(Exception) as context:
            self.connection.query("CREATE user:tobie SET name = 'Tobie';")
        self.assertEqual(
            "error querying: Database record `user:tobie` already exists",
            str(context.exception)
        )

    def test_run_multiple_queries(self):
        self.queries = ["DELETE user;"]
        self.connection.query(
            "CREATE user:tobie SET name = 'Tobie'; CREATE user:jaime SET name = 'Jaime';"
        )
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 2)
        self.assertEqual(
            [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
            outcome
        )

    def test_context(self):
        self.queries = ["DELETE user;"]
        with self.connection as conn:
            conn.query("CREATE user:tobie SET name = 'Tobie';")
            conn.query("CREATE user:jaime SET name = 'Jaime';")
            outcome = conn.query("SELECT * FROM user;")
            self.assertEqual(len(outcome), 2)
            self.assertEqual(
                [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
                outcome
            )

        # asserting that the connection is closed
        with self.assertRaises(Exception) as context:
            conn.query("SELECT * FROM user;")
        self.assertEqual(
            "sent 1000 (OK); no close frame received",
            str(context.exception)
        )

        # has to create another connection for the teardown
        self.connection = SurrealSyncConnection(
            "localhost",
            8000,
            "root",
            "root"
        )

    def test_multi_one(self):
        self.queries = ["DELETE user;"]
        self.connection.query("CREATE user:tobie SET name = 'Tobie'; CREATE user:jaime SET name = 'Jaime';")
        outcome = self.connection.query("SELECT * FROM user;")
        self.assertEqual(len(outcome), 2)
        self.assertEqual(
            [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
            outcome
        )


if __name__ == "__main__":
    main()
