import mysql.connector
import config

"""" Underneath an example of the correct syntax to use this class 
    # Create an object JOIN 
    >>> join_object = JOIN('my_database')
    # Decide whether to launch the query or create the SQL code to be displayed.
    # There can be many reasons to use the create method, for example, in case only the
    # string is actually needed.
    >>> join_object.launch() # execute the query
    >>> join_object.create() # provide the SQL text of the query

    # Reminder: to visualise the SQL query, echo must be set to True and the method create()

    @BeGeos """

"""" Reminder: to setup the connection with a mysql database, access the congif.py file and input your credentials
     If already provided for the Database or Table classes, no action is required."""


class JOIN:
    """ This can be used with a generic database and it will create a query to join all the tables in that database.
        It uses a combination of primary keys and foreign keys. Therefore, it has one main rule: the name of primary
        key in Table A must be identical to the foreign key in Table B which is referring to. Besides being a best
        practice, this should be something to include when designing any database. """

    def __init__(self, dbname, echo=False):
        self.dbname = dbname
        self.conn = mysql.connector.connect(host=config.host,
                                            user=config.user,
                                            passwd=config.password,
                                            database=self.dbname)
        self.cur = self.conn.cursor()
        self.echo = echo

    def describe(self, name):
        string = "DESCRIBE " + name
        self.cur.execute(string)
        return self.cur.fetchall()

    def table_finder(self):
        result = {}
        self.cur.execute('SHOW TABLES')
        results = self.cur.fetchall()
        for each in results:
            info = JOIN.describe(self, each[0])
            result[each[0]] = info
        return result

    @staticmethod
    def primary_key_finder(from_table_finder: dict):
        primary_keys = {}
        keys = []
        for k, v in from_table_finder.items():
            for cols in v:
                if cols[3] == 'PRI':
                    keys.append(cols[0])
            primary_keys[k] = keys
            keys = []
        del keys
        return primary_keys

    def walk_tables(self, table: dict, primary_keys: dict):
        """Walk tables in a database to create the query and join all tables"""

        """Create the dict with table: [list of columns]"""
        all_tables_columns = {}
        tmp_cols = []
        for key in table:
            for columns in table[key]:
                tmp_cols.append(columns[0])
            all_tables_columns[key] = tmp_cols
            tmp_cols = []
        list_tables = list(all_tables_columns.keys())  # Temporary just to get the start table
        del tmp_cols

        """ Create a list of primary keys from the dictionary, making sure to just take it once.
        It is a 2 step process because some tables have multiple primary keys and the return 
        is a list """
        tmp_list_pk = []
        for each in primary_keys.values():
            for e in each:
                if e not in tmp_list_pk:
                    tmp_list_pk.append(e)

        """ Initialise the elements for the process """
        connections = {}
        next_step = []
        start_table = list_tables[0]
        next_step.append(start_table)
        del list_tables

        """ - Main process - """
        query_string = 'SELECT * FROM ' + start_table + '\n'
        while len(next_step) > 0:
            tmp = {}
            for each in next_step:
                for col in all_tables_columns[each]:
                    for step_table in all_tables_columns.keys():
                        if next_step != step_table and step_table != start_table:
                            if col in all_tables_columns[step_table] and col in tmp_list_pk:
                                if step_table not in connections.keys():
                                    connections[step_table] = col
                                    tmp[step_table] = col

            next_step = [k for k in tmp.keys()]

        del all_tables_columns, tmp_list_pk, tmp

        for k, v in connections.items():
            query_string += "JOIN " + k + " USING (" + v + ")\n"

        del connections

        """ Just print the query string to be put in a SQL manager"""
        if self.echo:
            print(query_string)
            return
        return query_string

    def create(self):
        tables = JOIN.table_finder(self)
        p_keys = JOIN.primary_key_finder(tables)
        return JOIN.walk_tables(self, tables, p_keys)

    def launch(self):
        if not self.echo:
            query = JOIN.create(self)
            self.cur.execute(query)
            records = self.cur.fetchall()
            for record in records:
                print(record)
            return
        print('To view SQL use create()')
