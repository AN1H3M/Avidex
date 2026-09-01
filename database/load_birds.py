import csv, os, sys, MySQLdb

from dotenv import load_dotenv

from scripts.scraper.bird_scraper import *
from pathlib import Path


# Gets the project directory: Avidex/
ROOT_DIR = Path(__file__).resolve().parent.parent

# Loads Avidex/.env file in the root directory
load_dotenv(ROOT_DIR / ".env",override=True)


# Use the CSV path supplied in the command.
CSV_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else ROOT_DIR / "data" / "processed_birds.csv"
)

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_NAME = os.getenv("DB_NAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Removes extra whitespace and turns empty values into None
def clean(value):
    if value is None:
        return None

    value = value.strip()

    return value if value else None

# Read bird records from the CSV file and insert them into MySQL
def load_birds():

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

    # Open the CSV file.
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as csv_file:

        # DictReader uses the first CSV row as column names.
        reader = csv.DictReader(csv_file)

        # These columns must exist in the CSV file.
        required_columns = {
            "rarityID",
            "commonName",
            "species",
            "wingspan",
            "size",
            "identifyingMarks",
            "range",
            "description",
            "matingSeason"
        }

        # Get the columns found in the CSV
        csv_columns = set(reader.fieldnames or [])

        # Find required columns that are missing
        missing_columns = required_columns - csv_columns
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))

            raise ValueError(
                f"CSV is missing required columns: {missing}"
            )

        # Process every bird row
        for line_number, row in enumerate(reader, start=2):

            # Clean the required fields
            rarity = clean(row.get("rarityID"))
            common_name = clean(row.get("commonName"))
            species = clean(row.get("species"))
            wingspan = clean(row.get("wingspan"))
            size = clean(row.get("size"))
            identifyingMarks = clean(row.get("identifyingMarks"))
            range = clean(row.get("range"))
            description = clean(row.get("description"))
            matingSeason = clean(row.get("matingSeason"))

            
            # add the row in the same order as the SQL statement
            rows.append(
                (
                    rarity,
                    common_name,
                    species,
                    wingspan,
                    size,
                    identifyingMarks,
                    range,
                    description,
                    matingSeason
                )
            )

    # Stop if no valid rows were found
    if not rows:
        print("No valid birds were found.")
        return

    # Open a connection to MySQL
    connection = MySQLdb.connect(
        host = DB_HOST,
        user = DB_USER,
        passwd = DB_PASSWORD,
        db = DB_NAME,
        charset = "utf8mb4",
    )

    try:
        # Create a cursor for executing SQL statements.
        cursor = connection.cursor()

        # Call the pl_add_bird stored procedure once per bird instead of a
        # raw INSERT. pl_add_bird's parameter order (rarityID, commonName,
        # species, wingspan, size, identifyingMarks, range, description,
        # matingSeason) already matches the order `rows` tuples were built
        # in above, so no reordering is needed here.
        #
        # callproc() (in a loop) is used instead of executemany() because
        # pl_add_bird has a COMMIT inside it -- executemany() assumes a
        # single simple statement repeated across rows, and doesn't play
        # well with stored procedures that commit internally.
        loaded_count = 0
        failed_rows = []

        for row in rows:
            try:
                cursor.callproc("pl_add_bird", row)
                loaded_count += 1
            except Exception as row_error:
                # Keep going instead of aborting the whole load on one bad
                # row (e.g. a duplicate species, which pl_add_bird doesn't
                # currently guard against the way pl_add_birder_reward does)
                print(f"Failed to load bird '{row[1]}': {row_error}")
                failed_rows.append((row[1], str(row_error)))

        # Permanently save the changes
        connection.commit()

        print(f"Loaded {loaded_count} of {len(rows)} bird records.")
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


# Run the loader only when this file is executed directly.
if __name__ == "__main__":
    try:
        load_birds()

    except Exception:
        raise
    