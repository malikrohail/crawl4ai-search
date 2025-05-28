# 🚀 Crawl4AI API Endpoints Reference

## 📁 **API Code Location**
```
deploy/docker/
├── server.py          # Main FastAPI app with all endpoints
├── api.py            # Core API logic and handlers  
├── schemas.py        # Pydantic request/response models
├── auth.py           # JWT authentication
├── config.yml        # Configuration settings
├── utils.py          # Utility functions
├── crawler_pool.py   # Browser pool management
├── job.py            # Background job handling
└── mcp_bridge.py     # Model Context Protocol integration
```

## 🔗 **Complete API Endpoints List**

### **🏠 Core Application**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `GET` | `/` | Redirects to playground interface | ❌ |
| `GET` | `/playground` | Interactive API testing interface | ❌ |

### **🔐 Authentication & Configuration**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `POST` | `/token` | Generate JWT access token | ❌ |
| `POST` | `/config/dump` | Validate and dump config objects | ✅ |
| `GET` | `/schema` | Get BrowserConfig & CrawlerRunConfig schemas | ✅ |

### **📄 Content Extraction**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `POST` | `/md` | Convert webpage to markdown with filtering | ✅ |
| `POST` | `/html` | Get preprocessed HTML for schema extraction | ✅ |
| `POST` | `/crawl` | Main crawling endpoint (batch mode) | ✅ |
| `POST` | `/crawl/stream` | Streaming crawl for real-time results | ✅ |
| `POST` | `/search` | **NEW** Web search with optional content scraping | ✅ |

### **🖼️ Media Generation**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `POST` | `/screenshot` | Capture full-page PNG screenshots | ✅ |
| `POST` | `/pdf` | Generate PDF documents | ✅ |

### **⚡ Dynamic Interaction**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `POST` | `/execute_js` | Execute JavaScript on pages | ✅ |
| `GET` | `/llm/{url:path}` | LLM-powered Q&A using page content | ✅ |

### **📚 Context & Documentation**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `GET` | `/ask` | Search crawl4ai documentation/code context | ✅ |

### **🔧 Monitoring & Health**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `GET` | `/health` | Health check endpoint | ❌ |
| `GET` | `/metrics` | Prometheus metrics | ❌ |

### **🔌 MCP Integration**
| Method | Endpoint | Purpose | Auth Required |
|--------|----------|---------|---------------|
| `GET` | `/mcp/sse` | Server-Sent Events for MCP | ❌ |
| `GET` | `/mcp/schema` | MCP schema definition | ❌ |

---

## 📝 **Detailed Endpoint Documentation**

### **1. POST `/md` - Markdown Generation**
```python
# Request Body (MarkdownRequest)
{
    "url": "https://example.com",
    "f": "FIT",  # FilterType: RAW, FIT, BM25, LLM
    "q": "optional query for filtering",
    "c": "0"     # Cache control
}

# Response
{
    "url": "https://example.com",
    "filter": "FIT",
    "query": null,
    "cache": "0",
    "markdown": "# Page Title\n\nContent...",
    "success": true
}
```

### **2. POST `/crawl` - Main Crawling**
```python
# Request Body (CrawlRequest)
{
    "urls": ["https://example.com", "https://another.com"],
    "browser_config": {
        "headless": true,
        "user_agent": "custom-agent"
    },
    "crawler_config": {
        "cache_mode": "ENABLED",
        "extraction_strategy": {...}
    }
}

# Response
{
    "success": true,
    "results": [
        {
            "url": "https://example.com",
            "html": "<html>...",
            "markdown": {...},
            "success": true,
            "extracted_content": "...",
            "links": {...},
            "media": {...}
        }
    ],
    "server_processing_time_s": 2.5,
    "server_memory_delta_mb": 45.2
}
```

### **3. POST `/execute_js` - JavaScript Execution**
```python
# Request Body (JSEndpointRequest)
{
    "url": "https://example.com",
    "scripts": [
        "document.title",
        "window.scrollTo(0, document.body.scrollHeight)",
        "document.querySelectorAll('a').length"
    ]
}

# Response - Full CrawlResult object
{
    "url": "https://example.com",
    "html": "<html>...",
    "js_execution_result": {
        "script_0": "Page Title",
        "script_1": null,
        "script_2": 25
    },
    "success": true,
    # ... all other CrawlResult fields
}
```

### **4. GET `/llm/{url}` - LLM Q&A**
```python
# URL: /llm/https://example.com?q=What is the main topic?
# Response
{
    "answer": "The main topic of this page is..."
}
```

