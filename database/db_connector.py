import os
from pathlib import Path
from dotenv import load_dotenv
import MySQLdb

# used AI for the dotenv portion. There was some confusion with the name USER, which my code read as the local username, not the DB login
# Prompt below:
'''
hey, I keep getting this error after changing my files to use a .env:

127.0.0.1 - - [28/Jul/2026 18:48:14] "GET /Avidex HTTP/1.1" 200 -
127.0.0.1 - - [28/Jul/2026 18:48:14] "GET /static/style.css HTTP/1.1" 304 -
Error executing queries: (1045, "Access denied for user 'baruaha'@'classwork.engr.oregonstate.edu' (using password: YES)")
127.0.0.1 - - [28/Jul/2026 18:48:19] "GET 

which doesn't make sense to me since I should be trying to connect tot he server classmysql.engr.oregonstate.edu, not classwork. and I checked my .env, and it does say classmysql.engr.oregonstate.edu...i'm so confused to why I'm getting this error
'''

# Created by AI
# force loading .env from the project root and override any shell values
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

# database credentials
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

# Created by AI
missing = [name for name, value in [("DB_HOST", host), ("DB_USER", user), ("DB_PASSWORD", password), ("DB_NAME", database)] if not value]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

# Function used to connect to the database
def connectDB(host=host, user=user, password=password, database=database):
    '''
    connects to a database and returns a database object
    '''
    ## Used AI to add charset connections
    dbConnection = MySQLdb.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4',
        use_unicode=True
    )
    return dbConnection

def query(dbConnection = None, query = None, query_params = ()):
    '''
    executes a given SQL query on the given db connection and returns a Cursor object...
    dbConnection: a MySQLdb connection object created by connectDB()
    query: string containing SQL query
    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually access the results.
    '''

    if dbConnection is None:
        print("No connection to the DB found.")
        return None

    if query is None or len(query.strip()) == 0:
        print("Query is empty! Pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params))

    # Creating a cursor to execute query because supposedly they optimize execution by retaining a reference, according to POP02
    cursor = dbConnection.cursor(MySQLdb.cursors.DictCursor)

    # Sanitizing the query before executing it.
    cursor.execute(query, query_params)

    # Comminting changes to the db
    dbConnection.commit()

    # Using AI here to fix an issue with POINT values showing up as (b") instead of NULL
    # Convert bytes to strings in results
    class DecodingCursor:
        def __init__(self, cursor):
            self.cursor = cursor
        
        def fetchall(self):
            rows = self.cursor.fetchall()
            return [{k: v.decode('utf-8') if isinstance(v, bytes) else v 
                     for k, v in row.items()} for row in rows]
        
        def fetchone(self):
            row = self.cursor.fetchone()
            return {k: v.decode('utf-8') if isinstance(v, bytes) else v 
                    for k, v in row.items()} if row else None

    return cursor
