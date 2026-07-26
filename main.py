from preprocessing.preprocessing import Preprocessor
from database.database import Database

p = Preprocessor()
df, report = p.preprocess()

db = Database()
db.load_database(df)

count = db.get_connection().execute("""
SELECT COUNT(*)
FROM titles
""").fetchone()[0]

print(count)