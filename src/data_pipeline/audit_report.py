"""
Audits platform financial metrics against TSMC management report PDFs.
"""

import re
import sys
from pathlib import Path
import pandas as pd
import pypdf

# Add project root to sys.path when run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import PROJECT_ROOT, DATASET_DIR
from src.data_pipeline.historical_loader import load_platform_metrics

MANAGEMENT_REPORTS_DIR = PROJECT_ROOT / "Management_reports"


def extract_metrics_from_pdf(pdf_path: Path) -> dict:
    """Extracts gross margin and platform percentage breakdown from a PDF report."""
    reader = pypdf.PdfReader(str(pdf_path))
    full_text = ""
    for page in reader.pages[:3]:
        full_text += page.extract_text() + "\n"

    extracted = {"gross_margin": None, "platforms": {}}

    gm_match = re.search(r"Gross margin (?:was )?([0-9]+\.[0-9]+)%", full_text, re.IGNORECASE)
    if gm_match:
        extracted["gross_margin"] = float(gm_match.group(1))

    platform_patterns = {
        "HPC": r"(?:High Performance Computing|HPC)\s+([0-9]+)%",
        "Smartphone": r"Smartphone\s+([0-9]+)%",
        "IOT": r"(?:Internet of Things|IoT)\s+([0-9]+)%",
        "Automotive": r"Automotive\s+([0-9]+)%",
        "DCE": r"(?:Digital Consumer Electronics|DCE)\s+([0-9]+)%"
    }

    for plat, pattern in platform_patterns.items():
        m = re.search(pattern, full_text, re.IGNORECASE)
        if m:
            extracted["platforms"][plat] = float(m.group(1))

    return extracted


def audit_dataset_against_pdfs():
    """Reconciles platform CSV metrics with available quarterly PDF reports."""
    print("=" * 70)
    print("TSMC DATA AUDIT: PDF REPORTS VS CSV DATASET")
    print("=" * 70)

    df = load_platform_metrics()
    pdf_files = sorted(list(MANAGEMENT_REPORTS_DIR.glob("*Management*Report*.pdf")))

    if not pdf_files:
        print(f"No PDF reports found in {MANAGEMENT_REPORTS_DIR}")
        return

    audit_records = []
    total_checks = 0
    passed_checks = 0

    for pdf_path in pdf_files:
        match = re.search(r"([1-4])Q([0-9]{2})", pdf_path.name)
        if not match:
            continue

        quarter_num, year_short = match.groups()
        quarter_tag = f"Q{quarter_num}-20{year_short}"

        pdf_data = extract_metrics_from_pdf(pdf_path)
        csv_quarter = df[df["quater_year"] == quarter_tag]

        if csv_quarter.empty:
            continue

        # Verify gross margin
        csv_gm = csv_quarter["gross_margin_ptc"].iloc[0]
        pdf_gm = pdf_data["gross_margin"]

        total_checks += 1
        gm_match_status = "MATCH"
        if pdf_gm is not None:
            if abs(csv_gm - pdf_gm) < 0.1:
                passed_checks += 1
            else:
                gm_match_status = f"DIFF (CSV: {csv_gm}%, PDF: {pdf_gm}%)"
        else:
            gm_match_status = "PDF UNPARSED"

        # Verify platform revenue share
        for plat, pdf_pct in pdf_data["platforms"].items():
            csv_row = csv_quarter[csv_quarter["business_platform"] == plat]
            if not csv_row.empty:
                csv_pct = csv_row["platform_share_ptc"].iloc[0]
                total_checks += 1
                if abs(csv_pct - pdf_pct) < 1.0:
                    passed_checks += 1
                    status = "MATCH"
                else:
                    status = f"MISMATCH (CSV: {csv_pct}%, PDF: {pdf_pct}%)"

                audit_records.append({
                    "Quarter": quarter_tag,
                    "Metric": f"{plat} Share",
                    "CSV_Value": f"{csv_pct:.1f}%",
                    "PDF_Value": f"{pdf_pct:.1f}%",
                    "Status": status
                })

        audit_records.append({
            "Quarter": quarter_tag,
            "Metric": "Gross Margin",
            "CSV_Value": f"{csv_gm:.1f}%",
            "PDF_Value": f"{pdf_gm:.1f}%" if pdf_gm else "N/A",
            "Status": gm_match_status
        })

    audit_df = pd.DataFrame(audit_records)
    print(audit_df.to_string(index=False))

    accuracy_pct = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
    print("\n" + "=" * 70)
    print(f"AUDIT SUMMARY: {passed_checks}/{total_checks} checks passed ({accuracy_pct:.1f}% accuracy).")
    print("=" * 70)


if __name__ == "__main__":
    audit_dataset_against_pdfs()