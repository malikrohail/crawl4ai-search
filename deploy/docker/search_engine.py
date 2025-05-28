"""
Search Engine Implementation for Crawl4AI
Supports multiple search providers with query operators
Feature implementation based on FireCrawl search endpoint: https://docs.firecrawl.dev/features/search
"""

import asyncio
import aiohttp
import json
import urllib.parse
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Basic search result from search engine"""
    title: str
    description: str
    url: str
    position: int = 0

class SearchEngine:
    """Base search engine class"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.timeout),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[SearchResult]:
        """Override in subclasses"""
        raise NotImplementedError

class DuckDuckGoSearch(SearchEngine):
    """DuckDuckGo search implementation"""
    
    def __init__(self, timeout: int = 30):
        super().__init__(timeout)
        self.base_url = "https://duckduckgo.com/"
        self.instant_answer_url = "https://api.duckduckgo.com/"
    
    async def search(self, query: str, limit: int = 10, lang: str = "en", country: str = "us", tbs: str = None, **kwargs) -> List[SearchResult]:
        """Search using DuckDuckGo"""
        try:
            # Add initial delay to avoid rate limiting
            await asyncio.sleep(1.0)
            
            # Check if query has operators that work better with HTML search
            # migrated these operators feature from firecrawl
            has_operators = any(op in query.lower() for op in ['site:', 'inurl:', 'intitle:', 'filetype:', '-'])
            
            if has_operators:
                # For queries with operators, try HTML search first
                logger.info("Query contains operators, trying HTML search first")
                
                # Try regular HTML search first for operators
                html_results = await self._try_html_search(query, limit, lang, country, tbs)
                if html_results:
                    logger.info(f"Found {len(html_results)} results from HTML search")
                    return html_results
                
                # do lite HTML search , if regular html search fails
                lite_results = await self._try_lite_search(query, limit, lang, country, tbs)
                if lite_results:
                    logger.info(f"Found {len(lite_results)} results from lite search")
                    return lite_results
            else:
                # For simple queries, try instant answer first
                logger.info("Simple query")
                
                # Try instant answer API for simple queries
                instant_results = await self._try_instant_answer(query, limit)
                if instant_results:
                    logger.info(f"Found {len(instant_results)} results from instant answer API")
                    return instant_results
                
                # Try lite HTML search
                lite_results = await self._try_lite_search(query, limit, lang, country, tbs)
                if lite_results:
                    logger.info(f"Found {len(lite_results)} results from lite search")
                    return lite_results
                
                # Fallback to regular HTML search
                html_results = await self._try_html_search(query, limit, lang, country, tbs)
                if html_results:
                    logger.info(f"Found {len(html_results)} results from HTML search")
                    return html_results
            
            logger.warning("No results found from any DuckDuckGo endpoint")
            return []
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {str(e)}")
            return []
    
    async def _try_instant_answer(self, query: str, limit: int) -> List[SearchResult]:
        """Try DuckDuckGo instant answer API"""
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            async with self.session.get(self.instant_answer_url, params=params) as response:
                if response.status == 200:
                    # Handle both JSON and JavaScript responses
                    content_type = response.headers.get('content-type', '')
                    if 'json' in content_type or 'javascript' in content_type:
                        text_content = await response.text()
                        # Try to parse as JSON
                        try:
                            data = json.loads(text_content)
                            return self._parse_instant_answer(data, query, limit)
                        except json.JSONDecodeError:
                            logger.debug("Failed to parse instant answer as JSON")
                    else:
                        data = await response.json()
                        return self._parse_instant_answer(data, query, limit)
        except Exception as e:
            logger.debug(f"Instant answer failed: {str(e)}")
        
        return []
    
    async def _try_html_search(self, query: str, limit: int, lang: str, country: str, tbs: str) -> List[SearchResult]:
        """Try DuckDuckGo HTML search (better for operators)"""
        try:
            # Add a delay to avoid rate limiting
            await asyncio.sleep(1.2)
            
            # Use regular DuckDuckGo HTML for better operator support
            search_url = "https://duckduckgo.com/html/"
            params = {
                'q': query,
                'kl': f'{country}-{lang}' if country and lang else 'us-en',
            }
            
            # Add time-based filters if specified
            if tbs:
                params['df'] = self._convert_tbs_to_ddg(tbs)
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._parse_ddg_html_results(html_content, limit)
                else:
                    logger.debug(f"DuckDuckGo HTML search failed with status {response.status}")
        except Exception as e:
            logger.debug(f"HTML search error: {str(e)}")
        
        return []
    
    def _parse_instant_answer(self, data: dict, query: str, limit: int) -> List[SearchResult]:
        """Parse DuckDuckGo instant answer response"""
        results = []
        
        try:
            # Check for related topics
            related_topics = data.get('RelatedTopics', [])
            for i, topic in enumerate(related_topics[:limit]):
                if isinstance(topic, dict) and 'FirstURL' in topic and 'Text' in topic:
                    title = topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else topic.get('Text', '')
                    description = topic.get('Text', '')
                    url = topic.get('FirstURL', '')
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title[:100],  # Truncate long titles
                            description=description[:300],  # Truncate long descriptions
                            url=url,
                            position=i + 1
                        ))
            
            # If no related topics, try to create a result from the abstract
            if not results and data.get('Abstract'):
                abstract_url = data.get('AbstractURL', '')
                if abstract_url:
                    results.append(SearchResult(
                        title=data.get('Heading', query),
                        description=data.get('Abstract', ''),
                        url=abstract_url,
                        position=1
                    ))
                    
        except Exception as e:
            logger.warning(f"Error parsing instant answer: {str(e)}")
        
        return results
    
    async def _try_lite_search(self, query: str, limit: int, lang: str, country: str, tbs: str) -> List[SearchResult]:
        """Try DuckDuckGo lite search (optimized for parsing)"""
        try:
            # Add a delay to avoid rate limiting
            await asyncio.sleep(0.8)
            
            search_url = "https://lite.duckduckgo.com/lite/"
            params = {
                'q': query,
                'kl': f'{country}-{lang}' if country and lang else 'us-en',
            }
            
            # Add time-based filters if specified
            if tbs:
                params['df'] = self._convert_tbs_to_ddg(tbs)
            
            async with self.session.get(search_url, params=params) as response:
                if response.status == 200:
                    html_content = await response.text()
                    return self._parse_lite_results(html_content, limit)
                else:
                    logger.debug(f"DuckDuckGo lite search failed with status {response.status}")
        except Exception as e:
            logger.debug(f"Lite search error: {str(e)}")
        
        return []
    
    def _parse_lite_results(self, html: str, limit: int) -> List[SearchResult]:
        """Parse DuckDuckGo lite version results (table-based)"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Lite version uses table rows
            table_rows = soup.find_all('tr')
            
            for i, row in enumerate(table_rows):
                try:
                    # Look for links in the row
                    links = row.find_all('a')
                    
                    for link in links:
                        href = link.get('href', '')
                        title = link.get_text(strip=True)
                        
                        # Skip internal DuckDuckGo links and empty titles
                        if (href and title and 
                            href.startswith('http') and 
                            'duckduckgo.com' not in href and
                            len(title) > 3):
                            
                            # Try to get description from the same row or next cells
                            description = ""
                            cells = row.find_all('td')
                            for cell in cells:
                                cell_text = cell.get_text(strip=True)
                                if cell_text and cell_text != title and len(cell_text) > 10:
                                    description = cell_text
                                    break
                            
                            results.append(SearchResult(
                                title=title[:200],
                                description=description[:500],
                                url=href,
                                position=len(results) + 1
                            ))
                            
                            if len(results) >= limit:
                                return results
                                
                except Exception as e:
                    logger.debug(f"Error parsing lite result row {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo lite results: {str(e)}")
        
        return results
    
    def _parse_ddg_html_results(self, html: str, limit: int) -> List[SearchResult]:
        """Parse regular DuckDuckGo HTML results (better for operators)"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for result containers in regular DuckDuckGo HTML
            result_elements = (
                soup.find_all('div', class_='result') or
                soup.find_all('div', class_='web-result') or
                soup.find_all('div', class_='results_links') or
                soup.find_all('div', class_='result__body') or
                soup.find_all('div', {'class': re.compile(r'result')})
            )
            
            for i, element in enumerate(result_elements[:limit * 2]):  # Get more to filter
                try:
                    # Look for title link with multiple selectors
                    title_link = (
                        element.find('a', class_='result__a') or
                        element.find('a', class_='result__url') or
                        element.find('h2', class_='result__title') or
                        element.find('h3') or
                        element.find('a', href=True)
                    )
                    
                    if not title_link:
                        continue
                    
                    title = title_link.get_text(strip=True)
                    url = title_link.get('href', '')
                    
                    # Extract description with multiple selectors
                    desc_element = (
                        element.find('a', class_='result__snippet') or
                        element.find('div', class_='result__snippet') or
                        element.find('span', class_='result__snippet') or
                        element.find('div', class_='snippet') or
                        element.find('p')
                    )
                    description = desc_element.get_text(strip=True) if desc_element else ""
                    
                    # Validate and clean the result
                    if (title and url and url.startswith('http') and 
                        len(title) > 3 and 'duckduckgo.com' not in url):
                        
                        results.append(SearchResult(
                            title=title[:200],
                            description=description[:500],
                            url=url,
                            position=len(results) + 1
                        ))
                        
                        if len(results) >= limit:
                            break
                        
                except Exception as e:
                    logger.debug(f"Error parsing HTML result {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo HTML results: {str(e)}")
        
        return results

    def _convert_tbs_to_ddg(self, tbs: str) -> str:
        """Convert Google-style tbs to DuckDuckGo date filter"""
        tbs_mapping = {
            'qdr:h': 'd',    # Past hour -> Past day (DDG doesn't have hour)
            'qdr:d': 'd',    # Past day
            'qdr:w': 'w',    # Past week
            'qdr:m': 'm',    # Past month
            'qdr:y': 'y'     # Past year
        }
        return tbs_mapping.get(tbs, '')
    
    def _parse_ddg_results(self, html: str, limit: int) -> List[SearchResult]:
        """Parse DuckDuckGo HTML results"""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try multiple selectors for DuckDuckGo results (including lite version)
            result_elements = (
                soup.find_all('tr') or  # Lite version uses table rows
                soup.find_all('div', class_='result') or
                soup.find_all('div', class_='web-result') or
                soup.find_all('div', class_='results_links') or
                soup.find_all('div', class_='result__body')
            )
            
            for i, element in enumerate(result_elements[:limit * 2]):  # Get more to filter
                try:
                    # For lite version (table rows)
                    if element.name == 'tr':
                        link = element.find('a')
                        if not link or not link.get('href'):
                            continue
                        
                        title = link.get_text(strip=True)
                        url = link.get('href', '')
                        
                        # Get description from next sibling or same row
                        desc_element = element.find_next('td') or element.find('td')
                        description = desc_element.get_text(strip=True) if desc_element else ""
                        
                    else:
                        # For regular version (divs)
                        title_link = (
                            element.find('a', class_='result__a') or
                            element.find('a', class_='result__url') or
                            element.find('h2', class_='result__title') or
                            element.find('a')
                        )
                        
                        if not title_link:
                            continue
                        
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        
                        # Extract description with multiple selectors
                        desc_element = (
                            element.find('a', class_='result__snippet') or
                            element.find('div', class_='result__snippet') or
                            element.find('span', class_='result__snippet') or
                            element.find('div', class_='snippet')
                        )
                        description = desc_element.get_text(strip=True) if desc_element else ""
                    
                    # Validate and clean the result
                    if title and url and url.startswith('http') and len(title) > 3:
                        # Skip DuckDuckGo internal links
                        if 'duckduckgo.com' not in url:
                            results.append(SearchResult(
                                title=title[:200],  # Truncate long titles
                                description=description[:500],  # Truncate long descriptions
                                url=url,
                                position=len(results) + 1
                            ))
                            
                            if len(results) >= limit:
                                break
                        
                except Exception as e:
                    logger.warning(f"Error parsing DDG result {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing DuckDuckGo results: {str(e)}")
        
        return results

