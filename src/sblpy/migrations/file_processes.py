"""
This module contains functions for managing the migration directories and files.
"""
import os
from sblpy.migrations.migrations import Migration


def setup_migration_directories(base_path) -> None:
    """
    Creates the necessary directories and files for managing migrations.

    :param base_path: (str) the base path to create the directories and files in
    :return: None
    """
    # Define the directory paths
    surreal_migrations_path = os.path.join(base_path, 'surreal_migrations')
    up_path = os.path.join(surreal_migrations_path, 'up')
    down_path = os.path.join(surreal_migrations_path, 'down')

    # Check if surreal_migrations directory exists, if not, create it
    if not os.path.exists(surreal_migrations_path):
        os.makedirs(surreal_migrations_path)
        print(f"Created directory: {surreal_migrations_path}")

    # Create the "up" directory if it doesn't exist
    if not os.path.exists(up_path):
        os.makedirs(up_path)
        print(f"Created directory: {up_path}")

    # Create the "down" directory if it doesn't exist
    if not os.path.exists(down_path):
        os.makedirs(down_path)
        print(f"Created directory: {down_path}")

    # Create "1.sql" file in both "up" and "down" directories
    up_sql_file = os.path.join(up_path, '1.sql')
    down_sql_file = os.path.join(down_path, '1.sql')

    # Create "1.sql" in "up" directory if it doesn't exist
    if not os.path.exists(up_sql_file):
        with open(up_sql_file, 'w') as f:
            f.close()
        print(f"Created file: {up_sql_file}")

    # Create "1.sql" in "down" directory if it doesn't exist
    if not os.path.exists(down_sql_file):
        with open(down_sql_file, 'w') as f:
            f.close()
        print(f"Created file: {down_sql_file}")


def get_highest_sql_file_number(directory) -> int:
    """
    Get the highest number from the SQL files in the given directory.

    :param directory: (str) the directory to search for SQL files
    :return: (int) the highest number found in the SQL files
    """
    numbers = get_all_versions(directory)
    # Return the highest number or 0 if no files exist
    return max(numbers) if numbers else 0


def get_all_versions(directory) -> list[int]:
    """
    Get a list of all the version numbers from the SQL files in the given directory.

    :param directory: (str) the directory to search for SQL files
    :return: (list[int]) a list of all the version numbers found in the SQL files
    """
    # Get a list of all .sql files in the directory
    sql_files = [f for f in os.listdir(directory) if f.endswith('.sql')]

    # Extract the number from each file, assume filenames like "1.sql"
    numbers = []
    for file in sql_files:
        try:
            number = int(file.split('.')[0])
            numbers.append(number)
        except ValueError:
            continue  # In case the filename isn't a number followed by .sql

    # Return the list of all numbers
    return numbers


def generate_new(base_path: str) -> None:
    """
    Generate new SQL files in the "up" and "down" directories.

    :param base_path: (str) the base path to create the new SQL files in
    :return: None
    """
    # Define the paths to the "up" and "down" directories
    surreal_migrations_path = os.path.join(base_path, 'surreal_migrations')
    up_path = os.path.join(surreal_migrations_path, 'up')
    down_path = os.path.join(surreal_migrations_path, 'down')

    # Get the highest numbered SQL file in both directories
    highest_up = get_highest_sql_file_number(up_path)
    highest_down = get_highest_sql_file_number(down_path)

    # Increment by 1 to get the next number
    new_file_number = max(highest_up, highest_down) + 1

    # Create new SQL file in "up" directory
    new_up_file = os.path.join(up_path, f'{new_file_number}.sql')
    with open(new_up_file, 'w') as f:
        f.close()
    print(f"Created file: {new_up_file}")

    # Create new SQL file in "down" directory
    new_down_file = os.path.join(down_path, f'{new_file_number}.sql')
    with open(new_down_file, 'w') as f:
        f.close()
    print(f"Created file: {new_down_file}")


def get_migrations(base_path: str, up=True) -> list[Migration]:
    """
    Get a list of all the "up" migration files.

    :param base_path: (str) the base path to search for "up" migration files
    :param up: (bool) whether to get the "up" or "down" migrations
    :return: (list[Migration]) a list of all the "up" migrations
    """
    # Define the path to the "up" directory
    mg_dir = 'up' if up else 'down'
    mg_path = os.path.join(base_path, 'surreal_migrations', mg_dir)

    # Get a list of all .sql files in the "up" directory
    files = [f for f in os.listdir(mg_path) if f.endswith('.sql')]
    files.sort()
    paths = [os.path.join(mg_path, f) for f in files]
    buffer = []
    # Create a Migration object for each file
    for path in paths:
        buffer.append(Migration.from_file(path))
    return buffer
