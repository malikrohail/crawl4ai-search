# Google Custom Search API Setup

## Why You Need This
DuckDuckGo has limited support for advanced search operators like:
- `site:github.com` - Search specific sites
- `inurl:tutorial` - Search URLs containing words
- `intitle:python` - Search page titles
- `filetype:pdf` - Search specific file types

Google Custom Search API provides full operator support and better results.

## Setup Steps

### 1. Get Google Custom Search API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the "Custom Search API"
4. Go to "Credentials" → "Create Credentials" → "API Key"
5. Copy your API key

### 2. Create Custom Search Engine
1. Go to [Google Custom Search](https://cse.google.com/cse/)
2. Click "Add" to create new search engine
3. In "Sites to search", enter `*` (to search entire web)
4. Click "Create"
5. Copy your "Search engine ID" from the control panel

### 3. Configure Crawl4AI
Add to your `deploy/docker/config.yml`:

```yaml
search_engines:
  google_api_key: "YOUR_GOOGLE_API_KEY_HERE"
  google_search_engine_id: "YOUR_SEARCH_ENGINE_ID_HERE"
  bing_api_key: ""  # Optional: Bing as backup
```

### 4. Test Configuration
```bash
curl -X POST "http://localhost:11234/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "site:github.com machine learning",
    "limit": 5
  }'
```

## Pricing
- **Free Tier**: 100 searches/day
- **Paid**: $5 per 1,000 queries (after free tier)
- Much cheaper than most alternatives

## Supported Operators
✅ `site:domain.com` - Search specific sites
✅ `inurl:keyword` - URL contains keyword  
✅ `intitle:keyword` - Title contains keyword
✅ `filetype:pdf` - Specific file types
✅ `"exact phrase"` - Exact phrase matching
✅ `-exclude` - Exclude terms
✅ `OR` - Boolean OR
✅ Time filters (`qdr:d`, `qdr:w`, etc.) 