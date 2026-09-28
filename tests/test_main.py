from unittest.mock import patch
import pandas as pd
import pytest

from ts_academy_capstone.main import run_complete_logistics_pipeline


@patch("ts_academy_capstone.main.analyze_seasonal_patterns")
@patch("ts_academy_capstone.main.analyze_safety_metrics")
@patch("ts_academy_capstone.main.analyze_customer_performance")
@patch("ts_academy_capstone.main.analyze_fuel_efficiency")
@patch("ts_academy_capstone.main.analyze_maintenance")
@patch("ts_academy_capstone.main.analyze_fleet_utilization")
@patch("ts_academy_capstone.main.analyze_route_profitability")
@patch("ts_academy_capstone.main.analyze_driver_performance")
@patch("ts_academy_capstone.main.engineer_logistics_features")
@patch("ts_academy_capstone.main.validate_relational_integrity")
@patch("ts_academy_capstone.main.standardize_logistics_data")
@patch("ts_academy_capstone.main.load_logistics_data")
def test_run_complete_logistics_pipeline(
    mock_load,
    mock_standardize,
    mock_validate,
    mock_engineer,
    mock_driver,
    mock_route,
    mock_fleet,
    mock_maint,
    mock_fuel,
    mock_cust,
    mock_safety,
    mock_seasonal,
):
    """Tests that the main orchestrator script executes all pipeline phases in order
    and aggregates final outputs correctly.
    """
    # Mock all intermediate module return values with sample DataFrames
    mock_load.return_value = {"trips": pd.DataFrame({"trip_id": [1]})}
    mock_standardize.return_value = {"trips": pd.DataFrame({"trip_id": [1]})}
    mock_validate.return_value = {"trips": pd.DataFrame({"trip_id": [1]})}
    mock_engineer.return_value = {"trips": pd.DataFrame({"trip_id": [1]})}

    mock_seasonal.return_value = pd.DataFrame({"quarter": ["Q1"]})
    mock_safety.return_value = pd.DataFrame({"driver_id": [1]})
    mock_cust.return_value = pd.DataFrame({"customer_id": [10]})
    mock_fuel.return_value = pd.DataFrame({"trip_id": [1]})
    mock_maint.return_value = pd.DataFrame({"truck_id": [101]})
    mock_fleet.return_value = pd.DataFrame({"truck_id": [101]})
    mock_route.return_value = pd.DataFrame({"route_id": [1]})
    mock_driver.return_value = pd.DataFrame({"driver_id": [1]})

    # Run the orchestrator
    enriched, analytics = run_complete_logistics_pipeline("data/raw_data")

    # Assertions to verify proper execution and return shapes
    assert isinstance(enriched, dict)
    assert isinstance(analytics, dict)
    assert "driver_performance" in analytics
    assert "route_profitability" in analytics
    assert "seasonal_patterns" in analytics

    # Verify ingestion was called with the correct target directory
    mock_load.assert_called_once_with("data/raw_data")