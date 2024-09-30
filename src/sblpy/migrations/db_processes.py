"""
Defines the functions that interact with the database to manage the migrations table in the database
"""
from sblpy.connection import SurrealSyncConnection


def lower_version(
            host: str,
            port: int,
            user: str,
            password: str,
            namespace="default",
            database="default"
    ) -> None:
    """
    Lowers the version of the database by deleting the latest version from the migrations table.

    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will run the migration on
    :param database: (str) The database that the connection will run the migration on
    :return: None
    """
    version = get_latest_version(
        host,
        port,
        user,
        password,
        namespace,
        database
    )
    with SurrealSyncConnection(
            host,
            port,
            user,
            password,
            namespace,
            database
    ) as connection:
        outcome = connection.query(
            f"DELETE _sbl_migrations:{version};"
        )


def bump_version(
            host: str,
            port: int,
            user: str,
            password: str,
            namespace="default",
            database="default"
    ) -> None:
    """
    Bumps the version of the database by adding a new version to the migrations table.

    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will run the migration on
    :param database: (str) The database that the connection will run the migration on
    :return: None
    """
    version = get_latest_version(
        host,
        port,
        user,
        password,
        namespace,
        database
    ) + 1
    with SurrealSyncConnection(
            host,
            port,
            user,
            password,
            namespace,
            database
    ) as connection:
        outcome = connection.query(
            f"CREATE _sbl_migrations:{version} SET version = {version}, applied_at = time::now();"
        )


def get_latest_version(
            host: str,
            port: int,
            user: str,
            password: str,
            namespace="default",
            database="default"
    ) -> int:
    """
    Gets the latest version of the database from the migrations table.

    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will run the migration on
    :param database: (str) The database that the connection will run the migration on
    :return: (int) the latest version of the database (0 if no versions exist)
    """
    versions = get_all_versions(
        host,
        port,
        user,
        password,
        namespace,
        database
    )
    if len(versions) == 0:
        return 0
    return versions[-1]["version"]


def get_all_versions(
            host: str,
            port: int,
            user: str,
            password: str,
            namespace="default",
            database="default"
    ):
    """
    Gets all versions of the database from the migrations table.

    :param host: (str) the url of the database to process queries for
    :param port: (int) the port that the database is listening on
    :param user: (str) the username to login on
    :param password: (str) the password to login on
    :param namespace: (str) the namespace that the connection will run the migration on
    :param database: (str) The database that the connection will run the migration on
    :return: (list) a list of dictionaries containing the version and applied_at timestamp
    """
    with SurrealSyncConnection(
            host,
            port,
            user,
            password,
            namespace,
            database
    ) as connection:
        outcome = connection.query("SELECT * FROM _sbl_migrations;")
    return outcome
