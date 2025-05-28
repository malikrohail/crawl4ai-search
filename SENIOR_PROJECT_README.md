# Crawl4AI Search API Extension - Senior Project

**Author**: Malik Salim  
**Institution**: Bennington College  
**Project**: Senior Plan (Capstone Project)
**Year**: 2025

## 🎯 Project Overview

Extended the **Crawl4AI** web scraping framework by implementing a comprehensive **`/search`** endpoint that matches FireCrawl's functionality. This project demonstrates full-stack development with backend API implementation and frontend integration to the server on top of pre existing endpoints.

### 🚀 Key Achievements
- **Extended production codebase** with 4 new modules (1,100+ lines)
- **Multi-provider search engine** (Google, Bing, DuckDuckGo) with intelligent fallback
- **Comprehensive content extraction** (markdown, html, screenshots, links)
- **Frontend playground integration** for interactive testing
- **Production-ready API** with validation, error handling

## 🏗️ Technical Implementation

### Files Created/Modified for This Project

#### Core Backend Files (New)
```
deploy/docker/
├── search_engine.py          # Multi-provider search orchestration
├── search_endpoint.py        # FastAPI REST endpoint implementation  
├── search_schemas.py         # Pydantic data models
└── static/screenshots/       # Directory for hosted screenshot files
```

#### Modified Existing Files
```
deploy/docker/
├── server.py                 #  Added /search endpoint integration
├── config.yml               #  Search configuration settings
└── static/playground/
    └── index.html           # Frontend playground integration
```

#### Documentation Files (New)
```
├── SENIOR_PROJECT_README.md  # Complete project documentation
```


### Frontend Integration
- **Interactive playground** at `http://localhost:11234/playground`
- **Seamless UI integration** with existing Crawl4AI interface
- **Real-time testing** with live response visualization
- **Format selection** via checkbox interface
- **Auto-generated code** (Python & cURL example for /search endpoint)

## 🔧 Core Features

### Multi-Provider Search Engine
- **Primary**: Google Custom Search API (requires API key)
- **Secondary**: Bing Search API (requires API key)
- **Fallback**: DuckDuckGo (no API key required)

### Query Operators Support
- `site:github.com` - Search within specific domains
- `intitle:"machine learning"` - Search in page titles
- `inurl:tutorial` - Search in URLs
- `-exclude` - Exclude terms from results
- `"exact phrase"` - Exact phrase matching

### Content Format Extraction
- **Markdown**: Clean, structured text content
- **HTML**: Processed HTML for further parsing
- **Raw HTML**: Original page HTML source
- **Links**: Extracted internal and external hyperlinks
- **Screenshots**: Full-page PNG captures with hosted URLs

### Localization & Filtering
- **Language**: `en`, `es`, `fr`, `de`, `zh`, `ja`
- **Country**: `us`, `uk`, `ca`, `au`, `de`, `fr`
- **Time filters**: `qdr:h` (hour), `qdr:d` (day), `qdr:w` (week), `qdr:m` (month), `qdr:y` (year)

## 🚀 Quick Setup

### 1. Install & Start
```bash
git clone https://github.com/unclecode/crawl4ai.git
cd crawl4ai
pip install -r requirements.txt
pip install google-api-python-client duckduckgo-search
pip install -e .

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

#### Option B: Config File
Edit `deploy/docker/config.yml`:
```yaml
search:
  google_api_key: "your_google_api_key"
  google_search_engine_id: "your_search_engine_id"
  bing_api_key: "your_bing_api_key"
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

## 🧪 Validation Results

### Test Coverage
```
✅ Multi-provider search with intelligent fallback
✅ All content formats working correctly
✅ Query operators fully supported
✅ Screenshot hosting implemented
✅ Frontend playground integration complete
✅ Error handling and validation robust
✅ Production-ready deployment
✅ API specification compliance
```

### Performance Metrics
- **Average response time**: 5-10 seconds
- **Concurrent requests**: 10+ supported

## 🔍 Comparison with FireCrawl

| Feature | FireCrawl | This Implementation | Status |
|---------|-----------|-------------------|---------|
| Web Search | ✅ | ✅ | **Complete** |
| Content Formats (HTML, JSON, Markdown) | ✅ | ✅ | **Complete** |
| Screenshots | ✅ | ✅ | **Complete**  |
| Query Operators | ✅ | ✅ | **Complete** |
| Time Filtering | ✅ | ✅ | **Complete** |

## 🏆 Technical Skills Demonstrated

### Backend Development
- **API Design**: RESTful endpoint with comprehensive validation
- **Multi-provider Integration**: Robust fallback system
- **Error Handling**: Graceful degradation and detailed error messages
- **Content Processing**: Multiple format extraction and hosting
- **Performance**: Efficient async request handling

### Frontend Development
- **UI Integration**: Added the search api endpoint to playground enhancement
- **Code Generation**: Automatic Python/cURL examples
