# DataBase
- Introduction to OOP and SQL for database CRUD operations

The system is pretty straightforward: there are 2 classes (DataBase and Table), they both allows to create a database
connection and a Table object. The various methods represent a way to interact with a sqlite database, they form SQL queries
strings that are later executed.

I find a very reliable and quick way to use SQL with Python, instead of writing queries, but using a more pythonistic
approach of Object-oriented programming.

## Documentation

The system is pretty straightforward: there are 2 classes (DataBase and Table). 
The various methods represent a way to interact with my Server, they create SQL queries strings that are later executed.

To properly use this module you need both the ezSQL.py and config.py. The latter is essential to put credentials to access the mysql Server. 
If you don't have mysql installed well you should download it. You also need to have the mysql-connector-python package installed on your machine. 

Simply execute on bash

    python3 -m pip install mysql-connector-python

### Database(class)
* **DataBase**(self, dbname, echo=False): class

This class allows to create an instance of a database with proper connections to the mysql server. 
It takes 2 arguments: 

* dbname: The name of the database you want to create
* echo: A key argument with a default value of False. When set to True it allows to print SQL queries without executing them

### Methods
* **create_db**(self): method

It creates the database from the instance of the class. The title of the database will be the dbname given at initialisation. 
It doesn't take in any argument. 
A common syntax would be:
	
    >>> my_database = DataBase("my_db")
    >>> my_database.create_db()
    'my_db' created successfully

* **delete_db**(self): method

As the name suggests it deletes a database from the instance. There is no option to do it with the actual name of the database, 
this is because the connection to the mysql Server is obtained through the instance. Therefore, you need to first init the class 
and then you can delete it. The method takes no argument.

    >>> my_database.delete_db()
    'my_db' deleted successfully

### Table(class)
* **Table**(self, dbname, name, echo=False): class

This class manages tables in a database as objects. Thus, every method is called directly upon an instance which represents 
an actual table in the database. If the connection fails all the methods won't work. Although, you will still be able to 
print (echo=True) since this doesn't need a connection.
It takes 3 arguments: 
	
* **dbname**: The name of the database the table will be in. It is very important
		since this will provide the connection to the server for all the
		methods in the class. You may use a variable, hardcode the name or
		use the instance attribute .name -- my_db.dbname (from previous);
  
* **name**: The name of the table. This method require to initialise one table at 
	      a time. It is also a best practice 
  
* **echo**: A key argument with a default value of False. When set to True
	      it allows to print SQL queries without executing them

### Methods 
* **create**(self, **kwargs): method

It creates the table from the instance. It takes several key arguments and each key:value
represents the column name in the table and its data type. In mysql you must provide a data
type. In addition, the values must be given as strings. If no key argument is given the 
method creates a table with one id column set as default, in any case the id column will always be created 
as the default primary key. You can later change the name. In case, you can add columns later -- see insert_column
A common syntax:

    >>> emp = Table('my_db', 'Employee')
    >>> emp.create()
    'Employee' created successfully

In case you want to add columns:

    >>> emp.create(first_name='varchar(20)', last_name='varchar(20)', phone='int')
    'Employee' created successfully

The most common data types in mysql can be found on the documentation of the software itself. 
Most used are: 
1. INT for numbers 
   
2. DECIMAL for decimal numbers 
   
3. CHAR or VARCHAR for regular text. A number of character can be given in varchar
	       
4. DATE indicates the date as 'YYYY-MM-DD' 
   
5. BINARY or VARBINARY as char and varchar for binary strings (byte strings)	

* **describe**(self): method

It doesn't need any argument other than the instance and it returns the schema of a table. 
The result is usually a list of tuples. With a simple for loop it can be made more readable such as:


    >>> for each in emp.describe():
   	    print(each)
    ('id', b'int', 'NO', 'PRI', None, 'auto_increment') # id column auto generated -- see above
    ('first_name', b'varchar(20)', 'YES', '', None, '')
    ('last_name', b'varchar(20)', 'YES', '', None, '')
    ('phone', b'int', 'YES', '', None, '')

* **delete**(self): method

It deletes the table from the instance. It doesn't take any argument.

    >>> emp.delete()
    'Employee' deleted successfully

* **rename**(self, new_name): method

