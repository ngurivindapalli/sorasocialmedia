from openai import AsyncOpenAI
from typing import List, Dict, Optional
import os
import re
import asyncio
from datetime import datetime
from urllib.parse import urlparse
import aiohttp
from bs4 import BeautifulSoup


class SEOAEOService:
    """Service for SEO/AEO (Answer Engine Optimization) analysis"""
    
    def __init__(self, openai_api_key: str):
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-2024-08-06"
    
    async def analyze_website(self, brand_url: str) -> Dict:
        """Analyze website to understand brand positioning"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(brand_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Extract key information
                        title = soup.find('title')
                        title_text = title.get_text() if title else ""
                        
                        meta_desc = soup.find('meta', attrs={'name': 'description'})
                        meta_desc_text = meta_desc.get('content', '') if meta_desc else ""
                        
                        # Extract headings
                        headings = [h.get_text() for h in soup.find_all(['h1', 'h2', 'h3'])[:10]]
                        
                        # Extract main content
                        paragraphs = [p.get_text() for p in soup.find_all('p')[:5]]
                        
                        return {
                            "title": title_text,
                            "meta_description": meta_desc_text,
                            "headings": headings,
                            "content_snippets": paragraphs,
                            "url": brand_url
                        }
        except Exception as e:
            print(f"Error analyzing website: {e}")
            return {"url": brand_url, "error": str(e)}
    
    async def generate_prompts(
        self, 
        brand_name: str, 
        brand_info: Optional[Dict] = None,
        topics: Optional[List[str]] = None,
        num_prompts: int = 100
    ) -> List[str]:
        """Generate diverse prompts that mirror real user queries"""
        
        # Base topics if none provided
        if not topics:
            topics = [
                "product features",
                "pricing",
                "comparison",
                "alternatives",
                "how to use",
                "best practices",
                "troubleshooting",
                "integration",
                "getting started",
                "use cases"
            ]
        
        # Generate prompts using GPT
        system_prompt = f"""You are a prompt generator for SEO/AEO analysis. Generate diverse, natural user queries that people might ask about {brand_name} or related topics.

Brand context: {brand_info.get('title', '') if brand_info else ''}
Topics to cover: {', '.join(topics)}

Generate {num_prompts} diverse prompts that:
1. Sound like real user questions
2. Cover different aspects and use cases
3. Include variations in phrasing
4. Mix beginner and advanced questions
5. Include comparison questions
6. Include problem-solving questions

Return ONLY a JSON array of strings, no other text."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate {num_prompts} diverse prompts about {brand_name} and related topics."}
                ],
                temperature=0.9,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            content = response.choices[0].message.content
            # Try to extract JSON array
            if isinstance(content, str):
                # Look for JSON array in response
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    import json
                    prompts = json.loads(json_match.group())
                    return prompts[:num_prompts]
                else:
                    # Try parsing as JSON object
                    import json
                    data = json.loads(content)
                    # Look for prompts key
                    if 'prompts' in data:
                        return data['prompts'][:num_prompts]
                    elif isinstance(data, list):
                        return data[:num_prompts]
            
            # Fallback: generate simple prompts
            return self._generate_fallback_prompts(brand_name, topics, num_prompts)
            
        except Exception as e:
            print(f"Error generating prompts: {e}")
            return self._generate_fallback_prompts(brand_name, topics, num_prompts)
    
    def _generate_fallback_prompts(self, brand_name: str, topics: List[str], num_prompts: int) -> List[str]:
        """Generate simple fallback prompts"""
        prompts = []
        variations = [
            "What is",
            "How does",
            "How to use",
            "Best",
            "Compare",
            "Alternatives to",
            "Why use",
            "Features of",
            "Pricing for",
            "Getting started with"
        ]
        
        for i in range(num_prompts):
            variation = variations[i % len(variations)]
            topic = topics[i % len(topics)]
            prompts.append(f"{variation} {brand_name} {topic}?")
        
        return prompts
    
    async def test_prompt_with_chatgpt(
        self, 
        prompt: str, 
        brand_name: str,
        competitors: Optional[List[str]] = None
    ) -> Dict:
        """Test a prompt with ChatGPT and analyze the response"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Provide accurate, informative answers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response_text = response.choices[0].message.content
            
            # Check if brand is mentioned
            brand_mentioned = brand_name.lower() in response_text.lower()
            
            # Extract sources/citations (look for URLs)
            sources = self._extract_sources(response_text)
            
            # Check for competitor mentions
            competitors_mentioned = []
            if competitors:
                for competitor in competitors:
                    if competitor.lower() in response_text.lower():
                        competitors_mentioned.append(competitor)
            
            return {
                "prompt": prompt,
                "response": response_text,
                "brand_mentioned": brand_mentioned,
                "sources": sources,
                "competitors_mentioned": competitors_mentioned
            }
            
        except Exception as e:
            print(f"Error testing prompt: {e}")
            return {
                "prompt": prompt,
                "response": "",
                "brand_mentioned": False,
                "sources": [],
                "competitors_mentioned": [],
                "error": str(e)
            }
    
    def _extract_sources(self, text: str) -> List[Dict]:
        """Extract source URLs and domains from text"""
        sources = []
        
        # Find URLs
        url_pattern = r'https?://[^\s\)]+'
        urls = re.findall(url_pattern, text)
        
        seen_domains = set()
        for url in urls:
            try:
                parsed = urlparse(url)
                domain = parsed.netloc
                
                if domain and domain not in seen_domains:
                    seen_domains.add(domain)
                    sources.append({
                        "domain": domain,
                        "url": url,
                        "title": None,
                        "snippet": None
                    })
            except:
                continue
        
        return sources
    
    async def categorize_source(self, domain: str) -> str:
        """Categorize source type based on domain"""
        domain_lower = domain.lower()
        
        if any(x in domain_lower for x in ['github.com', 'gitlab.com', 'bitbucket.org']):
            return "Code Repository"
        elif any(x in domain_lower for x in ['reddit.com', 'stackoverflow.com', 'discourse', 'forum']):
            return "Community"
        elif any(x in domain_lower for x in ['medium.com', 'dev.to', 'hashnode.com', 'substack.com']):
            return "Blog"
        elif any(x in domain_lower for x in ['youtube.com', 'vimeo.com']):
            return "Video"
        elif any(x in domain_lower for x in ['twitter.com', 'x.com', 'linkedin.com']):
            return "Social Media"
        else:
            return "Website"
    
    async def analyze_batch_prompts(
        self,
        prompts: List[str],
        brand_name: str,
        competitors: Optional[List[str]] = None,
        max_concurrent: int = 5
    ) -> List[Dict]:
        """Analyze multiple prompts concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_limit(prompt: str):
            async with semaphore:
                return await self.test_prompt_with_chatgpt(prompt, brand_name, competitors)
        
        tasks = [analyze_with_limit(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Error in batch analysis: {result}")
            else:
                valid_results.append(result)
        
        return valid_results

