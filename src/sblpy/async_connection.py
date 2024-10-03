"""
A basic async connection to a SurrealDB instance.
"""
import json
from typing import Optional, Dict, Any
import uuid

import websockets

from sblpy.query import Query


class AsyncSurrealConnection:
    """
    A single async connection to a SurrealDB instance. To be used once and discarded.

    # Notes
    A new connection is created for each query. This is because the async websocket connection is
    dropped

    Attributes:
        url: The URL of the database to process queries for.
        user: The username to login on.
        password: The password to login on.
        namespace: The namespace that the connection will stick to.
        database: The database that the connection will stick to.
        max_size: The maximum size of the connection.
        id: The ID of the connection.
    """
    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            namespace: str = "default",
            database: str = "default",
            max_size: int = 2 ** 20,
            encrypted: bool = False
    ) -> None:
        """
        The constructor for the AsyncSurrealConnection class.

        :param host: (str) the url of the database to process queries for
        :param port: (int) the port that the database is listening on
        :param user: (str) the username to login on
        :param password: (str) the password to login on
        :param namespace: (str) the namespace that the connection will stick to
        :param database: (str) The database that the connection will stick to
        :param max_size: (int) The maximum size of the connection
        :param encrypted: (bool) Whether the connection is encrypted
        """
        if encrypted is True:
            self.url: str = f"wss://{host}:{port}/rpc"
        else:
            self.url: str = f"ws://{host}:{port}/rpc"
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.namespace: str = namespace
        self.database: str = database
        self.max_size: int = max_size
        self.id: str = str(uuid.uuid4())

    async def signin(self, socket) -> None:
        """
        Signs in to the SurrealDB instance.

        :return: None
        """
        await socket.send(json.dumps(self.sign_params, ensure_ascii=False))
        response = json.loads(await socket.recv())
        if response.get("error") is not None:
            raise Exception(f"error signing in: {response.get('error')}")
        if response.get("result") is None:
            raise Exception(f"no result signing in: {response}")
        self.token = response["result"]
        if response.get("id") is None:
            raise Exception(f"no id signing in: {response}")
        self.id = response["id"]

    async def set_space(self, socket) -> None:
        """
        Sets the namespace and database for the connection.

        :return: None
        """
        await socket.send(json.dumps(self.use_params, ensure_ascii=False))
        _ = json.loads(await socket.recv())

    async def query(self, query: str, vars: Optional[Dict[str, Any]] = None) -> dict:
        """
        Queries the SurrealDB instance.

        :param query: The query to run
        :param vars: The variables to use in the query
        :return: The result of the query
        """
        query = Query(query, vars)

        async with websockets.connect(self.url, max_size=self.max_size) as websocket:
            # login and set the space
            await self.signin(websocket)
            await self.set_space(websocket)

            # send and receive the query
            await websocket.send(json.dumps(query.query_params, ensure_ascii=False))
            response = json.loads(await websocket.recv())
            if response.get("result") is None:
                raise Exception(f"error querying no result: {response}")
            response = response["result"]
            if response[0].get("status") is not None and response[0].get("status") == "ERR":
                raise Exception(f"error querying: {response[0].get('result')}")
        return response[0]["result"]

    @property
    def sign_params(self) -> dict:
        return {
            "id": self.id,
            "method": "signin",
            "params": [
                {
                    "user": self.user,
                    "pass": self.password
                }
            ]
        }

    @property
    def use_params(self) -> dict:
        return {
            "id": self.id,
            "method": "use",
            "params": [
                self.namespace,
                self.database
            ]
        }
