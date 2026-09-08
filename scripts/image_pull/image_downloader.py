import database.db_connector as db
import csv
import os
import requests
from pathlib import Path
import time
import hashlib

PARENT_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = Path(PARENT_DIR / "data")

CONTACT_EMAIL = os.getenv("WIKIMEDIA_CONTACT_EMAIL")
HEADERS = {"User-Agent": f"Avidex/0.92 (contact: {CONTACT_EMAIL})"}

DOWNLOAD_MANIFEST_PATH = DATA_DIR / "download_manifest.csv"





def get_downloaded():
    done = []

    file_exists = Path(DOWNLOAD_MANIFEST_PATH).exists()

    if not file_exists:
        return None
    
    with open(DOWNLOAD_MANIFEST_PATH, "r", encoding="utf-8", newline="") as manifest:
        reader = csv.reader(manifest)
        next(reader, None)

        for row in reader:
            folderName = row[0]
            hash = row[1]
            url = row[2]

            done.append([folderName,hash,url])

    return done





def get_birds_from_db():
    dbConnection = db.connectDB()
    
    query = """
        SELECT Birds.birdID, Birds.commonName, BirdPhotos.photographUrl FROM Birds
        LEFT JOIN BirdPhotos ON BirdPhotos.birdID = Birds.birdID;
    """

    rows = db.query(dbConnection, query).fetchall()

    # A dictionary of each bird's ID and their links 
    birds = {}

    # setting the birds dictionary
    # {
    #     7: ["url1", "url2"],
    #     8: ["url3", "url4"],
    # }
    for row in rows:
        birds.setdefault(row["commonName"],[]).append(row["photographUrl"])

    dbConnection.close()

    return birds



def save_in_specific_folders():
    birds = get_birds_from_db()

    sleeptime = 1

    total_urls = sum(len(urls) for urls in birds.values())
    overall_url_count = 0

    already_downloaded = get_downloaded()
    # Before your loop
    if already_downloaded:
        already_downloaded_urls = {item[2] for item in already_downloaded}  # Gets 3rd element
    

    file_exists = Path(DOWNLOAD_MANIFEST_PATH).exists()


    with Path(DOWNLOAD_MANIFEST_PATH).open("a", encoding="utf-8", newline="") as downloaded_csv:
        writer = csv.writer(downloaded_csv)

        if not file_exists:
            writer.writerow(["Directory Name", "Hash", "Url"])
        

        for bird_index, (commonName, urls) in enumerate(birds.items(), start=1):

            commonName = commonName.replace(" ", "_")

            folder_name =  f"{commonName}_photos"

            # Creating the directory where the files should be saved
            folder_path = DATA_DIR / f"downloaded_bird_photos/{folder_name}"

            Path(folder_path).mkdir(exist_ok=True, parents=True)

            Path(folder_path / f"{commonName}_urls.txt").write_text(f"{commonName}:{urls}")

            # Getting the content_hashes of the images
            for url_index, url in enumerate(urls, start=1):
                time.sleep(sleeptime)
                overall_url_count += 1  

                if already_downloaded:
                    if url in already_downloaded_urls:
                        print(f"Url {url_index} for bird {bird_index} already downloaded. Skipping...")
                        print(f"{overall_url_count} urls saved")
                        print()
                        continue

                try:
                    response = requests.get(url, timeout=15,headers=HEADERS)
                    response.raise_for_status()
                    image_bytes = response.content
                    content_hash = hashlib.md5(image_bytes).hexdigest()
                except Exception as e:
                    print(f"Image Byte save failed for {url} with exception {e}")
                    continue
                

                Path(folder_path / f"{content_hash}.jpg").write_bytes(image_bytes)

                writer.writerow([folder_path, content_hash, url])
                

                print(f"Image Byte {url_index} of {len(urls)} urls for bird {bird_index} of {len(birds.items())} birds")
                print(f"{overall_url_count} urls saved out of {total_urls}")
                print()




save_in_specific_folders()