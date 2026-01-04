# Perplexity API Setup Guide

This guide explains how to set up and use Perplexity API for enhanced web search functionality in the application.

## What is Perplexity API?

Perplexity API provides AI-powered real-time web search that combines the accuracy of traditional search engines with AI understanding. It's particularly useful for:

- Real-time information retrieval
- Comprehensive research queries
- Getting AI-summarized answers with citations
- Finding current information and trends

## Setup Instructions

### 1. Get a Perplexity API Key

1. **Sign up for Perplexity**: Visit [perplexity.ai](https://www.perplexity.ai)
2. **Navigate to API section**: Go to your account settings and find the API section
3. **Generate API Key**: Create a new API key
4. **Copy the key**: Save it securely

### 2. Add API Key to Environment

Add your Perplexity API key to your `.env` file in the backend directory:

```bash
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

### 3. Configure Search Engine (Optional)

By default, the system will auto-detect and use Perplexity if the API key is available. You can also explicitly set it:

```bash
WEB_SEARCH_ENGINE=perplexity
```

Or let it auto-detect (recommended):
```bash
WEB_SEARCH_ENGINE=auto
```

## How It Works

The Perplexity integration is part of the `WebResearchService` and follows this priority order:

1. **Perplexity** (if API key is set) - AI-powered real-time search
2. **SerpAPI** (if API key is set) - Traditional search results
3. **Google Custom Search** (if API key and CX are set)
4. **Tavily** (if API key is set) - AI research API
5. **DuckDuckGo** (fallback, no API key required)

## Usage

The Perplexity search is automatically used when:

1. **Company Research**: When researching companies for document analysis
2. **Web Research**: Any web search functionality in the application
3. **Content Generation**: When generating content that requires current information

### Example: Company Research

When you upload a document or research a company, the system will:

1. Use Perplexity to search for company information
2. Get AI-summarized results with citations
3. Extract structured data (competitors, marketing methods, etc.)
4. Use this information to enhance content generation

## API Features

### Real-time Search
Perplexity uses the `llama-3.1-sonar-large-128k-online` model which:
- Searches the web in real-time
- Provides current information
- Includes source citations

### Citation Extraction
The implementation automatically extracts:
- Source URLs
- Source titles
- Relevant snippets
- Content summaries

## Benefits Over Other Search Engines

1. **AI-Powered**: Provides summarized answers, not just links
2. **Real-time**: Always up-to-date information
3. **Citations**: Includes source URLs for verification
4. **Context-Aware**: Understands query intent better
5. **Comprehensive**: Combines multiple sources into coherent answers

## Troubleshooting

### API Key Not Working

1. **Verify the key**: Make sure the API key is correct
2. **Check environment**: Ensure the key is loaded from `.env`
3. **Test manually**: Try a direct API call to verify

### No Results Returned

1. **Check API quota**: Verify you haven't exceeded your API limits
2. **Check query format**: Ensure queries are clear and specific
3. **Review logs**: Check backend console for error messages

### Fallback to Other Engines

If Perplexity fails, the system automatically falls back to:
- SerpAPI (if configured)
- Google Custom Search (if configured)
- Tavily (if configured)
- DuckDuckGo (always available as last resort)

## Cost Considerations

Perplexity API has usage-based pricing. Check [Perplexity pricing](https://www.perplexity.ai/pricing) for current rates.

**Tips to optimize costs:**
- Use Perplexity for important queries
- Let the system auto-fallback to free options when appropriate
- Cache results when possible

## Integration Points

Perplexity is used in:

1. **Document Analysis** (`/api/document/video`)
   - Researching companies mentioned in documents
   - Finding competitor information
   - Discovering marketing strategies

2. **LinkedIn Tools** (`/api/linkedin/chat`)
   - Researching trending topics
   - Finding industry insights
   - Getting current information

3. **Marketing Post Generation** (`/api/marketing-post`)
   - Researching topics for posts
   - Finding relevant information
   - Getting current trends

## Testing

Test the Perplexity integration:

```python
# In Python shell or test script
from services.web_research_service import WebResearchService

service = WebResearchService()
results = await service.search_web("latest AI video generation trends", num_results=5)
print(results)
```

## API Documentation

For more details on Perplexity API:
- [Perplexity API Docs](https://docs.perplexity.ai/)
- [Perplexity Models](https://docs.perplexity.ai/docs/models)

## Example Response Format

Perplexity search returns results in this format:

```python
[
    {
        "title": "Source Title",
        "snippet": "Relevant content snippet...",
        "url": "https://source-url.com"
    },
    ...
]
```

These results are then used by the AI analysis layer to extract structured insights about companies, competitors, and marketing strategies.











