import duckdb
import pandas as pd

class SQLRunner:
    """
    Executes SQL queries against a provided database connection.
    """

    def __init__(self, connection: duckdb.DuckDBPyConnection):
        self.conn = connection

    def execute(self, query: str):
        """
        Executes a SQL query (e.g. DDL, DML, or INSERT)
        :param query:
        :return:
        """
        self.conn.execute(query)

    def fetch_dataframe(self, query: str) -> pd.DataFrame:
        """
        Executes a SELECT query and return the Pandas DataFrame.
        :param query:
        """
        return self.conn.execute(query).fetchdf()

    def fetch_scalar(self, query: str):
        """
        Execute a query that is expected to return a single row and column
        (e.g., COUNT(*), MAX(date)). Returns the scalar value.
        :param query:
        """
        result = self.conn.execute(query).fetchone()
        return result[0] if result else None

    def explain(self, query: str):
        """
        Return the query execution plan for a given SQL query.
        Useful for performance tuning in analytics modules.
        :param query:
        """
        # DuckDB's EXPLAIN returns a DataFrame with execution plan
        return self.conn.execute(f"EXPLAIN {query}").fetchdf()