class BingSearch(SearchEngine):
    """Bing search implementation using Bing Web Search API"""
    
    def __init__(self, api_key: str = None, timeout: int = 30):
        super().__init__(timeout)
        self.api_key = api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
    
    async def search(self, query: str, limit: int = 10, lang: str = "en", country: str = "us", tbs: str = None, **kwargs) -> List[SearchResult]:
        """Search using Bing API"""
        if not self.api_key:
            logger.warning("Bing API key not provided, falling back to DuckDuckGo")
            ddg = DuckDuckGoSearch(self.timeout)
            async with ddg:
                return await ddg.search(query, limit, lang, country, tbs, **kwargs)
        
        try:
            headers = {
                'Ocp-Apim-Subscription-Key': self.api_key,
                'User-Agent': 'Mozilla/5.0 (compatible; Crawl4AI/1.0)'
            }
            
            params = {
                'q': query,
                'count': min(limit, 50),
                'mkt': f'{lang}-{country.upper()}',
                'responseFilter': 'Webpages',
                'textDecorations': False,
                'textFormat': 'Raw'
            }
            
            # Add freshness filter if specified
            if tbs:
                freshness = self._convert_tbs_to_bing(tbs)
                if freshness:
                    params['freshness'] = freshness
            
            async with self.session.get(self.base_url, headers=headers, params=params) as response:
                if response.status != 200:
                    logger.error(f"Bing search failed with status {response.status}")
                    return []
                
                data = await response.json()
                return self._parse_bing_results(data)
                
        except Exception as e:
            logger.error(f"Bing search error: {str(e)}")
            return []
    
    def _convert_tbs_to_bing(self, tbs: str) -> str:
        """Convert Google-style tbs to Bing freshness filter"""
        tbs_mapping = {
            'qdr:d': 'Day',
            'qdr:w': 'Week',
            'qdr:m': 'Month'
        }
        return tbs_mapping.get(tbs, '')
    
    def _parse_bing_results(self, data: dict) -> List[SearchResult]:
        """Parse Bing API response"""
        results = []
        try:
            web_pages = data.get('webPages', {})
            values = web_pages.get('value', [])
            
            for i, item in enumerate(values):
                try:
                    title = item.get('name', '')
                    description = item.get('snippet', '')
                    url = item.get('url', '')
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title,
                            description=description,
                            url=url,
                            position=i + 1
                        ))
                        
                except Exception as e:
                    logger.warning(f"Error parsing Bing result {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Bing results: {str(e)}")
        
        return results

