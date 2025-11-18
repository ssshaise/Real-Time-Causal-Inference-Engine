import duckdb
import pandas as pd
import logging

DB_PATH = "data/rcie.duckdb"

class Database:
    def __init__(self):
        self.conn = duckdb.connect(DB_PATH)
    
    def import_csv(self, csv_path: str, table_name: str = "events"):
        """Loads a CSV into DuckDB table"""
        self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM read_csv_auto('{csv_path}')")
        logging.info(f"Data loaded into table '{table_name}'")

    def get_data(self, table_name: str = "events") -> pd.DataFrame:
        """Fetches data as Pandas DataFrame"""
        return self.conn.execute(f"SELECT * FROM {table_name}").df()

    def query(self, sql: str):
        return self.conn.execute(sql).df()

# Initialize DB
if __name__ == "__main__":
    db = Database()
    db.import_csv("data/raw/ecommerce_data.csv")
    print(db.query("SELECT count(*) FROM events"))