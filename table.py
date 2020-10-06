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
        schema = (cur.fetchall())
        cache_tables = {}
        for table in schema:
            cur.execute("PRAGMA table_info ('" + table[0] + "')")
            result = cur.fetchall()
            cache_columns = []
            for column in result:
                cache_columns.append(column[1])
            cache_tables[table[0]] = cache_columns
        return cache_tables

    @staticmethod
    def print_sql():
        DataBase.print_string_sql = True


class Table(DataBase):

    def __init__(self, dbname, name):
        self.name = name
        DataBase.__init__(self, dbname)
        # self.dbname = dbname

    def create(self):
        """ Create one table at a time simply from the name of the initialisation of the object """

        cur = self.cur
        try:
            # cur.execute('DROP TABLE IF EXISTS ' + each)
            cur.execute('CREATE TABLE ' + self.name + '(id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT)')
            self.conn.commit()
            print("'{}' created successfully".format(self.name))
        except sqlite3.OperationalError as op:
            print(op)

    def delete(self):
        """ Deletes a table """

        cur = self.cur
        try:
            cur.execute('DROP TABLE ' + self.name)
            self.conn.commit()
            print("'{}' deleted successfully".format(self.name))
        except sqlite3.OperationalError as op:
            print(op)

    def rename(self, new_name):
        """ Just change the name of a table """

        cur = self.cur
        new_name.rstrip()
        new_name = new_name.replace(' ', '_')
        try:
            cur.execute('ALTER TABLE ' + self.name + ' RENAME TO ' + new_name)
            self.conn.commit()
            print("{} changed successfully into -> {}".format(self.name, new_name))
            Table.__init__(self, self.dbname, new_name)
        except sqlite3.OperationalError as op:
            print(op)

    def insert_column(self, *columns):  # to be updated for type inputs
        """ Create columns in the table object """

        cur = self.cur
        for column in columns:
            try:
                cur.execute('ALTER TABLE ' + self.name + ' ADD ' + column)
            except sqlite3.OperationalError as op:
                print(op)
                quit()
            print("'{}' added successfully".format(column))
        self.conn.commit()

    def drop_column(self, table, column): # to be updated
        """ Drop a column or a series of columns """

        cur = self.cur
        cur.execute('ALTER TABLE ' + table + ' DROP COLUMN ' + column)

    def rename_column(self, old_name, new_name):
        """ Change column name or columns """

        cur = self.cur
        try:
            cur.execute('ALTER TABLE ' + self.name + ' RENAME COLUMN ' + old_name + ' TO ' + new_name)
            self.conn.commit()
            print("{} renamed successfully into -> {}".format(old_name, new_name))
        except sqlite3.OperationalError as op:
            print(op)

    def add_data(self, columns: tuple or list, data: tuple or list):  # to be updated for type inputs
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
        try:
            cur.execute("INSERT OR IGNORE INTO " + self.name + " (" + column_string + ") VALUES (" + data_string + ")")
            self.conn.commit()
            print('Data uploaded successfully')
        except sqlite3.OperationalError as op:
            print(op)

    @staticmethod
    def and_or_query(dictionary: dict, _and=False, _or=False):
        condition_query = ''
        if _and and _or:
            raise TypeError
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
            pass
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
            # print('column string:', column_string): Debug

        # It writes the conditional part of the query if there is 0, one or more and it allows AND and OR statements
        if len(kwargs) == 0:
            # print('SELECT ' + column_string + ' FROM ' + self.name): Debug
            try:
                cur.execute('SELECT ' + column_string + ' FROM ' + self.name)
                result = cur.fetchall()
                # for each in result:
                #     print("{}".format(each))
                return result
            except sqlite3.OperationalError as op:
                print(op)
                quit()
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            condition_query = ''
            for key in kwargs:
                if isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                    condition_query += key + '=' + str(kwargs[key])
                else:
                    condition_query += key + "='" + kwargs[key] + "'"
        # print("SELECT " + column_string + " FROM " + self.name + " WHERE " + condition_query): Debug
        try:
            cur.execute("SELECT " + column_string + " FROM " + self.name + " WHERE " + condition_query)
            result = cur.fetchall()
            # for each in result:
            #     print("{}".format(each))
            return result
        except sqlite3.OperationalError as op:
            print(op)

    def fetch_all(self, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and=False, _or=False, **kwargs)
        for each in result:
            print(each)

    def fetch_one(self, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and=False, _or=False, **kwargs)
        print(result[0])

    def fetch_head(self, num=5, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and=False, _or=False, **kwargs)
        for each in result[:num]:
            print(each)

    def fetch_tail(self, num=5, *column, _and=False, _or=False, **kwargs):
        result = Table.fetch(self, *column, _and=False, _or=False, **kwargs)
        for each in result[-num:]:
            print(each)

    def update_data(self, column, new_data, _and=False, _or=False, **kwargs):  # to be updated AND and OR together
        """ It updates data into rows under a specific condition i.g: column=value """

        cur = self.cur
        condition_query = ''
        if len(kwargs) == 0:
            print('Please specify a condition')
            quit()
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            for key in kwargs:
                if isinstance(kwargs[key], int) or isinstance(kwargs[key], float):
                    condition_query += key + '=' + str(kwargs[key])
                else:
                    condition_query += key + "='" + kwargs[key] + "'"
        try:
            cur.execute("UPDATE " + self.name + " SET " + column + "='" + new_data + "' WHERE " + condition_query)
            self.conn.commit()
        except sqlite3.OperationalError as op:
            print(op)
            quit()
        print('Data updated successfully')
