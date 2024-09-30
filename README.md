# surreal-lite-py
An unofficial Python API for surrealDB that only has one dependency (websockets) and has a very simple interface. One interface is a blocking isolated query interface, and the other is an async connection pool interface.

## Contents in order of appearance

- [Installation](#installation)
- [Async Connection Pool Interface](#async-connection-pool-interface)
- [Basic Blocking Interface](#basic-blocking-interface)
- [Migrations via command line](#migrations-via-command-line)
- [Run SQL scripts via command line](#run-sql-scripts-via-command-line)
- [Command line parameters](#command-line-parameters)
- [Migrations via python code](#migrations-via-python-code)
- [Future Plans](#future-plans)

## Installation
You can install the package using the following command:
```bash
pip install sdblpy
```

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

<!-- - [Migrations via command line](#migrations-via-command-line)
- [Migrations via python code](#migrations-via-python-code)
- [Run SQL scripts via command line](#run-sql-scripts-via-command-line) -->

## Migrations via command line

You can run migrations via the command line. First we must setup the migrations folder with the following command:

```bash
sdblpy migrations create
```

This creates the following folder structure in the current working directory:

```
└── surreal_migrations
    ├── down
    │   └── 1.sql
    └── up
        └── 1.sql

```

If we run the same `sdblpy migrations create` again we will get another migration file with number 2 as seen below:

```
└── surreal_migrations
    ├── down
    │   ├── 1.sql
    │   └── 2.sql
    └── up
        ├── 1.sql
        └── 2.sql
```

We can now make some simple migrations in the sql scripts:

```sql
-- surreal_migrations/up/1.sql
CREATE user:tobie SET name = 'Tobie';
```

```sql
-- surreal_migrations/down/1.sql
DELETE user:tobie;
```

```sql
-- surreal_migrations/up/2.sql
CREATE user:jaime SET name = 'Jaime';
```

```sql
-- surreal_migrations/down/2.sql
DELETE user:jaime;
```

Before we run any migrations, we must ensure that the database is running and we also must check the migrations version of the database. We can do this with the following command:

```bash
sdblpy migrations version -ho localhost -p 8000 -u root -pw root -ns default -d default
```

And this gives us the following output:

```
Current version: 0
```

We can see that we are at version `0`. If we refer to the [command line parameters table section](#command-line-parameters) we can see that we passed in all default values so the `sdblpy migrations version` command will also just work if your server is running on the default values.

We can now run all the migrations with the following command:

```bash
sdblpy migrations run
```

Running the `sdblpy migrations version` command again will give us the following output:

```
Current version: 2
```

Here we can see that our migrations have run successfully as the `sdblpy migrations run` gets the current version of the database and runs all the migrations that are greater than the current version. We can also decrement the version by one with the following command:

```bash
sdblpy migrations down
```

Our version is now down to `1` if we run the `sdblpy migrations version` command again. We can bump up the version of our database by one with the following command:

```bash
sdblpy migrations up
```

Our version is now up to `2` if we run the `sdblpy migrations version` command again. But lets double check that the migrations have actually run by running SQL scripts in the command line.

## Run SQL scripts via command line

We can run SQL scripts against the database using the command line. First, lets create a simple SQL script called `main.sql` in our current working directory:

```sql
-- main.sql
SELECT * FROM user;
```
If our database has the migrations run in the previous section, then we should see both users come back from the table. We can run the SQL script with the following command:

```bash
sdblpy run sql -f main.sql
```

Provided that the database is running the default parameters otherwise you will have to add them as additional arguments after the `sdblpy run sql` command, we should get the following:

```
[{'id': 'user:jaime', 'name': 'Jaime'}, {'id': 'user:tobie', 'name': 'Tobie'}]
```

What happens here is the SQL script is run against the database and the response is printed to the console. This is a very simple way to run SQL scripts against the database.

## Command line parameters

Below are the command line parameters that can be passed to the `sdblpy` command:

| Argument            | Flags               | Required  | Default      | Description                                           |
|---------------------|---------------------|-----------|--------------|-------------------------------------------------------|
| `command`           |                     | Yes       |              | The main command (e.g., 'migrations', 'run').          |
| `subcommand`        |                     | Yes       |              | The subcommand (e.g., 'up', 'down', 'create', 'run', 'version'). |
| `--host`            | `-ho`, `--host`     | No        | `localhost`  | The database host.                                    |
| `--port`            | `-p`, `--port`      | No        | `8000`       | The database port.                                    |
| `--user`            | `-u`, `--user`      | No        | `root`       | The database user.                                    |
| `--password`        | `-pw`, `--password` | No        | `root`       | The database password.                                |
| `--namespace`       | `-ns`, `--namespace`| No        | `default`    | The database namespace.                               |
| `--database`        | `-d`, `--database`  | No        | `default`    | The database name.                                    |
| `--file`            | `-f`, `--file`      | No        | `main.sql`   | Pointer to SQL file.                                  |


## Migrations via python code

We can define and run migrations directly in the python code. Migrations can come from a string, list of strings, or a file. Below is an example of how we can construct a migration:

```python
from sblpy.migrations.migrations import Migration


migration_one = Migration.from_docstring("""
            CREATE user:tobie SET name = 'Tobie';
            CREATE user:jaime SET name = 'Jaime';
        """)

migration_two = Migration.from_list([
            "CREATE user:tobie SET name = 'Tobie';",
            "CREATE user:jaime SET name = 'Jaime'"
        ])

migration_three = Migration.from_file("./some/path/to/file.sql")
```

Once we have these migrations, we need a runner that gets the version of of the database, and then performs migration operations. These operations are the exact same code that the command line interface uses. Below is an example of how we can run migrations:

```python
from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.migrations import Migration
from sblpy.migrations.runner import MigrationRunner
from sblpy.migrations.db_processes import get_latest_version

# define the connection used to run the migrations
connection = SurrealSyncConnection(
    host="localhost",
    port=8000,
    user="root",
    password="root"
)

# define the migrations and the order of the migrations 
up_migrations = [
    Migration.from_docstring("""CREATE user:tobie SET name = 'Tobie';"""), # version 1
    Migration.from_docstring("""CREATE user:jaime SET name = 'Jaime';""") # version 2
]

down_migrations = [
    Migration.from_docstring("""DELETE user:tobie;"""), # version 1
    Migration.from_docstring("""DELETE user:jaime;""") # version 2
]

# define the migration runner
runner = MigrationRunner(
    up_migrations=up_migrations,
    down_migrations=down_migrations,
    connection=connection
)

# run the migrations
runner.run()

# decrement the version by one
runner.decrement()

# increment the version by one
runner.increment()

# get the latest version of the database
latest_version: int = get_latest_version(
    connection.connection.host,
    connection.connection.port,
    connection.connection.user,
    connection.connection.password
)
```

And with this we can run migrations directly in our python. For instance, it is a good idea to run migrations in the `setUp` and `tearDown` methods of a test class when building your own unit tests. You can also run your own migrations in the `main` method of your application before the server starts. This will ensure that the database is in the correct state before the server starts without having to run the migrations manually in a separate terminal or init pod.

## Future Plans

There isn't much, this is just a super simple API. The less moving parts the less that can go wrong. I want to keep the dependencies to a minimum and the codebase as simple as possible. However, I do want to add the following features:

- [ ] Migration tool with command line interface
