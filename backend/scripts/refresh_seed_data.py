"""
Seed Data Refresher with AMFI NAV Integration
----------------------------------------------
- Fetches daily NAV from api.mfapi.in (official AMFI data) for all 25 funds.
- Static fields (expense ratio, exit load, min SIP) use verified defaults.
  These fields change at most annually and are manually verified.
- Safe by design: if NAV fetch fails, previous value is preserved.
- Run daily via GitHub Actions at 9:15 AM IST.
"""
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

AMFI_NAV_API = "https://api.mfapi.in/mf/{scheme_code}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
    )
}

# ─────────────────────────────────────────────────────────────────────────────
# FUND MASTER TABLE
# amfi_scheme_code: Verified scheme code from api.mfapi.in (Direct Growth plan)
# source_url: The canonical AMC/AMFI page cited in answers
# ─────────────────────────────────────────────────────────────────────────────
FUND_DEFINITIONS = [
    # ── HDFC ─────────────────────────────────────────────────────────────────
    {
        "fund_name": "HDFC Flexi Cap Fund",
        "amc": "HDFC",
        "category": "Equity: Flexi Cap",
        "amfi_scheme_code": 118955,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.92%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "HDFC Mid-Cap Opportunities Fund",
        "amc": "HDFC",
        "category": "Equity: Mid Cap",
        "amfi_scheme_code": 118957,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.85%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "HDFC Small Cap Fund",
        "amc": "HDFC",
        "category": "Equity: Small Cap",
        "amfi_scheme_code": 118960,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.60%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "HDFC ELSS Tax Saver Fund",
        "amc": "HDFC",
        "category": "Equity: ELSS",
        "amfi_scheme_code": 118956,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "1.05%",
            "exit_load": "Nil (3-year lock-in applies)",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "HDFC Balanced Advantage Fund",
        "amc": "HDFC",
        "category": "Hybrid: Balanced Advantage",
        "amfi_scheme_code": 118958,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.75%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    # ── SBI ──────────────────────────────────────────────────────────────────
    {
        "fund_name": "SBI Bluechip Fund",
        "amc": "SBI",
        "category": "Equity: Large Cap",
        "amfi_scheme_code": 119598,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "0.88%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "SBI Small Cap Fund",
        "amc": "SBI",
        "category": "Equity: Small Cap",
        "amfi_scheme_code": 125497,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "0.68%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "SBI Magnum Midcap Fund",
        "amc": "SBI",
        "category": "Equity: Mid Cap",
        "amfi_scheme_code": 120488,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "0.89%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "SBI Long Term Equity Fund",
        "amc": "SBI",
        "category": "Equity: ELSS",
        "amfi_scheme_code": 119769,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "1.00%",
            "exit_load": "Nil (3-year lock-in applies)",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "SBI Flexicap Fund",
        "amc": "SBI",
        "category": "Equity: Flexi Cap",
        "amfi_scheme_code": 127042,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "0.84%",
            "exit_load": "0.5% if redeemed within 30 days",
            "riskometer": "Very High",
        },
    },
    # ── ICICI ─────────────────────────────────────────────────────────────────
    {
        "fund_name": "ICICI Prudential Bluechip Fund",
        "amc": "ICICI",
        "category": "Equity: Large Cap",
        "amfi_scheme_code": 120586,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.75%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "ICICI Prudential Midcap Fund",
        "amc": "ICICI",
        "category": "Equity: Mid Cap",
        "amfi_scheme_code": 120591,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.95%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "ICICI Prudential Smallcap Fund",
        "amc": "ICICI",
        "category": "Equity: Small Cap",
        "amfi_scheme_code": 120592,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.87%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "ICICI Prudential ELSS Tax Saver Fund",
        "amc": "ICICI",
        "category": "Equity: ELSS",
        "amfi_scheme_code": 120581,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "1.05%",
            "exit_load": "Nil (3-year lock-in applies)",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "ICICI Prudential Balanced Advantage Fund",
        "amc": "ICICI",
        "category": "Hybrid: Balanced Advantage",
        "amfi_scheme_code": 120578,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.76%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Moderately High",
        },
    },
    # ── NIPPON ────────────────────────────────────────────────────────────────
    {
        "fund_name": "Nippon India Small Cap Fund",
        "amc": "Nippon",
        "category": "Equity: Small Cap",
        "amfi_scheme_code": 118778,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.70%",
            "exit_load": "1.0% if redeemed within 1 month",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Nippon India Large Cap Fund",
        "amc": "Nippon",
        "category": "Equity: Large Cap",
        "amfi_scheme_code": 118825,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.81%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Nippon India Growth Fund",
        "amc": "Nippon",
        "category": "Equity: Mid Cap",
        "amfi_scheme_code": 118831,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.98%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Nippon India Tax Saver Fund (ELSS)",
        "amc": "Nippon",
        "category": "Equity: ELSS",
        "amfi_scheme_code": 118836,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "1.10%",
            "exit_load": "Nil (3-year lock-in applies)",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Nippon India Flexi Cap Fund",
        "amc": "Nippon",
        "category": "Equity: Flexi Cap",
        "amfi_scheme_code": 125494,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.79%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    # ── KOTAK ─────────────────────────────────────────────────────────────────
    {
        "fund_name": "Kotak Flexicap Fund",
        "amc": "Kotak",
        "category": "Equity: Flexi Cap",
        "amfi_scheme_code": 120166,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.65%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Kotak Small Cap Fund",
        "amc": "Kotak",
        "category": "Equity: Small Cap",
        "amfi_scheme_code": 120827,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.52%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Kotak Bluechip Fund",
        "amc": "Kotak",
        "category": "Equity: Large Cap",
        "amfi_scheme_code": 120821,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.64%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Kotak ELSS Tax Saver Fund",
        "amc": "Kotak",
        "category": "Equity: ELSS",
        "amfi_scheme_code": 120825,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 500",
            "expense_ratio": "0.78%",
            "exit_load": "Nil (3-year lock-in applies)",
            "riskometer": "Very High",
        },
    },
    {
        "fund_name": "Kotak Emerging Equity Fund",
        "amc": "Kotak",
        "category": "Equity: Mid Cap",
        "amfi_scheme_code": 120823,
        "source_url": "https://www.amfiindia.com/nav-history-download",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.36%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
]


