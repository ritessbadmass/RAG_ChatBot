"""Web scraping service for mutual fund documents."""
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from mf_assistant.config import SCRAPER_CONFIG, RELEVANT_FIELDS, get_settings
from mf_assistant.core.exceptions import ScrapingException
from mf_assistant.models.schemas import ExtractedData

logger = logging.getLogger(__name__)
settings = get_settings()


class PDFParser:
    """PDF document parser."""
    
    def extract_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF content."""
        try:
            from pypdf import PdfReader
            import io
            
            reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise ScrapingException(f"Failed to parse PDF: {e}")


class HTMLParser:
    """HTML document parser."""
    
    def extract_text(self, html_content: bytes) -> str:
        """Extract text from HTML content."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator='\n', strip=True)
        
        # Clean up whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        return '\n'.join(lines)


class MutualFundScraper:
    """
    Smart scraper that extracts only relevant factual data per problem statement.
    """
    
    def __init__(self, raw_data_dir: str = "./data/raw"):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.pdf_parser = PDFParser()
        self.html_parser = HTMLParser()
        self.config = SCRAPER_CONFIG
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    def scrape_url(self, url: str, doc_type: Optional[str] = None) -> ExtractedData:
        """
        Scrape a single URL and extract relevant fields only.
        
        Args:
            url: URL to scrape
            doc_type: Type of document (factsheet, sid, kim, etc.)
            
        Returns:
            ExtractedData object with scraped information
        """
        try:
            # Validate URL
            if not self._validate_url(url):
                raise ScrapingException(f"URL not in allowed domains: {url}")
            
            logger.info(f"Scraping URL: {url}")
            
            # Handle Kuvera URLs specially
            if 'kuvera.in' in url:
                return self._scrape_kuvera(url)
            
            # Determine document type from URL if not provided
            if doc_type is None:
                doc_type = self._detect_doc_type(url)
            
            # Scrape based on content type
            if url.endswith('.pdf'):
                return self._scrape_pdf(url, doc_type)
            else:
                return self._scrape_html(url, doc_type)
                
        except Exception as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return ExtractedData(
                source_url=url,
                error=str(e),
                scraped_at=datetime.utcnow().isoformat()
            )
    
    def scrape_multiple(self, urls: List[Dict[str, str]]) -> List[ExtractedData]:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of dicts with 'url' and optionally 'doc_type'
            
        Returns:
            List of ExtractedData objects
        """
        results = []
        for item in urls:
            url = item['url'] if isinstance(item, dict) else item
            doc_type = item.get('doc_type') if isinstance(item, dict) else None
            
            result = self.scrape_url(url, doc_type)
            results.append(result)
            
            # Rate limiting
            time.sleep(self.config['rate_limit_delay'])
        
        return results
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL is from allowed domains."""
        for domain in self.config['allowed_domains']:
            if domain in url:
                return True
        return False
    
    def _detect_doc_type(self, url: str) -> str:
        """Detect document type from URL."""
        url_lower = url.lower()
        
        if 'factsheet' in url_lower or 'fact' in url_lower:
            return 'factsheet'
        elif 'sid' in url_lower:
            return 'sid'
        elif 'kim' in url_lower:
            return 'kim'
        elif 'faq' in url_lower or 'help' in url_lower:
            return 'faq'
        else:
            return 'generic'
    
    def _scrape_pdf(self, url: str, doc_type: str) -> ExtractedData:
        """Download and parse PDF documents."""
        # Download with retries
        content = self._download_with_retry(url)
        
        # Check file size
        size_mb = len(content) / (1024 * 1024)
        if size_mb > self.config['max_pdf_size_mb']:
            raise ScrapingException(f"PDF too large: {size_mb:.2f}MB")
        
        # Save raw PDF
        pdf_path = self._save_raw_pdf(url, content)
        
        # Extract text
        text = self.pdf_parser.extract_text(content)
        
        # Parse based on document type
        data = self._parse_by_type(text, doc_type)
        
        return ExtractedData(
            source_url=url,
            doc_type=doc_type,
            raw_text=text[:10000],  # Store first 10k chars for reference
            extracted_fields=data,
            pdf_path=str(pdf_path),
            scraped_at=datetime.utcnow().isoformat()
        )
    
    def _scrape_html(self, url: str, doc_type: str) -> ExtractedData:
        """Parse HTML pages."""
        # Download with retries
        content = self._download_with_retry(url)
        
        # Parse HTML
        text = self.html_parser.extract_text(content)
        
        # Parse based on document type
        data = self._parse_by_type(text, doc_type)
        
        return ExtractedData(
            source_url=url,
            doc_type=doc_type,
            raw_text=text[:10000],  # Store first 10k chars for reference
            extracted_fields=data,
            scraped_at=datetime.utcnow().isoformat()
        )
    
    def _download_with_retry(self, url: str) -> bytes:
        """Download content with retry logic."""
        for attempt in range(self.config['max_retries']):
            try:
                response = self.session.get(
                    url,
                    timeout=self.config['timeout'],
                    stream=True
                )
                response.raise_for_status()
                return response.content
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Download attempt {attempt + 1} failed: {e}")
                if attempt < self.config['max_retries'] - 1:
                    time.sleep(self.config['retry_delay'] * (attempt + 1))
                else:
                    raise ScrapingException(f"Failed to download after {self.config['max_retries']} attempts: {e}")
        
        raise ScrapingException("Download failed")
    
    def _save_raw_pdf(self, url: str, content: bytes) -> Path:
        """Save raw PDF to disk."""
        # Generate filename from URL hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
        filename = f"{url_hash}.pdf"
        filepath = self.raw_data_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(content)
        
        return filepath
    
    def _scrape_kuvera(self, url: str) -> ExtractedData:
        """
        Scrape Kuvera mutual fund pages.
        Since Kuvera uses React (client-side rendering), we extract info from URL
        and fetch basic page content for any available data.
        """
        try:
            logger.info(f"Scraping Kuvera URL: {url}")
            
            # Extract fund info from URL
            fund_info = self._extract_fund_info_from_url(url)
            
            # Download page (may have some SSR content or meta tags)
            response = self.session.get(url, timeout=self.config['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to get better fund name from page title
            title = soup.find('title')
            if title:
                title_text = title.get_text()
                # Extract fund name from title (usually "Fund Name | Kuvera")
                if '|' in title_text:
                    fund_name = title_text.split('|')[0].strip()
                    if fund_name and fund_name != 'Kuvera':
                        fund_info['fund_name'] = fund_name
            
            # Try to get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                fund_info['description'] = meta_desc.get('content', '')
            
            # Get raw text for any available content
            text = self.html_parser.extract_text(response.content)
            
            # Build structured content
            structured_text = self._build_kuvera_content(fund_info, text)
            
            return ExtractedData(
                source_url=url,
                doc_type='factsheet',
                fund_name=fund_info.get('fund_name', 'Unknown Fund'),
                amc_name=fund_info.get('amc_name', 'Unknown AMC'),
                raw_text=structured_text,
                extracted_fields=fund_info,
                scraped_at=datetime.utcnow().isoformat()
            )
            
        except Exception as e:
            logger.error(f"Failed to scrape Kuvera URL {url}: {e}")
            return ExtractedData(
                source_url=url,
                error=str(e),
                scraped_at=datetime.utcnow().isoformat()
            )
    
    def _extract_fund_info_from_url(self, url: str) -> Dict[str, Any]:
        """Extract fund information from Kuvera URL structure."""
        data = {}
        
        # URL format: https://kuvera.in/mutual-funds/fund/{fund-slug}--{code}
        # Example: sbi-bluechip-direct-growth--SBI072-GR
        
        parts = url.split('--')
        if len(parts) >= 2:
            # Extract fund slug
            slug_part = parts[0].split('/')[-1]
            
            # Convert slug to readable name
            # sbi-bluechip-direct-growth -> SBI Bluechip Direct Growth
            words = slug_part.replace('-', ' ').split()
            fund_name = ' '.join(word.capitalize() for word in words)
            data['fund_name'] = fund_name
            
            # Extract AMC from slug
            if words:
                amc = words[0].upper()
                amc_map = {
                    'SBI': 'SBI Mutual Fund',
                    'ICICI': 'ICICI Prudential Mutual Fund',
                    'HDFC': 'HDFC Mutual Fund',
                    'NIPPON': 'Nippon India Mutual Fund',
                    'KOTAK': 'Kotak Mahindra Mutual Fund',
                    'AXIS': 'Axis Mutual Fund',
                    'UTI': 'UTI Mutual Fund',
                    'DSP': 'DSP Mutual Fund',
                    'TATA': 'Tata Mutual Fund',
                    'LIC': 'LIC Mutual Fund'
                }
                data['amc_name'] = amc_map.get(amc, f'{amc} Mutual Fund')
            
            # Extract ISIN/code
            code_part = parts[1].split('-')[0]
            data['fund_code'] = code_part
            
            # Determine plan type
            if 'direct' in slug_part.lower():
                data['plan_type'] = 'Direct'
            else:
                data['plan_type'] = 'Regular'
            
            # Determine option type
            if 'growth' in slug_part.lower():
                data['option_type'] = 'Growth'
            elif 'idcw' in slug_part.lower() or 'dividend' in slug_part.lower():
                data['option_type'] = 'IDCW'
        
        return data
    
    def _build_kuvera_content(self, fund_info: Dict[str, Any], raw_text: str) -> str:
        """Build structured content for the fund."""
        content_parts = []
        
        # Add fund identification
        content_parts.append(f"Fund Name: {fund_info.get('fund_name', 'Unknown')}")
        content_parts.append(f"AMC: {fund_info.get('amc_name', 'Unknown')}")
        content_parts.append(f"Plan Type: {fund_info.get('plan_type', 'Unknown')}")
        content_parts.append(f"Option Type: {fund_info.get('option_type', 'Unknown')}")
        
        if 'fund_code' in fund_info:
            content_parts.append(f"Fund Code: {fund_info['fund_code']}")
        
        if 'description' in fund_info:
            content_parts.append(f"\nDescription: {fund_info['description']}")
        
        # Add any extracted metrics from raw text
        content_parts.append("\n--- Additional Information ---")
        content_parts.append(raw_text[:5000])  # Add first 5000 chars of raw text
        
        return '\n'.join(content_parts)
    
    def _extract_kuvera_fund_name(self, soup: BeautifulSoup) -> str:
        """Extract fund name from Kuvera page."""
        # Try multiple selectors
        selectors = [
            'h1[data-testid="fund-name"]',
            'h1.fund-name',
            'h1',
            '[data-testid="fund-header"] h1'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return "Unknown Fund"
    
    def _extract_kuvera_amc(self, soup: BeautifulSoup) -> str:
        """Extract AMC name from Kuvera page."""
        # Look for AMC in the page
        selectors = [
            '[data-testid="amc-name"]',
            '.amc-name',
            'a[href*="/mutual-funds/amc/"]'
        ]
        
        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return "Unknown AMC"
    
    def _extract_kuvera_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract key metrics from Kuvera page."""
        data = {}
        
        # Try to find JSON data in script tags
        scripts = soup.find_all('script', type='application/json')
        for script in scripts:
            try:
                json_data = json.loads(script.string)
                # Extract from JSON if available
                if isinstance(json_data, dict):
                    data.update(self._parse_kuvera_json(json_data))
            except:
                pass
        
        # Extract from HTML elements
        # NAV
        nav_elem = soup.select_one('[data-testid="nav-value"], .nav-value, .current-nav')
        if nav_elem:
            data['nav'] = nav_elem.get_text(strip=True)
        
        # Expense Ratio
        expense_elem = soup.select_one('[data-testid="expense-ratio"], .expense-ratio')
        if expense_elem:
            data['expense_ratio'] = expense_elem.get_text(strip=True)
        
        # AUM
        aum_elem = soup.select_one('[data-testid="aum"], .aum, .fund-size')
        if aum_elem:
            data['aum'] = aum_elem.get_text(strip=True)
        
        # Category
        category_elem = soup.select_one('[data-testid="fund-category"], .category')
        if category_elem:
            data['fund_category'] = category_elem.get_text(strip=True)
        
        # Risk
        risk_elem = soup.select_one('[data-testid="risk-level"], .risk, .riskometer')
        if risk_elem:
            data['riskometer'] = risk_elem.get_text(strip=True)
        
        return data
    
    def _parse_kuvera_json(self, json_data: Dict) -> Dict[str, Any]:
        """Parse Kuvera JSON data structure."""
        data = {}
        
        # Navigate through possible JSON structures
        if 'props' in json_data and 'pageProps' in json_data['props']:
            page_props = json_data['props']['pageProps']
            
            if 'fund' in page_props:
                fund = page_props['fund']
                data['fund_name'] = fund.get('name', '')
                data['amc_name'] = fund.get('amc', '')
                data['nav'] = fund.get('nav', '')
                data['expense_ratio'] = fund.get('expense_ratio', '')
                data['aum'] = fund.get('aum', '')
                data['fund_category'] = fund.get('category', '')
                data['riskometer'] = fund.get('risk_level', '')
                data['benchmark'] = fund.get('benchmark', '')
                data['min_sip_amount'] = fund.get('min_sip_amount', '')
        
        return data
    
    def _parse_kuvera_text(self, text: str) -> Dict[str, Any]:
        """Parse Kuvera page text for fund information."""
        data = {}
        
        # Fund name patterns
        fund_patterns = [
            r'Fund\s*Name[\s:]+([^\n]+)',
            r'Scheme\s*Name[\s:]+([^\n]+)',
        ]
        fund_match = self._extract_with_patterns(text, fund_patterns)
        if fund_match:
            data['fund_name'] = fund_match
        
        # AMC patterns
        amc_patterns = [
            r'AMC[\s:]+([^\n]+)',
            r'Fund\s*House[\s:]+([^\n]+)',
            r'Asset\s*Management\s*Company[\s:]+([^\n]+)',
        ]
        amc_match = self._extract_with_patterns(text, amc_patterns)
        if amc_match:
            data['amc_name'] = amc_match
        
        # NAV patterns
        nav_patterns = [
            r'NAV[\s:]+(?:Rs\.?\s*)?([\d,.]+)',
            r'Net\s*Asset\s*Value[\s:]+(?:Rs\.?\s*)?([\d,.]+)',
        ]
        nav_match = self._extract_with_patterns(text, nav_patterns)
        if nav_match:
            data['nav'] = f"Rs. {nav_match}"
        
        # Expense ratio patterns
        expense_patterns = [
            r'Expense\s*Ratio[\s:]+([\d.]+)\s*%?',
            r'TER[\s:]+([\d.]+)\s*%?',
        ]
        expense_match = self._extract_with_patterns(text, expense_patterns)
        if expense_match:
            data['expense_ratio'] = f"{expense_match}%"
        
        # AUM patterns
        aum_patterns = [
            r'AUM[\s:]+(?:Rs\.?\s*)?([\d,.]+\s*(?:Cr|Lac|Lakh))',
            r'Fund\s*Size[\s:]+(?:Rs\.?\s*)?([\d,.]+\s*(?:Cr|Lac|Lakh))',
        ]
        aum_match = self._extract_with_patterns(text, aum_patterns)
        if aum_match:
            data['aum'] = f"Rs. {aum_match}"
        
        # Category patterns
        category_patterns = [
            r'Category[\s:]+([^\n]+)',
            r'Fund\s*Category[\s:]+([^\n]+)',
            r'Scheme\s*Category[\s:]+([^\n]+)',
        ]
        category_match = self._extract_with_patterns(text, category_patterns)
        if category_match:
            data['fund_category'] = category_match
        
        # Risk patterns
        risk_patterns = [
            r'Risk[\s:]+(\w+)',
            r'Riskometer[\s:]+(\w+)',
            r'Risk\s*Level[\s:]+(\w+)',
        ]
        risk_match = self._extract_with_patterns(text, risk_patterns)
        if risk_match:
            data['riskometer'] = risk_match
        
        # Benchmark patterns
        benchmark_patterns = [
            r'Benchmark[\s:]+([^\n]+)',
            r'Benchmark\s*Index[\s:]+([^\n]+)',
        ]
        benchmark_match = self._extract_with_patterns(text, benchmark_patterns)
        if benchmark_match:
            data['benchmark'] = benchmark_match
        
        # Min SIP patterns
        sip_patterns = [
            r'Minimum\s*SIP[\s:]+(?:Rs\.?\s*)?([\d,]+)',
            r'Min\s*SIP[\s:]+(?:Rs\.?\s*)?([\d,]+)',
            r'SIP\s*Minimum[\s:]+(?:Rs\.?\s*)?([\d,]+)',
        ]
        sip_match = self._extract_with_patterns(text, sip_patterns)
        if sip_match:
            data['min_sip_amount'] = f"Rs. {sip_match}"
        
        # Exit load patterns
        exit_patterns = [
            r'Exit\s*Load[\s:]+([^\n]+)',
            r'Redemption\s*Charge[\s:]+([^\n]+)',
        ]
        exit_match = self._extract_with_patterns(text, exit_patterns)
        if exit_match:
            data['exit_load'] = exit_match
        
        return data

    def _parse_by_type(self, text: str, doc_type: str) -> Dict:
        """Parse text based on document type."""
        parsers = {
            'factsheet': self._parse_factsheet,
            'sid': self._parse_sid,
            'kim': self._parse_kim,
            'faq': self._parse_faq,
            'generic': self._parse_generic
        }
        
        parser = parsers.get(doc_type, self._parse_generic)
        return parser(text)
    
    def _parse_factsheet(self, text: str) -> Dict:
        """Parse factsheet PDF for key metrics."""
        data = {}
        
        # Expense Ratio
        expense_patterns = [
            r'expense\s*ratio[:\s]+([\d.]+)\s*%',
            r'total\s*expense\s*ratio[:\s]+([\d.]+)\s*%',
            r'ter[:\s]+([\d.]+)\s*%',
        ]
        data['expense_ratio'] = self._extract_with_patterns(text, expense_patterns)
        
        # Exit Load
        exit_patterns = [
            r'exit\s*load[:\s]+([^\n.]+)',
            r'redemption\s*charge[:\s]+([^\n.]+)',
        ]
        data['exit_load'] = self._extract_with_patterns(text, exit_patterns)
        
        # Minimum SIP
        sip_patterns = [
            r'minimum\s*sip[:\s]+(?:rs\.?\s*)?([\d,]+)',
            r'sip\s*minimum[:\s]+(?:rs\.?\s*)?([\d,]+)',
            r'min\.?\s*investment[:\s]+(?:rs\.?\s*)?([\d,]+)',
        ]
        sip_value = self._extract_with_patterns(text, sip_patterns)
        if sip_value:
            data['min_sip_amount'] = f"Rs. {sip_value}"
        
        # Riskometer
        risk_patterns = [
            r'riskometer[:\s]+(\w+)',
            r'risk\s*level[:\s]+(\w+)',
            r'risk[:\s]+(\w+)',
        ]
        data['riskometer'] = self._extract_with_patterns(text, risk_patterns)
        
        # Benchmark
        benchmark_patterns = [
            r'benchmark[:\s]+([^\n.]+)',
            r'benchmark\s*index[:\s]+([^\n.]+)',
        ]
        data['benchmark'] = self._extract_with_patterns(text, benchmark_patterns)
        
        # NAV
        nav_patterns = [
            r'nav[:\s]+(?:rs\.?\s*)?([\d.]+)',
            r'net\s*asset\s*value[:\s]+(?:rs\.?\s*)?([\d.]+)',
        ]
        nav_value = self._extract_with_patterns(text, nav_patterns)
        if nav_value:
            data['nav'] = f"Rs. {nav_value}"
        
        # AUM
        aum_patterns = [
            r'aum[:\s]+(?:rs\.?\s*)?([\d,]+\s*(?:cr|crore|mn|million))',
            r'assets\s*under\s*management[:\s]+(?:rs\.?\s*)?([\d,]+\s*(?:cr|crore))',
        ]
        aum_value = self._extract_with_patterns(text, aum_patterns)
        if aum_value:
            data['aum'] = f"Rs. {aum_value}"
        
        # Fund Manager
        fm_patterns = [
            r'fund\s*manager[:\s]+([^\n.]+)',
            r'managed\s*by[:\s]+([^\n.]+)',
        ]
        data['fund_manager'] = self._extract_with_patterns(text, fm_patterns)
        
        return data
    
    def _parse_sid(self, text: str) -> Dict:
        """Parse SID for scheme information."""
        data = {}
        
        # Lock-in period
        lockin_patterns = [
            r'lock[-\s]?in\s*period[:\s]+([^\n.]+)',
            r'lockin[:\s]+([^\n.]+)',
        ]
        data['lock_in_period'] = self._extract_with_patterns(text, lockin_patterns)
        
        # Fund Category
        category_patterns = [
            r'scheme\s*category[:\s]+([^\n.]+)',
            r'category[:\s]+([^\n.]+)',
        ]
        data['fund_category'] = self._extract_with_patterns(text, category_patterns)
        
        # Investment Objective
        obj_patterns = [
            r'investment\s*objective[:\s]+([^\n]+(?:\n[^\n]+){0,3})',
        ]
        data['investment_objective'] = self._extract_with_patterns(text, obj_patterns)
        
        # Inception Date
        date_patterns = [
            r'date\s*of\s*inception[:\s]+([\d\-A-Za-z]+)',
            r'inception[:\s]+([\d\-A-Za-z]+)',
            r'launch\s*date[:\s]+([\d\-A-Za-z]+)',
        ]
        data['inception_date'] = self._extract_with_patterns(text, date_patterns)
        
        return data
    
    def _parse_kim(self, text: str) -> Dict:
        """Parse KIM for key information."""
        data = {}
        
        # Entry/Exit Load
        load_patterns = [
            r'load[:\s]+([^\n.]+(?:\n[^\n.]+){0,2})',
            r'entry\s*load[:\s]+([^\n.]+)',
            r'exit\s*load[:\s]+([^\n.]+)',
        ]
        data['load_structure'] = self._extract_with_patterns(text, load_patterns)
        
        # Minimum Investment
        min_inv_patterns = [
            r'minimum\s*(?:purchase|investment)[:\s]+(?:rs\.?\s*)?([\d,]+)',
            r'min\.?\s*investment[:\s]+(?:rs\.?\s*)?([\d,]+)',
        ]
        min_inv = self._extract_with_patterns(text, min_inv_patterns)
        if min_inv:
            data['min_investment'] = f"Rs. {min_inv}"
        
        return data
    
    def _parse_faq(self, text: str) -> Dict:
        """Parse FAQ pages for procedural information."""
        data = {}
        
        # Statement download
        if 'statement' in text.lower() and 'download' in text.lower():
            stmt_patterns = [
                r'(?:how\s*to\s*)?download\s*statement[:\s]+([^\n]+(?:\n[^\n]+){0,5})',
            ]
            data['statement_download'] = self._extract_with_patterns(text, stmt_patterns)
        
        # Tax documents
        if 'tax' in text.lower() or 'capital gain' in text.lower():
            tax_patterns = [
                r'(?:how\s*to\s*)?download\s*tax[^\n]+[:\s]+([^\n]+(?:\n[^\n]+){0,5})',
            ]
            data['tax_document'] = self._extract_with_patterns(text, tax_patterns)
        
        return data
    
    def _parse_generic(self, text: str) -> Dict:
        """Generic parser for any document type."""
        data = {}
        
        for field, keywords in RELEVANT_FIELDS.items():
            for keyword in keywords:
                # Try multiple pattern variations
                patterns = [
                    rf'{keyword}[:\s]+([^\n.]+)',
                    rf'{keyword}\s+is[:\s]+([^\n.]+)',
                    rf'{keyword}\s+[:\s]+Rs\.?\s*([\d,.]+)',
                ]
                value = self._extract_with_patterns(text, patterns)
                if value:
                    data[field] = value
                    break
        
        return data
    
    def _extract_with_patterns(self, text: str, patterns: List[str]) -> Optional[str]:
        """Extract value using multiple patterns."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                value = match.group(1).strip()
                # Clean up the value
                value = ' '.join(value.split())  # Remove extra whitespace
                if value and value.lower() not in ['na', 'n/a', '-', '']:
                    return value
        return None


class ScrapingPipeline:
    """Pipeline for scraping multiple sources."""
    
    def __init__(self, scraper: Optional[MutualFundScraper] = None):
        self.scraper = scraper or MutualFundScraper()
    
    def run_pipeline(self, urls_config: List[Dict]) -> List[ExtractedData]:
        """
        Run full scraping pipeline.
        
        Args:
            urls_config: List of dicts with 'url', 'amc', 'scheme', 'doc_type'
            
        Returns:
            List of ExtractedData
        """
        logger.info(f"Starting scraping pipeline for {len(urls_config)} URLs")
        
        results = []
        for config in urls_config:
            url = config['url']
            doc_type = config.get('doc_type')
            
            result = self.scraper.scrape_url(url, doc_type)
            
            # Add metadata
            result.metadata = {
                'amc': config.get('amc', 'Unknown'),
                'scheme': config.get('scheme', 'Unknown'),
                'category': config.get('category', 'Unknown')
            }
            
            results.append(result)
            
            logger.info(f"Scraped {url}: {len(result.extracted_fields)} fields extracted")
        
        logger.info(f"Pipeline complete. {len(results)} documents scraped.")
        return results
