import pandas as pd
import pytest
from  ts_academy_capstone.features_aggregate import (
    analyze_customer_performance,
    analyze_driver_performance,
    analyze_fleet_utilization,
    analyze_fuel_efficiency,
    analyze_maintenance,
    analyze_route_profitability,
    analyze_safety_metrics,
    analyze_seasonal_patterns,
)


def test_analyze_driver_performance():
  monthly = pd.DataFrame({
      "driver_id": [1],
      "total_revenue": [5000],
      "total_miles": [2000],
      "average_mpg": [6.5],
      "on_time_delivery_rate": [0.95],
  })
  safety = pd.DataFrame(
      {"driver_id": [1], "incident_id": [1], "preventable_flag": [True]}
  )
  res = analyze_driver_performance(monthly, safety)
  assert res["revenue_per_mile"].iloc[0] == 2.5


def test_analyze_route_profitability():
  routes = pd.DataFrame({
      "route_id": [1],
      "origin_city": ["NY"],
      "destination_city": ["CHI"],
      "typical_distance_miles": [800],
  })
  loads = pd.DataFrame({"load_id": [10], "route_id": [1], "revenue": [3000]})
  res = analyze_route_profitability(routes, loads)
  assert res["total_revenue"].iloc[0] == 3000


def test_analyze_fleet_utilization():
  util = pd.DataFrame({
      "truck_id": [101],
      "utilization_rate": [0.85],
      "total_miles": [10000],
      "total_revenue": [25000],
      "downtime_hours": [12],
  })
  res = analyze_fleet_utilization(util)
  assert res["revenue_per_mile"].iloc[0] == 2.5


def test_analyze_maintenance(sample_maintenance_df):
  """Tests maintenance cost per mile leveraging conftest maintenance fixture."""
  util = pd.DataFrame({"truck_id": [101, 102], "total_miles": [10000, 12000]})
  res = analyze_maintenance(sample_maintenance_df, util)
  assert "cost_per_mile" in res.columns


def test_analyze_fuel_efficiency(sample_fuel_df, sample_trips_df):
  """Tests fuel efficiency calculations using conftest fuel and trip fixtures."""
  res = analyze_fuel_efficiency(sample_fuel_df, sample_trips_df)
  assert "calculated_mpg" in res.columns


def test_analyze_customer_performance():
  loads = pd.DataFrame({"load_id": [1], "customer_id": [10], "revenue": [1500]})
  customers = pd.DataFrame({
      "customer_id": [10],
      "customer_name": ["Acme"],
      "annual_revenue_potential": [50000],
  })
  events = pd.DataFrame(
      {"load_id": [1], "on_time_flag": [1], "detention_minutes": [15]}
  )
  res = analyze_customer_performance(loads, customers, events)
  assert res["realized_revenue"].iloc[0] == 1500


def test_analyze_safety_metrics(sample_safety_df):
  """Tests total financial loss metrics using conftest safety fixture."""
  res = analyze_safety_metrics(sample_safety_df)
  assert "total_financial_loss" in res.columns


def test_analyze_seasonal_patterns():
  loads = pd.DataFrame(
      {"load_id": [1], "load_date": ["2026-02-14"], "revenue": [2000]}
  )
  res = analyze_seasonal_patterns(loads)
  assert res["total_load_volume"].iloc[0] == 1