class GoogleCustomSearch(SearchEngine):
    """Google Custom Search implementation"""
    
    def __init__(self, api_key: str = None, search_engine_id: str = None, timeout: int = 30):
        super().__init__(timeout)
        self.api_key = api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, limit: int = 10, lang: str = "en", country: str = "us", tbs: str = None, **kwargs) -> List[SearchResult]:
        """Search using Google Custom Search API"""
        if not self.api_key or not self.search_engine_id:
            logger.warning("Google Custom Search credentials not provided, falling back to DuckDuckGo")
            ddg = DuckDuckGoSearch(self.timeout)
            async with ddg:
                return await ddg.search(query, limit, lang, country, tbs, **kwargs)
        
        try:
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(limit, 10),  # Google allows max 10 per request
                'hl': lang,
                'gl': country,
                'safe': 'off'
            }
            
            # Add date restriction if specified
            if tbs:
                date_restrict = self._convert_tbs_to_google(tbs)
                if date_restrict:
                    params['dateRestrict'] = date_restrict
            
            async with self.session.get(self.base_url, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google search failed with status {response.status}")
                    return []
                
                data = await response.json()
                return self._parse_google_results(data)
                
        except Exception as e:
            logger.error(f"Google search error: {str(e)}")
            return []
    
    def _convert_tbs_to_google(self, tbs: str) -> str:
        """Convert tbs to Google dateRestrict format"""
        tbs_mapping = {
            'qdr:h': 'd1',   # Past hour -> Past day
            'qdr:d': 'd1',   # Past day
            'qdr:w': 'w1',   # Past week
            'qdr:m': 'm1',   # Past month
            'qdr:y': 'y1'    # Past year
        }
        return tbs_mapping.get(tbs, '')
    
    def _parse_google_results(self, data: dict) -> List[SearchResult]:
        """Parse Google Custom Search API response"""
        results = []
        try:
            items = data.get('items', [])
            
            for i, item in enumerate(items):
                try:
                    title = item.get('title', '')
                    description = item.get('snippet', '')
                    url = item.get('link', '')
                    
                    if title and url:
                        results.append(SearchResult(
                            title=title,
                            description=description,
                            url=url,
                            position=i + 1
                        ))
                        
                except Exception as e:
                    logger.warning(f"Error parsing Google result {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing Google results: {str(e)}")
        
        return results

class SearchEngineManager:
    """Manages multiple search engines with fallback"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.engines = self._initialize_engines()
    
    def _initialize_engines(self) -> List[SearchEngine]:
        """Initialize available search engines in priority order"""
        engines = []
        
        # Google Custom Search (if configured)
        google_api_key = self.config.get('google_api_key')
        google_search_engine_id = self.config.get('google_search_engine_id')
        if google_api_key and google_search_engine_id:
            engines.append(GoogleCustomSearch(google_api_key, google_search_engine_id))
        
        # Bing Search (if configured)
        bing_api_key = self.config.get('bing_api_key')
        if bing_api_key:
            engines.append(BingSearch(bing_api_key))
        
        # DuckDuckGo (always available as fallback)
        engines.append(DuckDuckGoSearch())
        
        return engines
    
    async def search(self, query: str, limit: int = 10, **kwargs) -> List[SearchResult]:
        """Search using available engines with fallback"""
        logger.info(f"SearchEngineManager: Starting search for query '{query}' with {len(self.engines)} engines")
        
        for i, engine in enumerate(self.engines):
            try:
                logger.info(f"SearchEngineManager: Trying engine {i+1}/{len(self.engines)}: {engine.__class__.__name__}")
                async with engine:
                    results = await engine.search(query, limit, **kwargs)
                    logger.info(f"SearchEngineManager: {engine.__class__.__name__} returned {len(results)} results")
                    if results:
                        logger.info(f"Search successful using {engine.__class__.__name__}")
                        return results
                    else:
                        logger.warning(f"No results from {engine.__class__.__name__}")
            except Exception as e:
                logger.error(f"Search failed with {engine.__class__.__name__}: {str(e)}")
                continue
        
        logger.error("All search engines failed")
        return []

def validate_search_operators(query: str) -> bool:
    """Validate supported search operators in query"""
    # List of supported operators from FireCrawl documentation
    supported_operators = [
        r'"[^"]*"',           # Exact match with quotes
        r'-\w+',              # Exclude with minus
        r'site:\S+',          # Site-specific search
        r'inurl:\w+',         # URL contains word
        r'allinurl:[\w\s]+',  # URL contains all words
        r'intitle:\w+',       # Title contains word
        r'allintitle:[\w\s]+', # Title contains all words
        r'related:\S+'        # Related to domain
    ]
    
    # Check if query contains any unsupported complex operators
    # This is a basic validation - can be enhanced
    return True  # For now, allow all queries

async def perform_web_search(
    query: str,
    limit: int = 10,
    lang: str = "en",
    country: str = "us",
    tbs: str = None,
    timeout: int = 30,
    config: dict = None
) -> List[SearchResult]:
    """
    Perform web search using configured search engines
    
    Args:
        query: Search query with optional operators
        limit: Maximum number of results
        lang: Language code
        country: Country code
        tbs: Time-based search filter
        timeout: Request timeout in seconds
        config: Search engine configuration
    
    Returns:
        List of search results
    """
    # Validate query operators
    if not validate_search_operators(query):
        logger.warning(f"Query contains unsupported operators: {query}")
    
    # Initialize search manager
    search_manager = SearchEngineManager(config)
    
    # Perform search
    results = await search_manager.search(
        query=query,
        limit=limit,
        lang=lang,
        country=country,
        tbs=tbs,
        timeout=timeout
    )
    
    return results 