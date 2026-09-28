import numpy as np
import pandas as pd


def clean_dataframe_schema(df: pd.DataFrame) -> pd.DataFrame:
  """Converts column names to strict snake_case."""
  df.columns = (
      df.columns.str.strip()
      .str.lower()
      .str.replace(r"[^\w\s]", "", regex=True)
      .str.replace(r"\s+", "_", regex=True)
  )
  return df


def detect_and_fix_dates_by_content(df: pd.DataFrame) -> pd.DataFrame:
  """Dynamically inspects column values and names to find and convert date/time fields safely."""
  for col in df.columns:
    # Skip if already a datetime type
    if pd.api.types.is_datetime64_any_dtype(df[col]):
      continue

    # Sample non-null values to test content
    sample_data = df[col].dropna().head(20)
    if sample_data.empty:
      continue

    # Check if column name contains time-related keywords
    is_keyword_match = any(
        kw in col.lower() for kw in ["date", "time", "stamp", "at"]
    )

    parsed_successfully = False
    # Test if object/string column or keyword-matched column can parse as dates
    if is_keyword_match or df[col].dtype == "object":
      try:
        pd.to_datetime(sample_data, errors="raise", format="mixed")
        parsed_successfully = True
      except (ValueError, TypeError):
        parsed_successfully = False

    # Convert safely if content matches
    if parsed_successfully:
      df[col] = pd.to_datetime(df[col], errors="coerce")
      print(
          f"Converted column '{col}' to datetime based on content/keyword"
          " inspection."
      )

  return df


def standardize_logistics_data(tables: dict) -> dict:
  """Applies cleaning rules across specific logistics tables."""
  cleaned_tables = {}

  for name, df in tables.items():
    df = clean_dataframe_schema(df)

    # 1. Advanced Timestamp & Datetime Alignment (Content-Aware)
    df = detect_and_fix_dates_by_content(df)

    # 2. Missing Value Treatment
    if "safety_incidents" in name and "incident_count" in df.columns:
      df["incident_count"] = df["incident_count"].fillna(0)
    elif "status" in df.columns:
      df["status"] = df["status"].ffill()

    cleaned_tables[name] = df

  return cleaned_tables


def validate_relational_integrity(tables: dict) -> dict:
  """Ensures orphan records are filtered out and duplicates are dropped."""
  trips_df = tables.get("trips")

  # 1. Orphan Record Check: Ensure fuel purchases link to real trips
  if "fuel_purchases" in tables and trips_df is not None:
    initial_count = len(tables["fuel_purchases"])
    valid_trips = set(trips_df["trip_id"])
    tables["fuel_purchases"] = tables["fuel_purchases"][
        tables["fuel_purchases"]["trip_id"].isin(valid_trips)
    ]
    dropped = initial_count - len(tables["fuel_purchases"])
    print(f"Dropped {dropped} orphan fuel purchase records.")

  # 2. Duplicate Detection (Fixed string literal bug to use loop variable 'name')
  for name, df in tables.items():
    before_len = len(df)
    tables[name] = df.drop_duplicates()
    after_len = len(tables[name])
    if before_len != after_len:
      print(f"Removed {before_len - after_len} duplicates from {name}.")

  return tables


def engineer_logistics_features(tables: dict) -> dict:
  """Computes MPG, TCO, and Safety Risk Index."""
  trips = tables.get("trips")
  fuel = tables.get("fuel_purchases")
  maintenance = tables.get("maintenance_records")
  safety = tables.get("safety_incidents")

  if trips is not None and fuel is not None:
    # 1. Fuel Efficiency (MPG): Miles driven / Gallons purchased
    trip_fuel = fuel.groupby("trip_id")["gallons"].sum().reset_index()
    trips = trips.merge(trip_fuel, on="trip_id", how="left")

    # Handle alternative column names for distance safely
    distance_col = "distance_miles" if "distance_miles" in trips.columns else "distance"
    if distance_col in trips.columns:
        trips["calculated_mpg"] = trips[distance_col] / trips["gallons"]
    else:
        trips["calculated_mpg"] = 0.0

  if trips is not None and maintenance is not None:
    # 2. Total Cost of Ownership (TCO) per trip approximation
    truck_maint = maintenance.groupby("truck_id")["total_cost"].sum().reset_index()
    trips = trips.merge(truck_maint, on="truck_id", how="left").fillna(
        {"total_cost": 0}
    )

    fuel_cost = trips["total_fuel_cost"] if "total_fuel_cost" in trips.columns else 0
    driver_wages = trips["driver_pay"] if "driver_pay" in trips.columns else 0
    
    trips["total_trip_cost"] = fuel_cost + trips["total_cost"] + driver_wages

  if safety is not None:
    # 3. Safety Risk Index (Weighted severity score per driver/trip)
    severity_col = "severity_level" if "severity_level" in safety.columns else ("severity" if "severity" in safety.columns else None)
    
    if severity_col is not None:
        severity_weights = {"minor": 1, "moderate": 3, "severe": 10}
        safety["risk_score"] = safety[severity_col].map(severity_weights).fillna(1)
        if "trip_id" in safety.columns:
            trip_risk = safety.groupby("trip_id")["risk_score"].sum().reset_index()
            trips = trips.merge(trip_risk, on="trip_id", how="left").fillna(
                {"risk_score": 0}
            )
    else:
        safety["risk_score"] = 1
        if trips is not None and "risk_score" not in trips.columns:
            trips["risk_score"] = 0

  if trips is not None:
    tables["trips"] = trips
  return tables