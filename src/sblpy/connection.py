"""
A basic synchronous connection to a SurrealDB instance.
"""
import json
import uuid
from types import TracebackType
from typing import Optional, Dict, Any, Type

from websockets.sync.client import connect

from sblpy.query import Query


class SurrealSyncConnection:
    """
    A basic synchronous connection to a SurrealDB instance.

    Attributes:
        url: The URL of the database to process queries for.
        user: The username to login on.
        password: The password to login on.
        namespace: The namespace that the connection will stick to.
        database: The database that the connection will stick to.
        socket: The WebSocket connection to the SurrealDB instance.
        id: The ID of the connection.
        token: The token of the connection.
    """
    def __init__(
            self,
            host: str,
            port: int,
            user: str,
            password: str,
            namespace = "default",
            database = "default"
    ) -> None:
        """
        The constructor for the SurrealSyncConnection class.

        :param host: (str) the url of the database to process queries for
        :param port: (int) the port that the database is listening on
        :param user: (str) the username to login on
        :param password: (str) the password to login on
        :param namespace: (str) the namespace that the connection will stick to
        :param database: (str) The database that the connection will stick to
        """
        self.url: str = f"ws://{host}:{port}/rpc"
        self.host: str = host
        self.port: int = port
        self.user: str = user
        self.password: str = password
        self.namespace: str = namespace
        self.database: str = database
        self.socket = connect(self.url)
        self.id: str = str(uuid.uuid4())
        self.token: Optional[str] = None
        self.signin()
        self.set_space()

    def signin(self) -> None:
        """
        Signs in to the SurrealDB instance.

        :return: None
        """
        self.socket.send(json.dumps(self.sign_params, ensure_ascii=False))
        response = json.loads(self.socket.recv())
        if response.get("error") is not None:
            raise Exception(f"error signing in: {response.get('error')}")
        if response.get("result") is None:
            raise Exception(f"no result signing in: {response}")
        self.token = response["result"]
        if response.get("id") is None:
            raise Exception(f"no id signing in: {response}")
        self.id = response["id"]

    def set_space(self) -> None:
        """
        Sets the namespace and database for the connection.

        :return: None
        """
        self.socket.send(json.dumps(self.use_params, ensure_ascii=False))
        _ = json.loads(self.socket.recv())

    def query(self, query: str, vars: Optional[Dict[str, Any]] = None) -> dict:
        """
        Queries the SurrealDB instance.

        :param query: The query to run
        :param vars: The variables to use in the query
        :return: The result of the query
        """
        query = Query(query, vars)
        self.socket.send(json.dumps(query.query_params, ensure_ascii=False))
        response = json.loads(self.socket.recv())
        if response.get("result") is None:
            raise Exception(f"error querying no result: {response}")
        response = response["result"]
        if response[0].get("status") is not None and response[0].get("status") == "ERR":
            raise Exception(f"error querying: {response[0].get('result')}")
        return response[0]["result"]

    def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]] = None,
            exc_value: Optional[Type[BaseException]] = None,
            traceback: Optional[Type[TracebackType]] = None,
    ) -> None:
        """Close the connection when exiting the context manager.

        Args:
            exc_type: The type of the exception.
            exc_value: The value of the exception.
            traceback: The traceback of the exception.
        """
        self.socket.close()

    def __enter__(self) -> "SurrealSyncConnection":
        """No-op for entering the context manager since the connection is established during __init__."""
        return self

    def __exit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:
        """Closes the connection when exiting the context manager."""
        self.socket.close()

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
