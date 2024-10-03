import asyncio
from typing import List
from unittest import TestCase, main

from sblpy.async_connection import AsyncSurrealConnection
from sblpy.connection import SurrealSyncConnection


class TestConnectionPool(TestCase):

    def setUp(self):
        self.queries: List[str] = ["DELETE user;"]
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

    def test_query(self):
        async def run_test():
            con = AsyncSurrealConnection(
                "localhost",
                8000,
                "root",
                "root",
                max_size=2**20
            )
            await con.query("CREATE user:tobie SET name = 'Tobie';")
            await con.query("CREATE user:jaime SET name = 'Jaime';")

            outcome = await con.query("SELECT * FROM user;")
            self.assertEqual(len(outcome), 2)
            self.assertEqual(
                [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
                outcome
            )

        asyncio.run(run_test())


if __name__ == "__main__":
    main()
