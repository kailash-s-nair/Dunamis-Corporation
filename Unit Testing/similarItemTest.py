import unittest
from backend import Navigator 

class similarItemTest(unittest.TestCase):
    def setUpClass(cls):
        # Initialize Navigator instance; this loads credentials and connects to the database.
        cls.navigator = Navigator()
        cls.test_table = 'test_table'
        cursor = cls.navigator.cursor

        # Create a temporary test table with two columns: id and name.
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {cls.test_table} (
                id INT NOT NULL AUTO_INCREMENT,
                name VARCHAR(50),
                PRIMARY KEY (id)
            )
        """)
        cls.navigator.db.commit()

        #Insert a test record into the temporary table.
        cursor.execute(f"INSERT INTO {cls.test_table} (name) VALUES (%s)", ('test_item',))
        cls.navigator.db.commit()

    def tearDownClass(cls):
        #Close the database connection.
        cursor = cls.navigator.cursor
        cursor.execute(f"DROP TABLE IF EXISTS {cls.test_table}")
        cls.navigator.db.commit()
        cls.navigator.cursor.close()
        cls.navigator.db.close()

    def test_basic_item_search(self):
        #Searching for an item known to exist ("test_item") should return an ID.
        item_id = self.navigator.name_exists_in_table(self.test_table, 'name', 'id', 'test_item')
        self.assertIsNotNone(item_id, "The item 'test_item' should exist and return an id.")

        #Searching for a non-existent item ("fake_item") should return None.
        non_existent = self.navigator.name_exists_in_table(self.test_table, 'name', 'id', 'fake_item')
        self.assertIsNone(non_existent, "The item 'fake_item' should not be found in the table.")

    def test_similar_item_search(self):
        #Searching for an item close to the item that exists ("test_item") should return an ID.
        item_id = self.navigator.name_exists_in_table(self.test_table, 'name', 'id', 'tset_item')
        self.assertIsNotNone(item_id, "The item 'tset_item' should return the id of test_item.")

        #Searching for a ("test_item") again, with a different item name.
        non_existent = self.navigator.name_exists_in_table(self.test_table, 'name', 'id', 'testitem')
        self.assertIsNone(non_existent, "The item 'fake_item' should not be found in the table.")


if __name__ == '__main__':
    unittest.main()
