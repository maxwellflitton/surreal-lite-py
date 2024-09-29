"""
Defines the async websocket connection pool for database queries

# Notes
The outputs are raw because we need the connections to have as little chance
of crashing. This means that you need to handle your output yourself.
"""
import asyncio
import json
from uuid import uuid4

import websockets

from sblpy.pool.setup_config import setup_connection
from sblpy.query import Query

# Dictionary to map request ids to asyncio.Future objects
pending_responses = {}

# WebSocket client pool size
NUM_CLIENTS = 5

# The message queue to send the queries to the connection pool
MESSAGE_QUEUE = asyncio.Queue()


async def websocket_client(
        client_id,
        host: str,
        port: int,
        user: str,
        password: str,
        namespace: str = "default",
        database: str = "default"
    ) -> None:
    """
    Spins up a websocket client in the async runtime as an actor.

    :param client_id: The ID of the client to enable mapping
    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will stick to
    :param database: (str) The database that the connection will stick to
    :return: None
    """
    url: str = f"ws://{host}:{port}/rpc"
    id = str(uuid4())
    async with websockets.connect(url) as websocket:
        print(f"Client {client_id} connected to {url}")
        await setup_connection(websocket, id, user, password, namespace, database)
        while True:
            # Get the message to send to the external server
            request_id, message = await MESSAGE_QUEUE.get()
            if message == "shutdown":
                break

            await websocket.send(json.dumps(message, ensure_ascii=False))

            # Await the response from the WebSocket server
            response = await websocket.recv()

            # Set the result of the future so the request handler can continue
            pending_responses[request_id].set_result(response)
            del pending_responses[request_id]


async def client_pool(
        host: str,
        port: int,
        user: str,
        password: str,
        namespace: str = "default",
        database: str = "default",
        number_of_clients: int = 5
    ) -> None:
    """
    Spins up an async connection pool.

    # Notes
    To be run in the background using the following:
    ```
    asyncio.create_task(client_pool(
        "localhost",
        8000,
        "root",
        "root",
        number_of_clients=NUM_CLIENTS
    ))
    ```
    Do not await on this

    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connections will stick to
    :param database: (str) The database that the connections will stick to
    :param number_of_clients: (int) the number of clients in the connection pool
    :return: None
    """
    tasks = []
    for i in range(number_of_clients):
        tasks.append(asyncio.create_task(websocket_client(
            i, host, port, user, password, namespace, database
        )))
    await asyncio.gather(*tasks)


async def shutdown_pool(number_of_clients: int = 5) -> None:
    """
    Sends kill messages to all clients shutting down the connection pool.

    :param number_of_clients: (int) the number of clients to kill (should be the same number for creating the connection pool)
    :return: None
    """
    for _ in range(number_of_clients):
        await MESSAGE_QUEUE.put((None, "shutdown"))


async def execute_pooled_query(query: Query) -> dict:
    """
    Sends a query to the connection pool to be executed on the database.

    :param query: (Query)
    :return:
    """
    request_id = str(uuid4())
    response_future = asyncio.get_running_loop().create_future()
    pending_responses[request_id] = response_future

    # Send the request to the WebSocket client via the message_queue
    await MESSAGE_QUEUE.put((request_id, query.query_params))

    # Wait for the WebSocket client to get a response and set the future's result
    response = await response_future

    return json.loads(response)
