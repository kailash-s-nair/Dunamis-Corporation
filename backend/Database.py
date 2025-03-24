import mysql.connector
import json
class Database:
    def __init__(self):
        '''Initializer for the Database class.'''
        
        with open('very secure credentials folder/credentials.json', 'r') as file:
            cred = json.load(file)
        
        self.db = mysql.connector.connect(
            user=cred.get('user'),
            password = cred.get('password'),
            database = 'items_database',
            host = 'dynama.ddns.net' #Server (i.e. Clover's laptop) has to be on
        )
        
        self.cursor = self.db.cursor(buffered=True)
        self.cursor.execute('SET autocommit=0')

    def execute(self, *stmts:str):
        '''Execute one or several statements in succession (use string literals when writing statements,
        taking care to include quotes for varchar(20) (string) row values.)
        
        Parameters
        ----------
        *stmts:str
            List of statements to be executed.'''
            
        for stmt in stmts:
            print(stmt)
            self.cursor.execute(stmt)
    
    def fetchone(self):
        '''Gets one result. Use only after a statement has been executed.
        
        Returns
        -------
        self.cursor.fetchone():Rowtype|None
            A row (given as a tuple), or None.'''
        return self.cursor.fetchone()
    
    def fetchall(self):
        '''Gets every result. Use only after a statement has been executed.
        
        Returns
        -------
        self.cursor.fetchall():List[Rowtype]
            A list of rows (given as tuples).'''
            
        return self.cursor.fetchall()
    
    def commit(self):
        self.db.commit()
    
    def exists(self, table_name=None):
        '''Gets if a table of the given name exists or not.
        
        Parameters
        ----------
        table_name
            The name of the table to confirm the existence of.
        Returns
        -------
        boolean
            Whether or not the named table exists in the database.'''
            
        if not table_name:
            self.execute(f"SELECT EXISTS(SELECT table_name FROM INFORMATION_SCHEMA.tables WHERE table_schema = 'items_database')")
        else:
            self.execute(f"SELECT EXISTS(SELECT table_name FROM INFORMATION_SCHEMA.tables WHERE table_schema = 'items_database' AND table_name = '{table_name}')")
        result = self.fetchone()
        
        if result and result[0] == 1:
            return True
        else:
            return False
        
    def exists_in(self, table_name, field_name, val):
        '''Gets if a given value exists within the table under the field name (column) given.
        
        Parameters
        ----------
        table_name
            The name of one table to be checked.
        field_name
            The column to check for the value.
        val
            The item which may or may not be in the table under the column.
        Returns
        -------
        boolean
            Whether or not the item exists in the table under the given column.'''
            
        if(isinstance(val, str)):
            val = f"'{val}'"
        self.execute(f"SELECT EXISTS(SELECT * FROM {table_name} WHERE {field_name} = {val})")
        result = self.fetchone()
        if result and result[0] == 1:
            return True
        else:
            return False
    
    def select(self, columns:str|tuple[str], tables:str|tuple[str], conditions:str|tuple[str]|None=None):
        '''Returns the rows in the specified tables (only specified columns) where each row meets the conditions (if any).
        
        Parameters
        ----------
        columns:str|tuple[str]
            Column(s) given as a tuple, in SQL syntax. The column(s) will be included in
            the output.
        
        tables:str|tuple[str]
            The names of the tables used in the array. In the event there are
            several tables, every time a column from a unique table is listed,
            add the tables to the tuple.
            
        conditions:str|tuple[str]
            Condition(s) as to which rows to show, in SQL syntax. Rows which do not meet
            the conditions are not included in the results.
        
        Returns
        -------
        List[Rowtype]
            Rows containing values under the given columns that meet each condition.'''
            
        stmt = 'SELECT '
        
        if isinstance(columns, str) and isinstance(tables, str): #Case: 1 column and 1 table
            stmt += f'{columns} FROM {tables} '
        elif isinstance(columns, tuple) and isinstance(tables, str): #Case: Several columns from one table
            for i, column in enumerate(columns):
                stmt += column
                if i < len(columns) - 1:
                    stmt += ', '
            stmt += f' FROM {tables}'
        elif isinstance(columns, tuple) and isinstance(tables, tuple): #Case: Several columns from several tables
            for i, column in enumerate(columns):
                stmt += column
                if i < len(columns) - 1:
                    stmt += ', '
            ' FROM '
            for i, table in enumerate(tables):
                stmt += table
                if i < len(tables) - 1:
                    stmt += ', '

        if conditions and isinstance(conditions, str): #Case: One condition statement
            stmt += f' WHERE {conditions}'
        elif isinstance(conditions, tuple):
            for i, condition in enumerate(conditions): #Case: Several condition statements
                stmt += condition
                if i < len(conditions) - 1:
                    stmt += ', '

        self.execute(f'SELECT EXISTS({stmt})')

        if(self.fetchone()):
            self.execute(stmt)
            temp = self.fetchall()
            return temp
        
        else:
            return None
        
    def get_columns(self, table_name:str):
        '''Returns the columns in a given table.
        
        Parameters
        ----------
        table_name:str
        The name of the table.
        
        Returns
        -------
        list[str]:
            List of columns in the table.'''
        
        if self.exists(table_name):
            self.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
            return list(map(lambda a : a[0], self.fetchall()))
        else:
            raise RuntimeError(f'{table_name} does not exist')
        