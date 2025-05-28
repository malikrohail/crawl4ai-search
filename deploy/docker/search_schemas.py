"""
Pydantic models for the search API endpoint
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    limit: int = Field(default=5, ge=1, le=50, description="Max results")
    tbs: Optional[str] = Field(default=None, description="Time filter")
    lang: str = Field(default="en", description="Language")
    country: str = Field(default="us", description="Country")
    location: Optional[str] = Field(default=None, description="Location")
    timeout: int = Field(default=60000, ge=1000, le=300000, description="Timeout ms")
    ignoreInvalidURLs: bool = Field(default=False, description="Skip bad URLs")
    scrapeOptions: Optional[Dict[str, Any]] = Field(default=None, description="Scrape config")

class SearchResultMetadata(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    sourceURL: str
    statusCode: Optional[int] = None
    error: Optional[str] = None

class SearchResult(BaseModel):
    title: str
    description: str
    url: str
    # Content in different formats
    markdown: Optional[str] = None
    html: Optional[str] = None
    rawHtml: Optional[str] = None
    links: Optional[List[str]] = None
    screenshot: Optional[str] = None
    metadata: Optional[SearchResultMetadata] = None

class SearchResponse(BaseModel):
    success: bool
    data: List[SearchResult]
    warning: Optional[str] = None

class SearchEngine(str, Enum):
    GOOGLE = "google"
    BING = "bing"
    DUCKDUCKGO = "duckduckgo"