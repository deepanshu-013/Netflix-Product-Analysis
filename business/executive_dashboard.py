from sql.sql_runner import SQLRunner
from analytics.content_analysis import ContentAnalysis
from analytics.genre_analysis import GenreAnalysis
from analytics.country_analysis import CountryAnalysis


class ExecutiveDashboard:
    """
    High-level KPIs for executives.
    Architecture: Business -> Analytics -> SQLRunner -> DuckDB
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner
        self.content = ContentAnalysis(runner)
        self.genre = GenreAnalysis(runner)
        self.country = CountryAnalysis(runner)

    def summary(self) -> dict:
        """Returns a dictionary of top-level KPIs."""

        # 1. Total Titles & Types
        total = self.content.total_titles()
        types_df = self.content.content_type_distribution()

        movies = int(types_df[types_df['type'] == 'Movie']['count'].values[0]) if len(types_df) > 0 else 0
        tv_shows = int(types_df[types_df['type'] == 'TV Show']['count'].values[0]) if len(types_df) > 1 else 0

        # 2. Top Genre & Country
        top_genre_df = self.genre.top_genres(limit=1)
        top_genre = top_genre_df['genre'].values[0] if not top_genre_df.empty else "Unknown"

        top_country_df = self.country.top_countries(limit=1)
        top_country = top_country_df['country'].values[0] if not top_country_df.empty else "Unknown"

        # 3. Averages
        avg_movie_dur = self.content.average_movie_duration()
        avg_show_seasons = self.content.average_tv_show_season()

        # 4. New titles this year
        # We use SQLRunner directly for a highly specific KPI query
        current_year_query = "SELECT EXTRACT(YEAR FROM CURRENT_DATE)"
        current_year = self.runner.fetch_scalar(current_year_query)

        new_titles_query = f"""
            SELECT COUNT(*) 
            FROM titles 
            WHERE EXTRACT(YEAR FROM date_added) = {current_year}
        """
        new_titles = self.runner.fetch_scalar(new_titles_query)

        return {
            "total_titles": total,
            "movies": movies,
            "tv_shows": tv_shows,
            "top_genre": top_genre,
            "top_country": top_country,
            "average_movie_duration": avg_movie_dur,
            "average_show_seasons": avg_show_seasons,
            "new_titles_this_year": new_titles
        }