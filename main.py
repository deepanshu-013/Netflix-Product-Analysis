from preprocessing.preprocessing import Preprocessor
from database.database import Database
from sql.sql_runner import SQLRunner
from analytics.content_analysis import ContentAnalysis

p = Preprocessor()
df, report = p.preprocess()
print(f"Cleaned Dataset Shape: {df.shape}")
print(f"Fatal Errors: {report.get('fatal_errors', 'None')}")


db = Database()
db.load_database(df)
print("Data inserted into 'titles' table.")

# print("Testing SQLRunner...")
print("Running Content Analysis...")
conn = db.get_connection()
runner = SQLRunner(connection=conn)

# # Fetch scalar
# total_titles = runner.fetch_scalar("SELECT COUNT(*) FROM titles")
# print(f"Total titles via SQLRunner: {total_titles}")
#
# # Fetch dataframe
# sample_df = runner.fetch_dataframe("SELECT type, COUNT(*) as count FROM titles GROUP BY type")
# print("Content type distribution:")
# print(sample_df.to_string(index=False))
#
# # 4. Close connection
# db.close()
# print("\nPipeline finished successfully.")

analyzer = ContentAnalysis(runner=runner)

# Total titles
total = analyzer.total_titles()
print(f"Total titles: {total}")

# Movies vs TV Shows
dist_df = analyzer.content_type_distribution()
print("\nMovies vs TV Shows:")
print(dist_df.to_string(index=False))

# Average movie duration
avg_dur = analyzer.average_movie_duration()
print(f"\nAverage Movie Duration: {avg_dur} minutes")

# Content added per year (showing last 5 years)
yearly_df = analyzer.content_added_per_year()
print("\nContent added per year (Recent 5 years):")
print(yearly_df.tail(5).to_string(index=False))

# Close connection
db.close()
print("\nPipeline finished successfully.")
