from pathlib import Path
import pandas as pd
import csv

PARENT_DIR = Path(__file__).resolve().parent.parent.parent

IMAGE_DIR = Path(PARENT_DIR / "data/downloaded_bird_photos")

dataframe = {}
names = []
lengths = []

for bird_dir in IMAGE_DIR.iterdir():
    if bird_dir.is_dir():
        bird_name = bird_dir.name
        bird_images = list(bird_dir.glob("*.jpg"))
        names.append(bird_name)
        lengths.append(len(bird_images))
dataframe["Bird Name"] = names
dataframe["Image Count"] = lengths

downloaded_folder = pd.DataFrame(dataframe)

print("Downloaded Empty Birds")
empty_birds = downloaded_folder[downloaded_folder["Image Count"] == 0]
print(empty_birds)

print()
print("Birds with Less than 2")
thin_birds = downloaded_folder[downloaded_folder["Image Count"] <= 2]
print("Downloaded thin birds")
print(thin_birds)
print()
def csv_to__thin_df(csvPath):
    bird_urls_dict = {}
    with Path(csvPath).open("r", newline="", encoding="utf-8") as bird_urls:
        reader = csv.reader(bird_urls)
        next(reader, None)

        urls = {}
        for row in reader:
            name = row[0]
            url = row[2]

            urls.setdefault(name, []).append(url)


    urls_dataframe = {}
    names = []
    lengths = []
    for key in urls.keys():
        names.append(key)
        lengths.append(len(urls[key]))
    urls_dataframe["Bird Names"] = names
    urls_dataframe["Image Count"] = lengths

    bird_urls_dataframe = pd.DataFrame(urls_dataframe)

    thin_urls = bird_urls_dataframe[bird_urls_dataframe["Image Count"] <= 2]

    print(thin_urls)

csv_to__thin_df(PARENT_DIR / "data/bird_urls.csv")
print()
csv_to__thin_df(PARENT_DIR / "data/download_manifest.csv")