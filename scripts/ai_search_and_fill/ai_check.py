from pathlib import Path
import csv
from collections import Counter
from scripts.ai_search_and_fill.ai_integration import spacer

scraped_birds_path = Path("data/scraped_birds.csv")
processed_birds_path = Path("data/processed_birds.csv")
hallucinated_duplicated_birds_path = Path("data/hallucinated_duplicated_birds.csv")

with (
    scraped_birds_path.open(
        "r",
        encoding="utf-8",
        newline = ""
    ) as scraped_file,
    processed_birds_path.open(
        "r",
        encoding="utf-8",
        newline=""
    ) as processed_file,
    hallucinated_duplicated_birds_path.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as hallucinated_duplicated_file
):
    scraped_reader = csv.reader(scraped_file)
    processed_reader = csv.reader(processed_file)
    writer = csv.writer(hallucinated_duplicated_file)

    scraped_species = {
        row[1].strip() for row in scraped_reader
    }

    writer.writerow(["Common Name", "Species", "Hallucinated/Duplicated", "Index in processed csv"])

    # Counter
    seen_counts = Counter()

    # Skip header rows -- otherwise the header itself gets compared
    # against bird data and flagged as "Hallucinated".
    next(scraped_reader, None)
    next(processed_reader, None)

    for index, processed_row in enumerate(processed_reader, start=2):


        common_name = processed_row[1].strip()
        species = processed_row[2].strip()

        seen_counts[species] += 1

        # Exact match, not substring ("in") -- substring checks produce
        # false matches between unrelated birds that share a word
        # (e.g. "Crow" in "American Crow").
        if species not in scraped_species:
            writer.writerow([common_name, species, "Hallucinated", index])

        # Flag every occurrence past the first, so both copies of a
        # duplicate show up for review, not just one.
        if seen_counts[species] > 1:
            # writerow() takes ONE iterable -- the original passed a list
            # plus two extra positional args, which raises a TypeError.
            writer.writerow([common_name, species, "Duplicated", index])