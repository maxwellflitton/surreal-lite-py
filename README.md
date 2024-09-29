# surreal-lite-py
An unofficial Python API for surrealDB that only has one dependency (websockets) and has a very simple interface. One interface is a blocking isolated query interface, and the other is an async connection pool interface.

## Async Connection Pool Interface
You can spin up an async connection pool and make requests using the code below:
```python
import asyncio

from sblpy.pool.connection_pool import execute_pooled_query, client_pool, shutdown_pool
from sblpy.query import Query


async def main():
    # Create a pool of 5 clients
    asyncio.create_task(client_pool(
        host="localhost",
        port=8000,
        user="root",
        password="root",
        number_of_clients=5
    ))

    # make 400 requests
    for _ in range(100):
        _ = await execute_pooled_query(Query("CREATE user:tobie SET name = 'Tobie';"))
        _ = await execute_pooled_query(Query("CREATE user:jaime SET name = 'Jaime';"))
        response = await execute_pooled_query(Query("SELECT * FROM user;"))
        print(response)
        _ = await execute_pooled_query(Query("DELETE user;"))

    # Shutdown the pool    
    await shutdown_pool(number_of_clients=5)

if __name__ == "__main__":
    asyncio.run(main())
```

Here we can see that we pass in a `Query` object that defines the query and the params if they are also passed into the `Query` object constructor. If you print this you can also see that the response is raw. In the integration tests you can see how to parse this response using `response["result"][0]["result"]` This is because we do not want any serialization errors happening in the connection pool. You have control over how you handle the response. This can also help isolate against breaking changes in the future. 

## Basic Blocking Interface
We can create a basic blocking interface using the code below:
```python
from sblpy.connection import SurrealSyncConnection

connection = SurrealSyncConnection(
            host="localhost",
            port=8000,
            user="root",
            password="root"
        )

_ = connection.query("CREATE user:tobie SET name = 'Tobie';")
_ = connection.query("CREATE user:jaime SET name = 'Jaime';")
outcome = connection.query("SELECT * FROM user;")
print(outcome)
```

Here you will see that the response is a lot smoother. This is because if there are any errors or issue with parsing, we can directly throw them as the connection is going to close anyway once the connection goes out of scope. The python garbage collector will take care of cleaning up the connection but this will be delayed. If you want to ensure that the connection is closed, you can call `connection.socket.close()` to close the connection.

## Future Plans

There isn't much, this is just a super simple API. The less moving parts the less that can go wrong. I want to keep the dependencies to a minimum and the codebase as simple as possible. However, I do want to add the following features:

- [ ] Migration tool with command line interface
