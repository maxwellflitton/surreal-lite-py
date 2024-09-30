import asyncio
from unittest import TestCase

from sblpy.pool.connection_pool import execute_pooled_query, client_pool, NUM_CLIENTS, shutdown_pool
from sblpy.query import Query


class TestConnectionPool(TestCase):

    def setUp(self):
        self.message_queue = asyncio.Queue()

    def tearDown(self):
        pass

    def test_query_pool(self):
        async def run_test():
            asyncio.create_task(client_pool(
                "localhost",
                8000,
                "root",
                "root",
                number_of_clients=NUM_CLIENTS
            ))
            for _ in range(100):
                _ = await execute_pooled_query(Query("CREATE user:tobie SET name = 'Tobie';"))
                _ = await execute_pooled_query(Query("CREATE user:jaime SET name = 'Jaime';"))
                response = await execute_pooled_query(Query("SELECT * FROM user;"))
                self.assertEqual(len(response["result"][0]["result"]), 2)
                self.assertEqual(
                    [{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}],
                    response["result"][0]["result"]
                )
                _ = await execute_pooled_query(Query("DELETE user;"))
            await shutdown_pool(number_of_clients=NUM_CLIENTS)
        asyncio.run(run_test())