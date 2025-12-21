"""
Web Research Service - Scrapes web for company information, competitors, and advertising methods
Enhances document context with real-time web data
"""

import os
import httpx
from typing import Dict, List, Optional
import re
from urllib.parse import quote_plus, urlparse, parse_qs
import asyncio

# BeautifulSoup for better HTML parsing
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("[WebResearch] WARNING BeautifulSoup4 not installed. Using basic regex parsing.")

class WebResearchService:
    """Service for web scraping and research to enhance user context"""
    
    def __init__(self, openai_service=None):
        # Priority order: Perplexity > SerpAPI > Google Custom Search > Tavily > DuckDuckGo
        # Perplexity is AI-powered and provides excellent real-time results
        self.search_engine = os.getenv('WEB_SEARCH_ENGINE', 'auto')  # 'auto', 'perplexity', 'serpapi', 'google', 'tavily', 'duckduckgo'
        self.perplexity_api_key = os.getenv('PERPLEXITY_API_KEY', '')
        self.serpapi_key = os.getenv('SERPAPI_KEY', '')
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY', '')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX', '')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY', '')
        
        # Auto-detect best available search engine
        if self.search_engine == 'auto':
            if self.perplexity_api_key:
                self.search_engine = 'perplexity'
            elif self.serpapi_key:
                self.search_engine = 'serpapi'
            elif self.google_api_key and self.google_cx:
                self.search_engine = 'google'
            elif self.tavily_api_key:
                self.search_engine = 'tavily'
            else:
                self.search_engine = 'duckduckgo'
        
        self.openai_service = openai_service  # For AI-powered analysis of search results
        
        print(f"[WebResearch] OK Web research service initialized")
        print(f"[WebResearch]   Search engine: {self.search_engine}")
        if self.search_engine == 'duckduckgo':
            print(f"[WebResearch]   WARNING Using DuckDuckGo (free but limited). For better results, set PERPLEXITY_API_KEY, SERPAPI_KEY, or GOOGLE_SEARCH_API_KEY")
    
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict]:
        """
        Search the web for information with automatic fallback
        
        Returns list of search results with title, snippet, and URL
        """
        # Try primary search engine first
        try:
            if self.search_engine == 'perplexity' and self.perplexity_api_key:
                results = await self._search_perplexity(query, num_results)
                if results:
                    return results
            elif self.search_engine == 'serpapi' and self.serpapi_key:
                results = await self._search_serpapi(query, num_results)
                if results:
                    return results
            elif self.search_engine == 'google' and self.google_api_key and self.google_cx:
                results = await self._search_google(query, num_results)
                if results:
                    return results
            elif self.search_engine == 'tavily' and self.tavily_api_key:
                results = await self._search_tavily(query, num_results)
                if results:
                    return results
        except Exception as e:
            print(f"[WebResearch] Primary search engine failed: {e}")
        
        # Fallback chain: Try other available engines
        fallback_engines = []
        if self.perplexity_api_key and self.search_engine != 'perplexity':
            fallback_engines.append(('perplexity', self._search_perplexity))
        if self.serpapi_key and self.search_engine != 'serpapi':
            fallback_engines.append(('serpapi', self._search_serpapi))
        if self.google_api_key and self.google_cx and self.search_engine != 'google':
            fallback_engines.append(('google', self._search_google))
        if self.tavily_api_key and self.search_engine != 'tavily':
            fallback_engines.append(('tavily', self._search_tavily))
        
        for engine_name, search_func in fallback_engines:
            try:
                results = await search_func(query, num_results)
                if results:
                    print(f"[WebResearch] Using fallback: {engine_name}")
                    return results
            except Exception as e:
                print(f"[WebResearch] Fallback {engine_name} failed: {e}")
                continue
        
        # Last resort: DuckDuckGo
        try:
            return await self._search_duckduckgo(query, num_results)
        except Exception as e:
            print(f"[WebResearch] All search engines failed: {e}")
            return []
    
    async def _search_perplexity(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using Perplexity API (AI-powered real-time search)"""
        try:
            url = "https://api.perplexity.ai/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.perplexity_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "llama-3.1-sonar-large-128k-online",  # Online model for real-time web search
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides accurate, real-time information from web search results. Always cite your sources with URLs."
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.2,
                "return_citations": True,
                "return_related_queries": False
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                results = []
                
                # Extract citations from Perplexity response
                # Citations are typically in the response metadata or in the content
                citations = []
                
                # Try to get citations from response
                if "citations" in data:
                    citations = data["citations"]
                elif "choices" in data and len(data["choices"]) > 0:
                    choice = data["choices"][0]
                    # Citations might be in the message or in metadata
                    if "citations" in choice:
                        citations = choice["citations"]
                    elif "message" in choice and "citations" in choice["message"]:
                        citations = choice["message"]["citations"]
                    elif "metadata" in choice and "citations" in choice["metadata"]:
                        citations = choice["metadata"]["citations"]
                
                # Parse citations into search results
                if citations:
                    for i, citation in enumerate(citations[:num_results]):
                        if isinstance(citation, dict):
                            results.append({
                                "title": citation.get("title", citation.get("text", f"Source {i+1}")),
                                "snippet": citation.get("snippet", citation.get("text", ""))[:300],
                                "url": citation.get("url", citation.get("link", ""))
                            })
                        elif isinstance(citation, str):
                            # If citation is just a URL string
                            results.append({
                                "title": f"Source {i+1}",
                                "snippet": "",
                                "url": citation
                            })
                
                # Extract content from the response
                content = ""
                if "choices" in data and len(data["choices"]) > 0:
                    message = data["choices"][0].get("message", {})
                    content = message.get("content", "")
                
                # If we have content but no citations, try to extract URLs from content
                if content and not results:
                    # Look for URLs in the content
                    import re
                    url_pattern = r'https?://[^\s\)]+'
                    urls = re.findall(url_pattern, content)
                    for i, url in enumerate(urls[:num_results]):
                        results.append({
                            "title": f"Source {i+1}",
                            "snippet": content[:300] if i == 0 else "",
                            "url": url
                        })
                
                # If still no results but we have content, create a result from the answer
                if not results and content:
                    results.append({
                        "title": query,
                        "snippet": content[:500],
                        "url": ""
                    })
                
                print(f"[WebResearch] Perplexity search: Found {len(results)} results for '{query}'")
                return results[:num_results]
                
        except Exception as e:
            print(f"[WebResearch] Perplexity search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using DuckDuckGo (free, no API key required)"""
        try:
            # Use DuckDuckGo instant answer API (more reliable than HTML scraping)
            # Fallback to HTML if API doesn't work
            api_url = f"https://api.duckduckgo.com/?q={quote_plus(query)}&format=json&no_html=1&skip_disambig=1"
            
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                }
                
                # Try API first
                try:
                    response = await client.get(api_url, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        results = []
                        
                        # Extract abstract if available
                        if data.get("AbstractText"):
                            results.append({
                                "title": data.get("Heading", query),
                                "snippet": data.get("AbstractText", "")[:300],
                                "url": data.get("AbstractURL", "")
                            })
                        
                        # Extract related topics
                        for topic in data.get("RelatedTopics", [])[:num_results-1]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append({
                                    "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", "")[:50],
                                    "snippet": topic.get("Text", "")[:300],
                                    "url": topic.get("FirstURL", "")
                                })
                        
                        if results:
                            print(f"[WebResearch] DuckDuckGo API: Found {len(results)} results for '{query}'")
                            return results[:num_results]
                except Exception as api_error:
                    print(f"[WebResearch] DuckDuckGo API failed, trying HTML: {api_error}")
                
                # Fallback to HTML search
                search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
                response = await client.get(search_url, headers=headers)
                response.raise_for_status()
                
                html = response.text
                results = []
                
                if BS4_AVAILABLE:
                    # Use BeautifulSoup for better parsing
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Try multiple selectors for DuckDuckGo results
                    result_divs = soup.find_all('div', class_='result') or soup.find_all('div', class_='web-result') or soup.find_all('div', {'class': re.compile(r'result')})
                    
                    for result_div in result_divs[:num_results]:
                        # Try multiple ways to find title and URL
                        title_link = (result_div.find('a', class_='result__a') or 
                                     result_div.find('a', class_='result-link') or
                                     result_div.find('a', href=re.compile(r'^http')))
                        
                        if not title_link:
                            continue
                        
                        title = title_link.get_text(strip=True)
                        url = title_link.get('href', '')
                        
                        # Clean up URL (DuckDuckGo sometimes uses redirect URLs)
                        if url.startswith('/l/?kh='):
                            # Extract actual URL from DuckDuckGo redirect
                            parsed = urlparse(url)
                            params = parse_qs(parsed.query)
                            if 'uddg' in params:
                                url = params['uddg'][0]
                        
                        # Extract snippet
                        snippet_elem = (result_div.find('a', class_='result__snippet') or
                                      result_div.find('div', class_='result__snippet') or
                                      result_div.find('span', class_='result__snippet'))
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        if title and url:
                            results.append({
                                "title": title,
                                "snippet": snippet[:300],
                                "url": url
                            })
                else:
                    # Fallback to regex parsing
                    pattern = r'<a[^>]*class="[^"]*result[^"]*"[^>]*href="([^"]*)"[^>]*>([^<]+)</a>'
                    matches = re.findall(pattern, html, re.IGNORECASE)
                    
                    for url, title in matches[:num_results]:
                        results.append({
                            "title": title.strip(),
                            "snippet": "",
                            "url": url
                        })
                
                print(f"[WebResearch] DuckDuckGo HTML: Found {len(results)} results for '{query}'")
                return results[:num_results]
                
        except Exception as e:
            print(f"[WebResearch] DuckDuckGo search error: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _search_serpapi(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using SerpAPI (requires API key)"""
        try:
            url = "https://serpapi.com/search"
            params = {
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for result in data.get("organic_results", [])[:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("snippet", ""),
                        "url": result.get("link", "")
                    })
                
                print(f"[WebResearch] SerpAPI search: Found {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            print(f"[WebResearch] SerpAPI search error: {e}")
            return []
    
    async def _search_google(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using Google Custom Search API"""
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": self.google_cx,
                "q": query,
                "num": min(num_results, 10)  # Google API max is 10
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", [])[:num_results]:
                    results.append({
                        "title": item.get("title", ""),
                        "snippet": item.get("snippet", ""),
                        "url": item.get("link", "")
                    })
                
                print(f"[WebResearch] Google search: Found {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            print(f"[WebResearch] Google search error: {e}")
            return []
    
    async def _search_tavily(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search using Tavily API (AI-powered research API)"""
        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": self.tavily_api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": num_results
            }
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for result in data.get("results", [])[:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "snippet": result.get("content", "")[:300],
                        "url": result.get("url", "")
                    })
                
                print(f"[WebResearch] Tavily search: Found {len(results)} results for '{query}'")
                return results
                
        except Exception as e:
            print(f"[WebResearch] Tavily search error: {e}")
            return []
    
    async def _search_wikipedia(self, query: str) -> Optional[Dict]:
        """Search Wikipedia for company information (fallback)"""
        try:
            # Wikipedia API search
            search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + quote_plus(query.replace(" ", "_"))
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(search_url, headers={'User-Agent': 'VideoHook/1.0'})
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "title": data.get("title", ""),
                        "snippet": data.get("extract", "")[:500],
                        "url": data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    }
        except Exception:
            pass
        return None
    
    async def research_company(self, company_name: str) -> Dict:
        """
        Research a company using AI-powered analysis of comprehensive search results.
        Does 1-2 broad searches and lets AI extract competitors, advertising methods, etc.
        
        Returns:
        {
            "company_info": {...},
            "competitors": [...],
            "advertising_methods": [...],
            "marketing_strategies": [...],
            "brand_positioning": "..."
        }
        """
        print(f"[WebResearch] 🔍 Researching company: {company_name}")
        
        # Do comprehensive searches for richer context
        print(f"[WebResearch] 📊 Performing comprehensive search for {company_name}...")
        
        # Search 1: General company information and overview
        search_query_1 = f"{company_name} company business overview industry"
        comprehensive_results = await self.search_web(search_query_1, num_results=5)
        
        # Search 2: Marketing, competitors, and advertising (always do this for richer context)
        search_query_2 = f"{company_name} marketing strategy competitors advertising campaigns"
        additional_results = await self.search_web(search_query_2, num_results=5)
        comprehensive_results.extend(additional_results)
        
        # Search 3: Recent news, trends, and industry insights
        search_query_3 = f"{company_name} recent news 2024 industry trends"
        recent_results = await self.search_web(search_query_3, num_results=3)
        comprehensive_results.extend(recent_results)
        
        # Search 4: Social media presence and brand voice
        search_query_4 = f"{company_name} LinkedIn social media brand voice content style"
        social_results = await self.search_web(search_query_4, num_results=3)
        comprehensive_results.extend(social_results)
        
        # Try Wikipedia as additional source
        wiki_result = await self._search_wikipedia(company_name)
        if wiki_result:
            comprehensive_results.append(wiki_result)
        
        print(f"[WebResearch] OK Collected {len(comprehensive_results)} comprehensive search results (enriched context)")
        
        # If we have OpenAI service, use AI to analyze and extract insights
        if self.openai_service and comprehensive_results:
            print(f"[WebResearch] 🤖 Using AI to analyze search results and extract insights...")
            return await self._analyze_with_ai(company_name, comprehensive_results)
        else:
            # Fallback to pattern-based extraction if no AI service
            print(f"[WebResearch] WARNING No AI service available, using pattern-based extraction")
            company_info = self._extract_company_info(comprehensive_results)
            competitors = self._extract_competitors(comprehensive_results)
            advertising_methods = self._extract_advertising_methods(comprehensive_results)
            
            return {
                "company_name": company_name,
                "company_info": company_info,
                "competitors": competitors,
                "advertising_methods": advertising_methods,
                "search_results": {
                    "comprehensive": comprehensive_results
                }
            }
    
    async def _analyze_with_ai(self, company_name: str, search_results: List[Dict]) -> Dict:
        """
        Use AI to analyze comprehensive search results and extract structured insights
        """
        try:
            # Combine all search results into a comprehensive text
            combined_context = f"COMPANY: {company_name}\n\n"
            combined_context += "SEARCH RESULTS:\n"
            for i, result in enumerate(search_results[:10], 1):  # Limit to top 10 results
                combined_context += f"\n--- Result {i} ---\n"
                combined_context += f"Title: {result.get('title', 'N/A')}\n"
                combined_context += f"Content: {result.get('snippet', 'N/A')}\n"
                combined_context += f"URL: {result.get('url', 'N/A')}\n"
            
            # Use OpenAI to analyze and extract structured information
            analysis_prompt = f"""Analyze the following web search results about the company "{company_name}" and extract comprehensive insights.

{combined_context}

Based on the search results above, provide a comprehensive, detailed analysis with:

1. COMPANY INFORMATION:
   - Description: Detailed overview of what the company does, their mission, and core business
   - Industry: What industry/sector they operate in, market position
   - Founded: Year founded (if mentioned)
   - Headquarters: Location (if mentioned)
   - Key facts: 3-5 important facts about the company (revenue, size, notable achievements, recent milestones)
   - Recent news/trends: Any recent developments, news, or industry trends affecting the company

2. COMPETITORS & MARKET POSITION:
   - List 5-7 main competitors or companies in the same space
   - Include brief context about why they're competitors and how they differ
   - Market positioning: How this company differentiates from competitors
   - Competitive advantages: What makes this company unique

3. ADVERTISING & MARKETING METHODS (DETAILED):
   - List 5-10 advertising and marketing methods/strategies used by this company
   - Include specific examples if mentioned (e.g., "social media marketing on Instagram and TikTok")
   - Recent campaigns: Any notable recent marketing campaigns or initiatives
   - Content style: How they communicate, tone, messaging approach
   - Platform presence: Where they're most active (LinkedIn, Instagram, etc.)

4. BRAND POSITIONING & VOICE:
   - How the company positions itself in the market
   - Key messaging themes and brand values
   - Target audience: Detailed description of primary and secondary audiences
   - Brand personality: Professional, friendly, innovative, authoritative, etc.
   - Content themes: What topics they typically cover in their content

5. CONTENT INSIGHTS:
   - What types of content perform well for this company
   - Common content themes and topics
   - Engagement strategies they use
   - Visual style preferences (if mentioned)

Format your response as structured text that can be easily parsed. Be specific and cite information from the search results when possible."""

            # Call OpenAI API
            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a business research analyst. Analyze web search results and extract structured insights about companies, their competitors, and marketing strategies. Be accurate and cite information from the provided search results."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more factual extraction
                max_tokens=2000  # Increased for richer, more detailed analysis
            )
            
            ai_analysis = response.choices[0].message.content
            print(f"[WebResearch] OK AI analysis completed ({len(ai_analysis)} characters)")
            
            # Parse AI response into structured format
            parsed_data = self._parse_ai_analysis(ai_analysis, company_name)
            
            return {
                "company_name": company_name,
                "company_info": parsed_data.get("company_info", {}),
                "competitors": parsed_data.get("competitors", []),
                "advertising_methods": parsed_data.get("advertising_methods", []),
                "brand_positioning": parsed_data.get("brand_positioning", ""),
                "content_insights": parsed_data.get("content_insights", {}),
                "market_position": parsed_data.get("market_position", ""),
                "recent_campaigns": parsed_data.get("recent_campaigns", []),
                "ai_analysis": ai_analysis,  # Include raw analysis for reference
                "search_results": {
                    "comprehensive": search_results
                }
            }
            
        except Exception as e:
            print(f"[WebResearch] WARNING AI analysis failed: {e}, falling back to pattern extraction")
            import traceback
            traceback.print_exc()
            # Fallback to pattern-based extraction
            company_info = self._extract_company_info(search_results)
            competitors = self._extract_competitors(search_results)
            advertising_methods = self._extract_advertising_methods(search_results)
            
            return {
                "company_name": company_name,
                "company_info": company_info,
                "competitors": competitors,
                "advertising_methods": advertising_methods,
                "search_results": {
                    "comprehensive": search_results
                }
            }
    
    def _parse_ai_analysis(self, ai_text: str, company_name: str) -> Dict:
        """
        Parse AI analysis text into structured data
        """
        import re
        
        result = {
            "company_info": {
                "description": "",
                "industry": "",
                "founded": "",
                "headquarters": "",
                "key_facts": [],
                "recent_news": ""
            },
            "competitors": [],
            "advertising_methods": [],
            "brand_positioning": "",
            "content_insights": {
                "content_themes": [],
                "engagement_strategies": [],
                "visual_style": ""
            },
            "market_position": "",
            "recent_campaigns": []
        }
        
        # Extract company info
        desc_match = re.search(r'Description[:\-]?\s*(.+?)(?:\n|Industry|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            result["company_info"]["description"] = desc_match.group(1).strip()[:300]
        
        industry_match = re.search(r'Industry[:\-]?\s*(.+?)(?:\n|Founded|$)', ai_text, re.IGNORECASE)
        if industry_match:
            result["company_info"]["industry"] = industry_match.group(1).strip()
        
        founded_match = re.search(r'Founded[:\-]?\s*(\d{4})', ai_text, re.IGNORECASE)
        if founded_match:
            result["company_info"]["founded"] = founded_match.group(1)
        
        # Extract competitors (look for numbered list or bullet points)
        competitors_section = re.search(r'COMPETITORS[:\-]?\s*(.+?)(?:\n\n|ADVERTISING|MARKETING|BRAND|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if competitors_section:
            comp_text = competitors_section.group(1)
            # Extract competitor names (lines starting with - or numbers)
            comp_matches = re.findall(r'(?:^|\n)[\-\d\.]+\s*([A-Z][^:\n]+)', comp_text, re.MULTILINE)
            result["competitors"] = [c.strip() for c in comp_matches[:5]]
        
        # Extract advertising methods
        advertising_section = re.search(r'ADVERTISING[:\-]?\s*(.+?)(?:\n\n|BRAND|MARKETING|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if advertising_section:
            adv_text = advertising_section.group(1)
            # Extract methods (lines starting with - or numbers)
            adv_matches = re.findall(r'(?:^|\n)[\-\d\.]+\s*([^:\n]+)', adv_text, re.MULTILINE)
            result["advertising_methods"] = [a.strip() for a in adv_matches[:7]]
        
        # Extract brand positioning
        positioning_match = re.search(r'BRAND POSITIONING[:\-]?\s*(.+?)(?:\n\n|CONTENT|MARKET|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if positioning_match:
            result["brand_positioning"] = positioning_match.group(1).strip()[:300]
        
        # Extract content insights
        content_section = re.search(r'CONTENT INSIGHTS[:\-]?\s*(.+?)(?:\n\n|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if content_section:
            content_text = content_section.group(1)
            # Extract content themes
            themes_matches = re.findall(r'(?:themes|topics)[:\-]?\s*([^\.]+)', content_text, re.IGNORECASE)
            if themes_matches:
                result["content_insights"]["content_themes"] = [t.strip() for t in themes_matches[0].split(',')[:5]]
            # Extract engagement strategies
            engagement_matches = re.findall(r'(?:engagement|strategies)[:\-]?\s*([^\.]+)', content_text, re.IGNORECASE)
            if engagement_matches:
                result["content_insights"]["engagement_strategies"] = [e.strip() for e in engagement_matches[0].split(',')[:5]]
        
        # Extract market position
        market_match = re.search(r'MARKET POSITION[:\-]?\s*(.+?)(?:\n\n|COMPETITIVE|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if market_match:
            result["market_position"] = market_match.group(1).strip()[:200]
        
        # Extract recent campaigns
        campaigns_section = re.search(r'RECENT CAMPAIGNS[:\-]?\s*(.+?)(?:\n\n|$)', ai_text, re.IGNORECASE | re.DOTALL)
        if campaigns_section:
            campaigns_text = campaigns_section.group(1)
            campaign_matches = re.findall(r'(?:^|\n)[\-\d\.]+\s*([^:\n]+)', campaigns_text, re.MULTILINE)
            result["recent_campaigns"] = [c.strip() for c in campaign_matches[:5]]
        
        return result
    
    def _extract_company_info(self, search_results: List[Dict]) -> Dict:
        """Extract company information from search results"""
        info = {
            "description": "",
            "industry": "",
            "founded": "",
            "headquarters": "",
            "key_facts": []
        }
        
        # Combine all snippets
        combined_text = " ".join([r.get("snippet", "") for r in search_results])
        
        # Extract key information using patterns
        # Industry
        industry_patterns = [
            r'industry[:\s]+([^\.]+)',
            r'in the ([^\.]+) industry',
            r'([^\.]+) company'
        ]
        for pattern in industry_patterns:
            match = re.search(pattern, combined_text, re.IGNORECASE)
            if match:
                info["industry"] = match.group(1).strip()
                break
        
        # Founded year
        founded_match = re.search(r'founded[:\s]+(\d{4})', combined_text, re.IGNORECASE)
        if founded_match:
            info["founded"] = founded_match.group(1)
        
        # Description (first snippet)
        if search_results:
            info["description"] = search_results[0].get("snippet", "")[:300]
        
        return info
    
    def _extract_competitors(self, search_results: List[Dict]) -> List[str]:
        """Extract competitor names from search results"""
        competitors = []
        
        # Combine all text
        combined_text = " ".join([r.get("title", "") + " " + r.get("snippet", "") for r in search_results])
        
        # Look for competitor mentions
        # Common patterns: "competitors include", "competes with", "rivals"
        competitor_patterns = [
            r'competitors? (?:include|are|:)\s*([^\.]+)',
            r'competes? with ([^\.]+)',
            r'rivals? (?:include|are|:)\s*([^\.]+)',
            r'(?:main|major|top) competitors? (?:include|are|:)\s*([^\.]+)'
        ]
        
        for pattern in competitor_patterns:
            matches = re.finditer(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                competitors_text = match.group(1)
                # Split by common separators
                competitor_list = re.split(r'[,;]|\sand\s', competitors_text)
                for comp in competitor_list:
                    comp_clean = comp.strip()
                    if comp_clean and len(comp_clean) > 2:
                        competitors.append(comp_clean)
        
        # Remove duplicates and limit
        competitors = list(dict.fromkeys(competitors))[:10]
        
        return competitors
    
    def _extract_advertising_methods(self, search_results: List[Dict]) -> List[str]:
        """Extract advertising and marketing methods from search results"""
        methods = []
        
        # Combine all text
        combined_text = " ".join([r.get("title", "") + " " + r.get("snippet", "") for r in search_results])
        
        # Common advertising methods/keywords
        advertising_keywords = [
            "social media marketing", "digital advertising", "TV commercials",
            "influencer partnerships", "content marketing", "email marketing",
            "search engine marketing", "display advertising", "video advertising",
            "podcast advertising", "sponsorships", "event marketing",
            "guerrilla marketing", "viral marketing", "native advertising"
        ]
        
        # Check which methods are mentioned
        for keyword in advertising_keywords:
            if keyword.lower() in combined_text.lower():
                methods.append(keyword)
        
        # Also extract any specific mentions
        method_patterns = [
            r'uses? ([^\.]+) (?:advertising|marketing)',
            r'advertising (?:methods?|strategies?|approaches?) (?:include|are|:)\s*([^\.]+)',
            r'marketing (?:methods?|strategies?|approaches?) (?:include|are|:)\s*([^\.]+)'
        ]
        
        for pattern in method_patterns:
            matches = re.finditer(pattern, combined_text, re.IGNORECASE)
            for match in matches:
                methods_text = match.group(1)
                method_list = re.split(r'[,;]|\sand\s', methods_text)
                for method in method_list:
                    method_clean = method.strip()
                    if method_clean and len(method_clean) > 3:
                        methods.append(method_clean)
        
        # Remove duplicates and limit
        methods = list(dict.fromkeys(methods))[:15]
        
        return methods
    
    async def extract_companies_from_text(self, text: str) -> List[str]:
        """
        Extract company names from text using pattern matching and NLP heuristics
        
        Returns list of potential company names (filtered to avoid false positives)
        """
        companies = []
        
        # Pattern 1: "Company X", "X Inc", "X Corp", "X LLC"
        pattern1 = r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co\.)'
        matches = re.finditer(pattern1, text)
        for match in matches:
            company = match.group(1).strip()
            if len(company) > 2 and company not in ['The', 'A', 'An']:
                companies.append(company)
        
        # Pattern 2: Capitalized phrases (common for company names)
        # Look for sequences of capitalized words (2-4 words)
        pattern2 = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
        matches = re.finditer(pattern2, text)
        for match in matches:
            potential_company = match.group(1).strip()
            # Filter out common words and phrases
            common_words = ['The', 'This', 'That', 'These', 'Those', 'Our', 'Your', 'Their',
                          'Company', 'Business', 'Organization', 'Corporation', 'Inc', 'Ltd']
            words = potential_company.split()
            if not any(word in common_words for word in words) and len(potential_company) > 3:
                companies.append(potential_company)
        
        # Pattern 3: Quoted company names
        pattern3 = r'"([^"]+)"'
        matches = re.finditer(pattern3, text)
        for match in matches:
            quoted = match.group(1).strip()
            if len(quoted) > 2 and quoted[0].isupper():
                companies.append(quoted)
        
        # Remove duplicates
        companies = list(dict.fromkeys(companies))
        
        # Enhanced false positive filtering
        false_positives = [
            # Locations
            'United States', 'New York', 'Los Angeles', 'San Francisco', 'Silicon Valley',
            'United Kingdom', 'European Union', 'North America', 'South America',
            'New Jersey', 'California', 'Texas', 'Florida', 'Chicago', 'Boston',
            # Common phrases
            'Partial Swipe', 'Swipe File', 'Pearl House', 'Fireflies Zoom',
            # Generic terms
            'Worldwide Alumni', 'Alumni Day', 'Consulting Group', 'Studios',
            # Days/Months
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ]
        
        # Filter out false positives
        filtered_companies = []
        for company in companies:
            # Skip if it's a known false positive
            if any(fp.lower() in company.lower() or company.lower() in fp.lower() for fp in false_positives):
                continue
            # Skip single words that are too generic
            if len(company.split()) == 1 and len(company) < 5:
                continue
            # Skip if it looks like a location (contains "Valley", "City", "Bay", etc.)
            location_words = ['valley', 'city', 'bay', 'beach', 'mountain', 'river', 'lake', 'island']
            if any(loc in company.lower() for loc in location_words):
                continue
            filtered_companies.append(company)
        
        # Limit to top 5 most mentioned (to avoid too many API calls)
        from collections import Counter
        company_counts = Counter(filtered_companies)
        top_companies = [company for company, count in company_counts.most_common(5)]
        
        print(f"[WebResearch] Extracted {len(top_companies)} potential companies: {', '.join(top_companies)}")
        return top_companies
    
    async def research_companies_from_document(self, document_text: str) -> Dict:
        """
        Extract companies from document, identify the MAIN COMPANY (user's company),
        and research them with priority on the main company
        
        Returns comprehensive research data with main company identified
        """
        print(f"[WebResearch] 📄 Analyzing document for companies...")
        
        # Extract company names
        companies = await self.extract_companies_from_text(document_text)
        
        if not companies:
            print(f"[WebResearch] No companies found in document")
            return {
                "companies_found": [],
                "main_company": None,
                "research_data": {}
            }
        
        print(f"[WebResearch] Found {len(companies)} companies: {', '.join(companies)}")
        
        # Identify the MAIN COMPANY (user's company) using AI
        main_company = None
        if self.openai_service and companies:
            print(f"[WebResearch] 🤖 Identifying main company (user's company) from document...")
            main_company = await self._identify_main_company(document_text, companies)
        
        # If AI identification failed, use heuristics (most mentioned, first mentioned, etc.)
        if not main_company and companies:
            # Simple heuristic: most frequently mentioned company
            from collections import Counter
            company_counts = Counter()
            for company in companies:
                count = document_text.lower().count(company.lower())
                company_counts[company] = count
            main_company = company_counts.most_common(1)[0][0] if company_counts else companies[0]
            print(f"[WebResearch] Using heuristic: Main company is '{main_company}' (most frequently mentioned)")
        
        # Research companies with priority on main company
        research_data = {}
        
        # Research main company first (most important)
        if main_company:
            try:
                print(f"[WebResearch] 🎯 Researching MAIN COMPANY: {main_company}")
                company_research = await self.research_company(main_company)
                research_data[main_company] = company_research
                # Mark as main company in research data
                research_data[main_company]["is_main_company"] = True
                await asyncio.sleep(1)
            except Exception as e:
                print(f"[WebResearch] Error researching main company {main_company}: {e}")
        
        # Research other companies (limit to 2 additional to avoid too many API calls)
        other_companies = [c for c in companies if c != main_company][:2]
        for company in other_companies:
            try:
                print(f"[WebResearch] Researching additional company: {company}")
                company_research = await self.research_company(company)
                research_data[company] = company_research
                research_data[company]["is_main_company"] = False
                await asyncio.sleep(1)
            except Exception as e:
                print(f"[WebResearch] Error researching {company}: {e}")
                continue
        
        return {
            "companies_found": companies,
            "main_company": main_company,
            "research_data": research_data
        }
    
    async def _identify_main_company(self, document_text: str, companies: List[str]) -> Optional[str]:
        """
        Use AI to identify which company is the user's main company from the document
        """
        try:
            # Create context for AI
            companies_list = "\n".join([f"- {company}" for company in companies])
            
            prompt = f"""Analyze this document and identify which company is the MAIN COMPANY (the company the author/user works for or represents).

DOCUMENT CONTENT:
{document_text[:3000]}  # Limit to first 3000 chars

COMPANIES MENTIONED:
{companies_list}

Based on the document content, determine which company is the MAIN COMPANY. Look for:
- First-person references ("we", "our company", "my company")
- Company ownership/employment context
- Most detailed descriptions of one company
- Author's affiliation or role at a company
- Company that the content is primarily about

Respond with ONLY the company name (exactly as it appears in the list above), or "UNKNOWN" if you cannot determine.

Company name:"""

            response = await self.openai_service.client.chat.completions.create(
                model=self.openai_service.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a document analyst. Identify the main company that the document author works for or represents based on context clues like first-person references, employment context, and primary focus."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,  # Low temperature for consistent identification
                max_tokens=50
            )
            
            identified_company = response.choices[0].message.content.strip()
            
            # Validate that the identified company is in our list
            if identified_company and identified_company.upper() != "UNKNOWN":
                # Try to match (case-insensitive, partial match)
                for company in companies:
                    if company.lower() in identified_company.lower() or identified_company.lower() in company.lower():
                        print(f"[WebResearch] OK AI identified main company: {company}")
                        return company
            
            print(f"[WebResearch] WARNING AI could not clearly identify main company")
            return None
            
        except Exception as e:
            print(f"[WebResearch] WARNING Error identifying main company with AI: {e}")
            return None
    
    def format_research_for_ai(self, research_data: Dict) -> str:
        """
        Format research data into a context string for AI prompts
        Prioritizes and emphasizes the MAIN COMPANY (user's company)
        """
        if not research_data.get("research_data"):
            return ""
        
        main_company = research_data.get("main_company")
        research_dict = research_data.get("research_data", {})
        
        context_parts = []
        context_parts.append("WEB RESEARCH - COMPANY & COMPETITOR ANALYSIS:")
        context_parts.append("")
        
        # First, format the MAIN COMPANY with emphasis
        if main_company and main_company in research_dict:
            research = research_dict[main_company]
            context_parts.append("=" * 60)
            context_parts.append(f"MAIN COMPANY (USER'S COMPANY): {main_company}")
            context_parts.append("=" * 60)
            
            # Company info
            if research.get("company_info", {}).get("description"):
                context_parts.append(f"  Description: {research['company_info']['description']}")
            if research.get("company_info", {}).get("industry"):
                context_parts.append(f"  Industry: {research['company_info']['industry']}")
            if research.get("company_info", {}).get("founded"):
                context_parts.append(f"  Founded: {research['company_info']['founded']}")
            
            # Competitors (especially relevant for main company)
            if research.get("competitors"):
                context_parts.append(f"  Competitors: {', '.join(research['competitors'][:5])}")
            
            # Advertising methods (key for understanding their marketing)
            if research.get("advertising_methods"):
                context_parts.append(f"  Advertising Methods: {', '.join(research['advertising_methods'][:5])}")
            
            # Brand positioning
            if research.get("brand_positioning"):
                context_parts.append(f"  Brand Positioning: {research['brand_positioning']}")
            
            # AI analysis if available
            if research.get("ai_analysis"):
                context_parts.append(f"  Additional Insights: {research['ai_analysis'][:300]}...")
            
            context_parts.append("")
            context_parts.append("IMPORTANT: This is the user's main company. Focus content generation on this company's brand, style, and marketing approach.")
            context_parts.append("")
        
        # Then, format other companies mentioned (for context)
        other_companies = {name: data for name, data in research_dict.items() if name != main_company}
        if other_companies:
            context_parts.append("OTHER COMPANIES MENTIONED (for context):")
            context_parts.append("")
            
            for company_name, research in other_companies.items():
                context_parts.append(f"COMPANY: {company_name}")
                
                # Brief info only for other companies
                if research.get("company_info", {}).get("description"):
                    context_parts.append(f"  Description: {research['company_info']['description'][:150]}...")
                if research.get("company_info", {}).get("industry"):
                    context_parts.append(f"  Industry: {research['company_info']['industry']}")
                
                context_parts.append("")
        
        return "\n".join(context_parts)

