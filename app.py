#################################
########### SETUP ###########
#################################

from pathlib import Path
from flask import Flask, render_template, request, redirect
import database.db_connector as db

PORT = 8001

app = Flask(__name__)

## defines the project root
# PROJECT_ROOT = Path(__file__).resolve().parent
## defining the path to the DDL.sql
# DDL_PATH = PROJECT_ROOT / "DDL.sql"
#############################################
## HELPER FUNCTION FOR READING SQL FILES
#############################################
## AI was used in this portion: Figuring out how to read the DDL.sql file as well as execute the SQL lines
# def execute_sql_script(db_connection,script_path):
#    statements = []
#    current_statement = []
#
#     # Reading the SQL file line by line
#     for line in script_path.read_text(encoding = "utf-8").splitlines():
#         cleaned = line.strip()
# 
#        # skipping blank and commented lines
#         if not cleaned or cleaned.startswith("--"):
#              continue
#        
#          # adding the current line to a variable
#          current_statement.append(line)
#  
#        # if the current line is a finished statement, add it to the statements list
#        if ";" in line:
#            statement = "\n".join(current_statement).strip()
#            if statement:
#                statements.append(statement)
#            current_statement = []
#
#    # handling if the final statement of the file didnt end with ;
#    if current_statement:
#        statement = "\n".join(current_statement)
#        if statement:
#            statements.append(statement)
#
#    # actually executing each line
#    for statement in statements:
#        if statement:
#            db.query(db_connection,statement)



############################################
########### ROUTE HANDLERSS ###########
############################################

############################################
# READ ROUTES
############################################

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

# Birders Page
@app.route("/Avidex/birders", methods = ["GET"])
def avidex_birders():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT * FROM Birders;"

        birders = db.query(dbConnection, query1).fetchall()

        return render_template(
            "birders.j2", birders = birders
        )

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Nests Page
@app.route("/Avidex/nests", methods = ["GET"])
def avidex_nests():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT * FROM Nests;"

        nests = db.query(dbConnection, query1).fetchall()

        return render_template(
            "nests.j2", nests = nests
        )


    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Rewards Page
@app.route("/Avidex/rewards", methods = ["GET"])
def avidex_rewards():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT * FROM Rewards;"

        rewards = db.query(dbConnection, query1).fetchall()

        return render_template(
            "rewards.j2", rewards = rewards
        )


    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Sightings Page
@app.route("/Avidex/sightings", methods = ["GET"])
def avidex_sightings():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT Sightings.sightingID, Birders.birderName, Birds.commonName, Sightings.birdCount, Sightings.gpsLocation, Sightings.time FROM Sightings\
                LEFT JOIN Birders ON Birders.birderID = Sightings.birderID\
                LEFT JOIN Birds ON Birds.birdID = Sightings.birdID;"
        query2 = "SELECT * FROM Birders;"
        query3 = "SELECT * FROM Birds;"

        sightings = db.query(dbConnection, query1).fetchall()
        birders = db.query(dbConnection, query2).fetchall()
        birds = db.query(dbConnection, query3).fetchall()

        return render_template(
            "sightings.j2", sightings = sightings, birders = birders, birds = birds
        )


    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# BirdersRewards Page
@app.route("/Avidex/birders-rewards", methods = ["GET"])
def avidex_birders_rewards():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT Rewards.name, Birders.birderName FROM BirdersRewards\
                LEFT JOIN Birders ON Birders.birderID = BirdersRewards.birderID\
                LEFT JOIN Rewards ON Rewards.rewardID = BirdersRewards.rewardID;"
        query2 = "SELECT * FROM Birders;"
        query3 = "SELECT * FROM Rewards;"

        birdersrewards = db.query(dbConnection, query1).fetchall()
        birders = db.query(dbConnection, query2).fetchall()
        rewards = db.query(dbConnection, query3).fetchall()

        return render_template(
            "birders-rewards.j2", birdersrewards = birdersrewards, birders = birders, rewards = rewards
        )
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# BirdsList Page
@app.route("/Avidex/birds-list", methods = ["GET"])
def avidex_birds_list():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT Birders.birderName, Birds.commonName, BirdsList.count FROM BirdsList\
                LEFT JOIN Birders ON Birders.birderID = BirdsList.birderID\
                LEFT JOIN Birds on Birds.birdID = BirdsList.birdID;"
        query2 = "SELECT * FROM Birders;"
        query3 = "SELECT * FROM Birds;"

        birdslists = db.query(dbConnection, query1).fetchall()
        birders = db.query(dbConnection, query2).fetchall()
        birds = db.query(dbConnection, query3).fetchall()

        return render_template(
            "birds-list.j2", birdslists = birdslists, birders = birders, birds = birds
        )
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# BirdsNests Page
@ app.route("/Avidex/birds-nests", methods = ["GET"])
def avidex_birds_nests():
    try:
        dbConnection = db.connectDB()

        query1 = "SELECT Birds.commonName, BirdsNests.nestID, Nests.type, Nests.location FROM BirdsNests\
                LEFT JOIN Birds ON Birds.birdID = BirdsNests.birdID\
                LEFT JOIN Nests ON Nests.nestID = BirdsNests.nestID;"
        query2 = "SELECT * FROM Birds;"
        query3 = "SELECT * FROM Nests;"

        birdsnests = db.query(dbConnection, query1).fetchall()
        birds = db.query(dbConnection, query2).fetchall()
        nests = db.query(dbConnection, query3).fetchall()

        return render_template(
            "birds-nests.j2", birdsnests = birdsnests, birds = birds, nests = nests
        )

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

