"""
Project configuration and path management for TSMC Institutional Intelligence Lab.
"""
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATASET_DIR = PROJECT_ROOT / "dataset"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Database Configuration
DUCKDB_PATH = DATA_DIR / "tsmc_warehouse.duckdb"

# Tickers & Benchmark Configuration
TSMC_US_TICKER = "TSM"         # NYSE ADR (1 ADR = 5 Ordinary Shares)
TSMC_TW_TICKER = "2330.TW"     # Taiwan Stock Exchange
SEMI_BENCHMARK = "SOXX"        # iShares Semiconductor ETF
PEERS_DOWNSTREAM = ["NVDA", "AAPL", "AMD", "QCOM"]
PEERS_UPSTREAM = ["ASML", "AMAT", "LRCX"]
FX_TICKER = "TWD=X"            # USD to TWD Exchange Rate

# Ensure directories exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
