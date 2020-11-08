import mysql.connector
import config


class DataBase:

    def __init__(self, dbname, echo=False):
        self.dbname = dbname
        self.echo = echo
        self.conn = mysql.connector.connect(host=config.host,
                                            user=config.user,
                                            passwd=config.password)
        self.cur = self.conn.cursor()

    def create_db(self):
        """ Create a database from the instance. It stills need to be called """

        create_string = "CREATE DATABASE " + self.dbname
        try:
            self.cur.execute(create_string)
            print("'{}' created successfully".format(self.dbname))
        except mysql.connector.Error as err:
            print(err)

    def delete_db(self):
        delete_string = "DROP DATABASE " + self.dbname
        try:
            self.cur.execute(delete_string)
            print("'{}' deleted successfully".format(self.dbname))
        except mysql.connector.Error as err:
            print(err)


class Table:

    def __init__(self, dbname, name, echo=False):
        self.name = name
        self.echo = echo
        self.dbname = dbname
        try:
            self.conn = mysql.connector.connect(host=config.host,
                                                user=config.user,
                                                passwd=config.password,
                                                database=dbname)
            self.cur = self.conn.cursor()
        except mysql.connector.Error as err:
            print(err)

    @staticmethod
    def if_type(dictionary):
        condition_query = ''
        for key in dictionary:
            if isinstance(dictionary[key], int) or isinstance(dictionary[key], float):
                condition_query += key + '=' + str(dictionary[key])
            else:
                condition_query += key + "='" + dictionary[key] + "'"
        return condition_query

    def create(self, default=True, p_key=None, **kwargs):
        """ Create one table at a time simply from the name of the initialisation of the object
        You can also create your own primary key, just set uid=False, and indicate the column that
        will be the primary key. Beware: this action will not set the auto_increment option to your
        primary key. """

        first_id = self.name + '_id'
        if default and len(kwargs) != 0:
            condition_query = ''
            for key in kwargs:
                condition_query += key + ' ' + kwargs[key].upper() + ', '
            cat_string = ("CREATE TABLE " + self.name + " (" + first_id.lower() +
                          " INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT," +
                          condition_query[:-2] + ")")
        elif default and len(kwargs) == 0:
            cat_string = ("CREATE TABLE " + self.name + " (" + first_id +
                          " INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT)")
        elif not default and len(kwargs) != 0:
            if p_key is None:
                raise ValueError('-- There must be a primary key, please specify --')
            condition_query = ''
            for key in kwargs:
                if key == p_key:
                    condition_query += key + ' ' + kwargs[key].upper() + ' NOT NULL PRIMARY KEY, '
                else:
                    condition_query += key + ' ' + kwargs[key].upper() + ', '
            cat_string = ("CREATE TABLE " + self.name + " (" + condition_query[:-2] + ")")
        elif not default and len(kwargs) == 0:
            raise ValueError('Cannot create table with [0] columns!')
        else:
            cat_string = None
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("'{}' created successfully".format(self.name))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def describe(self):
        """ Description of Table schema  """

        joint = '.'.join([self.dbname, self.name])
        string = "DESCRIBE " + joint
        if self.echo:
            print(string)
            return
        self.cur.execute(string)
        return self.cur.fetchall()

    def delete(self):
        """ Deletes a table """

        cat_string = 'DROP TABLE ' + self.name
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("'{}' deleted successfully".format(self.name))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def rename(self, new_name):
        """ Just change the name of a table """

        new_name.rstrip()
        new_name = new_name.replace(' ', '_')
        cat_string = ('ALTER TABLE ' + self.name + ' RENAME TO ' + new_name)
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("{} changed successfully into => {}".format(self.name, new_name))
            self.conn.close()
            Table.__init__(self, self.dbname, new_name)
        except mysql.connector.Error as err:
            print(err)

    def insert_column(self, column, d_type):
        """ Create columns in the table object one at a time """

        column.rstrip()
        column = column.replace(' ', '_')
        cat_string = ('ALTER TABLE ' + self.name + ' ADD ' + column + ' ' + d_type.upper())
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("'{}' added successfully".format(column))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def insert_foreign_key(self, column_fk, table_name, d_type):
        """ It allows to create an individual column with the attribute foreign key.
         It is also a best practice to have the names of both foreign keys identical to simplify
         the search. See join_search"""

        fk = column_fk + " " + d_type.upper() + " REFERENCES " + table_name + "(" + column_fk + ")"
        cat_string = "ALTER TABLE " + self.name + " ADD " + fk
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print('Foreign key added successfully')
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def many_to_many(self, keys: tuple or list, d_type: tuple or list):
        """ To create relations many to many. It is important that the data are iterables with more
        than 1 element. In addition, it is also essential to specify the column and the table it is referring to
        in the args argument, in this way: Table.column. It is also recommended to rename the id column
        in the main table not create overlaps or redundancies. """

        if len(keys) <= 1:
            raise Exception('Not enough elements found')
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
        cat_string = "CREATE TABLE " + self.name + " (" + d_type_string + unique_string + ")"
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("'{}' created successfully".format(self.name))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def delete_column(self, column):
        """ Drop a column """

        cat_string = ('ALTER TABLE ' + self.name + ' DROP COLUMN ' + column)
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("'{}' deleted successfully".format(self.name))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def rename_column(self, old_name, new_name):
        """ Change column name or columns """

        cat_string = ('ALTER TABLE ' + self.name + ' RENAME COLUMN ' + old_name + ' TO ' + new_name)
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            self.conn.commit()
            print("{} renamed successfully into => {}".format(old_name, new_name))
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def add_record(self, columns: tuple or list, data: tuple or list):
        """As the name suggests it populates the rows in a specific table, namely the table object.
        It is important that the number of columns match the number of data per input and
        that the type of the two parameters remain iterables either tuples or lists """

        if len(data) == 0:
            raise ValueError('No record to be added')
        elif len(columns) != len(data):
            raise ValueError('Number mismatch between columns and data')

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
            self.cur.execute(cat_string)
            self.conn.commit()
            print('Data uploaded successfully')
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    # def add_record_via_dictionary():  to be updated

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

    def fetch(self, num=-1, column=(), _and=False, _or=False, **kwargs):  # SELECT column FROM Table WHERE ""
        """ Write a query in the database """

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
            if num != -1:
                cat_string = 'SELECT ' + column_string + ' FROM ' + self.name + ' LIMIT ' + str(num)
            else:
                cat_string = ('SELECT ' + column_string + ' FROM ' + self.name)
            if self.echo:
                print(cat_string)
                return
            try:
                self.cur.execute(cat_string)
                result = self.cur.fetchall()
                return result
            except mysql.connector.Error as err:
                print(err)
                quit()
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            condition_query = Table.if_type(kwargs)
        cat_string = ("SELECT " + column_string + " FROM " + self.name + " WHERE " + condition_query)
        if num != -1:
            cat_string = cat_string + "LIMIT " + str(num)
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            result = self.cur.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def join_search(self, table, f_key, column: tuple or list, num=-1, _and=False, _or=False, **kwargs):
        """ Implementing join search in SQL database. Make sure that the key name is identical
         in the table you want to join """

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
            if num != -1:
                cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                             " USING (" + f_key + ") LIMIT " + str(num)
            else:
                cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                             " USING (" + f_key + ")"
            if self.echo:
                print(cat_string)
                return
            try:
                self.cur.execute(cat_string)
                result = self.cur.fetchall()
                return result
            except mysql.connector.Error as err:
                print(err)
                quit()
        elif len(kwargs) > 1:
            condition_query = Table.and_or_query(kwargs, _and, _or)
        else:
            condition_query = Table.if_type(kwargs)

        cat_string = "SELECT " + column_string + " FROM " + self.name + " JOIN " + table + \
                     " USING (" + f_key + ") WHERE " + condition_query
        if num != -1:
            cat_string = cat_string + " LIMIT " + str(num)
        if self.echo:
            print(cat_string)
            return
        try:
            self.cur.execute(cat_string)
            result = self.cur.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def regexp_search(self, num=-1, **kwargs):  # SELECT * FROM Table WHERE column REGEXP ....
        """ It allows to search via regular expression in SQL. The condition must be 1 only as key:value pair.
         Reminder: * Zero or more instances of string preceding it
                   + One or more instances of strings preceding it
                   . Any single character
                   ? Match zero or one instance of the strings preceding it
                   ^ Matches beginning of a string
                   $ End of a string
                   [a-z][0-9] Match a range of letters or numbers (SQL is case sensitive)
                   string1|string2|string(n) Logical OR """

        cond_list = list(kwargs.items())
        query = "SELECT * FROM " + self.name + " WHERE " + cond_list[0][0] + " REGEXP '" + cond_list[0][1] + "' "
        if num != -1:
            limit_string = "LIMIT " + str(num)
            final_query = query + limit_string
        else:
            final_query = query
        if self.echo:
            print(final_query)
            return
        try:
            self.cur.execute(final_query)
            result = self.cur.fetchall()
            return result
        except mysql.connector.Error as err:
            print(err)

    def update_record(self, column, new_data, _and=False, _or=False, **kwargs):  # to be updated AND and OR together
        """ It updates data into rows under a specific condition i.g: column=value """

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
            self.cur.execute(cat_string)
            self.conn.commit()
            print('Data updated successfully')
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)

    def delete_record(self, num=1, **condition):
        """ It deletes record from a table and by default it is set at 1 record. Deleting is quite
        dangerous therefore I recommend not to change the default value. However, if you really want
        you can set the number of records to delete in one go. To delete all record with a certain
        condition just set num to -1 """

        cond_string = list(condition.items())
        del_string = "DELETE FROM " + self.name + " WHERE " + cond_string[0][0] + "=" + cond_string[0][1]
        if num == 1:
            final_string = del_string + " LIMIT 1"
        elif num > 1:
            final_string = del_string + " LIMIT " + str(num)
        elif num == -1:  # This will delete ALL records with the set condition
            final_string = del_string
        else:
            print('The limit is not a valid number')
            quit()
        if self.echo:
            print(final_string)
            return
        try:
            self.cur.execute(final_string)
            self.conn.commit()
            print("Record/s deleted successfully")
            self.conn.close()
        except mysql.connector.Error as err:
            print(err)
