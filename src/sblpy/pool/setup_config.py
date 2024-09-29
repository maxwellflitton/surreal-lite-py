"""
Sets up the pooled connection.
"""
import json


async def setup_connection(
    websocket,
    id: str,
    user: str,
    password: str,
    namespace: str,
    database: str
) -> None:
    """
    Sets up the connection ready to be used by logging in and defining the namespace and database.

    :param websocket: (Websocket) the connection that is going to be bound to the async task.
    :param id: (str) the ID of the connection actor
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will stick to
    :param database: (str) The database that the connection will stick to
    :return:
    """
    sign_params = {
        "id": id,
        "method": "signin",
        "params": [
            {
                "user": user,
                "pass": password
            }
        ]
    }
    # Send the sign-in message
    await websocket.send(json.dumps(sign_params, ensure_ascii=False))
    response = await websocket.recv()
    response = json.loads(response)

    if response.get("error") is not None:
        raise Exception(f"Error signing in: {response.get('error')}")
    if response.get("result") is None:
        raise Exception(f"No result signing in: {response}")
    if response.get("id") is None:
        raise Exception(f"No id signing in: {response}")
    id = response["id"]

    use_params = {
        "id": id,
        "method": "use",
        "params": [
            namespace,
            database
        ]
    }

    await websocket.send(json.dumps(use_params, ensure_ascii=False))
    await websocket.recv()
