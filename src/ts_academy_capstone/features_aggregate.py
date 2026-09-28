import pandas as pd

def analyze_driver_performance(
    driver_monthly: pd.DataFrame, safety: pd.DataFrame
) -> pd.DataFrame:
  """Calculates revenue per mile, on-time rates, and safety risk profiles per driver."""
  driver_perf = (
      driver_monthly.groupby("driver_id")
      .agg(
          total_revenue=("total_revenue", "sum"),
          total_miles=("total_miles", "sum"),
          avg_mpg=("average_mpg", "mean"),
          avg_on_time=("on_time_delivery_rate", "mean"),
      )
      .reset_index()
  )

  driver_perf["revenue_per_mile"] = (
      driver_perf["total_revenue"] / driver_perf["total_miles"]
  )

  driver_safety = (
      safety.groupby("driver_id")
      .agg(
          total_incidents=("incident_id", "count"),
          preventable_accidents=(
              "preventable_flag",
              lambda x: (x == True).sum(),
          ),
      )
      .reset_index()
  )

  return pd.merge(
      driver_perf, driver_safety, on="driver_id", how="left"
  ).fillna({"total_incidents": 0, "preventable_accidents": 0})


def analyze_route_profitability(
    routes: pd.DataFrame, loads: pd.DataFrame
) -> pd.DataFrame:
  """Cross-references routes with loads to compute lane-level volumes and revenue."""
  load_route = pd.merge(loads, routes, on="route_id", how="inner")
  return (
      load_route.groupby(["route_id", "origin_city", "destination_city"])
      .agg(
          total_loads=("load_id", "count"),
          total_revenue=("revenue", "sum"),
          avg_distance=("typical_distance_miles", "mean"),
      )
      .reset_index()
  )

def analyze_fleet_utilization(truck_util: pd.DataFrame) -> pd.DataFrame:
    """Evaluates asset performance, mileage, and revenue per asset."""
    if truck_util is None or truck_util.empty:
        return pd.DataFrame()

    # Ensure all aggregated columns are strictly numeric to prevent datetime/object summation errors
    numeric_cols = ["utilization_rate", "total_miles", "total_revenue", "downtime_hours"]
    for col in numeric_cols:
        if col in truck_util.columns:
            truck_util[col] = pd.to_numeric(truck_util[col], errors="coerce").fillna(0)

    # Build aggregation mappings dynamically based on available columns
    agg_dict = {}
    if "utilization_rate" in truck_util.columns:
        agg_dict["mean_utilization"] = ("utilization_rate", "mean")
    if "total_miles" in truck_util.columns:
        agg_dict["total_miles"] = ("total_miles", "sum")
    if "total_revenue" in truck_util.columns:
        agg_dict["total_revenue"] = ("total_revenue", "sum")
    if "downtime_hours" in truck_util.columns:
        agg_dict["total_downtime_hours"] = ("downtime_hours", "sum")

    if not agg_dict or "truck_id" not in truck_util.columns:
        return pd.DataFrame()

    fleet_util = (
        truck_util.groupby("truck_id")
        .agg(**agg_dict)
        .reset_index()
    )

    if "total_revenue" in fleet_util.columns and "total_miles" in fleet_util.columns:
        fleet_util["revenue_per_mile"] = (
            fleet_util["total_revenue"] / fleet_util["total_miles"].replace(0, pd.NA)
        ).fillna(0)

    return fleet_util


def analyze_maintenance(
    maintenance: pd.DataFrame, fleet_util: pd.DataFrame
) -> pd.DataFrame:
    """Correlates maintenance costs and downtime with mileage to compute Cost Per Mile."""
    if maintenance is None or maintenance.empty or fleet_util is None or fleet_util.empty:
        return pd.DataFrame()

    maint_df = maintenance.copy()

    # Force numeric conversion to fix datetime type mismatches
    numeric_cols = ["total_cost", "downtime_hours"]
    for col in numeric_cols:
        if col in maint_df.columns:
            maint_df[col] = pd.to_numeric(maint_df[col], errors="coerce").fillna(0)

    # Build aggregation dictionary dynamically
    agg_dict = {}
    if "total_cost" in maint_df.columns:
        agg_dict["total_maintenance_cost"] = ("total_cost", "sum")
    if "downtime_hours" in maint_df.columns:
        agg_dict["total_downtime_hours"] = ("downtime_hours", "sum")
    if "maintenance_id" in maint_df.columns:
        agg_dict["maintenance_events"] = ("maintenance_id", "count")

    if not agg_dict or "truck_id" not in maint_df.columns:
        return pd.DataFrame()

    truck_maint = maint_df.groupby("truck_id").agg(**agg_dict).reset_index()

    # Prepare fleet_util with numeric total_miles
    fleet_df = fleet_util.copy()
    if "total_miles" in fleet_df.columns:
        fleet_df["total_miles"] = pd.to_numeric(fleet_df["total_miles"], errors="coerce").fillna(0)
    else:
        fleet_df["total_miles"] = 0

    maintenance_analysis = pd.merge(
        truck_maint,
        fleet_df[["truck_id", "total_miles"]],
        on="truck_id",
        how="inner",
    )

    if "total_maintenance_cost" in maintenance_analysis.columns and "total_miles" in maintenance_analysis.columns:
        maintenance_analysis["cost_per_mile"] = (
            maintenance_analysis["total_maintenance_cost"]
            / maintenance_analysis["total_miles"].replace(0, pd.NA)
        ).fillna(0)

    return maintenance_analysis

