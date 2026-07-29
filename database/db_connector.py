import os
from dotenv import load_dotenv
import MySQLdb

load_dotenv()

# database credentials
host = os.getenv("HOST")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
db = os.getenv("DATABASE")


# Function used to connect to the database
def connectDB(host = host, user = user, pasword = password, db = db):
    '''
    connects to a database and returns a database object
    '''
    dbConnection = MySQLdb.connect(host, user, password, db)
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

    return cursor


   