from pathlib import Path
import pandas as pd


def load_logistics_data(directory_path: str = "data/raw_data") -> dict:
    """Loads all logistics CSV files from a target directory into a dictionary of DataFrames."""
    data_dir = Path(directory_path)
    logistics_tables = {}

    # Iterate through each CSV file safely without shadowing parameters
    for file_item in data_dir.glob("*.csv"):
        table_name = file_item.stem.lower()
        logistics_tables[table_name] = pd.read_csv(file_item)

    return logistics_tables