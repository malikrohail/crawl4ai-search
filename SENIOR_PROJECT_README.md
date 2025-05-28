# Crawl4AI Search API Extension - Senior Project

**Author**: Malik Salim  
**Institution**: Bennington College  
**Course**: Senior Plan  
**Year**: 2025

## 🎯 Project Overview

Extended the **Crawl4AI** web scraping framework by implementing a comprehensive **`/search`** endpoint that matches FireCrawl's functionality. This project demonstrates full-stack development with backend API implementation and frontend integration to the server on top of pre existing endpoints.

### 🚀 Key Achievements
- **Extended production codebase** with 4 new modules (1,100+ lines)
- **Multi-provider search engine** (Google, Bing, DuckDuckGo) with intelligent fallback
- **Comprehensive content extraction** (markdown, html, screenshots, links)
- **Frontend playground integration** for interactive testing
- **Production-ready API** with validation, error handling, and hosted screenshots

## 🏗️ Technical Implementation

### Files Created/Modified

#### New Files
- `search_engine.py` - Multi-provider search orchestration
- `search_endpoint.py` - FastAPI REST endpoint implementation  
- `search_schemas.py` - Pydantic data models
- `static/screenshots/` - Directory for hosted screenshot files

#### Modified Files
- `server.py` - Added /search endpoint integration
- `config.yml` - Search configuration settings
- `static/playground/index.html` - Frontend playground integration

### Frontend Integration
- **Interactive playground** at `http://localhost:11234/playground`
- **Seamless UI integration** with existing Crawl4AI interface
- **Real-time testing** with live response visualization
- **Format selection** via checkbox interface
- **Auto-generated code** (Python & cURL example for /search endpoint)

## 🔧 Core Features

### Multi-Provider Search
- **Google Custom Search** (primary) → **Bing API** (secondary) → **DuckDuckGo** (fallback)
- **Query operators**: `site:`, `intitle:`, `inurl:`, `-exclude`, `"exact phrase"`
- **Content formats**: markdown, html, rawHtml, links, screenshots
- **Localization**: Multiple languages and countries
- **Time filtering**: Recent results (hour/day/week/month/year)

## 🚀 Quick Setup

### 1. Install & Start
```bash
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
pip install -r requirements.txt


# Start server
cd deploy/docker
python server.py
```
Server runs on: `http://localhost:11234`

### 2. Configure Search APIs (Optional)

#### Option A: Environment Variables
```bash
export GOOGLE_API_KEY="your_google_api_key"
export GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"
export BING_API_KEY="your_bing_api_key"
```

#### Option B: YAML Configuration File
Edit `deploy/docker/config.yml` and add:
```yaml
# Search Engine Configuration
search:
  # Google Custom Search (Primary - Best Results)
  google_api_key: "your_google_api_key_here"
  google_search_engine_id: "your_search_engine_id_here"
  
  # Bing Search API (Secondary)
  bing_api_key: "your_bing_api_key_here"
  
  # Default Settings
  default_engine: "duckduckgo"  # Fallback when APIs fail
  default_limit: 10
  default_timeout: 30
  
# Application Configuration (existing)
app:
  title: "Crawl4AI API"
  version: "1.0.0"
  host: "0.0.0.0"
  port: 11234
  base_url: "http://localhost:11234"
```

**Note**: Without API keys, DuckDuckGo is used as fallback (works without configuration)

## 🧪 Testing Options

### Option 1: Interactive Playground (Recommended)
1. Open `http://localhost:11234/playground`
2. Select `/search` from dropdown
3. Enter query: `site:github.com python machine learning`
4. Select content formats (markdown, screenshot, links)
5. Configure options (limit, language, time filter)
6. Click "Run" to test
7. View results in Response/Python/cURL tabs

### Option 2: Direct API Testing
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "site:github.com python",
    "limit": 5,
    "scrapeOptions": {
      "formats": ["markdown", "screenshot", "links"]
    }
  }'
