"""
Unit and integration tests for TSMC data pipeline and warehouse.
"""

import pytest
import pandas as pd
from config.settings import DUCKDB_PATH, PROCESSED_DATA_DIR
from src.data_pipeline.historical_loader import load_platform_metrics, load_long_term_financial_history
from src.data_pipeline.warehouse import initialize_warehouse, query_warehouse


def test_platform_metrics_cleaning():
    """Verify that platform metrics are cleaned without trailing commas or invalid types."""
    df = load_platform_metrics()
    assert not df.empty, "Platform metrics DataFrame should not be empty"
    assert "platform_rev_usd_m" in df.columns
    assert "gross_margin_ptc" in df.columns
    assert pd.api.types.is_numeric_dtype(df["platform_rev_usd_m"])
    assert pd.api.types.is_numeric_dtype(df["gross_margin_ptc"])
    assert df["gross_margin_ptc"].min() > 0, "Gross margin should be positive"


def test_long_term_historical_series():
    """Verify 14-year historical coverage (2012 to 2026)."""
    df = load_long_term_financial_history()
    assert len(df) >= 56, f"Expected at least 56 quarters, got {len(df)}"
    assert df["year"].min() == 2012
    assert df["year"].max() >= 2026
    assert (df["total_revenue_usd_m"] > 0).all()
    assert (df["total_capex_usd_m"] > 0).all()


def test_duckdb_warehouse_schema():
    """Verify that DuckDB Star Schema and analytical views build accurately."""
    initialize_warehouse()
    assert DUCKDB_PATH.exists(), "DuckDB file should exist on disk"

    # Query fact table
    qf = query_warehouse("SELECT count(*) as cnt FROM fact_quarterly_financials")
    assert qf["cnt"].iloc[0] >= 56

    # Query analytical view
    view_df = query_warehouse("""
        SELECT time_key, platform_name, platform_share_pct, gross_margin_pct
        FROM v_platform_financial_telemetry
        WHERE platform_name = 'HPC'
        ORDER BY time_key DESC
        LIMIT 5
    """)
    assert not view_df.empty
    assert "gross_margin_pct" in view_df.columns
