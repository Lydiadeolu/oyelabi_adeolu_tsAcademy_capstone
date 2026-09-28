from pathlib import Path
import tempfile
import pandas as pd
import pytest

from ts_academy_capstone.load import load_logistics_data


def test_load_logistics_data_success():
  """Tests that CSV files in a target directory are loaded correctly into DataFrames."""
  with tempfile.TemporaryDirectory() as tmpdir:
    tmp_path = Path(tmpdir)
    df = pd.DataFrame({"column_a": [1, 2], "column_b": [3, 4]})
    df.to_csv(tmp_path / "test_table.csv", index=False)

    tables = load_logistics_data(str(tmp_path))
    assert "test_table" in tables
    assert len(tables["test_table"]) == 2


def test_load_logistics_data_empty():
  """Tests behavior when the target directory contains no CSV files."""
  with tempfile.TemporaryDirectory() as tmpdir:
    tables = load_logistics_data(tmpdir)
    assert len(tables) == 0