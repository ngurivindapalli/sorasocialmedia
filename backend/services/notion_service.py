"""
Notion Service - Integration with Notion API
Allows users to import pages and databases from Notion as brand context
"""

import os
import httpx
from typing import Dict, Optional, List
import asyncio


class NotionService:
    """Service for interacting with Notion API"""
    
    def __init__(self):
        self.api_base_url = "https://api.notion.com/v1"
        # Support both OAuth and internal integration token
        self.internal_token = os.getenv("NOTION_SECRET", "")  # Internal integration token
        self.client_id = os.getenv("NOTION_CLIENT_ID", "")
        self.client_secret = os.getenv("NOTION_CLIENT_SECRET", "")
        # Use backend URL for callback (OAuth callback goes to backend, then redirects to frontend)
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.redirect_uri = os.getenv("NOTION_REDIRECT_URI", f"{backend_url}/api/integrations/notion/callback")
        
        if self.internal_token:
            print("[Notion] Service initialized with internal integration token")
        elif self.client_id and self.client_secret:
            print("[Notion] Service initialized with OAuth credentials")
        else:
            print("[Notion] WARNING: Notion not configured. Set NOTION_SECRET (for internal integration) or NOTION_CLIENT_ID and NOTION_CLIENT_SECRET (for OAuth)")
    
    def get_token(self, user_token: Optional[str] = None) -> Optional[str]:
        """Get Notion API token - prefer user token, then internal token, then None"""
        if user_token:
            return user_token
        if self.internal_token:
            return self.internal_token
        return None
    
    def get_authorization_url(self, state: str) -> str:
        """Get Notion OAuth authorization URL"""
        if not self.client_id:
            raise ValueError("Notion OAuth not configured. Set NOTION_CLIENT_ID and NOTION_CLIENT_SECRET")
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "owner": "user",
            "state": state
        }
        from urllib.parse import urlencode
        return f"https://api.notion.com/v1/oauth/authorize?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.notion.com/v1/oauth/token",
                    auth=(self.client_id, self.client_secret),
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Notion] Error exchanging code: {e}")
            return None
    
    async def get_user_info(self, access_token: str) -> Optional[Dict]:
        """Get authenticated user information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/users/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Notion-Version": "2022-06-28"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Notion] Error getting user info: {e}")
            return None
    
    async def search_pages(self, access_token: Optional[str] = None, query: str = "") -> List[Dict]:
        """Search for pages in user's Notion workspace"""
        token = self.get_token(access_token)
        if not token:
            print("[Notion] No token available for search")
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/search",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Notion-Version": "2022-06-28",
                        "Content-Type": "application/json"
                    },
                    json={
                        "query": query,
                        "filter": {
                            "value": "page",
                            "property": "object"
                        },
                        "page_size": 100
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except Exception as e:
            print(f"[Notion] Error searching pages: {e}")
            return []
    
    async def get_page_content(self, access_token: Optional[str], page_id: str) -> Optional[str]:
        """Get full content of a Notion page as text"""
        token = self.get_token(access_token)
        if not token:
            print("[Notion] No token available for page content")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # Get page blocks
                response = await client.get(
                    f"{self.api_base_url}/blocks/{page_id}/children",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Notion-Version": "2022-06-28"
                    },
                    params={"page_size": 100}
                )
                response.raise_for_status()
                blocks = response.json().get("results", [])
                
                # Extract text from blocks
                content_parts = []
                for block in blocks:
                    block_type = block.get("type", "")
                    if block_type == "paragraph":
                        text = self._extract_rich_text(block.get("paragraph", {}).get("rich_text", []))
                        if text:
                            content_parts.append(text)
                    elif block_type == "heading_1":
                        text = self._extract_rich_text(block.get("heading_1", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"# {text}")
                    elif block_type == "heading_2":
                        text = self._extract_rich_text(block.get("heading_2", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"## {text}")
                    elif block_type == "heading_3":
                        text = self._extract_rich_text(block.get("heading_3", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"### {text}")
                    elif block_type == "bulleted_list_item":
                        text = self._extract_rich_text(block.get("bulleted_list_item", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"- {text}")
                    elif block_type == "numbered_list_item":
                        text = self._extract_rich_text(block.get("numbered_list_item", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"1. {text}")
                    elif block_type == "to_do":
                        text = self._extract_rich_text(block.get("to_do", {}).get("rich_text", []))
                        checked = block.get("to_do", {}).get("checked", False)
                        if text:
                            content_parts.append(f"{'[x]' if checked else '[ ]'} {text}")
                    elif block_type == "quote":
                        text = self._extract_rich_text(block.get("quote", {}).get("rich_text", []))
                        if text:
                            content_parts.append(f"> {text}")
                
                return "\n\n".join(content_parts) if content_parts else None
        except Exception as e:
            print(f"[Notion] Error getting page content: {e}")
            return None
    
    def _extract_rich_text(self, rich_text: List[Dict]) -> str:
        """Extract plain text from Notion rich text array"""
        if not rich_text:
            return ""
        return "".join([item.get("plain_text", "") for item in rich_text])

