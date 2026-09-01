import os
from pathlib import Path
from dotenv import load_dotenv
import typesense
import database.db_connector as db

ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

client = typesense.Client({
    "nodes": [{
        "host": os.getenv("TYPESENSE_HOST"),
        "port": os.getenv("TYPESENSE_PORT"),
        "protocol": "http",
    }],
    "api_key": os.getenv("TYPESENSE_ADMIN_API_KEY"),
    "connection_timeout_seconds": 5,
})

# Schema for the "birds" collection. commonName/species/description are
# what query_by searches against (see typesense.js on the frontend);
# photos is stored but not searched, so the frontend can render a card
# straight from a search hit without a second fetch back to Flask.
SCHEMA = {
    "name": "birds",
    "fields": [
        {"name": "birdID", "type": "int32"},
        {"name": "commonName", "type": "string"},
        {"name": "species", "type": "string"},
        {"name": "description", "type": "string"},
        {"name": "photos", "type": "string[]", "optional": True, "index": False},
    ],
}

def index_birds():
    # Drop and recreate the collection so this script is safe to
    # re-run any time the DB changes -- avoids stale/duplicate docs
    try:
        client.collections["birds"].delete()
    except typesense.exceptions.ObjectNotFound:
        pass

    client.collections.create(SCHEMA)

    dbConnection = db.connectDB()

    query1 = """
        SELECT Birds.birdID, Birds.commonName, Birds.species, Birds.description,
               GROUP_CONCAT(BirdPhotos.photographUrl SEPARATOR '||') AS photoUrls
        FROM Birds
        LEFT JOIN BirdPhotos ON BirdPhotos.birdID = Birds.birdID
        GROUP BY Birds.birdID;
    """

    birds = db.query(dbConnection, query1).fetchall()
    dbConnection.close()

    documents = []
    for bird in birds:
        raw_urls = bird.pop("photoUrls")
        bird["photos"] = raw_urls.split("||") if raw_urls else []
        # Typesense requires a string "id" field per document
        bird["id"] = str(bird["birdID"])
        documents.append(bird)

    # import_() batches all documents in one call instead of one HTTP
    # request per bird -- much faster for ~1650 rows
    results = client.collections["birds"].documents.import_(documents, {"action": "upsert"})

    failed = [r for r in results if not r.get("success")]
    print(f"Indexed {len(documents) - len(failed)} of {len(documents)} birds.")
    if failed:
        print("Failed documents:", failed[:5])

if __name__ == "__main__":
    index_birds()