from sqlalchemy import create_engine
import pandas as pd

def get_sql_server_engine(server: str = "localhost\\SQLEXPRESS", database: str = "LogisticsCapstone"):
    """
    Creates a SQLAlchemy engine for SQL Server using Windows Authentication.
    Adjust 'server' (e.g., 'localhost', 'localhost\\SQLEXPRESS', or your machine name) 
    and 'database' as needed for your SSMS setup.
    """
    connection_string = (
        f"mssql+pyodbc://@{server}/{database}"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )
    return create_engine(connection_string)

def save_tables_to_sql_server(tables: dict, server: str = "localhost\\SQLEXPRESS", database: str = "LogisticsCapstone") -> None:
    """
    Persists all standardized and aggregated pipeline tables directly into SQL Server tables.
    """
    try:
        engine = get_sql_server_engine(server, database)
        for table_name, df in tables.items():
            if isinstance(df, pd.DataFrame) and not df.empty:
                df.to_sql(table_name, con=engine, if_exists='replace', index=False)
                print(f"Table '{table_name}' successfully loaded into SQL Server.")
        print("All pipeline tables synchronized to SSMS successfully!")
    except Exception as e:
        print(f"Error connecting to SQL Server: {e}")