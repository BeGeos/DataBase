import sqlite3


class DataBase:
    print_string_sql = False

    def __init__(self, dbname):
        self.dbname = dbname + '.sqlite'
        self.conn = sqlite3.connect(self.dbname)
        self.cur = self.conn.cursor()

    def db_schema(self):
        cur = self.cur
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        schema = cur.fetchall()
        cache_tables = {}
        for table in schema:
            cur.execute("PRAGMA table_info ('" + table[0] + "')")
            result = cur.fetchall()
            cache_columns = []
            for column in result:
                cache_columns.append(column[1:])
            cache_tables[table[0]] = cache_columns
        for k in cache_tables:
            if k != 'sqlite_sequence':
                print(k, cache_tables[k])

    @staticmethod
    def print_sql():
        DataBase.print_string_sql = True


class Table(DataBase):

    def __init__(self, name):
        self.name = name
        super().__init__('Table')
        # self.dbname = dbname

    @staticmethod
    def if_type(dictionary):
        condition_query = ''
        for key in dictionary:
            if isinstance(dictionary[key], int) or isinstance(dictionary[key], float):
                condition_query += key + '=' + str(dictionary[key])
            else:
                condition_query += key + "='" + dictionary[key] + "'"
        return condition_query

    def create(self, **kwargs):
        """ Create one table at a time simply from the name of the initialisation of the object """

        cur = self.cur
        if len(kwargs) != 0:
            condition_query = ''
            for key in kwargs:
                condition_query += key + ' ' + kwargs[key] + ', '
            cat_string = ("CREATE TABLE " + self.name + "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                                                        + condition_query[:-2] + ")")
        else:
            cat_string = ("CREATE TABLE " + self.name + "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)")
        # print(cat_string)
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("'{}' created successfully".format(self.name))
        except sqlite3.OperationalError as op:
            print(op)

    def delete(self):
        """ Deletes a table """

        cur = self.cur
        cat_string = 'DROP TABLE ' + self.name
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("'{}' deleted successfully".format(self.name))
        except sqlite3.OperationalError as op:
            print(op)

    def rename(self, new_name):
        """ Just change the name of a table """

        cur = self.cur
        new_name.rstrip()
        new_name = new_name.replace(' ', '_')
        cat_string = ('ALTER TABLE ' + self.name + ' RENAME TO ' + new_name)
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("{} changed successfully into -> {}".format(self.name, new_name))
            Table.__init__(self, new_name)
        except sqlite3.OperationalError as op:
            print(op)

    def insert_column(self, column, d_type=''):
        """ Create columns in the table object """

        cur = self.cur
        cat_string = ('ALTER TABLE ' + self.name + ' ADD ' + column + ' ' + d_type.upper())
        # print(cat_string)
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("'{}' added successfully".format(column))
        except sqlite3.OperationalError as op:
            print(op)

    def insert_foreign_key(self, column_from, column_to, d_type):
        """ It allows to create an individual column with the attribute foreign key.
        It is essential to refer the table name in the column to as argument as Table_name.column_fk """

        cur = self.cur
        column_to = column_to.split('.')
        fk = column_from + " " + d_type + " REFERENCES " + column_to[0] + "(" + column_to[1] + ")"
        cat_string = "ALTER TABLE " + self.name + " ADD " + fk
        # print(cat_string)
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print('Foreign key added successfully')
        except sqlite3.OperationalError as op:
            print(op)

    def drop_column(self, column): # to be updated
        """ Drop a column or a series of columns """

        cur = self.cur
        cat_string = ('ALTER TABLE ' + self.name + ' DROP COLUMN ' + column)
        cur.execute(cat_string)

    def rename_column(self, old_name, new_name):
        """ Change column name or columns """

        cur = self.cur
        cat_string = ('ALTER TABLE ' + self.name + ' RENAME COLUMN ' + old_name + ' TO ' + new_name)
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("{} renamed successfully into -> {}".format(old_name, new_name))
        except sqlite3.OperationalError as op:
            print(op)

    def add_data(self, columns: tuple or list, data: tuple or list):
        """As the name suggests it populates the rows in a specific table, namely the table object.
        It is important that the number of columns match the number of data per input and
        that the type of the two parameters remain iterables either tuples or lists """

        if len(columns) != len(data):
            print('Number mismatch between columns and data')
            quit()

        cur = self.cur

        column_string = ''
        data_string = ''
        for column in columns:
            column = str(column)
            column = column + ","
            column_string += column
        column_string = column_string[:-1]
        for each in data:
            each = str(each)
            each = "'" + each + "',"
            data_string += each
        data_string = data_string[:-1]
        cat_string = ("INSERT OR IGNORE INTO " + self.name + " (" + column_string + ") VALUES (" + data_string + ")")
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print('Data uploaded successfully')
        except sqlite3.OperationalError as op:
            print(op)

    @staticmethod
    def and_or_query(dictionary: dict, _and=False, _or=False):
        condition_query = ''
        if _and and _or:
            print('Is either AND or OR!')
            quit()
        elif _and:
            for key in dictionary:
                if isinstance(dictionary[key], int) or isinstance(dictionary[key], float):
                    condition_query += key + '=' + str(dictionary[key]) + " AND "
                else:
                    condition_query += key + "='" + dictionary[key] + "' AND "
            condition_query = condition_query[:-4]
        elif _or:
            for key in dictionary:
                if isinstance(dictionary[key], int) or isinstance(dictionary[key], float):
                    condition_query += key + '=' + str(dictionary[key]) + " OR "
                else:
                    condition_query += key + "='" + dictionary[key] + "' OR "
            condition_query = condition_query[:-4]
        else:
            print('Is either AND or OR! ')
            quit()
        return condition_query

    def fetch(self, *column, _and=False, _or=False, **kwargs):  # SELECT column FROM Table WHERE "...."
        """ Write a query in the database """

        cur = self.cur
        # It writes the column part of the query
        column_string = ''
        if len(column) == 0:
            column_string = '*'
        else:
            for c in column:
                column_string += c + ", "
            column_string = column_string[:-2]

        # It writes the conditional part of the query if there is 0, one or more and it allows AND and OR statements
        if len(kwargs) == 0:
            cat_string = ('SELECT ' + column_string + ' FROM ' + self.name)
            try:
                cur.execute(cat_string)
                result = cur.fetchall()
                return result
            except sqlite3.OperationalError as op:
                print(op)
                quit()
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            condition_query = Table.if_type(kwargs)
        cat_string = ("SELECT " + column_string + " FROM " + self.name + " WHERE " + condition_query)
        try:
            cur.execute(cat_string)
            result = cur.fetchall()
            return result
        except sqlite3.OperationalError as op:
            print(op)

    def fetch_all(self, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and, _or, **kwargs)
        for each in result:
            print(each)

    def fetch_one(self, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and, _or, **kwargs)
        print(result[0])

    def fetch_head(self, num=5, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and, _or, **kwargs)
        for each in result[:num]:
            print(each)

    def fetch_tail(self, num=5, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and=False, _or=False, **kwargs)
        for each in result[-num:]:
            print(each)

    def update_data(self, column, new_data, _and=False, _or=False, **kwargs):  # to be updated AND and OR together
        """ It updates data into rows under a specific condition i.g: column=value """

        cur = self.cur
        if len(kwargs) == 0:
            raise TypeError
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            condition_query = Table.if_type(kwargs)
        cat_string = ("UPDATE " + self.name + " SET " + column + "='" + new_data + "' WHERE " + condition_query)

        try:
            cur.execute(cat_string)
            self.conn.commit()
            print('Data updated successfully')
        except sqlite3.OperationalError as op:
            print(op)
