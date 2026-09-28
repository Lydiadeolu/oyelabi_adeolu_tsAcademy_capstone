import numpy as np
import pandas as pd
import pytest
import sys
from pathlib import Path

root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

@pytest.fixture
def sample_trips_df():
  return pd.DataFrame({
      "trip_id": [1, 2],
      "truck_id": [101, 102],
      "driver_id": [10, 20],
      "distance_miles": [100, 250],
      "actual_distance_miles": [105, 245],
      "average_mpg": [6.5, 7.0],
  })


@pytest.fixture
def sample_fuel_df():
  return pd.DataFrame({
      "trip_id": [1, 2], "gallons": [15, 35], "total_cost": [60.0, 140.0]
  })


@pytest.fixture
def sample_maintenance_df():
  return pd.DataFrame({
      "maintenance_id": [1, 2],
      "truck_id": [101, 102],
      "total_cost": [200.0, 450.0],
      "downtime_hours": [4, 10],
  })


@pytest.fixture
def sample_safety_df():
  return pd.DataFrame({
      "incident_id": [1, 2],
      "driver_id": [10, 20],
      "trip_id": [1, 2],
      "severity_level": ["minor", "moderate"],
      "preventable_flag": [True, False],
      "vehicle_damage_cost": [100, 500],
      "cargo_damage_cost": [0, 200],
      "claim_amount": [50, 300],
  })


@pytest.fixture
def sample_logistics_tables(
    sample_trips_df, sample_fuel_df, sample_maintenance_df, sample_safety_df
):
  return {
      "trips": sample_trips_df,
      "fuel_purchases": sample_fuel_df,
      "maintenance_records": sample_maintenance_df,
      "safety_incidents": sample_safety_df,
  }