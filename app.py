#################################
########### SETUP ###########
#################################

from flask import Flask, render_template, request, redirect
import database.db_connector as db

PORT = 8000

app = Flask(__name__)

############################################
########### ROUTE HANDLERSS ###########
############################################
# READ ROUTES
# Homepage
@app.route("/Avidex", methods = ["GET"])
def home():
    try:
        return render_template("home.j2")

    except Exception as e:
        print(f"Error rendering page: {e}")
        return "An error occurred while rendering the page.", 500

# Bird Page
@app.route("/Avidex/birds", methods = ["GET"])
def avidex_birds():
    try:
        dbConnection = db.connectDB() 

        # Creating and executing our queries
        query1 = "SELECT * FROM Birds ORDER BY Birds.birdID ASC;"
        query2 = "SELECT * FROM Rarities"

        birds = db.query(dbConnection, query1).fetchall()
        rarities = db.query(dbConnection, query2).fetchall()

        # Render the page and pass both the birds and rarities data to the template.
        return render_template(
            "avidex-birds.j2", birds = birds, rarities = rarities
        )

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries.", 500

    finally:
        # closing the DB connection, if it exists
        if "dbConnection" in locals() and dbConnection: dbConnection.close()

# Rarity Page
@app.route("/Avidex/rarities", methods = ["GET"])
def avidex_rarities():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT * FROM Rarities;"

        rarities = db.query(dbConnection, query1).fetchall()

        return render_template(
            "rarities.j2", rarities = rarities
        )
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

#################################
########### LISTENER ###########
#################################
if __name__ == "__main__":
    app.run(
        port = PORT, debug = True
    )