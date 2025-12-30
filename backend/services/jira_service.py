"""
Jira Service - Integration with Jira API
Allows users to import issues and content from Jira as brand context
"""

import os
import httpx
from typing import Dict, Optional, List
import base64


class JiraService:
    """Service for interacting with Jira API"""
    
    def __init__(self):
        self.api_base_url = "https://api.atlassian.com"
        self.oauth_base_url = "https://auth.atlassian.com"
        self.client_id = os.getenv("JIRA_CLIENT_ID", "")
        self.client_secret = os.getenv("JIRA_CLIENT_SECRET", "")
        # Use backend URL for callback (OAuth callback goes to backend, then redirects to frontend)
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.redirect_uri = os.getenv("JIRA_REDIRECT_URI", f"{backend_url}/api/integrations/jira/callback")
        
        # Scopes needed for reading issues and content
        self.scopes = [
            "read:jira-work",
            "read:jira-user",
            "offline_access"
        ]
        
        if self.client_id and self.client_secret:
            print("[Jira] Service initialized with OAuth credentials")
        else:
            print("[Jira] WARNING: Jira OAuth not configured. Set JIRA_CLIENT_ID and JIRA_CLIENT_SECRET")
    
    def get_authorization_url(self, state: str) -> str:
        """Get Jira OAuth authorization URL"""
        from urllib.parse import urlencode
        params = {
            "audience": "api.atlassian.com",
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "redirect_uri": self.redirect_uri,
            "state": state,
            "response_type": "code",
            "prompt": "consent"
        }
        return f"{self.oauth_base_url}/authorize?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.oauth_base_url}/oauth/token",
                    data={
                        "grant_type": "authorization_code",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "redirect_uri": self.redirect_uri
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Jira] Error exchanging code: {e}")
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.oauth_base_url}/oauth/token",
                    data={
                        "grant_type": "refresh_token",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token
                    },
                    headers={
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Jira] Error refreshing token: {e}")
            return None
    
    async def get_accessible_resources(self, access_token: str) -> List[Dict]:
        """Get list of accessible Jira sites/cloud IDs"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/oauth/token/accessible-resources",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Jira] Error getting accessible resources: {e}")
            return []
    
    async def get_user_info(self, access_token: str, cloud_id: str) -> Optional[Dict]:
        """Get authenticated user information"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/ex/jira/{cloud_id}/rest/api/3/myself",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[Jira] Error getting user info: {e}")
            return None
    
    async def search_issues(self, access_token: str, cloud_id: str, jql: str = "", max_results: int = 100) -> List[Dict]:
        """Search for issues in Jira using JQL"""
        try:
            params = {
                "maxResults": max_results,
                "fields": "summary,description,status,assignee,reporter,created,updated,project,issuetype,priority"
            }
            
            if jql:
                params["jql"] = jql
            else:
                # Default: get recent issues
                params["jql"] = "ORDER BY updated DESC"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/ex/jira/{cloud_id}/rest/api/3/search",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    },
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("issues", [])
        except Exception as e:
            print(f"[Jira] Error searching issues: {e}")
            return []
    
    async def get_issue_content(self, access_token: str, cloud_id: str, issue_key: str) -> Optional[str]:
        """Get full content of a Jira issue as text"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/ex/jira/{cloud_id}/rest/api/3/issue/{issue_key}",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/json"
                    },
                    params={
                        "fields": "summary,description,status,assignee,reporter,created,updated,project,issuetype,priority,comment"
                    }
                )
                response.raise_for_status()
                issue = response.json()
                
                # Extract fields
                fields = issue.get("fields", {})
                
                # Build content string
                content_parts = []
                
                # Summary
                summary = fields.get("summary", "")
                if summary:
                    content_parts.append(f"# {summary}")
                
                # Description (may be in ADF format)
                description = fields.get("description", {})
                if description:
                    description_text = self._extract_adf_text(description)
                    if description_text:
                        content_parts.append(f"\n## Description\n{description_text}")
                
                # Status
                status = fields.get("status", {})
                if status:
                    content_parts.append(f"\n## Status\n{status.get('name', 'Unknown')}")
                
                # Project
                project = fields.get("project", {})
                if project:
                    content_parts.append(f"\n## Project\n{project.get('name', 'Unknown')}")
                
                # Issue Type
                issuetype = fields.get("issuetype", {})
                if issuetype:
                    content_parts.append(f"\n## Issue Type\n{issuetype.get('name', 'Unknown')}")
                
                # Priority
                priority = fields.get("priority", {})
                if priority:
                    content_parts.append(f"\n## Priority\n{priority.get('name', 'Unknown')}")
                
                # Assignee
                assignee = fields.get("assignee", {})
                if assignee:
                    content_parts.append(f"\n## Assignee\n{assignee.get('displayName', 'Unassigned')}")
                
                # Reporter
                reporter = fields.get("reporter", {})
                if reporter:
                    content_parts.append(f"\n## Reporter\n{reporter.get('displayName', 'Unknown')}")
                
                # Comments
                comment = fields.get("comment", {})
                if comment:
                    comments = comment.get("comments", [])
                    if comments:
                        content_parts.append(f"\n## Comments")
                        for cmt in comments:
                            author = cmt.get("author", {}).get("displayName", "Unknown")
                            body = cmt.get("body", {})
                            body_text = self._extract_adf_text(body)
                            created = cmt.get("created", "")
                            if body_text:
                                content_parts.append(f"\n### {author} ({created})\n{body_text}")
                
                return "\n".join(content_parts) if content_parts else None
        except Exception as e:
            print(f"[Jira] Error getting issue content: {e}")
            return None
    
    def _extract_adf_text(self, adf_node: Dict) -> str:
        """Extract plain text from Atlassian Document Format (ADF)"""
        if not isinstance(adf_node, dict):
            return ""
        
        text_parts = []
        
        # Handle different node types
        node_type = adf_node.get("type", "")
        content = adf_node.get("content", [])
        
        if node_type == "text":
            # Direct text node
            text = adf_node.get("text", "")
            marks = adf_node.get("marks", [])
            # Apply mark formatting if needed (bold, italic, etc.)
            if any(m.get("type") == "strong" for m in marks):
                text = f"**{text}**"
            elif any(m.get("type") == "em" for m in marks):
                text = f"*{text}*"
            return text
        
        # Recursively process content
        for child in content:
            child_text = self._extract_adf_text(child)
            if child_text:
                text_parts.append(child_text)
        
        # Add formatting based on node type
        if node_type == "paragraph":
            return "\n".join(text_parts)
        elif node_type == "heading":
            level = adf_node.get("attrs", {}).get("level", 1)
            prefix = "#" * level + " "
            return prefix + "\n".join(text_parts)
        elif node_type == "bulletList":
            return "\n".join(f"- {item}" for item in text_parts if item)
        elif node_type == "orderedList":
            return "\n".join(f"{i+1}. {item}" for i, item in enumerate(text_parts) if item)
        elif node_type == "listItem":
            return "\n".join(text_parts)
        elif node_type == "codeBlock":
            return f"```\n{''.join(text_parts)}\n```"
        elif node_type == "blockquote":
            return "\n".join(f"> {item}" for item in text_parts if item)
        else:
            return "\n".join(text_parts)