### **5. POST `/search` - Web Search with Scraping**
```python
# Request Body (SearchRequest)
{
    "query": "artificial intelligence latest news",
    "limit": 5,
    "tbs": "qdr:w",  # Time filter: past week
    "lang": "en",
    "country": "us",
    "scrapeOptions": {
        "formats": ["markdown", "html", "links"]
    },
    "ignoreInvalidURLs": true
}

# Response (SearchResponse)
{
    "success": true,
    "data": [
        {
            "title": "Latest AI Developments",
            "description": "Recent advances in artificial intelligence...",
            "url": "https://example.com/ai-news",
            "markdown": "# Latest AI Developments\n\nContent...",
            "html": "<html>...",
            "links": ["https://link1.com", "https://link2.com"],
            "metadata": {
                "title": "Latest AI Developments",
                "description": "Recent advances...",
                "sourceURL": "https://example.com/ai-news",
                "statusCode": 200,
                "error": null
            }
        }
    ],
    "warning": null
}

# Supported Query Operators:
# - "exact match"
# - site:domain.com
# - inurl:keyword
# - intitle:keyword
# - -exclude
# - related:domain.com
```

---

## 🛠️ **Adding Custom Endpoints**

### **Option 1: Extend Existing server.py**
```python
# Add to deploy/docker/server.py

@app.post("/custom/my-endpoint")
@limiter.limit(config["rate_limiting"]["default_limit"])
async def my_custom_endpoint(
    request: Request,
    body: MyCustomRequest,  # Define in schemas.py
    _td: Dict = Depends(token_dep),
):
    """Your custom endpoint logic"""
    # Your implementation here
    return JSONResponse({"result": "success"})
```

### **Option 2: Create New Module**
```python
# Create: deploy/docker/custom_endpoints.py

from fastapi import APIRouter, Depends, Request
from .auth import get_token_dependency
from .schemas import MyCustomRequest

router = APIRouter(prefix="/custom", tags=["custom"])

@router.post("/my-endpoint")
async def my_custom_endpoint(
    request: Request,
    body: MyCustomRequest,
    _td: Dict = Depends(get_token_dependency(config)),
):
    """Your custom endpoint"""
    return {"result": "success"}

# Then in server.py, add:
# from custom_endpoints import router as custom_router
# app.include_router(custom_router)
```

### **Option 3: Create Separate FastAPI App**
```python
# Create: my_custom_api/
# ├── main.py
# ├── endpoints.py
# └── models.py

# main.py
from fastapi import FastAPI
import httpx

app = FastAPI(title="My Custom Crawl4AI API")

# Proxy to existing crawl4ai API
crawl4ai_client = httpx.AsyncClient(base_url="http://localhost:11235")

@app.post("/simplified-crawl")
async def simplified_crawl(url: str):
    response = await crawl4ai_client.post("/md", json={
        "url": url,
        "f": "FIT"
    })
    data = response.json()
    return {"content": data["markdown"]}
```

---

## 📋 **Request/Response Models**

### **Existing Schemas (schemas.py)**
```python
class CrawlRequest(BaseModel):
    urls: List[str] = Field(min_length=1, max_length=100)
    browser_config: Optional[Dict] = Field(default_factory=dict)
    crawler_config: Optional[Dict] = Field(default_factory=dict)

class MarkdownRequest(BaseModel):
    url: str
    f: FilterType = FilterType.FIT  # RAW, FIT, BM25, LLM
    q: Optional[str] = None
    c: Optional[str] = "0"

class HTMLRequest(BaseModel):
    url: str

class ScreenshotRequest(BaseModel):
    url: str
    screenshot_wait_for: Optional[float] = 2
    output_path: Optional[str] = None

class PDFRequest(BaseModel):
    url: str
    output_path: Optional[str] = None

class JSEndpointRequest(BaseModel):
    url: str
    scripts: List[str]
```

---

## 🚀 **Quick Start for Custom Endpoints**

1. **Create your new folder structure:**
```bash
mkdir my_custom_api
cd my_custom_api
```

2. **Copy the base files you need:**
```bash
cp ../deploy/docker/schemas.py .
cp ../deploy/docker/auth.py .
cp ../deploy/docker/config.yml .
```

3. **Create your custom API:**
```python
# main.py
from fastapi import FastAPI, Depends
from schemas import CrawlRequest  # Reuse existing schemas
from auth import get_token_dependency
import httpx

app = FastAPI(title="My Custom Crawl4AI Wrapper")

# Your custom endpoints here
@app.post("/my-custom-crawl")
async def my_custom_crawl(request: CrawlRequest):
    # Your custom logic
    pass
```

4. **Run your custom API:**
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 💡 **Best Practices**

1. **Reuse existing schemas** when possible
2. **Use the same authentication pattern** for consistency
3. **Follow the same error handling patterns**
4. **Add rate limiting** for production endpoints
5. **Include proper logging** and monitoring
6. **Document your endpoints** with docstrings
7. **Use the existing crawler pool** for performance

---

## 🔍 **Rate Limiting & Security**

All endpoints use:
- **Rate limiting**: `@limiter.limit(config["rate_limiting"]["default_limit"])`
- **Authentication**: `_td: Dict = Depends(token_dep)`
- **MCP Integration**: `@mcp_tool("endpoint_name")` for AI tool access

Configure in `config.yml`:
```yaml
rate_limiting:
  enabled: true
  default_limit: "1000/minute"
  
security:
  enabled: true
  jwt_enabled: true
``` 