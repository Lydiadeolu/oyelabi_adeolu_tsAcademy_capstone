from ts_academy_capstone.load import load_logistics_data
from sql_database.database import save_tables_to_sql_server
from ts_academy_capstone.cleaning import (
    engineer_logistics_features,
    standardize_logistics_data,
    validate_relational_integrity,
)

# Import functions from your separate modules
from ts_academy_capstone.features_aggregate import ( 
    analyze_customer_performance,
    analyze_driver_performance,
    analyze_fleet_utilization,
    analyze_fuel_efficiency,
    analyze_maintenance,
    analyze_route_profitability,
    analyze_safety_metrics,
    analyze_seasonal_patterns,
)


def run_complete_logistics_pipeline(data_directory: str = "data/raw_data"):
  """Executes the end-to-end modular logistics analytics pipeline."""
  print("=== PHASE 1: INGESTION ===")
  # 1. Load all 14 raw CSV files using load.py
  raw_tables = load_logistics_data(data_directory)
  print(f"Loaded {len(raw_tables)} raw tables into memory.")

  print("\n=== PHASE 2: STANDARDIZATION & CLEANING ===")
  # 2. Standardize schemas, clean names, and align dates content-aware via cleaning.py
  cleaned_tables = standardize_logistics_data(raw_tables)

  print("\n=== PHASE 3: RELATIONAL INTEGRITY CHECK ===")
  # 3. Drop duplicates and filter out orphan records via cleaning.py
  validated_tables = validate_relational_integrity(cleaned_tables)

  print("\n=== PHASE 4: OPERATIONAL FEATURE ENGINEERING ===")
  # 4. Compute core metrics like MPG, TCO, and Risk Index via cleaning.py
  enriched_tables = engineer_logistics_features(validated_tables)

  print("\n=== PHASE 5: EXECUTIVE ANALYTICS & AGREGATIONS ===")
  # 5. Extract high-level business intelligence using features&aggregte.py functions
  analytics_results = {
      "driver_performance": analyze_driver_performance(
          enriched_tables.get("driver_monthly_metrics"),
          enriched_tables.get("safety_incidents"),
      ),
      "route_profitability": analyze_route_profitability(
          enriched_tables.get("routes"), enriched_tables.get("loads")
      ),
      "fleet_utilization": analyze_fleet_utilization(
          enriched_tables.get("truck_utilization_metrics")
      ),
      "maintenance_summary": analyze_maintenance(
          enriched_tables.get("maintenance_records"),
          enriched_tables.get("truck_utilization_metrics"),
      ),
      "fuel_audit": analyze_fuel_efficiency(
          enriched_tables.get("fuel_purchases"),
          enriched_tables.get("trips"),
      ),
      "customer_performance": analyze_customer_performance(
          enriched_tables.get("loads"),
          enriched_tables.get("customers_csv"),
          enriched_tables.get("delivery_events"),
      ),
      "safety_summary": analyze_safety_metrics(
          enriched_tables.get("safety_incidents")
      ),
      "seasonal_patterns": analyze_seasonal_patterns(
          enriched_tables.get("loads")
      ),
  }

  print("\n=== PIPELINE EXECUTION SUCCESSFUL ===")
  return enriched_tables, analytics_results


# Execute pipeline
if __name__ == "__main__":
  master_tables, executive_kpis = run_complete_logistics_pipeline(
      "data/raw_data"
  )

# Combine master tables and executive KPIs into one unified dictionary
  all_pipeline_outputs = {**master_tables, **executive_kpis}

  print("\n=== PHASE 6: PERSISTING TO SQL SERVER ===")
  save_tables_to_sql_server(all_pipeline_outputs)