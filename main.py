from preprocessing.preprocessing import Preprocessor
from database.database import Database
from sql.sql_runner import SQLRunner
from stats.inference import InferenceStats
from business.executive_dashboard import ExecutiveDashboard
from business.content_strategy import ContentStrategy
import json


def main():
    print("=" * 60)
    print("Product Analytics — Netflix Titles Pipeline")
    print("=" * 60)

    # 1. Preprocess
    print("\nRunning Preprocessor...")
    preprocessor = Preprocessor()
    df, report = preprocessor.preprocess()
    print(f"Cleaned Dataset Shape: {df.shape}")

    # 2. Database Ingestion
    print("\nLoading data into DuckDB...")
    db = Database()
    db.load_database(df)
    print("Data inserted into 'titles' table.")

    # 3. Fetch Data via SQLRunner
    print("\nRunning Inference Statistics...")
    conn = db.get_connection()
    runner = SQLRunner(connection=conn)

    # Fetch a relevant subset of data for our tests
    test_df = runner.fetch_dataframe("""
                                     SELECT type, rating, release_year
                                     FROM titles
                                     WHERE rating IS NOT NULL
                                       AND rating != 'Unknown'
                                     """)

    inference = InferenceStats(df=test_df)

    # --- Test 1: Confidence Interval ---
    # print("\n--- Confidence Interval (Movie Duration) ---")
    # ci_lower, ci_upper = inference.confidence_interval('rating', confidence=0.95)
    # print(f"95% Confidence Interval for Movie Duration: [{ci_lower:.2f}, {ci_upper:.2f}] minutes")
    # print("(We are 95% confident the true average movie length falls in this range)")

    # --- Test 2: Chi-Square Test of Independence ---
    print("\n--- Chi-Square Test (Type vs Rating) ---")
    chi_results = inference.chi_square('type', 'rating')
    print(f"Chi2 Statistic: {chi_results['chi2_statistic']}")
    print(f"P-value: {chi_results['p_value']}")
    if chi_results['p_value'] < 0.05:
        print("Result: Significant relationship between Content Type and Rating (Reject Null Hypothesis)")
    else:
        print("Result: No significant relationship (Fail to Reject Null Hypothesis)")

    # --- Test 3: One-Way ANOVA ---
    print("\n--- One-Way ANOVA (Release Year across Ratings) ---")
    anova_results = inference.anova('rating', 'release_year')
    print(f"F-Statistic: {anova_results['f_statistic']:.2f}")
    print(f"P-value: {anova_results['p_value']:.4e}")
    if anova_results['p_value'] < 0.05:
        print("Result: Significant difference in release years among rating groups (Reject Null Hypothesis)")
    else:
        print("Result: No significant difference in release years (Fail to Reject Null Hypothesis)")

    # 4. Business Layer Execution
    print("\n[3] Running Business Layer...")
    # Executive Dashboard
    dashboard = ExecutiveDashboard(runner=runner)
    summary = dashboard.summary()

    print("\n--- Executive Summary ---")
    # Pretty print the JSON dictionary
    print(json.dumps(summary, indent=4))

    # Content Strategy
    strategy = ContentStrategy(runner=runner)

    print("\n--- Content Strategy Recommendations ---")
    expand = strategy.best_genres_to_expand()
    print(f"Expand: {expand}")

    decline = strategy.genre_decline()
    print(f"Decline: {decline}")

    # 5. Close connection
    db.close()
    print("\n" + "=" * 60)
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()