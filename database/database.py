import duckdb
import pandas as pd
from config import DB_PATH

class Database:
    """Handles the DuckDB ingestion form DataFrame.
    It only loads data into the database and maintain connectivity."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None

    def __connect(self):
        """Establish connection to DuckDB."""
        if self.conn is None:
            self.conn = duckdb.connect(self.db_path)

    def __create_tables(self, df: pd.DataFrame):
        """Creates the "titles" table in DuckDB as per the DataFrame schema.
        Drops the table first to ensure idempotency."""
        if not self.conn:
            self.__connect()

        # Using DataFrame schema to dynamically create the table.
        # Since Python DataFrame can not be used directly in execute command of DuckDB.
        self.conn.register('_temp_df', df)

        self.conn.execute("DROP TABLE IF EXISTS titles")
        self.conn.execute("""
            CREATE TABLE titles AS
            SELECT * FROM _temp_df
            WHERE 1 = 0 --Create schema without inserting data yet 
            """)

        self.conn.unregister('_temp_df')

    def __insert_dataframe(self, df: pd.DataFrame):
        """Inserts the DataFrame into the database."""
        if not self.conn:
            self.__connect()

        # Using the 'register' again to directly execute insertion.
        self.conn.register('_temp_df', df)
        self.conn.execute("INSERT INTO titles SELECT * FROM _temp_df")
        self.conn.unregister('_temp_df')

    def load_database(self, df: pd.DataFrame):
        """
        Loads the DataFrame into the database.
        Combines, connect()-> create_tables()-> insert_dataframe() in a single function
        """
        if not self.conn:
            self.__connect()
        self.__create_tables(df)
        self.__insert_dataframe(df)

    def get_connection(self):
        """Returns the active DuckDB connection for external use (e.g., SQL queries)."""
        if self.conn is None:
            self.__connect()
        return self.conn

    def close(self):
        """Closes the connection to DuckDB."""
        if self.conn:
            self.conn.close()
            self.conn = None