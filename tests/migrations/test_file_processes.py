import os
import shutil
import tempfile
from unittest import TestCase, main

from sblpy.migrations.file_processes import setup_migration_directories, generate_new


class TestMigrationDirectories(TestCase):

    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Remove the temporary directory after the test
        shutil.rmtree(self.test_dir)

    def test_migration_directories(self):
        # Call the function to set up migration directories
        setup_migration_directories(self.test_dir)

        # Check if surreal_migrations directory exists
        surreal_migrations_path = os.path.join(self.test_dir, 'surreal_migrations')
        self.assertTrue(os.path.isdir(surreal_migrations_path))

        # Check if "up" and "down" directories exist
        up_path = os.path.join(surreal_migrations_path, 'up')
        down_path = os.path.join(surreal_migrations_path, 'down')
        self.assertTrue(os.path.isdir(up_path))
        self.assertTrue(os.path.isdir(down_path))

        # Check if "1.sql" files exist in both directories
        up_sql_file = os.path.join(up_path, '1.sql')
        down_sql_file = os.path.join(down_path, '1.sql')
        self.assertTrue(os.path.isfile(up_sql_file))
        self.assertTrue(os.path.isfile(down_sql_file))

    def test_generate_new(self):
        # First, set up the initial migration directories
        setup_migration_directories(self.test_dir)

        # Call generate_new to create a new set of "2.sql" files
        generate_new(self.test_dir)

        # Check if "2.sql" files were created in "up" and "down" directories
        surreal_migrations_path = os.path.join(self.test_dir, 'surreal_migrations')
        up_sql_file = os.path.join(surreal_migrations_path, 'up', '2.sql')
        down_sql_file = os.path.join(surreal_migrations_path, 'down', '2.sql')
        self.assertTrue(os.path.isfile(up_sql_file))
        self.assertTrue(os.path.isfile(down_sql_file))


if __name__ == '__main__':
    main()
