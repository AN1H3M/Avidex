from pathlib import Path
from PIL import Image

PARENT_DIR = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = PARENT_DIR / "data/downloaded_bird_photos"

def check_image(image_path):
    try:
        Image.open(image_path).verify()
        return True
    except Exception:
        return False

