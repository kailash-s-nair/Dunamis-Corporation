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
            host = 'dynama.ddns.net' #Server (i.e. Clover's laptop) has to be on
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
    def create_spec_table(self, spec_name):
        if(not self.exists(spec_name)): #String literal must be used here
            stmt = f'CREATE TABLE {spec_name}(\
                    {spec_name}_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,\
                    {spec_name}_name VARCHAR(20))'

            self.cursor.execute(stmt, params=None)
            self.db.commit()
        else:
            raise RuntimeError('Table ' + spec_name + ' already exists')

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
    
    # Create a new part type with specifications;
    # Each specification is a tuple containing spec name (spec) and spec variable name (var),
    # used in calling create_spec_table(*(spec, var)).
    # 1. GPU
    def add_part_type(self, part_type, *specs):
        # First create the part type
        stmt = 'INSERT INTO categories (category_name)\
                VALUES (%s)'
        args = (part_type,)
        self.cursor.execute(stmt, params=args)
        self.db.commit()
        
        print(part_type + ' inserted into categories')
        
        #Ensure part type name is formatted correctly
        if part_type == None:
            raise ValueError('Empty argument')
        
        part_type = str.lower(part_type)
            
        if(self.exists(part_type)):
            raise RuntimeError('Part type already exists')
        
        # For each value in the specifications, create a table for normalization
        for spec in specs:
            if(not self.exists(spec)):
                self.create_spec_table(spec)
                print('table ' + spec + ' created')
            else:
                raise RuntimeError('table for ' + spec + ' already exists')
        
        # Create statement to be sent to the cursor,
        # beginning with the name of the new table
        stmt = f'CREATE TABLE {part_type} ('
        stmt += f'{str.lower(part_type)}_id INT NOT NULL AUTO_INCREMENT, '
        stmt += 'product_id INT NOT NULL, '
        
        # Add attribute variable name columns
        for spec in specs:
            stmt += f'{spec}_id INT NOT NULL'
            stmt += ', '
        
        # Link each table to the tables that were just created
        stmt += f'PRIMARY KEY ({part_type}_id), '
        stmt += f'FOREIGN KEY (product_id) REFERENCES products(product_id), '
        
        for i, spec in enumerate(specs):
            stmt += f'FOREIGN KEY ({spec}_id) REFERENCES {spec}({spec}_id)'
            if i < len(specs)-1:
                stmt += ', '
        else:
            stmt += ')'
            
        self.cursor.execute(stmt, params=None)
        self.db.commit()
        print(part_type + ' table successfully created')
    
    #Get the number of spec arguments for a given part type
    def get_spec_count(self, part_type):
        stmt = 'SELECT count(*) FROM information_schema.columns WHERE table_name = %s'
        args = (part_type,)
        if self.exists(part_type):
            self.cursor.execute(stmt, params=args)
            self.db.commit
            return self.cursor.fetchone()[0]
        else:
            raise ValueError("Part type name not found")
    
    #Returns an ID if element of a given name exists within the table, None otherwise
    def name_exists_in_table(self, table_name, name_field, id_field, name):
        self.cursor.execute(f'SELECT {id_field} FROM {table_name} WHERE {name_field} LIKE \'{name}\'')
        temp = self.cursor.fetchone()
        if(temp):
            return temp[0]
        else:
            return None
        
    #Returns column name if a part type has a given spec in it, None otherwise
    def spec_exists_in_part(self, part, spec):
        self.cursor.execute(f'SHOW COLUMNS FROM {part} LIKE \'{spec}_id\'')
        temp = self.cursor.fetchone()[0]
        if(temp):
            return str(temp)
        else:
            return None
    
    #Get product id from products by name
    def get_product_id(self, product_name):
        self.cursor.execute(f'SELECT product_id FROM products WHERE product_name = \'{product_name}\'')
        return str(self.cursor.fetchone()[0])
    
    #Get part type from categories by name
    def get_part_type_id(self, part_type):
        self.cursor.execute(f'SELECT category_id FROM categories WHERE category_name = \'{part_type}\'')
        return str(self.cursor.fetchone()[0])
    
    #Get spec value from a given spec table by name
    def get_spec_id(self, spec_type, spec_name):
        self.cursor.execute(f'SELECT {spec_type}_id FROM {spec_type} WHERE {spec_type}_name = \'{spec_name}\'')
        return str(self.cursor.fetchone()[0])
    
    #Add value to products table if it doesn't exist
    def add_to_products(self, product_name, part_id):
        if not self.name_exists_in_table('products', 'product_name', 'product_id', product_name):
            stmt = 'INSERT INTO products (product_name, category_id)\
                    VALUES (%s, %s)'
            par = (product_name, part_id)
            self.cursor.execute(stmt, params=par)
            self.db.commit()
    
    #Add value to given spec table if it doesn't exist
    def add_to_spec(self, spec, val):
        if not self.name_exists_in_table(spec, spec+'_name', spec+'_id', val):
            stmt =  f'INSERT INTO {spec} ({spec}_name) '
            stmt += 'VALUES (%s)'
            par = (val,)
            self.cursor.execute(stmt, params=par)
            self.db.commit()
    
    #Add value to a given part type table.
    def add_to_part_type(self, product_name, part_type, specs):
        stmt1 = f'INSERT INTO {part_type} ('
        stmt1 += 'product_id, '
        stmt2 = 'VALUES ('
        stmt2 += self.get_product_id(product_name)
        stmt2 += ', '
            
        for i, spec in enumerate(specs):
                stmt1 += spec[0] + '_id'
                stmt2 += self.get_spec_id(spec[0], spec[1])
                if i < len(specs) - 1:
                    stmt1 += ', '
                    stmt2 += ', '
        else:
            stmt1 += ') '
            stmt2 += ')'
        
        stmt = stmt1 + stmt2
            
        print(stmt)
            
        self.cursor.execute(stmt, params=None)
        self.db.commit()
    
    #Add product of a given type and specifications
    def add_product(self, product_name, part_type, *specs):
        if not self.exists(part_type):
            raise ValueError('Part type not found')
        if self.get_spec_count(part_type) - 2 != len(specs):
            raise ValueError('Number of arguments does not match part type number of specs')
        for spec in specs:
            if not self.spec_exists_in_part(part_type, spec[0]):
                raise ValueError('Specification ' + spec[0] + ' does not exist in ' + part_type)
        
        part_id = self.get_part_type_id(part_type)
    
        if(part_id):
            self.add_to_products(product_name, part_id)
            print(product_name + ' of type ' + part_type + ' successfully added to products database')
            
            for spec in specs:
                if len(spec) != 2:
                    raise ValueError('Illegal argument format')
                self.add_to_spec(spec[0], spec[1])
                print(spec[1] + ' added to ' + spec[0])
            
            self.add_to_part_type(product_name, part_type, specs)
        else:
            raise ValueError('Part type ID not found')
    
    def edit_product(self, product_name, part_type, *spec_value_pairs):
        product_id = self.get_product_id(product_name)
        if(product_id and self.name_exists_in_table(part_type, 'product_id', f'{part_type}_id'), product_id):
            for pair in spec_value_pairs:
                if(self.spec_exists_in_part(pair[0])):
                    stmt = f'UPDATE {part_type} SET {pair[0]} = {pair[1]} WHERE product_id = {product_id}'
                else:
                    raise ValueError('Spec does not exist in part')
    
    def clear_table(self, table_name):
        if(self.exists(table_name)):
            self.cursor.execute(f'DELETE FROM {table_name}')
            self.cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 0')
    
    #TODO:  Add current inventory (num. of) column to products table
    
    #Closes cursor and database upon program exit
    def __exit__(self):
        self.cursor.close()
        self.db.close()

