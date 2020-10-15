import sqlite3


class DataBase:

    def __init__(self, dbname, echo=False):
        self.dbname = dbname + '.sqlite'
        self.echo = echo
        self.conn = sqlite3.connect(self.dbname)
        self.cur = self.conn.cursor()

    def db_schema(self):
        cur = self.cur
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        if self.echo:
            print(query)
        cur.execute(query)
        schema = cur.fetchall()
        cache_tables = {}
        for table in schema:
            iterate_query = "PRAGMA table_info ('" + table[0] + "')"
            cur.execute(iterate_query)
            if self.echo:
                print(iterate_query)
            result = cur.fetchall()
            cache_columns = []
            for column in result:
                cache_columns.append(column[1:])
            cache_tables[table[0]] = cache_columns
        return cache_tables


class Table(DataBase):

    def __init__(self, dbname, name, echo=False):
        name.rstrip()
        name = name.replace(' ', '_')
        self.name = name
        DataBase.__init__(self, dbname, echo)
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
        print(self.echo)
        cur = self.cur
        if len(kwargs) != 0:
            condition_query = ''
            for key in kwargs:
                condition_query += key + ' ' + kwargs[key] + ', '
            cat_string = ("CREATE TABLE " + self.name + "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"
                                                        + condition_query[:-2] + ")")
        else:
            cat_string = ("CREATE TABLE " + self.name + "(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)")
        if self.echo:
            print(cat_string)
            return
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
        if self.echo:
            print(cat_string)
            return
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
        if self.echol:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("{} changed successfully into -> {}".format(self.name, new_name))
            Table.__init__(self, self.dbname, new_name)
        except sqlite3.OperationalError as op:
            print(op)

    def insert_column(self, column, d_type=''):
        """ Create columns in the table object one at a time """

        cur = self.cur
        column.rstrip()
        column = column.replace(' ', '_')
        cat_string = ('ALTER TABLE ' + self.name + ' ADD ' + column + ' ' + d_type.upper())
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("'{}' added successfully".format(column))
        except sqlite3.OperationalError as op:
            print(op)

    def insert_foreign_key(self, column_from, column_to, d_type):
        """ It allows to create an individual column with the attribute foreign key.
        It is essential to refer the table name in the column_to as argument as Table_name.column_fk.
         It is also a best practice to have the names of both foreign keys identical to simply
         the search. See join_search"""

        cur = self.cur
        column_to = column_to.split('.')
        fk = column_from + " " + d_type + " REFERENCES " + column_to[0] + "(" + column_to[1] + ")"
        cat_string = "ALTER TABLE " + self.name + " ADD " + fk
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print('Foreign key added successfully')
        except sqlite3.OperationalError as op:
            print(op)

    def many_to_many(self, keys: tuple or list, d_type: tuple or list):  # tbu as dictionary
        """ To create relations many to many. It is important that the data are iterables and more
        than 1. In addition, it is also essential to specify the column and the table it is referring to
        in the args argument, in this way: Table.column. It is also recommended to rename the id column
        in the main table not create overlaps or redundancies. """

        if len(keys) <= 1:
            raise TypeError
        elif len(keys) != len(d_type):
            raise TypeError
        fk_string = ''
        column_string = ''
        d_type_string = ''
        # It creates the first part of the SQL query to create the column and their data type and
        # the second part of the query which match the foreign keys and the tables, all together
        for each in zip(keys, d_type):
            parsed = each[0].split('.')
            table = parsed[0]
            column = parsed[1]
            column_string += column + ","
            d_type_string += column + " " + each[1] + " NOT NULL,\n"
            fk_string += "FOREIGN KEY (" + column + ") REFERENCES " + table + "(" + column + "),\n"
        unique_string = fk_string + "UNIQUE (" + column_string[:-1] + ")"
        cat_string = "CREATE TABLE " + self.name + "(" + d_type_string + unique_string + ")"
        if self.echo:
            print(cat_string)
            return
        cur = self.cur
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("'{}' created successfully".format(self.name))
        except sqlite3.OperationalError as op:
            print(op)

    def delete_column(self, column):  # to be updated
        """ Drop a column or a series of columns """

        cat_string = ('ALTER TABLE ' + self.name + ' DROP COLUMN ' + column)
        if self.echo:
            print(cat_string)
            return

        cur = self.cur
        cur.execute(cat_string)

    def rename_column(self, old_name, new_name):
        """ Change column name or columns """

        cur = self.cur
        cat_string = ('ALTER TABLE ' + self.name + ' RENAME COLUMN ' + old_name + ' TO ' + new_name)
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print("{} renamed successfully into -> {}".format(old_name, new_name))
        except sqlite3.OperationalError as op:
            print(op)

    def add_record(self, columns: tuple or list, data: tuple or list):
        """As the name suggests it populates the rows in a specific table, namely the table object.
        It is important that the number of columns match the number of data per input and
        that the type of the two parameters remain iterables either tuples or lists """

        if len(columns) == 0:
            print('No record to be added')
            quit()
        elif len(columns) != len(data):
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
        cat_string = ("INSERT INTO " + self.name + " (" + column_string + ") VALUES (" + data_string + ")")
        if self.echo:
            print(cat_string)
            return
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

    def fetch(self, num=0, column=(), _and=False, _or=False, **kwargs):  # SELECT column FROM Table WHERE ""
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
            if num != 0:
                cat_string = 'SELECT ' + column_string + ' FROM ' + self.name + ' LIMIT ' + str(num)
            else:
                cat_string = ('SELECT ' + column_string + ' FROM ' + self.name)
            if self.echo:
                print(cat_string)
                return
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
        if num != 0:
            cat_string = cat_string + "LIMIT " + str(num)
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            result = cur.fetchall()
            return result
        except sqlite3.OperationalError as op:
            print(op)

    def join_search(self, table, key, column: tuple or list, num=0, _and=False, _or=False, **kwargs):
        """ Implementing join search in SQL database. Make sure that the key name is identical
         in the table you want to join """

        cur = self.cur
        # It writes the column part of the query
        column_string = ''
        if len(column) == 0:
            column_string = '*'
        else:
            for c in column:
                column_string += c + ", "
            column_string = column_string[:-2]
        # It write the conditional part of the query WHERE = ...
        if len(kwargs) == 0:
            if num != 0:
                cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                             " USING (" + key + ") LIMIT " + str(num)
            else:
                cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                             " USING (" + key + ")"
            if self.echo:
                print(cat_string)
                return
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

        cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                     " USING (" + key + ") WHERE " + condition_query
        if num != 0:
            cat_string = cat_string + " LIMIT " + str(num)
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            result = cur.fetchall()
            return result
        except sqlite3.OperationalError as op:
            print(op)

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
        if self.echo:
            print(cat_string)
            return
        try:
            cur.execute(cat_string)
            self.conn.commit()
            print('Data updated successfully')
        except sqlite3.OperationalError as op:
            print(op)
