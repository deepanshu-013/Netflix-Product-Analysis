from preprocessing.preprocessing import Preprocessor
from database.database import Database
from sql.sql_runner import SQLRunner
from analytics.rating_analysis import RatingAnalysis
from analytics.release_analysis import ReleaseAnalysis

def main():
    print("=" * 60)
    print("Product Analytics — Netflix Titles Pipeline")
    print("=" * 60)

    # 1. Preprocess
    print("\n[1] Running Preprocessor...")
    preprocessor = Preprocessor()
    df, report = preprocessor.preprocess()
    print(f"Cleaned Dataset Shape: {df.shape}")

    # 2. Database Ingestion
    print("\n[2] Loading data into DuckDB...")
    db = Database()
    db.load_database(df)
    print("Data inserted into 'titles' table.")

    # 3. Analytics Execution
    print("\n[3] Running Analytics Modules...")
    conn = db.get_connection()
    runner = SQLRunner(connection=conn)

    # Test Rating Analytics
    rating_analytics = RatingAnalysis(runner=runner)
    print("\n--- Rating Analysis ---")

    print("\n Kids vs Adults Distribution:")
    print(rating_analytics.kids_vs_adults().to_string(index=False))

    # Test Release Analytics
    release_analytics = ReleaseAnalysis(runner=runner)
    print("\n--- Release Analysis ---")

    print(f"Oldest decade: {release_analytics.oldest_decade()}s")
    print(f"Newest decade: {release_analytics.newest_decade()}s")

    print("\nTitles per decade (Recent 5):")
    print(release_analytics.titles_per_decade().tail(5).to_string(index=False))

    print("\nContent Age Distribution:")
    print(release_analytics.content_age_distribution().to_string(index=False))

    # 4. Close connection
    db.close()
    print("\n" + "=" * 60)
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()