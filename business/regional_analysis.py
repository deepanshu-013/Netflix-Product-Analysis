from asyncio.windows_events import NULL

import pandas as pd
from sql.sql_runner import SQLRunner


class RegionalAnalysis:
    """
    Analyzes regional market trends, growth, and genre composition.
    Architecture: Business -> Analytics -> SQLRunner -> DuckDB
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def get_regional_profiles(self, limit: int = 10) -> list:
        """
        Builds comprehensive profiles for the top N countries.
        Includes Movie/TV split, dominant genre, and YoY growth.
        """
        # 1. Get Country Metrics (Volume & Movie/TV Split)
        metrics_query = f"""
            WITH CountryData AS (
                SELECT 
                    trim(c) as country,
                    t.show_id,
                    t.type,
                    EXTRACT(YEAR FROM t.date_added) as yr
                FROM titles t, UNNEST(SPLIT(t.country, ',')) AS t(c)
                WHERE t.date_added IS NOT NULL AND trim(c) NOT IN ('', 'Unknown')
            ),
            YearlyCounts AS (
                SELECT country, yr, COUNT(DISTINCT show_id) as cnt
                FROM CountryData GROUP BY 1, 2
            ),
            LatestYear AS (
                SELECT MAX(yr) as max_yr FROM YearlyCounts
            ),
            GrowthData AS (
                SELECT 
                    y1.country,
                    y1.cnt as latest_cnt,
                    y0.cnt as prev_cnt,
                    CASE WHEN y0.cnt IS NULL OR y0.cnt = 0 THEN NULL 
                         ELSE ROUND((y1.cnt - y0.cnt) * 100.0 / y0.cnt, 1) 
                    END as yoy_growth
                FROM YearlyCounts y1
                JOIN LatestYear ly ON y1.yr = ly.max_yr
                LEFT JOIN YearlyCounts y0 ON y1.country = y0.country AND y0.yr = (ly.max_yr - 1)
            )
            SELECT 
                cd.country,
                COUNT(DISTINCT cd.show_id) as total_titles,
                ROUND(COUNT(DISTINCT CASE WHEN cd.type='Movie' THEN cd.show_id END) * 100.0 / COUNT(DISTINCT cd.show_id), 1) as movie_pct,
                ROUND(COUNT(DISTINCT CASE WHEN cd.type='TV Show' THEN cd.show_id END) * 100.0 / COUNT(DISTINCT cd.show_id), 1) as tv_pct,
                g.yoy_growth
            FROM CountryData cd
            JOIN GrowthData g ON cd.country = g.country
            GROUP BY 1, g.yoy_growth
            ORDER BY total_titles DESC
            LIMIT {limit}
        """
        profiles_df = self.runner.fetch_dataframe(metrics_query)

        # 2. Get Dominant Genre per Country
        genre_query = """
                      WITH CountryGenres AS (
                          SELECT 
                              trim(c) as country,
                              trim(g)  as genre, 
                              COUNT(*) as cnt 
                          FROM titles, UNNEST(SPLIT(country, ',')) AS t(c), UNNEST(SPLIT(listed_in, ',')) AS t(g) 
                          WHERE trim(c) NOT IN ('', 'Unknown') 
                          AND trim(g) != ''
                          GROUP BY 1, 2
                      ),
                      Ranked AS (
                        SELECT 
                          country, 
                          genre, 
                          ROW_NUMBER() OVER (PARTITION BY country ORDER BY cnt DESC) as rnk
                        FROM CountryGenres
                      )
                      SELECT 
                          country, 
                          genre as dominant_genre
                      FROM Ranked 
                      WHERE rnk = 1 
                      """
        genres_df = self.runner.fetch_dataframe(genre_query)

        # 3. Merge in Pandas and format to list of dicts
        if profiles_df.empty:
            return []

        merged_df = pd.merge(profiles_df, genres_df, on='country', how='left')

        profiles = []
        for _, row in merged_df.iterrows():
            growth = row['yoy_growth'] if pd.notna(row['yoy_growth']) else NULL
            profiles.append({
                "country": row['country'],
                "movie_pct": row['movie_pct'],
                "tv_pct": row['tv_pct'],
                "dominant_genre": row['dominant_genre'],
                "yoy_growth": growth,
                "total_titles": int(row['total_titles']),
                "opportunity": self.__assess_opportunity(row['movie_pct'], growth)
            })

        return profiles

    def __assess_opportunity(self, movie_pct: float, growth: float) -> str:
        """Internal business logic to tag a region's opportunity level."""
        if growth > 15:
            return "High Growth / Expansion Opportunity"
        elif movie_pct > 80:
            return "High Movie Concentration (Potential for TV Expansion)"
        else:
            return "Stable / Mature Market"