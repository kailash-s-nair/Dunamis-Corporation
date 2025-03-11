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
        
    def execute(*stmts):
        for stmt in stmts:
            self.cursor.execute(stmt)

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
                    stock INT, \
                    price INT, \
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

        specs = list(specs)

        for i in range(len(specs)):
            specs[i] = specs[i].replace(' ', '_')
            specs[i] = specs[i].lower()
        
        #Ensure part type name is formatted correctly
        if part_type == None:
            raise ValueError('Empty argument')
        
        part_type = str.lower(part_type)
            
        if(self.exists(part_type)):
            print(f'Part type {part_type} already exists')
            return
        
        # For each value in the specifications, create a table for normalization and add column to products
        stmt2 =  f'ALTER TABLE products '
        for i, spec in enumerate(specs):
            if(not self.exists(spec)):
                stmt2 += f'ADD {spec}_id INT' #Add spec to main table
                if(i < len(specs)-1):
                    stmt2 += ', '
            else:
                raise RuntimeError('table for ' + spec + ' already exists')
        
        #For each new column, add foreign key
        stmt3 = f'ALTER TABLE products '
        for i, spec in enumerate(specs):
            stmt3 += f'ADD FOREIGN KEY ({spec}_id) REFERENCES {spec}({spec}_id)'
            if(i < len(specs)-1):
                stmt3 += ', '
        
        #Alter display table
        stmt4 = 'ALTER TABLE display_products '
        for i, spec in enumerate(specs):
            stmt4 += f'ADD {spec} VARCHAR(20)'
            if(i < len(specs)-1):
                stmt4 += ', '
        
        #Create table with spec information
        stmt5 = f'CREATE TABLE {part_type}_specs ('
        stmt5 += 'specs_in_type VARCHAR(20) NOT NULL, '
        stmt5 += 'UNIQUE (specs_in_type)'
        stmt5 += ')'

        #Insert parts into table
        stmt6 = f'INSERT INTO {part_type}_specs '
        stmt6 += 'VALUES ('

        for i, spec in enumerate(specs):
            stmt6 += f'{spec} VARCHAR(20) NOT NULL'
            if(i < len(specs)-1):
                stmt6 += ', '
        stmt6 += ')'
        
        # print(stmt1,stmt2,stmt3,stmt4,stmt5,stmt6, sep='\n\n')

        for spec in specs:
          spec = spec.replace(' ', '_')
          self.create_spec_table(spec) #Create spec tables
        print('Spec tables created')
        
        self.execute(stmt1, stmt2, stmt3, stmt4, stmt5, stmt6)
        self.db.commit()
        print(part_type + f'{part_type} specs added to main table')
    
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
    def spec_exists_in_product(self, product, spec):
        self.cursor.execute(f'SELECT * FROM products WHERE product_name = \'{product}\' AND {spec}_id IS NOT NULL')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    #Get product id from products by name
    def get_product_id(self, product_name):
        self.cursor.execute(f'SELECT product_id FROM products WHERE product_name = \'{product_name}\'')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    #Get part type from categories by name
    def get_part_type_id(self, part_type):
        self.cursor.execute(f'SELECT category_id FROM categories WHERE category_name = \'{part_type}\'')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    #Get spec value from a given spec table by name
    def get_spec_id(self, spec_type, spec_name):
        self.cursor.execute(f'SELECT {spec_type}_id FROM {spec_type} WHERE {spec_type}_name = \'{spec_name}\'')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    def get_product_name(self, product_id):
        self.cursor.execute(f'SELECT product_name FROM products WHERE product_id = {product_id}')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    def get_part_type_name(self, part_type_id):
        self.cursor.execute(f'SELECT category_name FROM categories WHERE category_id = {part_type_id}')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    def get_spec_name(self, spec_type, spec_id):
        self.cursor.execute(f'SELECT {spec_type}_name FROM {spec_type} WHERE {spec_type}_id = \'{spec_id}\'')
        temp = self.cursor.fetchone()
        if temp:
            return str(temp[0])
        else:
            return None
    
    #Add value to products table if it doesn't exist
    def add_to_products(self, product_name, part_id, price, *spec_pairs):
        if(not self.name_exists_in_table('products', 'product_name', 'product_id', product_name)
            and self.exists(self.get_part_type_id(part_id))):
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
            self.execute(stmt1, stmt2)
            self.db.commit()
        else:
            print('Product already exists')
    
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

    def edit_product(self, product_name, *spec_pairs):
        stmt1 = 'UPDATE products '
        stmt2 = 'UPDATE display_products '
        if self.get_product_id(product_name):
            for pair in spec_pairs:
                temp = self.get_spec_id(pair[0], pair[1])

                if not temp:
                    # self.add_to_spec(temp)
                    temp = self.get_spec_id(pair[1])
                
                stmt1 += f'set {pair[0]}_id = {temp} '
                stmt2 += f'set {pair[0]} = {pair[1]} '
            stmt1 += f'WHERE product_name = \'{product_name}\''
            stmt2 += f'WHERE product_name = \'{product_name}\''

            print(stmt1)
            print(stmt2)

            # self.execute(stmt1, stmt2)
        else:
            raise ValueError('Product does not exist')
    
    def clear_table(self, table_name):
        if(self.exists(table_name)):
            self.cursor.execute(f'DELETE FROM {table_name}')
            self.cursor.execute(f'ALTER TABLE {table_name} AUTO_INCREMENT = 0')
    
    #TODO:  Add current inventory (num. of) column to products table
    
    #Closes cursor and database upon program exit
    def __exit__(self):
        self.cursor.close()
        self.db.close()

