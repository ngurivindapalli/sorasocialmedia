import httpx
import os
from typing import List, Dict, Optional
import asyncio


class XAPIService:
    """Service for interacting with X (Twitter) API v2"""
    
    def __init__(self, bearer_token: str):
        self.bearer_token = bearer_token
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }
    
    async def get_user_videos(self, username: str, limit: int = 1) -> List[Dict]:
        """
        Fetch videos from a user - OPTIMIZED to minimize API calls
        Single API call gets user ID + tweets together
        """
        try:
            # Single API call: Get user by username with their tweets
            params = {
                "user.fields": "id,username",
                "max_results": max(5, min(limit * 2, 10)),  # Minimal results to save quota
                "tweet.fields": "public_metrics,created_at,attachments,text",
                "expansions": "attachments.media_keys",
                "media.fields": "url,type,variants,duration_ms"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # First get user ID
                user_response = await client.get(
                    f"{self.base_url}/users/by/username/{username}",
                    headers=self.headers
                )
                user_response.raise_for_status()
                user_id = user_response.json()["data"]["id"]
                
                # Then get tweets
                tweets_response = await client.get(
                    f"{self.base_url}/users/{user_id}/tweets",
                    headers=self.headers,
                    params=params
                )
                tweets_response.raise_for_status()
                data = tweets_response.json()
            
            # Extract videos with metrics
            videos = []
            tweets = data.get("data", [])
            media_items = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])} if "includes" in data else {}
            
            for tweet in tweets:
                if "attachments" in tweet:
                    for media_key in tweet["attachments"].get("media_keys", []):
                        media = media_items.get(media_key)
                        if media and media.get("type") == "video":
                            # Get highest quality video URL
                            video_url = self._get_best_video_url(media.get("variants", []))
                            if video_url:
                                videos.append({
                                    "id": tweet["id"],
                                    "tweet_url": f"https://twitter.com/{username}/status/{tweet['id']}",
                                    "video_url": video_url,
                                    "views": tweet["public_metrics"].get("impression_count", 0),
                                    "likes": tweet["public_metrics"].get("like_count", 0),
                                    "text": tweet.get("text", "")[:100] + "..." if len(tweet.get("text", "")) > 100 else tweet.get("text", ""),
                                    "duration": media.get("duration_ms", 0) / 1000  # Convert to seconds
                                })
            
            # Sort by views (engagement) and return requested amount
            videos.sort(key=lambda x: x["views"], reverse=True)
            return videos[:limit]
            
        except httpx.HTTPStatusError as e:
            raise Exception(f"X API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Error fetching videos: {str(e)}")
    
    def _get_best_video_url(self, variants: List[Dict]) -> Optional[str]:
        """Get the highest quality video URL from variants"""
        video_variants = [v for v in variants if v.get("content_type") == "video/mp4"]
        if not video_variants:
            return None
        
        # Sort by bitrate (if available) or use first one
        video_variants.sort(key=lambda x: x.get("bit_rate", 0), reverse=True)
        return video_variants[0].get("url")
    
    async def download_video(self, video_url: str, video_id: str) -> str:
        """Download video to temporary file"""
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/{video_id}.mp4"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(video_url)
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
        
        return file_path
