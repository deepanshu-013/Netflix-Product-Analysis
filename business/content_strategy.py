from sql.sql_runner import SQLRunner


class ContentStrategy:
    """
    Analyzes trends to recommend content strategy.
    Architecture: Business -> Analytics -> SQLRunner -> DuckDB
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner

    def best_genres_to_expand(self) -> dict:
        """
        Finds the genre with the highest Year-over-Year (YoY) growth
        in the most recent complete year.
        """
        query = """
                WITH GenreYearCounts AS (
                    SELECT 
                        trim(g) as genre,
                        EXTRACT(YEAR FROM date_added) as yr,
                        COUNT(*) as cnt 
                    FROM titles, UNNEST(SPLIT(listed_in, ',')) AS t(g)
                    WHERE date_added IS NOT NULL AND trim(g) != ''
                    GROUP BY 1, 2
                ),
                YoYGrowth AS (
                    SELECT
                        genre,
                        yr,
                        cnt, 
                        LAG(cnt) OVER (PARTITION BY genre ORDER BY yr) as prev_yr_cnt
                    FROM GenreYearCounts
                ), 
                GrowthRates AS (
                    SELECT
                        genre,
                        yr, 
                        cnt, 
                        prev_yr_cnt,
                        CASE
                            WHEN prev_yr_cnt IS NULL OR prev_yr_cnt = 0 THEN NULL
                            ELSE ROUND(((cnt - prev_yr_cnt) * 100.0 / prev_yr_cnt), 2)
                        END as growth_pct
                    FROM YoYGrowth
                    WHERE yr = (SELECT MAX (yr) FROM GenreYearCounts) -- Most recent year
                )
                SELECT genre, growth_pct
                FROM GrowthRates
                WHERE growth_pct IS NOT NULL
                ORDER BY growth_pct DESC 
                LIMIT 1
                """
        df = self.runner.fetch_dataframe(query)

        if df.empty:
            return {"genre": None, "growth": "0%", "reason": "No growth data available"}

        genre = df['genre'].values[0]
        growth = df['growth_pct'].values[0]

        return {
            "genre": genre,
            "growth": f"+{growth}%" if growth > 0 else f"{growth}%",
            "reason": "Highest YoY growth in the most recent year"
        }

    def genre_decline(self) -> dict:
        """
        Finds the genre with the steepest Year-over-Year (YoY) decline.
        """
        query = """
                WITH GenreYearCounts AS (
                    SELECT 
                        trim(g) as genre, 
                        EXTRACT(YEAR FROM date_added) as yr, 
                        COUNT(*) as cnt 
                    FROM titles, UNNEST(SPLIT(listed_in, ',')) AS t(g)
                    WHERE date_added IS NOT NULL AND trim(g) != ''
                    GROUP BY 1, 2
                ),
                YoYGrowth AS (
                    SELECT
                        genre, 
                        yr, 
                        cnt, 
                        LAG(cnt) OVER (PARTITION BY genre ORDER BY yr) as prev_yr_cnt
                    FROM GenreYearCounts
                ), 
                GrowthRates AS (
                    SELECT
                        genre,
                        yr, 
                        CASE
                            WHEN prev_yr_cnt IS NULL OR prev_yr_cnt = 0 THEN NULL
                            ELSE ROUND(((cnt - prev_yr_cnt) * 100.0 / prev_yr_cnt), 2)
                        END as growth_pct
                    FROM YoYGrowth
                    WHERE yr = (SELECT MAX (yr) FROM GenreYearCounts)
                )
                SELECT genre, growth_pct
                FROM GrowthRates
                WHERE growth_pct IS NOT NULL
                ORDER BY growth_pct ASC 
                LIMIT 1
                """
        df = self.runner.fetch_dataframe(query)

        if df.empty:
            return {"genre": None, "trend": "Unknown"}

        genre = df['genre'].values[0]
        growth = df['growth_pct'].values[0]

        return {
            "genre": genre,
            "trend": f"Declining ({growth}% YoY)" if growth < 0 else "Stagnant or Growing"
        }