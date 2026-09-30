"""
Exploratory data analysis of TSMC platform revenue transitions and margin trends.
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
    initialize_warehouse()
    
    financials_df = query_warehouse("""
        SELECT time_key, year, quarter, total_revenue_usd_m, total_capex_usd_m, 
               gross_margin_pct, capex_intensity_pct, dominant_node, core_driver
        FROM fact_quarterly_financials
        ORDER BY year, quarter
    """)
    
    platforms_df = query_warehouse("""
        SELECT time_key, year, quarter, platform_name, platform_category,
               platform_share_pct, platform_revenue_usd_m, gross_margin_pct
        FROM v_platform_financial_telemetry
        ORDER BY year, quarter, platform_share_pct DESC
    """)
    
    print(f"Loaded {len(financials_df)} quarterly records and {len(platforms_df)} platform records.")
    
    # Platform share shifts (HPC vs. Smartphone)
    hpc_df = platforms_df[platforms_df["platform_name"] == "HPC"].copy()
    phone_df = platforms_df[platforms_df["platform_name"] == "Smartphone"].copy()
    
    hpc_start = hpc_df.iloc[0]["platform_share_pct"]
    hpc_end = hpc_df.iloc[-1]["platform_share_pct"]
    phone_start = phone_df.iloc[0]["platform_share_pct"]
    phone_end = phone_df.iloc[-1]["platform_share_pct"]
    gm_start = hpc_df.iloc[0]["gross_margin_pct"]
    gm_end = hpc_df.iloc[-1]["gross_margin_pct"]
    
    print("\nPlatform Shifts (2023-2026):")
    print(f"  HPC Share   : {hpc_start:.1f}% -> {hpc_end:.1f}% (Δ {hpc_end - hpc_start:+.1f}%)")
    print(f"  Smartphone  : {phone_start:.1f}% -> {phone_end:.1f}% (Δ {phone_end - phone_start:+.1f}%)")
    print(f"  Gross Margin: {gm_start:.1f}% -> {gm_end:.1f}% (Δ {gm_end - gm_start:+.1f}% pts)")
    
    # Correlation between HPC revenue share and gross margin
    merged_hpc = pd.merge(
        hpc_df[["time_key", "platform_share_pct", "platform_revenue_usd_m"]],
        financials_df[["time_key", "gross_margin_pct", "total_capex_usd_m", "total_revenue_usd_m"]],
        on="time_key"
    )
    corr = merged_hpc[["platform_share_pct", "gross_margin_pct", "total_capex_usd_m", "total_revenue_usd_m"]].corr()
    print("\nCorrelation Matrix:")
    print(corr.round(3))
    
    # Chart 1: Platform Revenue Stack
    fig1 = px.area(
        platforms_df,
        x="time_key",
        y="platform_revenue_usd_m",
        color="platform_name",
        title="TSMC Quarterly Revenue by Platform ($M USD)",
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
    print(f"\nSaved {chart1_path.name}")
    
    # Chart 2: CapEx & Gross Margin
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
        title="TSMC 14-Year CapEx Allocation and Gross Margin (2012-2026)",
        xaxis_title="Quarter",
        legend=dict(x=0.01, y=0.99)
    )
    fig2.update_yaxes(title_text="CapEx ($M USD)", secondary_y=False)
    fig2.update_yaxes(title_text="Gross Margin (%)", secondary_y=True)
    
    chart2_path = PROCESSED_DATA_DIR / "chart2_14yr_capex_margin.html"
    fig2.write_html(str(chart2_path), include_plotlyjs="cdn")
    print(f"Saved {chart2_path.name}")


if __name__ == "__main__":
    run_eda()
