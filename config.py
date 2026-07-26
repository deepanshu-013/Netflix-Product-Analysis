from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

DATA_PATH = PROJECT_DIR / "data" / "netflix_titles.csv"
DB_PATH = PROJECT_DIR / "database" / "product_analytics.db"

RANDOM_SEED = 42

DATE_FORMAT = "%B %d, %Y"

VALID_RATINGS = {
    "TV-MA", "TV-14", "TV-PG", "R", "PG-13", "PG", "G",
    "NR", "UR", "TV-Y", "TV-Y7", "TV-Y7-FV", "NC-17", "TV-G"
}

REQUIRED_COLUMNS = [
    "show_id", "type", "title", "director", "cast", "country",
    "date_added", "release_year", "rating", "duration",
    "listed_in", "description"
]

