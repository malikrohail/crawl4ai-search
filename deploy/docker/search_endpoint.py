"""
Search Endpoint Implementation for Crawl4AI
Integrates web search with crawl4ai's scraping capabilities
"""

import asyncio
import logging
import time
import base64
import uuid
import os
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from urllib.parse import urlparse
import validators

from search_engine import perform_web_search, SearchResult as EngineSearchResult
from search_schemas import SearchRequest, SearchResponse, SearchResult, SearchResultMetadata
from api import handle_crawl_request  # Import existing crawl functionality
from schemas import CrawlRequest
from crawl4ai import BrowserConfig, CrawlerRunConfig

logger = logging.getLogger(__name__)

class SearchService:
    """Service class for handling search operations"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.search_config = self.config.get('search', {})
        # Create screenshots directory if it doesn't exist
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), "static", "screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def _save_screenshot_to_file(self, base64_data: str) -> str:
        """Save base64 screenshot data to file and return URL"""
        try:
            # Generate unique filename
            screenshot_id = str(uuid.uuid4())
            filename = f"screenshot-{screenshot_id}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Decode and save base64 data
            image_data = base64.b64decode(base64_data)
            with open(filepath, 'wb') as f:
                f.write(image_data)
            
            # Return URL (assuming server serves static files)
            base_url = self.config.get('app', {}).get('base_url', 'http://localhost:11234')
            screenshot_url = f"{base_url}/static/screenshots/{filename}"
            
            logger.info(f"Screenshot saved: {screenshot_url}")
            return screenshot_url
            
        except Exception as e:
            logger.error(f"Failed to save screenshot: {str(e)}")
            return base64_data  # Return original base64 as fallback
    
    async def search_and_scrape(self, request: SearchRequest) -> SearchResponse:
        """
        Perform web search and optionally scrape results
        
        Args:
            request: Search request parameters
            
        Returns:
            SearchResponse with search results and optional scraped content
        """
        start_time = time.time()
        
        try:
            # Step 1: Perform web search
            logger.info(f"Performing web search for query: {request.query}")
            search_results = await self._perform_search(request)
            
            if not search_results:
                logger.warning(f"No search results found for query: {request.query}")
                return SearchResponse(
                    success=True,
                    data=[],
                    warning="No search results found"
                )
            
            # Step 2: Process results and optionally scrape content
            processed_results = await self._process_search_results(
                search_results, request
            )
            
            # Step 3: Filter invalid URLs if requested
            if request.ignoreInvalidURLs:
                processed_results = self._filter_valid_urls(processed_results)
            
            processing_time = time.time() - start_time
            logger.info(f"Search completed in {processing_time:.2f}s, found {len(processed_results)} results")
            
            return SearchResponse(
                success=True,
                data=processed_results
            )
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Search operation failed: {str(e)}"
            )
    
    async def _perform_search(self, request: SearchRequest) -> List[EngineSearchResult]:
        """Perform the actual web search"""
        try:
            logger.info(f"SearchService: Starting web search for '{request.query}' with config: {self.search_config}")
            results = await perform_web_search(
                query=request.query,
                limit=request.limit,
                lang=request.lang,
                country=request.country,
                tbs=request.tbs,
                timeout=request.timeout // 1000,  # Convert to seconds
                config=self.search_config
            )
            logger.info(f"SearchService: perform_web_search returned {len(results)} results")
            for i, result in enumerate(results):
                logger.info(f"SearchService: Result {i+1}: {result.title} - {result.url}")
            return results
        except Exception as e:
            logger.error(f"Web search failed: {str(e)}")
            return []
    
    async def _process_search_results(
        self, 
        search_results: List[EngineSearchResult], 
        request: SearchRequest
    ) -> List[SearchResult]:
        """Process search results and optionally scrape content"""
        processed_results = []
        
        # Check if scraping is requested
        should_scrape = request.scrapeOptions is not None
        
        if should_scrape:
            # Scrape content from search result URLs
            scraped_results = await self._scrape_search_results(
                search_results, request.scrapeOptions
            )
            processed_results = scraped_results
        else:
            # Return basic search results without scraping
            for result in search_results:
                processed_results.append(SearchResult(
                    title=result.title,
                    description=result.description,
                    url=result.url,
                    metadata=SearchResultMetadata(
                        title=result.title,
                        description=result.description,
                        sourceURL=result.url
                    )
                ))
        
        return processed_results
    
    async def _scrape_search_results(
        self, 
        search_results: List[EngineSearchResult], 
        scrape_options: Dict[str, Any]
    ) -> List[SearchResult]:
        """Scrape content from search result URLs using crawl4ai"""
        urls = [result.url for result in search_results]
        
        try:
            # Prepare crawl request using existing crawl4ai infrastructure
            browser_config = {}
            
            # Convert formats to crawl4ai parameters
            formats = scrape_options.get('formats', ['markdown'])
            crawler_config = {
                "cache_mode": "BYPASS",  # Don't cache search results
                "screenshot": "screenshot" in formats,  # Enable screenshot if requested
                **{k: v for k, v in scrape_options.items() if k != 'formats'}  # Pass other options
            }
            
            # Use existing crawl functionality
            crawl_response = await handle_crawl_request(
                urls=urls,
                browser_config=browser_config,
                crawler_config=crawler_config,
                config=self.config  # Pass the service config
            )
            
            # Convert crawl results to search results
            processed_results = []
            crawl_results = crawl_response.get('results', [])
            for i, (search_result, crawl_result) in enumerate(zip(search_results, crawl_results)):
                try:
                    # Determine which formats were requested
                    formats = scrape_options.get('formats', ['markdown'])
                    
                    search_result_data = SearchResult(
                        title=search_result.title,
                        description=search_result.description,
                        url=search_result.url,
                        metadata=SearchResultMetadata(
                            title=crawl_result.get('metadata', {}).get('title', search_result.title),
                            description=crawl_result.get('metadata', {}).get('description', search_result.description),
                            sourceURL=search_result.url,
                            statusCode=crawl_result.get('status_code'),
                            error=crawl_result.get('error_message')
                        )
                    )
                    
                    # Add requested content formats
                    if 'markdown' in formats and crawl_result.get('markdown'):
                        # Handle markdown structure
                        markdown_data = crawl_result.get('markdown')
                        if isinstance(markdown_data, dict):
                            search_result_data.markdown = markdown_data.get('fit_markdown') or markdown_data.get('raw_markdown')
                        else:
                            search_result_data.markdown = markdown_data
                    
                    if 'html' in formats and crawl_result.get('cleaned_html'):
                        search_result_data.html = crawl_result.get('cleaned_html')
                    
                    if 'rawHtml' in formats and crawl_result.get('html'):
                        search_result_data.rawHtml = crawl_result.get('html')
                    
                    if 'links' in formats and crawl_result.get('links'):
                        links_data = crawl_result.get('links', {})
                        all_links = []
                        if isinstance(links_data, dict):
                            internal_links = links_data.get('internal', [])
                            external_links = links_data.get('external', [])
                            all_links = [link.get('href') for link in internal_links + external_links if link.get('href')]
                        search_result_data.links = all_links
                    
                    if 'screenshot' in formats and crawl_result.get('screenshot'):
                        search_result_data.screenshot = self._save_screenshot_to_file(crawl_result.get('screenshot'))
                    
                    processed_results.append(search_result_data)
                    
                except Exception as e:
                    logger.warning(f"Error processing crawl result {i}: {str(e)}")
                    # Add basic result even if scraping failed
                    processed_results.append(SearchResult(
                        title=search_result.title,
                        description=search_result.description,
                        url=search_result.url,
                        metadata=SearchResultMetadata(
                            title=search_result.title,
                            description=search_result.description,
                            sourceURL=search_result.url,
                            error=str(e)
                        )
                    ))
            
            return processed_results
            
        except Exception as e:
            logger.error(f"Failed to scrape search results: {str(e)}")
            # Return basic results if scraping fails
            return [
                SearchResult(
                    title=result.title,
                    description=result.description,
                    url=result.url,
                    metadata=SearchResultMetadata(
                        title=result.title,
                        description=result.description,
                        sourceURL=result.url,
                        error="Scraping failed"
                    )
                )
                for result in search_results
            ]
    
    def _filter_valid_urls(self, results: List[SearchResult]) -> List[SearchResult]:
        """Filter out results with invalid URLs"""
        valid_results = []
        
        for result in results:
            try:
                # Validate URL format
                if validators.url(result.url):
                    # Additional checks for common issues
                    parsed = urlparse(result.url)
                    if parsed.scheme in ['http', 'https'] and parsed.netloc:
                        valid_results.append(result)
                    else:
                        logger.debug(f"Filtered invalid URL: {result.url}")
                else:
                    logger.debug(f"Filtered invalid URL format: {result.url}")
            except Exception as e:
                logger.debug(f"Error validating URL {result.url}: {str(e)}")
                continue
        
        return valid_results

# Global search service instance
search_service = None

def get_search_service(config: dict = None) -> SearchService:
    """Get or create search service instance"""
    global search_service
    if search_service is None:
        search_service = SearchService(config)
    return search_service

async def handle_search_request(request: SearchRequest, config: dict = None) -> SearchResponse:
    """
    Handle search request - main entry point for search endpoint
    
    Args:
        request: Search request parameters
        config: Application configuration
        
    Returns:
        SearchResponse with results
    """
    service = get_search_service(config)
    return await service.search_and_scrape(request) 