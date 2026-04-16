# Mutual Fund FAQ Assistant - Architecture Document

## Table of Contents
1. [Data Sources & Scheme Selection](#1-data-sources--scheme-selection)
2. [System Overview](#2-system-overview)
3. [Data Pipeline Architecture](#3-data-pipeline-architecture)
4. [Component Architecture](#4-component-architecture)
5. [API Endpoints](#5-api-endpoints)
6. [Data Flow](#6-data-flow)
7. [Configuration](#7-configuration)
8. [Security & Compliance](#8-security--compliance)
9. [Deployment](#9-deployment)
10. [Testing Strategy](#10-testing-strategy)
11. [Monitoring & Logging](#11-monitoring--logging)
12. [Future Enhancements](#12-future-enhancements)

---

## 1. Data Sources & Scheme Selection

### 1.1 Selected AMC & Schemes

#### 1.1.1 SBI Mutual Fund

| # | Fund Name | Category | Kuvera URL | Factsheet | SID | KIM |
|---|-----------|----------|------------|-----------|-----|-----|
| 1 | SBI Equity Hybrid Fund | Aggressive Hybrid | [Kuvera](https://kuvera.in/mutual-funds/fund/sbi-equity-hybrid-growth--SBD24G-GR) | [Factsheet](https://www.sbimf.com/en-us/investor-corner/factsheets) | [SID](https://www.sbimf.com/docs/default-source/default-document-library/sid/sbi-equity-hybrid-fund.pdf) | [KIM](https://www.sbimf.com/docs/default-source/default-document-library/kim/sbi-equity-hybrid-fund.pdf) |
| 2 | SBI Large Cap Fund | Bluechip Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/sbi-large-cap-growth--SBD103G-GR) | [Factsheet](https://www.sbimf.com/en-us/investor-corner/factsheets) | [SID](https://www.sbimf.com/docs/default-source/default-document-library/sid/sbi-large-cap-fund.pdf) | [KIM](https://www.sbimf.com/docs/default-source/default-document-library/kim/sbi-large-cap-fund.pdf) |
| 3 | SBI Contra Fund | Value/Contrarian Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/sbi-contra-growth--SBD036G-GR) | [Factsheet](https://www.sbimf.com/en-us/investor-corner/factsheets) | [SID](https://www.sbimf.com/docs/default-source/default-document-library/sid/sbi-contra-fund.pdf) | [KIM](https://www.sbimf.com/docs/default-source/default-document-library/kim/sbi-contra-fund.pdf) |
| 4 | SBI Small Cap Fund | High-growth Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/sbi-small-cap-growth--SBD346G-GR) | [Factsheet](https://www.sbimf.com/en-us/investor-corner/factsheets) | [SID](https://www.sbimf.com/docs/default-source/default-document-library/sid/sbi-small-cap-fund.pdf) | [KIM](https://www.sbimf.com/docs/default-source/default-document-library/kim/sbi-small-cap-fund.pdf) |
| 5 | SBI Nifty 50 ETF | Passive Index | [Kuvera](https://kuvera.in/stocks/sbi-nifty-50-etf) | [Factsheet](https://www.sbimf.com/en-us/investor-corner/factsheets) | [SID](https://www.sbimf.com/docs/default-source/default-document-library/sid/sbi-etf-nifty-50.pdf) | [KIM](https://www.sbimf.com/docs/default-source/default-document-library/kim/sbi-etf-nifty-50.pdf) |

**SBI MF Official Sources:**
- Factsheets: https://www.sbimf.com/en-us/investor-corner/factsheets
- Downloads: https://www.sbimf.com/en-us/downloads
- SID/KIM: https://www.sbimf.com/en-us/downloads/sid-and-kim

#### 1.1.2 ICICI Prudential Mutual Fund

| # | Fund Name | Category | Kuvera URL | Factsheet | SID | KIM |
|---|-----------|----------|------------|-----------|-----|-----|
| 1 | ICICI Pru Bluechip Fund | Large Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/icici-prudential-bluechip-growth--8042-GR) | [Factsheet](https://www.icicipruamc.com/downloads/factsheets) | [SID](https://www.icicipruamc.com/downloads/sid/icici-prudential-bluechip-fund-sid.pdf) | [KIM](https://www.icicipruamc.com/downloads/kim/icici-prudential-bluechip-fund-kim.pdf) |
| 2 | ICICI Pru Value Discovery Fund | Value Strategy | [Kuvera](https://kuvera.in/mutual-funds/fund/icici-prudential-value-discovery-growth--8176-GR) | [Factsheet](https://www.icicipruamc.com/downloads/factsheets) | [SID](https://www.icicipruamc.com/downloads/sid/icici-prudential-value-discovery-fund-sid.pdf) | [KIM](https://www.icicipruamc.com/downloads/kim/icici-prudential-value-discovery-fund-kim.pdf) |
| 3 | ICICI Pru Balanced Advantage Fund | Dynamic Asset Allocation | [Kuvera](https://kuvera.in/mutual-funds/fund/icici-prudential-balanced-advantage-growth--8180-GR) | [Factsheet](https://www.icicipruamc.com/downloads/factsheets) | [SID](https://www.icicipruamc.com/downloads/sid/icici-prudential-balanced-advantage-fund-sid.pdf) | [KIM](https://www.icicipruamc.com/downloads/kim/icici-prudential-balanced-advantage-fund-kim.pdf) |
| 4 | ICICI Pru Multi-Asset Fund | Hybrid (Equity/Debt/Gold) | [Kuvera](https://kuvera.in/mutual-funds/fund/icici-prudential-multi-asset-growth--8004-GR) | [Factsheet](https://www.icicipruamc.com/downloads/factsheets) | [SID](https://www.icicipruamc.com/downloads/sid/icici-prudential-multi-asset-fund-sid.pdf) | [KIM](https://www.icicipruamc.com/downloads/kim/icici-prudential-multi-asset-fund-kim.pdf) |
| 5 | ICICI Pru Equity & Debt Fund | Aggressive Hybrid | [Kuvera](https://kuvera.in/mutual-funds/fund/icici-prudential-equity-debt-growth--8017-GR) | [Factsheet](https://www.icicipruamc.com/downloads/factsheets) | [SID](https://www.icicipruamc.com/downloads/sid/icici-prudential-equity-debt-fund-sid.pdf) | [KIM](https://www.icicipruamc.com/downloads/kim/icici-prudential-equity-debt-fund-kim.pdf) |

**ICICI Prudential MF Official Sources:**
- Factsheets: https://www.icicipruamc.com/downloads/factsheets
- SID: https://www.icicipruamc.com/downloads/sid
- KIM: https://www.icicipruamc.com/downloads/kim
- Forms & Downloads: https://www.icicipruamc.com/about-us/forms-and-downloads

#### 1.1.3 HDFC Mutual Fund

| # | Fund Name | Category | Kuvera URL | Factsheet | SID | KIM |
|---|-----------|----------|------------|-----------|-----|-----|
| 1 | HDFC Balanced Advantage Fund | Dynamic Asset Allocation | [Kuvera](https://kuvera.in/mutual-funds/fund/hdfc-balanced-advantage-growth--GFGT-GR) | [Factsheet](https://www.hdfcfund.com/investor-corner/factsheets) | [SID](https://www.hdfcfund.com/statutory-disclosure/addendum/sid) | [KIM](https://www.hdfcfund.com/statutory-disclosure/addendum/kim) |
| 2 | HDFC Flexi Cap Fund | Multi-cap Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/hdfc-flexicap-growth--02T-GR) | [Factsheet](https://www.hdfcfund.com/investor-corner/factsheets) | [SID](https://www.hdfcfund.com/statutory-disclosure/addendum/sid) | [KIM](https://www.hdfcfund.com/statutory-disclosure/addendum/kim) |
| 3 | HDFC Mid-Cap Opportunities Fund | Mid Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/hdfc-mid-cap-opportunities-growth--MCOGT-GR) | [Factsheet](https://www.hdfcfund.com/investor-corner/factsheets) | [SID](https://www.hdfcfund.com/statutory-disclosure/addendum/sid) | [KIM](https://www.hdfcfund.com/statutory-disclosure/addendum/kim) |
| 4 | HDFC Small Cap Fund | Small Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/hdfc-small-cap-growth--HDACG1G-GR) | [Factsheet](https://www.hdfcfund.com/investor-corner/factsheets) | [SID](https://www.hdfcfund.com/statutory-disclosure/addendum/sid) | [KIM](https://www.hdfcfund.com/statutory-disclosure/addendum/kim) |
| 5 | HDFC Large Cap Fund | Top 100 Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/hdfc-large-cap-growth--44T-GR) | [Factsheet](https://www.hdfcfund.com/investor-corner/factsheets) | [SID](https://www.hdfcfund.com/statutory-disclosure/addendum/sid) | [KIM](https://www.hdfcfund.com/statutory-disclosure/addendum/kim) |

**HDFC MF Official Sources:**
- Factsheets: https://www.hdfcfund.com/investor-corner/factsheets
- SID: https://www.hdfcfund.com/statutory-disclosure/addendum/sid
- KIM: https://www.hdfcfund.com/statutory-disclosure/addendum/kim
- Downloads: https://www.hdfcfund.com/downloads

#### 1.1.4 Nippon India Mutual Fund

| # | Fund Name | Category | Kuvera URL | Factsheet | SID | KIM |
|---|-----------|----------|------------|-----------|-----|-----|
| 1 | Nippon India Small Cap Fund | Small Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/nippon-india-small-cap-growth--SCAG-GR) | [Factsheet](https://www.nipponindiamf.com/downloads/factsheets) | [SID](https://www.nipponindiamf.com/downloads/sid) | [KIM](https://www.nipponindiamf.com/downloads/kim) |
| 2 | Nippon India ETF Nifty 50 BeES | Passive Index | [Kuvera](https://kuvera.in/stocks/nippon-india-etf-nifty-50-bees) | [Factsheet](https://www.nipponindiamf.com/downloads/factsheets) | [SID](https://www.nipponindiamf.com/downloads/sid) | [KIM](https://www.nipponindiamf.com/downloads/kim) |
| 3 | Nippon India Multi Cap Fund | Multi-cap Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/nippon-india-multi-cap-growth--EOAG-GR) | [Factsheet](https://www.nipponindiamf.com/downloads/factsheets) | [SID](https://www.nipponindiamf.com/downloads/sid) | [KIM](https://www.nipponindiamf.com/downloads/kim) |
| 4 | Nippon India Growth Fund | Mid Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/nippon-india-growth-fund-growth--GFAG-GR) | [Factsheet](https://www.nipponindiamf.com/downloads/factsheets) | [SID](https://www.nipponindiamf.com/downloads/sid) | [KIM](https://www.nipponindiamf.com/downloads/kim) |
| 5 | Nippon India Large Cap Fund | Large Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/nippon-india-large-cap-growth--EAAG-GR) | [Factsheet](https://www.nipponindiamf.com/downloads/factsheets) | [SID](https://www.nipponindiamf.com/downloads/sid) | [KIM](https://www.nipponindiamf.com/downloads/kim) |

**Nippon India MF Official Sources:**
- Factsheets: https://www.nipponindiamf.com/downloads/factsheets
- SID: https://www.nipponindiamf.com/downloads/sid
- KIM: https://www.nipponindiamf.com/downloads/kim
- Downloads: https://www.nipponindiamf.com/downloads

#### 1.1.5 Kotak Mahindra Mutual Fund

| # | Fund Name | Category | Kuvera URL | Factsheet | SID | KIM |
|---|-----------|----------|------------|-----------|-----|-----|
| 1 | Kotak Equity Arbitrage Fund | Low-risk Arbitrage | [Kuvera](https://kuvera.in/mutual-funds/fund/kotak-equity-arbitrage-growth--KO179D-GR) | [Factsheet](https://www.kotakmf.com/docs/default-source/factsheets) | [SID](https://www.kotakmf.com/docs/default-source/sid) | [KIM](https://www.kotakmf.com/docs/default-source/kim) |
| 2 | Kotak Midcap Fund | Mid Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/kotak-emerging-equity-growth--KO123D-GR) | [Factsheet](https://www.kotakmf.com/docs/default-source/factsheets) | [SID](https://www.kotakmf.com/docs/default-source/sid) | [KIM](https://www.kotakmf.com/docs/default-source/kim) |
| 3 | Kotak Flexicap Fund | Multi-cap Equity | [Kuvera](https://kuvera.in/mutual-funds/fund/kotak-flexicap-growth--KO168D-GR) | [Factsheet](https://www.kotakmf.com/docs/default-source/factsheets) | [SID](https://www.kotakmf.com/docs/default-source/sid) | [KIM](https://www.kotakmf.com/docs/default-source/kim) |
| 4 | Kotak Emerging Equities Fund | Large & Mid Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/kotak-emerging-equity-growth--KO123D-GR) | [Factsheet](https://www.kotakmf.com/docs/default-source/factsheets) | [SID](https://www.kotakmf.com/docs/default-source/sid) | [KIM](https://www.kotakmf.com/docs/default-source/kim) |
| 5 | Kotak Small Cap Fund | Small Cap | [Kuvera](https://kuvera.in/mutual-funds/fund/kotak-small-cap-growth--KO104D-GR) | [Factsheet](https://www.kotakmf.com/docs/default-source/factsheets) | [SID](https://www.kotakmf.com/docs/default-source/sid) | [KIM](https://www.kotakmf.com/docs/default-source/kim) |

**Kotak Mahindra MF Official Sources:**
- Factsheets: https://www.kotakmf.com/docs/default-source/factsheets
- SID: https://www.kotakmf.com/docs/default-source/sid
- KIM: https://www.kotakmf.com/docs/default-source/kim
- Downloads: https://www.kotakmf.com/downloads

### 1.2 Regulatory & Industry Sources

**AMFI (Association of Mutual Funds in India):**
- Official Website: https://www.amfiindia.com/
- Scheme NAV: https://www.amfiindia.com/modules/SchemeInformation
- Investor Corner: https://www.amfiindia.com/investor-corner
- Mutual Fund FAQ: https://www.amfiindia.com/investor-corner/information-center/mutual-fund-faq

**SEBI (Securities and Exchange Board of India):**
- Official Website: https://www.sebi.gov.in/
- Mutual Funds Circulars: https://www.sebi.gov.in/legal/circulars/mutual-funds
- Investor Guidelines: https://www.sebi.gov.in/investor/protect-your-interests
- SID/KIM Guidelines: https://www.sebi.gov.in/legal/circulars/mutual-funds/guidelines-on-scheme-related-documents

---

## 2. System Overview

### 2.1 Architecture Style
- **Pattern**: Modular monolith with clear separation of concerns
- **UI**: Streamlit (Python-based, single codebase for UI + backend logic)
- **Communication**: In-process function calls (simplified architecture)
- **Deployment**: Cloud-hosted (Render) with managed vector storage (Chroma Cloud)

### 2.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           STREAMLIT APPLICATION                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    UI + Backend (Single Process)                     │    │
│  │                                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │    │
│  │  │   Chat      │  │   Quick     │  │  Document   │  │  Thread    │  │    │
│  │  │   Interface │  │   Actions   │  │  Status     │  │  History   │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │    │
│  │                                                                      │    │
│  └──────────────────────────────────┬───────────────────────────────────┘    │
└─────────────────────────────────────┼────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RAG SERVICE LAYER                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    RAGService (app/rag/rag_service.py)               │    │
│  │                                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐  │    │
│  │  │   Query     │  │   Vector    │  │   Context   │  │  Response  │  │    │
│  │  │   Classifier│  │   Search    │  │   Builder   │  │  Generator │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘  │    │
│  │                                                                      │    │
│  └──────────────────────────────────┬───────────────────────────────────┘    │
└─────────────────────────────────────┼────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   EMBEDDING SERVICE │  │   VECTOR STORE      │  │   LLM SERVICE       │
│   (BGE-small-en)    │  │   (Chroma Cloud)    │  │   (Groq API)        │
│                     │  │                     │  │                     │
│  ┌───────────────┐  │  │  ┌───────────────┐  │  │  ┌───────────────┐  │
│  │  BAAI/bge-    │  │  │  │  Chroma Cloud │  │  │  │  llama3-8b    │  │
│  │  small-en-v1.5│  │  │  │  (TryChroma)  │  │  │  │  or mixtral   │  │
│  │  (Local/Free) │  │  │  │  (Managed)    │  │  │  │  (Fast API)   │  │
│  └───────────────┘  │  │  └───────────────┘  │  │  └───────────────┘  │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATA SOURCES                                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   Kuvera.in     │  │   Chroma Cloud  │  │   Groq API      │              │
│  │   (Scraped)     │  │   (Persistent)  │  │   (LLM)         │              │
│  │                 │  │                 │  │                 │              │
│  │  25 Mutual Fund │  │  140+ Chunks    │  │  Fast Inference │              │
│  │  URLs           │  │  Embedded       │  │  $0 Cost        │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Pipeline Architecture

### 3.1 GitHub Actions Scheduler

**Schedule:** Daily at 9:15 AM IST (3:45 AM UTC)

```yaml
# .github/workflows/daily-data-update.yml
name: Daily Mutual Fund Data Update

on:
  schedule:
    - cron: '45 3 * * *'  # 3:45 AM UTC = 9:15 AM IST
  workflow_dispatch:  # Manual trigger support

jobs:
  update-data:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run document ingestion
        env:
          CHROMA_CLOUD_TOKEN: ${{ secrets.CHROMA_CLOUD_TOKEN }}
          CHROMA_CLOUD_TENANT: ${{ secrets.CHROMA_CLOUD_TENANT }}
          CHROMA_CLOUD_DATABASE: ${{ secrets.CHROMA_CLOUD_DATABASE }}
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: |
          python scripts/ingest_data.py
      
      - name: Verify ingestion
        run: |
          echo "Data ingestion completed at $(date)"
```

### 3.2 Scraping Service Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SCRAPING SERVICE                                     │
│              (Extract Relevant Data per Problem Statement)                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  URL SOURCES    │────▶│  SMART SCRAPER  │────▶│  DATA EXTRACTOR │
│                 │     │                 │     │                 │
│ • AMC Factsheets│     │ • URL Router    │     │ • Field Parser  │
│ • SID PDFs      │     │ • Format Detect │     │ • Validator     │
│ • KIM PDFs      │     │ • Retry Logic   │     │ • Normalizer    │
│ • AMFI/SEBI     │     │ • Rate Limiting │     │ • Deduplicator  │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌──────────────────────────┼──────────────────┐
                              │                          │                  │
                              ▼                          ▼                  ▼
                    ┌─────────────────┐      ┌─────────────────┐   ┌─────────────────┐
                    │  RELEVANT FIELDS│      │  EXTRACTED DATA │   │  OUTPUT STORE   │
                    │  (Per Problem   │      │  JSON Format    │   │  (Raw Docs)     │
                    │   Statement)    │      │                 │   │                 │
                    │                 │      │ • Fund Metadata │   │ • JSON Files    │
                    │ • Expense Ratio │      │ • Key Metrics   │   │ • PDF Cache     │
                    │ • Exit Load     │      │ • Risk Data     │   │ • Versioning    │
                    │ • Min SIP Amt   │      │ • Charges       │   │ • Audit Trail   │
                    │ • Lock-in Period│      │ • Dates         │   │                 │
                    │ • Riskometer    │      │ • Sources       │   │                 │
                    │ • Benchmark     │      │                 │   │                 │
                    │ • Tax Info      │      │                 │   │                 │
                    └─────────────────┘      └─────────────────┘   └─────────────────┘
```

#### 3.2.1 Relevant Data Fields (per Problem Statement)

Per the problem statement requirements, the scraper extracts only these factual fields:

| Field | Description | Source Location | Example |
|-------|-------------|-----------------|---------|
| **Expense Ratio** | Annual fund management charges | Factsheet, SID | "0.85%" |
| **Exit Load** | Charges for early redemption | Factsheet, KIM | "1% if redeemed within 12 months" |
| **Minimum SIP Amount** | Minimum investment for SIP | Factsheet, KIM | "Rs. 500" |
| **ELSS Lock-in Period** | Tax-saving scheme lock-in | SID, Factsheet | "3 years" |
| **Riskometer** | Risk classification | Factsheet, SID | "Very High" |
| **Benchmark Index** | Performance benchmark | Factsheet, SID | "NIFTY 50" |
| **Statement Download Process** | How to get account statements | AMC FAQ, Help pages | Step-by-step guide |
| **Tax Document Guide** | Capital gains statement info | AMC FAQ, Help pages | Download procedure |
| **Fund Category** | Scheme classification | SID, Factsheet | "Large Cap Fund" |
| **NAV** | Net Asset Value | AMFI, Factsheet | "Rs. 45.67" |
| **AUM** | Assets Under Management | Factsheet | "Rs. 10,000 Cr" |
| **Fund Manager** | Current fund manager(s) | Factsheet | "John Doe" |
| **Inception Date** | Fund launch date | SID | "01-Jan-2010" |

**Explicitly Excluded (Advisory Content):**
- Past performance returns
- Return comparisons between funds
- Investment recommendations
- "Best fund" rankings
- Future return projections

#### 3.2.2 Scraping Service Implementation

```python
# app/services/scraper.py
class MutualFundScraper:
    """
    Smart scraper that extracts only relevant factual data per problem statement.
    """
    
    RELEVANT_FIELDS = {
        # Core factual fields from problem statement
        "expense_ratio": ["expense ratio", "total expense ratio", "ter"],
        "exit_load": ["exit load", "redemption charge", "contingent deferred sales charge"],
        "min_sip_amount": ["minimum sip", "sip minimum", "min sip", "minimum investment"],
        "lock_in_period": ["lock in", "lock-in", "elss lock", "mandatory lock"],
        "riskometer": ["riskometer", "risk level", "risk grade", "risk profile"],
        "benchmark": ["benchmark", "underlying index", "comparison index"],
        "statement_download": ["statement download", "account statement", "capital gains statement"],
        "tax_document": ["tax certificate", "capital gains tax", "tax statement"],
        
        # Supporting metadata
        "fund_category": ["category", "scheme type", "fund type"],
        "nav": ["nav", "net asset value"],
        "aum": ["aum", "assets under management", "fund size"],
        "fund_manager": ["fund manager", "portfolio manager"],
        "inception_date": ["inception", "launch date", "commencement"]
    }
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.pdf_parser = PDFParser()
        self.html_parser = HTMLParser()
    
    def scrape_url(self, url: str, doc_type: str) -> ExtractedData:
        """
        Scrape a single URL and extract relevant fields only.
        """
        try:
            if url.endswith('.pdf'):
                return self._scrape_pdf(url, doc_type)
            else:
                return self._scrape_html(url, doc_type)
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ExtractedData(error=str(e), source_url=url)
    
    def _scrape_pdf(self, url: str, doc_type: str) -> ExtractedData:
        """
        Download and parse PDF documents (SID, KIM, Factsheets).
        """
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        # Save raw PDF
        pdf_path = self._save_raw_pdf(url, response.content)
        
        # Extract text
        text = self.pdf_parser.extract_text(response.content)
        
        # Parse based on document type
        if doc_type == "factsheet":
            data = self._parse_factsheet(text)
        elif doc_type == "sid":
            data = self._parse_sid(text)
        elif doc_type == "kim":
            data = self._parse_kim(text)
        else:
            data = self._parse_generic(text)
        
        return ExtractedData(
            source_url=url,
            doc_type=doc_type,
            raw_text=text,
            extracted_fields=data,
            pdf_path=pdf_path,
            scraped_at=datetime.utcnow().isoformat()
        )
    
    def _scrape_html(self, url: str, doc_type: str) -> ExtractedData:
        """
        Parse HTML pages (AMFI, SEBI, AMC FAQ pages).
        """
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        
        # Extract relevant fields
        data = self._parse_generic(text)
        
        return ExtractedData(
            source_url=url,
            doc_type=doc_type,
            raw_text=text,
            extracted_fields=data,
            scraped_at=datetime.utcnow().isoformat()
        )
    
    def _parse_factsheet(self, text: str) -> Dict:
        """
        Parse factsheet PDF for key metrics.
        """
        data = {}
        
        # Expense Ratio
        expense_match = re.search(r'expense ratio[:\s]+([\d.]+)%', text, re.IGNORECASE)
        if expense_match:
            data['expense_ratio'] = f"{expense_match.group(1)}%"
        
        # Exit Load
        exit_load_match = re.search(r'exit load[:\s]+([^\n]+)', text, re.IGNORECASE)
        if exit_load_match:
            data['exit_load'] = exit_load_match.group(1).strip()
        
        # Minimum SIP
        sip_match = re.search(r'minimum sip[:\s]+(?:rs\.?\s*)?([\d,]+)', text, re.IGNORECASE)
        if sip_match:
            data['min_sip_amount'] = f"Rs. {sip_match.group(1)}"
        
        # Riskometer
        risk_match = re.search(r'riskometer[:\s]+(\w+)', text, re.IGNORECASE)
        if risk_match:
            data['riskometer'] = risk_match.group(1)
        
        # Benchmark
        benchmark_match = re.search(r'benchmark[:\s]+([^\n]+)', text, re.IGNORECASE)
        if benchmark_match:
            data['benchmark'] = benchmark_match.group(1).strip()
        
        # NAV
        nav_match = re.search(r'nav[:\s]+(?:rs\.?\s*)?([\d.]+)', text, re.IGNORECASE)
        if nav_match:
            data['nav'] = f"Rs. {nav_match.group(1)}"
        
        # AUM
        aum_match = re.search(r'aum[:\s]+(?:rs\.?\s*)?([\d,]+\s*(?:cr|crore))', text, re.IGNORECASE)
        if aum_match:
            data['aum'] = f"Rs. {aum_match.group(1)}"
        
        return data
    
    def _parse_sid(self, text: str) -> Dict:
        """
        Parse SID for scheme information and terms.
        """
        data = {}
        
        # Lock-in period (especially for ELSS)
        lockin_match = re.search(r'lock[- ]?in period[:\s]+([^\n]+)', text, re.IGNORECASE)
        if lockin_match:
            data['lock_in_period'] = lockin_match.group(1).strip()
        
        # Fund Category
        category_match = re.search(r'scheme category[:\s]+([^\n]+)', text, re.IGNORECASE)
        if category_match:
            data['fund_category'] = category_match.group(1).strip()
        
        # Investment Objective
        objective_match = re.search(r'investment objective[:\s]+([^\n]+(?:\n[^\n]+){0,5})', text, re.IGNORECASE)
        if objective_match:
            data['investment_objective'] = objective_match.group(1).strip()
        
        return data
    
    def _parse_kim(self, text: str) -> Dict:
        """
        Parse KIM for key information and charges.
        """
        data = {}
        
        # Entry/Exit Load
        load_match = re.search(r'load[:\s]+([^\n]+(?:\n[^\n]+){0,2})', text, re.IGNORECASE)
        if load_match:
            data['load_structure'] = load_match.group(1).strip()
        
        # Minimum Investment
        min_inv_match = re.search(r'minimum (?:purchase|investment)[:\s]+([^\n]+)', text, re.IGNORECASE)
        if min_inv_match:
            data['min_investment'] = min_inv_match.group(1).strip()
        
        return data
    
    def _parse_generic(self, text: str) -> Dict:
        """
        Generic parser for any document type.
        """
        data = {}
        
        for field, keywords in self.RELEVANT_FIELDS.items():
            for keyword in keywords:
                pattern = rf'{keyword}[:\s]+([^\n]+)'
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    data[field] = match.group(1).strip()
                    break
        
        return data
```

#### 3.2.3 Scraping Configuration

```python
# app/config/scraper_config.py
SCRAPER_CONFIG = {
    # Request settings
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 2,
    "rate_limit_delay": 1,  # seconds between requests
    
    # Content filters
    "max_pdf_size_mb": 10,
    "allowed_domains": [
        "sbimf.com",
        "icicipruamc.com",
        "hdfcfund.com",
        "nipponindiamf.com",
        "kotakmf.com",
        "amfiindia.com",
        "sebi.gov.in"
    ],
    
    # Field extraction priorities
    "field_priority": {
        "expense_ratio": ["factsheet", "amfi"],
        "exit_load": ["kim", "factsheet"],
        "min_sip_amount": ["kim", "factsheet"],
        "lock_in_period": ["sid", "factsheet"],
        "riskometer": ["factsheet", "sid"],
        "benchmark": ["factsheet", "sid"],
        "statement_download": ["amc_faq", "amc_help"],
        "tax_document": ["amc_faq", "amc_help"]
    },
    
    # Validation rules
    "validation": {
        "expense_ratio": r"^[\d.]+%$",
        "nav": r"^Rs\.?\s*[\d.,]+$",
        "min_sip_amount": r"^Rs\.?\s*[\d,]+$"
    }
}
```

### 3.3 Chunking & Embedding Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CHUNKING & EMBEDDING PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  INPUT SOURCES  │────▶│  PREPROCESSING  │────▶│   CHUNKING      │
│                 │     │                 │     │                 │
│ • Kuvera HTML   │     │ • HTML Parsing  │     │ • Text Splitter │
│ • AMC PDFs      │     │ • PDF Extraction│     │ • Token-based   │
│ • Factsheets    │     │ • Clean Noise   │     │ • Overlap Mgmt  │
│ • SID/KIM docs  │     │ • Normalize     │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌──────────────────────────┼──────────────────┐
                              │                          │                  │
                              ▼                          ▼                  ▼
                    ┌─────────────────┐      ┌─────────────────┐   ┌─────────────────┐
                    │  METADATA       │      │  CHUNK STORE    │   │  EMBEDDING      │
                    │  EXTRACTION     │      │  (Temporary)    │   │  GENERATION     │
                    │                 │      │                 │   │                 │
                    │ • Fund Name     │      │ • Chunk Text    │   │ • OpenAI API    │
                    │ • AMC           │      │ • Chunk ID      │   │ • Batch (100)   │
                    │ • Category      │      │ • Metadata      │   │ • Retry Logic   │
                    │ • Source URL    │      │ • Position      │   │ • Rate Limiting │
                    │ • Doc Type      │      │                 │   │                 │
                    │ • Date          │      │                 │   │                 │
                    └────────┬────────┘      └─────────────────┘   └────────┬────────┘
                             │                                              │
                             └──────────────────────┬───────────────────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────┐
                                         │  VECTOR STORE   │
                                         │  (ChromaDB)     │
                                         │                 │
                                         │ • Collection:   │
                                         │   mutual_fund_  │
                                         │   docs          │
                                         │ • Vectors:      │
                                         │   1536 dims     │
                                         │ • Metadata:     │
                                         │   Full JSON     │
                                         │ • Index:        │
                                         │   HNSW          │
                                         └─────────────────┘
```

#### 3.3.1 Chunking Strategy

```python
# app/rag/chunking.py
class DocumentChunker:
    """
    Advanced chunking with multiple strategies based on document type.
    """
    
    CHUNK_CONFIG = {
        "factsheet": {
            "chunk_size": 800,
            "chunk_overlap": 150,
            "separator": "\n\n",
            "strategy": "section_based"
        },
        "sid_kim": {
            "chunk_size": 1200,
            "chunk_overlap": 200,
            "separator": "\n## ",
            "strategy": "heading_based"
        },
        "faq": {
            "chunk_size": 500,
            "chunk_overlap": 50,
            "separator": "\nQ:",
            "strategy": "qa_pair"
        },
        "default": {
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "separator": "\n",
            "strategy": "recursive"
        }
    }
    
    def chunk_document(self, doc: Document, doc_type: str) -> List[Chunk]:
        config = self.CHUNK_CONFIG.get(doc_type, self.CHUNK_CONFIG["default"])
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
            separators=[config["separator"], "\n", ".", " "],
            length_function=len,
            is_separator_regex=False
        )
        
        chunks = text_splitter.split_text(doc.content)
        
        return [
            Chunk(
                id=f"{doc.id}_{i}",
                text=chunk,
                metadata={
                    **doc.metadata,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "chunking_strategy": config["strategy"]
                }
            )
            for i, chunk in enumerate(chunks)
        ]
```

#### 3.3.2 Embedding Pipeline

```python
# app/rag/embeddings.py
class EmbeddingPipeline:
    """
    Batch embedding generation with caching and error handling.
    """
    
    def __init__(self):
        self.client = OpenAI()
        self.model = "text-embedding-3-small"
        self.batch_size = 100
        self.max_retries = 3
        self.cache = {}  # Simple in-memory cache
    
    def generate_embeddings(self, chunks: List[Chunk]) -> List[Embedding]:
        """
        Generate embeddings in batches with progress tracking.
        """
        embeddings = []
        
        for i in range(0, len(chunks), self.batch_size):
            batch = chunks[i:i + self.batch_size]
            batch_embeddings = self._embed_batch(batch)
            embeddings.extend(batch_embeddings)
            
            # Progress logging
            logger.info(f"Embedded {min(i + self.batch_size, len(chunks))}/{len(chunks)} chunks")
        
        return embeddings
    
    def _embed_batch(self, chunks: List[Chunk]) -> List[Embedding]:
        """
        Embed a single batch with retry logic.
        """
        texts = [chunk.text for chunk in chunks]
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=texts,
                    dimensions=1536
                )
                
                return [
                    Embedding(
                        chunk_id=chunk.id,
                        vector=data.embedding,
                        model=self.model
                    )
                    for chunk, data in zip(chunks, response.data)
                ]
                
            except RateLimitError:
                wait_time = (attempt + 1) * 2
                logger.warning(f"Rate limit hit, waiting {wait_time}s...")
                time.sleep(wait_time)
            
            except Exception as e:
                logger.error(f"Embedding error: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(1)
```

#### 3.3.3 Vector Store Integration

```python
# app/rag/vector_store.py
class VectorStoreManager:
    """
    Manages ChromaDB operations with versioning and rollback.
    """
    
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name="mutual_fund_docs",
            metadata={"hnsw:space": "cosine"}
        )
    
    def upsert_documents(self, chunks: List[Chunk], embeddings: List[Embedding]):
        """
        Upsert documents with versioning support.
        """
        ids = [chunk.id for chunk in chunks]
        texts = [chunk.text for chunk in chunks]
        vectors = [emb.vector for emb in embeddings]
        metadatas = [chunk.metadata for chunk in chunks]
        
        # Add ingestion timestamp
        for meta in metadatas:
            meta["ingested_at"] = datetime.utcnow().isoformat()
            meta["version"] = self._get_next_version()
        
        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=vectors,
            metadatas=metadatas
        )
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the vector store.
        """
        return {
            "total_documents": self.collection.count(),
            "dimension": 1536,
            "last_updated": self._get_last_update(),
            "unique_funds": len(self._get_unique_funds()),
            "unique_amcs": len(self._get_unique_amcs())
        }
```

#### 3.3.4 Pipeline Orchestration

```python
# scripts/ingest_documents.py
class DataPipelineOrchestrator:
    """
    Main orchestrator for the daily data pipeline.
    """
    
    def __init__(self):
        self.chunker = DocumentChunker()
        self.embedder = EmbeddingPipeline()
        self.vector_store = VectorStoreManager("./data/vector_store")
        self.url_sources = self._load_url_sources()
    
    def run_full_pipeline(self):
        """
        Execute the complete data pipeline.
        """
        logger.info("Starting daily data pipeline...")
        
        # 1. Fetch documents
        documents = self._fetch_all_documents()
        logger.info(f"Fetched {len(documents)} documents")
        
        # 2. Chunk documents
        all_chunks = []
        for doc in documents:
            doc_type = self._classify_document_type(doc)
            chunks = self.chunker.chunk_document(doc, doc_type)
            all_chunks.extend(chunks)
        logger.info(f"Created {len(all_chunks)} chunks")
        
        # 3. Generate embeddings
        embeddings = self.embedder.generate_embeddings(all_chunks)
        logger.info(f"Generated {len(embeddings)} embeddings")
        
        # 4. Store in vector DB
        self.vector_store.upsert_documents(all_chunks, embeddings)
        logger.info("Updated vector store")
        
        # 5. Generate report
        stats = self.vector_store.get_collection_stats()
        self._save_pipeline_report(stats)
        
        logger.info("Pipeline completed successfully")
        return stats
    
    def _fetch_all_documents(self) -> List[Document]:
        """
        Fetch documents from all configured URLs.
        """
        documents = []
        
        for url in self.url_sources:
            try:
                doc = self._fetch_document(url)
                documents.append(doc)
            except Exception as e:
                logger.error(f"Failed to fetch {url}: {e}")
        
        return documents
```

### 3.4 Pipeline Monitoring

```python
# app/services/pipeline_monitor.py
class PipelineMonitor:
    """
    Monitor pipeline health and send alerts.
    """
    
    def check_pipeline_health(self) -> HealthStatus:
        """
        Check if daily pipeline ran successfully.
        """
        last_run = self._get_last_pipeline_run()
        
        if not last_run:
            return HealthStatus.ERROR, "No pipeline runs found"
        
        hours_since_run = (datetime.utcnow() - last_run).total_seconds() / 3600
        
        if hours_since_run > 26:  # More than 26 hours (allowing for some delay)
            return HealthStatus.ERROR, f"Pipeline stale: {hours_since_run:.1f}h since last run"
        
        if hours_since_run > 25:
            return HealthStatus.WARNING, f"Pipeline delayed: {hours_since_run:.1f}h since last run"
        
        return HealthStatus.HEALTHY, f"Pipeline healthy: last run {hours_since_run:.1f}h ago"
```

---

## 4. Component Architecture

### 4.1 Project Structure
```
mutual-fund-faq-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # Chat endpoints
│   │   │   ├── documents.py       # Document ingestion endpoints
│   │   │   ├── threads.py         # Thread management endpoints
│   │   │   └── health.py          # Health check endpoints
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # Security utilities
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── middleware.py          # Custom middleware
│   ├── services/
│   │   ├── __init__.py
│   │   ├── rag_service.py         # Main RAG orchestration
│   │   ├── query_classifier.py    # Query classification service
│   │   ├── advisory_detector.py   # Advisory content detection
│   │   └── thread_service.py      # Chat thread management
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── document_loader.py     # Document loading utilities
│   │   ├── embeddings.py          # Embedding generation
│   │   ├── vector_store.py        # ChromaDB wrapper
│   │   ├── retriever.py           # Document retrieval
│   │   └── chain.py               # LangChain RAG chain
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic models
│   │   └── database.py            # Database models
│   └── utils/
│       ├── __init__.py
│       ├── validators.py          # Input validators
│       └── formatters.py          # Response formatters
├── data/
│   ├── raw/                       # Raw downloaded documents
│   ├── processed/                 # Processed chunks
│   └── vector_store/              # ChromaDB persistence
├── docs/                          # Documentation
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── frontend/                      # React frontend (optional)
├── scripts/
│   ├── ingest_documents.py        # Document ingestion script
│   └── setup.sh                   # Setup script
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

### 4.2 Core Components

#### 4.2.1 Document Ingestion Pipeline
```python
# app/rag/document_loader.py
class DocumentIngestionPipeline:
    """
    Handles downloading, parsing, and chunking of AMC documents.
    """
    - download_documents(urls: List[str]) -> List[Document]
    - parse_pdf(file_path: str) -> Document
    - parse_html(url: str) -> Document
    - chunk_documents(docs: List[Document]) -> List[DocumentChunk]
    - extract_metadata(doc: Document) -> Dict
```

**Supported Document Types:**
- PDF (Factsheets, KIM, SID)
- HTML (AMC FAQ pages, AMFI/SEBI pages)

**Chunking Strategy:**
- Method: RecursiveCharacterTextSplitter
- Chunk Size: 1000 tokens
- Chunk Overlap: 200 tokens
- Metadata: Source URL, document type, AMC name, scheme name, last updated

#### 4.2.2 Vector Store (ChromaDB - Local or Cloud)

```python
# app/rag/vector_store.py
class VectorStoreService:
    """
    Service for managing vector store operations with ChromaDB.
    Supports both local persistence and Chroma Cloud.
    """
    - add_embeddings(chunks: List[Chunk], embeddings: List[List[float]])
    - search(query_embedding: List[float], n_results: int = 5) -> List[Chunk]
    - get_stats() -> Dict
    - Using Cloud: bool
```

**Configuration:**
- Collection Name: `mutual_fund_docs`
- Distance Metric: Cosine Similarity
- **Cloud Mode**: Chroma Cloud (TryChroma) - persistent, managed
- **Local Mode**: Local filesystem (`./data/vector_store`) - development only
- Embedding Model: `BAAI/bge-small-en-v1.5` (Free, local)

**Cloud Configuration:**
```python
# Chroma Cloud (Production)
CHROMA_CLOUD_TOKEN=your-api-key
CHROMA_CLOUD_TENANT=your-tenant-id
CHROMA_CLOUD_DATABASE=your-database-name

# Local (Development)
CHROMA_PERSIST_DIRECTORY=./data/vector_store
```

#### 4.2.3 Query Classification Service
```python
# app/services/query_classifier.py
class QueryClassifier:
    """
    Classifies user queries into categories.
    """
    - classify(query: str) -> QueryType
    
    QueryType Enum:
    - FACTUAL (expense ratio, exit load, etc.)
    - ADVISORY ("should I invest", "which is better")
    - PROCEDURAL ("how to download statement")
    - GREETING/CHITCHAT
    - UNKNOWN
```

#### 4.2.4 Advisory Detector
```python
# app/services/advisory_detector.py
class AdvisoryDetector:
    """
    Detects and refuses advisory/investment recommendation queries.
    """
    - is_advisory(query: str) -> bool
    - get_refusal_response(query_type: str) -> str
    
    Patterns to detect:
    - "should I invest"
    - "which fund is better"
    - "recommend"
    - "advice"
    - Comparative questions between funds
```

#### 4.2.5 RAG Service
```python
# app/services/rag_service.py
class RAGService:
    """
    Main orchestration service for RAG pipeline.
    """
    - process_query(query: str, thread_id: str) -> Response
    - _retrieve_documents(query: str) -> List[Document]
    - _generate_response(query: str, context: List[Document]) -> str
    - _format_response(answer: str, sources: List[str]) -> Response
```

**Response Format:**
```json
{
  "answer": "string (max 3 sentences)",
  "source_url": "string (exactly one citation)",
  "last_updated": "YYYY-MM-DD",
  "thread_id": "string",
  "query_type": "factual|advisory|procedural"
}
```

#### 4.2.6 Thread Management
```python
# app/services/thread_service.py
class ThreadService:
    """
    Manages multiple chat conversations.
    """
    - create_thread() -> Thread
    - get_thread(thread_id: str) -> Thread
    - add_message(thread_id: str, message: Message)
    - get_history(thread_id: str) -> List[Message]
    - delete_thread(thread_id: str)
```

**Thread Model:**
```python
class Thread:
    id: str (UUID)
    created_at: datetime
    updated_at: datetime
    messages: List[Message]
    
class Message:
    role: str ("user" | "assistant")
    content: str
    timestamp: datetime
    sources: List[str] (optional)
```

---

## 5. API Endpoints

### 5.1 Chat Endpoints
```yaml
POST /api/v1/chat
  - Send a message and get response
  - Body: { "query": "string", "thread_id": "string (optional)" }
  - Response: { "answer": "string", "source_url": "string", "last_updated": "string", "thread_id": "string" }

GET /api/v1/chat/{thread_id}/history
  - Get chat history for a thread
  - Response: { "thread_id": "string", "messages": [...] }

DELETE /api/v1/chat/{thread_id}
  - Delete a chat thread
```

### 5.2 Thread Management
```yaml
POST /api/v1/threads
  - Create a new chat thread
  - Response: { "thread_id": "string", "created_at": "datetime" }

GET /api/v1/threads
  - List all threads
  - Response: { "threads": [...] }

GET /api/v1/threads/{thread_id}
  - Get thread details
```

### 5.3 Document Management
```yaml
POST /api/v1/documents/ingest
  - Trigger document ingestion
  - Body: { "urls": ["string"] }
  - Response: { "status": "string", "documents_processed": int }

GET /api/v1/documents/status
  - Get ingestion status
  - Response: { "total_documents": int, "last_ingested": "datetime" }

POST /api/v1/documents/refresh
  - Refresh documents from sources
```

### 5.4 Health & Status
```yaml
GET /health
  - Health check
  - Response: { "status": "healthy", "version": "string" }

GET /api/v1/stats
  - System statistics
  - Response: { "total_documents": int, "total_threads": int, "vector_store_size": int }
```

---

## 6. Data Flow

### 6.1 Document Ingestion Flow
```
1. Admin/Scheduler triggers ingestion
2. DocumentLoader downloads URLs
3. Documents parsed (PDF/HTML)
4. TextSplitter creates chunks
5. OpenAIEmbeddings generates vectors
6. ChromaVectorStore stores vectors with metadata
7. Metadata stored in SQLite for tracking
```

### 6.2 Query Processing Flow
```
1. User sends query via POST /api/v1/chat
2. QueryClassifier determines query type
3. AdvisoryDetector checks for advisory content
   - If advisory: Return refusal response with educational link
4. For factual queries:
   a. Query embedded using OpenAI
   b. ChromaDB retrieves top-k similar chunks
   c. LangChain RAG chain generates response
   d. Response formatted (max 3 sentences + source)
5. ThreadService stores message in history
6. Response returned to user
```

---

## 7. Configuration

### 7.1 Environment Variables (.env)
```bash
# Application
APP_NAME="Mutual Fund FAQ Assistant"
APP_VERSION="1.0.0"
DEBUG=false
HOST=0.0.0.0
PORT=8000

# LLM Provider (Groq - Fast & Cheap)
LLM_PROVIDER=groq
GROQ_API_KEY=gsk-...
GROQ_MODEL=llama3-8b-8192

# Embeddings (Free - Local)
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
EMBEDDING_DEVICE=cpu

# ChromaDB - Cloud (Production) or Local (Development)
# Option 1: Chroma Cloud (Recommended for Render deployment)
# Get credentials from: https://trychroma.com
CHROMA_CLOUD_TOKEN=ck-your-chroma-cloud-token
CHROMA_CLOUD_TENANT=your-tenant-uuid
CHROMA_CLOUD_DATABASE=your-database-name

# Option 2: Local ChromaDB (Development only - data lost on restart)
# Uncomment below if NOT using Chroma Cloud
# CHROMA_PERSIST_DIRECTORY=./data/vector_store

CHROMA_COLLECTION_NAME=mutual_fund_docs

# Database
DATABASE_URL=sqlite:///./data/chat_history.db

# Documents
AMC_NAME="Example AMC"
SCHEMES=["Scheme A", "Scheme B", "Scheme C"]
DOCUMENT_URLS=["url1", "url2", ...]

# Security
MAX_QUERY_LENGTH=500
RATE_LIMIT_PER_MINUTE=30

# Compliance
DISCLAIMER="Facts-only. No investment advice."
```

---

## 8. Security & Compliance

### 8.1 Input Validation
- Query length limit: 500 characters
- PII detection: PAN, Aadhaar, account numbers, emails, phones
- Rate limiting: 30 requests per minute per IP

### 8.2 Content Restrictions
- Advisory query detection with pattern matching
- Refusal responses for investment advice requests
- Source citation enforcement

### 8.3 Data Privacy
- No storage of personal financial information
- Chat history purged after 30 days (configurable)
- Audit logging for compliance

---

## 9. Deployment

### 9.1 Architecture Overview

The deployment uses a **hybrid cloud architecture**:
- **Frontend/UI**: Streamlit (Python-based, single codebase)
- **Backend**: FastAPI embedded within Streamlit
- **Vector Store**: Chroma Cloud (managed, persistent)
- **LLM**: Groq API (fast inference)
- **Hosting**: Render (free tier with UptimeRobot for 24/7 uptime)

### 9.2 Chroma Cloud Configuration

We use **Chroma Cloud** (TryChroma) for managed vector storage:

**Benefits:**
- No local disk persistence needed
- Automatic backups
- Scalable storage
- Free tier available

**Configuration:**
```python
# app/config.py
CHROMA_CLOUD_TOKEN: str = ""      # API key from Chroma Cloud
CHROMA_CLOUD_TENANT: str = ""     # Tenant ID
CHROMA_CLOUD_DATABASE: str = ""   # Database name
CHROMA_COLLECTION_NAME: str = "mutual_fund_docs"
```

**Environment Variables:**
```bash
CHROMA_CLOUD_TOKEN=your-chroma-cloud-api-key
CHROMA_CLOUD_TENANT=your-tenant-id
CHROMA_CLOUD_DATABASE=your-database-name
CHROMA_COLLECTION_NAME=mutual_fund_docs
```

### 9.3 Render Deployment

**render.yaml:**
```yaml
services:
  - type: web
    name: mutual-fund-faq-assistant
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: LLM_PROVIDER
        value: groq
      - key: GROQ_API_KEY
        sync: false
      - key: GROQ_MODEL
        value: llama-3.1-8b-instant
      - key: CHROMA_CLOUD_TOKEN
        sync: false
      - key: CHROMA_CLOUD_TENANT
        sync: false
      - key: CHROMA_CLOUD_DATABASE
        sync: false
      - key: CHROMA_COLLECTION_NAME
        value: mutual_fund_docs
    healthCheckPath: /_stcore/health
```

### 9.4 24/7 Uptime with UptimeRobot

Since Render free tier sleeps after 15 minutes of inactivity:

1. **Sign up** at https://uptimerobot.com/
2. **Add Monitor** → HTTP(s)
3. **URL**: Your Render app URL
4. **Interval**: 5 minutes
5. **Monitor Type**: HTTP(s)

This pings your app every 5 minutes to prevent sleep.

### 9.5 Local Development

```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Chroma Cloud credentials

# Run Streamlit UI
python -m streamlit run streamlit_app.py --server.port=8501

# Ingest documents (one-time setup)
python scripts/ingest_data.py

# Upload to Chroma Cloud (optional - for cloud persistence)
python scripts/upload_to_chroma_cloud.py
```

**Note on Python 3.14+ Compatibility:**
The Streamlit UI uses ASCII-only characters (no emojis/Unicode) to avoid syntax errors with Python 3.14's stricter encoding handling.

### 9.6 Docker Configuration (Optional - Local Only)

For local development without Chroma Cloud:
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./data:/app/data
    
  chromadb:
    image: chromadb/chroma:latest
    volumes:
      - ./data/vector_store:/chroma/chroma
```

---

## 10. Testing Strategy

### 10.1 Unit Tests
- Query classifier accuracy
- Advisory detector patterns
- Response formatting
- Vector store operations

### 10.2 Integration Tests
- End-to-end query processing
- Document ingestion pipeline
- API endpoint testing

### 10.3 Compliance Tests
- Advisory query refusal validation
- Source citation presence
- Response length constraints

---

## 11. Monitoring & Logging

### 11.1 Metrics
- Query volume
- Response latency
- Advisory query rate
- Source citation accuracy

### 11.2 Logging
- Structured JSON logging
- Query/response audit trail
- Error tracking

---

## 12. Implementation Status

### ✅ Completed
- **Multi-AMC support**: 5 AMCs (SBI, ICICI, HDFC, Nippon, Kotak) with 25 schemes
- **Chroma Cloud Integration**: Managed vector storage with 100+ chunks uploaded
- **Render + Vercel Deployment**: Backend on Render, frontend on Vercel
- **Next.js Frontend**: React-based UI with Tailwind CSS
- **Multi-Thread Chat**: Isolated chat sessions with no memory sharing between threads
- **Thread Management**: Create, list, select, delete chat threads
- **Daily Data Ingestion**: GitHub Actions scheduler at 9:15 AM IST
- **Free Tier Architecture**: Groq LLM (llama-3.1-8b-instant) + BGE embeddings + Chroma Cloud
- **RAG Pipeline**: Query classification, advisory detection, context retrieval, LLM generation
- **Data Upload Script**: `upload_to_chroma_cloud.py` for manual cloud sync

### 🔄 In Progress
- GitHub Actions automatic upload to Chroma Cloud (quota limits on free tier)
- Better fund metric extraction from Kuvera pages
- User authentication for personalized thread access

### 📋 Future Enhancements
- Real-time document updates via webhooks
- Advanced analytics dashboard
- Multi-language support (Hindi, Tamil, etc.)
- Voice interface
- Caching layer (Redis)
- Incremental updates (only changed documents)
- A/B testing for chunking strategies
- More AMCs (Axis, UTI, DSP, etc.)

---

This architecture provides a solid foundation for building a compliant, scalable, and maintainable Mutual Fund FAQ Assistant.
