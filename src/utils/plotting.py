"""
Styling and plotting utilities for TSMC Institutional Research.
Provides high-contrast, publication-grade dark themes for Plotly and Matplotlib.
"""

import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt

# Color Palette: Institutional Semiconductor Theme
COLORS = {
    "background": "#0f172a",       # Slate 900
    "card": "#1e293b",             # Slate 800
    "text": "#f8fafc",             # Slate 50
    "muted": "#94a3b8",            # Slate 400
    "grid": "#334155",             # Slate 700
    "hpc_cyan": "#06b6d4",         # Cyan 500 (AI/HPC)
    "phone_purple": "#8b5cf6",     # Violet 500 (Smartphone)
    "iot_green": "#10b981",        # Emerald 500 (IoT)
    "auto_amber": "#f59e0b",       # Amber 500 (Automotive)
    "capex_rose": "#f43f5e",       # Rose 500 (CapEx)
    "margin_emerald": "#34d399",   # Emerald 400 (Margin)
}

# Define custom Plotly dark template
tsmc_plotly_template = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=COLORS["background"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"], family="Inter, -apple-system, sans-serif", size=12),
        xaxis=dict(
            gridcolor=COLORS["grid"],
            zerolinecolor=COLORS["grid"],
            showline=True,
            linecolor=COLORS["grid"],
        ),
        yaxis=dict(
            gridcolor=COLORS["grid"],
            zerolinecolor=COLORS["grid"],
            showline=True,
            linecolor=COLORS["grid"],
        ),
        legend=dict(
            bgcolor="rgba(30, 41, 59, 0.7)",
            bordercolor=COLORS["grid"],
            borderwidth=1,
            font=dict(color=COLORS["text"]),
        ),
        hoverlabel=dict(
            bgcolor=COLORS["card"],
            font_size=12,
            font_family="Inter, sans-serif",
        ),
    )
)

pio.templates["tsmc_dark"] = tsmc_plotly_template
pio.templates.default = "tsmc_dark"


def set_matplotlib_style():
    """Sets a sleek dark theme for Matplotlib/Seaborn figures."""
    plt.style.use("dark_background")
    plt.rcParams.update({
        "figure.facecolor": COLORS["background"],
        "axes.facecolor": COLORS["card"],
        "axes.edgecolor": COLORS["grid"],
        "axes.labelcolor": COLORS["text"],
        "text.color": COLORS["text"],
        "xtick.color": COLORS["muted"],
        "ytick.color": COLORS["muted"],
        "grid.color": COLORS["grid"],
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
        "font.family": "sans-serif",
    })