############################################
# POST ROUTES
############################################

# Reset Button
@app.route("/Avidex/reset", methods = ["POST"])
def reset_db_route():
    try:
        dbConnection = db.connectDB()
        db.query(dbConnection, "CALL pl_reset_avidex();")

        next_url = request.form.get("next") or request.referrer or "/Avidex"
        
        return redirect(next_url)
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

#################################
# ADD OBJECT
#################################

# Add a Birder
@app.route("/Avidex/birders", methods = ["POST"])
def add_birder():
    try:
        dbConnection = db.connectDB()

        birder_name = request.form.get("create_birder_name")
        birder_points = int(request.form.get("create_birder_points"))

        db.query(dbConnection, "CALL pl_add_birder(%s,%s);",(birder_name, birder_points))
        
        return redirect("/Avidex/birders")

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Bird
@app.route("/Avidex/birds", methods = ["POST"])
def add_bird():
    try:
        dbConnection = db.connectDB()

        bird_rarity = request.form.get("create_bird_rarity")
        bird_commonName = request.form.get("create_bird_common_name")
        bird_species = request.form.get("create_bird_species")
        bird_callUrl = request.form.get("create_bird_call_url")
        bird_wingspan = request.form.get("create_bird_wingspan")
        bird_size = request.form.get("create_bird_size")
        bird_identifyingMarks = request.form.get("create_bird_identifying_marks")
        bird_range = request.form.get("create_bird_range")
        bird_description = request.form.get("create_bird_description")
        bird_photographUrl = request.form.get("create_bird_photograph_url")
        bird_matingSeason = request.form.get("create_bird_mating_season")

        db.query(dbConnection, "CALL pl_add_bird(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (
            bird_rarity,
            bird_commonName,
            bird_species,
            bird_callUrl,
            bird_wingspan,
            bird_size,
            bird_identifyingMarks,
            bird_range,
            bird_description,
            bird_photographUrl,
            bird_matingSeason
        ))

        return redirect("/Avidex/birds")
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Reward
@app.route("/Avidex/rewards", methods = ["POST"])
def add_reward():
    try:
        dbConnection = db.connectDB()

        reward_name = request.form.get("create_reward_name")
        reward_description = request.form.get("create_reward_description")
        reward_threshold = int(request.form.get("create_reward_threshold"))

        db.query(dbConnection, "CALL pl_add_reward(%s,%s,%s)",(reward_name,reward_description,reward_threshold))

        return redirect("/Avidex/rewards")

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Birder's Reward
@app.route("/Avidex/birders-rewards", methods = ["POST"])
def add_birders_reward():
    try:
        dbConnection = db.connectDB()

        rewardID = request.form.get("create_birderreward_reward_name")
        birderID = request.form.get("create_birderreward_birder_name")

        db.query(dbConnection, "CALL pl_add_birdersreward(%s,%s)",(rewardID, birderID))

        return redirect("/Avidex/birders-rewards")

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Bird's List
@app.route("/Avidex/birds-list", methods = ["POST"])
def  add_birds_list():
    try:
        dbConnection = db.connectDB()

        count = request.form.get("create_birdlist_count")
        birdID = request.form.get("create_birdlist_bird")
        birderID = request.form.get("create_birdlist_birder")

        db.query(dbConnection, "CALL pl_add_birdslist(%s,%s,%s)",(count, birdID, birderID))
        return redirect("/Avidex/birds-list")

        print("Added birdslist")

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Bird's Nest
@app.route("/Avidex/birds-nests", methods = ["POST"])
def add_birds_nest():
    try:
        dbConnection = db.connectDB()

        birdID = request.form.get("create_birdnest_bird")
        nestID = request.form.get("create_birdnest_nest")

        db.query(dbConnection, "CALL pl_add_birdsnest(%s,%s)",(birdID,nestID))

        return redirect("/Avidex/birds-nest")

    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()

# Add a Nest
@app.route("/Avidex/nests", methods = ["POST"])
def add_nest():
    try:
        dbConnection = db.connectDB()

        nest_type = request.form.get("create_nest_type")
        nest_location = request.form.get("create_nest_location")

        db.query(dbConnection, "CALL pl_add_nest(%s,%s)",(nest_type, nest_location))

        return redirect("/Avidex/nests")
    
    except Exception as e:
        print(f"Error executing queries: {e}")
        return "An error occurred while executing the db queries", 500
    
    finally:
        if dbConnection in locals() and dbConnection: dbConnection.close()
 
# Add a Rarity
@app.route("/Avidex/rarities", methods = ["POST"])
def add_rarity():
    try:
        dbConnection = db.connectDB()

        rarity = request.form.get("create_rarity")

        db.query(dbConnection, "CALL pl_add_rarity(%s)",(rarity))

        return redirect("/Avidex/rarities")
    
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