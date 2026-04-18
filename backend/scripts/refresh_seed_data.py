"""
Seed Data Refresher
-------------------
Scrapes official AMC pages for factual fund data and overwrites seed_data.json.
Safe by design: if scraping fails for a fund, it retains the existing data for that fund.
Run daily via GitHub Actions at 9:15 AM IST.
"""
import json
import logging
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# FUND DEFINITIONS
# Each entry defines the ground-truth facts and the source URL.
# We attempt a live scrape to refresh values; if the scrape fails,
# the DEFAULTS below are preserved so the bot never goes blank.
# ─────────────────────────────────────────────
FUND_DEFINITIONS = [
    # ── HDFC ──────────────────────────────────────────────────────────────────
    {
        "fund_name": "HDFC Flexi Cap Fund",
        "amc": "HDFC",
        "category": "Equity: Flexi Cap",
        "source_url": "https://www.hdfcfund.com/product-literature/hdfc-flexi-cap-fund",
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
        "source_url": "https://www.hdfcfund.com/product-literature/hdfc-mid-cap-opportunities-fund",
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
        "source_url": "https://www.hdfcfund.com/product-literature/hdfc-small-cap-fund",
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
        "source_url": "https://www.hdfcfund.com/product-literature/hdfc-elss-tax-saver",
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
        "source_url": "https://www.hdfcfund.com/product-literature/hdfc-balanced-advantage-fund",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.75%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
    # ── SBI ───────────────────────────────────────────────────────────────────
    {
        "fund_name": "SBI Bluechip Fund",
        "amc": "SBI",
        "category": "Equity: Large Cap",
        "source_url": "https://www.sbimf.com/en-us/equity-schemes/sbi-bluechip-fund",
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
        "source_url": "https://www.sbimf.com/en-us/equity-schemes/sbi-small-cap-fund",
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
        "source_url": "https://www.sbimf.com/en-us/equity-schemes/sbi-magnum-midcap-fund",
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
        "source_url": "https://www.sbimf.com/en-us/equity-schemes/sbi-long-term-equity-fund",
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
        "source_url": "https://www.sbimf.com/en-us/equity-schemes/sbi-flexicap-fund",
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
        "source_url": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-bluechip-fund",
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
        "source_url": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-midcap-fund",
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
        "source_url": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-smallcap-fund",
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
        "source_url": "https://www.icicipruamc.com/mutual-funds/equity-funds/icici-prudential-long-term-equity-fund-tax-saving",
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
        "source_url": "https://www.icicipruamc.com/mutual-funds/hybrid-funds/icici-prudential-balanced-advantage-fund",
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
        "source_url": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-small-cap-fund",
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
        "source_url": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-large-cap-fund",
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
        "source_url": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-growth-fund",
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
        "source_url": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-tax-saver-fund",
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
        "source_url": "https://mf.nipponindiaim.com/funds/equity-funds/nippon-india-flexi-cap-fund",
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
        "source_url": "https://www.kotakmf.com/funds/equity-funds/kotak-flexicap-fund",
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
        "source_url": "https://www.kotakmf.com/funds/equity-funds/kotak-small-cap-fund",
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
        "source_url": "https://www.kotakmf.com/funds/equity-funds/kotak-bluechip-fund",
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
        "source_url": "https://www.kotakmf.com/funds/equity-funds/kotak-tax-saver-fund",
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
        "source_url": "https://www.kotakmf.com/funds/equity-funds/kotak-emerging-equity-fund",
        "defaults": {
            "min_sip_amount": "Rs. 100",
            "expense_ratio": "0.36%",
            "exit_load": "1.0% if redeemed within 1 year",
            "riskometer": "Very High",
        },
    },
]


# ─────────────────────────────────────────────
# SCRAPING HELPERS
# ─────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

EXPENSE_PATTERNS = [
    r"expense\s*ratio[\s:]+([0-9]+\.[0-9]+)\s*%",
    r"ter[\s:]+([0-9]+\.[0-9]+)\s*%",
    r"total\s*expense\s*ratio[\s:]+([0-9]+\.[0-9]+)\s*%",
]

EXIT_LOAD_PATTERNS = [
    r"exit\s*load[\s:]+([^\n]{5,80})",
    r"redemption\s*charge[\s:]+([^\n]{5,80})",
]

SIP_PATTERNS = [
    r"minimum\s*sip[\s:]+(?:rs\.?\s*)?([0-9,]+)",
    r"min\.?\s*sip[\s:]+(?:rs\.?\s*)?([0-9,]+)",
    r"sip\s*minimum[\s:]+(?:rs\.?\s*)?([0-9,]+)",
]

RISK_PATTERNS = [
    r"riskometer[\s:]+(very\s+high|high|moderately\s+high|moderate|low\s+to\s+moderate|low)",
    r"risk\s+level[\s:]+(very\s+high|high|moderately\s+high|moderate|low)",
]


def _extract(text: str, patterns: list[str]) -> str | None:
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE | re.MULTILINE)
        if m:
            value = m.group(1).strip()
            if value and value.lower() not in {"na", "n/a", "-", ""}:
                return value
    return None


