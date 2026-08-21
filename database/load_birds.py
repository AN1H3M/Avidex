import csv, os, sys, MySQLdb

from dotenv import load_dotenv

from scraper.bird_scraper import *
from pathlib import Path


# Gets the project directory: Avidex/
ROOT_DIR = Path(__file__).resolve().parent.parent

# Loads Avidex/.env file in the root directory
load_dotenv(ROOT_DIR / ".env")

# Use the CSV path supplied in the command.
CSV_PATH = (
    Path(sys.argv[1])
    if len(sys.argv) > 1
    else ROOT_DIR / "data" / "NACC_list_species.csv"
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
            "common_name",
            "species"
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
            common_name = clean(row.get("common_name"))
            species = clean(row.get("species"))

            # Skip rows that do not have both
            if not common_name or not species:
                print(
                    f"Skipping line {line_number}: "
                    "missing common_name or scientific_name"
                )
                continue

            # add the row in the same order as the SQL statement
            rows.append(
                (
                    common_name,
                    species
                )
            )

    # Stop if no valid rows were found
    if not rows:
        print("No valid birds were found.")
        return

    return rows

"""
# Open a connection to MySQL
    connection = MySQLdb.connect(
        host = DB_HOST,
        user = DB_NAME,
        passwd = DB_PASSWORD,
        db = DB_NAME,
        charset = "utf8mb4",
    )

    try:
        # Create a cursor for executing SQL statements.
        cursor = connection.cursor()

        # Insert every bird into the birds table.
        #
        # %s values are safely replaced by MySQLdb.
        #
        # ON DUPLICATE KEY UPDATE prevents duplicate birds if
        # scientific_name has a UNIQUE constraint.
        insert_sql =
            INSERT INTO birds (
                common_name,
                scientific_name,
                family,
                region,
                description,
                image_url
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                common_name = VALUES(common_name),
                family = VALUES(family),
                region = VALUES(region),
                description = VALUES(description),
                image_url = VALUES(image_url)

        # Insert each row into MySQL
        cursor.executemany(insert_sql, rows)

        # Permanently save the changes
        connection.commit()

        print(f"Loaded or updated {cursor.rowcount} bird records.")

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
"""

# Run the loader only when this file is executed directly.
if __name__ == "__main__":
    rows = load_birds()

    try:
        if not rows:
            raise SystemExit("No bird rows were loaded.")

        scraped_birds, failed_birds = search_for_birds(rows)

        print(
            f"Successfully scraped {len(scraped_birds)} birds."
        )
        print(
            f"Failed to scrape {len(failed_birds)} birds."
        )

        completion_message = (
            "Bird scraper finished scraping!\n"
            f"Successfully scraped: {len(scraped_birds)} birds.\n"
            f"Failed to scrape: {len(failed_birds)} birds."
        )

        try:
            send_discord_message(
                completion_message,
                username="Bird Scraper",
            )
        except Exception as notification_error:
            print(
                "Could not send completion Discord message:",
                notification_error,
            )


    except Exception:

        failure_message = (
            "Bird scraper failed.\n"
            f"Error: {type(error).__name__}: {error}\n"
            f"Successful so far: {len(scraped_birds)} birds.\n"
            f"Failed so far: {len(failed_birds)} birds."
        )

        try:
            send_discord_message(
                failure_message,
                username="Bird Scraper",
            )
        except Exception as notification_error:
            print(
                "Could not send failure Discord message:",
                notification_error,
            )
        
        raise