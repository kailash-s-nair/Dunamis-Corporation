import mysql.connector
import json
import socket
from tabulate import tabulate

class Navigator:
    #Loads credentials, accesses database, creates cursor to database
    def __init__(self):
        with open('very secure credentials folder/credentials.json', 'r') as file:
            cred = json.load(file)
        
        hostname = socket.gethostname()
        
        self.db = mysql.connector.connect(
            user=cred.get('user'),
            password = cred.get('password'),
            database = 'items_database',
            host = socket.gethostbyname(hostname) #Server (i.e. Clover's laptop) has to be on
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
                    product_name VARCHAR(20) NOT NULL,\
                    category_id INT NOT NULL,\
                    PRIMARY KEY (product_id))'
            
            self.cursor.execute(stmt, params=None)
        
        if not self.exists('categories'):
            stmt = 'CREATE TABLE categories(\
                    category_id INT NOT NULL AUTO_INCREMENT,\
                    category_name VARCHAR(20) NOT NULL,\
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
    
    # Create a new part type with specifications;
    # Each specification is a tuple containing spec name (spec) and spec variable name (var),
    # used in calling create_spec_table(*(spec, var))
    # 1. GPU
    def add_part_type(self, part_type_name, *specifications):
        # First create the part type
        stmt = 'INSERT INTO categories (category_name)\
                VALUES (%s)'
        args = (part_type_name,)
        self.cursor.execute(stmt, params=args)
        self.db.commit()
        
        #Ensure part type name is formatted correctly
        part_type_name = str.lower(part_type_name)
        if part_type_name == None:
            return
        if part_type_name[-2] == 's':
            part_type_name = part_type_name[:-2]
        
        # For each value in the specifications, create a table for normalization
        for spec in specifications:
            if(not self.exists(spec[0])):
                self.create_spec_table(*spec)
        
        # Create statement to be sent to the cursor,
        # beginning with the name of the new table
        stmt = f'CREATE TABLE {part_type_name}s ('
        stmt += f'{str.lower(part_type_name)}_id INT NOT NULL AUTO_INCREMENT, '
        stmt += 'product_id INT NOT NULL, '
        
        # Add attribute variable name columns
        for spec in specifications:
            stmt += f'{spec[1]}_id INT NOT NULL'
            stmt += ', '
        
        # Link each table to the tables that were just created
        stmt += f'PRIMARY KEY ({part_type_name}_id), '
        stmt += f'FOREIGN KEY (product_id) REFERENCES products(product_id), '
        
        for i, spec in enumerate(specifications):
            stmt += f'FOREIGN KEY ({spec[1]}_id) REFERENCES {spec[0]}({spec[1]}_id)'
            if i < len(specifications)-1:
                stmt += ', '
        else:
            stmt += ')'
        
        print(stmt)
            
        self.cursor.execute(stmt, params=None)
        self.db.commit()
    
    #TODO:  Add current inventory (num. of) column to products table
    
    #Closes cursor and database upon program exit
    def __exit__(self):
        self.cursor.close()
        self.db.close()

if __name__ == '__main__':
    navi = Navigator() # Not supposed to be the actual interface

    while(True):
        val = input('1. Get Products'
                    + '\n2. Add spec table'
                    + '\n3. Table exists'
                    + '\n4. Create new category'
                    + '\nx. Exit\n')
        
        if (val == 'x'):
            break

        if(val == '1'):
            products = navi.get_products()
            print(tabulate(products, headers=('name', 'category'))) 
        
        if(val == '2'):
            val1 = input('Enter spec name (x to cancel): ')
            if(val1 == 'x'):
                continue
            val2 = input('Enter value name (x to cancel): ')
            if(val2 == 'x'):
                continue
            if(val1 != None and val2 != None):
                navi.create_spec_table(val, val2)

        if(val == '3'):
            val = input('Enter table name: ')
            print(navi.exists(val))

        if(val == '4'):
            vals = list()
            val = input('Create part type name (x to cancel): ')
            
            if(val == 'x'):
                break
            
            while(True):
                temp1 = input('Add category specification (x to cancel): ')
                if(temp1 == 'x'):
                    break
                
                temp2 = input('Add specification variable name (x to cancel): ')
                if(temp2 == 'x'):
                    break
                
                if(temp1 != None and temp2 != None):
                    vals.append((temp1, temp2))
            
            vals = tuple(vals)
            
            if(vals != None):
                navi.add_part_type(val, *vals)
                (f'New part type {val} successfully created')