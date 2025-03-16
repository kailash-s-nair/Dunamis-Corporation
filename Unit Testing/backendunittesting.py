import unittest
from unittest.mock import patch, MagicMock, mock_open
import json

# Import your Navigator class from its module (adjust the module name as needed)
from navigator import Navigator

class TestNavigator(unittest.TestCase):

    def setUp(self):
        # Prepare a fake credentials JSON string.
        self.fake_credentials = {"user": "test_user", "password": "test_password"}
        credentials_str = json.dumps(self.fake_credentials)

        # Patch the built-in open so that reading the credentials file returns our fake credentials.
        self.open_patch = patch("builtins.open", mock_open(read_data=credentials_str))
        self.mock_open = self.open_patch.start()

        # Patch mysql.connector.connect so that it returns a fake connection.
        self.mysql_patch = patch("mysql.connector.connect")
        self.mock_mysql_connect = self.mysql_patch.start()

        # Create a fake database connection and cursor.
        self.fake_cursor = MagicMock()
        self.fake_db = MagicMock()
        self.fake_db.cursor.return_value = self.fake_cursor
        self.mock_mysql_connect.return_value = self.fake_db

        # Now when Navigator() is instantiated, it will use the patched open() and mysql.connector.connect()
        self.navigator = Navigator()

    def tearDown(self):
        # Stop all patches.
        self.open_patch.stop()
        self.mysql_patch.stop()

    def test_exists_returns_true(self):
        # Simulate that the table exists by having fetchone() return a non-empty tuple.
        self.fake_cursor.fetchone.return_value = ("existing_table",)
        result = self.navigator.exists("existing_table")
        self.assertTrue(result)
        # Ensure the proper SQL statement was used.
        self.fake_cursor.execute.assert_called_once_with("SHOW TABLES LIKE %s", params=("existing_table",))

    def test_exists_returns_false(self):
        # Simulate no matching table (fetchone() returns None).
        self.fake_cursor.fetchone.return_value = None
        result = self.navigator.exists("nonexistent_table")
        self.assertFalse(result)

    def test_create_spec_table_creates_table_when_not_exists(self):
        # Force exists() to return False.
        self.navigator.exists = MagicMock(return_value=False)
        self.navigator.create_spec_table("spec_table")
        # Check that a CREATE TABLE statement was executed and commit was called.
        self.fake_cursor.execute.assert_called()
        self.fake_db.commit.assert_called()

    def test_create_spec_table_raises_when_table_exists(self):
        # Force exists() to return True so that create_spec_table should raise an error.
        self.navigator.exists = MagicMock(return_value=True)
        with self.assertRaises(RuntimeError):
            self.navigator.create_spec_table("spec_table")
        
if __name__ == '__main__':
    unittest.main()