It renames a table. it is recommended not to put spaces in the name, in any case they will be changed into _. 
It must be noted that, since the name of a table is related to the instance this method will also change 
the instance itself reinitialising it, so that all the attributes are updated.

    >>> emp.rename("Employees")
    Employee changed successfully into => Employees
    >>> emp.name
    Employees

* **insert_column**(self, column, d_type): method

  It inserts columns into a table. It is recommended to insert one column at a time and, again, 
  in mysql a data type must be provided.

  * **column**: It's the name the column will have. 
  
  * **d_type**: The data type of the column. To see data types accepted in mysql, please 
  refer to "create" (method) above
  

        >>> emp.insert_column("role", "varchar(20)")
        'role' added successfully

* **insert_foreign_key**(self, column_fk, table_name, d_type): method

  It creates a single column with an attribute of foreign key. 
  It takes 3 arguments:
  * **column_fk**: The table is set from the instance, so there is no need to provide it. This will also be the name the 
		   column will have once it's created. Notice that the name of this column will be the same of the one is 
		   referring to. This is to simplify search operations, to be more readable and overall a best practice 
		   when dealing with Relational Databases
	
  * **table_name**: This is the name of the table where the column is referring to
	
  * **d_type**: As above is the data type of the column, which in the case of foreign keys should always be INT, 
		but it provides a bit of flexibility
    

        >>> emp.insert_foreign_key("branch_id", "Branch", "int")
        Foreign key added successfully

* **many_to_many**(self, keys: tuple or list, d_type: tuple or list): method

  This method allows to create tables for many to many relationships. Reminder: the table still needs to be 
  initialised as per other tables (see above). In theory, these tables have 2 or more columns and the primary 
  keys are represented by the unique combination of these columns.
  For these reasons such tables needs to be created after the creation of the parent table, and in this case 
  it is essential to do so because there would be no reference table and the method would throw an error. 
  It takes 2 arguments as iterables (either tuple or list):
	
  * **keys**: This represents the names of the columns in the table and for best practice they must have 
	      the same names of the columns they refer to. There must be a reference to the table too 
	      as Table.column -- (see example below)
    
  * **d_type**: It takes the data types for the various columns. Again, it should be integer by default but 
		it is always better to have some flexibility


        >>> many_rel = Table("my_db", "ManyToMany")
        >>> many_rel.many_to_many(("Employees.employees_id", "Branch.branch_id"), ("int", "int"))
        'ManyToMany' created successfully

This operation has created a table named ManyToMany with 2 columns: employees_id and branch_id.
The combination of this 2 columns will be unique an it is used to resolve many to many relationships.

* **delete_column**(self, column): method

  It allows to delete a column from a table. As best practice it is recommended to delete 1 column at a time 
  and it is strongly encouraged, when dealing with databases, to keep delete operations under control. 
  In SQL once a record is gone, is gone. 
  It takes 1 argument:
	
  * **column**: it refers to the column to be deleted. The table is inferred from the instance
    

        >>> emp.delete_column("phone")
        'phone' deleted successfully

* **rename_column**(self, old_name, new_name): method

  As the name implies it allows to rename a column in a table. It takes 2 arguments:
  
  * **old_name**: It is the name of the existing column. If the column doesn't exist the method will raise an error
	
  * **new_name**: It is the new name the column will have. Don't use spaces, instead use _


        >>> emp.rename_column("role", "position")
        role renamed successfully into => position

* **add_record**(self, columns: tuple or list, data: tuple or list): method

  It allows inserting record in a table. This method in particular needs 2 iterable arguments, 
  one representing the column, and the other representing the actual record. 

  * **columns**: As the plural suggests it takes an iterable object with all the names of the columns you want to insert data into
	
  * **data**: The actual data that go into the columns


        >>> emp.add_record(("first_name","last_name","phone"), ("John", "Smith", 1234567))
        Data uploaded successfully

It is important that the 2 arguments have the same length (number of parameters) or else the method will raise an error.
In addition, if no argument is given it will raise an error, as well.

*TODO*: I am currently trying to create a similar method that takes a dictionary instead of tuples. 
In that case, records would be referenced as key:value pairs. On a side note, expanding such method could 
potentially take JSON files and directly upload them into a table.

