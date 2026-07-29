import pandas as pd
from sql.sql_runner import SQLRunner

class RatingAnalysis:
    """
    Answers business questions related to content ratings.
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def rating_distribution(self) -> pd.DataFrame:
        """Returns the total count of titles for each rating."""
        query = """
            SELECT rating, COUNT(*) as title_count
            FROM titles
            GROUP BY rating
            ORDER BY title_count DESC
        """
        return self.runner.fetch_dataframe(query)

    def movie_rating_distribution(self) -> pd.DataFrame:
        """Returns the count of Movies for each rating."""
        query = """
            SELECT rating, COUNT(*) as title_count
            FROM titles
            WHERE type = 'Movie'
            GROUP BY rating
            ORDER BY title_count DESC
        """
        return self.runner.fetch_dataframe(query)

    def tv_rating_distribution(self) -> pd.DataFrame:
        """Returns the count of TV Shows for each rating."""
        query = """
            SELECT rating, COUNT(*) as title_count
            FROM titles
            WHERE type = 'TV Show'
            GROUP BY rating
            ORDER BY title_count DESC
        """
        return self.runner.fetch_dataframe(query)

    def kids_vs_adults(self) -> pd.DataFrame:
        """
        Groups ratings into 'Kids/Family', 'Teens', 'Adults', and 'Unrated'.
        """
        query = """
            SELECT 
                CASE 
                    WHEN rating IN ('G', 'TV-Y', 'TV-Y7', 'TV-Y7-FV', 'TV-G', 'PG', 'TV-PG') THEN 'Kids/Family'
                    WHEN rating IN ('PG-13', 'TV-14') THEN 'Teens'
                    WHEN rating IN ('R', 'NC-17', 'TV-MA') THEN 'Adults'
                    ELSE 'Unrated/Other'
                END as audience_category,
                COUNT(*) as title_count
            FROM titles
            GROUP BY 1
            ORDER BY title_count DESC
        """
        return self.runner.fetch_dataframe(query)

    def rating_trend(self) -> pd.DataFrame:
        """Returns the number of titles added per year, split by rating."""
        query = """
            SELECT 
                EXTRACT(YEAR FROM date_added) as year_added,
                rating,
                COUNT(*) as title_count
            FROM titles
            WHERE date_added IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1 ASC, 3 DESC
        """
        return self.runner.fetch_dataframe(query)