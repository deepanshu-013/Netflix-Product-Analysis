import pandas as pd
from sql.sql_runner import SQLRunner

class ReleaseAnalysis:
    """
    Answers business questions based on the original release year of the content.
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def titles_per_year(self) -> pd.DataFrame:
        """Returns the number of titles released per year."""
        query = """
            SELECT release_year, COUNT(*) as title_count
            FROM titles
            WHERE release_year > 0
            GROUP BY release_year
            ORDER BY release_year ASC
        """
        return self.runner.fetch_dataframe(query)

    def titles_per_decade(self) -> pd.DataFrame:
        """Returns the number of titles released per decade."""
        query = """
            SELECT release_decade, COUNT(*) as title_count
            FROM titles
            WHERE release_decade IS NOT NULL AND release_decade > 0
            GROUP BY release_decade
            ORDER BY release_decade ASC
        """
        return self.runner.fetch_dataframe(query)

    def oldest_decade(self) -> int:
        """Returns the earliest decade present in the catalog."""
        query = """
            SELECT MIN(release_decade) 
            FROM titles 
            WHERE release_decade > 0
        """
        return self.runner.fetch_scalar(query)

    def newest_decade(self) -> int:
        """Returns the most recent decade present in the catalog."""
        query = """
            SELECT MAX(release_decade) 
            FROM titles 
            WHERE release_decade IS NOT NULL
        """
        return self.runner.fetch_scalar(query)

    def content_age_distribution(self) -> pd.DataFrame:
        """
        Buckets the content_age (years since release) into understandable groups.
        """
        query = """
            WITH AgeData AS (
                SELECT 
                    CASE 
                        WHEN content_age <= 5 THEN '0-5 years (New)'
                        WHEN content_age <= 10 THEN '6-10 years'
                        WHEN content_age <= 20 THEN '11-20 years'
                        WHEN content_age <= 30 THEN '21-30 years'
                        WHEN content_age > 30 THEN '30+ years (Classic)'
                        ELSE 'Unknown'
                    END as age_bucket,
                    CASE 
                        WHEN content_age <= 5 THEN 1
                        WHEN content_age <= 10 THEN 2
                        WHEN content_age <= 20 THEN 3
                        WHEN content_age <= 30 THEN 4
                        WHEN content_age > 30 THEN 5
                        ELSE 6
                    END as sort_order
                FROM titles
                WHERE content_age IS NOT NULL
            )
            SELECT 
                age_bucket,
                COUNT(*) as title_count
            FROM AgeData
            GROUP BY age_bucket, sort_order
            ORDER BY sort_order
        """
        return self.runner.fetch_dataframe(query)

    def release_trend(self, start_year: int = 2000) -> pd.DataFrame:
        """
        Returns titles released per year since a specified start year.
        Useful for visualizing modern content production trends.
        """
        query = f"""
            SELECT release_year, COUNT(*) as title_count
            FROM titles
            WHERE release_year >= {start_year}
            GROUP BY release_year
            ORDER BY release_year ASC
        """
        return self.runner.fetch_dataframe(query)