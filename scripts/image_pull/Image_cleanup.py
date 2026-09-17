from pathlib import Path
from PIL import Image
import csv
import warnings

PARENT_DIR = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = PARENT_DIR / "data/downloaded_bird_photos"
MANIFEST_CSV = PARENT_DIR / "data/download_manifest.csv"

def check_image(image_path):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            Image.open(image_path).verify()
            return True
        except Exception:
            return False

def get_working_hashes(image_dir_path):
    bird_dirs = sorted(d for d in image_dir_path.iterdir() if d.is_dir())

    hashes_to_keep = []
    for bird_dir in bird_dirs:
        images = bird_dir.glob('*.jpg')
        for image in images:
            if check_image(image):
                hashes_to_keep.append(image.name.split(".")[0])

    return hashes_to_keep

def remove_bad_images_from_csv(csv_path, image_dir_path):
    hashes = set(get_working_hashes(image_dir_path))  # set() for fast lookup, given how many rows this could be
    with open(csv_path, "r", encoding="utf-8", newline="") as bird_csv:
        reader = csv.DictReader(bird_csv)
        fieldnames = reader.fieldnames
        rows_to_keep = [row for row in reader if row["Hash"] in hashes]

    

    with open(csv_path, "w", encoding="utf-8", newline="") as out_csv:
        writer = csv.DictWriter(out_csv, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_keep)



def check_for_dupes(duped_csv):
    with open(duped_csv, "r", encoding="utf-8", newline="") as duped:
        reader = csv.DictReader(duped)

        hashes = [row["Hash"] for row in reader]

        seen = []
        duplicates = {}
        for i, hash in enumerate(hashes):
            if hash not in seen:
                seen.append(hash)
            else:
                duplicates.setdefault(hash, []).append(i)

        return duplicates

def remove_duplicates_from_csv(duped_path):
    duplicates = check_for_dupes(duped_path)
    indices = []
    keys = duplicates.keys()
    for key in keys:
        indices.append(duplicates.get(key)[0])

    with open(duped_path, "r", encoding="utf-8", newline="") as duped:
        reader = csv.DictReader(duped)
        fieldnames = reader.fieldnames
        rows = list(enumerate(reader))

    to_write = []
    for index, row in rows:
        if index not in indices:
            to_write.append(row)

    with open(duped_path, "w", encoding="utf-8", newline="") as unduped:
        writer = csv.DictWriter(unduped, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(to_write)





def uninstall_garbage_bytes(image_dir_path):
    hashes_to_keep = get_working_hashes(image_dir_path)

    bird_dirs = sorted(d for d in image_dir_path.iterdir() if d.is_dir())

    for bird_dir in bird_dirs:
        images = bird_dir.glob('*.jpg')
        for image in images:
            hash = image.name.split(".")[0]
            if hash not in hashes_to_keep:
                image.unlink()


# Not needed since it duplicate names aren't allowed on mac, and the filenames were all the hashes.
def uninstall_duplicate_bytes(image_dir_path):
    bird_dirs = sorted(d for d in image_dir_path.iterdir() if d.is_dir())

    for bird_dir in bird_dirs:
        images = bird_dir.glob('*.jpg')
        seen = []
        for image in images:
            hash = image.name.split('.')[0]
            if hash in seen:
                image.unlink()
            else:
                seen.append(hash)

def image_number(image_dir_path):
    images = list(image_dir_path.glob('**/*.jpg'))
    return len(images)

def clean_data(images_path, csv_path):
    og_image_num = image_number(images_path)
    print(f"Original file count: {og_image_num}")
    remove_bad_images_from_csv(csv_path, images_path)
    print("Removed garbage images from csv")
    remove_duplicates_from_csv(csv_path)
    print("Removed duplicates from csv")
    uninstall_garbage_bytes(images_path)
    print("Uninstalled garbage images")
    uninstall_duplicate_bytes(images_path)
    print("Uninstalled duplicate images")
    new_image_num = image_number(images_path)
    print(f"New file count: {new_image_num}")
    print(f"{og_image_num - new_image_num} duplicate/garbage bytes deleted")

clean_data(IMAGE_DIR,MANIFEST_CSV)