* **fetch**(self, num=-1, column=(), _and=False, _or=False, **kwargs): method

  In the CRUD logic this method introduces the READ function as search. There are various methods for 
  database search, this is the first one. It returns the result of the search.
  It takes 4 arguments and n key arguments:
	
  * **num**: It sets the number of results the search will yield. Default value -1 will give all the 
	     results as in fetchall()
	
  * **column**: It must be an iterable object and it defines the columns to be showed from the search. 
		If left undefined, the default value will yield all the columns (*)
	
  * **_and**: In case of complex search with multiple conditions. It introduces a logical AND to the query. 
	      Beware if the conditions are not more than 1 this parameter will have no effect. 
	      Default is set to False, just set it to True
	
  * **_or**: In case of complex search with multiple conditions. It introduces a logical OR to the query. 
	     Beware if the conditions are not more than 1 this parameter will have no effect. 
	     Default is set to False, just set it to True
	
  * __**kwargs__: Key arguments for conditions in the search


        >>> emp.fetch()
        [(1, 'John', 'Smith', 1234567, None, None)]
        >>> emp.fetch(column=("first_name", "last_name")))
        [('John', 'Smith')]
        >>> emp = Table('testing_db', 'Employees', echo=True)
        >>> emp.fetch(_and=True, id=1, first_name="John")
        SELECT * FROM Employees WHERE id=1 AND first_name='John'

* **join_search**(self, 
		table, 
		f_key, 
		column: tuple or list, 
		num=-1, 
		_and=False, 
		_or=False, 
		**kwargs): method

  As the name suggest it allows to lunch a SQL query in multiple tables, namely join search. 
  It is important that the name of the foreign keys used for the join statement are identical. 
  This is probably true thanks to the constrains on previous methods.
  It takes 6 arguments and n key arguments:

  * **table**: Table with which the instance need to be joined;
	
  *  **f_key**: column that acts as binder between the tables;
	
  * **column**: The columns that will be shown in the search. If left undefined it will show all the 
		columns (*) by default;
	
  * **num**: The number of results the search will yield. Default value -1 will give all the results. 
	     *Notice*: if num is bigger than the number of records in the result no error will be returned 
    but you will only get what's in there;
	
  * **_and**: In case of complex search with multiple conditions. It introduces a logical AND to the query. 
	      Beware if the conditions are not more than 1 this parameter will have no effect. 
	      Default is set to False, just set it to True;
	
  * **_or**: In case of complex search with multiple conditions. It introduces a logical OR to the query. 
	     Beware if the conditions are not more than 1 this parameter will have no effect. 
	     Default is set to False, just set it to True;
	
  * __**kwargs__: Key arguments for conditions in the search


        >>> emp.join_search(table="Address", f_key="address_id") 
        [(1, 1, 'John', 'Smith', 1234567, None, 'Beverly Hills St', '90210', 'Los Angeles', 'USA', None)]
        >>> emp = Table('testing_db', 'Employees', echo=True)
        >>> emp.join_search(table="Address", f_key="address_id", column=("first_name", "last_name", "street"))
        SELECT first_name, last_name, street FROM Employees JOIN Address USING (address_id)

* **regexp_search**(self, num=-1, **kwargs): method

  It allows a database search via Regular Expressions. To see all the RegExp for SQL you can consult 
  the documentation in mysql. There is a brief description as docstring in the method.
  It takes 1 argument and 1 key argument:
	
  * **num**: It dictates the number of results the search yields. Default value is -1 and
	     it will return all the results;
    
  * __**kwargs__: It takes just 1 key:value pair. You can insert how many you want but they won't
		  be considered. The format is column="RegularExpression". 


        >>> emp.regexp_search(first_name='^J') # mysql is not case sensitive
        [(1, 'John', 'Smith', 1234567, None, 1)]
        >>> emp.regexp_search(last_name='th')
        [(1, 'John', 'Smith', 1234567, None, 1)]

* **update_record**(self, column, new_data, _and=False, _or=False, **kwargs): method

  It allows to update a particular record where a condition is defined, therefore a condition 
  must be defined or the method will raise an error. It takes 4 arguments and n key arguments):

  * **column**: Specify the column to be updated;
	
  * **new_data**: It's the new record you want to add or change. Reminder - all update actions are destructive, 
		  which means that the previous record will not be available anymore;
	
  * **_and**: In case of complex search with multiple conditions. It introduces a logical AND to
	      the query. Beware if the conditions are not more than 1 this parameter will have no effect. 
	      Default is set to False, just set it to True;
    
  * **_or**: In case of complex search with multiple conditions. It introduces a logical OR to the query. 
	     Beware if the conditions are not more than 1 this parameter will have no effect. 
	     Default is set to False, just set it to True;
	
  * __**kwargs__: Key arguments for conditions in the search;

