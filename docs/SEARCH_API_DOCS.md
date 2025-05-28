# 🔍 Crawl4AI Search API Documentation

## Overview

The Crawl4AI Search API provides web search capabilities with optional content scraping, matching [FireCrawl's Search API](https://docs.firecrawl.dev/api-reference/endpoint/search) functionality. This endpoint combines web search (SERP) with Crawl4AI's powerful scraping capabilities to return full page content for any query.

## 🚀 Quick Start

### Basic Search Request
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "artificial intelligence latest news",
    "limit": 5
  }'
```

### Search with Content Scraping
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python web scraping tutorial",
    "limit": 3,
    "scrapeOptions": {
      "formats": ["markdown", "html"]
    }
  }'
```

## 📋 API Reference

### Endpoint
```
POST /search
```

### Request Headers
```
Content-Type: application/json
Authorization: Bearer <token>  # If authentication is enabled
```

### Request Body Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | ✅ Yes | - | The search query with optional operators |
| `limit` | integer | ❌ No | 5 | Number of search results (1-50) |
| `tbs` | string | ❌ No | null | Time-based search filters |
| `lang` | string | ❌ No | "en" | Language code (e.g., 'en', 'es', 'fr') |
| `country` | string | ❌ No | "us" | Country code (e.g., 'us', 'uk', 'ca') |
| `location` | string | ❌ No | null | Specific location for localized results |
| `timeout` | integer | ❌ No | 60000 | Timeout in milliseconds (1000-300000) |
| `ignoreInvalidURLs` | boolean | ❌ No | false | Whether to ignore invalid URLs |
| `scrapeOptions` | object | ❌ No | null | Options for scraping search results |

### scrapeOptions Object

| Parameter | Type | Description |
|-----------|------|-------------|
| `formats` | array | Content formats to return: `["markdown", "html", "rawHtml", "links", "screenshot"]` |
| `cache_mode` | string | Cache mode: `"ENABLED"`, `"DISABLED"`, `"BYPASS"` |
| Additional crawl4ai options | - | Any valid crawl4ai configuration options |

### Response Structure

```json
{
  "success": boolean,
  "data": [
    {
      "title": "string",
      "description": "string", 
      "url": "string",
      "markdown": "string",      // If requested in scrapeOptions
      "html": "string",          // If requested in scrapeOptions
      "rawHtml": "string",       // If requested in scrapeOptions
      "links": ["string"],       // If requested in scrapeOptions
      "screenshot": "string",    // If requested in scrapeOptions
      "metadata": {
        "title": "string",
        "description": "string",
        "sourceURL": "string",
        "statusCode": integer,
        "error": "string"
      }
    }
  ],
  "warning": "string"           // Optional warning message
}
```

## 🔍 Supported Query Operators

The Search API supports various query operators to refine your search:

| Operator | Functionality | Example |
|----------|---------------|---------|
| `""` | Exact match for a string of text | `"machine learning"` |
| `-` | Excludes certain keywords | `python -django` |
| `site:` | Only returns results from a specified website | `site:github.com` |
| `inurl:` | Only returns results that include a word in the URL | `inurl:tutorial` |
| `allinurl:` | Only returns results that include multiple words in the URL | `allinurl:python tutorial` |
| `intitle:` | Only returns results that include a word in the title | `intitle:API` |
| `allintitle:` | Only returns results that include multiple words in the title | `allintitle:web scraping guide` |
| `related:` | Only returns results that are related to a specific domain | `related:stackoverflow.com` |

## ⏰ Time-Based Search Filters

Use the `tbs` parameter for time-based filtering:

| Filter | Description |
|--------|-------------|
| `qdr:h` | Past hour |
| `qdr:d` | Past day |
| `qdr:w` | Past week |
| `qdr:m` | Past month |
| `qdr:y` | Past year |

## 🌍 Localization

### Language Codes
Common language codes: `en`, `es`, `fr`, `de`, `it`, `pt`, `ru`, `ja`, `ko`, `zh`

### Country Codes  
Common country codes: `us`, `uk`, `ca`, `au`, `de`, `fr`, `es`, `it`, `jp`, `kr`

## 📝 Usage Examples

### 1. Basic Web Search
```json
{
  "query": "latest AI developments",
  "limit": 10,
  "lang": "en",
  "country": "us"
}
```

### 2. Site-Specific Search
```json
{
  "query": "site:stackoverflow.com python async",
  "limit": 5
}
```

### 3. Time-Filtered Search
```json
{
  "query": "cryptocurrency news",
  "limit": 8,
  "tbs": "qdr:w",
  "lang": "en"
}
```