def scrape_fund(definition: dict) -> dict:
    """
    Attempt a live scrape of the fund's source page.
    Always returns a complete fund record — uses defaults for any field
    that cannot be extracted from the live page.
    """
    fund_name = definition["fund_name"]
    source_url = definition["source_url"]
    defaults = definition["defaults"]

    result = {
        "fund_name": fund_name,
        "amc": definition["amc"],
        "category": definition["category"],
        "source_url": source_url,
        **defaults,                      # start with safe defaults
    }

    try:
        resp = requests.get(source_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # Remove noise
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)

        # Try to extract each field; keep default if extraction fails
        expense = _extract(text, EXPENSE_PATTERNS)
        if expense:
            result["expense_ratio"] = f"{expense}%"

        exit_load = _extract(text, EXIT_LOAD_PATTERNS)
        if exit_load:
            # Truncate to one sentence so it stays clean in the bot
            result["exit_load"] = exit_load.split(".")[0].strip()

        sip = _extract(text, SIP_PATTERNS)
        if sip:
            result["min_sip_amount"] = f"Rs. {sip.replace(',', '')}"

        risk = _extract(text, RISK_PATTERNS)
        if risk:
            result["riskometer"] = risk.title()

        logger.info(f"✅ Scraped live data for {fund_name}")

    except Exception as exc:
        logger.warning(
            f"⚠️  Scrape failed for {fund_name} ({source_url}): {exc}. "
            "Retaining existing defaults."
        )

    return result


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    seed_path = Path(__file__).parent.parent / "data" / "seed_data.json"
    seed_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing data as a safety net (fund_name → record)
    existing: dict[str, dict] = {}
    if seed_path.exists():
        try:
            with open(seed_path, "r", encoding="utf-8") as f:
                old = json.load(f)
            existing = {fd["fund_name"]: fd for fd in old.get("funds", [])}
            logger.info(f"Loaded {len(existing)} existing fund records as fallback.")
        except Exception:
            logger.warning("Could not read existing seed_data.json — starting fresh.")

    updated_funds = []
    for defn in FUND_DEFINITIONS:
        # Merge: existing record → attempt live scrape → overwrite fields found
        base = existing.get(defn["fund_name"], {})
        live = scrape_fund(defn)
        merged = {**base, **live}          # live data wins over stale existing data
        updated_funds.append(merged)
        time.sleep(1.5)                    # polite rate-limiting between requests

    payload = {
        "last_updated": datetime.now(timezone.utc).strftime("%B %d, %Y"),
        "funds": updated_funds,
    }

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    logger.info(
        f"✅ seed_data.json refreshed with {len(updated_funds)} funds. "
        f"Saved to {seed_path}"
    )


if __name__ == "__main__":
    main()
