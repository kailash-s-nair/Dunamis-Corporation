from tabulate import tabulate
from Db_Controller import Db_Controller
def is_close(val):
    return (val == 'x')

def console_add_type(controller:Db_Controller):
    '''Add a part type by console.'''
    vals = []
    val1 = input('Create part type name (x to cancel):\n>')
            
    if(is_close(val1)):
        return
    
    while(True):
        temp1 = input('Add spec (x to cancel, o to submit):\n>')
        if(temp1 == 'x'):
            return
        if temp1 == 'o':
            break
        if(val1 == 'x'):
            return
        
        temp2 = input('String (1) or num (2)?\n>')
        if(is_close(temp2)):
            return
        if(temp2 == '1'):
            temp2 = 1
        if(temp2 == '2'):
            temp2 = 2
        
        vals.append((temp1, temp2))

    if(vals != None):
        controller.add_part_type(val1, *vals)
        (f'New part type {val} successfully created')

def console_add_product(controller: Db_Controller):
    '''Add product by console.'''
    vals = []
    val1 = input('Enter product name (x to cancel):\n>')
    if(val1 == 'x'):
        return
            
    val2 = input('Enter product type (x to cancel):\n>')
    if(is_close(val2)):
        return
    
    specs = controller.getter.get_specs(val2)
    print(specs)

    if not specs:
        print('Part type does not exist')
        return
    
    val3 = input('Enter stock:\n>')
    if(is_close(val3)):
        return
    val3 = int(val3)
            
    val4 = input('Enter price:\n>')
    
    if(is_close(val4)):
        return
    val4 = int(val4)
    
    val5 = input('Enter manufacturer:\n>')
    if(is_close(val5)):
        return

    for spec in specs:
        temp2 = input(f'Add value for {spec[0]} (x to cancel):\n>')
        if(is_close(temp2)):
            return
        if(spec[1] == 2):
            temp2 = int(temp2)
        
        vals.append((spec[0], temp2))
    
    controller.add_product(val1, val2, val3, val4, val5, *vals)
    print(f'New part type {val} successfully created')

def console_edit_product(controller: Db_Controller):
    '''Edit product by console.'''
    vals = []
    val1 = input('Enter product name (x to cancel):\n>')
    if(is_close(val1)):
        return
            
    val2 = input('Enter product type (x to cancel):\n>')
    if(is_close(val2)):
        return
    
    if not controller.db.exists_in('part_types', 'part_type_name', val2):
        print('Part type does not exist')
        return
    vals = []

    while(True):
        val3 = input('Enter field to edit (x to cancel, o to submit):\n>')
        if is_close(val3):
            return
        if val3 == 'o':
            break
        val4 = input('Enter value (x to cancel):\n>')
        if (val3 == 'stock' or val3 == 'price') or (controller.getter.get_spec_var_form(val2, val3) == 2):
            val4 = int(val4)
        if is_close(val4):
            return
        if val3 and val4:
            vals.append((val3, val4))
    
    controller.edit_product(val1, val2, *vals)

if __name__ == '__main__':
    '''Code that runs if backend.py is opened directly.'''
    controller = Db_Controller()

    while(True):
        val = input('1. Create basic tables\n' +
                    '2. Format database\n' +
                    '3. Add part type\n' +
                    '4. Add product\n' +
                    '5. Edit product\n'
                    '6. Get products\n'
                    'x. Exit\n' +
                    '> ')
        
        if val == '1':
            controller.create_basic_tables()
        
        elif val == '2':
            controller.format()

        elif val == '3':
            console_add_type(controller)

        elif val == '4':
            console_add_product(controller)

        elif val == '5':
            console_edit_product(controller)
        
        elif val == '6':
            out = tabulate(controller.getter.get_products(), headers=('Part name', 'Part type', 'Stock', 'Price', 'Manufacturer'))
            print('-' * 58)
            print(out)
            print('-' * 58)

        elif val == 'x':
            break
            
        else:
            print('Invalid input')