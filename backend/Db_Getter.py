from Database import Database

def string_catch(var):
    '''If **var** is a string, it'll return it surrounded in single quotes.'''
    if isinstance(var, str):
        var = f"'{var}'"
    return var

class Db_Getter:
    def __init__(self, database:Database):
        self.db = database
    
    def get_products(self):
        '''Returns products from display_products table. Doesn't include individual specs.'''
        return self.db.select(('product_name', 'part_type', 'price', 'stock', 'manufacturer'),
                            'display_products')
    
    def get_specs(self, part_type:str):
        '''Returns specs of a given part type (str).'''
        return self.db.select('*', f'{part_type}_specs')
    
    def get_spec_names(self, part_type:str):
        '''Returns spec names for a given part type (str).'''
        return list(map(lambda a: a[:][0], self.db.select('*', f'{part_type}_specs')))

    def get_spec_id(self, spec:str, spec_val:str|int):
        '''Returns spec ID for a given spec and spec value (i.e. 'foobar' or 42)'''
        spec_val = string_catch(spec_val)
        return self.db.select(f'{spec}_id', f'{spec}', f"{spec}_val = {spec_val}")[0][0]
    
    def get_part_type_id(self, part_type_name:str):
        '''Get part type ID by name (str).'''
        return self.db.select(f'part_type_id', 'part_types', f"part_type_name = '{part_type_name}'")[0][0]
    
    def get_manufacturer_id(self, manufacturer_name:str):
        '''Get manufacture by name (str).'''
        return self.db.select('manufacturer_id', 'manufacturers', f"manufacturer_name = '{manufacturer_name}'")[0][0]
    
    def get_spec_var_form(self, part_type:str, spec_name:str):
        '''Get spec variable form by inputting the part type the spec belongs to (str),
        and the spec's name (str).'''
        return self.db.select('spec_var_form', f'{part_type}_specs', f"spec_name = '{spec_name}'")