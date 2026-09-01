from database.load_birds import *

# Use the CSV path supplied in the command.
CSV_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else ROOT_DIR / "data" / "bird_urls.csv"
)

def load_photos():
    # Make sure the required connection settings exist.
    required_settings = {
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD,
        "DB_NAME": DB_NAME,
    }

    missing_settings = [
        name for name, value in required_settings.items()
        if not value
    ]

    if missing_settings:
        raise ValueError(
            "Missing Database Credentials: " 
            + ", ".join(missing_settings) + ". Check your .env file"
        )

    # store valid CSV rows before inserting them into MySQL
    rows = []

    photo_labels = []

    # Open the CSV file.
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as csv_file:

        # DictReader uses the first CSV row as column names.
        reader = csv.DictReader(csv_file)

        # DictReader uses the first CSV row as column names.
        reader = csv.DictReader(csv_file)

        # These columns must exist in the CSV file.
        required_columns = {"Common Name", "Species", "Url"}

        # Get the columns found in the CSV
        csv_columns = set(reader.fieldnames or [])

        # Find required columns that are missing
        missing_columns = required_columns - csv_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))

            raise ValueError(
                f"CSV is missing required columns: {missing}"
            )

         # Open a connection to MySQL
        connection = MySQLdb.connect(
            host = DB_HOST,
            user = DB_USER,
            passwd = DB_PASSWORD,
            db = DB_NAME,
            charset = "utf8mb4",
        )

    

        # Process every photo row
        for line_number, row in enumerate(reader, start=2):
            # Clean the required fields
            common_name = clean(row.get("Common Name"))
            species = clean(row.get("Species"))
            url = clean(row.get("Url"))
            license = clean(row.get("License"))
            artist = clean(row.get("Artist"))

            try:
                cursor = connection.cursor()
                cursor.execute(
                    "SELECT birdID FROM Birds WHERE Birds.commonName = %s AND Birds.species = %s;",
                    (common_name, species)
                )
                result = cursor.fetchone()

                # fetchone() returns a tuple like (5,) on a match, or None
                # if nothing matched -- a bare species mismatch (e.g. this
                # bird's species field in the DB still has leftover
                # hallucinated/mutated text from before) means result is
                # None here, and result[0] would throw
                if result is None:
                    print(f"No matching bird found for '{common_name}' ({species}) on line {line_number}, skipping.")
                    continue

                birdID = result[0]

            
            except Exception as e:
                print(f"birdID fetch failed on line {line_number}. Error: {e}")
                continue
    
            # add the row in the same order as the SQL statement
            rows.append(
                (
                    birdID,
                    url,
                    license,
                    artist
                )
            )

            photo_labels.append(common_name)

            cursor.close()

        # Stop if no valid rows were found
        if not rows:
            print("No valid photos were found.")
            return
    
        try:
            # Create a cursor for executing SQL statements.
            cursor = connection.cursor()
    
            # Call the pl_add_bird_photo stored procedure once per bird photo
            # instead of a full raw INSERT. 
            loaded_count = 0
            failed_rows = []
    
            for index, row in enumerate(rows):
                try:
                    cursor.callproc("pl_add_bird_photo", row)
                    loaded_count += 1
                except Exception as row_error:
                    # Keep going instead of aborting the whole load on one bad
                    # row
                    print(f"Failed to load bird photo '{photo_labels[index]}': {row_error}")
                    failed_rows.append((photo_labels[index], str(row_error)))
    
            # Permanently save the changes
            connection.commit()
    
            print(f"Loaded {loaded_count} of {len(rows)} photo records.")
            if failed_rows:
                print("Failed rows:")
                for name, error in failed_rows:
                    print(f"  - {name}: {error}")
    
        except Exception:
            # Undo all changes if something fails
            connection.rollback()
    
            # Display the error to the terminal
            raise
    
        finally:
            # Close the cursor
            cursor.close()
    
            # Close the database connection.
            connection.close()
    

load_photos()