### 4. Search with Full Content Scraping
```json
{
  "query": "FastAPI documentation",
  "limit": 3,
  "scrapeOptions": {
    "formats": ["markdown", "html", "links"],
    "cache_mode": "BYPASS"
  },
  "ignoreInvalidURLs": true
}
```

### 5. Exact Match Search
```json
{
  "query": "\"web scraping best practices\"",
  "limit": 5,
  "scrapeOptions": {
    "formats": ["markdown"]
  }
}
```

### 6. Exclude Terms Search
```json
{
  "query": "python tutorial -beginner",
  "limit": 7,
  "lang": "en"
}
```

## 🔧 Search Engine Configuration

The API supports multiple search engines with automatic fallback:

1. **Google Custom Search** (requires API key + Search Engine ID)
2. **Bing Search** (requires API key)  
3. **DuckDuckGo** (no API key required - default fallback)

### Environment Variables
```bash
# Optional: Google Custom Search
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_ENGINE_ID=your_search_engine_id

# Optional: Bing Search  
BING_API_KEY=your_bing_api_key
```

### Configuration in config.yml
```yaml
search:
  google_api_key: ""  # Set via GOOGLE_API_KEY env var
  google_search_engine_id: ""  # Set via GOOGLE_SEARCH_ENGINE_ID env var
  bing_api_key: ""  # Set via BING_API_KEY env var
  default_engine: "duckduckgo"
  default_limit: 10
  default_timeout: 30
  default_lang: "en"
  default_country: "us"
```

## 🚨 Error Handling

### Common Error Responses

#### 400 Bad Request
```json
{
  "detail": "Invalid query parameter"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Search operation failed: <error_message>"
}
```

#### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

## 🔒 Authentication

If authentication is enabled, include the Bearer token:

```bash
curl -X POST "http://localhost:11234/search" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"query": "test search"}'
```

## ⚡ Performance Tips

1. **Use specific queries** - More specific queries return better results faster
2. **Limit results** - Use appropriate `limit` values (5-10 for most use cases)
3. **Cache when possible** - Don't use `"cache_mode": "BYPASS"` unless necessary
4. **Filter invalid URLs** - Set `"ignoreInvalidURLs": true` for cleaner results
5. **Choose formats wisely** - Only request the content formats you actually need

## 🔄 Comparison with FireCrawl

| Feature | Crawl4AI Search | FireCrawl Search | Status |
|---------|----------------|------------------|---------|
| Basic web search | ✅ | ✅ | ✅ Compatible |
| Query operators | ✅ | ✅ | ✅ Compatible |
| Time-based filters | ✅ | ✅ | ✅ Compatible |
| Content scraping | ✅ | ✅ | ✅ Compatible |
| Multiple formats | ✅ | ✅ | ✅ Compatible |
| Localization | ✅ | ✅ | ✅ Compatible |
| Rate limiting | ✅ | ✅ | ✅ Compatible |
| Authentication | ✅ | ✅ | ✅ Compatible |
| Multiple search engines | ✅ | ❌ | 🚀 **Enhanced** |
| Free tier (DuckDuckGo) | ✅ | ❌ | 🚀 **Enhanced** |

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_search_api.py
```

This will test:
- Basic search functionality
- Content scraping with multiple formats
- Query operators
- Time-based filtering
- Error handling
- Performance metrics

## 🤝 Integration Examples

### Python
```python
import aiohttp
import asyncio

async def search_and_scrape(query: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "query": query,
            "limit": 5,
            "scrapeOptions": {"formats": ["markdown"]}
        }
        async with session.post(
            "http://localhost:11234/search",
            json=payload
        ) as response:
            return await response.json()

# Usage
results = asyncio.run(search_and_scrape("python tutorials"))
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

async function searchAndScrape(query) {
  const response = await axios.post('http://localhost:11234/search', {
    query: query,
    limit: 5,
    scrapeOptions: { formats: ['markdown'] }
  });
  return response.data;
}

// Usage
searchAndScrape('javascript tutorials').then(console.log);
```

### cURL
```bash
#!/bin/bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "'"$1"'",
    "limit": 5,
    "scrapeOptions": {"formats": ["markdown"]}
  }' | jq '.'
```

## 📚 Additional Resources

- [Crawl4AI Documentation](https://crawl4ai.com/mkdocs/)
- [FireCrawl API Reference](https://docs.firecrawl.dev/api-reference/endpoint/search)
- [Search Engine Optimization Guide](https://developers.google.com/search)
- [Web Scraping Best Practices](https://blog.apify.com/web-scraping-best-practices/)

---

**🎉 The Crawl4AI Search API provides a powerful, FireCrawl-compatible search solution with enhanced features like multiple search engines and free tier support!** 