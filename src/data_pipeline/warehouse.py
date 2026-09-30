"""
DuckDB Relational Dimensional Warehouse for TSMC Telemetry.
Implements a Star Schema for high-speed analytical querying.
"""

import duckdb
import pandas as pd
from config.settings import DUCKDB_PATH, PROCESSED_DATA_DIR
from src.data_pipeline.historical_loader import load_platform_metrics, load_long_term_financial_history


def initialize_warehouse():
    """
    Creates and populates the DuckDB Star Schema from historical and platform datasets.
    """
    # Ensure source data is prepared
    hist_df = load_long_term_financial_history()
    platform_df = load_platform_metrics()

    # Connect to DuckDB database file
    conn = duckdb.connect(str(DUCKDB_PATH))

    print(f"Connecting to DuckDB at {DUCKDB_PATH}...")

    # 1. Dimension: dim_time
    time_df = hist_df[["period", "year", "quarter"]].drop_duplicates().copy()
    time_df.rename(columns={"period": "time_key"}, inplace=True)
    time_df["quarter_int"] = time_df["quarter"].str.replace("Q", "").astype(int)

    # 2. Dimension: dim_platform
    platform_names = platform_df["business_platform"].unique()
    dim_platform = pd.DataFrame({
        "platform_id": range(1, len(platform_names) + 1),
        "platform_name": platform_names,
        "platform_category": [
            "High-Growth Computing" if p == "HPC" else
            "Consumer Mobile" if p == "Smartphone" else
            "Industrial & Edge" if p in ["IOT", "Automotive"] else "Consumer / Other"
            for p in platform_names
        ]
    })

    # 3. Fact: fact_quarterly_financials (2012-2026)
    fact_financials = hist_df[[
        "period", "year", "quarter", "total_revenue_usd_m", 
        "total_capex_usd_m", "gross_margin_pct", "capex_intensity_pct", 
        "dominant_node", "core_driver"
    ]].copy()
    fact_financials.rename(columns={"period": "time_key"}, inplace=True)

    # 4. Fact: fact_platform_breakdown (2023-2026 granular telemetry)
    fact_platforms = platform_df[[
        "period", "business_platform", "platform_share_ptc", "platform_rev_usd_m"
    ]].copy()
    fact_platforms.rename(columns={
        "period": "time_key",
        "business_platform": "platform_name",
        "platform_share_ptc": "platform_share_pct",
        "platform_rev_usd_m": "platform_revenue_usd_m"
    }, inplace=True)

    # Register into DuckDB tables
    conn.execute("CREATE OR REPLACE TABLE dim_time AS SELECT * FROM time_df")
    conn.execute("CREATE OR REPLACE TABLE dim_platform AS SELECT * FROM dim_platform")
    conn.execute("CREATE OR REPLACE TABLE fact_quarterly_financials AS SELECT * FROM fact_financials")
    conn.execute("CREATE OR REPLACE TABLE fact_platform_breakdown AS SELECT * FROM fact_platforms")

    # Create analytical view: combined platform view with gross margin & capex context
    conn.execute("""
        CREATE OR REPLACE VIEW v_platform_financial_telemetry AS
        SELECT 
            f.time_key,
            t.year,
            t.quarter,
            p.platform_name,
            p.platform_category,
            f.platform_share_pct,
            f.platform_revenue_usd_m,
            qf.total_revenue_usd_m,
            qf.total_capex_usd_m,
            qf.gross_margin_pct,
            qf.dominant_node
        FROM fact_platform_breakdown f
        JOIN dim_time t ON f.time_key = t.time_key
        JOIN dim_platform p ON f.platform_name = p.platform_name
        JOIN fact_quarterly_financials qf ON f.time_key = qf.time_key
    """)

    # Verify tables
    tables = conn.execute("SHOW TABLES").fetchall()
    print("Warehouse tables and views created successfully:")
    for t in tables:
        count = conn.execute(f"SELECT count(*) FROM {t[0]}").fetchone()[0]
        print(f" - {t[0]}: {count} records")

    conn.close()
    print(f"DuckDB warehouse initialized at {DUCKDB_PATH}")


def query_warehouse(query_sql: str) -> pd.DataFrame:
    """Utility function to run SQL against the warehouse and return a Pandas DataFrame."""
    conn = duckdb.connect(str(DUCKDB_PATH), read_only=True)
    res_df = conn.execute(query_sql).df()
    conn.close()
    return res_df


if __name__ == "__main__":
    initialize_warehouse()
