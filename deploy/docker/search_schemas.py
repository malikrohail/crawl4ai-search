"""
Search API Schemas for Crawl4AI
Matches FireCrawl's search endpoint structure
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class SearchRequest(BaseModel):
    """Request schema for web search endpoint"""
    query: str = Field(..., description="The search query")
    limit: int = Field(default=5, ge=1, le=50, description="Number of search results to return")
    tbs: Optional[str] = Field(default=None, description="Time-based search filters (e.g., 'qdr:w' for past week)")
    lang: str = Field(default="en", description="Language code (e.g., 'en', 'es', 'fr')")
    country: str = Field(default="us", description="Country code (e.g., 'us', 'uk', 'ca')")
    location: Optional[str] = Field(default=None, description="Specific location for localized results")
    timeout: int = Field(default=60000, ge=1000, le=300000, description="Timeout in milliseconds")
    ignoreInvalidURLs: bool = Field(default=False, description="Whether to ignore invalid URLs")
    scrapeOptions: Optional[Dict[str, Any]] = Field(default=None, description="Options for scraping search results")

class SearchResultMetadata(BaseModel):
    """Metadata for search result"""
    title: Optional[str] = None
    description: Optional[str] = None
    sourceURL: str
    statusCode: Optional[int] = None
    error: Optional[str] = None

class SearchResult(BaseModel):
    """Individual search result"""
    title: str
    description: str
    url: str
    markdown: Optional[str] = None
    html: Optional[str] = None
    rawHtml: Optional[str] = None
    links: Optional[List[str]] = None
    screenshot: Optional[str] = None
    metadata: Optional[SearchResultMetadata] = None

class SearchResponse(BaseModel):
    """Response schema for web search endpoint"""
    success: bool
    data: List[SearchResult]
    warning: Optional[str] = None

class SearchEngine(str, Enum):
    """Supported search engines"""
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"
    SEARX = "searx" 