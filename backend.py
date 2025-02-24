import mysql.connector
import json
from tabulate import tabulate

class Navigator:
    #Loads credentials, accesses database, creates cursor to database
    def __init__(self):
        with open('very secure credentials folder/credentials.json', 'r') as file:
            cred = json.load(file)
        
        self.db = mysql.connector.connect(
            user=cred.get('user'),
            password = cred.get('password'),
            database = 'items_database',
            host = '172.29.160.1'
        )
        
        self.cursor = self.db.cursor()

    #Returns list of tuples containing every product
    def get_products(self):
        stmt = 'SELECT products.product_name AS product, categories.category_name AS category\
                FROM products\
                INNER JOIN categories ON products.category_id=categories.category_id;'
        self.cursor.execute(stmt, params=None)
        return self.cursor.fetchall()
    
    # Product IDs auto-increment; no need to add manually
    # Type of product specified by Category ID number (see below)
    def add_product(self, name, category_id):
        stmt = 'INSERT INTO products (product_name, category_id) VALUES (%s %s)'
        args = (name, category_id)
        self.cursor.execute(stmt, params=args)
        self.db.commit()
    
    # Category IDS auto-increment; no need to add manually
    # Category ID keys:
    # 1. GPU
    def add_category(self, category_name):
        stmt = 'INSERT INTO products (category_name) VALUES (%s)'
        args = (category_name)
        self.cursor.execute(stmt, params=args)
        self.db.commit()
    
    def __exit__(self):
        self.cursor.close()
        self.db.close()

if __name__ == '__main__':
    navi = Navigator()
    products = navi.get_products()
    print(tabulate(products, headers=('name', 'category'))) # Not supposed to be the actual interface