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
        
        self.cursor = self.db.cursor(buffered=True)

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
            stmt =  f'CREATE TABLE {spec_name} ('
            stmt += f'{spec_name}_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, '
            stmt += f'{spec_name}_name VARCHAR(20))'
            
            print(stmt)
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
        stmt1 =  f'INSERT INTO categories (category_name, spec_count) '
        stmt1 += f'VALUES (\'{part_type}\', {len(specs)})'
        
        print(part_type + ' inserted into categories')
        
        #Ensure part type name is formatted correctly
        if part_type == None:
            raise ValueError('Empty argument')
        
        part_type = str.lower(part_type)
            
        if(self.exists(part_type)):
            print(f'Part type {part_type} already exists')
        
        # For each value in the specifications, create a table for normalization
        stmt2 =  f'ALTER TABLE products '
        for i, spec in enumerate(specs):
            if(not self.exists(spec)):
                self.create_spec_table(spec)  #Create table for spec
                stmt2 += f'ADD {spec}_id INT' #Add spec to main table
                if(i < len(specs)-1):
                    stmt2 += ', '
            else:
                raise RuntimeError('table for ' + spec + ' already exists')
        stmt3 = f'ALTER TABLE products '
        for i, spec in enumerate(specs):
            stmt3 += f'ADD FOREIGN KEY ({spec}_id) REFERENCES {spec}({spec}_id)'
            if(i < len(specs)-1):
                stmt3 += ', '
        
        stmt4 = 'ALTER TABLE display_products '
        for i, spec in enumerate(specs):
            stmt4 += f'ADD {spec} VARCHAR(20)'
            if(i < len(specs)-1):
                stmt4 += ', '
        
        print(stmt1)
        print(stmt2)
        print(stmt3)
        print(stmt4)
        
        self.cursor.execute(stmt1)
        self.cursor.execute(stmt2)
        self.cursor.execute(stmt3)
        self.cursor.execute(stmt4)
        
        self.db.commit()
        
        print(part_type + ' specs added to main table')
    
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
        stmt = f'SELECT {id_field} FROM {table_name} WHERE {name_field} LIKE \'{name}\''
        print(stmt)
        self.cursor.execute(stmt)
        temp = self.cursor.fetchone()
        print(temp)
        if temp:
            return temp[0]
        else:
            return None
        
    #Returns column name if a part type has a given spec in it, None otherwise
    def spec_exists_in_part(self, part, spec):
        self.cursor.execute(f'SHOW COLUMNS FROM {part} LIKE \'{spec}_id\'')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
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
    
    def get_product_name(self, product_id):
        self.cursor.execute(f'SELECT product_name FROM products WHERE product_id = {product_id}')
        return str(self.cursor.fetchone()[0])
    
    def get_part_type_name(self, part_type_id):
        self.cursor.execute(f'SELECT category_name FROM categories WHERE category_id = {part_type_id}')
        return str(self.cursor.fetchone()[0])
    
    def get_spec_name(self, spec_type, spec_id):
        self.cursor.execute(f'SELECT {spec_type}_name FROM {spec_type} WHERE {spec_type}_id = \'{spec_id}\'')
        return str(self.cursor.fetchone()[0])
    
    #Add value to products table if it doesn't exist
    def add_to_products(self, product_name, part_id, price, *spec_pairs):
        if not self.name_exists_in_table('products', 'product_name', 'product_id', product_name):
            stmt1 = 'INSERT INTO products (product_name, category_id, stock, price, '
            for i, spec_pair in enumerate(spec_pairs):
                stmt1 += f'{spec_pair[0]}_id'
                if(i < len(spec_pairs)-1):
                    stmt1 += ', '
            else:
                stmt1 += ') '
            stmt1 += f'VALUES (\'{product_name}\', {part_id}, 0, {price}, '
            for i, spec_pair in enumerate(spec_pairs):
                stmt1 += f'\'{self.get_spec_id(spec_pair[0], spec_pair[1])}\''
                if(i < len(spec_pairs) - 1):
                    stmt1 += ', '
            else:
                stmt1 += ')'
            print(stmt1)
            
            stmt2 = 'INSERT INTO display_products (product_name, product_type, stock, price, '
            for i, spec_pair in enumerate(spec_pairs):
                stmt2 += f'{spec_pair[0]}'
                if(i < len(spec_pairs)-1):
                    stmt2 += ', '
            else:
                stmt2 += ') '
            stmt2 += f'VALUES (\'{product_name}\', \'{self.get_part_type_name(part_id)}\', 0, {price}, '
            for i, spec_pair in enumerate(spec_pairs):
                stmt2 += f'\'{spec_pair[1]}\''
                if(i < len(spec_pairs) - 1):
                    stmt2 += ', '
            else:
                stmt2 += ')'
            print(stmt1)
            print(stmt2)
            self.cursor.execute(stmt1)
            self.cursor.execute(stmt2)
            self.db.commit()
    
    #Add value to given spec table if it doesn't exist
    def add_to_spec(self, spec, val):
        if not self.name_exists_in_table(spec, spec+'_name', spec+'_id', val):
            stmt =  f'INSERT INTO {spec} ({spec}_name) '
            stmt += f'VALUES (\'{val}\')'
            self.cursor.execute(stmt)
            self.db.commit()
    
    #Add product of a given type and specifications
    def add_product(self, product_name, part_type, price, *spec_pairs):
        for spec_pair in spec_pairs:
            self.add_to_spec(*spec_pair)
        self.add_to_products(product_name, self.get_part_type_id(part_type), price, *spec_pairs)
    
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
            
            val3 = input('Enter price: ')
            
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
                navi.add_product(val1, val2, val3, *vals)
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