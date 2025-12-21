# Web Search Setup Guide - Better Context Gathering

## Problem
DuckDuckGo often returns 0 results, limiting context gathering. This guide shows how to use better search APIs.

## Available Search Engines (Priority Order)

### 1. **SerpAPI** (Recommended - Best Results)
- **Pros**: Most reliable, Google-quality results, easy to use
- **Cons**: Paid service (free tier: 100 searches/month)
- **Setup**:
  ```bash
  # Get API key from https://serpapi.com/
  # Add to .env file:
  SERPAPI_KEY=your_serpapi_key_here
  WEB_SEARCH_ENGINE=serpapi
  ```

### 2. **Google Custom Search API** (Good Alternative)
- **Pros**: Official Google API, reliable results
- **Cons**: Requires Google Cloud setup, limited free tier
- **Setup**:
  1. Go to https://programmablesearchengine.google.com/
  2. Create a Custom Search Engine
  3. Get your Search Engine ID (CX)
  4. Get API key from Google Cloud Console
  5. Add to .env:
     ```bash
     GOOGLE_SEARCH_API_KEY=your_google_api_key
     GOOGLE_SEARCH_CX=your_search_engine_id
     WEB_SEARCH_ENGINE=google
     ```

### 3. **Tavily API** (AI-Powered Research)
- **Pros**: Designed for research, AI-optimized results
- **Cons**: Paid service
- **Setup**:
  ```bash
  # Get API key from https://tavily.com/
  TAVILY_API_KEY=your_tavily_key_here
  WEB_SEARCH_ENGINE=tavily
  ```

### 4. **DuckDuckGo** (Default - Free but Limited)
- **Pros**: Free, no API key needed
- **Cons**: Often returns 0 results, unreliable
- **Setup**: No setup needed (default)

## Auto-Detection

If you set `WEB_SEARCH_ENGINE=auto`, the system will automatically use the best available API:
1. SerpAPI (if key is set)
2. Google Custom Search (if keys are set)
3. Tavily (if key is set)
4. DuckDuckGo (fallback)

## Improvements Made

### 1. **Multiple Search Queries**
- Tries different query variations if first search fails
- Falls back to simpler queries
- Uses Wikipedia as additional fallback

### 2. **Better Company Filtering**
- Filters out false positives like "Silicon Valley" (location)
- Removes generic terms like "Partial Swipe File"
- Limits to top 3 companies (was 5) for better quality

### 3. **Fallback Chain**
- Tries primary search engine
- Falls back to other available engines automatically
- Last resort: DuckDuckGo

### 4. **Wikipedia Integration**
- Uses Wikipedia API for company information when web search fails
- Provides reliable company descriptions

## Quick Setup (Recommended)

**For best results, use SerpAPI:**

1. Sign up at https://serpapi.com/ (free tier: 100 searches/month)
2. Get your API key
3. Add to `backend/.env`:
   ```
   SERPAPI_KEY=your_key_here
   WEB_SEARCH_ENGINE=auto
   ```
4. Restart backend

That's it! The system will automatically use SerpAPI for much better search results.

## Testing

After setup, test by uploading a document with a company name. You should see:
```
[WebResearch] SerpAPI search: Found X results for 'Company Name company information'
```

Instead of:
```
[WebResearch] DuckDuckGo HTML: Found 0 results...
```

## Cost Comparison

- **SerpAPI**: $50/month for 5,000 searches (or free tier: 100/month)
- **Google Custom Search**: Free tier: 100 searches/day
- **Tavily**: Check pricing at tavily.com
- **DuckDuckGo**: Free but unreliable

## Recommendation

For production use, **SerpAPI** is the best balance of cost and reliability. The free tier (100 searches/month) is enough for testing, and paid plans are affordable for production.














