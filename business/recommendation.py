from asyncio.windows_events import NULL
from sql.sql_runner import SQLRunner
from business.executive_dashboard import ExecutiveDashboard
from business.content_strategy import ContentStrategy
from business.regional_analysis import RegionalAnalysis


class Recommendations:
    """
    The ultimate business orchestrator.
    Combines metrics from all other business modules to generate strategic action items.
    """

    def __init__(self, runner: SQLRunner):
        self.runner = runner
        self.dashboard = ExecutiveDashboard(runner)
        self.strategy = ContentStrategy(runner)
        self.regional = RegionalAnalysis(runner)

    def next_action(self) -> list:
        """
        Analyzes the catalog and returns a prioritized list of strategic actions.
        """
        actions = []

        # 1. Genre Strategy Recommendations
        expand = self.strategy.best_genres_to_expand()
        if expand.get("genre"):
            actions.append(f"Increase {expand['genre']} investment (Reason: {expand['reason']})")

        decline = self.strategy.genre_decline()
        if decline.get("genre") and "Declining" in decline.get("trend", ""):
            actions.append(f"Monitor declining {decline['genre']} acquisitions")

        # 2. Regional Strategy Recommendations
        profiles = self.regional.get_regional_profiles(limit=10)

        # Find the fastest-growing emerging market
        emerging_markets = [p for p in profiles if p['yoy_growth'] is not NULL and p['yoy_growth'] > 10]
        if emerging_markets:
            # Sort by growth descending
            top_emerging = sorted(emerging_markets, key=lambda x: x['yoy_growth'], reverse=True)[0]
            actions.append(
                f"Expand {top_emerging['country']} content (Reason: {top_emerging['yoy_growth']}% YoY growth)")

        # Find markets heavily skewed towards Movies (suggesting TV opportunity)
        tv_opportunities = [p for p in profiles if p['movie_pct'] > 75 and p['total_titles'] > 100]
        if tv_opportunities:
            # Just pick the first one as an example
            target = tv_opportunities[0]
            actions.append(f"Acquire more TV Shows in {target['country']} (Currently {target['movie_pct']}% Movies)")

        # 3. General Catalog Health
        summary = self.dashboard.summary()
        if summary.get("movies", 0) > summary.get("tv_shows", 0) * 2:
            actions.append("Reduce reliance on Movie-only acquisitions to balance catalog")

        return actions