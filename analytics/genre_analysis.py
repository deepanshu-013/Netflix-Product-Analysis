import pandas as pd
from sql.sql_runner import SQLRunner

class GenreAnalysis:
    """
    Answers business questions related to genres (listed_in).
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def top_genres(self, limit: int = 10) -> pd.DataFrame:
        """Returns the top N genres by title count."""
        query = f"""
            SELECT trim(g) as genre, COUNT(*) as title_count
            FROM titles, UNNEST(SPLIT(listed_in, ',')) AS t(g)
            WHERE trim(g) != ''
            GROUP BY 1
            ORDER BY title_count DESC
            LIMIT {limit}
        """
        return self.runner.fetch_dataframe(query)

    def genre_growth(self) -> pd.DataFrame:
        """Returns the number of titles added per year for the top 10 genres."""
        query = """
            WITH TopGenres AS (
                SELECT trim(g) as genre
                FROM titles, UNNEST(SPLIT(listed_in, ',')) AS t(g)
                WHERE trim(g) != ''
                GROUP BY 1
                ORDER BY COUNT(*) DESC
                LIMIT 10
            )
            SELECT 
                EXTRACT(YEAR FROM t.date_added) as year_added,
                trim(g) as genre,
                COUNT(*) as title_count
            FROM titles t
            JOIN UNNEST(SPLIT(t.listed_in, ',')) AS t(g) ON 1=1
            JOIN TopGenres tg ON trim(g) = tg.genre
            WHERE t.date_added IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1 ASC, 3 DESC
        """
        return self.runner.fetch_dataframe(query)

    def genre_movies_vs_tv(self) -> pd.DataFrame:
        """Returns the count of Movies vs TV Shows for each genre."""
        query = """
            SELECT 
                trim(g) as genre,
                t.type,
                COUNT(*) as title_count
            FROM titles t
            JOIN UNNEST(SPLIT(t.listed_in, ',')) AS t(g) ON 1=1
            WHERE trim(g) != ''
            GROUP BY 1, 2
            ORDER BY 1, 3 DESC
        """
        return self.runner.fetch_dataframe(query)

    def average_genres_per_title(self) -> float:
        """Returns the average number of genres tagged per title."""
        query = """
            SELECT ROUND(AVG(genre_count), 2)
            FROM titles
        """
        return self.runner.fetch_scalar(query)

    def most_common_genre_pairs(self, limit: int = 10) -> pd.DataFrame:
        """Returns the most frequent combinations of two genres on a single title."""
        # We self-join the unnested genres on the same show_id where g1 < g2
        # to avoid duplicate pairs like (Drama, Comedy) and (Comedy, Drama)
        query = f"""
            WITH GenrePairs AS (
                SELECT 
                    trim(g1) as genre_1,
                    trim(g2) as genre_2
                FROM titles t
                JOIN UNNEST(SPLIT(t.listed_in, ',')) AS t1(g1) ON 1=1
                JOIN UNNEST(SPLIT(t.listed_in, ',')) AS t2(g2) ON 1=1
                WHERE trim(g1) != '' AND trim(g2) != '' AND g1 < g2
            )
            SELECT 
                genre_1,
                genre_2,
                COUNT(*) as pair_count
            FROM GenrePairs
            GROUP BY 1, 2
            ORDER BY pair_count DESC
            LIMIT {limit}
        """
        return self.runner.fetch_dataframe(query)