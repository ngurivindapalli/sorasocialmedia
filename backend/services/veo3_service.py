"""
Veo 3 Video Generation Service
Integrates Google DeepMind's Veo 3 via Google Cloud Vertex AI
Supports text-to-video and image-to-video generation
Reference: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation
"""

import os
import httpx
from typing import Dict, Optional, List
import asyncio
import base64
import subprocess
import json

# Try to import google-auth for service account authentication
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("[Veo3] ⚠️ google-auth library not installed. Service account auth will use gcloud CLI fallback.")
    print("[Veo3] Install with: pip install google-auth")


class Veo3Service:
    """Service for Veo 3 video generation via Google Cloud Vertex AI API"""
    
    def __init__(self):
        # Google Cloud configuration
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', '')
        self.location = os.getenv('GOOGLE_CLOUD_LOCATION', 'us-central1')
        self.model_id = os.getenv('VEO3_MODEL_ID', 'veo-3')
        
        # Authentication - can use API key, service account key, or gcloud CLI
        self.api_key = os.getenv('VEO3_API_KEY', '')  # Direct API key/access token
        self.service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        self.use_gcloud_auth = os.getenv('VEO3_USE_GCLOUD_AUTH', 'false').lower() == 'true'
        
        # Base URL for Vertex AI API
        self.api_base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        if not self.project_id:
            print("[Veo3] ⚠️ GOOGLE_CLOUD_PROJECT_ID not set. Veo 3 features will be disabled.")
            print("[Veo3] To enable: Set GOOGLE_CLOUD_PROJECT_ID in your .env file")
        else:
            print(f"[Veo3] ✓ Veo 3 service initialized (Google Cloud Vertex AI)")
            print(f"[Veo3]   Project ID: {self.project_id}")
            print(f"[Veo3]   Location: {self.location}")
            print(f"[Veo3]   Model: {self.model_id}")
            if self.api_key:
                print(f"[Veo3]   Auth: API Key")
            elif self.use_gcloud_auth:
                print(f"[Veo3]   Auth: gcloud CLI")
            elif self.service_account_key:
                print(f"[Veo3]   Auth: Service Account")
    
    async def _get_access_token(self) -> str:
        """Get Google Cloud access token for authentication"""
        # Priority 1: Direct API key/access token (if provided)
        # Note: This should be an OAuth 2.0 access token, not a simple API key
        if self.api_key:
            print("[Veo3] Using provided access token for authentication")
            # Check if it looks like an OAuth token (starts with ya29. or similar)
            if not (self.api_key.startswith('ya29.') or self.api_key.startswith('AQ.')):
                print("[Veo3] ⚠️ Warning: Token format may be incorrect. Vertex AI requires OAuth 2.0 access tokens.")
            return self.api_key
        
        # Priority 2: gcloud CLI authentication
        if self.use_gcloud_auth:
            # Use gcloud CLI to get access token
            try:
                result = subprocess.run(
                    ['gcloud', 'auth', 'print-access-token'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise Exception(
                    "Failed to get access token from gcloud CLI. "
                    "Make sure gcloud is installed and you're authenticated: gcloud auth login"
                )
        elif self.service_account_key:
            # Use service account key file
            if not os.path.exists(self.service_account_key):
                raise Exception(
                    f"Service account key file not found: {self.service_account_key}. "
                    "Please check the GOOGLE_APPLICATION_CREDENTIALS path."
                )
            
            if GOOGLE_AUTH_AVAILABLE:
                # Use google-auth library for proper service account authentication
                try:
                    credentials = service_account.Credentials.from_service_account_file(
                        self.service_account_key,
                        scopes=['https://www.googleapis.com/auth/cloud-platform']
                    )
                    # Refresh the token if needed
                    if not credentials.valid:
                        credentials.refresh(Request())
                    return credentials.token
                except Exception as e:
                    raise Exception(
                        f"Failed to authenticate with service account: {str(e)}. "
                        "Make sure the JSON key file is valid and has the correct permissions."
                    )
            else:
                # Fallback to gcloud CLI if google-auth is not available
                print("[Veo3] ⚠️ google-auth not installed, trying gcloud CLI fallback...")
                try:
                    result = subprocess.run(
                        ['gcloud', 'auth', 'activate-service-account', '--key-file', self.service_account_key],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    # Now get the token
                    result = subprocess.run(
                        ['gcloud', 'auth', 'print-access-token'],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    return result.stdout.strip()
                except (subprocess.CalledProcessError, FileNotFoundError) as e:
                    raise Exception(
                        f"Service account authentication failed. Install google-auth: pip install google-auth, "
                        f"or ensure gcloud CLI is available. Error: {str(e)}"
                    )
        else:
            raise Exception(
                "No authentication method configured. "
                "Set VEO3_API_KEY with your API key, "
                "or set VEO3_USE_GCLOUD_AUTH=true and run 'gcloud auth login', "
                "or set GOOGLE_APPLICATION_CREDENTIALS to a service account key file"
            )
    
    async def generate_video(
        self,
        prompt: str,
        duration: int = 8,
        resolution: str = "1280x720",
        image_urls: Optional[List[str]] = None,
        style: Optional[str] = None
    ) -> Dict:
        """
        Generate a video using Veo 3 via Google Cloud Vertex AI
        
        Args:
            prompt: Text description of the video
            duration: Video duration in seconds (4-60, typically 5 or 10)
            resolution: Video resolution (e.g., "1280x720", "1920x1080")
            image_urls: Optional list of image URLs to incorporate into video (image-to-video)
            style: Optional style preset (not directly supported, can be included in prompt)
            
        Returns:
            Dict with operation_name (job_id), status, and video_url when ready
        """
        if not self.project_id:
            raise Exception("Google Cloud Project ID not configured. Set GOOGLE_CLOUD_PROJECT_ID in .env file")
        
        print(f"[Veo3] Generating video with prompt: {prompt[:100]}...")
        print(f"[Veo3] Duration: {duration}s, Resolution: {resolution}")
        if image_urls:
            print(f"[Veo3] Incorporating {len(image_urls)} image(s) into video")
        
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # Build the request payload according to Vertex AI API format
            instances = []
            
            if image_urls and len(image_urls) > 0:
                # Image-to-video: include image in the instance
                # Use the first image URL
                image_data = await self._image_url_to_base64(image_urls[0])
                mime_type = self._extract_mime_type(image_urls[0])
                
                instance = {
                    "prompt": prompt,
                    "image": {
                        "bytesBase64Encoded": image_data,
                        "mimeType": mime_type
                    }
                }
            else:
                # Text-to-video
                instance = {
                    "prompt": prompt
                }
            
            instances.append(instance)
            
            # Parse resolution to get aspect ratio
            aspect_ratio = self._resolution_to_aspect_ratio(resolution)
            
            # Build parameters
            parameters = {
                "sampleCount": 1,  # Number of videos to generate (1-4)
                "aspectRatio": aspect_ratio,
                "duration": f"{duration}s"
            }
            
            # Optional: storage URI for GCS bucket (if you want videos stored in GCS)
            storage_uri = os.getenv('VEO3_STORAGE_URI', '')
            if storage_uri:
                parameters["storageUri"] = storage_uri
            
            payload = {
                "instances": instances,
                "parameters": parameters
            }
            
            # Make the API request
            # Try different model ID variations since Veo might have different naming
            possible_model_ids = [
                self.model_id,  # Try configured model ID first
                "veo-3.1-generate-001",  # Veo 3.1 model ID
                "veo-3-generate-001",    # Alternative format
                "veo-3.0-generate-001",  # Veo 3.0 model ID
                "veo-3",                 # Original format
            ]
            
            last_error = None
            working_model_id = None
            successful_response = None
            
            for model_id_attempt in possible_model_ids:
                url = f"{self.api_base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id_attempt}:predictLongRunning"
                
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    print(f"[Veo3] Trying model ID: {model_id_attempt}")
                    try:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        # Success! Use this model ID
                        working_model_id = model_id_attempt
                        successful_response = response
                        if model_id_attempt != self.model_id:
                            print(f"[Veo3] ✓ Found working model ID: {model_id_attempt}")
                            self.model_id = model_id_attempt
                        # Break out of the loop and continue with successful response
                        break
                    except httpx.HTTPStatusError as e:
                        last_error = e
                        if e.response.status_code == 404:
                            # Try next model ID
                            print(f"[Veo3]   Model ID '{model_id_attempt}' not found, trying next...")
                            continue
                        else:
                            # Different error, raise it
                            raise
            
            if not working_model_id:
                # All model IDs failed
                if last_error and last_error.response.status_code == 404:
                    error_data = last_error.response.json() if last_error.response.text else {}
                    error_msg = error_data.get('error', {}).get('message', 'Model not found')
                    print(f"[Veo3] ❌ Tried all model IDs: {', '.join(possible_model_ids)}")
                    print(f"[Veo3] Error: {error_msg}")
                    raise last_error
                elif last_error:
                    raise last_error
            
            # If we get here, we have a successful response
            if not successful_response:
                raise Exception("No successful response received from API")
            
            data = successful_response.json()
            
            # Extract operation name (this is the job_id)
            operation_name = data.get("name", "")
            if not operation_name:
                raise Exception("No operation name returned from API")
            
            print(f"[Veo3] ✓ Video generation started")
            print(f"[Veo3]   Operation: {operation_name}")
            print(f"[Veo3]   Using model: {working_model_id}")
            
            return {
                "job_id": operation_name,
                "operation_name": operation_name,
                "status": "in_progress",  # Frontend expects "in_progress" to start polling
                "progress": 0,
                "model": working_model_id,
                "created_at": 0
            }
                
        except httpx.HTTPStatusError as e:
            error_text = e.response.text[:500] if e.response.text else str(e)
            print(f"[Veo3] ❌ API error: {e.response.status_code}")
            print(f"[Veo3] Response: {error_text}")
            
            if e.response.status_code == 401:
                # Authentication error
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Authentication failed')
                    error_reason = None
                    if 'details' in error_data.get('error', {}):
                        for detail in error_data['error']['details']:
                            if detail.get('reason') == 'API_KEY_SERVICE_BLOCKED':
                                error_reason = 'API_KEY_SERVICE_BLOCKED'
                                break
                    
                    print(f"[Veo3]")
                    print(f"[Veo3] ⚠️  Authentication failed (401)")
                    if error_reason == 'API_KEY_SERVICE_BLOCKED':
                        print(f"[Veo3]    The provided API key is not valid for Vertex AI.")
                        print(f"[Veo3]    Vertex AI requires OAuth 2.0 access tokens, not API keys.")
                        print(f"[Veo3]")
                        print(f"[Veo3]    Solutions:")
                        print(f"[Veo3]    1. Use Service Account authentication (recommended):")
                        print(f"[Veo3]       - Set GOOGLE_APPLICATION_CREDENTIALS to your service account JSON file")
                        print(f"[Veo3]       - Remove VEO3_API_KEY from .env")
                        print(f"[Veo3]    2. Use gcloud CLI authentication:")
                        print(f"[Veo3]       - Run: gcloud auth login")
                        print(f"[Veo3]       - Set: VEO3_USE_GCLOUD_AUTH=true")
                        print(f"[Veo3]       - Remove VEO3_API_KEY from .env")
                        print(f"[Veo3]    3. Get a valid OAuth 2.0 access token:")
                        print(f"[Veo3]       - Use: gcloud auth print-access-token")
                        print(f"[Veo3]       - This gives you a temporary token (expires in 1 hour)")
                    else:
                        print(f"[Veo3]    Error: {error_msg}")
                        print(f"[Veo3]    Check your authentication credentials.")
                    print(f"[Veo3]")
                    print(f"[Veo3]    For now, the app will fall back to Sora 2.")
                except:
                    pass
            elif e.response.status_code == 404:
                # Model not found - Veo 3 may not be available
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Model not found')
                    print(f"[Veo3]")
                    print(f"[Veo3] ⚠️  Veo 3 model '{self.model_id}' not found in project '{self.project_id}'")
                    print(f"[Veo3]    This usually means:")
                    print(f"[Veo3]    1. Veo 3 is not available in your project yet (limited preview)")
                    print(f"[Veo3]    2. You need to request access to Veo 3 from Google Cloud")
                    print(f"[Veo3]    3. Check if Vertex AI API is fully enabled")
                    print(f"[Veo3]")
                    print(f"[Veo3]    Check available models:")
                    print(f"[Veo3]    https://console.cloud.google.com/vertex-ai/models?project={self.project_id}")
                    print(f"[Veo3]")
                    print(f"[Veo3]    For now, the app will fall back to Sora 2.")
                except:
                    pass
            
            raise Exception(f"Veo 3 API error: {e.response.status_code} - {error_text}")
        except Exception as e:
            print(f"[Veo3] Video generation error: {e}")
            raise Exception(f"Veo 3 video generation failed: {str(e)}")
    
    def _extract_mime_type(self, image_url: str) -> str:
        """Extract MIME type from image URL (data URL or HTTP URL)"""
        # Check if it's a data URL
        if image_url.startswith("data:image/"):
            # Format: data:image/png;base64,... or data:image/jpeg;base64,...
            mime_part = image_url.split(";", 1)[0]
            if mime_part.startswith("data:"):
                mime_type = mime_part[5:]  # Remove "data:" prefix
                return mime_type
        
        # For HTTP URLs, try to infer from URL extension or default to image/png
        # We'll download and check Content-Type header if needed
        if image_url.endswith(".jpg") or image_url.endswith(".jpeg"):
            return "image/jpeg"
        elif image_url.endswith(".png"):
            return "image/png"
        elif image_url.endswith(".webp"):
            return "image/webp"
        else:
            # Default to PNG for generated images
            return "image/png"
    
    async def _image_url_to_base64(self, image_url: str) -> str:
        """Convert image URL (data URL or HTTP URL) to base64 string"""
        try:
            # Check if it's already a data URL (data:image/...;base64,...)
            if image_url.startswith("data:image/"):
                # Extract base64 part from data URL
                # Format: data:image/png;base64,<base64_data>
                if "," in image_url:
                    base64_part = image_url.split(",", 1)[1]
                    # Validate it's actually base64
                    if len(base64_part) > 100:  # Reasonable minimum for an image
                        return base64_part
                raise Exception("Invalid data URL format")
            
            # Otherwise, download from HTTP/HTTPS URL
            # Limit URL length to avoid "URL too long" errors
            if len(image_url) > 2000:
                raise Exception(f"URL too long ({len(image_url)} chars). Use base64 data URL instead.")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                image_bytes = response.content
                return base64.b64encode(image_bytes).decode('utf-8')
        except Exception as e:
            print(f"[Veo3] ⚠️ Failed to process image: {e}")
            raise Exception(f"Failed to download image: {str(e)}")
    
    def _resolution_to_aspect_ratio(self, resolution: str) -> str:
        """Convert resolution string to aspect ratio format expected by API"""
        # Common resolutions to aspect ratios
        # API expects: "9:16", "16:9", "1:1", "4:3", "21:9"
        try:
            width, height = map(int, resolution.split('x'))
            # Calculate aspect ratio
            import math
            divisor = math.gcd(width, height)
            aspect_w = width // divisor
            aspect_h = height // divisor
            
            # Map to closest supported aspect ratio
            ratio = width / height
            if abs(ratio - 9/16) < 0.1:  # Vertical/portrait
                return "9:16"
            elif abs(ratio - 16/9) < 0.1:  # Horizontal/landscape
                return "16:9"
            elif abs(ratio - 1) < 0.1:  # Square
                return "1:1"
            elif abs(ratio - 4/3) < 0.1:
                return "4:3"
            elif abs(ratio - 21/9) < 0.1:
                return "21:9"
            else:
                # Default to 16:9 for landscape, 9:16 for portrait
                return "16:9" if ratio > 1 else "9:16"
        except Exception as e:
            print(f"[Veo3] ⚠️ Failed to parse resolution '{resolution}': {e}, defaulting to 16:9")
            # Default to 16:9 if parsing fails
            return "16:9"
    
    async def get_video_status(self, job_id: str) -> Dict:
        """
        Check the status of a Veo 3 video generation job
        Uses fetchPredictOperation endpoint to poll the long-running operation
        """
        if not self.project_id:
            raise Exception("Google Cloud Project ID not configured")
        
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # For predictLongRunning operations, we need to use fetchPredictOperation endpoint
            # Extract model ID and location from the operation name
            # Format: projects/{project}/locations/{location}/publishers/google/models/{model}/operations/{operation_id}
            if job_id.startswith("projects/"):
                parts = job_id.split("/")
                try:
                    # Extract location
                    location_index = parts.index("locations")
                    location = parts[location_index + 1]
                    
                    # Extract model ID (should be after "models")
                    models_index = parts.index("models")
                    model_id = parts[models_index + 1]
                    
                    # Use fetchPredictOperation endpoint
                    # Format: projects/{project}/locations/{location}/publishers/google/models/{model}:fetchPredictOperation
                    base_url = f"https://{location}-aiplatform.googleapis.com/v1"
                    fetch_endpoint = f"projects/{self.project_id}/locations/{location}/publishers/google/models/{model_id}:fetchPredictOperation"
                    url = f"{base_url}/{fetch_endpoint}"
                except (ValueError, IndexError):
                    # Fallback: use configured location and model
                    fetch_endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_id}:fetchPredictOperation"
                    url = f"{self.api_base_url}/{fetch_endpoint}"
            else:
                # Just operation ID - use configured values
                fetch_endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_id}:fetchPredictOperation"
                url = f"{self.api_base_url}/{fetch_endpoint}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Use POST with operationName in the body
            payload = {
                "operationName": job_id
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Check if operation is done
                done = data.get("done", False)
                
                # Check for errors
                if "error" in data:
                    error_msg = data["error"].get("message", "Unknown error")
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "progress": 0,
                        "video_url": None,
                        "error": error_msg
                    }
                
                # Map status to frontend format
                if done:
                    status = "completed"
                    progress = 100
                else:
                    status = "in_progress"
                    # Estimate progress based on operation metadata if available
                    progress = 50  # Default to 50% if still running
                
                # Extract video URLs from response
                video_url = None
                if done and "response" in data:
                    response_data = data["response"]
                    videos = response_data.get("videos", [])
                    if videos:
                        video = videos[0]  # Get first video
                        # Videos can be in GCS (gcsUri) or base64 encoded
                        if "gcsUri" in video:
                            # GCS URI - need to convert to downloadable URL or use download endpoint
                            gcs_uri = video["gcsUri"]
                            # For now, return the GCS URI - frontend will need to use download endpoint
                            video_url = f"/api/veo3/download/{job_id}"
                        elif "bytesBase64Encoded" in video:
                            # Base64 encoded - use download endpoint
                            video_url = f"/api/veo3/download/{job_id}"
                
                return {
                    "job_id": job_id,
                    "status": status,
                    "progress": progress,
                    "video_url": video_url,
                    "error": None
                }
        except httpx.HTTPStatusError as e:
            error_text = e.response.text[:500] if e.response.text else str(e)
            print(f"[Veo3] Status check error: {e.response.status_code}")
            print(f"[Veo3] Response: {error_text}")
            raise Exception(f"Failed to check Veo 3 video status: {str(e)}")
        except Exception as e:
            print(f"[Veo3] Status check error: {e}")
            raise Exception(f"Failed to check Veo 3 video status: {str(e)}")
    
    async def get_video_bytes(self, job_id: str, status: Dict) -> bytes:
        """
        Get video bytes from a completed Veo 3 video generation
        Extracts video data directly from the operation response
        """
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # Use fetchPredictOperation to get the video data
            if job_id.startswith("projects/"):
                parts = job_id.split("/")
                try:
                    location_index = parts.index("locations")
                    location = parts[location_index + 1]
                    models_index = parts.index("models")
                    model_id = parts[models_index + 1]
                    
                    base_url = f"https://{location}-aiplatform.googleapis.com/v1"
                    fetch_endpoint = f"projects/{self.project_id}/locations/{location}/publishers/google/models/{model_id}:fetchPredictOperation"
                    url = f"{base_url}/{fetch_endpoint}"
                except (ValueError, IndexError):
                    fetch_endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_id}:fetchPredictOperation"
                    url = f"{self.api_base_url}/{fetch_endpoint}"
            else:
                fetch_endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_id}:fetchPredictOperation"
                url = f"{self.api_base_url}/{fetch_endpoint}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "operationName": job_id
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Extract video data from response
                if "response" in data:
                    response_data = data["response"]
                    videos = response_data.get("videos", [])
                    if videos:
                        video = videos[0]
                        # Check for base64 encoded video
                        if "bytesBase64Encoded" in video:
                            return base64.b64decode(video["bytesBase64Encoded"])
                        # Check for GCS URI
                        elif "gcsUri" in video:
                            gcs_uri = video["gcsUri"]
                            raise Exception(
                                f"GCS URI download not yet implemented: {gcs_uri}. "
                                "Install google-cloud-storage and configure credentials to download from GCS."
                            )
                
                raise Exception("No video data found in operation response")
        except Exception as e:
            print(f"[Veo3] Get video bytes error: {e}")
            raise Exception(f"Failed to get Veo 3 video bytes: {str(e)}")
    
    async def download_video(self, video_url: str) -> bytes:
        """
        Download a completed Veo 3 video from a URL
        (Legacy method - use get_video_bytes instead)
        """
        try:
            if video_url.startswith("gs://"):
                raise Exception(
                    f"GCS URI download not yet implemented: {video_url}. "
                    "Install google-cloud-storage and configure credentials to download from GCS."
                )
            elif video_url.startswith("base64://"):
                import base64
                base64_data = video_url.replace("base64://", "")
                return base64.b64decode(base64_data)
            else:
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.get(video_url)
                    response.raise_for_status()
                    return response.content
        except Exception as e:
            print(f"[Veo3] Download error: {e}")
            raise Exception(f"Failed to download Veo 3 video: {str(e)}")
