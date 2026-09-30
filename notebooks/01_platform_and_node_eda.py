"""
Exploratory Data Analysis: TSMC 14-Year Platform Supercycle & Node Dynamics.
Analyzes the structural transition from Smartphone dominance to AI/HPC dominance
and its direct mathematical link to Gross Margin expansion.
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config.settings import PROCESSED_DATA_DIR
from src.data_pipeline.warehouse import initialize_warehouse, query_warehouse
from src.utils.plotting import COLORS


def run_eda():
    print("--- TSMC Platform & Node Supercycle EDA ---")
    
    # 1. Initialize and query warehouse
    initialize_warehouse()
    
    # Query 14-year headline financial progression
    financials_df = query_warehouse("""
        SELECT time_key, year, quarter, total_revenue_usd_m, total_capex_usd_m, 
               gross_margin_pct, capex_intensity_pct, dominant_node, core_driver
        FROM fact_quarterly_financials
        ORDER BY year, quarter
    """)
    
    # Query 2023-2026 granular platform breakdown
    platforms_df = query_warehouse("""
        SELECT time_key, year, quarter, platform_name, platform_category,
               platform_share_pct, platform_revenue_usd_m, gross_margin_pct
        FROM v_platform_financial_telemetry
        ORDER BY year, quarter, platform_share_pct DESC
    """)
    
    print(f"\n14-Year Telemetry Loaded: {len(financials_df)} quarters.")
    print(f"Platform Telemetry Loaded: {len(platforms_df)} records.")
    
    # 2. Key Statistical Insights
    # HPC vs Smartphone Inflection Point
    hpc_df = platforms_df[platforms_df["platform_name"] == "HPC"].copy()
    phone_df = platforms_df[platforms_df["platform_name"] == "Smartphone"].copy()
    
    hpc_start_share = hpc_df.iloc[0]["platform_share_pct"]
    hpc_end_share = hpc_df.iloc[-1]["platform_share_pct"]
    
    phone_start_share = phone_df.iloc[0]["platform_share_pct"]
    phone_end_share = phone_df.iloc[-1]["platform_share_pct"]
    
    gm_start = hpc_df.iloc[0]["gross_margin_pct"]
    gm_end = hpc_df.iloc[-1]["gross_margin_pct"]
    
    print("\n--- Key Statistical Inflection Metrics ---")
    print(f"HPC Revenue Share: {hpc_start_share:.1f}% ({hpc_df.iloc[0]['time_key']}) -> {hpc_end_share:.1f}% ({hpc_df.iloc[-1]['time_key']}) [Δ +{hpc_end_share - hpc_start_share:.1f}%]")
    print(f"Smartphone Share : {phone_start_share:.1f}% ({phone_df.iloc[0]['time_key']}) -> {phone_end_share:.1f}% ({phone_df.iloc[-1]['time_key']}) [Δ {phone_end_share - phone_start_share:.1f}%]")
    print(f"Gross Margin     : {gm_start:.1f}% -> {gm_end:.1f}% [Δ +{gm_end - gm_start:.1f}% pts]")
    
    # Correlation between HPC revenue share and Gross Margin
    merged_hpc = pd.merge(
        hpc_df[["time_key", "platform_share_pct", "platform_revenue_usd_m"]],
        financials_df[["time_key", "gross_margin_pct", "total_capex_usd_m", "total_revenue_usd_m"]],
        on="time_key"
    )
    corr_matrix = merged_hpc[["platform_share_pct", "gross_margin_pct", "total_capex_usd_m", "total_revenue_usd_m"]].corr()
    print("\n--- Correlation Matrix (2023-2026 AI Era) ---")
    print(corr_matrix.round(3))
    
    # 3. Generate Visual Artifacts
    # Chart 1: Platform Revenue Stacked Area Chart
    fig1 = px.area(
        platforms_df,
        x="time_key",
        y="platform_revenue_usd_m",
        color="platform_name",
        title="TSMC Quarterly Revenue by Platform ($M USD): The HPC Inflection",
        labels={"time_key": "Quarter", "platform_revenue_usd_m": "Revenue ($M USD)", "platform_name": "Platform"},
        color_discrete_map={
            "HPC": COLORS["hpc_cyan"],
            "Smartphone": COLORS["phone_purple"],
            "IOT": COLORS["iot_green"],
            "Automotive": COLORS["auto_amber"],
            "DCE": "#f97316",
            "Others": "#64748b"
        }
    )
    chart1_path = PROCESSED_DATA_DIR / "chart1_platform_revenue_stack.html"
    fig1.write_html(str(chart1_path), include_plotlyjs="cdn")
    print(f"\nSaved Chart 1 to: {chart1_path}")
    
    # Chart 2: 14-Year Gross Margin vs CapEx Intensity Dual-Axis
    fig2 = make_subplots(specs=[[{"secondary_y": True}]])
    fig2.add_trace(
        go.Bar(
            x=financials_df["time_key"],
            y=financials_df["total_capex_usd_m"],
            name="Quarterly CapEx ($M)",
            marker_color=COLORS["capex_rose"],
            opacity=0.6
        ),
        secondary_y=False
    )
    fig2.add_trace(
        go.Scatter(
            x=financials_df["time_key"],
            y=financials_df["gross_margin_pct"],
            name="Gross Margin (%)",
            line=dict(color=COLORS["margin_emerald"], width=3)
        ),
        secondary_y=True
    )
    fig2.update_layout(
        title="TSMC 14-Year Capital Allocation & Profitability Engine (2012-2026)",
        xaxis_title="Quarter",
        legend=dict(x=0.01, y=0.99)
    )
    fig2.update_yaxes(title_text="CapEx ($M USD)", secondary_y=False)
    fig2.update_yaxes(title_text="Gross Margin (%)", secondary_y=True)
    
    chart2_path = PROCESSED_DATA_DIR / "chart2_14yr_capex_margin.html"
    fig2.write_html(str(chart2_path), include_plotlyjs="cdn")
    print(f"Saved Chart 2 to: {chart2_path}")


if __name__ == "__main__":
    run_eda()