def analyze_fuel_efficiency(
    fuel: pd.DataFrame, trips: pd.DataFrame
) -> pd.DataFrame:
    """Compares native trip fuel logs against transactional fuel purchases."""
    if fuel is None or fuel.empty or trips is None or trips.empty:
        return pd.DataFrame()

    fuel_df = fuel.copy()
    # Guard against datetime casting errors on numeric columns
    for col in ["gallons", "total_cost"]:
        if col in fuel_df.columns:
            fuel_df[col] = pd.to_numeric(fuel_df[col], errors="coerce").fillna(0)

    trip_fuel_summary = (
        fuel_df.groupby("trip_id")
        .agg(
            purchased_gallons=("gallons", "sum"),
            total_fuel_spend=("total_cost", "sum"),
        )
        .reset_index()
    )

    fuel_audit = pd.merge(trips, trip_fuel_summary, on="trip_id", how="inner")
    
    # Safe column fallbacks for distance and mpg
    dist_col = "actual_distance_miles" if "actual_distance_miles" in fuel_audit.columns else ("distance_miles" if "distance_miles" in fuel_audit.columns else "distance")
    avg_mpg_col = "average_mpg" if "average_mpg" in fuel_audit.columns else None

    if dist_col in fuel_audit.columns:
        fuel_audit["calculated_mpg"] = (
            pd.to_numeric(fuel_audit[dist_col], errors="coerce").fillna(0) / 
            fuel_audit["purchased_gallons"].replace(0, pd.NA)
        ).fillna(0)
    else:
        fuel_audit["calculated_mpg"] = 0.0

    if avg_mpg_col in fuel_audit.columns:
        fuel_audit["mpg_variance"] = (
            pd.to_numeric(fuel_audit[avg_mpg_col], errors="coerce").fillna(0) - fuel_audit["calculated_mpg"]
        )
    else:
        fuel_audit["mpg_variance"] = 0.0

    return fuel_audit


def analyze_customer_performance(
    loads: pd.DataFrame,
    customers_csv: pd.DataFrame,
    delivery_events: pd.DataFrame,
) -> pd.DataFrame:
    """Tracks realized revenue versus annual potential and SLA compliance per customer."""
    if loads is None or loads.empty or customers_csv is None or customers_csv.empty:
        return pd.DataFrame()

    customer_loads = pd.merge(loads, customers_csv, on="customer_id", how="inner")
    
    # Coerce numeric columns
    for col in ["annual_revenue_potential", "revenue"]:
        if col in customer_loads.columns:
            customer_loads[col] = pd.to_numeric(customer_loads[col], errors="coerce").fillna(0)

    customer_revenue = (
        customer_loads.groupby(
            ["customer_id", "customer_name", "annual_revenue_potential"]
        )
        .agg(realized_revenue=("revenue", "sum"), total_loads=("load_id", "count"))
        .reset_index()
    )

    if delivery_events is not None and not delivery_events.empty:
        deliv_df = delivery_events.copy()
        for col in ["on_time_flag", "detention_minutes"]:
            if col in deliv_df.columns:
                deliv_df[col] = pd.to_numeric(deliv_df[col], errors="coerce").fillna(0)

        sla_summary = (
            deliv_df.groupby("load_id")
            .agg(
                on_time_status=("on_time_flag", "mean"),
                total_detention_mins=("detention_minutes", "sum"),
            )
            .reset_index()
        )

        loads_sla = pd.merge(loads[["load_id", "customer_id"]], sla_summary, on="load_id", how="left")
        cust_sla = loads_sla.groupby("customer_id").agg(
            avg_on_time_rate=("on_time_status", "mean"),
            total_detention_mins=("total_detention_mins", "sum")
        ).reset_index()

        return pd.merge(customer_revenue, cust_sla, on="customer_id", how="left")
    
    return customer_revenue


def analyze_safety_metrics(safety: pd.DataFrame) -> pd.DataFrame:
    """Computes total financial impact and preventable accident ratios per driver."""
    if safety is None or safety.empty:
        return pd.DataFrame()

    safety_df = safety.copy()
    for col in ["vehicle_damage_cost", "cargo_damage_cost", "claim_amount", "preventable_flag"]:
        if col in safety_df.columns:
            safety_df[col] = pd.to_numeric(safety_df[col], errors="coerce").fillna(0)

    safety_df["total_incident_cost"] = (
        safety_df.get("vehicle_damage_cost", 0)
        .add(safety_df.get("cargo_damage_cost", 0))
        .add(safety_df.get("claim_amount", 0))
    )

    agg_dict = {
        "total_incidents": ("incident_id", "count") if "incident_id" in safety_df.columns else ("driver_id", "count"),
        "total_financial_loss": ("total_incident_cost", "sum"),
    }
    if "preventable_flag" in safety_df.columns:
        agg_dict["preventable_ratio"] = ("preventable_flag", "mean")

    return (
        safety_df.groupby("driver_id")
        .agg(**agg_dict)
        .reset_index()
    )


def analyze_seasonal_patterns(loads: pd.DataFrame) -> pd.DataFrame:
    """Extracts temporal markers to map volume surges and rate fluctuations."""
    if loads is None or loads.empty:
        return pd.DataFrame()

    loads_df = loads.copy()
    if "load_date" in loads_df.columns:
        loads_df["load_date"] = pd.to_datetime(loads_df["load_date"], errors="coerce")
        loads_df["quarter"] = loads_df["load_date"].dt.to_period("Q").astype(str)
    else:
        loads_df["quarter"] = "Unknown"

    if "revenue" in loads_df.columns:
        loads_df["revenue"] = pd.to_numeric(loads_df["revenue"], errors="coerce").fillna(0)

    return (
        loads_df.groupby("quarter")
        .agg(
            total_load_volume=("load_id", "count") if "load_id" in loads_df.columns else ("quarter", "count"),
            total_revenue=("revenue", "sum"),
            avg_freight_rate=("revenue", "mean"),
        )
        .reset_index()
    )