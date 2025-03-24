from Database import Database

class Db_Editor:
    def __init__(self, database:Database):
        '''Database editor initializer.'''
        
        self.db = database
    
    def create_table(self, table_name:str, *columns:str):
        '''Creates a table.
        
        Parameters
        ----------
        table_name:str
            The name of the table.
        *columns:str
            Column values for the table, in SQL syntax 
            (i.e. "column_name INT NOT NULL AUTO_INCREMENT").
            Repeatable.'''
        
        stmt = f'CREATE TABLE {table_name} ('
        for i, column in enumerate(columns):
            stmt += column
            if i < len(columns) - 1:
                stmt += ', '
        stmt += ')'

        self.db.execute(stmt)

    def insert(self, table_name:str, *column_vals:tuple[str, any]):
        '''Insert new item into the given table.
        
        Parameters
        ----------
        table_name:str
            The name of the table.
        *column_vals:tuple[str, any]
            Tuple with the column name, followed by the value for the item. Repeatable.'''
        stmt1 = f' INSERT INTO {table_name} ('
        stmt2 = f') VALUES ('

        for i, (column, val) in enumerate(column_vals):
            if isinstance(val, str):
                val = f"'{val}'"
            stmt1 += column
            stmt2 += f'{val}'

            if i < len(column_vals) - 1:
                stmt1 += ', '
                stmt2 += ', '
        stmt2 += ')'

        stmt = stmt1 + stmt2

        self.db.execute(stmt)
    
    def update_table(self, table_name:str, condition:str, *column_vals:tuple[str, any]):
        '''Insert new item into the given table.
        
        Parameters
        ----------
        table_name:str
            The name of the table.
        condition:str
            Only item(s) that meet the condition (in SQL syntax) are changed.
        *column_vals:tuple[str, any]
            Tuple with the column name, followed by the value for the item. Repeatable.'''
        stmt = f'UPDATE {table_name} SET '
        for i, (column, val) in enumerate(column_vals):
            if isinstance(val, str):
                val = f"'{val}'"
            stmt += f'{column} = {val}'
            if i < len(column_vals) - 1:
                stmt += ', '
        stmt += f' WHERE {condition}'

        self.db.execute(stmt)

    def alter_table(self, table_name:str, *args:str):
        '''Edits a table.
        
        Parameters
        ----------
        table_name:str
            The name of the table.
        *args:str
            Change to make to the table, in SQL syntax. Repeatable.
        '''
        stmt =  f'ALTER TABLE {table_name} '
        for i, arg in enumerate(args):
            stmt += arg
            if i < len(args)-1:
                stmt += ', '
        
        self.db.execute(stmt)