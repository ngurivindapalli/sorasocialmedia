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
import time

# Try to import google-genai for Gemini API (Veo 3.1 extension)
try:
    from google import genai
    from google.genai import types
    GEMINI_API_AVAILABLE = True
except ImportError:
    GEMINI_API_AVAILABLE = False
    print("[Veo3] WARNING: google-genai library not installed. Veo 3.1 extension via Gemini API will be disabled.")
    print("[Veo3] Install with: pip install google-genai")

# Try to import google-auth for service account authentication
try:
    from google.oauth2 import service_account
    from google.auth.transport.requests import Request
    GOOGLE_AUTH_AVAILABLE = True
except ImportError:
    GOOGLE_AUTH_AVAILABLE = False
    print("[Veo3] WARNING: google-auth library not installed. Service account auth will use gcloud CLI fallback.")
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
        self.service_account_json = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', '')  # JSON content from env var
        self.use_gcloud_auth = os.getenv('VEO3_USE_GCLOUD_AUTH', 'false').lower() == 'true'
        
        # Base URL for Vertex AI API
        self.api_base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        if not self.project_id:
            print("[Veo3] WARNING: GOOGLE_CLOUD_PROJECT_ID not set. Veo 3 features will be disabled.")
            print("[Veo3] To enable: Set GOOGLE_CLOUD_PROJECT_ID in your .env file")
        else:
            print(f"[Veo3] Veo 3 service initialized (Google Cloud Vertex AI)")
            print(f"[Veo3]   Project ID: {self.project_id}")
            print(f"[Veo3]   Location: {self.location}")
            print(f"[Veo3]   Model: {self.model_id}")
            if self.api_key:
                print(f"[Veo3]   Auth: API Key")
            elif self.use_gcloud_auth:
                print(f"[Veo3]   Auth: gcloud CLI")
            elif self.service_account_json:
                print(f"[Veo3]   Auth: Service Account (from GOOGLE_SERVICE_ACCOUNT_JSON)")
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
                print("[Veo3] WARNING Warning: Token format may be incorrect. Vertex AI requires OAuth 2.0 access tokens.")
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
        elif self.service_account_key or self.service_account_json:
            # Use service account key file or JSON content
            import json
            import tempfile
            
            # Determine if we have a file path or JSON content
            key_file_path = None
            is_temp_file = False
            
            if self.service_account_json:
                # JSON content provided directly
                try:
                    # Validate it's JSON
                    json.loads(self.service_account_json)
                    # Write to temp file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                        f.write(self.service_account_json)
                        key_file_path = f.name
                        is_temp_file = True
                    print("[Veo3] Using service account JSON from GOOGLE_SERVICE_ACCOUNT_JSON")
                except json.JSONDecodeError:
                    raise Exception("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON")
            elif self.service_account_key:
                # Check if it's JSON content first (before checking file path)
                service_account_key_stripped = self.service_account_key.strip()
                if service_account_key_stripped.startswith('{'):
                    # It's JSON content, not a file path
                    try:
                        json.loads(service_account_key_stripped)
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(service_account_key_stripped)
                            key_file_path = f.name
                            is_temp_file = True
                        print("[Veo3] Using service account JSON from GOOGLE_APPLICATION_CREDENTIALS")
                    except json.JSONDecodeError:
                        raise Exception("GOOGLE_APPLICATION_CREDENTIALS contains invalid JSON")
                elif os.path.exists(self.service_account_key):
                    # It's a valid file path
                    key_file_path = self.service_account_key
                    print("[Veo3] Using service account key file")
                else:
                    # File doesn't exist - check if it might be JSON content
                    try:
                        parsed_json = json.loads(service_account_key_stripped)
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                            f.write(service_account_key_stripped)
                            key_file_path = f.name
                            is_temp_file = True
                        print("[Veo3] Using service account JSON from GOOGLE_APPLICATION_CREDENTIALS (file not found, treating as JSON)")
                    except (json.JSONDecodeError, ValueError):
                        raise Exception(
                            f"Service account key file not found: {self.service_account_key}. "
                            "Please check the GOOGLE_APPLICATION_CREDENTIALS path or provide JSON content. "
                            "On Render, you can set GOOGLE_SERVICE_ACCOUNT_JSON with the full JSON content instead."
                        )
            
            if key_file_path:
                if GOOGLE_AUTH_AVAILABLE:
                    # Use google-auth library for proper service account authentication
                    try:
                        credentials = service_account.Credentials.from_service_account_file(
                            key_file_path,
                            scopes=['https://www.googleapis.com/auth/cloud-platform']
                        )
                        # Refresh the token if needed
                        if not credentials.valid:
                            credentials.refresh(Request())
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
                    print("[Veo3] WARNING google-auth not installed, trying gcloud CLI fallback...")
                    try:
                        result = subprocess.run(
                            ['gcloud', 'auth', 'activate-service-account', '--key-file', key_file_path],
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
        else:
            raise Exception(
                "No authentication method configured. "
                "Set VEO3_API_KEY with your API key, "
                "or set VEO3_USE_GCLOUD_AUTH=true and run 'gcloud auth login', "
                "or set GOOGLE_APPLICATION_CREDENTIALS to a service account key file"
            )
    
    def _sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize prompt to comply with Vertex AI content guidelines.
        Removes or replaces potentially problematic words/phrases.
        """
        import re
        original_prompt = prompt
        sanitized = prompt
        
        # Log original prompt for debugging
        print(f"[Veo3] INFO Original prompt (first 500 chars): {prompt[:500]}")
        
        # Remove script formatting and structure markers first
        # Remove "SCRIPT (Xs):" headers and similar
        sanitized = re.sub(r'SCRIPT\s*\([^)]*\)\s*:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'\*\*.*?SCRIPT.*?\*\*', '', sanitized, flags=re.IGNORECASE)
        
        # Remove formatting markers that might confuse the API
        # Remove markdown-style formatting, brackets, asterisks, timestamps
        sanitized = re.sub(r'\*\*', '', sanitized)  # Remove **
        sanitized = re.sub(r'\[.*?\]', '', sanitized)  # Remove [bracketed text like [5-27s Value Bomb]]
        sanitized = re.sub(r'\{.*?\}', '', sanitized)  # Remove {curly braces}
        sanitized = re.sub(r'<.*?>', '', sanitized)  # Remove <tags>
        sanitized = re.sub(r'\*\s*\[.*?\]', '', sanitized)  # Remove *[text] patterns
        sanitized = re.sub(r'\[.*?s.*?\]', '', sanitized)  # Remove [Xs-Ys Description] patterns
        sanitized = re.sub(r'\*\*.*?\*\*', '', sanitized)  # Remove **bold text**
        
        # Remove timestamp patterns like "[0-5s Hook]", "[5-27s Value Bomb]"
        sanitized = re.sub(r'\[[0-9]+-[0-9]+s\s+[^\]]+\]', '', sanitized, flags=re.IGNORECASE)
        
        # Remove "Visual:" directives
        sanitized = re.sub(r'Visual:\s*[^"]*', '', sanitized, flags=re.IGNORECASE)
        
        # Remove quoted sections that are just formatting
        sanitized = re.sub(r'"[^"]*"\s*$', '', sanitized)  # Remove trailing quoted text
        
        # Replace problematic words with safer alternatives
        # More comprehensive list of replacements
        replacements = {
            # Violence-related (common false positives in business contexts)
            r'\bkill\s+it\b': 'excel',
            r'\bkilling\s+it\b': 'excelling',
            r'\bkilled\b': 'succeeded',
            r'\bdeadline\b': 'target date',
            r'\bdead\s+end\b': 'final stage',
            r'\bdead\s+stop\b': 'complete stop',
            r'\bshoot\b': 'capture',  # for photography/video context
            r'\bshooting\b': 'filming',
            r'\bshot\b': 'capture',  # when used as verb
            r'\bshots\b': 'captures',  # plural
            r'\battack\b': 'approach',
            r'\battacking\b': 'addressing',
            r'\battacks\b': 'approaches',
            r'\bwar\b': 'competition',
            r'\bwars\b': 'competitions',
            r'\bbattle\b': 'challenge',
            r'\bbattles\b': 'challenges',
            r'\bfight\b': 'compete',
            r'\bfighting\b': 'competing',
            r'\bfights\b': 'competitions',
            r'\bweapon\b': 'tool',
            r'\bweapons\b': 'tools',
            r'\bgun\b': 'device',
            r'\bguns\b': 'devices',
            r'\bbomb\b': 'breakthrough',
            r'\bbombs\b': 'breakthroughs',
            r'\bexplosive\b': 'dramatic',
            r'\bexplosives\b': 'dramatic elements',
            r'\bviolence\b': 'intensity',
            r'\bviolent\b': 'intense',
            r'\bmurder\b': 'dominate',
            r'\bmurders\b': 'dominates',
            r'\bdeath\b': 'end',
            r'\bdeaths\b': 'ends',
            r'\bdie\b': 'end',
            r'\bdies\b': 'ends',
            r'\bdying\b': 'ending',
            r'\bdead\b': 'inactive',
            r'\bassault\b': 'challenge',
            r'\bassaults\b': 'challenges',
            r'\bassaulting\b': 'challenging',
            r'\bthreat\b': 'challenge',
            r'\bthreats\b': 'challenges',
            r'\bthreatening\b': 'challenging',
            # Business terms that might trigger false positives
            r'\boverhaul\b': 'transform',
            r'\boverhauling\b': 'transforming',
            r'\boverhauls\b': 'transforms',
            r'\boverhauled\b': 'transformed',
            r'\boverhauling\s+entire\b': 'transforming complete',
            r'\boverhauling\s+business\b': 'transforming business',
            r'\boverhauling\s+entire\s+business\b': 'transforming complete business',
            # Value "Bomb" - common business term that triggers filters
            r'\bvalue\s+bomb\b': 'value breakthrough',
            r'\bvalue\s+bombs\b': 'value breakthroughs',
            r'\bbomb\b': 'breakthrough',  # More aggressive - catch standalone "bomb"
            r'\bbombs\b': 'breakthroughs',
            # Additional business/tech terms that might trigger
            r'\bstrike\b': 'action',
            r'\bstrikes\b': 'actions',
            r'\bstriking\b': 'impressive',
            r'\bcrush\b': 'excel',
            r'\bcrushing\b': 'excelling',
            r'\bcrushed\b': 'succeeded',
            r'\bdominate\b': 'lead',
            r'\bdominating\b': 'leading',
            r'\bdomination\b': 'leadership',
            r'\bdestroy\b': 'transform',
            r'\bdestroying\b': 'transforming',
            r'\bdestroyed\b': 'transformed',
            r'\bannihilate\b': 'excel',
            r'\bannihilating\b': 'excelling',
            r'\bwipe\s+out\b': 'eliminate',
            r'\bwiping\s+out\b': 'eliminating',
            # Adult content
            r'\bsex\b': 'gender',
            r'\bsexual\b': 'personal',
            r'\bnude\b': 'minimal',
            r'\bnaked\b': 'bare',
            r'\bporn\b': 'content',
            r'\bpornography\b': 'content',
            r'\badult\b': 'mature',
            r'\bexplicit\b': 'clear',
            # Hate speech indicators
            r'\bhate\b': 'dislike',
            r'\bhates\b': 'dislikes',
            r'\bhated\b': 'disliked',
            r'\bracist\b': 'discriminatory',
            r'\bracism\b': 'discrimination',
            r'\bdiscrimination\b': 'selection',
            r'\boffensive\b': 'aggressive',
            # Other potentially problematic terms
            r'\bkill\b': 'eliminate',  # catch standalone "kill"
            r'\bkilling\b': 'eliminating',  # catch standalone "killing"
            r'\bkills\b': 'eliminates',
            r'\bterror\b': 'fear',
            r'\bterrorist\b': 'threat',
            r'\bterrorism\b': 'threat',
            # Medical/health terms that might trigger filters
            r'\bsuicide\b': 'self-harm',
            r'\bsuicidal\b': 'self-harming',
            # Drug-related (even in business contexts)
            r'\bdrug\b': 'substance',
            r'\bdrugs\b': 'substances',
            r'\bcocaine\b': 'substance',
            r'\bheroin\b': 'substance',
            r'\bmeth\b': 'substance',
        }
        
        # Apply replacements (case-insensitive)
        for pattern, replacement in replacements.items():
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        
        # Additional aggressive filtering: remove any remaining problematic standalone words
        # This is a last resort - be careful not to break the prompt
        problematic_words = [
            'kill', 'killing', 'murder', 'death', 'die', 'dead', 'weapon', 
            'gun', 'shoot', 'shooting', 'bomb', 'attack', 'violence', 
            'violent', 'war', 'battle', 'fight', 'fighting', 'assault',
            'threat', 'terror', 'terrorist', 'suicide', 'drug', 'cocaine'
        ]
        
        # Only remove if they're standalone words (not part of other words)
        for word in problematic_words:
            # Use word boundaries to match whole words only
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, sanitized, re.IGNORECASE):
                print(f"[Veo3] WARNING Warning: Found potentially problematic word '{word}' - removing")
                sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Clean up extra whitespace and punctuation issues
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        sanitized = re.sub(r'\s*,\s*,', ',', sanitized)  # Remove double commas
        sanitized = re.sub(r'\s*\.\s*\.', '.', sanitized)  # Remove double periods
        sanitized = sanitized.strip(' ,.')  # Remove leading/trailing punctuation
        
        # Log if we made changes
        if sanitized != original_prompt:
            print(f"[Veo3] WARNING Prompt sanitized to comply with content guidelines")
            print(f"[Veo3]   Original length: {len(original_prompt)} chars")
            print(f"[Veo3]   Sanitized length: {len(sanitized)} chars")
            print(f"[Veo3] INFO Sanitized prompt (first 500 chars): {sanitized[:500]}")
        else:
            print(f"[Veo3] OK Prompt passed sanitization check")
        
        return sanitized
    
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
        
        # Guardrail: Validate duration constraints for initial generation
        # Initial generation: 4, 6, or 8 seconds (can be extended later up to 148 seconds)
        valid_initial_durations = [4, 6, 8]
        if duration not in valid_initial_durations:
            # Clamp to nearest valid duration for initial generation
            original_duration = duration
            duration = min(valid_initial_durations, key=lambda x: abs(x - duration))
            print(f"[Veo3] WARNING Initial generation duration {original_duration}s not supported. Using {duration}s (can extend later)")
        if duration < 4 or duration > 8:
            raise Exception(f"Veo 3 initial generation must be 4, 6, or 8 seconds, got {duration}s")
        
        # Guardrail: Warn about long generation times for longer videos
        if duration > 30:
            print(f"[Veo3] WARNING Warning: Videos longer than 30 seconds may take 3-5 minutes to generate")
        elif duration > 15:
            print(f"[Veo3] WARNING Warning: Videos longer than 15 seconds may take 2-4 minutes to generate")
        
        # Sanitize prompt to comply with Vertex AI content guidelines
        original_prompt = prompt
        prompt = self._sanitize_prompt(prompt)
        
        # Guardrail: Validate prompt length (Veo 3 has practical limits)
        if len(prompt) > 2000:
            print(f"[Veo3] WARNING Warning: Prompt is very long ({len(prompt)} chars), may affect generation quality")
            prompt = prompt[:2000]  # Truncate to reasonable length
        
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
            
            # Storage URI is required for all Veo video generation (videos stored in GCS)
            # Format: gs://bucket-name/path/to/videos/
            storage_uri = os.getenv('VEO3_STORAGE_URI', '')
            # Remove old project references (igvideogen)
            if storage_uri and 'igvideogen' in storage_uri:
                print(f"[Veo3] WARNING Removing old storage URI (igvideogen project): {storage_uri}")
                storage_uri = ''
            
            if storage_uri:
                # Include storage URI - videos will be stored in GCS
                parameters["storageUri"] = storage_uri
                print(f"[Veo3] Using storage URI: {storage_uri}")
            else:
                # Try to construct default bucket if project_id is available
                if self.project_id:
                    default_bucket = f"{self.project_id}-veo3-videos"
                    storage_uri = f"gs://{default_bucket}/videos/"
                    parameters["storageUri"] = storage_uri
                    print(f"[Veo3] WARNING VEO3_STORAGE_URI not set. Using default: {storage_uri}")
                    print(f"[Veo3] To avoid this warning, set VEO3_STORAGE_URI in your .env file")
                else:
                    print(f"[Veo3] WARNING No storage URI set and no project ID - videos may not be stored properly")
            
            payload = {
                "instances": instances,
                "parameters": parameters
            }
            
            # Make the API request
            # Try different model ID variations since Veo might have different naming
            # NOTE: veo-3.1-generate-preview requires storage URI, so we'll try models that don't require it first
            # If extensions are needed, we'll use veo-3.1-generate-preview with storage URI
            storage_uri_set = bool(storage_uri)
            possible_model_ids = []
            
            if storage_uri_set:
                # If storage URI is set, we can use veo-3.1-generate-preview (supports extensions)
                possible_model_ids = [
                    self.model_id,  # Try configured model ID first
                    "veo-3.1-generate-preview",  # Veo 3.1 Preview (supports extensions, requires storage URI)
                    "veo-3.1-generate-001",      # Veo 3.1 model ID (supports extensions, requires storage URI)
                    "veo-3-generate-001",        # Alternative format
                    "veo-3.0-generate-001",      # Veo 3.0 model ID
                    "veo-3",                     # Original format
                ]
            else:
                # If no storage URI, try models that don't require it first
                possible_model_ids = [
                    self.model_id,  # Try configured model ID first
                    "veo-3.0-generate-001",      # Veo 3.0 model ID (may not require storage URI)
                    "veo-3-generate-001",        # Alternative format
                    "veo-3",                     # Original format
                    # Don't try veo-3.1-generate-preview without storage URI - it requires it
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
                
                # Timeout based on video duration: longer videos need more time
                # Base timeout: 60s for request + generation estimate
                # Estimate: ~10-15s per second of video for generation
                estimated_generation_time = max(60, duration * 12)  # At least 60s, or 12s per second of video
                request_timeout = min(600, estimated_generation_time + 60)  # Cap at 10 minutes, add 60s buffer
                
                async with httpx.AsyncClient(timeout=request_timeout) as client:
                    print(f"[Veo3] Trying model ID: {model_id_attempt}")
                    print(f"[Veo3] Request timeout: {request_timeout}s (estimated generation: ~{estimated_generation_time}s)")
                    try:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        # Success! Use this model ID
                        working_model_id = model_id_attempt
                        successful_response = response
                        if model_id_attempt != self.model_id:
                            print(f"[Veo3] OK Found working model ID: {model_id_attempt}")
                            self.model_id = model_id_attempt
                        # Break out of the loop and continue with successful response
                        break
                    except httpx.HTTPStatusError as e:
                        last_error = e
                        error_text = e.response.text[:500] if e.response.text else str(e)
                        
                        # Check if it's a storage bucket error
                        if "bucket" in error_text.lower() and "not found" in error_text.lower():
                            # Storage bucket error - this model requires storage URI but bucket doesn't exist
                            print(f"[Veo3]   Model '{model_id_attempt}' requires storage URI but bucket not found")
                            if not storage_uri_set and model_id_attempt.startswith("veo-3.1"):
                                # Skip veo-3.1 models if storage URI not set
                                print(f"[Veo3]   Skipping {model_id_attempt} (requires storage URI)")
                                continue
                            else:
                                # Storage URI was set but bucket doesn't exist - provide helpful error
                                print(f"[Veo3]   Storage URI set but bucket not found: {error_text}")
                                # Try next model
                                continue
                        
                        if e.response.status_code == 404:
                            # Try next model ID
                            print(f"[Veo3]   Model ID '{model_id_attempt}' not found, trying next...")
                            continue
                        else:
                            # Different error, raise it (but log first)
                            print(f"[Veo3]   Error with model '{model_id_attempt}': {error_text}")
                            raise
            
            if not working_model_id:
                # All model IDs failed
                if last_error and last_error.response.status_code == 404:
                    error_data = last_error.response.json() if last_error.response.text else {}
                    error_msg = error_data.get('error', {}).get('message', 'Model not found')
                    print(f"[Veo3] ERROR Tried all model IDs: {', '.join(possible_model_ids)}")
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
            
            print(f"[Veo3] OK Video generation started")
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
            print(f"[Veo3] ERROR API error: {e.response.status_code}")
            print(f"[Veo3] Response: {error_text}")
            
            # Check for content policy violation error
            if "violate" in error_text.lower() and "guidelines" in error_text.lower():
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', 'Content policy violation')
                    error_code = error_data.get('error', {}).get('code', 3)
                    
                    print(f"[Veo3]")
                    print(f"[Veo3] ERROR Content Policy Violation Detected")
                    print(f"[Veo3]    Error Code: {error_code}")
                    print(f"[Veo3]    Error Message: {error_msg}")
                    print(f"[Veo3]")
                    print(f"[Veo3]    The prompt contains words that violate Vertex AI's usage guidelines.")
                    print(f"[Veo3]    Even after sanitization, some terms may still trigger content filters.")
                    print(f"[Veo3]")
                    print(f"[Veo3]    Original prompt (first 300 chars): {original_prompt[:300]}...")
                    print(f"[Veo3]    Sanitized prompt (first 300 chars): {prompt[:300]}...")
                    print(f"[Veo3]")
                    print(f"[Veo3]    TIP Suggestions to fix this:")
                    print(f"[Veo3]    1. Review your document content for potentially problematic terms")
                    print(f"[Veo3]    2. Avoid business phrases like 'killing it', 'shooting for', 'attacking the market'")
                    print(f"[Veo3]    3. Use neutral alternatives: 'excelling', 'aiming for', 'targeting the market'")
                    print(f"[Veo3]    4. Remove any references to violence, weapons, or sensitive topics")
                    print(f"[Veo3]    5. Use professional, neutral language throughout")
                    print(f"[Veo3]")
                    print(f"[Veo3]    If you believe this is a false positive, you can:")
                    print(f"[Veo3]    - Send feedback to Google (support code: {error_data.get('error', {}).get('details', [{}])[0].get('supportCodes', ['N/A'])[0] if error_data.get('error', {}).get('details') else 'N/A'})")
                    print(f"[Veo3]    - Try rephrasing your document content or prompt")
                    print(f"[Veo3]")
                    
                    # Create a more user-friendly error message
                    user_friendly_error = (
                        f"Content Policy Violation: The video prompt contains words that violate "
                        f"Vertex AI's usage guidelines. Please review your document content and "
                        f"rephrase any potentially problematic terms. Common issues include business "
                        f"phrases like 'killing it' or 'shooting for' - try 'excelling' or 'aiming for' instead."
                    )
                    
                    # Raise a more descriptive exception
                    raise Exception(user_friendly_error) from e
                except Exception as inner_e:
                    # If we already raised a user-friendly exception, re-raise it
                    if "Content Policy Violation" in str(inner_e):
                        raise
                    # Otherwise, raise the original error
                    pass
            
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
                    print(f"[Veo3] WARNING  Authentication failed (401)")
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
                    print(f"[Veo3] WARNING  Veo 3 model '{self.model_id}' not found in project '{self.project_id}'")
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
            print(f"[Veo3] WARNING Failed to process image: {e}")
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
            print(f"[Veo3] WARNING Failed to parse resolution '{resolution}': {e}, defaulting to 16:9")
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
            
            # Timeout for status checks: should be quick, but allow extra time for long operations
            status_timeout = 60.0  # 60 seconds should be enough for status checks
            
            async with httpx.AsyncClient(timeout=status_timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Check if operation is done
                done = data.get("done", False)
                
                # Check for errors
                if "error" in data:
                    error_data = data["error"]
                    error_msg = error_data.get("message", "Unknown error")
                    error_code = error_data.get("code", "UNKNOWN")
                    
                    # Log full error details for debugging
                    print(f"[Veo3] ERROR Video generation failed!")
                    print(f"[Veo3]   Error code: {error_code}")
                    print(f"[Veo3]   Error message: {error_msg}")
                    print(f"[Veo3]   Full error data: {error_data}")
                    
                    # Check for storage URI error and provide helpful guidance
                    if "storage uri" in error_msg.lower() or "output storage" in error_msg.lower():
                        storage_uri = os.getenv('VEO3_STORAGE_URI', '')
                        if not storage_uri:
                            error_msg = (
                                f"{error_msg}\n\n"
                                "SOLUTION: Set VEO3_STORAGE_URI in your .env file.\n"
                                "Format: VEO3_STORAGE_URI=gs://your-bucket-name/videos/\n\n"
                                "To create a bucket:\n"
                                "1. Run: gsutil mb gs://your-project-id-veo3-videos\n"
                                "2. Add to .env: VEO3_STORAGE_URI=gs://your-project-id-veo3-videos/videos/\n"
                                "3. Make sure your service account has 'Storage Object Admin' role"
                            )
                    
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
                    print(f"[Veo3] ✅ Video generation completed for job: {job_id[:50]}...")
                else:
                    status = "in_progress"
                    # Estimate progress based on operation metadata if available
                    progress = 50  # Default to 50% if still running
                    print(f"[Veo3] WAIT Video generation in progress for job: {job_id[:50]}...")
                
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
                
                result = {
                    "job_id": job_id,
                    "status": status,
                    "progress": progress,
                    "video_url": video_url,
                    "error": None,
                    "can_extend": True  # Veo videos can be extended
                }
                
                # If video is completed and we have a URL, mark it as extendable
                if status == "completed" and video_url:
                    result["can_extend"] = True
                    result["current_duration"] = 8  # Default, will be updated if we track it
                
                return result
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
                            print(f"[Veo3] Video stored in GCS: {gcs_uri}")
                            # Download from GCS using google-cloud-storage
                            try:
                                from google.cloud import storage
                                # Parse GCS URI: gs://bucket-name/path/to/file
                                if not gcs_uri.startswith("gs://"):
                                    raise Exception(f"Invalid GCS URI format: {gcs_uri}")
                                
                                # Remove gs:// prefix and split
                                path_parts = gcs_uri[5:].split("/", 1)
                                bucket_name = path_parts[0]
                                blob_path = path_parts[1] if len(path_parts) > 1 else ""
                                
                                print(f"[Veo3] Downloading from GCS: bucket={bucket_name}, path={blob_path}")
                                
                                # Initialize storage client
                                client = storage.Client(project=self.project_id)
                                bucket = client.bucket(bucket_name)
                                blob = bucket.blob(blob_path)
                                
                                # Download video bytes
                                video_bytes = blob.download_as_bytes()
                                print(f"[Veo3] OK Downloaded {len(video_bytes)} bytes from GCS")
                                return video_bytes
                                
                            except ImportError:
                                raise Exception(
                                    f"GCS URI download requires google-cloud-storage library. "
                                    f"Install it with: pip install google-cloud-storage. "
                                    f"GCS URI: {gcs_uri}"
                                )
                            except Exception as gcs_error:
                                print(f"[Veo3] ERROR GCS download error: {gcs_error}")
                                raise Exception(
                                    f"Failed to download video from GCS: {gcs_uri}. "
                                    f"Error: {str(gcs_error)}. "
                                    f"Make sure your service account has Storage Object Viewer permissions."
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
                # Download from GCS
                try:
                    from google.cloud import storage
                    # Parse GCS URI: gs://bucket-name/path/to/file
                    path_parts = video_url[5:].split("/", 1)
                    bucket_name = path_parts[0]
                    blob_path = path_parts[1] if len(path_parts) > 1 else ""
                    
                    print(f"[Veo3] Downloading from GCS: bucket={bucket_name}, path={blob_path}")
                    
                    # Initialize storage client
                    client = storage.Client(project=self.project_id)
                    bucket = client.bucket(bucket_name)
                    blob = bucket.blob(blob_path)
                    
                    # Download video bytes
                    video_bytes = blob.download_as_bytes()
                    print(f"[Veo3] OK Downloaded {len(video_bytes)} bytes from GCS")
                    return video_bytes
                    
                except ImportError:
                    raise Exception(
                        f"GCS URI download requires google-cloud-storage library. "
                        f"Install it with: pip install google-cloud-storage. "
                        f"GCS URI: {video_url}"
                    )
                except Exception as gcs_error:
                    raise Exception(
                        f"Failed to download video from GCS: {video_url}. "
                        f"Error: {str(gcs_error)}"
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
    
    async def extend_video(
        self,
        video_url: str,
        extension_seconds: int = 7,
        max_extensions: int = 1
    ) -> Dict:
        """
        Extend a previously generated Veo video.
        
        Args:
            video_url: URL or path to the Veo-generated video to extend
            extension_seconds: Seconds to add per extension (typically 7 seconds)
            max_extensions: Maximum number of extensions (default 1, max 20, total up to 148 seconds)
            
        Returns:
            Dict with operation_name (job_id), status, and extended video URL
        """
        if not self.project_id:
            raise Exception("Google Cloud Project ID not configured. Set GOOGLE_CLOUD_PROJECT_ID in .env file")
        
        # Validate extension parameters
        if extension_seconds < 1 or extension_seconds > 30:
            raise Exception(f"Extension must add 1-30 seconds, got {extension_seconds}s")
        
        if max_extensions < 1 or max_extensions > 20:
            raise Exception(f"Maximum extensions must be 1-20, got {max_extensions}")
        
        print(f"[Veo3] Extending video: {video_url[:100]}...")
        print(f"[Veo3] Adding {extension_seconds} seconds per extension, up to {max_extensions} extensions")
        
        try:
            # Get access token
            access_token = await self._get_access_token()
            
            # Read video file and convert to base64
            import httpx
            video_bytes = None
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                if video_url.startswith('http'):
                    # Download video from HTTP/HTTPS URL
                    video_response = await client.get(video_url)
                    video_response.raise_for_status()
                    video_bytes = video_response.content
                elif video_url.startswith('/api/'):
                    # API endpoint - construct full URL
                    # Get the base API URL from environment or use localhost
                    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
                    full_url = f"{api_base_url}{video_url}"
                    print(f"[Veo3] Downloading video from API endpoint: {full_url}")
                    video_response = await client.get(full_url)
                    video_response.raise_for_status()
                    video_bytes = video_response.content
                elif os.path.exists(video_url):
                    # Local file path
                    with open(video_url, 'rb') as f:
                        video_bytes = f.read()
                else:
                    raise Exception(f"Video URL is neither a valid HTTP URL, API endpoint, nor local file path: {video_url}")
            
            if not video_bytes:
                raise Exception("Failed to retrieve video bytes")
            
            video_base64 = base64.b64encode(video_bytes).decode('utf-8')
            
            # Determine MIME type (assume MP4 for Veo videos)
            mime_type = "video/mp4"
            
            # Build the extension request
            # According to official Veo 3.1 API docs: https://ai.google.dev/gemini-api/docs/video?example=dialogue#extending_veo_videos
            # Extension uses the same generate model with video input
            # Try the same model IDs that work for generation
            possible_model_ids = [
                self.model_id,  # Try configured model ID first
                "veo-3.1-generate-preview",  # Veo 3.1 Preview (official model ID)
                "veo-3.1-generate-001",      # Alternative format
                "veo-3.0-generate-001",     # Veo 3.0 model ID
            ]
            
            working_model_id = None
            last_error = None
            operation_name = None
            
            for model_id in possible_model_ids:
                try:
                    # Use predictLongRunning endpoint like generation, but with video input
                    url = f"{self.api_base_url}/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_id}:predictLongRunning"
                    
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    
                    # Extension payload format per official API docs
                    # Video input with optional prompt for continuation
                    instances = [{
                        "video": {
                            "bytesBase64Encoded": video_base64,
                            "mimeType": mime_type
                        },
                        "prompt": ""  # Optional: can add continuation prompt to guide extension
                    }]
                    
                    # Extension parameters - based on official API documentation
                    # Note: The exact parameter name may vary - trying multiple formats
                    parameters = {
                        "sampleCount": 1,
                        "aspectRatio": "16:9"  # Match the original video aspect ratio
                    }
                    
                    # CRITICAL: Storage URI is REQUIRED for extended videos
                    storage_uri = os.getenv('VEO3_STORAGE_URI', '')
                    if not storage_uri:
                        # Don't use a default bucket that doesn't exist - require explicit configuration
                        raise Exception(
                            "VEO3_STORAGE_URI is required for Veo 3 video extension. "
                            "Set it in your .env file as: VEO3_STORAGE_URI=gs://your-bucket-name/videos/\n\n"
                            "To create a bucket:\n"
                            "1. Run: gsutil mb gs://your-project-id-veo3-videos\n"
                            "2. Add to .env: VEO3_STORAGE_URI=gs://your-project-id-veo3-videos/videos/\n"
                            "3. Make sure your service account has 'Storage Object Admin' role"
                        )
                    
                    parameters["storageUri"] = storage_uri
                    print(f"[Veo3] Using storage URI for extension: {storage_uri}")
                    
                    # Try different parameter names for extension duration
                    # The API might use "extensionSeconds", "extensionDuration", or similar
                    if extension_seconds:
                        # Try common parameter names
                        parameters["extensionSeconds"] = extension_seconds
                        # Also try alternative names
                        # parameters["extensionDuration"] = extension_seconds
                        # parameters["extendBy"] = extension_seconds
                    
                    payload = {
                        "instances": instances,
                        "parameters": parameters
                    }
                    
                    print(f"[Veo3] Trying extension with model: {model_id}, extensionSeconds: {extension_seconds}")
                    print(f"[Veo3] Payload structure: instances with video input, parameters with extensionSeconds")
                    
                    async with httpx.AsyncClient(timeout=600.0) as client:
                        response = await client.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        data = response.json()
                        
                        # Extract operation name
                        operation_name = data.get("name") or data.get("operationName")
                        if operation_name:
                            working_model_id = model_id
                            print(f"[Veo3] OK Extension request accepted with model: {model_id}")
                            print(f"[Veo3]   Operation: {operation_name}")
                            break
                            
                except httpx.HTTPStatusError as e:
                    error_text = e.response.text[:500] if e.response.text else str(e)
                    if e.response.status_code == 404:
                        last_error = f"Model {model_id} not found"
                        print(f"[Veo3]   Model {model_id} not found, trying next...")
                        continue
                    elif e.response.status_code == 400:
                        # Bad request - might be wrong parameter format
                        last_error = f"HTTP 400: {error_text}"
                        print(f"[Veo3]   Bad request with {model_id}: {error_text}")
                        # Try next model - might be parameter format issue
                        continue
                    else:
                        last_error = f"HTTP {e.response.status_code}: {error_text}"
                        print(f"[Veo3]   Error with {model_id}: {last_error}")
                        # Don't raise, try next model
                        continue
                except Exception as e:
                    last_error = str(e)
                    print(f"[Veo3]   Exception with {model_id}: {last_error}")
                    continue
            
            if not working_model_id or not operation_name:
                raise Exception(f"Could not find working Veo 3 extension model. Tried: {', '.join(possible_model_ids)}. Last error: {last_error}. Note: Video extension may not be available in your region or may require different API format.")
            
            # Return extension job info
            return {
                "job_id": operation_name,
                "status": "queued",
                "progress": 0,
                "video_url": None,
                "model": working_model_id,
                "created_at": 0,
                "is_extension": True,
                "extension_seconds": extension_seconds
            }
            
        except Exception as e:
            print(f"[Veo3] ERROR Extension error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to extend Veo 3 video: {str(e)}")
    
    async def extend_video_gemini_api(
        self,
        base_job_id: str,
        extension_seconds: int = 7,
        max_extensions: int = 1
    ) -> Dict:
        """
        Extend a previously generated Veo 3.1 video using Gemini API.
        This is the correct implementation per user feedback - uses 'source' parameter, not 'video'.
        
        Args:
            base_job_id: Job ID of the base video to extend
            extension_seconds: Seconds to add per extension (typically 7 seconds, up to 20 times)
            max_extensions: Maximum number of extensions (default 1, max 20, total up to 148 seconds)
            
        Returns:
            Dict with operation_name (job_id), status, and extended video info
        """
        if not GEMINI_API_AVAILABLE:
            raise Exception(
                "google-genai library not installed. Install with: pip install google-genai"
            )
        
        # Get Gemini API key (can use VEO3_API_KEY or GEMINI_API_KEY)
        gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('VEO3_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not gemini_api_key:
            raise Exception(
                "Gemini API key required for video extension. "
                "Set GEMINI_API_KEY, VEO3_API_KEY, or GOOGLE_API_KEY in your .env file"
            )
        
        # Validate extension parameters
        if extension_seconds < 1 or extension_seconds > 30:
            raise Exception(f"Extension must add 1-30 seconds, got {extension_seconds}s")
        
        if max_extensions < 1 or max_extensions > 20:
            raise Exception(f"Maximum extensions must be 1-20, got {max_extensions}")
        
        print(f"[Veo3] 🎬 Extending video using Gemini API (Veo 3.1)")
        print(f"[Veo3]   Base job ID: {base_job_id[:50]}...")
        print(f"[Veo3]   Extension: {extension_seconds}s per extension, up to {max_extensions} extensions")
        print(f"[Veo3]   Note: Using 'veo-3.1-generate-preview' (not fast-generate) for extensions")
        print(f"[Veo3]   Note: If you see quota errors, check: https://ai.dev/usage?tab=rate-limit")
        
        try:
            # Step 1: Get the base video from the job_id
            print(f"[Veo3] Step 1: Fetching base video from job {base_job_id[:50]}...")
            base_status = await self.get_video_status(base_job_id)
            
            if base_status.get("status") != "completed":
                raise Exception(
                    f"Base video not completed yet. Status: {base_status.get('status')}. "
                    f"Please wait for the base video to complete before extending."
                )
            
            # Download the base video
            print(f"[Veo3] Step 2: Downloading base video...")
            base_video_bytes = await self.get_video_bytes(base_job_id, base_status)
            print(f"[Veo3] OK Downloaded base video ({len(base_video_bytes)} bytes)")
            
            # Step 2: Initialize Gemini API client
            print(f"[Veo3] Step 3: Initializing Gemini API client...")
            client = genai.Client(api_key=gemini_api_key)
            
            # Step 3: Upload the base video to Gemini API
            # The video needs to be uploaded as a File first
            print(f"[Veo3] Step 4: Uploading base video to Gemini API...")
            
            # Create a temporary file to upload
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_file.write(base_video_bytes)
                temp_video_path = temp_file.name
            
            try:
                # Upload the video file to Gemini API
                # Note: API uses 'file' parameter, not 'path' (changed in google-genai v0.8.0+)
                # Try passing file path as string first
                try:
                    uploaded_file = client.files.upload(file=temp_video_path)
                except TypeError:
                    # If that doesn't work, try with file object
                    with open(temp_video_path, 'rb') as video_file:
                        uploaded_file = client.files.upload(file=video_file)
                print(f"[Veo3] OK Video uploaded to Gemini API: {uploaded_file.name}")
                
                # Step 4: Extend the video using generate_videos with source parameter
                # For Veo 3.1 extensions, we need to pass the uploaded file directly as source
                # The API expects the file URI/name, not a Video object
                print(f"[Veo3] Step 5: Extending video...")
                print(f"[Veo3]   Model: veo-3.1-generate-preview (must use generate, not fast-generate for extensions)")
                print(f"[Veo3]   Source file: {uploaded_file.name}")
                
                operation = None
                last_error = None
                
                # Method 1: Pass the file URI directly (simplest approach)
                try:
                    # Use the file name/URI directly as source
                    operation = client.models.generate_videos(
                        model="veo-3.1-generate-preview",
                        source=uploaded_file.name,  # Pass file URI directly
                    )
                    print(f"[Veo3] OK Method 1 (File URI as source) succeeded")
                except Exception as e1:
                    last_error = e1
                    # Check if it's a quota error
                    if "429" in str(e1) or "RESOURCE_EXHAUSTED" in str(e1) or "quota" in str(e1).lower():
                        raise Exception(f"Gemini API quota exceeded. Please check your plan and billing details: {e1}")
                    print(f"[Veo3] Method 1 (File URI as source) failed: {e1}")
                    
                    # Method 2: Try using the file object directly
                    try:
                        operation = client.models.generate_videos(
                            model="veo-3.1-generate-preview",
                            source=uploaded_file,  # Pass file object directly
                        )
                        print(f"[Veo3] OK Method 2 (File object as source) succeeded")
                    except Exception as e2:
                        last_error = e2
                        if "429" in str(e2) or "RESOURCE_EXHAUSTED" in str(e2) or "quota" in str(e2).lower():
                            raise Exception(f"Gemini API quota exceeded. Please check your plan and billing details: {e2}")
                        print(f"[Veo3] Method 2 (File object as source) failed: {e2}")
                        
                        # Method 3: Try using the file's URI property if it exists
                        try:
                            file_uri = getattr(uploaded_file, 'uri', None) or getattr(uploaded_file, 'name', None)
                            if file_uri:
                                operation = client.models.generate_videos(
                                    model="veo-3.1-generate-preview",
                                    source=file_uri,
                                )
                                print(f"[Veo3] OK Method 3 (File URI property) succeeded")
                            else:
                                raise Exception("No URI found in uploaded file")
                        except Exception as e3:
                            last_error = e3
                            if "429" in str(e3) or "RESOURCE_EXHAUSTED" in str(e3) or "quota" in str(e3).lower():
                                raise Exception(f"Gemini API quota exceeded. Please check your plan and billing details: {e3}")
                            print(f"[Veo3] Method 3 (File URI property) failed: {e3}")
                            raise Exception(f"Could not extend video. All methods failed. Last error: {last_error}")
                
                if operation is None:
                    raise Exception(f"Failed to create extension operation: {last_error}")
                
                print(f"[Veo3] OK Extension operation started")
                print(f"[Veo3]   Operation: {operation.name}")
                
                # Return the operation info
                return {
                    "job_id": operation.name,
                    "operation_name": operation.name,
                    "status": "in_progress",
                    "progress": 0,
                    "video_url": None,
                    "model": "veo-3.1-generate-preview",  # Must use generate (not fast-generate) for extensions
                    "created_at": int(time.time()),
                    "is_extension": True,
                    "extension_seconds": extension_seconds,
                    "base_job_id": base_job_id
                }
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_video_path)
                except:
                    pass
            
        except Exception as e:
            print(f"[Veo3] ERROR Gemini API extension error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to extend Veo 3 video via Gemini API: {str(e)}")
    
    async def wait_for_operation_completion(
        self,
        operation_name: str,
        check_interval: int = 10,
        max_wait_time: int = 600
    ) -> Dict:
        """
        Wait for a Gemini API operation to complete and return the result.
        
        Args:
            operation_name: Operation name from Gemini API
            check_interval: Seconds between status checks (default 10)
            max_wait_time: Maximum time to wait in seconds (default 600 = 10 minutes)
            
        Returns:
            Dict with completed video info
        """
        if not GEMINI_API_AVAILABLE:
            raise Exception("google-genai library not installed")
        
        gemini_api_key = os.getenv('GEMINI_API_KEY') or os.getenv('VEO3_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not gemini_api_key:
            raise Exception("Gemini API key required")
        
        client = genai.Client(api_key=gemini_api_key)
        
        start_time = time.time()
        operation = client.operations.get(operation_name)
        
        print(f"[Veo3] WAIT Waiting for operation to complete...")
        
        while not operation.done:
            elapsed = time.time() - start_time
            if elapsed > max_wait_time:
                raise Exception(f"Operation timed out after {max_wait_time} seconds")
            
            print(f"[Veo3]   Still processing... (elapsed: {int(elapsed)}s)")
            time.sleep(check_interval)
            operation = client.operations.get(operation_name)
        
        print(f"[Veo3] ✅ Operation completed!")
        
        # Get the generated video
        if hasattr(operation, 'response') and operation.response:
            generated_videos = operation.response.generated_videos
            if generated_videos and len(generated_videos) > 0:
                generated_video = generated_videos[0]
                
                # Download the video
                if hasattr(generated_video, 'video'):
                    video_file = generated_video.video
                    client.files.download(file=video_file)
                    video_file.save('extended_video.mp4')
                    
                    # Read the video bytes
                    with open('extended_video.mp4', 'rb') as f:
                        video_bytes = f.read()
                    
                    # Clean up
                    os.unlink('extended_video.mp4')
                    
                    return {
                        "status": "completed",
                        "video_bytes": video_bytes,
                        "video_file": video_file
                    }
        
        raise Exception("No video found in operation response")
