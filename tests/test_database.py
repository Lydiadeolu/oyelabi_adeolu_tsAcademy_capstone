from unittest.mock import patch, MagicMock
import pandas as pd
import pytest

from sql_database.database import get_sql_server_engine, save_tables_to_sql_server


@patch("sql_database.database.create_engine")
def test_get_sql_server_engine(mock_create_engine):
    """Tests that the SQLAlchemy engine is created with the correct MSSQL/PyODBC connection string format."""
    get_sql_server_engine("localhost\\SQLEXPRESS", "LogisticsCapstone")
    mock_create_engine.assert_called_once()
    args, _ = mock_create_engine.call_args
    assert "mssql+pyodbc://@localhost\\SQLEXPRESS/LogisticsCapstone" in args[0]
    assert "trusted_connection=yes" in args[0]


@patch("pandas.DataFrame.to_sql")
@patch("sql_database.database.create_engine")
def test_save_tables_to_sql_server(mock_create_engine, mock_to_sql):
    """Tests bulk uploading of table dictionaries to SQL Server using mocks."""
    mock_engine = MagicMock()
    mock_create_engine.return_value = mock_engine

    # Provide a valid non-empty dataframe and an empty one to test filtering logic
    tables = {
        "trips": pd.DataFrame({"trip_id": [1, 2], "revenue": [500, 700]}),
        "empty_table": pd.DataFrame()
    }

    save_tables_to_sql_server(tables, "localhost\\SQLEXPRESS", "LogisticsCapstone")

    # Verify that to_sql was called exactly once (skipping the empty table)
    mock_to_sql.assert_called_once()
    _, kwargs = mock_to_sql.call_args
    assert kwargs["con"] == mock_engine
    assert kwargs["if_exists"] == "replace"
    assert kwargs["index"] is False