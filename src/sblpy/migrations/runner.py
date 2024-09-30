"""
Defines the MigrationRunner class, which is responsible for gathering and running migrations.
"""
from typing import List

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import get_latest_version
from sblpy.migrations.migrations import Migration


class MigrationRunner:
    """
    Handles the running of migrations on the database.

    Attributes:
        up_migrations: The migrations to run in the up direction.
        down_migrations: The migrations to run in the down direction.
        connection: The connection to the database to run the migrations on.
        version: The current version of the database.
        index: The index of the migration to run.
    """
    def __init__(
            self,
            up_migrations: List[Migration],
            down_migrations: List[Migration],
            connection: SurrealSyncConnection
    ) -> None:
        """
        The constructor for the MigrationRunner class.

        :param up_migrations: (List[Migration]) the list of migrations to run in the up direction
        :param down_migrations: (List[Migration]) the list of migrations to run in the down direction
        :param connection: (SurrealSyncConnection) the connection to the database to run the migrations on
        """
        self.up_migrations: List[Migration] = up_migrations
        self.down_migrations: List[Migration] = down_migrations
        self.connection: SurrealSyncConnection = connection
        self.version: int = get_latest_version(
            connection.host,
            connection.port,
            connection.user,
            connection.password
        )
        if self.version == 0:
            self.index = 0
        else:
            self.index: int = self.version - 1

    def run(self) -> None:
        """
        Runs all migrations in the up direction.

        :return: None
        """
        for i in range(self.index, len(self.up_migrations)):
            self.up_migrations[i].run(self.connection, bump=True)
            self.index += 1
            self.version += 1

    def increment(self) -> None:
        """
        Increments the version of the database and runs the next up migration.

        :return: None
        """
        if self.version == len(self.up_migrations):
            return
        self.up_migrations[self.version].run(self.connection, bump=True)
        self.version += 1
        self.index += 1

    def decrement(self) -> None:
        """
        Decrements the version of the database and runs the previous down migration.

        :return: None
        """
        if self.version == 0:
            return
        self.down_migrations[self.index].run(self.connection, bump=False)
        self.version -= 1
        self.index -= 1