Again, as best practice it is recommended to update one record at a time because 
the previous value will be unreachable after the method.

    >>> emp.update_record("first_name", "Paul")  # no condition
    Data updated successfully
    >>> emp.update_record("last_name", "Smithson", id=1)
    Data updated successfully

* **delete_record**(self, num=1, **condition): method

  It allows to delete a record from a table. By default it will eliminate 1 record at a time 
  even if the condition matches multiple records. This is to prevent accidental removal of records. 
  You can set the method to delete all the records, just set num=-1. Although it is possible, 
  it is not recommended - see above. The method takes 1 argument and 1 key argument:

  * **num**: It specifies the number of records that match the condition. to be deleted. By default it is set to 1. 
	     To have all the records deleted at once just set it to -1
	
  * __**condition__: Specifies the condition for removal of records. You can put as many as you want but only 
		     the first condition will be taken into consideration. this is   
		     to guarantee a higher level of safety, preventing batch delete actions.

### JOIN(class)
This class is meant to simplify the join operations in SQL. Theoretically, it can create a join statement for any given
database. It is based upon a best practice that I understand it's not always abide by: the table keys must have the same 
names from the parent table to the child. \
*Ex:* A table with primary key == myTable_id has a child or related table (myRelatedTable) that has a 
foreign key == myTable_id. 

In this way the class will work properly and be very helpful because it can join countless tables as long as there is a
 relationship among them. This is something that you should be careful about when organising and managing a database.

To be initialised this class only necessitates of 1 argument, the 2nd argument can be omitted: 
* **dbname**: the name of the database it will run the script to. It takes a string and also you should configure the 
  database connection in the config file;
* **echo**: By default is set to False. When True no method will be executed, but the query will be returned entirely 
in string format, to be used in your SQL admin of choice. It could be very helpful instead of writing and considering 
  all the different relationships.
  
### Methods
* **describe**(self, name): method \
  It's a method intended as private that returns a list of tuples with information about the table passed in the name argument
  * **name**: the name of the table to describe;
    

* **table_finder**(self): method \
  Once again, a private method to retrieve all the tables in the database. The basic concept of this class is that 
  it has to build a virtual model of the database made of table, relationships and name. You will see other methods like this 
  one being executed. It doesn't take in any argument since it only considers the db specified in the instance. 
  It returns a list of names.
  

* **find_columns_in_table**(self, *args): method \
  Another private method. It takes in *args for table names. It returns a dictionary with key == tableName and 
  value == a list of columns in that table. As I mentioned before, it is used by the class to build the db model.
  

* **primary_key_finder**(from_table_finder: *dict*): method \
  A private static method to find and classify all the tables' primary keys. It is extremely important to do this since 
  a big part of database logic comprises primary keys.
  The only argument is a dictionary, and it comes from the previous methods:
  * **from_table_finder**: A dictionary with key == tableName and value == list(columnNames).
    

* **walk_tables**(self, table: *dict*, primary_keys: *dict*): method \
  This method represents the main logic of the class. Thanks to the db model provided by the 2 private methods, 
  this logic will walk through the table and map their relationship. In this case, it is fundamental that the 
  key concept of primary keys == foreign keys, is respected. \
  It doesn't care about the order of the tables in the database because it is set to join each one that has relationships
   with a main one, or start. As long as the tables have connections this method won't fail. 
  

* **join_all**(self): method \
  It returns a string as a SQL statement for joining all the tables in the database. This method doesn't actually 
  execute the join, it only provides the query string. It should be used in conjuction with **echo=True**.
  

* **join_some**(self, *args): method \
  Similar to the one before, it returns a string to join only the tables provided in the *args argument. 
  It doesn't execute the command, only prints out the query when **echo=True**.
  

### Main Executable methods
* **global_search**(self): method
  This is the main callable method that utilises all the private methods to build the db model, build the 
  query string and finally execute the command when **echo=False** \
  It doesn't take any arguments and it returns a global result of all the records in the database, across all tables.
  

* **local_search**(self, *args): method \
  The second main callable method. It returns a list of results from the tables specified in the *args argument.
  
  
    
Thanks,\
@BeGeos