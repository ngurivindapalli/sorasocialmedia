"""
LinkedIn Post Scraper with Scoring System
Scrapes LinkedIn posts and scores them based on engagement metrics
"""

import requests
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json


class LinkedInPostScraper:
    """Service for scraping LinkedIn posts with engagement metrics and scoring"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        print("[LinkedInScraper] Service initialized")
    
    def calculate_score(self, likes: int, comments: int, shares: int, views: int = 0) -> float:
        """
        Calculate engagement score for a LinkedIn post
        
        Scoring formula:
        - Likes: 1 point each
        - Comments: 5 points each (more valuable engagement)
        - Shares: 10 points each (highest value engagement)
        - Views: 0.01 points each (low engagement signal)
        - Engagement rate bonus: If engagement rate > 5%, add 50 bonus points
        
        Args:
            likes: Number of likes
            comments: Number of comments
            shares: Number of shares
            views: Number of views (optional)
        
        Returns:
            Engagement score (float)
        """
        # Base scoring
        score = (likes * 1.0) + (comments * 5.0) + (shares * 10.0)
        
        # Add views contribution (very small weight)
        if views > 0:
            score += views * 0.01
        
        # Calculate engagement rate
        if views > 0:
            total_engagement = likes + comments + shares
            engagement_rate = (total_engagement / views) * 100
            
            # Bonus for high engagement rate
            if engagement_rate > 5.0:
                score += 50.0  # High engagement bonus
            elif engagement_rate > 2.0:
                score += 20.0  # Medium engagement bonus
            elif engagement_rate > 1.0:
                score += 10.0  # Low engagement bonus
        
        # Normalize score (scale to 0-100 range for display)
        # Typical high-performing post: 1000+ likes, 100+ comments, 50+ shares
        # Max typical score: 1000 + 500 + 500 = 2000
        # Normalize to 0-100 scale
        normalized_score = min(100.0, (score / 20.0))  # Divide by 20 to get 0-100 scale
        
        return round(normalized_score, 2)
    
    async def scrape_posts_by_keyword(self, keyword: str, limit: int = 20) -> List[Dict]:
        """
        Scrape LinkedIn posts by keyword and score them
        
        Note: This is a simulated scraper. In production, you would:
        1. Use LinkedIn Marketing API
        2. Use authenticated scraping with proper permissions
        3. Respect LinkedIn's rate limits and ToS
        
        Args:
            keyword: Search keyword
            limit: Maximum number of posts to scrape
        
        Returns:
            List of posts with scores
        """
        try:
            print(f"[LinkedInScraper] Scraping posts for keyword: {keyword}")
            
            # Simulated LinkedIn posts with realistic engagement metrics
            # In production, this would be actual scraping
            simulated_posts = [
                {
                    "post_id": f"li_post_{keyword.replace(' ', '_')}_1",
                    "content": f"How {keyword} is transforming business operations in 2024. Here's what industry leaders are saying about the future of this technology.",
                    "author": "Tech Industry Leader",
                    "author_url": "https://linkedin.com/in/example",
                    "post_url": f"https://linkedin.com/posts/example-{keyword.replace(' ', '-')}",
                    "likes": 1250,
                    "comments": 145,
                    "shares": 89,
                    "views": 15000,
                    "hashtags": [keyword, "Business", "Innovation"],
                    "posted_at": "2024-01-15T10:30:00Z",
                    "industry": "Technology"
                },
                {
                    "post_id": f"li_post_{keyword.replace(' ', '_')}_2",
                    "content": f"5 key insights about {keyword} that every professional should know. These trends are reshaping how we work.",
                    "author": "Business Strategist",
                    "author_url": "https://linkedin.com/in/example2",
                    "post_url": f"https://linkedin.com/posts/example2-{keyword.replace(' ', '-')}",
                    "likes": 890,
                    "comments": 67,
                    "shares": 34,
                    "views": 12000,
                    "hashtags": [keyword, "Strategy", "Leadership"],
                    "posted_at": "2024-01-14T14:20:00Z",
                    "industry": "Business"
                },
                {
                    "post_id": f"li_post_{keyword.replace(' ', '_')}_3",
                    "content": f"The future of {keyword}: What you need to know. Industry experts weigh in on the latest developments.",
                    "author": "Industry Expert",
                    "author_url": "https://linkedin.com/in/example3",
                    "post_url": f"https://linkedin.com/posts/example3-{keyword.replace(' ', '-')}",
                    "likes": 2100,
                    "comments": 234,
                    "shares": 156,
                    "views": 25000,
                    "hashtags": [keyword, "Future", "Innovation"],
                    "posted_at": "2024-01-13T09:15:00Z",
                    "industry": "Technology"
                },
                {
                    "post_id": f"li_post_{keyword.replace(' ', '_')}_4",
                    "content": f"Breaking down {keyword} for beginners. A comprehensive guide to understanding this important topic.",
                    "author": "Educational Content Creator",
                    "author_url": "https://linkedin.com/in/example4",
                    "post_url": f"https://linkedin.com/posts/example4-{keyword.replace(' ', '-')}",
                    "likes": 567,
                    "comments": 45,
                    "shares": 23,
                    "views": 8000,
                    "hashtags": [keyword, "Education", "Learning"],
                    "posted_at": "2024-01-12T16:45:00Z",
                    "industry": "Education"
                },
                {
                    "post_id": f"li_post_{keyword.replace(' ', '_')}_5",
                    "content": f"{keyword} case study: How one company achieved 300% growth using these strategies.",
                    "author": "Business Case Study",
                    "author_url": "https://linkedin.com/in/example5",
                    "post_url": f"https://linkedin.com/posts/example5-{keyword.replace(' ', '-')}",
                    "likes": 1780,
                    "comments": 198,
                    "shares": 112,
                    "views": 18000,
                    "hashtags": [keyword, "CaseStudy", "Growth"],
                    "posted_at": "2024-01-11T11:30:00Z",
                    "industry": "Business"
                }
            ]
            
            # Calculate scores for each post
            scored_posts = []
            for post in simulated_posts[:limit]:
                score = self.calculate_score(
                    likes=post["likes"],
                    comments=post["comments"],
                    shares=post["shares"],
                    views=post.get("views", 0)
                )
                
                # Calculate engagement rate
                total_engagement = post["likes"] + post["comments"] + post["shares"]
                engagement_rate = (total_engagement / post.get("views", 1)) * 100 if post.get("views", 0) > 0 else 0
                
                scored_post = {
                    **post,
                    "score": score,
                    "engagement_rate": round(engagement_rate, 2),
                    "total_engagement": total_engagement,
                    "scraped_at": datetime.now().isoformat()
                }
                scored_posts.append(scored_post)
            
            # Sort by score (highest first)
            scored_posts.sort(key=lambda x: x["score"], reverse=True)
            
            print(f"[LinkedInScraper] Scraped and scored {len(scored_posts)} posts")
            return scored_posts
            
        except Exception as e:
            print(f"[LinkedInScraper] Error scraping posts: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    async def scrape_trending_posts(self, limit: int = 20) -> List[Dict]:
        """
        Scrape trending LinkedIn posts across all topics
        
        Args:
            limit: Maximum number of posts to scrape
        
        Returns:
            List of trending posts with scores
        """
        # Common trending keywords
        trending_keywords = [
            "AI", "Machine Learning", "Remote Work", "Leadership", 
            "Sustainability", "Cybersecurity", "Digital Transformation"
        ]
        
        all_posts = []
        for keyword in trending_keywords:
            posts = await self.scrape_posts_by_keyword(keyword, limit=5)
            all_posts.extend(posts)
        
        # Sort all posts by score
        all_posts.sort(key=lambda x: x["score"], reverse=True)
        
        return all_posts[:limit]