```

## 📊 Complete API Reference

### Endpoint
```
POST /search
Content-Type: application/json
```

### Request Parameters

#### Required Parameters
| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `query` | string | Search query with optional operators | `"site:github.com python"` |

#### Optional Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 5 | Number of results (1-50) |
| `lang` | string | "en" | Language code |
| `country` | string | "us" | Country code |
| `tbs` | string | null | Time filter |
| `ignoreInvalidUrls` | boolean | true | Skip invalid URLs |

### Available Formats (Users can also select all of them in a single request)
- `"markdown"` - Clean text content
- `"html"` - Structured HTML
- `"rawHtml"` - Complete page source
- `"links"` - Extracted hyperlinks
- `"screenshot"` - Visual page capture

### Complete Request Example
```json
{
  "query": "site:github.com machine learning -tensorflow",
  "limit": 10,
  "lang": "en",
  "country": "us",
  "tbs": "qdr:m",
  "scrapeOptions": {
    "formats": ["markdown", "html", "screenshot", "links"]
  },
  "ignoreInvalidUrls": true
}
```

### Response Format
```json
{
  "success": true,
  "data": [
    {
      "title": "Page Title",
      "description": "Page description from search results",
      "url": "https://example.com",
      "markdown": "# Page Content\n\nClean markdown text...",
      "html": "<div>Structured HTML content...</div>",
      "rawHtml": "<!DOCTYPE html><html>...</html>",
      "links": [
        "https://example.com/link1",
        "https://example.com/link2"
      ],
      "screenshot": "http://localhost:11234/static/screenshots/uuid.png"
    }
  ],
  "metadata": {
    "searchEngine": "duckduckgo",
    "totalResults": 10,
    "searchTime": "2.34s",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Invalid query parameter",
  "details": "Query cannot be empty"
}
```

## 🔍 Usage Examples

### Basic Search
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "python tutorial", "limit": 3}'
```

### Site-Specific Search
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "site:github.com machine learning",
    "limit": 5,
    "scrapeOptions": {"formats": ["markdown", "links"]}
  }'
```

### Advanced Search with Filters
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "intitle:\"python tutorial\" -beginner",
    "limit": 5,
    "lang": "en",
    "country": "us",
    "tbs": "qdr:m",
    "scrapeOptions": {"formats": ["markdown", "screenshot"]}
  }'
```

### Full Content Extraction
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "python documentation",
    "limit": 2,
    "scrapeOptions": {
      "formats": ["markdown", "html", "rawHtml", "links", "screenshot"]
    }
  }'
```

## 🧪 Validation & Performance

✅ Multi-provider search with intelligent fallback  
✅ All content formats working correctly  
✅ Query operators and time filtering supported  
✅ Screenshot hosting implemented  
✅ Frontend playground integration complete  
✅ Production-ready with robust error handling  

**Performance**: 5-10 second response time, 10+ concurrent requests supported

## 🔍 vs FireCrawl

| Feature | FireCrawl | This Implementation |
|---------|-----------|-------------------|
| Web Search | ✅ | ✅ Complete |
| Content Formats | ✅ | ✅ Complete |
| Screenshots | ✅ | ✅ Complete |
| Query Operators | ✅ | ✅ Complete |
| Provider Fallback | ❌ | ✅ **Enhanced** |

## 🏆 Skills Demonstrated

- **Full-Stack Development**: Backend API + Frontend integration
- **Production Code Extension**: Enhanced existing codebase
- **Multi-provider Integration**: Robust fallback system
- **API Design**: RESTful endpoint with comprehensive validation


## 🎓 Project Impact

Successfully extended a production web scraping framework with commercial-grade search functionality:
- ✅ **Feature parity** with paid services (FireCrawl)
- ✅ **Enhanced reliability** through multi-provider architecture  
- ✅ **User-friendly testing** via integrated playground interface
- ✅ **Production deployment** ready for real-world usage 
## 📁 Repository Structure

When you explore this repository, you'll find the following key files for the `/search` endpoint:

### Core Implementation Files
```
crawl4ai/
├── deploy/docker/
│   ├── search_engine.py          # Multi-provider search engine
│   ├── search_endpoint.py        # FastAPI endpoint handler
│   ├── search_schemas.py         # Request/response models
│   ├── server.py                 # Modified to include /search
│   ├── config.yml               # Updated with search settings
│   └── static/
│       ├── playground/
│       │   └── index.html       # Enhanced with search UI
│       └── screenshots/         # Hosted screenshot directory
├── docs/
│   └── SEARCH_IMPLEMENTATION_SUMMARY.md  # Technical notes
└── SENIOR_PROJECT_README.md     # This documentation
```

### Key Files to Review
1. **`search_engine.py`** - Core search logic with multi-provider fallback
2. **`search_endpoint.py`** - API endpoint implementation
3. **`search_schemas.py`** - Data validation models
4. **`static/playground/index.html`** - Frontend integration (search for `/search` sections)
5. **`server.py`** - Look for search endpoint registration
6. **`SENIOR_PROJECT_README.md`** - Complete project documentation

## 🔮 Future Enhancements

- **Rate Limiting**: Request throttling and quotas
- **Caching**: Redis-based result caching
- **Webhooks**: Asynchronous result delivery
- **Batch Processing**: Multiple query handling
- **Custom Extractors**: User-defined content rules

---