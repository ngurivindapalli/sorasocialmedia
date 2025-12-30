# Web Research Implementation Guide

## Overview

The web research service automatically extracts company names from documents and researches them online to gather:
- Company information (description, industry, founding details)
- Competitor analysis
- Advertising and marketing methods
- Brand positioning insights

This context is then integrated into document analysis to enhance script and video generation.

## Features

### 1. **Automatic Company Extraction**
- Extracts company names from documents using pattern matching
- Identifies companies mentioned in text (e.g., "Nike Inc", "Apple Corporation")
- Handles various company name formats

### 2. **Web Research**
- Searches web for company information
- Finds competitors
- Discovers advertising and marketing methods
- Extracts brand positioning insights

### 3. **Search Engine Support**
- **DuckDuckGo** (default, free, no API key required)
- **SerpAPI** (requires API key, set `SERPAPI_KEY` env var)
- **Google Custom Search** (requires API key and CX, set `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX`)

### 4. **Context Integration**
- Web research is automatically added to document context
- Stored in user context for future reference
- Used by AI to generate more informed scripts

## How It Works

### Example Flow:

1. **User uploads document** mentioning "Nike"
2. **System extracts company name**: "Nike"
3. **Web research triggered**:
   - Searches: "Nike company information"
   - Searches: "Nike competitors"
   - Searches: "Nike advertising methods marketing strategy"
4. **Data extracted**:
   - Company info: Industry, description, founding year
   - Competitors: Adidas, Puma, Under Armour
   - Advertising methods: Social media marketing, influencer partnerships, TV commercials
5. **Context enhanced**: Document context now includes web research
6. **AI generates script** with knowledge of:
   - Nike's competitors
   - Industry-standard advertising methods
   - Competitive positioning

## Configuration

### Environment Variables

```bash
# Optional: Choose search engine (default: duckduckgo)
WEB_SEARCH_ENGINE=duckduckgo  # or 'serpapi' or 'google'

# For SerpAPI (optional)
SERPAPI_KEY=your_serpapi_key_here

# For Google Custom Search (optional)
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_SEARCH_CX=your_search_engine_id
```

### Using DuckDuckGo (Default)

No configuration needed! Works out of the box.

### Using SerpAPI

1. Sign up at https://serpapi.com/
2. Get your API key
3. Set `SERPAPI_KEY` environment variable
4. Set `WEB_SEARCH_ENGINE=serpapi`

### Using Google Custom Search

1. Create a Custom Search Engine at https://programmablesearchengine.google.com/
2. Get your API key from Google Cloud Console
3. Set `GOOGLE_SEARCH_API_KEY` and `GOOGLE_SEARCH_CX`
4. Set `WEB_SEARCH_ENGINE=google`

## API Usage

### Automatic Integration

Web research is automatically triggered when:
- Documents are uploaded and analyzed
- Video scripts are generated from documents

### Manual Research

You can also manually research companies:

```python
from services.web_research_service import WebResearchService

web_research = WebResearchService()

# Research a specific company
research = await web_research.research_company("Nike")
print(research["competitors"])  # ['Adidas', 'Puma', ...]
print(research["advertising_methods"])  # ['Social media marketing', ...]

# Extract companies from text
companies = await web_research.extract_companies_from_text(document_text)

# Research all companies in a document
research_data = await web_research.research_companies_from_document(document_text)
```

## Data Structure

### Research Result Format

```python
{
    "company_name": "Nike",
    "company_info": {
        "description": "...",
        "industry": "Sportswear",
        "founded": "1964",
        "headquarters": "...",
        "key_facts": []
    },
    "competitors": ["Adidas", "Puma", "Under Armour"],
    "advertising_methods": [
        "Social media marketing",
        "Influencer partnerships",
        "TV commercials",
        "Sponsorships"
    ],
    "search_results": {
        "company_info": [...],
        "competitors": [...],
        "advertising": [...]
    }
}
```

## Integration Points

### 1. Document Processing

When documents are processed for video generation:
- Companies are automatically extracted
- Web research is performed
- Context is enhanced with research data

### 2. User Context Storage

Web research data is stored in user context:
- Companies researched
- Competitor information
- Advertising methods discovered
- Available for future generations

### 3. AI Prompt Enhancement

Web research is formatted and added to AI prompts:
```
WEB RESEARCH - COMPANY & COMPETITOR ANALYSIS:

COMPANY: Nike
  Description: ...
  Industry: Sportswear
  Competitors: Adidas, Puma, Under Armour
  Advertising Methods: Social media marketing, influencer partnerships, TV commercials
```

## Benefits

1. **Competitive Intelligence**: Understand competitors and market positioning
2. **Industry Insights**: Learn advertising methods used in the industry
3. **Better Scripts**: AI generates scripts with competitive context
4. **Automatic**: No manual research needed
5. **Contextual**: Research is specific to companies in user's documents

## Limitations & Considerations

1. **Rate Limiting**: Web searches may be rate-limited by search engines
2. **Accuracy**: Company extraction uses heuristics (may have false positives)
3. **API Costs**: SerpAPI and Google Custom Search have usage limits/costs
4. **Privacy**: Only searches for publicly available information
5. **Legal**: Respects robots.txt and terms of service

## Future Enhancements

1. **Better NLP**: Use AI to extract company names more accurately
2. **Caching**: Cache research results to avoid duplicate searches
3. **More Data Points**: Extract more information (revenue, market share, etc.)
4. **Competitor Deep Dive**: Research competitors' advertising in detail
5. **Trend Analysis**: Track advertising trends over time
6. **Social Media Analysis**: Scrape social media for advertising examples

## Troubleshooting

### No Companies Found

- Check if document contains company names
- Company names should be capitalized (e.g., "Nike", not "nike")
- Try mentioning company with legal suffix (e.g., "Nike Inc")

### Search Errors

- Check internet connection
- Verify API keys if using SerpAPI/Google
- Check rate limits
- System will continue without web research if errors occur

### Slow Performance

- Web research adds ~2-5 seconds per company
- Limited to 5 companies per document
- Consider using faster search APIs (SerpAPI/Google)

## Example Output

When a document mentions "Nike", the system will:

1. Extract: "Nike"
2. Research and find:
   - Competitors: Adidas, Puma, Under Armour, New Balance
   - Advertising: Social media, influencer marketing, TV ads, sponsorships
   - Industry: Sportswear and athletic apparel
3. Enhance document context with this information
4. AI generates script with competitive context:
   - "Like Nike's competitors Adidas and Puma, we can leverage..."
   - "Following industry-standard methods like social media marketing..."
   - "Positioning against competitors in the sportswear industry..."

This makes scripts more informed and competitive!



















