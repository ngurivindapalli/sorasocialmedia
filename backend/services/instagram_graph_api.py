"""
Instagram Graph API Service
Uses official Instagram Graph API instead of scraping
Requires Facebook App setup and access tokens
"""

import os
import requests
from typing import List, Dict, Optional
import time


class InstagramGraphAPIService:
    """Service for fetching Instagram videos using official Graph API"""
    
    def __init__(self):
        # Instagram Graph API configuration
        # Try Page Access Token first (more reliable), fall back to User Token
        self.access_token = os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN', '') or os.getenv('INSTAGRAM_ACCESS_TOKEN', '')
        self.instagram_account_id = os.getenv('INSTAGRAM_ACCOUNT_ID', '')  # Instagram Business Account ID
        self.graph_api_version = os.getenv('INSTAGRAM_GRAPH_API_VERSION', 'v21.0')
        self.base_url = f"https://graph.instagram.com/{self.graph_api_version}"
        
        # Check if access token is provided
        if not self.access_token:
            print("[IG Graph API] ⚠️ No access token set. Graph API features will be disabled.")
            print("[IG Graph API] To enable: Set INSTAGRAM_PAGE_ACCESS_TOKEN or INSTAGRAM_ACCESS_TOKEN in your .env file")
            print("[IG Graph API] See INSTAGRAM_GRAPH_API_SETUP.md for setup instructions")
        else:
            token_type = "Page Token" if os.getenv('INSTAGRAM_PAGE_ACCESS_TOKEN', '') else "User Token"
            print(f"[IG Graph API] ✓ Service initialized")
            print(f"[IG Graph API]   Token Type: {token_type}")
            print(f"[IG Graph API]   API Version: {self.graph_api_version}")
            print(f"[IG Graph API]   Base URL: {self.base_url}")
            if self.instagram_account_id:
                print(f"[IG Graph API]   Account ID: {self.instagram_account_id} (configured)")
            else:
                print(f"[IG Graph API]   Account ID: Not set (will try to get from username)")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a request to Instagram Graph API"""
        if not self.access_token:
            raise Exception("Instagram access token not configured. Set INSTAGRAM_ACCESS_TOKEN in .env")
        
        url = f"{self.base_url}/{endpoint}"
        request_params = {
            'access_token': self.access_token,
            **(params or {})
        }
        
        try:
            response = requests.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Instagram access token is invalid or expired. Please refresh your token.")
            elif e.response.status_code == 429:
                raise Exception("Instagram rate limit reached. Please wait before trying again.")
            else:
                raise Exception(f"Instagram Graph API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Error calling Instagram Graph API: {str(e)}")
    
    async def get_user_id(self, username: str) -> str:
        """Get Instagram User ID from username using Graph API"""
        # Note: Graph API requires either:
        # 1. Instagram Business Account ID (if you have access)
        # 2. Or use the username directly if you have the right permissions
        
        # For now, we'll try to get user info
        # This requires the user to be connected to your app
        try:
            # Try to get user by username (requires specific permissions)
            data = self._make_request(f"{username}", {'fields': 'id,username'})
            return data.get('id', '')
        except:
            # If that fails, we need the user to provide their Instagram Business Account ID
            raise Exception(
                f"Could not find Instagram user ID for @{username}. "
                "For Graph API, you need to either:\n"
                "1. Connect the Instagram account to your Facebook App\n"
                "2. Or use the Instagram Business Account ID directly"
            )
    
    async def get_user_videos(self, username: str, limit: int = 1) -> List[Dict]:
        """Fetch videos from Instagram profile using Graph API"""
        if not self.access_token:
            raise Exception("Instagram access token not configured. Set INSTAGRAM_ACCESS_TOKEN in .env")
        
        videos = []
        
        try:
            # Step 1: Get user's Instagram Business Account ID
            # Priority: Use INSTAGRAM_ACCOUNT_ID if set, otherwise try to get from username
            
            account_id = None
            
            # Option 1: Use provided Instagram Account ID (best method)
            if self.instagram_account_id:
                account_id = self.instagram_account_id
                print(f"[IG Graph API] Using provided Instagram Account ID: {account_id}")
            # Option 2: Check if username is actually an ID
            elif username.isdigit():
                account_id = username
                print(f"[IG Graph API] Using username as Account ID: {account_id}")
            else:
                # Option 3: Try to get account ID from username (requires account to be connected)
                try:
                    account_id = await self.get_user_id(username)
                except Exception as e:
                    raise Exception(
                        f"Cannot fetch videos for @{username} using Graph API.\n\n"
                        "To use Instagram Graph API:\n"
                        "1. The Instagram account must be a Business or Creator account\n"
                        "2. The account must be connected to your Facebook App\n"
                        "3. You need an access token with 'instagram_basic' and 'pages_read_engagement' permissions\n"
                        "4. Set INSTAGRAM_ACCOUNT_ID in your .env file with your Instagram Business Account ID\n\n"
                        f"Error: {str(e)}"
                    )
            
            # Step 2: Get media from the account
            print(f"[IG Graph API] Fetching media for account ID: {account_id}")
            
            params = {
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,like_count,comments_count',
                'limit': min(limit, 25)  # Graph API max is 25 per request
            }
            
            data = self._make_request(f"{account_id}/media", params)
            
            media_items = data.get('data', [])
            
            # Step 3: Filter for videos and format
            for item in media_items:
                if item.get('media_type') == 'VIDEO':
                    # Get video details
                    video_data = {
                        "id": item.get('id', ''),
                        "post_url": item.get('permalink', ''),
                        "video_url": item.get('media_url', ''),
                        "thumbnail_url": item.get('thumbnail_url', ''),
                        "views": 0,  # Graph API doesn't provide view count for all accounts
                        "likes": item.get('like_count', 0),
                        "text": item.get('caption', ''),
                        "duration": 0
                    }
                    
                    videos.append(video_data)
                    
                    if len(videos) >= limit:
                        break
            
            if not videos:
                raise Exception(f"No videos found for @{username} using Graph API")
            
            print(f"[IG Graph API] Successfully found {len(videos)} video(s)")
            return videos
            
        except Exception as e:
            print(f"[IG Graph API] Error: {str(e)}")
            raise
    
    async def get_profile_context(self, username: str) -> Dict:
        """Get profile context using Graph API"""
        if not self.access_token:
            return {
                "username": username,
                "full_name": "",
                "biography": "",
                "external_url": "",
                "is_business_account": False,
                "business_category": "",
                "followers": 0,
                "following": 0,
                "posts_count": 0,
                "is_verified": False,
                "profile_pic_url": ""
            }
        
        try:
            # Get user ID first
            account_id = await self.get_user_id(username)
            
            # Get account info
            data = self._make_request(account_id, {
                'fields': 'username,account_type,profile_picture_url'
            })
            
            return {
                "username": data.get('username', username),
                "full_name": "",
                "biography": "",
                "external_url": "",
                "is_business_account": data.get('account_type') in ['BUSINESS', 'CREATOR'],
                "business_category": "",
                "followers": 0,
                "following": 0,
                "posts_count": 0,
                "is_verified": False,
                "profile_pic_url": data.get('profile_picture_url', '')
            }
        except Exception as e:
            print(f"[IG Graph API] Error getting profile: {str(e)}")
            return {
                "username": username,
                "full_name": "",
                "biography": "",
                "external_url": "",
                "is_business_account": False,
                "business_category": "",
                "followers": 0,
                "following": 0,
                "posts_count": 0,
                "is_verified": False,
                "profile_pic_url": ""
            }
    
    async def download_video(self, video_url: str, video_id: str) -> str:
        """Download Instagram video to temporary file"""
        import os
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/ig_{video_id}.mp4"
        
        try:
            print(f"[IG Graph API] Downloading video: {video_id}")
            response = requests.get(video_url, timeout=90, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            print(f"[IG Graph API] Video downloaded: {file_path} ({len(response.content)} bytes)")
            return file_path
        except Exception as e:
            raise Exception(f"Error downloading Instagram video: {str(e)}")

