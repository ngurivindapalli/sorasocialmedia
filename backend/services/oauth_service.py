import os
import httpx
from typing import Dict, Optional
from urllib.parse import urlencode, parse_qs, urlparse


class OAuthService:
    """Service for handling OAuth flows for social media platforms"""
    
    def __init__(self):
        # OAuth configuration from environment variables
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        
        # Instagram OAuth (Facebook Graph API)
        self.instagram_client_id = os.getenv("INSTAGRAM_CLIENT_ID", "")
        self.instagram_client_secret = os.getenv("INSTAGRAM_CLIENT_SECRET", "")
        self.instagram_redirect_uri = f"{self.base_url}/api/oauth/instagram/callback"
        
        # LinkedIn OAuth
        self.linkedin_client_id = os.getenv("LINKEDIN_CLIENT_ID", "")
        self.linkedin_client_secret = os.getenv("LINKEDIN_CLIENT_SECRET", "")
        self.linkedin_redirect_uri = f"{self.base_url}/api/oauth/linkedin/callback"
        
        # X (Twitter) OAuth
        self.x_client_id = os.getenv("X_CLIENT_ID", "")
        self.x_client_secret = os.getenv("X_CLIENT_SECRET", "")
        self.x_redirect_uri = f"{self.base_url}/api/oauth/x/callback"
        
        # TikTok OAuth
        self.tiktok_client_id = os.getenv("TIKTOK_CLIENT_ID", "")
        self.tiktok_client_secret = os.getenv("TIKTOK_CLIENT_SECRET", "")
        self.tiktok_redirect_uri = f"{self.base_url}/api/oauth/tiktok/callback"
    
    def get_instagram_auth_url(self, state: str) -> str:
        """Get Instagram OAuth authorization URL (Facebook Graph API)"""
        # Instagram uses Facebook Graph API for OAuth
        # The redirect_uri must be registered in Facebook App settings
        params = {
            "client_id": self.instagram_client_id,
            "redirect_uri": self.instagram_redirect_uri,
            "scope": "instagram_basic,instagram_content_publish,pages_show_list,pages_read_engagement",
            "response_type": "code",
            "state": state
        }
        # Use Facebook Graph API OAuth endpoint for Instagram
        return f"https://api.instagram.com/oauth/authorize?{urlencode(params)}"
    
    async def exchange_instagram_code(self, code: str) -> Optional[Dict]:
        """Exchange Instagram authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                # Exchange code for short-lived token
                response = await client.post(
                    "https://api.instagram.com/oauth/access_token",
                    data={
                        "client_id": self.instagram_client_id,
                        "client_secret": self.instagram_client_secret,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.instagram_redirect_uri,
                        "code": code
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Exchange for long-lived token (60 days)
                long_token_response = await client.get(
                    "https://graph.instagram.com/access_token",
                    params={
                        "grant_type": "ig_exchange_token",
                        "client_secret": self.instagram_client_secret,
                        "access_token": token_data["access_token"]
                    }
                )
                long_token_response.raise_for_status()
                long_token_data = long_token_response.json()
                
                # Get user info
                user_response = await client.get(
                    "https://graph.instagram.com/me",
                    params={
                        "fields": "id,username",
                        "access_token": long_token_data["access_token"]
                    }
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                
                return {
                    "access_token": long_token_data["access_token"],
                    "expires_in": long_token_data.get("expires_in", 5184000),  # 60 days
                    "user_id": user_data["id"],
                    "username": user_data.get("username", "")
                }
        except Exception as e:
            print(f"[OAuth] Instagram token exchange failed: {e}")
            return None
    
    def get_linkedin_auth_url(self, state: str) -> str:
        """Get LinkedIn OAuth authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.linkedin_client_id,
            "redirect_uri": self.linkedin_redirect_uri,
            "state": state,
            "scope": "openid profile email w_member_social"
        }
        return f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
    
    async def exchange_linkedin_code(self, code: str) -> Optional[Dict]:
        """Exchange LinkedIn authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://www.linkedin.com/oauth/v2/accessToken",
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.linkedin_redirect_uri,
                        "client_id": self.linkedin_client_id,
                        "client_secret": self.linkedin_client_secret
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Get user info
                user_response = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"}
                )
                user_response.raise_for_status()
                user_data = user_response.json()
                
                return {
                    "access_token": token_data["access_token"],
                    "expires_in": token_data.get("expires_in", 5184000),
                    "refresh_token": token_data.get("refresh_token"),
                    "user_id": user_data.get("sub", ""),
                    "username": user_data.get("name", "")
                }
        except Exception as e:
            print(f"[OAuth] LinkedIn token exchange failed: {e}")
            return None
    
    def get_x_auth_url(self, state: str) -> str:
        """Get X (Twitter) OAuth authorization URL"""
        params = {
            "response_type": "code",
            "client_id": self.x_client_id,
            "redirect_uri": self.x_redirect_uri,
            "scope": "tweet.read tweet.write users.read offline.access",
            "state": state,
            "code_challenge": "challenge",  # In production, use PKCE
            "code_challenge_method": "plain"
        }
        return f"https://twitter.com/i/oauth2/authorize?{urlencode(params)}"
    
    async def exchange_x_code(self, code: str) -> Optional[Dict]:
        """Exchange X authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.twitter.com/2/oauth2/token",
                    data={
                        "code": code,
                        "grant_type": "authorization_code",
                        "client_id": self.x_client_id,
                        "redirect_uri": self.x_redirect_uri,
                        "code_verifier": "challenge"  # In production, use PKCE
                    },
                    auth=(self.x_client_id, self.x_client_secret)
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Get user info
                user_response = await client.get(
                    "https://api.twitter.com/2/users/me",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"}
                )
                user_response.raise_for_status()
                user_data = user_response.json()["data"]
                
                return {
                    "access_token": token_data["access_token"],
                    "expires_in": token_data.get("expires_in", 7200),
                    "refresh_token": token_data.get("refresh_token"),
                    "user_id": user_data["id"],
                    "username": user_data.get("username", "")
                }
        except Exception as e:
            print(f"[OAuth] X token exchange failed: {e}")
            return None
    
    def get_tiktok_auth_url(self, state: str) -> str:
        """Get TikTok OAuth authorization URL"""
        params = {
            "client_key": self.tiktok_client_id,
            "redirect_uri": self.tiktok_redirect_uri,
            "scope": "user.info.basic,video.upload,video.publish",
            "response_type": "code",
            "state": state
        }
        return f"https://www.tiktok.com/v2/auth/authorize/?{urlencode(params)}"
    
    async def exchange_tiktok_code(self, code: str) -> Optional[Dict]:
        """Exchange TikTok authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://open.tiktokapis.com/v2/oauth/token/",
                    data={
                        "client_key": self.tiktok_client_id,
                        "client_secret": self.tiktok_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.tiktok_redirect_uri
                    }
                )
                response.raise_for_status()
                token_data = response.json()["data"]
                
                # Get user info
                user_response = await client.get(
                    "https://open.tiktokapis.com/v2/user/info/",
                    headers={"Authorization": f"Bearer {token_data['access_token']}"},
                    params={"fields": "open_id,union_id,avatar_url,display_name"}
                )
                user_response.raise_for_status()
                user_data = user_response.json()["data"]["user"]
                
                return {
                    "access_token": token_data["access_token"],
                    "expires_in": token_data.get("expires_in", 7200),
                    "refresh_token": token_data.get("refresh_token"),
                    "user_id": user_data.get("open_id", ""),
                    "username": user_data.get("display_name", "")
                }
        except Exception as e:
            print(f"[OAuth] TikTok token exchange failed: {e}")
            return None


