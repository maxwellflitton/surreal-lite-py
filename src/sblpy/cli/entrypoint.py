"""
This module contains the entrypoint for the command line tool.
"""
import argparse
import os
import json

from sblpy.connection import SurrealSyncConnection
from sblpy.migrations.db_processes import get_latest_version
from sblpy.migrations.file_processes import setup_migration_directories, generate_new, get_migrations
from sblpy.migrations.runner import MigrationRunner
from sblpy.query import Query


def main() -> None:
    parser = argparse.ArgumentParser(description="Command line tool for database migrations.")

    # Add the first two positional arguments
    parser.add_argument('command', choices=['migrations', "run"], help="The main command (e.g., 'migrations', 'run').")
    parser.add_argument(
        'subcommand',
        help="The subcommand (e.g., 'up', 'down', 'create', 'run', 'version')."
    )

    # Add the optional arguments with flags
    parser.add_argument('-ho', '--host', required=False, help="The database host.", default="localhost")
    parser.add_argument('-p', '--port', required=False, help="The database port.", default=8000)
    parser.add_argument('-u', '--user', required=False, help="The database user.", default="root")
    parser.add_argument('-pw', '--password', required=False, help="The database password.", default="root")
    parser.add_argument('-ns', '--namespace', required=False, help="The database namespace.", default="default")
    parser.add_argument('-d', '--database', required=False, help="The database name.", default="default")
    parser.add_argument('-f', '--file', required=False, help="Pointer to SQL file", default="main.sql")
    args = parser.parse_args()

    current_working_directory = str(os.getcwd())

    if args.command == "migrations":
        if args.subcommand == "up":
            connection = SurrealSyncConnection(
                args.host,
                args.port,
                args.user,
                args.password,
                args.namespace,
                args.database
            )
            runner = MigrationRunner(
                up_migrations=get_migrations(current_working_directory, True),
                down_migrations=get_migrations(current_working_directory, False),
                connection=connection
            )
            runner.increment()

        elif args.subcommand == "down":
            connection = SurrealSyncConnection(
                args.host,
                args.port,
                args.user,
                args.password,
                args.namespace,
                args.database
            )
            runner = MigrationRunner(
                up_migrations=get_migrations(current_working_directory, True),
                down_migrations=get_migrations(current_working_directory, False),
                connection=connection
            )
            runner.decrement()
        elif args.subcommand == "create":
            if not os.path.exists(f"{current_working_directory}/surreal_migrations"):
                setup_migration_directories(current_working_directory)
            else:
                generate_new(current_working_directory)
        elif args.subcommand == "run":
            connection = SurrealSyncConnection(
                args.host,
                args.port,
                args.user,
                args.password,
                args.namespace,
                args.database
            )
            runner = MigrationRunner(
                up_migrations=get_migrations(current_working_directory, True),
                down_migrations=get_migrations(current_working_directory, False),
                connection=connection
            )
            runner.run()
        elif args.subcommand == "version":
            connection = SurrealSyncConnection(
                args.host,
                args.port,
                args.user,
                args.password,
                args.namespace,
                args.database
            )
            version = get_latest_version(
                connection.host,
                connection.port,
                connection.user,
                connection.password
            )
            print(f"Current version: {version}")
        else:
            print(
                f"{args.subcommand} subcommand not recognized for migrations"
                f" command. Please use 'up', 'down', 'create', 'run', or 'version'."
            )
    elif args.command == "run":
        if args.subcommand == "sql":
            connection = SurrealSyncConnection(
                args.host,
                args.port,
                args.user,
                args.password,
                args.namespace,
                args.database
            )
            query = Query.from_file(args.file)
            print(connection.query(query.sql))
