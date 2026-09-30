"""
Plotting styles and color definitions for charts.
"""

import plotly.io as pio
import plotly.graph_objects as go
import matplotlib.pyplot as plt

COLORS = {
    "background": "#0f172a",
    "card": "#1e293b",
    "text": "#f8fafc",
    "muted": "#94a3b8",
    "grid": "#334155",
    "hpc_cyan": "#06b6d4",
    "phone_purple": "#8b5cf6",
    "iot_green": "#10b981",
    "auto_amber": "#f59e0b",
    "capex_rose": "#f43f5e",
    "margin_emerald": "#34d399",
}

# Dark theme template for Plotly
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
    """Applies dark styling to Matplotlib figures."""
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
