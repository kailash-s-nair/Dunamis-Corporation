from Database import Database

def string_catch(var):
        if isinstance(var, str):
            var = f"'{var}'"
        return var

class Db_Getter:
    def __init__(self, database:Database):
        self.db = database
    
    def get_products(self):
        return self.db.select(('products.product_name', 'part_types.part_type_name'),
                              ('products', 'part_types'),
                              ('products.part_type_id = part_types.part_type_id'))
    
    def get_specs(self, part_type:str):
        return self.db.select('*', f'{part_type}_specs')
    
    def get_spec_names(self, part_type:str):
        return list(map(lambda a: a[:][0], self.db.select('*', f'{part_type}_specs')))

    def get_spec_id(self, spec:str, spec_val:str|int):
        spec_val = string_catch(spec_val)
        return self.db.select(f'{spec}_id', f'{spec}', f"{spec}_val = {spec_val}")[0][0]
    
    def get_part_type_id(self, part_type_name:str):
        return self.db.select(f'part_type_id', 'part_types', f"part_type_name = '{part_type_name}'")[0][0]
    
    def get_manufacturer_id(self, manufacturer_name:str):
        return self.db.select('manufacturer_id', 'manufacturers', f"manufacturer_name = '{manufacturer_name}'")[0][0]
    
    def get_spec_var_form(self, part_type:str, spec_name:str):
        return self.db.select('spec_var_form', f'{part_type}_specs', f"spec_name = '{spec_name}'")