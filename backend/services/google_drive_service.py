"""
Google Drive Service - Integration with Google Drive API
Allows users to import documents from Google Drive as brand context
"""

import os
import httpx
from typing import Dict, Optional, List
import asyncio
import base64


class GoogleDriveService:
    """Service for interacting with Google Drive API"""
    
    def __init__(self):
        self.api_base_url = "https://www.googleapis.com/drive/v3"
        self.oauth_base_url = "https://accounts.google.com/o/oauth2/v2"
        self.client_id = os.getenv("GOOGLE_DRIVE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_DRIVE_CLIENT_SECRET", "")
        # Use backend URL for callback (OAuth callback goes to backend, then redirects to frontend)
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.redirect_uri = os.getenv("GOOGLE_DRIVE_REDIRECT_URI", f"{backend_url}/api/integrations/google_drive/callback")
        
        # Scopes needed for reading files
        self.scopes = [
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.metadata.readonly"
        ]
        
        if self.client_id and self.client_secret:
            print("[GoogleDrive] Service initialized with OAuth credentials")
        else:
            print("[GoogleDrive] WARNING: Google Drive OAuth not configured. Set GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET")
    
    def get_authorization_url(self, state: str) -> str:
        """Get Google Drive OAuth authorization URL"""
        from urllib.parse import urlencode
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.scopes),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        return f"{self.oauth_base_url}/auth?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str) -> Optional[Dict]:
        """Exchange authorization code for access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.oauth_base_url}/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": self.redirect_uri
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[GoogleDrive] Error exchanging code: {e}")
            return None
    
    async def refresh_access_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh access token using refresh token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.oauth_base_url}/token",
                    data={
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "refresh_token": refresh_token,
                        "grant_type": "refresh_token"
                    }
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[GoogleDrive] Error refreshing token: {e}")
            return None
    
    async def list_files(self, access_token: str, mime_type: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """List files in user's Google Drive"""
        try:
            params = {
                "pageSize": limit,
                "fields": "files(id,name,mimeType,modifiedTime,size)",
                "q": "trashed=false"
            }
            
            # Filter by MIME type if specified (e.g., Google Docs, PDFs)
            if mime_type:
                params["q"] += f" and mimeType='{mime_type}'"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/files",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    },
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("files", [])
        except Exception as e:
            print(f"[GoogleDrive] Error listing files: {e}")
            return []
    
    async def get_file_content(self, access_token: str, file_id: str, mime_type: str) -> Optional[str]:
        """Get file content as text"""
        try:
            # Determine export format based on MIME type
            export_mime_type = None
            if mime_type == "application/vnd.google-apps.document":
                export_mime_type = "text/plain"  # Export Google Docs as plain text
            elif mime_type == "application/vnd.google-apps.spreadsheet":
                export_mime_type = "text/csv"  # Export Google Sheets as CSV
            elif mime_type == "application/vnd.google-apps.presentation":
                export_mime_type = "text/plain"  # Export Google Slides as plain text
            
            async with httpx.AsyncClient() as client:
                if export_mime_type:
                    # Export Google Workspace files
                    response = await client.get(
                        f"{self.api_base_url}/files/{file_id}/export",
                        headers={
                            "Authorization": f"Bearer {access_token}"
                        },
                        params={"mimeType": export_mime_type}
                    )
                else:
                    # Download regular files
                    response = await client.get(
                        f"{self.api_base_url}/files/{file_id}",
                        headers={
                            "Authorization": f"Bearer {access_token}"
                        },
                        params={"alt": "media"}
                    )
                
                response.raise_for_status()
                
                # Try to decode as text
                try:
                    return response.text
                except:
                    # If binary, return base64 encoded
                    return base64.b64encode(response.content).decode('utf-8')
        except Exception as e:
            print(f"[GoogleDrive] Error getting file content: {e}")
            return None
    
    async def get_file_metadata(self, access_token: str, file_id: str) -> Optional[Dict]:
        """Get file metadata"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_base_url}/files/{file_id}",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    },
                    params={"fields": "id,name,mimeType,modifiedTime,size,webViewLink"}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"[GoogleDrive] Error getting file metadata: {e}")
            return None