def console_get_products(navi: Navigator):
    products = navi.get_products()
    print(tabulate(products, headers=('name', 'category'))) 

def console_item_exists(navi: Navigator):
    val1 = input('Enter table name (x to cancel): ')
    if(val1 == 'x'):
        return
    print(navi.exists(val1))

def console_add_type(navi: Navigator):
    vals = []
    val1 = input('Create part type name (x to cancel): ')
            
    if(val1 == 'x'):
        return
    
    while(True):
        temp1 = input('Add spec (x to cancel, o to submit): ')
        if(temp1 == 'x'):
            return
        if temp1 == 'o':
            break
        if(val1 == 'x'):
            return
        
        temp1 = temp1.split(', ')

        for s in temp1:
            vals.append(s)

    if(vals != None):
        navi.add_part_type(val1, *vals)
        (f'New part type {val} successfully created')

def console_add_part(navi: Navigator):
    vals = []
    val1 = input('Enter part name (x to cancel): ')
    if(val1 == 'x'):
        return
            
    val2 = input('Enter part type (x to cancel): ')
    if(val2 == 'x'):
        return
            
    val3 = input('Enter price: ')
    if(val3 == 'x'):
        return
    
            
    while(True):
        temp1 = input('Add spec (x to cancel, o to submit): ')
        if(temp1 == 'x'):
            return
        if(temp1 == 'o'):
            break

        temp2 = input('Add spec value (x to cancel): ')
        if(temp2 == 'x'):
            return
                
        if(temp1 != None and temp2 != None):
            vals.append((temp1, temp2))
    
    navi.add_product(val1, val2, val3, *vals)
    print(f'New part type {val} successfully created')

def console_exists_in_table(navi: Navigator):
    val1 = input('Enter table name: ')
    val2 = input('Enter name field: ')
    val3 = input('Enter ID field: ')
    val4 = input('Enter name: ')
    temp = navi.name_exists_in_table(val1,val2,val3,val4)
    if(temp):
        print(f'{val4} exists in table {val1} under {val3}: {temp}')
    else:
        print(f'{val4} does not exist in the table')

def console_edit_product(navi: Navigator):
    val1 = input('Enter product name (x to cancel)')
    if(val1 == 'x'):
        return
    vals = []
    
    while(True):
        val2 = input('Enter spec (x to cancel, o to submit): ')
        if(val2 == 'x'):
            return
        if(val2 == 'o'):
            break
        val3 = input('Enter spec value: ')
        if(val3 == 'x'):
            return
        vals.append((val2, val3))
    
    navi.edit_product(val1, *vals)

    return

if __name__ == '__main__':
    navi = Navigator() # Not supposed to be the actual interface

    while(True):
        val = input('1. Get Products'
                    + '\n2. Table exists'
                    + '\n3. Create new part type'
                    + '\n4. Add new part'
                    + '\n5. Check if value exists in table'
                    + '\n6. Clear table'
                    + '\n7. Edit product'
                    + '\nx. Exit\n')
        
        if (val == 'x'):
            break

        if(val == '1'):
            console_get_products(navi)

        if(val == '2'):
            console_item_exists(navi)

        if(val == '3'):
            console_add_type(navi)
        
        if(val == '4'):
            console_add_part(navi)
            
        if (val == '5'):
            console_exists_in_table(navi)
            
        if (val == '6'):
            val1 = input('Enter table name: ')
            navi.clear_table(val1)
        
        if (val == '7'):
            console_edit_product(navi)