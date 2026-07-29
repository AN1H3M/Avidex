import os
from pathlib import Path
from dotenv import load_dotenv
import MySQLdb

# force loading .env from the project root and override any shell values
dotenv_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

# database credentials
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")

missing = [name for name, value in [("DB_HOST", host), ("DB_USER", user), ("DB_PASSWORD", password), ("DB_NAME", database)] if not value]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

# Function used to connect to the database
def connectDB(host=host, user=user, password=password, database=database):
    '''
    connects to a database and returns a database object
    '''
    dbConnection = MySQLdb.connect(host=host, user=user, password=password, database=database)
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