if __name__ == '__main__':
    navi = Navigator() # Not supposed to be the actual interface

    while(True):
        val = input('1. Get Products'
                    + '\n2. Table exists'
                    + '\n3. Create new part type'
                    + '\n4. Add new part'
                    + '\n5. Check if value exists in table'
                    + '\n6. Clear table'
                    + '\nx. Exit\n')
        
        if (val == 'x'):
            break

        if(val == '1'):
            products = navi.get_products()
            print(tabulate(products, headers=('name', 'category'))) 

        if(val == '2'):
            val1 = input('Enter table name (x to cancel): ')
            if(val1 == 'x'):
                continue
            print(navi.exists(val1))

        if(val == '3'):
            vals = []
            val1 = input('Create part type name (x to cancel): ')
            
            if(val1 == 'x'):
                continue
            
            while(True):
                temp1 = input('Add spec (x to cancel, o to submit): ')
                if(temp1 == 'x'):
                    val1 = 'x'
                    break
                if temp1 == 'o':
                    break
                vals.append(temp1)
            
            if(val1 == 'x'):
                continue
            else:
                vals = tuple(vals)
                
                if(vals != None):
                    navi.add_part_type(val1, *vals)
                    (f'New part type {val} successfully created')
        
        if(val == '4'):
            vals = []
            
            val1 = input('Enter part name (x to cancel): ')
            
            if(val1 == 'x'):
                continue
            
            val2 = input('Enter part type (x to cancel): ')
            
            if(val1 == 'x'):
                continue
            
            while(True):
                temp1 = input('Add spec (x to cancel, o to submit): ')
                if(temp1 == 'x'):
                    val1 = 'x'
                    break
                if(temp1 == 'o'):
                    break
                
                temp2 = input('Add spec value (x to cancel): ')
                if(temp2 == 'x'):
                    val1 = 'x'
                    break
                if(temp2 == 'o'):
                    break
                
                if(temp1 != None and temp2 != None):
                    vals.append((temp1, temp2))
            if(val1 == 'x'):
                continue
            
            if(vals != None):
                navi.add_product(val1, val2, *vals)
                (f'New part type {val} successfully created')
        if (val == '5'):
            val1 = input('Enter table name: ')
            val2 = input('Enter name field: ')
            val3 = input('Enter ID field: ')
            val4 = input('Enter name: ')
            temp = navi.name_exists_in_table(val1,val2,val3,val4)
            if(temp):
                print(f'{val4} exists in table {val1} under {val3}: {temp}')
            else:
                print(f'{val4} does not exist in the table')
        if (val == '6'):
            val1 = input('Enter table name: ')
            navi.clear_table(val1)