def fetch_nav(scheme_code: int) -> str | None:
    """Fetch latest NAV from api.mfapi.in (official AMFI data source)."""
    try:
        url = AMFI_NAV_API.format(scheme_code=scheme_code)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # Response: {"meta": {...}, "data": [{"date": "...", "nav": "..."}, ...]}
        nav_records = data.get("data", [])
        if nav_records:
            latest = nav_records[0]  # Most recent is first
            nav_value = latest.get("nav", "")
            nav_date = latest.get("date", "")
            if nav_value:
                return f"Rs. {float(nav_value):.2f} (as of {nav_date})"
        return None
    except Exception as exc:
        logger.warning(f"NAV fetch failed for scheme {scheme_code}: {exc}")
        return None


def main():
    seed_path = Path(__file__).parent.parent / "data" / "seed_data.json"
    seed_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing records as safety fallback
    existing: dict[str, dict] = {}
    if seed_path.exists():
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                old = json.load(f)
            existing = {fd["fund_name"]: fd for fd in old.get("funds", [])}
            logger.info(f"Loaded {len(existing)} existing records as fallback.")
        except Exception:
            logger.warning("Could not read existing seed_data.json — starting fresh.")

    updated_funds = []
    nav_success = 0
    nav_failed = 0

    for defn in FUND_DEFINITIONS:
        fund_name = defn["fund_name"]
        scheme_code = defn["amfi_scheme_code"]

        # Start with defaults, override with any previously scraped data
        record = {
            "fund_name": fund_name,
            "amc": defn["amc"],
            "category": defn["category"],
            "source_url": defn["source_url"],
            **defn["defaults"],
        }

        # Restore any previously fetched data that isn't in defaults
        if fund_name in existing:
            for key in ("nav", "aum", "benchmark", "fund_manager", "inception_date"):
                if key in existing[fund_name]:
                    record[key] = existing[fund_name][key]

        # Fetch fresh NAV from AMFI
        nav = fetch_nav(scheme_code)
        if nav:
            record["nav"] = nav
            nav_success += 1
            logger.info(f"✅ NAV updated for {fund_name}: {nav}")
        else:
            nav_failed += 1
            logger.warning(f"⚠️  NAV unavailable for {fund_name} (scheme {scheme_code}) — keeping previous value.")

        updated_funds.append(record)
        time.sleep(0.5)  # polite rate-limiting

    payload = {
        "last_updated": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "data_source": "NAV: api.mfapi.in (AMFI). Static fields: verified AMC disclosures.",
        "funds": updated_funds,
    }

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(
        f"✅ seed_data.json refreshed — {len(updated_funds)} funds | "
        f"NAV: {nav_success} live, {nav_failed} fallback."
    )


if __name__ == "__main__":
    main()
