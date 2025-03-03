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
            host = '10.160.5.178' #Server (i.e. Clover's laptop) has to be on
        )
        
        self.cursor = self.db.cursor()

    #Returns true or false if table exists or not
    def exists(self, name):
        stmt = "SHOW TABLES LIKE %s"
        args = (name,)
        self.cursor.execute(stmt, params=args)
        result = self.cursor.fetchone()
        if(result):
            return True
        else:
            return False

    #Create auto-incrementing table for computer part spec
    #When displaying data, JOIN on [category]_id, SELECT [spec].spec_name, or similar
    def create_spec_table(self, spec_name, var_name):
        if(not self.exists(spec_name)): #String literal must be used here
            stmt = f'CREATE TABLE {spec_name}(\
                    {var_name}_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    {var_name}_name VARCHAR(20))'

            self.cursor.execute(stmt, params=None)
            self.db.commit()

    #Create basic tables if they don't exist
    def create_tables(self):
        if not self.exists('products'):

            stmt = 'CREATE TABLE products(\
                    product_id INT NOT NULL AUTO_INCREMENT,\
                    product_name VARCHAR(20),\
                    category_id INT,\
                    PRIMARY KEY (product_id))'
            
            self.cursor.execute(stmt, params=None)
        
        if not self.exists('categories'):
            stmt = 'CREATE TABLE categories(\
                    category_id INT NOT NULL AUTO_INCREMENT,\
                    category_name VARCHAR(20),\
                    PRIMARY KEY (product_id))'
            
            self.cursor.execute(stmt, params=None)

    #Returns list of string tuples containing every product
    def get_products(self):
        stmt = 'SELECT products.product_name AS product, categories.category_name AS category\
                FROM products\
                INNER JOIN categories ON products.category_id=categories.category_id'
        self.cursor.execute(stmt, params=None)
        return self.cursor.fetchall()
    
    # Product IDs auto-increment; no need to add manually
    # Type of product specified by Category ID number (see below)
    def add_product(self, name, category_id):
        stmt = 'INSERT INTO products (product_name, category_id)\
                VALUES (%s, %s)'
        args = (name, category_id)
        self.cursor.execute(stmt, params=args)
        self.db.commit()
    
    # Category IDs auto-increment; no need to add manually
    # Category ID keys:
    # 1. GPU
    def add_category(self, category_name, *specifications):
        # stmt = 'INSERT INTO categories (category_name)\
        #         VALUES (%s)'
        # args = (category_name,)
        # self.cursor.execute(stmt, params=args)
        # self.db.commit()
        
        # for spec in specifications:
        #     self.create_spec_table(spec)
        
        stmt = f'CREATE TABLE {category_name} ('
        
        for i, spec in enumerate(specifications):
            stmt += f'{spec}_id INT NOT NULL'
            if not i == len(specifications) - 1:
                stmt += ', '
        else:
            stmt += ')'
            
        print(stmt)
            
        # self.cursor.execute(stmt, params=None)
        # self.db.commit()
    
    #TODO:  Add current inventory (num. of) column to products table
    #       Add way to quickly create item categories
    
    #Closes cursor and database upon program exit
    def __exit__(self):
        self.cursor.close()
        self.db.close()

if __name__ == '__main__':
    navi = Navigator() # Not supposed to be the actual interface
    
    print('add_category(a, b, c, d)')
    print(navi.add_category('a', 'b', 'c', 'd'))

    while(True):
        val = input('1. Get Products\n2. Add spec table\n3. Table exists\n4. Create new category\nx. Exit\n')

        if(val == '1'):
            products = navi.get_products()
            print(tabulate(products, headers=('name', 'category'))) 
        
        if(val == '2'):
            val = input('Enter spec name: ')
            val2 = input('Enter value name: ')
            navi.create_spec_table(val, val2)

        if(val == '3'):
            val = input('Enter table name: ')
            print(navi.exists(val))

        if(val == '4'):
            val = input('Create category name: ')
            navi.add_category(val)
            print('%s added to categories' % val)
        
        if(val == 'x'):
            break

        print()
    