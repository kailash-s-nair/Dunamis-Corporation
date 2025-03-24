import operator
from Database import Database
from Db_Editor import Db_Editor
from Db_Getter import Db_Getter
from contains_illegal import contains_illegal

VARCHAR = 1
NUMBER = 2

class Db_Controller():
    def __init__(self, database:Database|None=Database()):
        '''Db_Controller initializer.'''
        
        self.db = database
        self.editor = Db_Editor(self.db)
        self.getter = Db_Getter(self.db)

    def commit(self):
        '''Commits changes to the database.'''
        
        self.db.commit()

    def create_basic_tables(self):
        '''Ensures basic tables are created.'''
        
        self.editor.create_table('part_types',
                                'part_type_id INT NOT NULL AUTO_INCREMENT',
                                'part_type_name VARCHAR(20) NOT NULL',
                                'spec_count INT NOT NULL',
                                'PRIMARY KEY (part_type_id)')
        
        self.editor.create_table('manufacturers',
                                'manufacturer_id INT NOT NULL AUTO_INCREMENT',
                                'manufacturer_name VARCHAR(20) NOT NULL',
                                'PRIMARY KEY (manufacturer_id)')
        
        self.editor.create_table('products',
                                'product_id INT NOT NULL AUTO_INCREMENT',
                                'part_type_id INT NOT NULL',
                                'product_name VARCHAR(20) NOT NULL',
                                'stock INT NOT NULL',
                                'price INT NOT NULL',
                                'manufacturer_id INT NOT NULL',
                                'PRIMARY KEY (product_id)',
                                'FOREIGN KEY (part_type_id) REFERENCES part_types(part_type_id)',
                                'FOREIGN KEY (manufacturer_id) REFERENCES manufacturers(manufacturer_id)')
        
        self.editor.create_table('display_products',
                                'product_name VARCHAR(20) NOT NULL',
                                'part_type VARCHAR(20) NOT NULL',
                                'stock INT NOT NULL',
                                'price INT NOT NULL',
                                'manufacturer VARCHAR(20) NOT NULL'
                                )
        self.commit()
    
    def format(self):
        '''Clears all tables except for the basic tables, and empties them.'''
        
        self.db.execute('SHOW TABLES')
        if self.db.exists('products'):
            self.db.execute('DROP TABLE products')
        if self.db.exists():
            self.db.execute('SHOW TABLES')
            tables = self.db.fetchall()
            print(tables)
            for table in tables:
                self.db.execute(f'DROP TABLE {table[0]}')
        self.create_basic_tables()
        self.commit()
        print('Database cleared')
    
    def create_spec_table(self, spec_name:str, type_num):
        '''Create a table for a new spec (for a part type).
        
        Parameters
        ----------
        spec_name:str
            The name of the spec.
        type_num:int
            The type of spec it is (word(s) or number).
            1 (constant VARCHAR): 20-character string.
            2 (constant NUMBER): Integer value.'''
            
        var_type = 'VARCHAR (20)'
        if contains_illegal(spec_name):
            raise ValueError('Part type name contains illegal character(s)')
        elif self.db.exists(spec_name):
            raise RuntimeError(f'{spec_name} table already exists')
        else:
            if type_num == VARCHAR:
                var_type = 'VARCHAR(20)'
            elif type_num == NUMBER:
                var_type = 'INT'
                
            self.editor.create_table(spec_name,
                                        f'{spec_name}_id INT NOT NULL AUTO_INCREMENT',
                                        f'{spec_name}_val {var_type} NOT NULL',
                                        f'PRIMARY KEY ({spec_name}_id)')
    

    def add_part_type(self, part_type_name:str, *spec_type_pairs:tuple[str,int]):
        '''
        Adds a part type.
        
        Parameters
        ----------
        part_type_name:str
            The name of the new part type.
        *spec_type_pairs:tuple[str,int]
            A spec name, followed by what type of spec it is, described as an integer value
            (see: **create_spec_table()**). Repeatable.
        '''
        columns1 = []
        columns2 = []
        columns3 = []

        self.editor.insert('part_types', ('part_type_name', part_type_name), ('spec_count', len(spec_type_pairs)))

        if self.db.exists(f'{part_type_name}_specs'):
            raise RuntimeError(f'{part_type_name} spec table already exists')
        else:
            self.editor.create_table(f'{part_type_name}_specs', # Create table containing specs in the new part type
                                        'spec_name VARCHAR(20) NOT NULL',
                                        'spec_var_form INT NOT NULL',
                                        'UNIQUE (spec_Name)')
        
        for spec, type_num in spec_type_pairs:
            if type_num == VARCHAR:
                var_type = 'VARCHAR (20)'
                
            if type_num == NUMBER:
                var_type = 'INT'

            self.editor.insert(f'{part_type_name}_specs', # Insert spec into part type specs table
                            ('spec_name', f'{spec}'),
                            ('spec_var_form', type_num))

            if(not self.db.exists(spec)):
                self.create_spec_table(spec, type_num)
            else:
                raise RuntimeError(f'{spec} table already exists')

            columns1.append(f'ADD {spec}_id INT NOT NULL')
            columns2.append(f'ADD FOREIGN KEY ({spec}_id) REFERENCES {spec}({spec}_id)')
            columns3.append(f'ADD {spec} {var_type} NOT NULL')

        self.editor.alter_table('products', *columns1+columns2)
        self.editor.alter_table('display_products', *columns3)
    
    def add_product(self, product_name:str, part_type:str, stock:int, price:int, manufacturer:str, *specs:tuple[str,any]):
        '''Add product of a given part type.
        
        Parameters
        ----------
        product_name:str
            The name of the product.
        part_type:str
            The name of the part type the product is.
        stock:int
            The number of the product.
        price:int
            The price of the product.
        manufacturer:str
            The manufacturer of the product.
        *specs:tuple[str,any]
            Tuple, containing spec and spec value. Repeatable.'''
        if not self.db.exists_in('manufacturers', 'manufacturer_name', manufacturer):
            self.editor.insert('manufacturers', ('manufacturer_name', manufacturer))

        columns1 = ['product_name', 'part_type_id', 'stock', 'price', 'manufacturer_id']
        columns2 = ['product_name', 'part_type', 'stock', 'price', 'manufacturer']
        values1 = [product_name, self.getter.get_part_type_id(part_type), stock, price, self.getter.get_manufacturer_id(manufacturer)]
        values2 = [product_name, part_type, stock, price, manufacturer]

        for spec, val in specs:
            if not self.db.exists_in(spec, f'{spec}_val', val):
                self.editor.insert(spec, (f'{spec}_val', val))
            
            columns1.append(f'{spec}_id')
            columns2.append(f'{spec}')
            values1.append(self.getter.get_spec_id(spec, val))
            values2.append(val)

        print(values1)
        print(tuple(map(lambda a, b: (a, b), columns1, values1)))
        
        self.editor.insert('products', *tuple(map(lambda a, b: (a, b), columns1, values1)))
        self.editor.insert('display_products', *tuple(map(lambda a, b: (a, b), columns2, values2)))

        self.commit()
    
    def edit_product(self, product_name:str, part_type:str, *attributes:tuple[str,any]):
        '''Edit a product.
        
        Parameters
        ----------
        product_name:str
            The name of a product.
        part_type:str
            The type of part the product is.
        *attributes:tuple[str,any]
            The attribute you want to alter, followed by the new value.'''
        
        columns1 = []
        columns2 = []
        for att in attributes:
            print(self.db.get_columns('products'))
            if not (f'{att[0]}_id' in self.db.get_columns('products') 
                    and (att[0] in self.getter.get_spec_names(part_type) or att[0] == 'stock' or att[0] == 'price' or att[0] == 'manufacturer')):
                raise RuntimeError(f'{att[0]} not a valid attribute')
            if att[0] == 'stock' or att[0] == 'price':
                column1 = att[0]
                value1 = att[1]
            elif att[0] == 'manufacturer':
                if(not self.db.exists_in('manufacturers', 'manufacturer_name', att[0])):
                    self.editor.insert('manufacturers', ('manufacturer_name', att[1]))
                column1 = 'manufacturer_id'
                value1 = self.getter.get_manufacturer_id(att[1])
            else:
                if(not self.db.exists_in(f'{att[0]}', f'{att[0]}_val', att[1])):
                    self.editor.insert(f'{att[0]}', (f'{att[0]}_val', att[1]))
                column1 = f'{att[0]}_id'
                value1 = self.getter.get_spec_id(att[0], att[1])
            column2 = att[0]
            value2 = att[1]

            columns1.append((column1, value1))
            columns2.append((column2, value2))
            
        self.editor.update_table('products', f"product_name = '{product_name}'", *columns1)
        self.editor.update_table('display_products', f"product_name = '{product_name}'", *columns2)

        self.commit()

    def get_products(self):
        '''Gets products.
        
        Returns
        -------
        List[tuple:any]
            A list of tuples.'''
        
        self.getter.get_products()
        
        