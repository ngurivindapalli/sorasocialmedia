"""
Image Generation Service
Supports Nano Banana (Google's advanced image model) only
- Nano Banana - Superior photorealism and text rendering (94% text accuracy)
- DALL-E has been completely removed as requested
"""

import os
import httpx
from typing import Dict, Optional, List
import base64
import subprocess
import urllib3

# Suppress SSL warnings if needed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Try to import Google Cloud auth libraries
try:
    from google.auth import default
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False


class ImageGenerationService:
    """Service for generating images using various AI models"""
    
    def __init__(self):
        # Gemini 3 Pro Image configuration (via Vertex AI)
        # Using Vertex AI same as Veo 3 - requires Google Cloud credentials
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', os.getenv('VEO3_PROJECT_ID', ''))
        self.location = os.getenv('VEO3_LOCATION', 'us-central1')
        self.model_id = os.getenv('GEMINI_IMAGE_MODEL_ID', 'gemini-3-pro-image-preview')
        self.api_base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        # Always use Google Cloud auth for Gemini 3 Pro Image (same as Veo 3)
        self.google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        
        if self.project_id:
            print(f"[ImageGen] ✓ Gemini 3 Pro Image initialized via Vertex AI")
            print(f"[ImageGen]   Project ID: {self.project_id}")
            print(f"[ImageGen]   Location: {self.location}")
            print(f"[ImageGen]   Model: {self.model_id}")
            print(f"[ImageGen]   Using same Google Cloud auth as Veo 3")
        else:
            print("[ImageGen] ⚠️ GOOGLE_CLOUD_PROJECT_ID not set. Gemini 3 Pro Image generation disabled.")
        
        # Other providers can be added here
        self.stable_diffusion_api_key = os.getenv('STABLE_DIFFUSION_API_KEY', '')
        self.stable_diffusion_url = os.getenv('STABLE_DIFFUSION_URL', '')
    
    async def _get_google_cloud_token(self) -> str:
        """
        Get Google Cloud access token for Gemini 3 Pro Image (same method as Veo 3)
        Uses the same authentication priority as Veo 3:
        1. VEO3_API_KEY (direct access token)
        2. VEO3_USE_GCLOUD_AUTH (gcloud CLI)
        3. GOOGLE_APPLICATION_CREDENTIALS (service account)
        """
        # Priority 1: Direct API key/access token (same as Veo 3)
        veo3_api_key = os.getenv('VEO3_API_KEY', '')
        if veo3_api_key:
            print("[ImageGen] Using VEO3_API_KEY for authentication (same as Veo 3)")
            return veo3_api_key
        
        # Priority 2: gcloud CLI authentication (same as Veo 3)
        use_gcloud_auth = os.getenv('VEO3_USE_GCLOUD_AUTH', 'false').lower() == 'true'
        if use_gcloud_auth:
            try:
                result = subprocess.run(
                    ['gcloud', 'auth', 'print-access-token'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("[ImageGen] Using gcloud CLI for authentication (same as Veo 3)")
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                raise Exception(
                    "Failed to get access token from gcloud CLI. "
                    "Make sure gcloud is installed and you're authenticated: gcloud auth login"
                )
        
        # Priority 3: Service account key file or JSON content (same as Veo 3)
        service_account_key = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        # Also check for JSON content in environment variable
        service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
        
        if service_account_key or service_account_json:
            import json
            import tempfile
            
            # Determine if we have a file path or JSON content
            key_file_path = None
            is_temp_file = False
            
            if service_account_json:
                # JSON content provided directly
                try:
                    # Validate it's JSON
                    json.loads(service_account_json)
                    # Write to temp file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        f.write(service_account_json)
                        key_file_path = f.name
                        is_temp_file = True
                    print("[ImageGen] Using service account JSON from environment variable")
                except json.JSONDecodeError:
                    raise Exception("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON")
            elif service_account_key:
                # Check if it's a file path or JSON content
                if service_account_key.strip().startswith('{'):
                    # It's JSON content, not a file path
                    try:
                        json.loads(service_account_key)
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(service_account_key)
                            key_file_path = f.name
                            is_temp_file = True
                        print("[ImageGen] Using service account JSON from GOOGLE_APPLICATION_CREDENTIALS")
                    except json.JSONDecodeError:
                        raise Exception("GOOGLE_APPLICATION_CREDENTIALS contains invalid JSON")
                elif os.path.exists(service_account_key):
                    # It's a valid file path
                    key_file_path = service_account_key
                    print("[ImageGen] Using service account key file")
                else:
                    # File doesn't exist - might be JSON content or invalid path
                    if service_account_key.strip().startswith('{'):
                        try:
                            json.loads(service_account_key)
                            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                                f.write(service_account_key)
                                key_file_path = f.name
                                is_temp_file = True
                            print("[ImageGen] Using service account JSON from GOOGLE_APPLICATION_CREDENTIALS (file not found, treating as JSON)")
                        except json.JSONDecodeError:
                            raise Exception(
                                f"Service account key file not found: {service_account_key}. "
                                "If providing JSON content, ensure it's valid JSON."
                            )
                    else:
                        raise Exception(
                            f"Service account key file not found: {service_account_key}. "
                            "Please check the GOOGLE_APPLICATION_CREDENTIALS path or provide JSON content."
                        )
            
            if key_file_path:
                if GOOGLE_AUTH_AVAILABLE:
                    try:
                        credentials = service_account.Credentials.from_service_account_file(
                            key_file_path,
                            scopes=['https://www.googleapis.com/auth/cloud-platform']
                        )
                        if not credentials.valid:
                            credentials.refresh(Request())
                        print("[ImageGen] Using service account for authentication (same as Veo 3)")
                        token = credentials.token
                        # Clean up temp file if we created one
                        if is_temp_file:
                            try:
                                os.unlink(key_file_path)
                            except:
                                pass
                        return token
                    except Exception as e:
                        # Clean up temp file if we created one
                        if is_temp_file:
                            try:
                                os.unlink(key_file_path)
                            except:
                                pass
                        raise Exception(
                            f"Failed to authenticate with service account: {str(e)}. "
                            "Make sure the JSON key file is valid and has the correct permissions."
                        )
                else:
                    # Fallback to gcloud CLI if google-auth is not available
                    print("[ImageGen] ⚠️ google-auth not installed, trying gcloud CLI fallback...")
                    try:
                        result = subprocess.run(
                            ['gcloud', 'auth', 'activate-service-account', '--key-file', key_file_path],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        result = subprocess.run(
                            ['gcloud', 'auth', 'print-access-token'],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        # Clean up temp file if we created one
                        if is_temp_file:
                            try:
                                os.unlink(key_file_path)
                            except:
                                pass
                        return result.stdout.strip()
                    except (subprocess.CalledProcessError, FileNotFoundError) as e:
                        # Clean up temp file if we created one
                        if is_temp_file:
                            try:
                                os.unlink(key_file_path)
                            except:
                                pass
                        raise Exception(
                            f"Service account authentication failed. Install google-auth: pip install google-auth, "
                            f"or ensure gcloud CLI is available. Error: {str(e)}"
                        )
        
        # No authentication method found
        raise Exception(
            "No authentication method configured for image generation. "
            "Set VEO3_API_KEY with your access token, "
            "or set VEO3_USE_GCLOUD_AUTH=true and run 'gcloud auth login', "
            "or set GOOGLE_APPLICATION_CREDENTIALS to a service account key file. "
            "(Uses same authentication as Veo 3)"
        )
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "nanobanana",
        size: str = "1024x1024",
        quality: str = "medium",
        style: Optional[str] = None,
        n: int = 1,
        aspect_ratio: Optional[str] = None
    ) -> Dict:
        """
        Generate an image from a text prompt
        
        Args:
            prompt: Text description of the image
            model: Model to use (only "nanobanana" is supported - DALL-E removed)
            size: Image size (Nano Banana: "1024x1024", "1024x1792", etc.)
            quality: Image quality ("low", "medium", "high" for Nano Banana)
            style: Style preset (not used for Nano Banana)
            n: Number of images to generate (1 for Nano Banana)
            aspect_ratio: Aspect ratio for Nano Banana (e.g., "1:1", "16:9", "4:3")
            
        Returns:
            Dict with image_url, revised_prompt, image_base64, and image data
        """
        if model == "nanobanana" or model == "nano-banana" or model == "gemini-3-pro-image":
            return await self._generate_nanobanana(prompt, size, quality, aspect_ratio)
        elif model == "stable-diffusion":
            return await self._generate_stable_diffusion(prompt, size)
        else:
            raise Exception(f"Unsupported image generation model: {model}. Only 'gemini-3-pro-image' (via Vertex AI) is supported. DALL-E has been removed.")
    
    async def _generate_nanobanana(
        self,
        prompt: str,
        size: str,
        quality: str,
        aspect_ratio: Optional[str]
    ) -> Dict:
        """
        Generate image using Gemini 3 Pro Image via Vertex AI
        Uses same Google Cloud authentication as Veo 3
        Reference: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/gemini/3-pro-image
        """
        if not self.project_id:
            raise Exception(
                "Google Cloud Project ID not configured for Gemini 3 Pro Image. "
                "Set GOOGLE_CLOUD_PROJECT_ID in .env file (same as Veo 3)"
            )
        
        print(f"[ImageGen] Generating image with Gemini 3 Pro Image via Vertex AI")
        print(f"[ImageGen] Prompt: {prompt[:100]}...")
        
        try:
            # Get Google Cloud access token (same method as Veo 3)
            access_token = await self._get_google_cloud_token()
            
            # Convert size to aspect ratio for Gemini 3 Pro Image
            # Supported aspect ratios: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
            if not aspect_ratio:
                if size == "1024x1024":
                    aspect_ratio = "1:1"
                elif size == "1024x1792":
                    aspect_ratio = "9:16"
                elif size == "1792x1024":
                    aspect_ratio = "16:9"
                else:
                    aspect_ratio = "1:1"  # Default
            
            # Use only imagegeneration@006 (Imagen 2) - skip trying other models to save time
            possible_model_ids = [
                "imagegeneration@006",  # Imagen 2 model ID - only model to try
            ]
            
            # Try configured location first, then global
            locations_to_try = [
                self.location,  # Try configured location first
                "global",  # Fallback to global
            ]
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Build request payload for Gemini 3 Pro Image
            # The model accepts prompts in the instances array
            payload = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "aspectRatio": aspect_ratio,
                    "negativePrompt": "",  # Optional: negative prompts
                    "numberOfImages": 1,
                    "sampleCount": 1,
                    "safetyFilterLevel": "block_some"  # Safety filtering
                }
            }
            
            last_error = None
            working_model_id = None
            working_location = None
            
            # Try different model IDs and locations
            for location in locations_to_try:
                api_base_url = f"https://{location}-aiplatform.googleapis.com/v1" if location != "global" else "https://aiplatform.googleapis.com/v1"
                
                for model_id_attempt in possible_model_ids:
                    # Try different endpoint formats
                    # Format 1: Standard predict endpoint
                    url1 = f"{api_base_url}/projects/{self.project_id}/locations/{location}/publishers/google/models/{model_id_attempt}:predict"
                    # Format 2: Some models might use generate endpoint
                    url2 = f"{api_base_url}/projects/{self.project_id}/locations/{location}/publishers/google/models/{model_id_attempt}:generateImages"
                    
                    urls_to_try = [url1, url2]
                    
                    for url in urls_to_try:
                        print(f"[ImageGen] Trying model: {model_id_attempt} in location: {location}")
                        print(f"[ImageGen] Calling Vertex AI: {url}")
                        
                        async with httpx.AsyncClient(timeout=120.0) as client:
                            try:
                                response = await client.post(url, json=payload, headers=headers)
                                print(f"[ImageGen] ✅ Response received - Status: {response.status_code}")
                                
                                if response.status_code == 200:
                                    # Success! Use this model ID and location
                                    working_model_id = model_id_attempt
                                    working_location = location
                                    if model_id_attempt != self.model_id or location != self.location:
                                        print(f"[ImageGen] ✓ Found working model ID: {model_id_attempt} in location: {location}")
                                        self.model_id = model_id_attempt
                                        self.location = location
                                    # Break out of all loops
                                    break
                                elif response.status_code == 401:
                                    # Authentication error - try next auth method
                                    error_text = response.text[:500] if response.text else ""
                                    print(f"[ImageGen] ⚠️ Authentication failed (401) with current method, trying fallback...")
                                    print(f"[ImageGen] Error: {error_text}")
                                    
                                    # If using VEO3_API_KEY and it fails, try other methods
                                    veo3_api_key = os.getenv('VEO3_API_KEY', '')
                                    if veo3_api_key and access_token == veo3_api_key:
                                        print(f"[ImageGen] VEO3_API_KEY failed, trying service account or gcloud...")
                                        try:
                                            # Try to get token using other methods (skip VEO3_API_KEY)
                                            original_veo3_key = os.environ.get('VEO3_API_KEY')
                                            if original_veo3_key:
                                                del os.environ['VEO3_API_KEY']  # Temporarily remove
                                            access_token = await self._get_google_cloud_token()
                                            if original_veo3_key:
                                                os.environ['VEO3_API_KEY'] = original_veo3_key  # Restore
                                            headers["Authorization"] = f"Bearer {access_token}"
                                            print(f"[ImageGen] ✓ Got new token, retrying request...")
                                            # Retry the request with new token
                                            response = await client.post(url, json=payload, headers=headers)
                                            if response.status_code == 200:
                                                working_model_id = model_id_attempt
                                                working_location = location
                                                break
                                        except Exception as fallback_error:
                                            print(f"[ImageGen] Fallback auth also failed: {fallback_error}")
                                            raise Exception(f"Authentication failed with all methods. Original error: 401 Unauthorized")
                                    else:
                                        # Already tried fallback or not using VEO3_API_KEY
                                        response.raise_for_status()
                                elif response.status_code == 404:
                                    # Model not found
                                    error_text = response.text[:500] if response.text else ""
                                    if url == url2:
                                        # If second URL format also fails, try next model
                                        print(f"[ImageGen]   Model '{model_id_attempt}' not found with generateImages endpoint, trying next model...")
                                        last_error = f"404: Model not found in {location}"
                                        break  # Break out of URL loop, try next model
                                    else:
                                        # Try second URL format
                                        print(f"[ImageGen]   Model '{model_id_attempt}' not found with predict endpoint, trying generateImages...")
                                        continue  # Try next URL format
                                else:
                                    # Different error
                                    response.raise_for_status()
                            except httpx.HTTPStatusError as e:
                                last_error = e
                                if e.response.status_code == 404:
                                    if url == url2:
                                        # Both URL formats failed, try next model
                                        print(f"[ImageGen]   Model '{model_id_attempt}' not found in {location}, trying next model...")
                                        break  # Break out of URL loop
                                    else:
                                        # Try second URL format
                                        continue  # Try next URL format
                                else:
                                    # Different error, raise it
                                    raise
                        
                        if working_model_id:
                            break  # Break out of URL loop
                    
                    if working_model_id:
                        break  # Break out of model_id loop
                    
                    if working_model_id:
                        break  # Break out of model_id loop
                
                if working_model_id:
                    break  # Break out of location loop
            
            if not working_model_id:
                # All model IDs and locations failed
                error_msg = f"Gemini 3 Pro Image model not found in any location.\n"
                error_msg += f"Tried locations: {', '.join(locations_to_try)}\n"
                error_msg += f"Tried model IDs: {', '.join(possible_model_ids)}\n"
                error_msg += f"Project: {self.project_id}\n"
                error_msg += f"\n💡 This usually means:\n"
                error_msg += f"   1. Gemini 3 Pro Image is not available in your project yet (limited preview)\n"
                error_msg += f"   2. You need to request access to Gemini 3 Pro Image from Google Cloud\n"
                error_msg += f"   3. Check available models: https://console.cloud.google.com/vertex-ai/models?project={self.project_id}\n"
                if last_error:
                    error_msg += f"\n   Last error: {last_error}"
                raise Exception(error_msg)
            
            # Now make the actual request with the working model/location
            api_base_url = f"https://{working_location}-aiplatform.googleapis.com/v1" if working_location != "global" else "https://aiplatform.googleapis.com/v1"
            url = f"{api_base_url}/projects/{self.project_id}/locations/{working_location}/publishers/google/models/{working_model_id}:predict"
            
            print(f"[ImageGen] Using model: {working_model_id} in location: {working_location}")
            print(f"[ImageGen] Parameters: aspect_ratio={aspect_ratio}")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                print(f"[ImageGen] ✅ Response received - Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text[:500] if response.text else str(response.status_code)
                    print(f"[ImageGen] ⚠️ API error: {response.status_code}")
                    print(f"[ImageGen] Response: {error_text}")
                    response.raise_for_status()
                
                data = response.json()
                print(f"[ImageGen] ✅ Response parsed successfully")
                print(f"[ImageGen] Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extract image from Vertex AI response
                # Response format: {"predictions": [{"bytesBase64Encoded": "base64string", ...}]}
                image_base64 = None
                
                if "predictions" in data and isinstance(data["predictions"], list) and len(data["predictions"]) > 0:
                    prediction = data["predictions"][0]
                    # Try different possible field names
                    image_base64 = (
                        prediction.get("bytesBase64Encoded") or
                        prediction.get("b64_image") or
                        prediction.get("image") or
                        prediction.get("base64_image") or
                        prediction.get("generatedImage")
                    )
                    
                    # If it's nested in a field
                    if not image_base64 and "generatedContent" in prediction:
                        content = prediction["generatedContent"]
                        if isinstance(content, dict) and "image" in content:
                            image_base64 = content["image"].get("bytesBase64Encoded") or content["image"].get("base64")
                
                if not image_base64:
                    # Log full response for debugging
                    print(f"[ImageGen] ⚠️ Could not find image data. Full response structure:")
                    print(f"{str(data)[:2000]}")
                    raise Exception(f"No image data found in Gemini 3 Pro Image response. Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Convert base64 to data URL for immediate use
                image_data_url = f"data:image/png;base64,{image_base64}"
                
                print(f"[ImageGen] ✅ Successfully generated image with Gemini 3 Pro Image")
                
                return {
                    "image_base64": image_base64,
                    "image_url": image_data_url,  # Data URL for immediate use
                    "revised_prompt": prompt,  # Gemini may revise, but we'll use original for now
                    "model": "gemini-3-pro-image",
                    "size": size,
                    "quality": quality,
                    "aspect_ratio": aspect_ratio
                }
        except httpx.HTTPStatusError as e:
            error_text = e.response.text[:500] if e.response.text else str(e)
            print(f"[ImageGen] Gemini 3 Pro Image API error: {e.response.status_code}")
            print(f"[ImageGen] Response: {error_text}")
            raise Exception(f"Gemini 3 Pro Image generation failed: {str(e)}")
        except Exception as e:
            print(f"[ImageGen] Gemini 3 Pro Image generation error: {e}")
            raise Exception(f"Gemini 3 Pro Image generation failed: {str(e)}")
    
    async def edit_image_gemini(
        self,
        base_image_b64: str,
        edit_prompt: str,
        preserve_style: bool = True
    ) -> Dict:
        """
        Edit an existing image using Gemini 3 Pro Image (not yet implemented)
        """
        raise Exception("Image editing is not yet supported for Gemini 3 Pro Image via Vertex AI")
    
    async def _generate_stable_diffusion(
        self,
        prompt: str,
        size: str
    ) -> Dict:
        """Generate image using Stable Diffusion API"""
        if not self.stable_diffusion_api_key:
            raise Exception("Stable Diffusion API key not configured")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.stable_diffusion_url or "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                    headers={
                        "Authorization": f"Bearer {self.stable_diffusion_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text_prompts": [{"text": prompt}],
                        "cfg_scale": 7,
                        "width": int(size.split('x')[0]),
                        "height": int(size.split('x')[1])
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                # Stable Diffusion returns base64 images
                image_base64 = data.get("artifacts", [{}])[0].get("base64")
                
                return {
                    "image_base64": image_base64,
                    "model": "stable-diffusion",
                    "size": size
                }
        except Exception as e:
            print(f"[ImageGen] Stable Diffusion error: {e}")
            raise Exception(f"Stable Diffusion generation failed: {str(e)}")
    
    async def generate_multiple_images(
        self,
        prompts: List[str],
        model: str = "nanobanana",
        size: str = "1024x1024",
        quality: str = "medium"
    ) -> List[Dict]:
        """
        Generate multiple images from a list of prompts using Gemini 3 Pro Image via Vertex AI
        DALL-E has been completely removed
        """
        results = []
        for prompt in prompts:
            try:
                result = await self.generate_image(
                    prompt, 
                    model="gemini-3-pro-image",  # Gemini 3 Pro Image via Vertex AI
                    size=size,
                    quality=quality
                )
                results.append(result)
            except Exception as e:
                print(f"[ImageGen] Failed to generate image for prompt '{prompt[:50]}...': {e}")
                results.append({"error": str(e), "prompt": prompt})
        return results
    
    async def download_image(self, image_url: str) -> bytes:
        """Download an image from a URL"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            print(f"[ImageGen] Download error: {e}")
            raise Exception(f"Failed to download image: {str(e)}")

