"""
Defines the Migration class where we can run migrations on the database. These migration objects can be constructed
from strings, docstrings, lists, or files. The run method executes the migration on the database and bumps the version
or decreases the version based on the bump parameter.
"""
from typing import List, Optional

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import bump_version, lower_version
from sblpy.sql_adapter import SqlAdapter


class Migration:
    """
    Handles the migration transaction on the database.

    Attributes:
        sql: The SQL commands to be executed on the database.
    """
    def __init__(self) -> None:
        """
        The constructor for the Migration class.
        """
        self.sql: Optional[str] = None

    @staticmethod
    def from_docstring(docstring: str) -> "Migration":
        """
        Creates a Migration object from a docstring.

        :param docstring: (str) the docstring to create the migration from
        :return: (Self) the migration object created from the docstring
        """
        migration = Migration()
        migration.sql = SqlAdapter.from_docstring(docstring=docstring)
        return migration

    @staticmethod
    def from_list(commands: List[str]) -> "Migration":
        """
        Creates a Migration object from a list of commands.

        :param commands: (List[str]) the list of commands to create the migration from
        :return: (Self) the migration object created from the list of commands
        """
        migration = Migration()
        migration.sql = SqlAdapter.from_list(commands=commands)
        return migration

    @staticmethod
    def from_file(file_path: str) -> "Migration":
        """
        Creates a Migration object from a file.

        :param file_path: (str) the path to the file to create the migration from
        :return: (Self) the migration object created from the file
        """
        migration = Migration()
        migration.sql = SqlAdapter.from_file(file_path=file_path)
        return migration

    def run(self, connection: SurrealSyncConnection, bump=True) -> None:
        """
        Runs the migration on the database.

        :param connection: (SurrealSyncConnection) the connection to the database to run the migration on
        :param bump: (bool) whether to bump the version or lower the version
        :return: None
        """
        # for query in self.sql:
        connection.query(self.sql)
        if bump:
            bump_version(
                connection.host,
                connection.port,
                connection.user,
                connection.password,
                connection.namespace,
                connection.database
            )
        else:
            lower_version(
                connection.host,
                connection.port,
                connection.user,
                connection.password,
                connection.namespace,
                connection.database
            )

    def __str__(self) -> str:
        return "\n".join(self.sql)
