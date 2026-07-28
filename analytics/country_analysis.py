import pandas as pd
from sql.sql_runner import SQLRunner

class CountryAnalysis:
    """
    Answers questions related to the countries producing the content.
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def total_countries(self) -> int:
        """ Returns the total number of unique countries."""
        query= """
            SELECT COUNT(DISTINCT trim(c))
            FROM titles, UNNEST(SPLIT(country, ',')) AS t(c)
            WHERE trim(c) != '' AND trim(c) != 'Unknown'    
        """
        return self.runner.fetch_scalar(query)

    def top_countries(self, limit: int = 10) -> pd.DataFrame:
        """
        Returns the top N countries by number of titles produced.
        :param limit:
        """
        query= f"""
            SELECT trim(c) AS country, COUNT(*) AS title_count
            FROM titles, UNNEST(SPLIT(country, ',')) AS t(c)
            WHERE trim(c) != '' AND trim(c) != 'Unknown'    
            GROUP BY 1
            ORDER BY title_count DESC
            LIMIT {limit}
        """
        return self.runner.fetch_dataframe(query)

    def average_countries_per_title(self) -> float:
        """
        Returns the average number of countries listed per title.
        """
        query= """
            SELECT ROUND(AVG(country_count), 2)
            FROM titles
            WHERE country != 'Unknown'
        """
        return self.runner.fetch_scalar(query)

    def single_country_vs_multi_country(self) -> pd.DataFrame:
        """
        Returns the count of titles produced by a single country vs multiple.
        """
        query= """
            SELECT 
                CASE WHEN country_count = 1 THEN 'Single Country'
                    WHEN country_count > 1 THEN 'Multiple Countries'
                    ELSE 'Unknown'
                END AS production_type,
                COUNT(*) AS title_count
            FROM titles
            GROUP BY 1
            ORDER BY title_count DESC
        """
        return self.runner.fetch_dataframe(query)

    def country_growth_over_time(self) -> pd.DataFrame:
        """
        Returns the number of titles added per year for the top 10 countries.
        """
        query= """
            WITH TopCountries AS (
                SELECT trim(c) AS country
                FROM titles, UNNEST(SPLIT(country, ',')) AS t(c)
                WHERE trim(c) != '' AND trim(c) != 'Unknown'
                GROUP BY 1
                ORDER BY COUNT(*) DESC
                LIMIT 10
            )
            SELECT
                EXTRACT(YEAR FROM t.date_added) AS year_added,
                trim(c) AS country,
                COUNT(*) AS title_count
            FROM titles t 
            JOIN UNNEST(SPLIT(t.country, ',')) AS t(c) ON 1=1
            JOIN TopCountries tc ON trim(c) = tc.country
            WHERE t.date_added IS NOT NULL
            GROUP BY 1, 2
            ORDER BY 1 ASC, 3 DESC 
        """
        return self.runner.fetch_dataframe(query)

    def country_movie_vs_tv(self) -> pd.DataFrame:
        """Returns the split of Movies vs TV Shows for the top 10 countries."""
        query = """
            WITH TopCountries AS (
                SELECT trim(c) AS country
                FROM titles, UNNEST(SPLIT(country, ',')) AS t(c)
                WHERE trim(c) != '' AND trim(c) != 'Unknown'
                GROUP BY 1
                ORDER BY COUNT(*) DESC
                LIMIT 10
            )
            SELECT 
                trim(c) AS country,
                t.type,
                COUNT(*) AS title_count
            FROM titles t 
            JOIN UNNEST(SPLIT(t.country, ',')) AS t(c) ON 1=1
            JOIN TopCountries tc ON trim(c) = tc.country
            GROUP BY 1, 2
            ORDER BY 1 ASC, 3 DESC
        """
        return self.runner.fetch_dataframe(query)