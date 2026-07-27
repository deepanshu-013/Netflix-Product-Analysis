import pandas as pd
from sql.sql_runner import SQLRunner


class ContentAnalysis:
    """
    Answers business questions about the content catalog.
    Architecture: Analytics -> SQLRunner -> DuckDB
    """
    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def total_titles(self) -> int:
        """
        Returns the total number of titles in the content catalog.
        """
        query = "SELECT COUNT(*) FROM titles"
        return self.runner.fetch_scalar(query)

    def content_type_distribution(self) -> pd.DataFrame:
        """
        Return the raw count of Movies vs TV shows.
        """
        query = """
            SELECT type, COUNT(*) as count
            FROM titles
            GROUP BY type
            ORDER BY count DESC
        """
        return self.runner.fetch_dataframe(query)

    def content_type_distribution_percentage(self) -> pd.DataFrame:
        """
        Return the percentage split of Movies vs TV Shows.
        """
        query = """
            SELECT type, 
                COUNT(*) as count,
                ROUND(
                    COUNT(*) * 100.0 / 
                    SUM(COUNT(*)) OVER (),
                    2) 
                as percentage
            FROM titles
            GROUP BY type
            ORDER BY percentage DESC
        """
        return self.runner.fetch_dataframe(query)

    def average_movie_duration(self) -> float:
        """
        Returns the average duration of Movies in minutes.
        """
        query= """
            SELECT ROUND(AVG(duration_minutes), 2)
            FROM titles
            WHERE type = 'Movie' AND duration_minutes IS NOT NULL
        """
        return self.runner.fetch_scalar(query)

    def average_tv_show_season(self) -> float:
        """
        Returns the average number of seasons in TV shows.
        """
        query= """
            SELECT ROUND(AVG(TRY_CAST(REGEXP_EXTRACT(duration, '^[0-9]+', 0) AS INTEGER)), 2)
            FROM titles
            WHERE type = 'TV Show'
        """
        return self.runner.fetch_scalar(query)

    def oldest_title(self) -> pd.DataFrame:
        """
        Returns the oldest title(s) based on release year.
        """
        query= """
            SELECT title, release_year
            FROM titles
            WHERE  release_year = (
                SELECT MIN(release_year)
                FROM titles
                WHERE release_year > 0
            )
        """
        return self.runner.fetch_dataframe(query)

    def newest_title(self) -> pd.DataFrame:
        """
        Returns the newest title(s) based on release year.
        """
        query = """
            SELECT title, release_year
            FROM titles
            WHERE release_year = (
                SELECT MAX(release_year) 
                FROM titles 
                WHERE release_year > 0
            )
        """
        return self.runner.fetch_dataframe(query)

    def content_added_per_year(self) -> pd.DataFrame:
        """
        Returns the count of content added to the catalog per year.
        """
        query= """
            SELECT 
                EXTRACT(YEAR FROM date_added) as year_added, 
                COUNT(*) as count
            FROM titles
            WHERE date_added IS NOT NULL
            GROUP BY year_added
            ORDER by year_added ASC
        """
        return self.runner.fetch_dataframe(query)

    def content_added_per_month(self) -> pd.DataFrame:
        """
        Returns the count of content added to the catalog per month.
        """
        query= """
            SELECT 
                MONTHNAME(date_added) AS month, 
                COUNT(*) AS count
            FROM titles
            WHERE date_added IS NOT NULL
            GROUP BY MONTH(date_added)
            ORDER by MONTH(date_added)
        """
        return self.runner.fetch_dataframe(query)
