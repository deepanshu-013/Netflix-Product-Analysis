DATA_PATH = "./netflix_titles.csv"

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

