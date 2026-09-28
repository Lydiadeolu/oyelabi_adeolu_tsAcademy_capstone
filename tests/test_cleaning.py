import numpy as np
import pandas as pd
import pytest
from ts_academy_capstone.cleaning import (
    clean_dataframe_schema,
    detect_and_fix_dates_by_content,
    engineer_logistics_features,
    standardize_logistics_data,
    validate_relational_integrity,
)


def test_clean_dataframe_schema():
  """Tests conversion of headers to strict snake_case."""
  df = pd.DataFrame({"Truck ID": [1], "Driver Name!": ["A"]})
  res = clean_dataframe_schema(df)
  assert list(res.columns) == ["truck_id", "driver_name"]


def test_detect_and_fix_dates_by_content():
  """Tests dynamic timestamp recognition and datetime conversion."""
  df = pd.DataFrame({
      "created_date": ["2026-01-01", "2026-01-02"],
      "not_a_date": ["abc", "def"],
  })
  res = detect_and_fix_dates_by_content(df)
  assert pd.api.types.is_datetime64_any_dtype(res["created_date"])
  assert not pd.api.types.is_datetime64_any_dtype(res["not_a_date"])


def test_standardize_logistics_data():
  """Tests pipeline table standardization and missing value filling."""
  tables = {
      "safety_incidents": pd.DataFrame(
          {"incident_id": [1], "incident_count": [np.nan]}
      ),
  }
  res = standardize_logistics_data(tables)
  assert res["safety_incidents"]["incident_count"].iloc[0] == 0.0


def test_validate_relational_integrity(sample_trips_df, sample_fuel_df):
  """Tests orphan record filtering (e.g., invalid foreign keys) using conftest fixtures."""
  # Append an orphan row (trip_id 99) to test filtering
  invalid_fuel = pd.concat(
      [
          sample_fuel_df,
          pd.DataFrame(
              {"trip_id": [99], "gallons": [20], "total_cost": [80.0]}
          ),
      ],
      ignore_index=True,
  )

  tables = {
      "trips": sample_trips_df,
      "fuel_purchases": invalid_fuel,
  }
  res = validate_relational_integrity(tables)
  # Should drop the orphan record with trip_id 99, leaving the original 2 rows
  assert len(res["fuel_purchases"]) == 2


def test_engineer_logistics_features(sample_logistics_tables):
  """Tests MPG, TCO, and risk index calculations using conftest fixtures."""
  res = engineer_logistics_features(sample_logistics_tables)
  assert "calculated_mpg" in res["trips"].columns
  assert "total_trip_cost" in res["trips"].columns
  assert "risk_score" in res["trips"].columns