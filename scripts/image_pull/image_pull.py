import os
import requests
from pathlib import Path
from dotenv import load_dotenv
import csv

# Loading .env
ROOT_DIR = Path(__file__).resolve().parents[2]
load_dotenv(ROOT_DIR / ".env")

# Wikimedia asks that every request identify the calling app + a contact
# method. This isn't an API key -- it's a courtesy header they can use to
# reach you if your traffic causes problems, and they may rate-limit or
# block requests that don't include one.
CONTACT_EMAIL = os.getenv("WIKIMEDIA_CONTACT_EMAIL")

if not CONTACT_EMAIL:
    raise RuntimeError(
        "WIKIMEDIA_CONTACT_EMAIL is missing from the .env file. "
        "Wikimedia's API etiquette requires a contact identifier in the User-Agent."
    )

HEADERS = {
    "User-Agent": f"Avidex/0.92 (contact: {CONTACT_EMAIL})"
}

COMMONS_API_URL = "https://commons.wikimedia.org/w/api.php"

def _search_commons_images(query, limit=5):
    """
    Runs a single Commons API search and returns the raw list of image
    results (or an empty list if nothing came back). Kept separate from
    get_bird_photo_url() so the two-attempt (scientific name -> common
    name) retry logic below doesn't have to duplicate the request code.
    """
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,          # File: namespace -- restricts results to actual media files
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",  # pulls the direct file URL and license info in the same call
        "format": "json",
    }

    response = requests.get(COMMONS_API_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()

    data = response.json()

    # A search with zero hits has no "query" key at all, not an empty one --
    # this check has to come before we try to read data["query"]["pages"]
    if "query" not in data:
        return []

    # "pages" is a dict keyed by arbitrary page IDs, not a list --
    # .values() gets us the actual page objects
    pages = data["query"]["pages"].values()

    return list(pages)

def order_bird_photo_options(options):
    preferred = []
    options_copy = options.copy()

    for option in options:
        artist = option.get("artist") or ""

        if "inaturalist" in artist:
            preferred.append(option)
            options_copy.remove(option)
            
    preferred.extend(options_copy)
    return preferred


def get_bird_photo_options(species, common_name=None):
    options = []

    for query in filter(None,[species,common_name]):
        pages = _search_commons_images(query)

        for page in pages:
            imageinfo = page.get("imageinfo")

            if not imageinfo:
                continue

            info = imageinfo[0]

            # Belt-and-suspenders check: only accept files whose MIME type
            # actually starts with "image/" -- catches anything the
            # filetype:image search filter let through by mistake
            mime = info.get("mime", "")
            if not mime.startswith("image/"):
                continue

            metadata = info.get("extmetadata", {})

            options.append({"url": info.get("url"),"license": metadata.get("LicenseShortName", {}).get("value"),"artist": metadata.get("Artist", {}).get("value")})

    if not options:
        return None

    options = order_bird_photo_options(options)
    
    return options