"""
Image Generation Service
Supports Google Imagen models via Vertex AI
- Imagen 4 Ultra - Highest quality (slower, more expensive)
- Imagen 4 - Balanced quality/speed
- Imagen 4 Fast - Faster generation
- Imagen 3 - Previous generation
- Imagen 2 - Fallback option
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
        # Imagen configuration (via Vertex AI)
        # Using Vertex AI same as Veo 3 - requires Google Cloud credentials
        # Imagen 4 requires us-central1 location per documentation
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', os.getenv('VEO3_PROJECT_ID', ''))
        self.location = os.getenv('VEO3_LOCATION', 'us-central1')
        self.model_id = os.getenv('IMAGEN_MODEL_ID', 'imagen-4.0-generate-001')
        self.api_base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        # Always use Google Cloud auth for Imagen (same as Veo 3)
        self.google_application_credentials = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '')
        
        if self.project_id:
            print(f"[ImageGen] OK Imagen initialized via Vertex AI")
            print(f"[ImageGen]   Project ID: {self.project_id}")
            print(f"[ImageGen]   Location: {self.location} (us-central1 required for Imagen 4)")
            print(f"[ImageGen]   Default Model: {self.model_id}")
            print(f"[ImageGen]   Using same Google Cloud auth as Veo 3")
        else:
            print("[ImageGen] WARNING: GOOGLE_CLOUD_PROJECT_ID not set. Imagen generation disabled.")
        
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
                # Check if it's JSON content first (before checking file path)
                service_account_key_stripped = service_account_key.strip()
                if service_account_key_stripped.startswith('{'):
                    # It's JSON content, not a file path
                    try:
                        json.loads(service_account_key_stripped)
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(service_account_key_stripped)
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
                    # File doesn't exist - check if it might be JSON content (even if it doesn't start with {)
                    # This handles cases where JSON might have whitespace or be in a different format
                    try:
                        # Try to parse as JSON
                        parsed_json = json.loads(service_account_key_stripped)
                        # If it parses successfully, treat it as JSON
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(service_account_key_stripped)
                            key_file_path = f.name
                            is_temp_file = True
                        print("[ImageGen] Using service account JSON from GOOGLE_APPLICATION_CREDENTIALS (file not found, treating as JSON)")
                    except (json.JSONDecodeError, ValueError):
                        # Not JSON and file doesn't exist
                        raise Exception(
                            f"Service account key file not found: {service_account_key}. "
                            "Please check the GOOGLE_APPLICATION_CREDENTIALS path or provide JSON content. "
                            "On Render, you can set GOOGLE_SERVICE_ACCOUNT_JSON with the full JSON content instead."
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
                    print("[ImageGen] WARNING google-auth not installed, trying gcloud CLI fallback...")
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
        if model == "nanobanana" or model == "nano-banana" or model == "gemini-3-pro-image" or model == "imagen":
            return await self._generate_nanobanana(prompt, size, quality, aspect_ratio)
        elif model == "stable-diffusion":
            return await self._generate_stable_diffusion(prompt, size)
        else:
            raise Exception(f"Unsupported image generation model: {model}. Only 'imagen' (via Vertex AI) is supported. DALL-E has been removed.")
    
    async def _generate_nanobanana(
        self,
        prompt: str,
        size: str,
        quality: str,
        aspect_ratio: Optional[str]
    ) -> Dict:
        """
        Generate image using Google Imagen 4 via Vertex AI
        Uses same Google Cloud authentication as Veo 3
        Reference: https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview
        """
        if not self.project_id:
            raise Exception(
                "Google Cloud Project ID not configured for Imagen. "
                "Set GOOGLE_CLOUD_PROJECT_ID in .env file (same as Veo 3)"
            )
        
        print(f"[ImageGen] Generating image with Google Imagen via Vertex AI")
        print(f"[ImageGen] Prompt: {prompt[:100]}...")
        
        try:
            # Get Google Cloud access token (same method as Veo 3)
            access_token = await self._get_google_cloud_token()
            
            # Convert size to aspect ratio for Imagen
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
            
            # Try Imagen 4 models first (best quality), then fallback to Imagen 3 and 2
            # Imagen 4 Ultra > Imagen 4 > Imagen 4 Fast > Imagen 3 > Imagen 2
            # Using correct model IDs from Google Cloud documentation
            possible_model_ids = [
                "imagen-4.0-ultra-generate-001",  # Imagen 4 Ultra - best quality (slower, more expensive)
                "imagen-4.0-generate-001",        # Imagen 4 - balanced quality/speed
                "imagen-4.0-fast-generate-001",   # Imagen 4 Fast - faster generation
                "imagen-3.0-generate-002",        # Imagen 3 (latest version)
                "imagen-3.0-generate-001",        # Imagen 3 (fallback)
                "imagegeneration@006",            # Imagen 2 - fallback if newer models not available
            ]
            
            # Imagen 4 requires us-central1 location per documentation
            # Try us-central1 first (required for Imagen 4), then configured location, then global
            locations_to_try = [
                "us-central1",  # Required for Imagen 4 per documentation
                self.location,  # Try configured location
                "global",  # Fallback to global
            ]
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json; charset=utf-8"
            }
            
            # Build request payload matching Imagen 4 API documentation exactly
            # Always use high-quality prompts for best results with newer models
            enhanced_prompt = f"""Ultra high quality, photorealistic, professional photography, 8K resolution, sharp focus, crisp details, perfect text rendering, readable text, high contrast, vibrant colors, professional lighting, studio quality, marketing quality, social media ready, no artifacts, no blur: {prompt}"""
            
            # Build request payload matching Imagen 4 API format from documentation
            # Format: {"instances": [{"prompt": "..."}], "parameters": {"sampleCount": 1}}
            payload = {
                "instances": [
                    {
                        "prompt": enhanced_prompt
                    }
                ],
                "parameters": {
                    "sampleCount": 1,  # Number of images to generate (1-4)
                    # Optional parameters for Imagen 4 (will be ignored if not supported)
                    "aspectRatio": aspect_ratio,
                    "negativePrompt": "blurry, low quality, pixelated, distorted text, unreadable, low resolution, grainy, artifacts, noise, AI-generated look, artificial",
                }
            }
            
            last_error = None
            working_model_id = None
            working_location = None
            
            # Try different model IDs and locations
            for location in locations_to_try:
                # Build API base URL - us-central1 is required for Imagen 4
                if location == "global":
                    api_base_url = "https://aiplatform.googleapis.com/v1"
                else:
                    api_base_url = f"https://{location}-aiplatform.googleapis.com/v1"
                
                for model_id_attempt in possible_model_ids:
                    # Use the standard :predict endpoint format as per Imagen 4 documentation
                    # Format: https://us-central1-aiplatform.googleapis.com/v1/projects/PROJECT_ID/locations/us-central1/publishers/google/models/imagen-4.0-generate-001:predict
                    url = f"{api_base_url}/projects/{self.project_id}/locations/{location}/publishers/google/models/{model_id_attempt}:predict"
                    
                    # Determine model name from model ID
                    if "imagen-4.0-ultra" in model_id_attempt:
                        model_name = "Imagen 4 Ultra"
                    elif "imagen-4.0-fast" in model_id_attempt:
                        model_name = "Imagen 4 Fast"
                    elif "imagen-4.0" in model_id_attempt:
                        model_name = "Imagen 4"
                    elif "imagen-3.0" in model_id_attempt:
                        model_name = "Imagen 3"
                    elif "@007" in model_id_attempt:
                        model_name = "Imagen 3 (legacy)"
                    elif "@008" in model_id_attempt:
                        model_name = "Imagen 4 (legacy)"
                    else:
                        model_name = "Imagen 2"
                    print(f"[ImageGen] Trying {model_name} ({model_id_attempt}) in location: {location}")
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
                                    print(f"[ImageGen] OK Found working model ID: {model_id_attempt} in location: {location}")
                                    self.model_id = model_id_attempt
                                    self.location = location
                                # Break out of all loops
                                break
                            elif response.status_code == 401:
                                # Authentication error - try next auth method
                                error_text = response.text[:500] if response.text else ""
                                print(f"[ImageGen] WARNING Authentication failed (401) with current method, trying fallback...")
                                print(f"[ImageGen] Error: {error_text}")
                                
                                # If using VEO3_API_KEY and it fails, try other methods
                                veo3_api_key = os.getenv('VEO3_API_KEY', '')
                                if veo3_api_key and access_token == veo3_api_key:
                                    print(f"[ImageGen] VEO3_API_KEY failed, trying service account or gcloud...")
                                    try:
                                        # Try to get token using other methods (skip VEO3_API_KEY)
                                        original_veo3_key = os.environ.get('VEO3_API_KEY')
                                        original_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
                                        
                                        if original_veo3_key:
                                            del os.environ['VEO3_API_KEY']  # Temporarily remove
                                        
                                        # Try gcloud CLI first (if enabled)
                                        use_gcloud_auth = os.getenv('VEO3_USE_GCLOUD_AUTH', 'false').lower() == 'true'
                                        new_token = None
                                        
                                        if use_gcloud_auth:
                                            try:
                                                result = subprocess.run(
                                                    ['gcloud', 'auth', 'print-access-token'],
                                                    capture_output=True,
                                                    text=True,
                                                    check=True
                                                )
                                                new_token = result.stdout.strip()
                                                print("[ImageGen] OK Got token from gcloud CLI")
                                            except Exception as gcloud_error:
                                                print(f"[ImageGen] gcloud CLI failed: {gcloud_error}")
                                        
                                        # If gcloud didn't work, try service account
                                        if not new_token:
                                            # Check if we have JSON content in GOOGLE_SERVICE_ACCOUNT_JSON
                                            service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')
                                            if service_account_json:
                                                print("[ImageGen] Using GOOGLE_SERVICE_ACCOUNT_JSON for fallback auth")
                                                # Temporarily set GOOGLE_APPLICATION_CREDENTIALS to JSON content
                                                if original_creds:
                                                    del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                                                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = service_account_json
                                            
                                            new_token = await self._get_google_cloud_token()
                                            
                                            # Restore original GOOGLE_APPLICATION_CREDENTIALS
                                            if original_creds:
                                                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = original_creds
                                            elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ and service_account_json:
                                                del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                                        
                                        if original_veo3_key:
                                            os.environ['VEO3_API_KEY'] = original_veo3_key  # Restore
                                        
                                        access_token = new_token
                                        headers["Authorization"] = f"Bearer {access_token}"
                                        print(f"[ImageGen] OK Got new token, retrying request...")
                                        # Retry the request with new token
                                        response = await client.post(url, json=payload, headers=headers)
                                        if response.status_code == 200:
                                            working_model_id = model_id_attempt
                                            working_location = location
                                            break
                                        elif response.status_code == 401:
                                            raise Exception("All authentication methods failed. Please check your service account JSON or gcloud setup.")
                                    except Exception as fallback_error:
                                        print(f"[ImageGen] Fallback auth also failed: {fallback_error}")
                                        error_msg = f"Authentication failed with all methods.\n"
                                        error_msg += f"Original error: 401 Unauthorized\n"
                                        error_msg += f"Fallback error: {str(fallback_error)}\n\n"
                                        error_msg += f"TIP Solutions:\n"
                                        error_msg += f"1. Set GOOGLE_SERVICE_ACCOUNT_JSON in Render with your full service account JSON content\n"
                                        error_msg += f"2. Or remove GOOGLE_APPLICATION_CREDENTIALS (it has invalid Windows path)\n"
                                        error_msg += f"3. Or set VEO3_USE_GCLOUD_AUTH=true if gcloud is available\n"
                                        error_msg += f"4. Or update VEO3_API_KEY with a fresh access token"
                                        raise Exception(error_msg)
                                else:
                                    # Already tried fallback or not using VEO3_API_KEY
                                    response.raise_for_status()
                            elif response.status_code == 404:
                                # Model not found - try next model
                                error_text = response.text[:500] if response.text else ""
                                print(f"[ImageGen]   Model '{model_id_attempt}' not found in {location}, trying next model...")
                                last_error = f"404: Model not found in {location}"
                                continue  # Try next model
                            else:
                                # Different error
                                response.raise_for_status()
                        except httpx.HTTPStatusError as e:
                            last_error = e
                            if e.response.status_code == 404:
                                print(f"[ImageGen]   Model '{model_id_attempt}' not found in {location}, trying next model...")
                                continue  # Try next model
                            else:
                                # Different error, raise it
                                raise
                    
                    if working_model_id:
                        break  # Break out of model_id loop
                
                if working_model_id:
                    break  # Break out of location loop
            
            if not working_model_id:
                # All model IDs and locations failed
                error_msg = f"Imagen model not found in any location.\n"
                error_msg += f"Tried locations: {', '.join(locations_to_try)}\n"
                error_msg += f"Tried model IDs: {', '.join(possible_model_ids)}\n"
                error_msg += f"Project: {self.project_id}\n"
                error_msg += f"\nTIP This usually means:\n"
                error_msg += f"   1. Imagen 4 is not available in your project yet (may require access request)\n"
                error_msg += f"   2. You need to request access to Imagen 4 from Google Cloud Console\n"
                error_msg += f"   3. Check available models: https://console.cloud.google.com/vertex-ai/models?project={self.project_id}\n"
                error_msg += f"   4. Imagen 4 requires us-central1 location - ensure your project has access\n"
                if last_error:
                    error_msg += f"\n   Last error: {last_error}"
                raise Exception(error_msg)
            
            # Now make the actual request with the working model/location
            api_base_url = f"https://{working_location}-aiplatform.googleapis.com/v1" if working_location != "global" else "https://aiplatform.googleapis.com/v1"
            url = f"{api_base_url}/projects/{self.project_id}/locations/{working_location}/publishers/google/models/{working_model_id}:predict"
            
            # Determine model name from working model ID
            if "imagen-4.0-ultra" in working_model_id:
                model_name = "Imagen 4 Ultra"
            elif "imagen-4.0-fast" in working_model_id:
                model_name = "Imagen 4 Fast"
            elif "imagen-4.0" in working_model_id:
                model_name = "Imagen 4"
            elif "imagen-3.0" in working_model_id:
                model_name = "Imagen 3"
            elif "@007" in working_model_id:
                model_name = "Imagen 3 (legacy)"
            elif "@008" in working_model_id:
                model_name = "Imagen 4 (legacy)"
            else:
                model_name = "Imagen 2"
            print(f"[ImageGen] OK Using {model_name} ({working_model_id}) in location: {working_location}")
            print(f"[ImageGen] Parameters: aspect_ratio={aspect_ratio}, sampleCount=1")
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                print(f"[ImageGen] ✅ Response received - Status: {response.status_code}")
                
                if response.status_code != 200:
                    error_text = response.text[:500] if response.text else str(response.status_code)
                    print(f"[ImageGen] WARNING API error: {response.status_code}")
                    print(f"[ImageGen] Response: {error_text}")
                    response.raise_for_status()
                
                data = response.json()
                print(f"[ImageGen] ✅ Response parsed successfully")
                print(f"[ImageGen] Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extract image from Vertex AI response
                # Imagen 4 response format: {"predictions": [{"bytesBase64Encoded": "base64string", ...}]}
                image_base64 = None
                
                if "predictions" in data and isinstance(data["predictions"], list) and len(data["predictions"]) > 0:
                    prediction = data["predictions"][0]
                    # Try different possible field names for image data
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
                    print(f"[ImageGen] WARNING Could not find image data. Full response structure:")
                    print(f"{str(data)[:2000]}")
                    raise Exception(f"No image data found in Imagen response. Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Convert base64 to data URL for immediate use
                image_data_url = f"data:image/png;base64,{image_base64}"
                
                print(f"[ImageGen] ✅ Successfully generated image with {model_name}")
                
                return {
                    "image_base64": image_base64,
                    "image_url": image_data_url,  # Data URL for immediate use
                    "revised_prompt": prompt,  # Imagen may revise, but we'll use original for now
                    "model": working_model_id,  # Return the actual model ID used
                    "size": size,
                    "quality": quality,
                    "aspect_ratio": aspect_ratio
                }
        except httpx.HTTPStatusError as e:
            error_text = e.response.text[:500] if e.response.text else str(e)
            print(f"[ImageGen] Imagen API error: {e.response.status_code}")
            print(f"[ImageGen] Response: {error_text}")
            raise Exception(f"Imagen generation failed: {str(e)}")
        except Exception as e:
            print(f"[ImageGen] Imagen generation error: {e}")
            raise Exception(f"Imagen generation failed: {str(e)}")
    
    async def edit_image_gemini(
        self,
        base_image_b64: str,
        edit_prompt: str,
        preserve_style: bool = True
    ) -> Dict:
        """
        Edit an existing image using Imagen (not yet implemented)
        """
        raise Exception("Image editing is not yet supported for Imagen via Vertex AI")
    
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
        Generate multiple images from a list of prompts using Imagen via Vertex AI
        DALL-E has been completely removed
        """
        results = []
        for prompt in prompts:
            try:
                result = await self.generate_image(
                    prompt, 
                    model="imagen",  # Imagen via Vertex AI
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

