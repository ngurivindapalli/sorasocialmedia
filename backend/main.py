from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
import json
import re
import httpx
from dotenv import load_dotenv

from services.instagram_api import InstagramAPIService
from services.openai_service import OpenAIService
from services.linkedin_api import LinkedInAPIService
from services.linkedin_scraper import LinkedInPostScraper
from services.oauth_service import OAuthService
from services.posting_service import PostingService
from services.email_service import EmailService
from services.browser_automation import BrowserAutomationService
from services.veo3_service import Veo3Service
from services.image_generation_service import ImageGenerationService
from services.video_composition_service import VideoCompositionService
from services.document_service import DocumentService
from services.user_context_service import UserContextService
from services.memory_service import MemoryService  # Unified service (S3 + Mem0)
from services.bedrock_service import BedrockService
from services.notion_service import NotionService
from services.google_drive_service import GoogleDriveService
from services.jira_service import JiraService
# Hyperspell removed - using MemoryService (S3 + Mem0) directly
from utils.post_memory_helper import save_post_to_memory, is_first_post, get_post_performance_context, find_existing_post_with_image
from utils.hyperspell_helper import get_memory_context
from utils.veo_helper import wait_for_video_completion_with_extensions
from utils.user_id_helper import normalize_user_id, get_user_id_from_request
from services.web_research_service import WebResearchService
from services.seo_aeo_service import SEOAEOService
from models.schemas import (
    MarketingPostRequest,
    MarketingPostResponse,
    MarketingPostSuggestion,
    MarketingPostSuggestionsResponse,
    AigisMarketingRequest,
    AigisMarketingResponse,
    AigisMarketingPostRequest,
    AigisMarketingSuggestionsRequest,
    AigisMarketingSuggestionsResponse,
    VideoAnalysisRequest, VideoAnalysisResponse, ScrapedVideo, VideoResult,
    UserSignupRequest, UserLoginRequest, SocialMediaConnectionResponse,
    PostVideoRequest, PostVideoResponse,
    LinkedInCompanyPostRequest, LinkedInCompanyPostResponse,
    ManualInstagramPostRequest, ManualInstagramPostResponse,
    Veo3GenerateRequest, Veo3GenerateResponse, Veo3StatusResponse,
    Veo3ExtendRequest, Veo3ExtendResponse,
    Veo3GenerateWithContextRequest, Veo3GenerateWithContextResponse,
    ImageGenerateRequest, ImageGenerateResponse,
    SmartVideoCompositionRequest, SmartVideoCompositionResponse,
    InformationalVideoRequest, InformationalVideoResponse,
    DocumentVideoRequest, DocumentVideoResponse,
    VideoOptionsRequest, VideoOptionsResponse, ScriptApprovalRequest,
    UserPreferencesRequest, UserPreferencesResponse, UserContextResponse,
    FindCompetitorsRequest,
    IntegrationConnectionResponse,
    NotionPageResponse,
    GoogleDriveFileResponse,
    JiraIssueResponse,
    ImportContentRequest,
    SEOAEOAnalysisRequest,
    SEOAEOAnalysisResponse,
    SEOAEOStatusRequest,
    SEOAEOStatusResponse,
    SEOAEOSummary,
    PromptResult,
    TopicMentionStats,
    CompetitorStats,
    SourceStats,
    SourceCitation
)
from database import init_db, get_db, User, SocialMediaConnection, PostHistory, IntegrationConnection
from auth_utils import get_password_hash, verify_password, create_access_token, get_current_user
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import uuid

# Load environment variables (try .env file first, then system environment)
# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')

# Helper function to save image to local file
def save_image_to_file(image_base64: str, topic: str, user_id: str = "default") -> str:
    """
    Save base64 image to local file and return the URL path
    
    Args:
        image_base64: Base64 encoded image data
        topic: Topic name for filename
        user_id: User ID for organizing files
    
    Returns:
        URL path to access the image (e.g., "/static/images/marketing-posts/topic_hash.png")
    """
    import base64
    import hashlib
    
    # Create a hash from topic and user_id for consistent filenames
    filename_base = hashlib.md5(f"{user_id}_{topic}".encode()).hexdigest()[:12]
    safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    filename = f"{safe_topic}_{filename_base}.png"
    
    # Ensure directory exists
    images_dir = os.path.join(BASE_DIR, "static", "images", "marketing-posts")
    os.makedirs(images_dir, exist_makok=True)
    
    # Save image file
    file_path = os.path.join(images_dir, filename)
    image_data = base64.b64decode(image_base64)
    with open(file_path, 'wb') as f:
        f.write(image_data)
    
    # Return URL path (relative to API base)
    image_url = f"/static/images/marketing-posts/{filename}"
    print(f"[API] ✓ Image saved to: {file_path}")
    print(f"[API] ✓ Image URL: {image_url}")
    return image_url

def get_image_file_path(topic: str, user_id: str = "default") -> Optional[str]:
    """
    Check if an image file already exists for the given topic/user_id
    
    Args:
        topic: Topic name
        user_id: User ID
    
    Returns:
        URL path if file exists, None otherwise
    """
    import hashlib
    
    # Create the same hash as save_image_to_file
    filename_base = hashlib.md5(f"{user_id}_{topic}".encode()).hexdigest()[:12]
    safe_topic = "".join(c for c in topic[:30] if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
    filename = f"{safe_topic}_{filename_base}.png"
    
    file_path = os.path.join(BASE_DIR, "static", "images", "marketing-posts", filename)
    if os.path.exists(file_path):
        image_url = f"/static/images/marketing-posts/{filename}"
        print(f"[API] ✓ Found existing image file: {image_url}")
        return image_url
    return None
print(f"[DEBUG] Loading .env from: {env_path}")
print(f"[DEBUG] .env file exists: {os.path.exists(env_path)}")

# Helper function to parse quoted environment variables
def parse_env_value(value: str) -> str:
    """Parse environment variable value, removing quotes if present"""
    if not value:
        return value
    value = value.strip()
    # Remove quotes if present (single or double)
    if (value.startswith('"') and value.endswith('"')) or \
       (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]
    return value

# Try multiple methods to load the .env file
load_dotenv(env_path, override=True)

# Always manually parse Instagram credentials to ensure quoted passwords work
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if os.path.exists(env_path):
    print("[DEBUG] dotenv didn't load key, trying manual parse...")
    try:
        with open(env_path, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles BOM
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                
                # Parse Instagram credentials with quotes support
                if key == 'INSTAGRAM_USERNAME':
                    parsed_value = parse_env_value(value)
                    if parsed_value:
                        os.environ['INSTAGRAM_USERNAME'] = parsed_value
                        print(f"[DEBUG] Manually loaded INSTAGRAM_USERNAME")
                elif key == 'INSTAGRAM_PASSWORD':
                    parsed_value = parse_env_value(value)
                    if parsed_value:
                        os.environ['INSTAGRAM_PASSWORD'] = parsed_value
                        print(f"[DEBUG] Manually loaded INSTAGRAM_PASSWORD (length: {len(parsed_value)})")
                elif key == 'OPENAI_API_KEY' and not OPENAI_API_KEY:
                    # Only manually load OPENAI_API_KEY if dotenv didn't load it
                    parsed_value = parse_env_value(value)
                    if parsed_value:
                        OPENAI_API_KEY = parsed_value
                        os.environ['OPENAI_API_KEY'] = parsed_value
                        print(f"[DEBUG] Manually loaded OPENAI_API_KEY (length: {len(parsed_value)})")
    except Exception as e:
        print(f"[DEBUG] Manual parse failed: {e}")

print(f"[DEBUG] After loading, OPENAI_API_KEY present: {bool(OPENAI_API_KEY)}")

# Get API keys from environment variables
# OPENAI_API_KEY may have been set manually above, so check os.environ first
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
# Get Sora model preference (default: "sora-2", options: "sora-2", "sora-2-pro", "sora-4" if available)
SORA_MODEL_DEFAULT = os.getenv('SORA_MODEL', 'sora-2')
SORA_MODEL_PRO = os.getenv('SORA_MODEL_PRO', 'sora-2-pro')  # For high-quality videos

if not OPENAI_API_KEY:
    print("[WARNING] OPENAI_API_KEY not set. Video generation features will be disabled.")
    print("[INFO] OAuth and posting features will still work.")
else:
    print(f"[DEBUG] Using OpenAI API key: {OPENAI_API_KEY[:20]}...{OPENAI_API_KEY[-4:]}")

if ANTHROPIC_API_KEY:
    print(f"[DEBUG] Anthropic API key found: {ANTHROPIC_API_KEY[:20]}...{ANTHROPIC_API_KEY[-4:]}")
else:
    print("[DEBUG] ANTHROPIC_API_KEY not found. Claude features will be disabled.")

# Memory service uses S3 + Mem0 (no API key needed - uses AWS credentials and Mem0 API key)

app = FastAPI(title="Instagram Video to Sora Script Generator")

# Add exception handler for validation errors to provide better error messages
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors with detailed logging"""
    print(f"[API] Validation error on {request.method} {request.url}")
    print(f"[API] Validation errors: {exc.errors()}")
    
    # Return detailed validation errors
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": str(exc.body) if hasattr(exc, 'body') else None
        }
    )

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:5173",
        "https://web-production-2b02d.up.railway.app",
        "https://*.vercel.app",
        "https://aigismarketing.com",
        "https://www.aigismarketing.com",
        "*"  # Allow all origins in production (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Create static images directory if it doesn't exist
STATIC_IMAGES_DIR = os.path.join(BASE_DIR, "static", "images", "marketing-posts")
os.makedirs(STATIC_IMAGES_DIR, exist_ok=True)
print(f"[API] Static images directory: {STATIC_IMAGES_DIR}")

# Mount static files for serving images
app.mount("/static/images", StaticFiles(directory=STATIC_IMAGES_DIR), name="static_images")

# Initialize services
instagram_service = InstagramAPIService()
linkedin_service = LinkedInAPIService()
linkedin_scraper = LinkedInPostScraper()
oauth_service = OAuthService()
posting_service = PostingService()
email_service = EmailService()
browser_automation_service = BrowserAutomationService()
# VIDEO GENERATION DISABLED - Too expensive, focusing on images only
# veo3_service = Veo3Service()
class DisabledVeo3Service:
    """Placeholder for disabled Veo3 service"""
    project_id = None
    _extension_cache = {}
    async def generate_video(self, *args, **kwargs): raise Exception("Video generation is disabled")
    async def get_video_status(self, *args, **kwargs): raise Exception("Video generation is disabled")
    async def get_video_bytes(self, *args, **kwargs): raise Exception("Video generation is disabled")
    async def extend_video_gemini_api(self, *args, **kwargs): raise Exception("Video generation is disabled")
veo3_service = DisabledVeo3Service()
image_generation_service = ImageGenerationService()
video_composition_service = VideoCompositionService()
document_service = DocumentService()
# Initialize memory service (S3 + Mem0)
print("[API] Using MemoryService (S3 + Mem0)")
memory_service = MemoryService()
# Initialize integration services
notion_service = NotionService()
google_drive_service = GoogleDriveService()
jira_service = JiraService()
# Initialize user context service with Memory integration
user_context_service = UserContextService(hyperspell_service=memory_service)
# Check for fine-tuned model in environment
fine_tuned_model = os.getenv("OPENAI_FINE_TUNED_MODEL")
# Only initialize OpenAI service if API key is available
openai_service = None
if OPENAI_API_KEY:
    openai_service = OpenAIService(
        api_key=OPENAI_API_KEY, 
        anthropic_key=ANTHROPIC_API_KEY, 
        fine_tuned_model=fine_tuned_model,
        hyperspell_service=memory_service  # Pass Memory service for context integration (parameter name kept for compatibility)
    )
# Initialize SEO/AEO service
seo_aeo_service = None
if OPENAI_API_KEY:
    seo_aeo_service = SEOAEOService(openai_api_key=OPENAI_API_KEY)
    print("[API] SEO/AEO service initialized")
else:
    print("[INFO] OpenAI service not initialized - API key missing")

# Initialize Bedrock service for Claude (preferred for script generation)
bedrock_service = BedrockService()

# Initialize web research service AFTER openai_service (needs it for AI analysis)
web_research_service = WebResearchService(openai_service=openai_service if openai_service else None)

# Store OAuth states temporarily (in production, use Redis)
oauth_states = {}


@app.get("/")
async def root():
    return {
        "message": "VideoHook API - Social Media Video Generation Platform", 
        "status": "running",
        "features": {
            "oauth": "✓ Active - Connect social media accounts",
            "posting": "✓ Active - Post videos to social media",
            "email_notifications": "✓ Active - Email notifications for posts",
            "video_generation": "✓ Active" if openai_service else "⚠ Disabled - OPENAI_API_KEY not set",
            "structured_outputs": "✓ Active" if openai_service else "⚠ Disabled",
            "vision_api": "✓ Active" if openai_service else "⚠ Disabled",
            "veo3": "⛔ Disabled - Video generation turned off to reduce costs",
            "image_generation": "✓ Active" if image_generation_service.project_id else "⚠ Disabled - GOOGLE_CLOUD_PROJECT_ID not set",
            "gemini_3_pro_image": "✓ Active" if image_generation_service.project_id else "⚠ Disabled - GOOGLE_CLOUD_PROJECT_ID not set (uses Vertex AI)",
            "smart_composition": "✓ Active" if video_composition_service.openai_client else "⚠ Disabled",
            "memory": "✓ Active" if memory_service.is_available() else "⚠ Disabled - Check S3 and Mem0 configuration",
        },
        "model": openai_service.model if openai_service else "Not configured"
    }


@app.post("/api/analyze", response_model=VideoAnalysisResponse)
async def analyze_videos(request: VideoAnalysisRequest):
    """
    Scrape videos from Instagram, transcribe them, and generate Sora scripts with OpenAI Build Hours features.
    """
    try:
        print(f"[API] ===== ANALYZE REQUEST RECEIVED =====")
        print(f"[API] Username: {request.username}")
        print(f"[API] Video limit: {request.video_limit}")
        print(f"[API] Video seconds: {request.video_seconds}")
        print(f"[API] LLM provider: {request.llm_provider}")
        print(f"[API] Video model: {request.video_model}")
        print(f"[API] Veo 3 configured: {bool(veo3_service.project_id)}")
        print(f"[API] ====================================")
        
        # Check if OpenAI service is available (required for video analysis)
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required for video analysis. Please set OPENAI_API_KEY in your backend/.env file."
            )
        
        # Step 1: Extract profile context for all account types (business, personal, creator, etc.)
        print(f"[API] 📋 Extracting profile context for: @{request.username}")
        profile_context = await instagram_service.get_profile_context(request.username)
        
        # Step 2: Get document context if provided
        document_context = ""
        if request.document_ids and len(request.document_ids) > 0:
            print(f"[API] 📄 Retrieving context from {len(request.document_ids)} document(s)...")
            try:
                document_context = document_service.get_documents_context(request.document_ids)
                print(f"[API] ✓ Document context retrieved ({len(document_context)} characters)")
            except Exception as doc_error:
                print(f"[API] ⚠️ Error retrieving document context: {doc_error}")
                document_context = ""
        
        # Step 3: Research profile/page context using GPT-4 (works for all account types)
        print(f"[API] 🔍 Researching profile context (works for all account types)...")
        page_context = await openai_service.research_profile_context(profile_context, document_context)
        print(f"[API] ✓ Profile context researched: {len(page_context)} characters")
        
        # Step 3.5: Get Memory (S3 + Mem0) context for enhanced personalization (reusable helper)
        memory_query = f"{profile_context.get('biography', '')[:100]} {document_context[:100] if document_context else ''}".strip()
        if memory_query:
            memory_context = await get_memory_context(
                memory_service=memory_service,
                query=memory_query,
                user_email=None  # Can add user auth later
            )
            if memory_context:
                # Enhance page_context with Memory
                page_context = f"""{memory_context}

{page_context}"""
        
        # Step 3: Scrape videos from Instagram
        print(f"[API] Analyzing Instagram user: @{request.username}")
        videos = await instagram_service.get_user_videos(
            username=request.username,
            limit=request.video_limit or 3
        )
        
        if not videos:
            raise HTTPException(status_code=404, detail=f"No videos found for @{request.username}")
        
        print(f"[API] Found {len(videos)} video(s)")
        
        # Convert to ScrapedVideo objects for response
        scraped_videos = [ScrapedVideo(**v) for v in videos]
        
        # Step 5: Process each video with Build Hours features (analysis phase)
        print(f"[API] 🔄 Phase 1: Analyzing videos (transcription + script generation with context)...")
        analyzed_results = []
        video_data_for_sora = []  # Store data for parallel Sora generation
        
        for video in videos:
            try:
                print(f"[API] Processing video: {video['id']}")
                
                # Download video
                video_path = await instagram_service.download_video(video['video_url'], video['id'])
                
                # Check if OpenAI service is available before using it
                if not openai_service:
                    raise HTTPException(
                        status_code=400, 
                        detail="OpenAI API key is required for video analysis. Please set OPENAI_API_KEY in your .env file."
                    )
                
                # BUILD HOURS FEATURE: Vision API - Analyze thumbnail for visual context
                thumbnail_analysis = None
                try:
                    if video.get('thumbnail_url'):
                        print(f"[API] 👁️ Analyzing thumbnail with Vision API (Build Hours)...")
                        thumbnail_analysis = await openai_service.analyze_thumbnail_with_vision(
                            video['thumbnail_url']
                        )
                        print(f"[API] ✓ Vision analysis complete: {thumbnail_analysis.style_assessment}")
                except Exception as vision_error:
                    print(f"[API] Vision API skipped (non-critical): {vision_error}")
                
                # Transcribe with Whisper
                print(f"[API] Transcribing video...")
                transcription = await openai_service.transcribe_video(video_path)
                
                # Get user_id for Memory (S3 + Mem0) enhancement (if authenticated)
                user_id_for_memory = None
                try:
                    # TODO: Get actual user_id from authentication token when available
                    # For now, we'll enhance with Memory (S3 + Mem0) if available
                    user_id_for_memory = "default_user"  # Will be replaced with actual user_id
                except:
                    pass
                
                # Generate regular Sora script (always works as fallback) with page context + Memory (S3 + Mem0)
                llm_provider = request.llm_provider or "openai"
                print(f"[API] Generating Sora script with page context + Hyperspell memory using {llm_provider}...")
                sora_script = await openai_service.generate_sora_script(
                    transcription=transcription,
                    video_metadata={
                        'views': video['views'],
                        'likes': video['likes'],
                        'text': video['text'],
                        'user_id': user_id_for_memory
                    },
                    target_duration=request.video_seconds or 8,
                    page_context=page_context,  # Already enhanced with Hyperspell if available
                    llm_provider=llm_provider,
                    user_id=user_id_for_memory
                )
                
                # Try to generate structured Sora script (OpenAI Build Hours) with page context + Hyperspell
                structured_sora = None
                try:
                    print(f"[API] 📐 Generating structured Sora script with page context + Hyperspell memory (Build Hours: Structured Outputs)...")
                    structured_sora = await openai_service.generate_structured_sora_script(
                        transcription=transcription,
                        video_metadata={
                            'views': video['views'],
                            'likes': video['likes'],
                            'text': video['text'],
                            'duration': video.get('duration', 0),
                            'user_id': user_id_for_memory
                        },
                        thumbnail_analysis=thumbnail_analysis,  # Include Vision API data
                        target_duration=request.video_seconds or 8,  # Pass user's desired duration
                        page_context=page_context,  # Already enhanced with Hyperspell if available
                        user_id=user_id_for_memory  # For additional Hyperspell queries
                    )
                    print(f"[API] ✓ Structured output generated successfully")
                except Exception as struct_error:
                    print(f"[API] Structured output failed (non-critical): {struct_error}")
                    import traceback
                    traceback.print_exc()
                
                # Store video data for parallel Sora generation
                video_data_for_sora.append({
                    'video': video,
                    'transcription': transcription,
                    'sora_script': sora_script,
                    'structured_sora': structured_sora,
                    'thumbnail_analysis': thumbnail_analysis,
                    'video_path': video_path
                })
                
                print(f"[API] ✓ Video analyzed: {video['id']}")
                
            except Exception as video_error:
                print(f"[API] Failed to process video {video['id']}: {video_error}")
                import traceback
                traceback.print_exc()
        
        # Step 3: Generate Sora videos in PARALLEL for speed
        print(f"[API] 🚀 Phase 2: Generating {len(video_data_for_sora)} Sora videos in parallel...")
        
        async def generate_single_sora(video_data):
            """Helper function to generate a single Sora video"""
            try:
                video = video_data['video']
                structured_sora = video_data['structured_sora']
                sora_script = video_data['sora_script']
                
                # Use structured prompt if available, otherwise use regular script
                video_prompt = structured_sora.full_prompt if structured_sora else sora_script
                
                # Determine which video model to use
                video_model = request.video_model or "sora-2"
                user_seconds = request.video_seconds or 8
                
                print(f"[API] 🎬 Video model selection:")
                print(f"[API]   Request video_model: {request.video_model}")
                print(f"[API]   Selected video_model: {video_model}")
                print(f"[API]   Veo 3 service configured: {bool(veo3_service.project_id)}")
                print(f"[API]   Generating video for {video['id']} using {video_model}...")
                
                if video_model == "veo-3" or video_model == "veo3":
                    # Use Veo 3 for video generation
                    print(f"[API] 🎥 Attempting Veo 3 generation...")
                    if not veo3_service.project_id:
                        print(f"[API] ⚠️ Veo 3 not configured, falling back to Sora 2")
                        print(f"[API]   To use Veo 3, set GOOGLE_CLOUD_PROJECT_ID in backend/.env file")
                        video_model = "sora-2"
                    else:
                        # Validate Veo 3 duration constraints (4-60 seconds)
                        veo3_seconds = max(4, min(60, user_seconds))  # Clamp to 4-60
                        if veo3_seconds != user_seconds:
                            print(f"[API] ⚠️ Veo 3 duration adjusted from {user_seconds}s to {veo3_seconds}s (must be 4-60 seconds)")
                        
                        # Guardrail: Warn if duration is very long (may take significant time)
                        if veo3_seconds > 30:
                            print(f"[API] ⚠️ Veo 3 generation with {veo3_seconds}s duration may take 3-5 minutes")
                        
                        try:
                            print(f"[API] 🎥 Calling Veo 3 service.generate_video()...")
                            print(f"[API]   Duration: {veo3_seconds}s (Veo 3 supports 4-60 seconds)")
                            veo3_result = await veo3_service.generate_video(
                                prompt=video_prompt,
                                duration=veo3_seconds,
                                resolution="1280x720"
                            )
                            print(f"[API] ✅ Veo 3 generation successful! Job ID: {veo3_result.get('job_id')}")
                            from models.schemas import SoraVideoJob
                            # Use the actual model ID that was used (e.g., veo-3.1-generate-001)
                            model_name = veo3_result.get("model", "veo-3")
                            return SoraVideoJob(
                                job_id=veo3_result.get("job_id"),
                                status=veo3_result.get("status", "running"),
                                progress=veo3_result.get("progress", 0),
                                model=model_name,
                                created_at=veo3_result.get("created_at", 0)
                            )
                        except Exception as veo3_error:
                            print(f"[API] ❌ Veo 3 generation failed, falling back to Sora 2")
                            print(f"[API]   Error details: {veo3_error}")
                            import traceback
                            traceback.print_exc()
                            video_model = "sora-2"
                
                # Use Sora 2 (default or fallback)
                if video_model == "sora-2":
                    # Clamp video_seconds to valid range (5-16) and closest valid Sora value
                    user_seconds = request.video_seconds or 8
                    user_seconds = max(5, min(16, user_seconds))  # Clamp to 5-16
                    # Round to nearest valid Sora value (4, 8, 12)
                    if user_seconds <= 6:
                        sora_seconds = 4
                    elif user_seconds <= 10:
                        sora_seconds = 8
                    else:
                        sora_seconds = 12
                    
                    print(f"[API] 🎬 Using Sora 2 for video generation...")
                    print(f"[API]   Duration: {sora_seconds}s (Sora 2 supports 4, 8, or 12 seconds)")
                    sora_job_info = await openai_service.generate_sora_video(
                        prompt=video_prompt,
                        model=SORA_MODEL_DEFAULT,  # Configurable via SORA_MODEL env var (default: "sora-2")
                        size="1280x720",
                        seconds=sora_seconds
                    )
                    
                    from models.schemas import SoraVideoJob
                    return SoraVideoJob(
                        job_id=sora_job_info["job_id"],
                        status=sora_job_info["status"],
                        progress=sora_job_info.get("progress"),
                        model=sora_job_info["model"],
                        created_at=sora_job_info["created_at"]
                    )
                else:
                    # This should not happen, but handle it gracefully
                    print(f"[API] ⚠️ Unexpected video_model value: {video_model}, falling back to Sora 2")
                    sora_job_info = await openai_service.generate_sora_video(
                        prompt=video_prompt,
                        model=SORA_MODEL_DEFAULT,
                        size="1280x720",
                        seconds=sora_seconds
                    )
                    from models.schemas import SoraVideoJob
                    return SoraVideoJob(
                        job_id=sora_job_info["job_id"],
                        status=sora_job_info["status"],
                        progress=sora_job_info.get("progress"),
                        model=sora_job_info["model"],
                        created_at=sora_job_info["created_at"]
                    )
            except Exception as e:
                print(f"[API] Sora generation failed for {video['id']}: {e}")
                return None
        
        # Generate all Sora videos concurrently if we have <= 3 videos
        sora_jobs = []
        if request.video_limit and request.video_limit <= 3 and video_data_for_sora:
            sora_jobs = await asyncio.gather(*[
                generate_single_sora(vd) for vd in video_data_for_sora
            ])
        else:
            sora_jobs = [None] * len(video_data_for_sora)
        
        # Step 4: Combine results
        for i, video_data in enumerate(video_data_for_sora):
            video = video_data['video']
            analyzed_results.append(VideoResult(
                video_id=video['id'],
                post_url=video['post_url'],
                views=video['views'],
                likes=video['likes'],
                original_text=video['text'],
                transcription=video_data['transcription'],
                sora_script=video_data['sora_script'],
                structured_sora_script=video_data['structured_sora'],
                thumbnail_analysis=video_data['thumbnail_analysis'],
                sora_video_job=sora_jobs[i]  # May be None if generation failed or skipped
            ))
            
            # Cleanup
            video_path = video_data['video_path']
            if os.path.exists(video_path):
                os.remove(video_path)
        
        print(f"[API] ✅ All videos processed successfully!")
        
        return VideoAnalysisResponse(
            username=request.username,
            page_context=page_context,
            scraped_videos=scraped_videos,
            analyzed_videos=analyzed_results
        )
        
    except Exception as e:
        print(f"[API] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/multi")
async def analyze_multi_users(request: dict):
    """
    Analyze videos from multiple Instagram users and create a combined Sora script.
    Blends the best performing content styles from 2-5 creators.
    """
    from models.schemas import MultiUserAnalysisRequest, CombinedVideoResult
    
    try:
        # Validate request
        multi_request = MultiUserAnalysisRequest(**request)
        
        print(f"[API] Multi-user analysis: {', '.join(['@' + u for u in multi_request.usernames])}")
        
        all_videos = []
        all_results = []
        user_contexts = {}  # Store profile context for each user
        
        # Check if OpenAI service is available
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required for video analysis. Please set OPENAI_API_KEY in your .env file."
            )
        
        # Step 1: Extract profile context for each user
        print(f"[API] 📋 Extracting profile contexts for all users...")
        for username in multi_request.usernames:
            try:
                profile_context = await instagram_service.get_profile_context(username)
                page_context = await openai_service.research_profile_context(profile_context)
                user_contexts[username] = page_context
                print(f"[API] ✓ Context extracted for @{username}: {len(page_context)} characters")
            except Exception as context_error:
                print(f"[API] ⚠️ Could not extract context for @{username}: {context_error}")
                user_contexts[username] = None
        
        # Step 2: Scrape videos from each user
        for username in multi_request.usernames:
            try:
                print(f"[API] Scraping @{username}...")
                videos = await instagram_service.get_user_videos(
                    username=username,
                    limit=multi_request.videos_per_user
                )
                
                if videos:
                    # Add username to each video for tracking
                    for v in videos:
                        v['source_username'] = username
                    all_videos.extend(videos)
                    print(f"[API] Found {len(videos)} videos from @{username}")
                else:
                    print(f"[API] No videos found for @{username}")
                    
            except Exception as user_error:
                print(f"[API] Error scraping @{username}: {user_error}")
                continue
        
        if not all_videos:
            raise HTTPException(status_code=404, detail="No videos found from any of the specified users")
        
        print(f"[API] Total videos collected: {len(all_videos)}")
        
        # Step 3: Process each video
        for video in all_videos:
            try:
                video_path = await instagram_service.download_video(video['video_url'], video['id'])
                
                # Vision API analysis
                thumbnail_analysis = None
                if video.get('thumbnail_url'):
                    try:
                        thumbnail_analysis = await openai_service.analyze_thumbnail_with_vision(video['thumbnail_url'])
                    except Exception as vision_error:
                        print(f"[API] Vision API skipped: {vision_error}")
                
                # Transcribe
                transcription = await openai_service.transcribe_video(video_path)
                
                # Get context for this video's source user
                source_username = video.get('source_username', '')
                page_context = user_contexts.get(source_username)
                
                # Generate regular Sora script with context
                llm_provider = multi_request.llm_provider or "openai"
                sora_script = await openai_service.generate_sora_script(
                    transcription=transcription,
                    video_metadata={
                        "views": video['views'],
                        "likes": video['likes'],
                        "original_text": video['text'],
                        "username": source_username
                    },
                    target_duration=multi_request.video_seconds or 12,
                    page_context=page_context,
                    llm_provider=llm_provider
                )
                
                # Try structured output with context
                structured_script = None
                try:
                    structured_script = await openai_service.generate_structured_sora_script(
                        transcription=transcription,
                        video_metadata={
                            "views": video['views'],
                            "likes": video['likes'],
                            "original_text": video['text'],
                            "username": source_username
                        },
                        thumbnail_analysis=thumbnail_analysis,
                        target_duration=multi_request.video_seconds or 12,
                        page_context=page_context
                    )
                except Exception as structured_error:
                    print(f"[API] Structured output skipped: {structured_error}")
                
                all_results.append(VideoResult(
                    video_id=video['id'],
                    post_url=video['post_url'],
                    views=video['views'],
                    likes=video['likes'],
                    original_text=video['text'],
                    transcription=transcription,
                    sora_script=sora_script,
                    structured_sora_script=structured_script,
                    thumbnail_analysis=thumbnail_analysis
                ))
                
                if os.path.exists(video_path):
                    os.remove(video_path)
                    
            except Exception as video_error:
                print(f"[API] Error processing video: {video_error}")
                continue
        
        if not all_results:
            raise HTTPException(status_code=500, detail="Failed to process any videos")
        
        # Step 3: Generate combined script
        print(f"[API] Creating combined script from {len(all_results)} videos...")
        # Create combined Sora script
        combined_script = await openai_service.create_combined_script(
            results=all_results,
            usernames=multi_request.usernames,
            combine_style=multi_request.combine_style,
            target_duration=multi_request.video_seconds or 12  # Pass user's desired duration
        )
        
        # Try to generate structured combined script
        combined_structured = None
        try:
            combined_structured = await openai_service.create_combined_structured_script(
                results=all_results,
                usernames=multi_request.usernames,
                combine_style=multi_request.combine_style,
                target_duration=multi_request.video_seconds or 12  # Pass user's desired duration
            )
        except Exception as e:
            print(f"[API] Combined structured output skipped: {e}")
        
        # Generate video for the combined script
        combined_sora_video_job = None
        try:
            combined_prompt = combined_structured.full_prompt if combined_structured else combined_script
            
            # Determine which video model to use for combined video
            video_model = multi_request.video_model or "sora-2-pro"
            user_seconds = multi_request.video_seconds or 12
            print(f"[API] 🎬 Generating combined video using {video_model}...")
            
            if video_model == "veo-3":
                # Use Veo 3 for combined video
                if not veo3_service.project_id:
                    print(f"[API] ⚠️ Veo 3 not configured, falling back to Sora 2 Pro")
                    video_model = "sora-2-pro"
                    # Fallback to Sora duration validation
                    user_seconds = max(5, min(16, user_seconds))
                    if user_seconds <= 6:
                        video_seconds = 4
                    elif user_seconds <= 10:
                        video_seconds = 8
                    else:
                        video_seconds = 12
                else:
                    # Validate Veo 3 duration constraints (4-60 seconds)
                    video_seconds = max(4, min(60, user_seconds))
                    if video_seconds != user_seconds:
                        print(f"[API] ⚠️ Veo 3 duration adjusted from {user_seconds}s to {video_seconds}s (must be 4-60 seconds)")
                    
                    # Guardrail: Warn if duration is very long
                    if video_seconds > 30:
                        print(f"[API] ⚠️ Veo 3 generation with {video_seconds}s duration may take 3-5 minutes")
                    
                    try:
                        print(f"[API] 🎥 Using Veo 3 for combined video (duration: {video_seconds}s)")
                        veo3_result = await veo3_service.generate_video(
                            prompt=combined_prompt,
                            duration=video_seconds,
                            resolution="1280x720"
                        )
                        from models.schemas import SoraVideoJob
                        combined_sora_video_job = SoraVideoJob(
                            job_id=veo3_result.get("job_id"),
                            status=veo3_result.get("status", "queued"),
                            progress=veo3_result.get("progress", 0),
                            model="veo-3",
                            created_at=veo3_result.get("created_at", 0)
                        )
                        print(f"[API] ✓ Combined Veo 3 video job created: {combined_sora_video_job.job_id}")
                        # Skip Sora generation below
                        video_model = None
                    except Exception as veo3_error:
                        print(f"[API] Veo 3 generation failed, falling back to Sora 2 Pro: {veo3_error}")
                        video_model = "sora-2-pro"
                        # Fallback to Sora duration validation
                        user_seconds = max(5, min(16, user_seconds))
                        if user_seconds <= 6:
                            video_seconds = 4
                        elif user_seconds <= 10:
                            video_seconds = 8
                        else:
                            video_seconds = 12
            
            # Use Sora 2 Pro for combined videos (default or fallback)
            if video_model and video_model.startswith("sora"):
                # Clamp to valid Sora duration if not already set
                if video_model == "sora-2-pro":
                    user_seconds = max(5, min(16, user_seconds))
                    if user_seconds <= 6:
                        video_seconds = 4
                    elif user_seconds <= 10:
                        video_seconds = 8
                    else:
                        video_seconds = 12
                print(f"[API] 🎬 Using Sora 2 Pro for combined video (duration: {video_seconds}s)")
                sora_job_info = await openai_service.generate_sora_video(
                    prompt=combined_prompt,
                    model=SORA_MODEL_PRO,  # Configurable via SORA_MODEL_PRO env var (default: "sora-2-pro")
                    size="1280x720",
                    seconds=video_seconds
                )
                
                from models.schemas import SoraVideoJob
                combined_sora_video_job = SoraVideoJob(
                    job_id=sora_job_info["job_id"],
                    status=sora_job_info["status"],
                    progress=sora_job_info.get("progress"),
                    model=sora_job_info["model"],
                    created_at=sora_job_info["created_at"]
                )
                print(f"[API] ✓ Combined Sora video job created: {combined_sora_video_job.job_id}")
            
        except Exception as sora_error:
            print(f"[API] Combined Sora video generation failed (non-critical): {sora_error}")
        
        return CombinedVideoResult(
            usernames=multi_request.usernames,
            total_videos_analyzed=len(all_results),
            individual_results=all_results,
            combined_sora_script=combined_script,
            combined_structured_script=combined_structured,
            fusion_notes=f"Combined {len(all_results)} top-performing videos using {multi_request.combine_style} style",
            combined_sora_video_job=combined_sora_video_job
        )
        
    except Exception as e:
        print(f"[API] Multi-user analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sora/generate")
async def generate_sora_video(request: dict):
    """
    Generate a video using Sora API from a text prompt.
    Returns job ID for status polling.
    """
    try:
        prompt = request.get("prompt")
        model = request.get("model", SORA_MODEL_DEFAULT)  # Configurable via SORA_MODEL env var or request param
        size = request.get("size", "1280x720")
        seconds = request.get("seconds", 8)
        
        # Validate seconds (Sora API only accepts 4, 8, or 12)
        if seconds not in [4, 8, 12]:
            seconds = 8  # Default to 8 if invalid
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        print(f"[API] Creating Sora video job...")
        job_info = await openai_service.generate_sora_video(
            prompt=prompt,
            model=model,
            size=size,
            seconds=seconds
        )
        
        return job_info
        
    except Exception as e:
        print(f"[API] Sora generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sora/status/{job_id}")
async def get_sora_status(job_id: str):
    """
    Check the status of a Sora video generation job.
    """
    try:
        status = await openai_service.get_sora_video_status(job_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sora/download/{job_id}")
async def download_sora_video(job_id: str):
    """
    Download a completed Sora video as MP4.
    """
    from fastapi.responses import StreamingResponse
    import io
    
    try:
        # First check if the video is completed
        status = await openai_service.get_sora_video_status(job_id)
        
        if status["status"] != "completed":
            raise HTTPException(
                status_code=400, 
                detail=f"Video not ready. Current status: {status['status']}"
            )
        
        # Download the video
        video_bytes = await openai_service.download_sora_video(job_id)
        
        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=sora_{job_id}.mp4"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "x_api": "configured" if os.getenv("X_BEARER_TOKEN") else "missing",
        "openai_api": "configured" if OPENAI_API_KEY else "missing",
        "fine_tuned_model": os.getenv("OPENAI_FINE_TUNED_MODEL") or "not configured",
        "sora_video_generation": "✓ Available"
    }


@app.post("/api/finetune/create")
async def create_fine_tune(training_data: dict):
    """
    Create a fine-tuning job with training examples.
    
    Example training_data format:
    {
        "examples": [
            {
                "transcription": "Welcome to our channel...",
                "metadata": {"views": 1000, "likes": 50},
                "ideal_sora_prompt": "A cinematic shot of..."
            }
        ]
    }
    """
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Convert training data to JSONL format for fine-tuning
        import json
        import tempfile
        
        training_file_content = []
        for example in training_data.get("examples", []):
            training_file_content.append({
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert video production director creating Sora AI prompts."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this transcription and metrics, create a Sora prompt:\n\nTranscription: {example['transcription']}\n\nMetrics: {example['metadata']}"
                    },
                    {
                        "role": "assistant",
                        "content": example['ideal_sora_prompt']
                    }
                ]
            })
        
        # Save to temporary JSONL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for item in training_file_content:
                f.write(json.dumps(item) + '\n')
            temp_file_path = f.name
        
        # Upload training file
        with open(temp_file_path, 'rb') as f:
            file_response = await client.files.create(
                file=f,
                purpose='fine-tune'
            )
        
        # Create fine-tuning job
        fine_tune_response = await client.fine_tuning.jobs.create(
            training_file=file_response.id,
            model="gpt-4o-mini-2024-07-18",  # Using gpt-4o-mini for fine-tuning (cheaper)
            suffix="sora-script-generator"
        )
        
        # Clean up temp file
        os.unlink(temp_file_path)
        
        return {
            "status": "success",
            "fine_tune_id": fine_tune_response.id,
            "model": fine_tune_response.model,
            "status": fine_tune_response.status,
            "message": "Fine-tuning job created! Check status with GET /api/finetune/status/{fine_tune_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finetune/status/{fine_tune_id}")
async def get_fine_tune_status(fine_tune_id: str):
    """Get the status of a fine-tuning job"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        job = await client.fine_tuning.jobs.retrieve(fine_tune_id)
        
        return {
            "id": job.id,
            "status": job.status,
            "model": job.model,
            "fine_tuned_model": job.fine_tuned_model,
            "created_at": job.created_at,
            "finished_at": job.finished_at,
            "trained_tokens": job.trained_tokens,
            "message": "Once status is 'succeeded', add the fine_tuned_model to your .env file as OPENAI_FINE_TUNED_MODEL"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/finetune/list")
async def list_fine_tunes():
    """List all fine-tuning jobs"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        jobs = await client.fine_tuning.jobs.list(limit=10)
        
        return {
            "fine_tune_jobs": [
                {
                    "id": job.id,
                    "status": job.status,
                    "model": job.model,
                    "fine_tuned_model": job.fine_tuned_model,
                    "created_at": job.created_at
                }
                for job in jobs.data
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/batch/create")
async def create_batch_job(batch_request: dict):
    """
    CREATE BATCH JOB (Build Hours Feature - 50% cost savings!)
    
    Process multiple videos in batch mode for 50% cheaper API costs.
    Takes 24 hours but ideal for analyzing large sets of videos.
    
    Example batch_request:
    {
        "usernames": ["user1", "user2", "user3"],
        "video_limit_per_user": 5
    }
    """
    try:
        from openai import AsyncOpenAI
        import json
        import tempfile
        
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Collect all video data to process
        all_requests = []
        request_id = 0
        
        for username in batch_request.get("usernames", []):
            # Scrape videos for this user
            videos = await instagram_service.get_user_videos(
                username=username,
                limit=batch_request.get("video_limit_per_user", 5)
            )
            
            for video in videos:
                # Download and transcribe
                video_path = await instagram_service.download_video(video['video_url'], video['id'])
                transcription = await openai_service.transcribe_video(video_path)
                
                # Create batch request for Sora script generation
                all_requests.append({
                    "custom_id": f"request-{request_id}",
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": openai_service.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert video production director creating Sora AI prompts."
                            },
                            {
                                "role": "user",
                                "content": f"""Based on this video transcription and metrics, create a detailed Sora AI prompt.

TRANSCRIPTION: {transcription}
METRICS: Views: {video['views']}, Likes: {video['likes']}
CAPTION: {video['text']}

Create a comprehensive Sora prompt."""
                            }
                        ],
                        "temperature": 0.7
                    }
                })
                request_id += 1
                
                # Cleanup
                if os.path.exists(video_path):
                    os.remove(video_path)
        
        # Save batch requests to JSONL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
            for req in all_requests:
                f.write(json.dumps(req) + '\n')
            batch_file_path = f.name
        
        # Upload batch file
        with open(batch_file_path, 'rb') as f:
            batch_file = await client.files.create(
                file=f,
                purpose='batch'
            )
        
        # Create batch job
        batch_job = await client.batches.create(
            input_file_id=batch_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "description": f"Batch Sora script generation for {len(batch_request.get('usernames', []))} Instagram users"
            }
        )
        
        # Cleanup
        os.unlink(batch_file_path)
        
        return {
            "status": "success",
            "batch_id": batch_job.id,
            "total_requests": len(all_requests),
            "status": batch_job.status,
            "cost_savings": "50% cheaper than standard API",
            "completion_time": "~24 hours",
            "message": "Batch job created! Check status with GET /api/batch/status/{batch_id}"
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/status/{batch_id}")
async def get_batch_status(batch_id: str):
    """Get status of a batch job (Build Hours Feature)"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        batch = await client.batches.retrieve(batch_id)
        
        return {
            "id": batch.id,
            "status": batch.status,
            "created_at": batch.created_at,
            "completed_at": batch.completed_at,
            "request_counts": {
                "total": batch.request_counts.total,
                "completed": batch.request_counts.completed,
                "failed": batch.request_counts.failed
            },
            "output_file_id": batch.output_file_id,
            "message": "Once status is 'completed', download results with GET /api/batch/results/{batch_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/results/{batch_id}")
async def get_batch_results(batch_id: str):
    """Download and parse batch job results (Build Hours Feature)"""
    try:
        from openai import AsyncOpenAI
        import json
        
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Get batch status
        batch = await client.batches.retrieve(batch_id)
        
        if batch.status != "completed":
            return {
                "status": batch.status,
                "message": f"Batch not ready yet. Current status: {batch.status}"
            }
        
        # Download results
        result_file_id = batch.output_file_id
        result_content = await client.files.content(result_file_id)
        
        # Parse results
        results = []
        for line in result_content.text.strip().split('\n'):
            result = json.loads(line)
            results.append({
                "request_id": result["custom_id"],
                "sora_script": result["response"]["body"]["choices"][0]["message"]["content"]
            })
        
        return {
            "batch_id": batch_id,
            "status": "completed",
            "total_results": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/batch/list")
async def list_batch_jobs():
    """List all batch jobs (Build Hours Feature)"""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        batches = await client.batches.list(limit=10)
        
        return {
            "batch_jobs": [
                {
                    "id": batch.id,
                    "status": batch.status,
                    "created_at": batch.created_at,
                    "request_counts": {
                        "total": batch.request_counts.total,
                        "completed": batch.request_counts.completed,
                        "failed": batch.request_counts.failed
                    }
                }
                for batch in batches.data
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/linkedin/chat")
async def linkedin_chat(request: dict):
    """
    AI chat interface for LinkedIn trending video generation.
    The AI scrapes LinkedIn trends and creates Sora videos based on conversation.
    """
    try:
        from openai import AsyncOpenAI
        
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        print(f"[LinkedIn Chat] User message: {message}")
        
        # Use GPT-4 to understand user intent
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Build conversation context
        chat_messages = [
            {
                "role": "system",
                "content": """You are an AI assistant that helps users create viral Sora videos based on LinkedIn trending topics.

Your capabilities:
1. Scrape LinkedIn trending topics by industry, keyword, or general trends
2. Analyze trending topics and explain why they're important
3. Generate compelling Sora video scripts based on trends
4. Create actual Sora videos from the scripts

When users ask about trends:
- Return trending topics with descriptions
- Explain engagement levels and sentiment
- Suggest which would make the best video

When users ask to create a video:
- Pick the most relevant trending topic
- Generate a cinematic Sora script (8-12 seconds)
- Include visual style, camera work, and mood

Always be helpful, creative, and business-focused."""
            }
        ]
        
        # Add conversation history (last 5 messages for context)
        for msg in conversation_history[-5:]:
            if msg.get("role") in ["user", "assistant"]:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current message
        chat_messages.append({"role": "user", "content": message})
        
        # Get AI response to determine intent
        intent_response = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=chat_messages,
            temperature=0.7,
            max_tokens=500
        )
        
        ai_message = intent_response.choices[0].message.content
        
        # Determine if we should scrape trends or generate video
        message_lower = message.lower()
        should_scrape = any(word in message_lower for word in ["trending", "trends", "what's", "show me", "find", "popular", "hot topics"])
        should_generate_video = any(word in message_lower for word in ["create", "make", "generate", "video", "sora"])
        
        response_data = {
            "message": ai_message,
            "trends": None,
            "sora_script": None,
            "sora_video_job": None,
            "awaiting_selection": False
        }
        
        # Check if user is selecting a topic (by number)
        is_selecting_topic = any(word in message_lower for word in ["1", "2", "3", "first", "second", "third", "number"])
        
        # Scrape LinkedIn trends and generate video
        if should_scrape or should_generate_video:
            # Extract topic/industry from message
            query = None
            for word in ["ai", "remote work", "sustainability", "cybersecurity", "leadership", "web3", "mental health", "creator"]:
                if word in message_lower:
                    query = word
                    break
            
            trends = await linkedin_service.scrape_trending_topics(query=query, limit=3)
            response_data["trends"] = trends
            
            # Auto-generate video for the first/best trend
            if trends and len(trends) > 0:
                selected_trend = trends[0]
                print(f"[LinkedIn Chat] Auto-generating Sora video for: {selected_trend['topic']}")
                
                # Research topic context using GPT-4 (only if OpenAI service is available)
                topic_context = None
                if openai_service:
                    topic_context = await openai_service.research_topic_context(selected_trend)
                else:
                    topic_context = f"Trending topic: {selected_trend.get('topic', '')} - {selected_trend.get('description', '')}"
                
                # Generate Sora script based on the trend with context
                script_prompt = f"""Create a compelling 8-second Sora video script for this LinkedIn trending topic:

TOPIC CONTEXT:
{topic_context}

TRENDING TOPIC DETAILS:
- Topic: {selected_trend['topic']}
- Description: {selected_trend['description']}
- Engagement: {selected_trend['engagement']}
- Hashtags: {', '.join(selected_trend['hashtags'])}
- Sentiment: {selected_trend['sentiment']}
- Industry: {selected_trend.get('industry', 'General Business')}

Create a professional, attention-grabbing video that would go viral on LinkedIn. The video should:
- Align with the topic context and industry understanding
- Use visual style appropriate for the professional audience
- Include dynamic camera movements
- Feature key scenes that resonate with LinkedIn professionals
- Maintain a professional, authoritative tone

Keep it concise and impactful for LinkedIn's professional audience."""

                script_response = await client.chat.completions.create(
                    model="gpt-4o-2024-08-06",
                    messages=[
                        {"role": "system", "content": "You are an expert video director creating Sora scripts for LinkedIn viral content."},
                        {"role": "user", "content": script_prompt}
                    ],
                    temperature=0.8,
                    max_tokens=400
                )
                
                sora_script = script_response.choices[0].message.content
                response_data["sora_script"] = sora_script
                
                # Generate actual Sora video
                print(f"[LinkedIn Chat] Creating Sora video...")
                try:
                    sora_job = await openai_service.generate_sora_video(
                        prompt=sora_script,
                        model=SORA_MODEL_DEFAULT,  # Configurable via SORA_MODEL env var
                        size="1280x720",
                        seconds=8
                    )
                    
                    from models.schemas import SoraVideoJob
                    response_data["sora_video_job"] = {
                        "job_id": sora_job["job_id"],
                        "status": sora_job["status"],
                        "progress": sora_job.get("progress"),
                        "model": sora_job["model"],
                        "created_at": sora_job["created_at"]
                    }
                    
                    # Update AI message to include video generation status
                    response_data["message"] = f"✨ Perfect! Generating a Sora video for: **{selected_trend['topic']}**\n\n🎬 Your video is being created and will be ready in 30-60 seconds..."
                    response_data["awaiting_selection"] = False
                    
                except Exception as video_error:
                    print(f"[LinkedIn Chat] Sora video generation failed: {video_error}")
                    response_data["message"] = f"✨ Script created for: **{selected_trend['topic']}**\n\n⚠️ Video generation encountered an issue. You can try again."
                    response_data["awaiting_selection"] = False
        
        return response_data
        
    except Exception as e:
        print(f"[LinkedIn Chat] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/general")
async def general_chat(request: dict):
    """
    General AI chat interface for answering questions about VideoHook platform.
    The AI can explain features, guide users, and provide information about the program.
    """
    try:
        from openai import AsyncOpenAI
        
        message = request.get("message", "")
        conversation_history = request.get("conversation_history", [])
        
        if not message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        print(f"[General Chat] User message: {message}")
        
        # Use GPT-4 to answer questions about the program
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Build conversation context with comprehensive program information
        chat_messages = [
            {
                "role": "system",
                "content": """You are an AI assistant for VideoHook, a platform that helps creators generate viral video hooks using AI.

VIDEOHOOK PLATFORM OVERVIEW:
VideoHook is an AI-powered video generation platform that transforms social media content into professional Sora videos.

KEY FEATURES:

1. INSTAGRAM VIDEO ANALYSIS:
   - Scrapes videos from any Instagram creator
   - Uses Whisper API for automatic transcription
   - GPT-4 Vision API analyzes video thumbnails for visual context
   - Generates Sora video scripts based on successful Instagram content
   - Supports single user analysis or multi-user style fusion
   - Creates new viral videos inspired by top-performing content

2. LINKEDIN TRENDING VIDEO GENERATOR:
   - Scrapes trending topics from LinkedIn
   - Analyzes engagement, sentiment, and hashtags
   - AI conversational interface to discuss trends
   - Generates professional Sora videos from trending topics
   - Perfect for B2B and professional content creators

3. SORA VIDEO GENERATION:
   - Uses OpenAI Sora API to create actual videos
   - Generates 5-16 second professional videos
   - Supports structured outputs for consistent quality
   - Batch processing available for multiple videos
   - Videos are ready to download and share

4. AI CAPABILITIES:
   - GPT-4 with Structured Outputs for reliable script generation
   - Whisper API for accurate video transcription
   - GPT-4 Vision for visual analysis
   - Fine-tuning support for custom models
   - Batch API for cost-effective processing

TECHNICAL STACK:
- Backend: Python FastAPI
- Frontend: React
- AI: OpenAI GPT-4, Whisper, Vision API, Sora
- Video Processing: Sora API

HOW IT WORKS:
1. User provides Instagram username or LinkedIn topic
2. Platform scrapes and analyzes content
3. AI generates optimized Sora video scripts
4. Sora creates professional videos
5. User downloads and shares videos

Your role is to:
- Explain how VideoHook works
- Guide users through features
- Answer questions about Instagram and LinkedIn tools
- Explain Sora video generation
- Help users understand the platform capabilities
- Be friendly, helpful, and informative

Always provide clear, concise answers and guide users to the right tools for their needs."""
            }
        ]
        
        # Add conversation history (last 10 messages for better context)
        for msg in conversation_history[-10:]:
            if msg.get("role") in ["user", "assistant"]:
                chat_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current message
        chat_messages.append({"role": "user", "content": message})
        
        # Get AI response
        response = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",
            messages=chat_messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        ai_message = response.choices[0].message.content
        
        return {
            "message": ai_message
        }
        
    except Exception as e:
        print(f"[General Chat] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/api/auth/signup", response_model=None)
async def signup(
    request: UserSignupRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new user account.
    """
    try:
        username = request.username
        email = request.email
        password = request.password
        
        print(f"[AUTH] Signup request received")
        print(f"[AUTH] Username: {username[:20] if username else 'None'}...")
        print(f"[AUTH] Email: {email[:30] if email else 'None'}...")
        print(f"[AUTH] Password length: {len(password) if password else 0} chars")
        
        # Validate password length FIRST (bcrypt limit is 72 bytes)
        # This must happen before any other processing
        if not password:
            raise HTTPException(status_code=400, detail="Password is required")
        
        # Check character length first (quick check)
        if len(password) > 72:
            raise HTTPException(
                status_code=400, 
                detail="Password is too long. Maximum length is 72 characters. Please use a shorter password."
            )
        
        # Check byte length (more accurate for bcrypt)
        password_bytes = password.encode('utf-8')
        print(f"[AUTH] Password byte length: {len(password_bytes)} bytes")
        
        if len(password_bytes) > 72:
            raise HTTPException(
                status_code=400, 
                detail=f"Password is too long. Maximum byte length is 72 bytes, but your password is {len(password_bytes)} bytes. Please use a shorter password."
            )
        
        print(f"[AUTH] ✓ Password validation passed: {len(password)} chars, {len(password_bytes)} bytes")
        
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == email.lower().strip()).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create new user
        hashed_password = get_password_hash(password)
        new_user = User(
            username=username,
            email=email.lower().strip(),
            password_hash=hashed_password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create access token
        access_token = create_access_token(data={"sub": new_user.username})
        
        print(f"[AUTH] User created: {new_user.username} ({new_user.email})")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": new_user.id,
                "username": new_user.username,
                "email": new_user.email
            }
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like username/email already exists)
        raise
    except ValueError as ve:
        # Handle validation errors (e.g., from Form() parameters)
        print(f"[AUTH] Validation error: {str(ve)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=f"Validation error: {str(ve)}")
    except Exception as e:
        print(f"[AUTH] Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")


@app.post("/api/auth/login")
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    # Try to find user by email
    user = db.query(User).filter(User.email == request.email.lower().strip()).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
    }


@app.get("/api/auth/me")
async def get_current_user_info(current_user: Optional[User] = Depends(get_current_user)):
    """Get current user information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "email_notifications_enabled": current_user.email_notifications_enabled
    }


# ===== OAUTH ENDPOINTS =====

@app.get("/api/oauth/{platform}/authorize")
async def oauth_authorize(platform: str):
    """Initiate OAuth flow for a platform - no authentication required"""
    if platform not in ["instagram", "linkedin", "x", "tiktok"]:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    # Check if OAuth credentials are configured
    if platform == "instagram" and not oauth_service.instagram_client_id:
        raise HTTPException(
            status_code=400, 
            detail="Instagram OAuth not configured. Please set INSTAGRAM_CLIENT_ID and INSTAGRAM_CLIENT_SECRET in your .env file"
        )
    elif platform == "linkedin" and not oauth_service.linkedin_client_id:
        raise HTTPException(
            status_code=400, 
            detail="LinkedIn OAuth not configured. Please set LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET in your .env file"
        )
    elif platform == "x" and not oauth_service.x_client_id:
        raise HTTPException(
            status_code=400, 
            detail="X OAuth not configured. Please set X_CLIENT_ID and X_CLIENT_SECRET in your .env file"
        )
    elif platform == "tiktok" and not oauth_service.tiktok_client_id:
        raise HTTPException(
            status_code=400, 
            detail="TikTok OAuth not configured. Please set TIKTOK_CLIENT_ID and TIKTOK_CLIENT_SECRET in your .env file"
        )
    
    # Generate state token (no user required for now)
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": None,  # No user required
        "platform": platform,
        "created_at": datetime.utcnow()
    }
    
    # Get authorization URL
    try:
        if platform == "instagram":
            auth_url = oauth_service.get_instagram_auth_url(state)
        elif platform == "linkedin":
            auth_url = oauth_service.get_linkedin_auth_url(state)
        elif platform == "x":
            auth_url = oauth_service.get_x_auth_url(state)
        elif platform == "tiktok":
            auth_url = oauth_service.get_tiktok_auth_url(state)
        
        return {"authorization_url": auth_url, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate OAuth URL: {str(e)}")


@app.get("/api/oauth/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback and store connection"""
    # Verify state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    state_data = oauth_states[state]
    user_id = state_data.get("user_id")  # Can be None
    
    # Clean up state
    del oauth_states[state]
    
    # Exchange code for token
    token_data = None
    if platform == "instagram":
        token_data = await oauth_service.exchange_instagram_code(code)
    elif platform == "linkedin":
        token_data = await oauth_service.exchange_linkedin_code(code)
    elif platform == "x":
        token_data = await oauth_service.exchange_x_code(code)
    elif platform == "tiktok":
        token_data = await oauth_service.exchange_tiktok_code(code)
    
    if not token_data:
        raise HTTPException(status_code=400, detail="Failed to exchange authorization code")
    
    # Calculate token expiration
    expires_at = None
    if token_data.get("expires_in"):
        expires_at = datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
    
    # Check if connection already exists (no user filter if user_id is None)
    existing = None
    if user_id:
        existing = db.query(SocialMediaConnection).filter(
            SocialMediaConnection.user_id == user_id,
            SocialMediaConnection.platform == platform,
            SocialMediaConnection.account_id == token_data["user_id"]
        ).first()
    else:
        # Check by platform and account_id only
        existing = db.query(SocialMediaConnection).filter(
            SocialMediaConnection.platform == platform,
            SocialMediaConnection.account_id == token_data["user_id"]
        ).first()
    
    if existing:
        # Update existing connection
        existing.access_token = token_data["access_token"]
        existing.refresh_token = token_data.get("refresh_token")
        existing.token_expires_at = expires_at
        existing.is_active = True
        existing.last_used_at = datetime.utcnow()
        db.commit()
        connection = existing
    else:
        # Create new connection
        connection = SocialMediaConnection(
            user_id=user_id,
            platform=platform,
            account_username=token_data.get("username", ""),
            account_id=token_data["user_id"],
            access_token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_expires_at=expires_at
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
    
    # Redirect to frontend success page (Settings tab)
    from fastapi.responses import RedirectResponse
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=f"{frontend_url}/dashboard?tab=settings&connected={platform}")


# ===== SOCIAL MEDIA CONNECTION MANAGEMENT =====

@app.get("/api/connections", response_model=List[SocialMediaConnectionResponse])
async def get_connections(db: Session = Depends(get_db)):
    """Get all active social media connections - no authentication required"""
    connections = db.query(SocialMediaConnection).filter(
        SocialMediaConnection.is_active == True
    ).all()
    
    return [
        SocialMediaConnectionResponse(
            id=conn.id,
            platform=conn.platform,
            account_username=conn.account_username,
            account_id=conn.account_id,
            is_active=conn.is_active,
            connected_at=conn.connected_at.isoformat(),
            last_used_at=conn.last_used_at.isoformat() if conn.last_used_at else None
        )
        for conn in connections
    ]


@app.post("/api/connections/instagram/manual", response_model=SocialMediaConnectionResponse)
async def save_instagram_connection_manual(
    request: dict,
    db: Session = Depends(get_db)
):
    """Save Instagram connection manually with access token - no authentication required"""
    username = request.get("username", "").strip()
    access_token = request.get("access_token", "").strip()
    account_id = request.get("account_id", "").strip() or None
    
    if not username or not access_token:
        raise HTTPException(status_code=400, detail="Username and access token are required")
    
    # Try to get account info from Instagram API if account_id not provided
    if not account_id:
        try:
            # Use the access token to get user info
            import requests
            response = requests.get(
                f"https://graph.instagram.com/me?fields=id,username&access_token={access_token}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                account_id = data.get("id")
                if data.get("username"):
                    username = data["username"]  # Use the actual username from API
            else:
                # If API call fails, we can still save with username only
                print(f"[WARNING] Instagram API returned {response.status_code}: {response.text}")
                account_id = username  # Fallback to username as account_id
        except Exception as e:
            print(f"[WARNING] Could not fetch Instagram account info: {e}")
            # Continue without account_id - use username as fallback
            account_id = username if not account_id else account_id
    
    # Ensure account_id is set (required field)
    if not account_id:
        account_id = username  # Use username as account_id fallback
    
    # Check if connection already exists
    existing = db.query(SocialMediaConnection).filter(
        SocialMediaConnection.platform == "instagram",
        SocialMediaConnection.account_username == username
    ).first()
    
    if existing:
        # Update existing connection
        existing.access_token = access_token
        existing.account_id = account_id
        existing.is_active = True
        existing.connected_at = datetime.utcnow()
        existing.last_used_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        connection = existing
    else:
        # Create new connection
        connection = SocialMediaConnection(
            user_id=None,  # No user required
            platform="instagram",
            account_username=username,
            account_id=account_id,
            access_token=access_token,
            refresh_token=None,
            token_expires_at=None  # Manual tokens don't have expiration info
        )
        db.add(connection)
        db.commit()
        db.refresh(connection)
    
    return SocialMediaConnectionResponse(
        id=connection.id,
        platform=connection.platform,
        account_username=connection.account_username,
        account_id=connection.account_id,
        is_active=connection.is_active,
        connected_at=connection.connected_at.isoformat(),
        last_used_at=connection.last_used_at.isoformat() if connection.last_used_at else None
    )


@app.delete("/api/connections/{connection_id}")
async def disconnect_account(connection_id: int, db: Session = Depends(get_db)):
    """Disconnect a social media account - no authentication required"""
    connection = db.query(SocialMediaConnection).filter(
        SocialMediaConnection.id == connection_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    connection.is_active = False
    db.commit()
    
    return {"message": "Account disconnected successfully"}


# ===== INTEGRATION ENDPOINTS (Notion, Google Drive) =====

@app.get("/api/integrations/{platform}/authorize")
async def integration_authorize(
    platform: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Initiate OAuth flow for Notion, Google Drive, or Jira"""
    if platform not in ["notion", "google_drive", "jira"]:
        raise HTTPException(status_code=400, detail="Invalid platform. Supported: notion, google_drive, jira")
    
    # Generate state token
    state = secrets.token_urlsafe(32)
    oauth_states[state] = {
        "user_id": current_user.id,
        "platform": platform,
        "created_at": datetime.utcnow()
    }
    
    try:
        if platform == "notion":
            # Always use OAuth flow for Notion (each user connects their own account)
            if not notion_service.client_id or not notion_service.client_secret:
                raise HTTPException(
                    status_code=400,
                    detail="Notion OAuth not configured. Please set NOTION_CLIENT_ID and NOTION_CLIENT_SECRET in your environment variables."
                )
            auth_url = notion_service.get_authorization_url(state)
        elif platform == "google_drive":
            if not google_drive_service.client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Google Drive OAuth not configured. Set GOOGLE_DRIVE_CLIENT_ID and GOOGLE_DRIVE_CLIENT_SECRET"
                )
            auth_url = google_drive_service.get_authorization_url(state)
        elif platform == "jira":
            if not jira_service.client_id:
                raise HTTPException(
                    status_code=400,
                    detail="Jira OAuth not configured. Set JIRA_CLIENT_ID and JIRA_CLIENT_SECRET"
                )
            auth_url = jira_service.get_authorization_url(state)
        
        return {"auth_url": auth_url, "state": state}
    except Exception as e:
        print(f"[Integration] Error generating auth URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/integrations/{platform}/callback")
async def integration_callback(
    platform: str,
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle OAuth callback for integrations"""
    if platform not in ["notion", "google_drive", "jira"]:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    # Verify state
    if state not in oauth_states:
        raise HTTPException(status_code=400, detail="Invalid state token")
    
    state_data = oauth_states[state]
    user_id = state_data.get("user_id")
    
    if not user_id:
        raise HTTPException(status_code=400, detail="User not found in state")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Exchange code for token
    try:
        if platform == "notion":
            token_data = await notion_service.exchange_code_for_token(code)
            if not token_data:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            access_token = token_data.get("access_token")
            user_info = await notion_service.get_user_info(access_token)
            
            # Calculate token expiry
            expires_in = token_data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Save or update connection
            existing = db.query(IntegrationConnection).filter(
                IntegrationConnection.user_id == user_id,
                IntegrationConnection.platform == "notion"
            ).first()
            
            if existing:
                existing.access_token = access_token
                existing.token_expires_at = expires_at
                existing.is_active = True
                existing.platform_user_id = user_info.get("id") if user_info else None
                existing.platform_user_email = user_info.get("email") if user_info else None
            else:
                existing = IntegrationConnection(
                    user_id=user_id,
                    platform="notion",
                    access_token=access_token,
                    token_expires_at=expires_at,
                    platform_user_id=user_info.get("id") if user_info else None,
                    platform_user_email=user_info.get("email") if user_info else None,
                    is_active=True
                )
                db.add(existing)
            
            db.commit()
            
        elif platform == "google_drive":
            token_data = await google_drive_service.exchange_code_for_token(code)
            if not token_data:
                # Get more detailed error information
                error_detail = "Failed to exchange code for token. Common causes: redirect_uri mismatch, invalid client credentials, or code already used/expired."
                print(f"[API] Google Drive OAuth error: {error_detail}")
                print(f"[API] Redirect URI configured: {google_drive_service.redirect_uri}")
                print(f"[API] Client ID set: {bool(google_drive_service.client_id)}")
                print(f"[API] Client Secret set: {bool(google_drive_service.client_secret)}")
                raise HTTPException(status_code=400, detail=f"400: {error_detail}. Check that GOOGLE_DRIVE_REDIRECT_URI matches exactly in Google Cloud Console and environment variables.")
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            # Calculate token expiry
            expires_in = token_data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Save or update connection
            existing = db.query(IntegrationConnection).filter(
                IntegrationConnection.user_id == user_id,
                IntegrationConnection.platform == "google_drive"
            ).first()
            
            if existing:
                existing.access_token = access_token
                existing.refresh_token = refresh_token
                existing.token_expires_at = expires_at
                existing.is_active = True
            else:
                existing = IntegrationConnection(
                    user_id=user_id,
                    platform="google_drive",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expires_at=expires_at
                )
                db.add(existing)
            
            db.commit()
        
        elif platform == "jira":
            token_data = await jira_service.exchange_code_for_token(code)
            if not token_data:
                raise HTTPException(status_code=400, detail="Failed to exchange code for token")
            
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            
            # Get accessible resources (Jira sites)
            resources = await jira_service.get_accessible_resources(access_token)
            if not resources:
                raise HTTPException(status_code=400, detail="No accessible Jira sites found")
            
            # Use the first accessible resource (cloud_id)
            cloud_id = resources[0].get("id")
            site_url = resources[0].get("url", "")
            
            # Get user info
            user_info = await jira_service.get_user_info(access_token, cloud_id)
            
            # Calculate token expiry
            expires_in = token_data.get("expires_in", 3600)
            expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            
            # Save or update connection
            existing = db.query(IntegrationConnection).filter(
                IntegrationConnection.user_id == user_id,
                IntegrationConnection.platform == "jira"
            ).first()
            
            if existing:
                existing.access_token = access_token
                existing.refresh_token = refresh_token
                existing.token_expires_at = expires_at
                existing.is_active = True
                existing.platform_user_id = cloud_id
                existing.platform_user_email = user_info.get("emailAddress") if user_info else None
                # Store cloud_id in metadata or as platform_user_id
                if hasattr(existing, 'metadata'):
                    existing.metadata = json.dumps({"cloud_id": cloud_id, "site_url": site_url})
            else:
                existing = IntegrationConnection(
                    user_id=user_id,
                    platform="jira",
                    access_token=access_token,
                    refresh_token=refresh_token,
                    token_expires_at=expires_at,
                    platform_user_id=cloud_id,
                    platform_user_email=user_info.get("emailAddress") if user_info else None
                )
                db.add(existing)
            
            db.commit()
        
        # Clean up state
        del oauth_states[state]
        
        # Redirect to frontend (Brand Context page)
        from fastapi.responses import RedirectResponse
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(url=f"{frontend_url}/dashboard?tab=brand-context&connected={platform}")
        
    except Exception as e:
        print(f"[Integration] Error in callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/integrations", response_model=List[IntegrationConnectionResponse])
async def get_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active integrations for the current user"""
    connections = db.query(IntegrationConnection).filter(
        IntegrationConnection.user_id == current_user.id,
        IntegrationConnection.is_active == True
    ).all()
    
    return [
        IntegrationConnectionResponse(
            id=conn.id,
            platform=conn.platform,
            connected=conn.is_active,
            platform_user_email=conn.platform_user_email,
            connected_at=conn.connected_at.isoformat() if conn.connected_at else None,
            last_synced_at=conn.last_synced_at.isoformat() if conn.last_synced_at else None
        )
        for conn in connections
    ]


def _extract_notion_title(page: dict) -> str:
    """Extract title from Notion page or database entry object"""
    # Check if it's a database entry (has properties)
    properties = page.get("properties", {})
    if properties:
        for prop_name, prop_data in properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array:
                    return "".join([item.get("plain_text", "") for item in title_array])
    
    # Check if it's a database (has title in database object)
    if page.get("object") == "database":
        title_array = page.get("title", [])
        if title_array:
            return "".join([item.get("plain_text", "") for item in title_array])
    
    # Check if it's a page with title in page properties
    if page.get("object") == "page":
        # Try to get title from page properties
        page_properties = page.get("properties", {})
        for prop_name, prop_data in page_properties.items():
            if prop_data.get("type") == "title":
                title_array = prop_data.get("title", [])
                if title_array:
                    return "".join([item.get("plain_text", "") for item in title_array])
    
    # Fallback: try to extract from URL or use ID
    url = page.get("url", "")
    if url:
        # Extract page name from URL (last part before query params)
        url_part = url.split("/")[-1].split("?")[0]
        if url_part and url_part != page.get("id", ""):
            return url_part.replace("-", " ").title()
    
    # Last resort: use ID
    page_id = page.get("id", "")
    if page_id:
        return f"Notion Page {page_id[:8]}"
    
    return "Untitled"


@app.get("/api/integrations/notion/pages", response_model=List[NotionPageResponse])
async def list_notion_pages(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all pages from user's Notion workspace"""
    # Get user's OAuth connection (required - no internal token fallback)
    connection = db.query(IntegrationConnection).filter(
        IntegrationConnection.user_id == current_user.id,
        IntegrationConnection.platform == "notion",
        IntegrationConnection.is_active == True
    ).first()
    
    if not connection:
        print(f"[Notion Pages] No connection found for user {current_user.id}")
        raise HTTPException(
            status_code=404, 
            detail="Notion not connected. Please connect your Notion account first."
        )
    
    if not connection.access_token:
        print(f"[Notion Pages] Connection exists but no access token for user {current_user.id}")
        raise HTTPException(
            status_code=404, 
            detail="Notion connection is missing access token. Please reconnect your Notion account."
        )
    
    print(f"[Notion Pages] Fetching pages for user {current_user.id}, connection ID: {connection.id}")
    
    try:
        pages = await notion_service.search_pages(connection.access_token)
        print(f"[Notion Pages] Found {len(pages)} pages")
        
        if not pages:
            print(f"[Notion Pages] Warning: No pages returned. This might indicate:")
            print(f"  - The integration doesn't have access to any pages")
            print(f"  - All pages are in databases (not top-level pages)")
            print(f"  - The access token might be invalid or expired")
        
        result = [
            NotionPageResponse(
                id=page.get("id", ""),
                title=_extract_notion_title(page),
                url=page.get("url"),
                last_edited_time=page.get("last_edited_time")
            )
            for page in pages
        ]
        
        print(f"[Notion Pages] Returning {len(result)} pages")
        return result
    except httpx.HTTPStatusError as e:
        print(f"[Notion Pages] HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Notion access token expired or invalid. Please reconnect your Notion account."
            )
        elif e.response.status_code == 403:
            raise HTTPException(
                status_code=403,
                detail="Notion integration doesn't have permission to access pages. Please check your Notion integration settings."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch Notion pages: {e.response.text}"
            )
    except Exception as e:
        print(f"[Notion Pages] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch Notion pages: {str(e)}"
        )


@app.get("/api/integrations/google-drive/files", response_model=List[GoogleDriveFileResponse])
async def list_google_drive_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    mime_type: Optional[str] = None
):
    """List files from user's Google Drive"""
    connection = db.query(IntegrationConnection).filter(
        IntegrationConnection.user_id == current_user.id,
        IntegrationConnection.platform == "google_drive",
        IntegrationConnection.is_active == True
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Google Drive not connected")
    
    # Refresh token if needed
    access_token = connection.access_token
    if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
        if connection.refresh_token:
            token_data = await google_drive_service.refresh_access_token(connection.refresh_token)
            if token_data:
                access_token = token_data.get("access_token")
                connection.access_token = access_token
                expires_in = token_data.get("expires_in", 3600)
                connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                db.commit()
    
    files = await google_drive_service.list_files(access_token, mime_type)
    
    return [
        GoogleDriveFileResponse(
            id=file.get("id", ""),
            name=file.get("name", ""),
            mimeType=file.get("mimeType", ""),
            webViewLink=file.get("webViewLink")
        )
        for file in files
    ]


@app.get("/api/integrations/jira/issues", response_model=List[JiraIssueResponse])
async def list_jira_issues(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    jql: Optional[str] = None
):
    """List issues from user's Jira workspace"""
    connection = db.query(IntegrationConnection).filter(
        IntegrationConnection.user_id == current_user.id,
        IntegrationConnection.platform == "jira",
        IntegrationConnection.is_active == True
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Jira not connected")
    
    # Get cloud_id from platform_user_id (stored during OAuth)
    cloud_id = connection.platform_user_id
    if not cloud_id:
        raise HTTPException(status_code=400, detail="Jira cloud ID not found. Please reconnect.")
    
    # Refresh token if needed
    access_token = connection.access_token
    if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
        if connection.refresh_token:
            token_data = await jira_service.refresh_access_token(connection.refresh_token)
            if token_data:
                access_token = token_data.get("access_token")
                connection.access_token = access_token
                expires_in = token_data.get("expires_in", 3600)
                connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                db.commit()
    
    issues = await jira_service.search_issues(access_token, cloud_id, jql or "")
    
    return [
        JiraIssueResponse(
            id=issue.get("id", ""),
            key=issue.get("key", ""),
            summary=issue.get("fields", {}).get("summary", ""),
            status=issue.get("fields", {}).get("status", {}).get("name") if issue.get("fields", {}).get("status") else None,
            project=issue.get("fields", {}).get("project", {}).get("name") if issue.get("fields", {}).get("project") else None,
            issue_type=issue.get("fields", {}).get("issuetype", {}).get("name") if issue.get("fields", {}).get("issuetype") else None,
            priority=issue.get("fields", {}).get("priority", {}).get("name") if issue.get("fields", {}).get("priority") else None,
            assignee=issue.get("fields", {}).get("assignee", {}).get("displayName") if issue.get("fields", {}).get("assignee") else None,
            reporter=issue.get("fields", {}).get("reporter", {}).get("displayName") if issue.get("fields", {}).get("reporter") else None,
            created=issue.get("fields", {}).get("created"),
            updated=issue.get("fields", {}).get("updated"),
            url=None  # Can construct from site URL and issue key if needed
        )
        for issue in issues
    ]


async def process_content_with_claude(content: str, source_name: str, source_type: str = "document") -> str:
    """
    Process content with Claude to extract key information and enhance it for brand context.
    Uses Claude (Bedrock or Anthropic API) to summarize and extract important details.
    """
    try:
        # Create a prompt for Claude to process the content
        system_message = f"""You are an expert at extracting and summarizing key information from {source_type} content for brand context.

Your task is to:
1. Extract key brand information (company details, products, services, values, mission)
2. Identify important facts, statistics, and claims
3. Summarize the content concisely while preserving critical details
4. Structure the information clearly for use in brand context

Return a well-structured summary that captures the essential information from the content."""

        prompt = f"""Please process and summarize the following {source_type} content from {source_name}:

{content[:8000]}  # Limit to 8000 chars to avoid token limits

Extract and organize the key information that would be useful for brand context and marketing content generation."""

        processed_content = None
        
        # Try Bedrock (Claude Sonnet 4.5) first
        if bedrock_service and bedrock_service.is_available():
            try:
                sonnet_4_5_arn = "arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
                print(f"[Integration] 🤖 Using AWS Bedrock (Claude Sonnet 4.5) to process {source_type} from {source_name}...")
                processed_content = await bedrock_service.generate_text(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=2000,
                    temperature=0.3,  # Lower temperature for more factual extraction
                    model=sonnet_4_5_arn,
                    use_converse_api=True
                )
                if processed_content:
                    print(f"[Integration] ✅ Content processed with Claude Sonnet 4.5 ({len(processed_content)} chars)")
                    return processed_content
            except Exception as bedrock_error:
                print(f"[Integration] ⚠️ AWS Bedrock failed, trying Anthropic Claude API: {bedrock_error}")
        
        # Fallback to Anthropic Claude API
        if not processed_content and openai_service and openai_service.claude_available:
            try:
                print(f"[Integration] 🤖 Using Anthropic Claude API to process {source_type} from {source_name}...")
                processed_content = await openai_service.generate_text_with_claude(
                    prompt=prompt,
                    system_message=system_message,
                    max_tokens=2000,
                    temperature=0.3
                )
                if processed_content:
                    print(f"[Integration] ✅ Content processed with Claude API ({len(processed_content)} chars)")
                    return processed_content
            except Exception as claude_error:
                print(f"[Integration] ⚠️ Anthropic Claude API failed, using original content: {claude_error}")
        
        # If Claude processing fails, return original content with a note
        print(f"[Integration] ℹ️ Claude processing not available, using original content")
        return f"[Content from {source_name}]\n\n{content}"
        
    except Exception as e:
        print(f"[Integration] Error processing content with Claude: {e}")
        # Return original content if processing fails
        return f"[Content from {source_name}]\n\n{content}"


@app.post("/api/integrations/import")
async def import_content(
    request: ImportContentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Import content from Notion, Google Drive, or Jira to unified brand context (same as uploaded files)"""
    connection = db.query(IntegrationConnection).filter(
        IntegrationConnection.id == request.integration_id,
        IntegrationConnection.user_id == current_user.id,
        IntegrationConnection.is_active == True
    ).first()
    
    # For Notion with internal token, connection might not exist
    platform = connection.platform if connection else "notion"  # Default to notion if using internal token
    
    if not connection and platform != "notion":
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Check if using Notion internal token
    if platform == "notion" and not connection and not notion_service.internal_token:
        raise HTTPException(status_code=404, detail="Notion not connected and no internal token configured")
    
    user_id = normalize_user_id(current_user)
    imported_items = []
    errors = []
    
    try:
        if platform == "notion":
            # Use connection token if available, otherwise use internal token
            access_token = connection.access_token if connection else None
            for page_id in request.item_ids:
                try:
                    # Get page content
                    raw_content = await notion_service.get_page_content(access_token, page_id)
                    if not raw_content:
                        errors.append({"id": page_id, "error": "Failed to fetch content"})
                        continue
                    
                    # Get page title/name for context
                    page_name = f"Notion Page {page_id}"
                    try:
                        # Try to get page title from Notion API
                        import httpx
                        async with httpx.AsyncClient() as client:
                            token = notion_service.get_token(access_token)
                            if token:
                                page_response = await client.get(
                                    f"https://api.notion.com/v1/pages/{page_id}",
                                    headers={
                                        "Authorization": f"Bearer {token}",
                                        "Notion-Version": "2022-06-28"
                                    }
                                )
                                if page_response.status_code == 200:
                                    page_data = page_response.json()
                                    # Extract title from page properties
                                    properties = page_data.get("properties", {})
                                    for prop_name, prop_data in properties.items():
                                        if prop_data.get("type") == "title":
                                            title_array = prop_data.get("title", [])
                                            if title_array:
                                                page_name = "".join([item.get("plain_text", "") for item in title_array])
                                                break
                    except Exception as title_error:
                        print(f"[Integration] Could not get Notion page title: {title_error}")
                        # Use default page_name
                    
                    # Process content with Claude to extract key information
                    print(f"[Integration] Processing Notion page '{page_name}' with Claude...")
                    processed_content = await process_content_with_claude(
                        content=raw_content,
                        source_name=page_name,
                        source_type="notion page"
                    )
                    
                    # Append to unified brand context (same as uploaded files)
                    document_content = f"Notion Page: {page_name}\n\n{processed_content}"
                    result = await memory_service.append_to_unified_brand_context(
                            user_id=user_id,
                        new_content=document_content,
                        content_type="notion_page"
                    )
                    
                    if result is None:
                        errors.append({"id": page_id, "error": "Failed to save to unified brand context"})
                        continue
                    
                    resource_id = result.get("resource_id")
                    imported_items.append({
                        "id": page_id,
                        "resource_id": resource_id,
                        "name": page_name,
                        "context_updated": True
                    })
                    print(f"[Integration] ✅ Notion page '{page_name}' added to unified brand context")
                except Exception as e:
                    print(f"[Integration] Error importing Notion page {page_id}: {e}")
                    errors.append({"id": page_id, "error": str(e)})
        
        elif connection.platform == "google_drive":
            access_token = connection.access_token
            # Refresh token if needed
            if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
                if connection.refresh_token:
                    token_data = await google_drive_service.refresh_access_token(connection.refresh_token)
                    if token_data:
                        access_token = token_data.get("access_token")
            
            for file_id in request.item_ids:
                try:
                    # Get file metadata first
                    metadata = await google_drive_service.get_file_metadata(access_token, file_id)
                    if not metadata:
                        errors.append({"id": file_id, "error": "Failed to fetch metadata"})
                        continue
                    
                    file_name = metadata.get("name", f"Google Drive File {file_id}")
                    mime_type = metadata.get("mimeType", "")
                    
                    # Get file content
                    raw_content = await google_drive_service.get_file_content(access_token, file_id, mime_type)
                    if not raw_content:
                        errors.append({"id": file_id, "error": "Failed to fetch content"})
                        continue
                    
                    # For binary files (PDF, DOCX), try to extract text using document_service
                    processed_content = raw_content
                    if mime_type in ('application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                     'application/msword', 'application/vnd.google-apps.document'):
                        try:
                            # Download file temporarily to extract text
                            import tempfile
                            import httpx
                            
                            # Download file content
                            async with httpx.AsyncClient() as client:
                                file_response = await client.get(
                                    f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media",
                                    headers={"Authorization": f"Bearer {access_token}"},
                                    timeout=30.0
                                )
                                file_response.raise_for_status()
                                file_bytes = file_response.content
                            
                            # Save to temp file and extract text
                            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file_name)[1]) as tmp_file:
                                tmp_file.write(file_bytes)
                                tmp_path = tmp_file.name
                            
                            try:
                                extracted_text = await document_service.extract_text(tmp_path, mime_type)
                                if extracted_text and len(extracted_text.strip()) > 0:
                                    processed_content = extracted_text
                                    print(f"[Integration] Extracted {len(extracted_text)} characters from {file_name}")
                            except Exception as extract_error:
                                print(f"[Integration] Warning: Failed to extract text from {file_name}: {extract_error}")
                                # Use raw content if extraction fails
                            finally:
                                # Clean up temp file
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass
                        except Exception as download_error:
                            print(f"[Integration] Warning: Failed to download file for text extraction: {download_error}")
                            # Continue with raw content
                    
                    # Process content with Claude to extract key information
                    print(f"[Integration] Processing Google Drive file '{file_name}' with Claude...")
                    enhanced_content = await process_content_with_claude(
                        content=processed_content,
                        source_name=file_name,
                        source_type="google drive file"
                    )
                    
                    # Append to unified brand context (same as uploaded files)
                    document_content = f"Google Drive File: {file_name}\n\n{enhanced_content}"
                    result = await memory_service.append_to_unified_brand_context(
                            user_id=user_id,
                        new_content=document_content,
                        content_type="google_drive_file"
                    )
                    
                    if result is None:
                        errors.append({"id": file_id, "error": "Failed to save to unified brand context"})
                        continue
                    
                    resource_id = result.get("resource_id")
                    imported_items.append({
                        "id": file_id,
                        "resource_id": resource_id,
                        "name": file_name,
                        "context_updated": True
                    })
                    print(f"[Integration] ✅ Google Drive file '{file_name}' added to unified brand context")
                except Exception as e:
                    print(f"[Integration] Error importing Google Drive file {file_id}: {e}")
                    errors.append({"id": file_id, "error": str(e)})
        
        elif connection.platform == "jira":
            # Get cloud_id from platform_user_id
            cloud_id = connection.platform_user_id
            if not cloud_id:
                errors.append({"error": "Jira cloud ID not found. Please reconnect."})
            else:
                access_token = connection.access_token
                # Refresh token if needed
                if connection.token_expires_at and connection.token_expires_at < datetime.utcnow():
                    if connection.refresh_token:
                        token_data = await jira_service.refresh_access_token(connection.refresh_token)
                        if token_data:
                            access_token = token_data.get("access_token")
                            connection.access_token = access_token
                            expires_in = token_data.get("expires_in", 3600)
                            connection.token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
                            db.commit()
                
                # item_ids are issue keys (e.g., "PROJ-123")
                for issue_key in request.item_ids:
                    try:
                        raw_content = await jira_service.get_issue_content(access_token, cloud_id, issue_key)
                        if not raw_content:
                            errors.append({"id": issue_key, "error": "Failed to fetch content"})
                            continue
                        
                        # Process content with Claude to extract key information
                        print(f"[Integration] Processing Jira issue '{issue_key}' with Claude...")
                        processed_content = await process_content_with_claude(
                            content=raw_content,
                            source_name=issue_key,
                            source_type="jira issue"
                        )
                        
                        # Append to unified brand context (same as uploaded files)
                        document_content = f"Jira Issue: {issue_key}\n\n{processed_content}"
                        result = await memory_service.append_to_unified_brand_context(
                                user_id=user_id,
                            new_content=document_content,
                            content_type="jira_issue"
                        )
                        
                        if result is None:
                            errors.append({"id": issue_key, "error": "Failed to save to unified brand context"})
                            continue
                        
                        resource_id = result.get("resource_id")
                        imported_items.append({
                            "id": issue_key,
                            "resource_id": resource_id,
                            "name": issue_key,
                            "context_updated": True
                        })
                        print(f"[Integration] ✅ Jira issue '{issue_key}' added to unified brand context")
                    except Exception as e:
                        print(f"[Integration] Error importing Jira issue {issue_key}: {e}")
                        errors.append({"id": issue_key, "error": str(e)})
        
        # Update last_synced_at
        if connection:
            connection.last_synced_at = datetime.utcnow()
            db.commit()
        
        return {
            "success": True,
            "imported": imported_items,
            "errors": errors
        }
    except Exception as e:
        print(f"[Integration] Error importing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/integrations/{integration_id}")
async def disconnect_integration(
    integration_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect an integration"""
    connection = db.query(IntegrationConnection).filter(
        IntegrationConnection.id == integration_id,
        IntegrationConnection.user_id == current_user.id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    connection.is_active = False
    db.commit()
    
    return {"message": "Integration disconnected successfully"}


# ===== POSTING ENDPOINTS =====

@app.post("/api/post/video", response_model=PostVideoResponse)
async def post_video(
    request: PostVideoRequest,
    db: Session = Depends(get_db)
):
    """Post video to connected social media accounts - no authentication required"""
    # Get connections (no user filter for now)
    connections = db.query(SocialMediaConnection).filter(
        SocialMediaConnection.id.in_(request.connection_ids),
        SocialMediaConnection.is_active == True
    ).all()
    
    if not connections:
        raise HTTPException(status_code=400, detail="No valid connections found")
    
    results = []
    errors = []
    
    for connection in connections:
        try:
            # Post to platform
            if connection.platform == "instagram":
                result = await posting_service.post_to_instagram(
                    access_token=connection.access_token,
                    video_url=request.video_url,
                    caption=request.caption,
                    account_id=connection.account_id
                )
            elif connection.platform == "linkedin":
                result = await posting_service.post_to_linkedin(
                    access_token=connection.access_token,
                    video_url=request.video_url,
                    image_url=request.image_url,
                    caption=request.caption or "",
                    person_urn=f"urn:li:person:{connection.account_id}"
                )
            elif connection.platform == "x":
                result = await posting_service.post_to_x(
                    access_token=connection.access_token,
                    video_url=request.video_url,
                    caption=request.caption
                )
            elif connection.platform == "tiktok":
                result = await posting_service.post_to_tiktok(
                    access_token=connection.access_token,
                    video_url=request.video_url,
                    caption=request.caption
                )
            else:
                result = {"success": False, "error": "Unsupported platform", "platform": connection.platform}
            
            # Save post history (optional - only if user_id exists)
            post_history = None
            if connection.user_id:
                post_history = PostHistory(
                    user_id=connection.user_id,
                    connection_id=connection.id,
                    platform=connection.platform,
                    post_id=result.get("post_id"),
                    post_url=result.get("post_url"),
                    video_url=request.video_url,
                    caption=request.caption,
                    status="posted" if result.get("success") else "failed",
                    error_message=result.get("error"),
                    posted_at=datetime.utcnow() if result.get("success") else None
                )
                db.add(post_history)
            
            # Update connection last used
            connection.last_used_at = datetime.utcnow()
            
            results.append(result)
            
            # Send email notification if posting was successful - always send to nagurivindapalli@gmail.com
            if result.get("success"):
                email_sent = email_service.send_video_posted_notification(
                    to_email=None,  # Will use nagurivindapalli@gmail.com
                    username=connection.account_username or "User",
                    platform=connection.platform,
                    post_url=result.get("post_url"),
                    video_url=request.video_url,
                    caption=request.caption
                )
                if email_sent and post_history:
                    post_history.email_sent = True
                    post_history.email_sent_at = datetime.utcnow()
            
        except Exception as e:
            error_msg = f"Failed to post to {connection.platform}: {str(e)}"
            errors.append(error_msg)
            results.append({
                "success": False,
                "error": error_msg,
                "platform": connection.platform
            })
    
    db.commit()
    
    return PostVideoResponse(
        success=any(r.get("success") for r in results),
        posts=results,
        errors=errors if errors else None
    )


@app.get("/api/posts/history")
async def get_post_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get post history for current user"""
    posts = db.query(PostHistory).filter(
        PostHistory.user_id == current_user.id
    ).order_by(PostHistory.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": post.id,
            "platform": post.platform,
            "post_url": post.post_url,
            "caption": post.caption,
            "status": post.status,
            "posted_at": post.posted_at.isoformat() if post.posted_at else None,
            "created_at": post.created_at.isoformat(),
            "email_sent": post.email_sent
        }
        for post in posts
    ]


@app.post("/api/post/instagram/manual", response_model=ManualInstagramPostResponse)
async def post_to_instagram_manual(
    request: ManualInstagramPostRequest
):
    """Post video to Instagram using browser automation - no authentication required"""
    try:
        print(f"[API] Manual Instagram post requested for user: {request.username}")
        print(f"[API] Video URL: {request.video_url}")
        
        # Use browser automation to post
        result = await browser_automation_service.post_to_instagram_automation(
            username=request.username,
            password=request.password,
            video_url=request.video_url,
            caption=request.caption
        )
        
        if result.get("success"):
            # Send email notification
            email_service.send_video_posted_notification(
                to_email=None,  # Will use nagurivindapalli@gmail.com
                username=request.username,
                platform="instagram",
                post_url="https://www.instagram.com/",  # We don't have exact post URL from automation
                video_url=request.video_url,
                caption=request.caption
            )
        
        return ManualInstagramPostResponse(
            success=result.get("success", False),
            message=result.get("message", ""),
            error=result.get("error")
        )
    except Exception as e:
        print(f"[API] Error in manual Instagram post: {e}")
        import traceback
        traceback.print_exc()
        return ManualInstagramPostResponse(
            success=False,
            message="Failed to post video",
            error=str(e)
        )


@app.post("/api/post/linkedin/company", response_model=LinkedInCompanyPostResponse)
async def post_to_linkedin_company(
    request: LinkedInCompanyPostRequest,
    db: Session = Depends(get_db)
):
    """
    Post to LinkedIn company page (AIGIS page)
    
    This endpoint posts content directly to the configured LinkedIn company page.
    The company page is configured via LINKEDIN_COMPANY_ID environment variable.
    
    Requires:
    - LinkedIn OAuth access token with w_organization_social scope
    - Or a stored connection with LinkedIn
    """
    try:
        print(f"[API] LinkedIn company post requested")
        print(f"[API] Caption length: {len(request.caption)} chars")
        print(f"[API] Has image_url: {bool(request.image_url)}")
        print(f"[API] Has image_base64: {bool(request.image_base64)}")
        
        # Get access token - either from request or stored connection
        access_token = request.access_token
        
        if not access_token:
            # Try to get from stored LinkedIn connection
            linkedin_conn = db.query(SocialMediaConnection).filter(
                SocialMediaConnection.platform == "linkedin",
                SocialMediaConnection.is_active == True
            ).first()
            
            if linkedin_conn:
                access_token = linkedin_conn.access_token
                print(f"[API] Using stored LinkedIn connection token")
            else:
                return LinkedInCompanyPostResponse(
                    success=False,
                    error="No LinkedIn access token provided and no active LinkedIn connection found. Please connect LinkedIn first."
                )
        
        # Post to company page
        result = await posting_service.post_to_linkedin_company(
            access_token=access_token,
            caption=request.caption,
            image_url=request.image_url,
            image_base64=request.image_base64
        )
        
        if result.get("success"):
            print(f"[API] ✓ LinkedIn company post created: {result.get('post_url')}")
            
            # Send email notification
            email_service.send_video_posted_notification(
                to_email=None,
                username="AIGIS Company Page",
                platform="linkedin",
                post_url=result.get("post_url"),
                video_url=None,
                caption=request.caption[:200] + "..." if len(request.caption) > 200 else request.caption
            )
        else:
            print(f"[API] ✗ LinkedIn company post failed: {result.get('error')}")
        
        return LinkedInCompanyPostResponse(
            success=result.get("success", False),
            post_id=result.get("post_id"),
            post_url=result.get("post_url"),
            error=result.get("error")
        )
        
    except Exception as e:
        print(f"[API] Error in LinkedIn company post: {e}")
        import traceback
        traceback.print_exc()
        return LinkedInCompanyPostResponse(
            success=False,
            error=str(e)
        )


@app.get("/api/linkedin/auth-url")
async def get_linkedin_auth_url():
    """
    Get the LinkedIn OAuth authorization URL
    
    The user should be redirected to this URL to authorize LinkedIn access.
    After authorization, LinkedIn will redirect back to the callback URL.
    """
    try:
        state = secrets.token_urlsafe(32)
        auth_url = oauth_service.get_linkedin_auth_url(state)
        return {
            "auth_url": auth_url,
            "state": state
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/oauth/linkedin/callback")
async def linkedin_oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):
    """
    Handle LinkedIn OAuth callback
    
    This endpoint receives the authorization code from LinkedIn
    and exchanges it for an access token.
    """
    try:
        if error:
            print(f"[OAuth] LinkedIn authorization error: {error}")
            return JSONResponse(
                status_code=400,
                content={"error": f"LinkedIn authorization failed: {error}"}
            )
        
        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "No authorization code received"}
            )
        
        print(f"[OAuth] Exchanging LinkedIn code for token...")
        token_data = await oauth_service.exchange_linkedin_code(code)
        
        if not token_data:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to exchange authorization code"}
            )
        
        # Store the connection
        linkedin_conn = db.query(SocialMediaConnection).filter(
            SocialMediaConnection.platform == "linkedin"
        ).first()
        
        if linkedin_conn:
            # Update existing connection
            linkedin_conn.access_token = token_data["access_token"]
            linkedin_conn.refresh_token = token_data.get("refresh_token")
            linkedin_conn.account_id = token_data.get("user_id", "")
            linkedin_conn.account_username = token_data.get("username", "LinkedIn User")
            linkedin_conn.is_active = True
            linkedin_conn.expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))
            print(f"[OAuth] Updated existing LinkedIn connection")
        else:
            # Create new connection
            linkedin_conn = SocialMediaConnection(
                platform="linkedin",
                access_token=token_data["access_token"],
                refresh_token=token_data.get("refresh_token"),
                account_id=token_data.get("user_id", ""),
                account_username=token_data.get("username", "LinkedIn User"),
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 5184000))
            )
            db.add(linkedin_conn)
            print(f"[OAuth] Created new LinkedIn connection")
        
        db.commit()
        
        # Redirect to frontend success page
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3001")
        return JSONResponse(
            content={
                "success": True,
                "message": "LinkedIn connected successfully!",
                "username": token_data.get("username", "LinkedIn User"),
                "redirect_url": f"{frontend_url}/settings?linkedin=connected"
            }
        )
        
    except Exception as e:
        print(f"[OAuth] LinkedIn callback error: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/linkedin/company-info")
async def get_linkedin_company_info():
    """Get configured LinkedIn company page information"""
    company_id = os.getenv("LINKEDIN_COMPANY_ID", "")
    if not company_id:
        return {
            "configured": False,
            "error": "LINKEDIN_COMPANY_ID not set in environment"
        }
    
    return {
        "configured": True,
        "company_id": company_id,
        "company_url": f"https://www.linkedin.com/company/{company_id}/",
        "company_name": "AIGIS"  # Hardcoded for now, could be fetched from LinkedIn API
    }


@app.put("/api/user/email-notifications")
async def update_email_notifications(
    enabled: bool = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update email notification preferences"""
    from fastapi import Query
    # Get enabled from query parameter
    if enabled is None:
        raise HTTPException(status_code=400, detail="enabled query parameter is required")
    
    current_user.email_notifications_enabled = enabled
    db.commit()
    return {"email_notifications_enabled": enabled}


# ===== VEO 3 & IMAGE GENERATION ENDPOINTS =====

@app.post("/api/veo3/generate", response_model=Veo3GenerateResponse)
async def generate_veo3_video(request: Veo3GenerateRequest):
    """
    Generate a video using Veo 3 API
    Supports text-to-video and image-to-video generation
    If max_extensions > 0, extensions will be automatically triggered when the base video completes.
    """
    try:
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 not configured. Set GOOGLE_CLOUD_PROJECT_ID in your .env file"
            )
        
        result = await veo3_service.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            resolution=request.resolution,
            image_urls=request.image_urls,
            style=request.style
        )
        
        # Set up extension metadata if max_extensions > 0
        if request.max_extensions > 0:
            # Initialize extension cache if needed
            if not hasattr(veo3_service, '_extension_cache'):
                veo3_service._extension_cache = {}
            
            job_id = result.get("job_id")
            extension_metadata = {
                'base_job_id': job_id,
                'original_job_id': job_id,
                'needs_extension': True,
                'extension_count': request.max_extensions,
                'extensions_completed': 0,
                'current_duration': request.duration,
                'last_extension_job_id': None,
                'extension_attempted': False,
                'extension_failed': False
            }
            # Store with both full job_id and operation ID for easier lookup
            veo3_service._extension_cache[job_id] = extension_metadata
            # Also store with just the operation ID (last part after /operations/)
            if '/' in job_id:
                operation_id = job_id.split('/')[-1]
                veo3_service._extension_cache[operation_id] = extension_metadata
            print(f"[API] [OK] Extension metadata set up for job_id: {job_id[:80]}...")
            print(f"[API] [OK] {request.max_extensions} extensions will be triggered automatically when video completes")
        
        return Veo3GenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Veo 3 generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/veo3/status/{job_id:path}", response_model=Veo3StatusResponse)
async def get_veo3_status(job_id: str, extend: Optional[bool] = None):
    """Check the status of a Veo 3 video generation job
    
    job_id can be a full operation path like:
    projects/{project}/locations/{location}/publishers/google/models/{model}/operations/{operation_id}
    
    If extend=true and video is completed, will automatically extend the video.
    """
    try:
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 not configured. Set GOOGLE_CLOUD_PROJECT_ID in .env"
            )
        
        # URL decode the job_id in case it was encoded
        from urllib.parse import unquote
        job_id = unquote(job_id)
        
        status = await veo3_service.get_video_status(job_id)
        
        # Check video status
        status_value = status.get("status")
        print(f"[API] [STATUS] Status check - status: {status_value}")
        
        # If video generation failed, log the error and return immediately
        if status_value == "failed":
            error_msg = status.get("error", "Unknown error")
            print(f"[API] [ERROR] Video generation FAILED: {error_msg}")
            return Veo3StatusResponse(**status)
        
        # Check if this job needs extensions (from cache)
        extension_metadata = None
        is_extension_job = status.get("is_extension", False)
        
        # Check extension cache to see if this job needs extensions
        # This works for both base jobs and extension jobs
        if hasattr(veo3_service, '_extension_cache'):
            print(f"[API] [CACHE] Checking extension cache for job_id: {job_id[:80]}...")
            print(f"[API] [CACHE] Cache keys: {list(veo3_service._extension_cache.keys())[:3] if veo3_service._extension_cache else 'empty'}")
            
            # Try exact match first
            if job_id in veo3_service._extension_cache:
                extension_metadata = veo3_service._extension_cache[job_id]
                is_extension_job = True
                print(f"[API] [OK] Found extension metadata (exact match)")
            else:
                # Try partial matches (could be full path or just operation ID)
                for cached_job_id, cached_meta in veo3_service._extension_cache.items():
                    # Extract operation ID from full path for comparison
                    # Format: projects/.../operations/{operation_id}
                    job_operation_id = job_id.split('/')[-1] if '/' in job_id else job_id
                    cached_operation_id = cached_job_id.split('/')[-1] if '/' in cached_job_id else cached_job_id
                    
                    # Check if this job_id matches (could be full path or just operation ID)
                    if (job_id == cached_job_id or 
                        job_id.endswith(cached_job_id) or 
                        cached_job_id.endswith(job_id) or
                        job_operation_id == cached_operation_id or
                        job_operation_id == cached_job_id or
                        cached_operation_id == job_id):
                        extension_metadata = cached_meta
                        is_extension_job = True
                        print(f"[API] [OK] Found extension metadata (partial match: {cached_job_id[:50]}...)")
                        break
                
                if not extension_metadata:
                    print(f"[API] [WARN] No extension metadata found in cache for this job_id")
        
        # If video is completed, check if we need to trigger extensions
        if status_value == "completed":
            if extension_metadata and extension_metadata.get("needs_extension", False):
                extensions_completed = extension_metadata.get("extensions_completed", 0)
                extension_count = extension_metadata.get("extension_count", 0)
                base_job_id = extension_metadata.get("base_job_id") or extension_metadata.get("original_job_id") or job_id
                
                print(f"[API] [OK] Base video completed! Extensions: {extensions_completed}/{extension_count}")
                
                # If we haven't completed all extensions, trigger the next one
                # BUT: Check if we've already attempted this extension and failed (prevent infinite loops)
                extension_attempted = extension_metadata.get("extension_attempted", False)
                extension_failed = extension_metadata.get("extension_failed", False)
                
                if extensions_completed < extension_count:
                    # Prevent infinite retry loops - if extension failed, don't retry
                    if extension_failed:
                        print(f"[API] [WARN] Extension previously failed, not retrying to prevent infinite loop")
                        status["needs_extension"] = True
                        status["extension_count"] = extension_count
                        status["extensions_completed"] = extensions_completed
                        status["error"] = extension_metadata.get("extension_error", "Extension failed")
                        return Veo3StatusResponse(**status)
                    
                    # CRITICAL: Check if an extension is already in progress to prevent duplicate triggers
                    # If last_extension_job_id exists and is different from current job_id, check its status
                    last_ext_job_id = extension_metadata.get("last_extension_job_id")
                    if last_ext_job_id and last_ext_job_id != job_id:
                        try:
                            last_ext_status = await veo3_service.get_video_status(last_ext_job_id)
                            if last_ext_status.get("status") in ["queued", "in_progress"]:
                                # Extension already in progress, return its status
                                print(f"[API] [WAIT] Extension {extensions_completed + 1} already in progress, waiting...")
                                status["needs_extension"] = True
                                status["extension_count"] = extension_count
                                status["extensions_completed"] = extensions_completed
                                status["is_extension"] = True
                                status["status"] = last_ext_status.get("status", "in_progress")
                                status["progress"] = last_ext_status.get("progress", 0)
                                status["job_id"] = last_ext_job_id  # Return the extension job ID
                                return Veo3StatusResponse(**status)
                        except Exception:
                            # If we can't check the status, proceed with starting new extension
                            pass
                    
                    # Only attempt extension if we haven't tried yet, or if previous attempt succeeded
                    if not extension_attempted or extensions_completed > 0:
                        try:
                            print(f"[API] [EXTEND] Triggering extension {extensions_completed + 1}/{extension_count}...")
                            
                            # Mark that we're attempting extension (prevent duplicate attempts)
                            extension_metadata["extension_attempted"] = True
                            extension_metadata["extension_failed"] = False
                            veo3_service._extension_cache[base_job_id] = extension_metadata.copy()
                            
                            # Use Gemini API to extend the video
                            # For the first extension, use the base job_id
                            # For subsequent extensions, use the current job_id (which is the completed extension)
                            # This allows chaining: base -> ext1 -> ext2 -> ext3, etc.
                            source_job_id = base_job_id if extensions_completed == 0 else job_id
                            print(f"[API] [EXTEND] Triggering extension {extensions_completed + 1}/{extension_count}...")
                            print(f"[API] [EXTEND] Source job for extension {extensions_completed + 1}: {source_job_id[:50]}...")
                            
                            extension_result = await veo3_service.extend_video_gemini_api(
                                base_job_id=source_job_id,
                                extension_seconds=7,
                                max_extensions=1
                            )
                            
                            # Update metadata - extension started successfully
                            extension_metadata["extensions_completed"] = extensions_completed + 1
                            extension_metadata["current_duration"] = 8 + (extension_metadata["extensions_completed"] * 7)
                            new_extension_job_id = extension_result.get("job_id")
                            extension_metadata["last_extension_job_id"] = new_extension_job_id  # Always update to latest extension
                            extension_metadata["extension_attempted"] = False  # Reset for next extension
                            extension_metadata["extension_failed"] = False
                            
                            # Update cache with new extension job - CRITICAL: Update both the new job and base job
                            veo3_service._extension_cache[new_extension_job_id] = extension_metadata.copy()  # Make a copy
                            veo3_service._extension_cache[base_job_id] = extension_metadata.copy()  # Make a copy
                            
                            print(f"[API] [OK] Extension {extensions_completed + 1}/{extension_count} started! Job ID: {new_extension_job_id[:80]}...")
                            print(f"[API] [DEBUG] Updated last_extension_job_id to: {new_extension_job_id[:80]}...")
                            print(f"[API] [DEBUG] Current duration: {extension_metadata['current_duration']}s")
                            
                            # Return status showing extension in progress
                            status["needs_extension"] = True
                            status["extension_count"] = extension_count
                            status["extensions_completed"] = extensions_completed + 1
                            status["is_extension"] = True
                            status["status"] = "in_progress"  # Extension is now in progress
                            status["job_id"] = new_extension_job_id  # Return the extension job ID
                            return Veo3StatusResponse(**status)
                            
                        except Exception as ext_error:
                            print(f"[API] [ERROR] Extension failed: {ext_error}")
                            # Mark extension as failed to prevent infinite retries
                            extension_metadata["extension_failed"] = True
                            extension_metadata["extension_error"] = str(ext_error)
                            extension_metadata["extension_attempted"] = False  # Allow retry on next status check if needed
                            veo3_service._extension_cache[base_job_id] = extension_metadata
                            
                            # Return base video status with error
                            status["needs_extension"] = True
                            status["extension_count"] = extension_count
                            status["extensions_completed"] = extensions_completed
                            status["error"] = f"Extension failed: {str(ext_error)}"
                            return Veo3StatusResponse(**status)
                    else:
                        # Extension already attempted, waiting for it to complete
                        print(f"[API] [WAIT] Extension {extensions_completed + 1} already attempted, waiting for completion...")
                else:
                    # All extensions completed!
                    print(f"[API] [OK] All extensions completed! Final duration: ~{8 + (extension_count * 7)}s")
                    
                    # Get the final extension job ID from metadata
                    last_extension_job_id = extension_metadata.get("last_extension_job_id")
                    
                    # CRITICAL: Always use last_extension_job_id if available (this is the final extended video)
                    # Only use current job_id if it's an extension job AND it matches last_extension_job_id
                    if last_extension_job_id:
                        # Use the last_extension_job_id from metadata (this is the final extension)
                        final_job_id = last_extension_job_id
                        print(f"[API] [OK] Using last_extension_job_id from metadata as final video: {final_job_id[:50]}...")
                        print(f"[API] [DEBUG] Current job_id was: {job_id[:50]}...")
                    elif is_extension_job and extensions_completed >= extension_count:
                        # Fallback: if current job_id is an extension job and all extensions are done, use it
                        final_job_id = job_id
                        print(f"[API] [OK] Using current job_id as final extension job (no last_extension_job_id): {final_job_id[:50]}...")
                    else:
                        # Last resort: use current job_id (shouldn't happen if extensions worked)
                        final_job_id = job_id
                        print(f"[API] [WARN] No last_extension_job_id found, using current job_id: {final_job_id[:50]}...")
                        print(f"[API] [WARN] This might be the base video, not the extended one!")
                    
                    if final_job_id:
                        # Check status of the final extension job to get the final video
                        print(f"[API] [OK] Getting final video from extension job: {final_job_id[:80]}...")
                        print(f"[API] [DEBUG] Extension metadata: completed={extensions_completed}/{extension_count}, last_job_id={last_extension_job_id[:80] if last_extension_job_id else 'None'}...")
                        try:
                            extension_status = await veo3_service.get_video_status(final_job_id)
                            print(f"[API] [DEBUG] Extension status: status={extension_status.get('status')}, video_url={extension_status.get('video_url', 'None')}")
                            if extension_status.get("status") == "completed":
                                # Use the extension job's status (has the extended video)
                                status = extension_status.copy()  # Make a copy to avoid modifying the original
                                status["needs_extension"] = False  # All extensions done - set to False
                                status["extension_count"] = extension_count
                                status["extensions_completed"] = extensions_completed
                                status["is_extension"] = True
                                status["job_id"] = final_job_id  # CRITICAL: Use final extension job ID so frontend updates
                                # Ensure video_url is set
                                if not status.get("video_url") and extension_status.get("video_url"):
                                    status["video_url"] = extension_status.get("video_url")
                                print(f"[API] [OK] Final extended video ready from job: {final_job_id[:80]}...")
                                print(f"[API] [OK] Video URL: {status.get('video_url', 'None')}")
                                print(f"[API] [OK] Returning job_id: {status.get('job_id', 'None')[:80]}...")
                                # Return immediately with the final video
                                return Veo3StatusResponse(**status)
                            else:
                                # Extension still processing, return its status
                                status["needs_extension"] = False  # All extensions done, just waiting for final video
                                status["extension_count"] = extension_count
                                status["extensions_completed"] = extensions_completed
                                status["is_extension"] = True
                                status["job_id"] = final_job_id
                                status["status"] = extension_status.get("status", "in_progress")
                                status["progress"] = extension_status.get("progress", 0)
                                status["video_url"] = extension_status.get("video_url")
                                return Veo3StatusResponse(**status)
                        except Exception as ext_status_error:
                            print(f"[API] [WARN] Could not get extension status: {ext_status_error}")
                            # Fall back to base video if extension status check fails
                            status["needs_extension"] = False  # All extensions done
                            status["extension_count"] = extension_count
                            status["extensions_completed"] = extensions_completed
                            status["is_extension"] = True
                            status["job_id"] = final_job_id  # Use final job ID
                            return Veo3StatusResponse(**status)
                    else:
                        # No extension job ID found, use base video
                        status["needs_extension"] = False  # All extensions done
                        status["extension_count"] = extension_count
                        status["extensions_completed"] = extensions_completed
                        status["is_extension"] = True
                        # Return with base video since no extension job ID found
                        return Veo3StatusResponse(**status)
            else:
                # No extensions needed or metadata not found
                if extension_metadata:
                    status["needs_extension"] = extension_metadata.get("needs_extension", False)
                    status["extension_count"] = extension_metadata.get("extension_count", 0)
                    status["extensions_completed"] = extension_metadata.get("extensions_completed", 0)
                else:
                    status["needs_extension"] = False
                    status["extension_count"] = 0
                    status["extensions_completed"] = 0
                status["is_extension"] = is_extension_job
        
        return Veo3StatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/veo3/download/{job_id:path}")
async def download_veo3_video(job_id: str):
    """Download a completed Veo 3 video
    
    job_id can be a full operation path like:
    projects/{project}/locations/{location}/publishers/google/models/{model}/operations/{operation_id}
    """
    try:
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 not configured. Set GOOGLE_CLOUD_PROJECT_ID in .env"
            )
        
        # URL decode the job_id in case it was encoded
        from urllib.parse import unquote
        job_id = unquote(job_id)
        
        # Get video data from status
        status = await veo3_service.get_video_status(job_id)
        if status.get("status") != "completed":
            raise HTTPException(
                status_code=400,
                detail=f"Video not ready. Status: {status.get('status')}"
            )
        
        # Get video bytes - either from URL or directly from operation
        video_bytes = await veo3_service.get_video_bytes(job_id, status)
        
        from fastapi.responses import Response
        return Response(
            content=video_bytes,
            media_type="video/mp4",
            headers={
                "Content-Disposition": f"attachment; filename=veo3_{job_id}.mp4"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/veo3/extend", response_model=Veo3ExtendResponse)
async def extend_veo3_video(request: Veo3ExtendRequest):
    """
    Extend a previously generated Veo 3.1 video using Gemini API.
    This uses the correct implementation with 'source' parameter (not 'video').
    Can extend videos 7 seconds at a time, up to 20 times (148 seconds total).
    """
    try:
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 not configured. Set GOOGLE_CLOUD_PROJECT_ID in .env"
            )
        
        print(f"[API] 🎬 Extending Veo 3 video via Gemini API")
        print(f"[API]   Base job ID: {request.base_job_id}")
        print(f"[API]   Extension: {request.extension_seconds}s, max {request.max_extensions} extensions")
        
        # Use the Gemini API extension method
        result = await veo3_service.extend_video_gemini_api(
            base_job_id=request.base_job_id,
            extension_seconds=request.extension_seconds,
            max_extensions=request.max_extensions
        )
        
        return Veo3ExtendResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ❌ Extension error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/veo3/generate-with-context", response_model=Veo3GenerateWithContextResponse)
async def generate_veo3_video_with_context(
    request: Veo3GenerateWithContextRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Generate a Veo video using Mem0 context for script generation.
    
    Flow:
    1. Get user context from Mem0
    2. Generate video script based on context using OpenAI/Claude
    3. Save script to Mem0 for future inspiration
    4. Generate Veo video with the script
    5. Handle extensions (if requested) and wait for completion
    6. Return final video
    
    The script is saved to the user's memory so it can be used later for inspiration.
    """
    try:
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 not configured. Set GOOGLE_CLOUD_PROJECT_ID in your .env file"
            )
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI service not available. Set OPENAI_API_KEY in your .env file"
            )
        
        # Get user ID
        user_id = current_user.email.lower().strip() if current_user else "anonymous_user"
        if not current_user:
            print(f"[API] ⚠️ Generating video without authentication (using anonymous user)")
        
        print(f"[API] 🎬 Generating Veo video with context for user: {user_id}")
        print(f"[API] Topic: {request.topic}")
        print(f"[API] Duration: {request.duration}s, Max extensions: {request.max_extensions}")
        
        # Step 1: Get user context from Mem0
        user_context = ""
        if memory_service.is_available() and current_user:
            print(f"[API] 📋 Retrieving user context from Mem0...")
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user background profession industry work expertise content topics brand company business documents {request.topic}",
                user_email=user_id
            )
            
            if user_context:
                print(f"[API] ✓ Retrieved context ({len(user_context)} chars)")
                print(f"[API] Context preview: {user_context[:300]}...")
            else:
                print(f"[API] ⚠️ No context found in Mem0 for user")
        else:
            print(f"[API] ⚠️ Mem0 not available or user not authenticated - using generic script")
        
        # Step 2: Generate video script based on context
        print(f"[API] ✍️ Generating video script from context...")
        
        # Build prompt for script generation
        context_section = ""
        if user_context:
            context_section = f"\n\nUSER CONTEXT (from Mem0):\n{user_context}\n\nUse this context to create a personalized, relevant video script that aligns with the user's brand and expertise."
        
        script_prompt = f"""Create a detailed video script for a {request.duration}-second marketing/educational video about: {request.topic}

{context_section}

Requirements:
- Create a clear, engaging narrative suitable for Veo 3 video generation
- Include specific visual descriptions that Veo can understand
- Focus on professional, high-quality content
- Make it relevant to the user's context if provided
- Structure: opening hook, main content, closing
- Total duration: {request.duration} seconds

Return a detailed video script/prompt that can be used directly with Veo 3 for video generation."""
        
        # Generate script using Bedrock/Claude (preferred) or fallback to OpenAI
        llm_provider = request.llm_provider or "bedrock"
        generated_script = None
        
        # Try Bedrock/Claude first (preferred) - uses Claude Sonnet 4.5
        if llm_provider in ["bedrock", "claude"] and bedrock_service.is_available():
            try:
                print(f"[API] Using AWS Bedrock (Claude Sonnet 4.5) for script generation...")
                generated_script = await bedrock_service.generate_script(
                    prompt=script_prompt,
                    max_tokens=2000,
                    temperature=0.7
                )
                if generated_script:
                    print(f"[API] ✓ Script generated with Bedrock Claude Sonnet 4.5 ({len(generated_script)} chars)")
            except Exception as bedrock_error:
                print(f"[API] ⚠️ Bedrock generation failed, trying fallback: {bedrock_error}")
                generated_script = None
        
        # Fallback to Anthropic Claude API (if available)
        if not generated_script and llm_provider in ["claude", "bedrock"] and openai_service and openai_service.claude_available:
            try:
                print(f"[API] 🤖 Trying Anthropic Claude API as fallback...")
                generated_script = await openai_service.generate_text_with_claude(
                    prompt=script_prompt,
                    system_message="You are an expert video script writer who creates detailed, visual video scripts for AI video generation. Create scripts that are clear, engaging, and optimized for Veo 3 video generation.",
                    max_tokens=1000,
                    temperature=0.7
                )
                if generated_script:
                    llm_used = "Anthropic Claude API"
                    print(f"[API] ✅ Script generated with {llm_used} ({len(generated_script)} chars)")
            except Exception as claude_error:
                print(f"[API] ⚠️ Claude API generation failed, falling back to OpenAI: {claude_error}")
        
        # Final fallback to OpenAI
        if not generated_script and openai_service:
            try:
                print(f"[API] 🤖 Using OpenAI ({openai_service.model}) for script generation (fallback)...")
                script_response = await openai_service.client.chat.completions.create(
                    model=openai_service.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert video script writer who creates detailed, visual video scripts for AI video generation. Create scripts that are clear, engaging, and optimized for Veo 3 video generation."
                        },
                        {
                            "role": "user",
                            "content": script_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                generated_script = script_response.choices[0].message.content.strip()
                llm_used = f"OpenAI ({openai_service.model})"
                print(f"[API] ✅ Script generated with {llm_used} ({len(generated_script)} chars)")
            except Exception as script_error:
                print(f"[API] ⚠️ Script generation failed: {script_error}")
                # Fallback to simple prompt
                generated_script = f"Create a professional marketing video about {request.topic}. Show engaging visuals, clear messaging, and high-quality production values suitable for social media."
        
        if not generated_script:
            # Ultimate fallback
            generated_script = f"Create a professional marketing video about {request.topic}. Show engaging visuals, clear messaging, and high-quality production values suitable for social media."
        
        # Step 3: Save script to Mem0 for future inspiration
        script_saved = False
        if memory_service.is_available() and current_user and generated_script:
            try:
                print(f"[API] 💾 Saving script to Mem0 for future inspiration...")
                script_memory_text = f"""VIDEO SCRIPT GENERATED: {request.topic}

Script created for Veo 3 video generation:
{generated_script}

Topic: {request.topic}
Duration: {request.duration} seconds
Generated at: {datetime.now().isoformat()}

This script can be used as inspiration for future video content."""
                
                result = await memory_service.append_to_unified_brand_context(
                    user_id=user_id,
                    new_content=script_memory_text,
                    content_type="video_script"
                )
                
                if result:
                    script_saved = True
                    print(f"[API] ✓ Script saved to Mem0 memory (resource_id: {result.get('resource_id')})")
                else:
                    print(f"[API] ⚠️ Failed to save script to Mem0")
            except Exception as save_error:
                print(f"[API] ⚠️ Error saving script to Mem0: {save_error}")
        
        # Step 4: Generate Veo video with the script
        print(f"[API] 🎥 Generating Veo video with script...")
        
        # Ensure duration is valid (4, 6, or 8 seconds for initial generation)
        valid_durations = [4, 6, 8]
        if request.duration not in valid_durations:
            duration = min(valid_durations, key=lambda x: abs(x - request.duration))
            print(f"[API] ⚠️ Adjusted duration from {request.duration}s to {duration}s (Veo 3 supports 4, 6, or 8s initially)")
        else:
            duration = request.duration
        
        # Generate video
        video_result = await veo3_service.generate_video(
            prompt=generated_script,
            duration=duration,
            resolution=request.resolution
        )
        
        job_id = video_result.get("job_id")
        print(f"[API] ✓ Video generation started: {job_id[:50]}...")
        
        # Step 5: Handle extensions and wait for completion if requested
        video_url = None
        extensions_completed = 0
        final_duration = duration
        
        if request.wait_for_completion:
            print(f"[API] ⏳ Waiting for video to complete...")
            try:
                if request.max_extensions > 0:
                    print(f"[API] Will wait for {request.max_extensions} extensions to complete...")
                
                final_result = await wait_for_video_completion_with_extensions(
                    veo3_service=veo3_service,
                    job_id=job_id,
                    max_extensions=request.max_extensions,
                    check_interval=10,
                    max_wait_time=1800,  # 30 minutes
                    initial_duration=duration
                )
                
                video_url = final_result.get("video_url")
                extensions_completed = final_result.get("extensions_completed", 0)
                final_duration = final_result.get("final_duration", duration)
                final_job_id = final_result.get("job_id", job_id)  # Get final job_id (may have changed with extensions)
                
                print(f"[API] ✅ Video generation complete!")
                print(f"[API] Final duration: {final_duration}s ({extensions_completed} extensions)")
                
                # Step 6: Videos are automatically stored in GCS (configured via VEO3_STORAGE_URI)
                # The video_url returned from Veo will be a GCS URI or download endpoint
                if video_url:
                    print(f"[API] ✅ Video stored in GCS (via VEO3_STORAGE_URI)")
                
            except Exception as wait_error:
                print(f"[API] ⚠️ Error waiting for completion: {wait_error}")
                # Return job_id so user can poll status manually
                video_url = None
        
        return Veo3GenerateWithContextResponse(
            job_id=job_id,
            status="completed" if video_url else "in_progress",
            video_url=video_url,
            progress=100 if video_url else 0,
            model=video_result.get("model", "veo-3"),
            script=generated_script,
            script_saved=script_saved,
            extensions_completed=extensions_completed,
            final_duration=final_duration
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] ERROR Veo generation with context failed: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/image/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest):
    """
    Generate an image using Google Imagen via Vertex AI (nanobanana/gemini-3-pro-image)
    """
    try:
        # DALL-E support has been removed - only Imagen via Vertex AI is supported
        if request.model.startswith("dall-e"):
            raise HTTPException(
                status_code=400,
                detail="DALL-E is no longer supported. Please use 'nanobanana' or 'gemini-3-pro-image' model."
            )
        
        result = await image_generation_service.generate_image(
            prompt=request.prompt,
            model=request.model,
            size=request.size,
            quality=request.quality,
            style=request.style,
            n=request.n,
            aspect_ratio=request.aspect_ratio
        )
        
        print(f"[API] Image generation result keys: {list(result.keys())}")
        print(f"[API] Image URL present: {bool(result.get('image_url'))}")
        print(f"[API] Image base64 present: {bool(result.get('image_base64'))}")
        
        return ImageGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/marketing-post/create", response_model=MarketingPostResponse)
async def create_marketing_post(
    request: MarketingPostRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a complete marketing post with image and caption using nanobanana.
    Uses Hyperspell memories for personalized content based on logged-in user's data.
    Generates an image, creates engaging caption, and optionally posts to Instagram.
    
    Features:
    - First post is automatically an intro post about the company
    - All posts are saved to Hyperspell memory
    - Future posts use performance data from previous posts
    """
    try:
        # Use user email if authenticated, otherwise use a default/anonymous identifier
        if current_user:
            user_id = current_user.email
        else:
            # For unauthenticated users, use a default identifier
            # In production, you might want to require authentication
            user_id = "anonymous_user"
            print(f"[API] ⚠️ Creating post without authentication (using anonymous user)")
        
        print(f"[API] 📸 Creating marketing post for topic: {request.topic} (User: {user_id})")
        
        # First post check disabled - removed to prevent overwriting user-generated scripts
        # is_first = False
        # if memory_service.is_available():
        #     is_first = await is_first_post(memory_service, user_id)
        is_first = False  # Always set to False to disable first post logic
        
        # Get user context from Memory (company info, brand context)
        user_context = ""
        post_performance_context = ""
        
        if memory_service.is_available():
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"company information business brand products services {request.brand_context or ''}",
                user_email=user_id if current_user else None
            )
            
            # Get post performance context (previous posts and their performance)
            post_performance_context = await get_post_performance_context(
                memory_service=memory_service,
                user_id=user_id
            )
        
        # First post topic modification disabled - removed to prevent overwriting user-generated scripts
        # original_topic = request.topic
        # if is_first:
        #     ... (removed first post logic)
        
        # Step 1: Generate image prompt if not provided
        image_prompt = request.image_prompt
        if not image_prompt and openai_service:
            print(f"[API] Generating image prompt from topic...")
            try:
                # Build prompt with user context if available
                context_section = ""
                if user_context:
                    context_section = f"\n\nUSER CONTEXT (from uploaded documents):\n{user_context}\n\nUse this context to make the image more personalized and relevant."
                
                image_prompt_prompt = f"""Create a detailed, ultra high-quality, photorealistic image prompt for a marketing post about: {request.topic}

{f"Brand context: {request.brand_context}" if request.brand_context else ""}
{context_section}

Requirements:
- Ultra high quality, 8K resolution, professional photography
- Sharp focus, crisp details, perfect text rendering
- Readable text if text is included
- High contrast, vibrant colors, professional lighting
- Studio quality, marketing quality, social media ready
- Photorealistic, no AI artifacts, no blurriness
- Professional and high-quality
- Suitable for social media (Instagram/LinkedIn)
- Visually appealing and eye-catching
- Relevant to the topic
- Personalized based on user context if provided

Return ONLY the image prompt text, no additional text."""
                
                # Try Claude first if available, fallback to OpenAI
                image_prompt_text = None
                if openai_service.claude_available:
                    try:
                        image_prompt_text = await openai_service.generate_text_with_claude(
                            prompt=image_prompt_prompt,
                            system_message="You are an expert at creating detailed, visual image prompts for marketing posts. Create prompts that are photorealistic, engaging, and suitable for social media.",
                            max_tokens=200,
                            temperature=0.7
                        )
                        if image_prompt_text:
                            print(f"[API] ✓ Generated image prompt with Claude: {image_prompt_text[:100]}...")
                    except Exception as claude_error:
                        print(f"[API] ⚠️ Claude generation failed, falling back to OpenAI: {claude_error}")
                
                # Fallback to OpenAI if Claude not available or failed
                if not image_prompt_text:
                    prompt_generation = await openai_service.client.chat.completions.create(
                        model=openai_service.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert at creating detailed, visual image prompts for marketing posts. Create prompts that are photorealistic, engaging, and suitable for social media."
                            },
                            {
                                "role": "user",
                                "content": image_prompt_prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    image_prompt_text = prompt_generation.choices[0].message.content.strip()
                    print(f"[API] ✓ Generated image prompt with OpenAI: {image_prompt_text[:100]}...")
                
                image_prompt = image_prompt_text
            except Exception as e:
                print(f"[API] ⚠️ Failed to generate image prompt, using topic directly: {e}")
                image_prompt = f"Ultra high quality, photorealistic, professional photography, 8K resolution, sharp focus, crisp details, perfect text rendering, readable text, high contrast, vibrant colors, professional lighting, studio quality, marketing quality, social media ready: Professional marketing image about {request.topic}"
        elif not image_prompt:
            image_prompt = f"Professional marketing image about {request.topic}, high quality, social media style"
        
        # Step 2: Generate image using Google Imagen via Vertex AI
        print(f"[API] 🎨 Generating image with Google Imagen...")
        image_result = None
        
        try:
            # Use Imagen for image generation
            if image_generation_service and image_generation_service.project_id:
                # Map aspect ratios to sizes
                aspect_ratio = request.aspect_ratio or "1:1"
                if aspect_ratio == "16:9":
                    size = "1792x1024"
                elif aspect_ratio == "9:16":
                    size = "1024x1792"
                else:
                    size = "1024x1024"
                
                image_result = await image_generation_service.generate_image(
                    prompt=image_prompt,
                    model="imagen-4.0-generate-001",  # Use Imagen 4
                    size=size,
                    quality="high"
                )
                
                if image_result and image_result.get("image_base64"):
                    print(f"[API] ✓ Image generated with Google Imagen")
                else:
                    print(f"[API] ⚠️ Imagen generation returned no image")
                    image_result = None
            else:
                print(f"[API] ⚠️ Image generation service not available")
        except Exception as e:
            print(f"[API] ⚠️ Error generating image with Imagen: {e}")
            import traceback
            traceback.print_exc()
            image_result = None
        
        # Fallback: if image generation failed, create placeholder
        if not image_result:
            print(f"[API] ⚠️ Image generation failed, using placeholder")
            image_result = {
                "image_base64": None,
                "image_url": None,
                "revised_prompt": image_prompt,
                "model": "placeholder",
                "size": "1024x1024",
                "quality": "high",
                "aspect_ratio": request.aspect_ratio or "1:1"
            }
        
        # Step 4: Generate marketing caption
        print(f"[API] ✍️ Generating marketing caption...")
        caption = ""
        hashtags = []
        
        if openai_service:
            try:
                style_guidance = {
                    "engaging": "Create an engaging, attention-grabbing caption that hooks the reader",
                    "professional": "Create a professional, polished caption suitable for LinkedIn or business accounts",
                    "casual": "Create a casual, friendly caption that feels authentic and relatable",
                    "educational": "Create an educational caption that teaches something valuable"
                }
                style_instruction = style_guidance.get(request.caption_style or "engaging", style_guidance["engaging"])
                
                # Build caption prompt with user context and post performance context
                context_section = ""
                if user_context:
                    context_section = f"\n\nUSER CONTEXT (from uploaded documents - use this to personalize the caption):\n{user_context}\n\nMake the caption feel authentic and personalized based on this context."
                
                performance_section = ""
                if post_performance_context:
                    performance_section = f"\n\nPOST PERFORMANCE CONTEXT (learn from previous posts):\n{post_performance_context}\n\nUse insights from high-performing posts to create better content. Avoid approaches that didn't work well."
                
                # First post instruction disabled - removed to prevent overwriting user-generated scripts
                # first_post_instruction = ""
                # if is_first:
                #     ... (removed first post instruction)
                
                caption_prompt = f"""Create a marketing caption for a social media post about: {request.topic}

{f"Brand context: {request.brand_context}" if request.brand_context else ""}
{context_section}
{performance_section}

Style: {style_instruction}
Length: 2-4 sentences (concise but engaging)
Tone: {request.caption_style or "engaging"}

IMPORTANT: Do NOT include hashtags in the caption. Return only the caption text without any hashtags."""
                
                # Try Claude first if available, fallback to OpenAI
                generated_text = None
                if openai_service.claude_available:
                    try:
                        generated_text = await openai_service.generate_text_with_claude(
                            prompt=caption_prompt,
                            system_message="You are an expert social media marketer who creates compelling, engaging captions that drive engagement and conversions.",
                            max_tokens=300,
                            temperature=0.8
                        )
                        if generated_text:
                            print(f"[API] ✓ Generated caption with Claude ({len(generated_text)} chars)")
                    except Exception as claude_error:
                        print(f"[API] ⚠️ Claude generation failed, falling back to OpenAI: {claude_error}")
                
                # Fallback to OpenAI if Claude not available or failed
                if not generated_text:
                    caption_response = await openai_service.client.chat.completions.create(
                        model=openai_service.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert social media marketer who creates compelling, engaging captions that drive engagement and conversions."
                            },
                            {
                                "role": "user",
                                "content": caption_prompt
                            }
                        ],
                        temperature=0.8,
                        max_tokens=300
                    )
                    generated_text = caption_response.choices[0].message.content.strip()
                    print(f"[API] ✓ Generated caption with OpenAI ({len(generated_text)} chars)")
                
                # Caption should not contain hashtags (we'll generate them separately)
                caption = generated_text.strip()
                # Remove any hashtags that might have been included despite instructions
                caption = re.sub(r'#\w+\s*', '', caption).strip()
                
                print(f"[API] ✓ Caption generated ({len(caption)} chars)")
            except Exception as e:
                print(f"[API] ⚠️ Failed to generate caption with AI: {e}")
                caption = f"Check out our latest content about {request.topic}! 🚀"
        else:
            # Fallback caption
            caption = f"Exciting news about {request.topic}! Stay tuned for more updates. 🎉"
        
        # Step 4.5: Generate hashtags separately after caption is created
        hashtags = []
        if request.include_hashtags and openai_service:
            print(f"[API] #️⃣ Generating relevant hashtags for platform: {request.platform or 'instagram'}...")
            try:
                # Determine hashtag count based on platform
                platform = (request.platform or "instagram").lower()
                if platform == "linkedin":
                    hashtag_count = "3-5"  # LinkedIn uses fewer hashtags
                    platform_guidance = "LinkedIn hashtags should be professional, industry-specific, and relevant to B2B audiences. Focus on business, industry, and professional development tags."
                else:  # Instagram (default)
                    hashtag_count = "10-20"  # Instagram uses more hashtags
                    platform_guidance = "Instagram hashtags should be a mix of popular, niche, and branded tags. Include broad reach tags, specific niche tags, and community tags."
                
                # Build hashtag generation prompt
                hashtag_context = ""
                if user_context:
                    hashtag_context = f"\n\nUSER CONTEXT (use this to personalize hashtags):\n{user_context}\n"
                
                hashtag_prompt = f"""Generate relevant hashtags for a social media post.

Topic: {request.topic}
Caption: {caption}
Platform: {platform}
{hashtag_context}

{platform_guidance}

Requirements:
- Generate {hashtag_count} relevant hashtags
- Hashtags should be directly related to the topic and caption content
- Mix of broad and niche hashtags
- No hashtag symbols (#) in your response
- Return only the hashtag words, separated by commas
- Each hashtag should be a single word or phrase (no spaces, use camelCase for phrases)
- Make them specific and relevant to the content

Example format: marketing, business, entrepreneurship, startup, innovation, tech, digitalmarketing, socialmedia, branding, growth

Return only the hashtags, one per line or comma-separated."""
                
                # Generate hashtags using AI
                generated_hashtags = None
                if openai_service.claude_available:
                    try:
                        generated_hashtags = await openai_service.generate_text_with_claude(
                            prompt=hashtag_prompt,
                            system_message="You are an expert social media marketer who creates highly relevant, engaging hashtags for social media posts.",
                            max_tokens=200,
                            temperature=0.7
                        )
                        if generated_hashtags:
                            print(f"[API] ✓ Generated hashtags with Claude")
                    except Exception as claude_error:
                        print(f"[API] ⚠️ Claude hashtag generation failed, falling back to OpenAI: {claude_error}")
                
                # Fallback to OpenAI if Claude not available or failed
                if not generated_hashtags:
                    hashtag_response = await openai_service.client.chat.completions.create(
                        model=openai_service.model,
                        messages=[
                            {
                                "role": "system",
                                "content": "You are an expert social media marketer who creates highly relevant, engaging hashtags for social media posts."
                            },
                            {
                                "role": "user",
                                "content": hashtag_prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=200
                    )
                    generated_hashtags = hashtag_response.choices[0].message.content.strip()
                    print(f"[API] ✓ Generated hashtags with OpenAI")
                
                # Parse hashtags from response
                if generated_hashtags:
                    # Remove any # symbols and split by commas or newlines
                    hashtag_text = generated_hashtags.replace('#', '').strip()
                    # Split by comma or newline
                    hashtag_list = [tag.strip() for tag in re.split(r'[,\n]', hashtag_text) if tag.strip()]
                    # Clean up hashtags (remove spaces, convert to lowercase)
                    hashtags = [tag.lower().replace(' ', '') for tag in hashtag_list if tag]
                    # Limit hashtags based on platform
                    if platform == "linkedin":
                        hashtags = hashtags[:5]  # Max 5 for LinkedIn
                    else:
                        hashtags = hashtags[:20]  # Max 20 for Instagram
                    
                    print(f"[API] ✓ Generated {len(hashtags)} relevant hashtags: {', '.join(hashtags[:5])}...")
                else:
                    # Fallback hashtags
                    topic_words = request.topic.lower().split()
                    hashtags = [word.replace(' ', '') for word in topic_words[:3]]
                    if platform == "linkedin":
                        hashtags.extend(["business", "professional"])
                    else:
                        hashtags.extend(["marketing", "business", "entrepreneurship"])
                    print(f"[API] ⚠️ Using fallback hashtags")
            except Exception as hashtag_error:
                print(f"[API] ⚠️ Failed to generate hashtags with AI: {hashtag_error}")
                # Fallback hashtags
                topic_words = request.topic.lower().split()
                hashtags = [word.replace(' ', '') for word in topic_words[:3]]
                platform = (request.platform or "instagram").lower()
                if platform == "linkedin":
                    hashtags.extend(["business", "professional"])
                else:
                    hashtags.extend(["marketing", "business", "entrepreneurship"])
        elif request.include_hashtags:
            # Fallback if AI service not available
            topic_words = request.topic.lower().split()
            hashtags = [word.replace(' ', '') for word in topic_words[:3]]
            platform = (request.platform or "instagram").lower()
            if platform == "linkedin":
                hashtags.extend(["business", "professional"])
            else:
                hashtags.extend(["marketing", "business", "entrepreneurship"])
        
        # Combine caption and hashtags
        full_caption = caption
        if hashtags:
            hashtag_string = ' '.join([f"#{tag}" for tag in hashtags])
            full_caption = f"{caption}\n\n{hashtag_string}"
        
        # Step 5: Save post to Hyperspell memory (for all users, including anonymous)
        if memory_service.is_available():
            print(f"[API] 💾 Saving post to Hyperspell memory (User: {user_id})...")
            post_data = {
                "topic": request.topic,
                "caption": caption,
                "hashtags": hashtags,
                "image_prompt": image_prompt,
                "image_url": image_result.get("image_url"),  # Store file URL (not base64)
                "created_at": datetime.now().isoformat(),
                "post_id": None,  # Will be updated if posted
                "post_url": None,  # Will be updated if posted
                "is_first_post": is_first,
                "performance": {},  # Will be updated when performance data is available
                "caption_style": request.caption_style or "engaging",
                "aspect_ratio": request.aspect_ratio or "1:1"
            }
            
            resource_id = await save_post_to_memory(
                memory_service=memory_service,
                user_id=user_id,
                post_data=post_data,
                collection="user_posts"
            )
            
            if resource_id:
                print(f"[API] ✓ Post saved to memory: {resource_id}")
            else:
                print(f"[API] ⚠️ Failed to save post to memory")
        else:
            print(f"[API] ⚠️ Memory service not available, post not saved to memory")
        
        # Step 6: Optionally auto-post (currently disabled - returns image for manual posting)
        post_id = None
        post_url = None
        post_error = None
        
        if request.auto_post:
            print(f"[API] 📱 Auto-posting requested but not implemented for images")
            post_error = "Auto-posting images is not yet implemented. Please download the image and post manually."
        
        # Update post in memory if it was posted
        if post_id and memory_service.is_available():
            # Note: In a real implementation, you'd update the existing memory
            # For now, we save it initially and could update later when performance data comes in
            pass
        
        # Get full URL for image (prepend API base URL if relative)
        image_url = image_result.get("image_url")
        if image_url and not image_url.startswith("http"):
            # For local files, return the path that will be served by FastAPI
            # Frontend should prepend API_URL
            pass  # Keep as relative path, frontend will handle
        
        # Also include base64 in response for immediate display (optional)
        image_base64 = image_result.get("image_base64")
        
        response_data = {
            "success": True,
            "topic": request.topic,
            "image_url": image_url,
            "image_base64": image_base64,  # Include for immediate display
            "image_prompt": image_prompt,
            "caption": caption,
            "hashtags": hashtags if request.include_hashtags else None,
            "full_caption": full_caption,
            "post_id": post_id,
            "post_url": post_url,
            "error": post_error,
            "is_first_post": is_first
        }
        
        print(f"[API] Response data - image_url present: {bool(response_data['image_url'])}")
        print(f"[API] Response data - image_base64 present: {bool(response_data['image_base64'])}")
        print(f"[API] Response data keys: {list(response_data.keys())}")
        
        return MarketingPostResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Marketing post creation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/aigis-marketing/generate", response_model=AigisMarketingResponse)
async def generate_aigis_marketing_content(
    request: AigisMarketingRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Generate content for Aigis Marketing in 5 minutes (instead of 2-3 hours).
    
    Process:
    1. Brainstorm topics
    2. Outline key points
    3. Write draft
    4. Review and edit
    5. Prepare for posting (image, excerpt, tags)
    """
    try:
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] 📝 Generating Aigis Marketing content for topic: {request.topic} (Style: {request.style}, User: {user_id})")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required. Please set OPENAI_API_KEY in your .env file."
            )
        
        # Get user context if available
        user_context = ""
        if memory_service.is_available():
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user content style preferences brand context {request.topic}",
                user_email=user_id if current_user else None
            )
        
        # Build style-specific instructions
        style_instructions = {
            "thought-leadership": """Create educational, evidence-based content for health tech and healthcare professionals.
            Focus on teaching and providing education on evidence generation for value creation.
            Tone: Professional, authoritative, educational, easy to understand (ELI5 style when appropriate).
            Structure: Framework-based, structured, concise with clear call to action.""",
            "company-content": """Create brand-focused content for company marketing.
            Tone: Professional, engaging, aligned with company values.
            Structure: Clear value proposition, benefits, call to action.""",
            "personal-blog": """Create personal insights and experiences content.
            Tone: Conversational, authentic, relatable.
            Structure: Story-driven, personal anecdotes, lessons learned."""
        }
        
        style_guide = style_instructions.get(request.style, style_instructions["thought-leadership"])
        
        # Step 1-3: Generate outline and draft in one call
        content_prompt = f"""You are an expert content creator helping create high-quality {request.style} content in 5 minutes.

TOPIC: {request.topic}

STYLE GUIDE:
{style_guide}

USER CONTEXT:
{user_context if user_context else "No specific user context available."}

TASK: Create a complete article following these steps:

1. OUTLINE: Provide 5-7 key points/takeaways as a bulleted list
2. DRAFT: Write a complete, well-structured article (800-1200 words) that:
   - Follows the outline
   - Is engaging and easy to understand
   - Includes a clear call to action
   - Uses the appropriate tone for {request.style}
   - Is suitable for LinkedIn and blog posting

3. IMAGE PROMPT: Suggest an appropriate image description for this article
4. EXCERPT: Create a 2-3 sentence excerpt for blog preview (150-200 characters)
5. TAGS: Suggest 5-7 relevant tags/hashtags

Return your response in this JSON format:
{{
  "outline": ["point 1", "point 2", ...],
  "draft": "full article text here...",
  "imagePrompt": "description of image to use",
  "excerpt": "brief excerpt for blog",
  "tags": ["tag1", "tag2", ...]
}}"""
        
        print(f"[API] 🤖 Generating content with OpenAI...")
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content creator specializing in creating high-quality, engaging content for LinkedIn and blogs. You help professionals create thought leadership content efficiently."
                },
                {
                    "role": "user",
                    "content": content_prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        content_data = json.loads(response.choices[0].message.content)
        
        print(f"[API] ✓ Content generated successfully")
        
        return AigisMarketingResponse(
            success=True,
            outline=content_data.get("outline", []),
            draft=content_data.get("draft", ""),
            imagePrompt=content_data.get("imagePrompt", ""),
            excerpt=content_data.get("excerpt", ""),
            tags=content_data.get("tags", []),
            content=content_data.get("draft", "")
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error generating Aigis Marketing content: {e}")
        return AigisMarketingResponse(
            success=False,
            error=f"Failed to generate content: {str(e)}"
        )


@app.post("/api/aigis-marketing/brainstorm")
async def brainstorm_topics(
    request: AigisMarketingRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Step 1: Brainstorm topic ideas based on the initial topic.
    """
    try:
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] 💡 Brainstorming topics for: {request.topic}")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required."
            )
        
        # Get user context
        user_context = ""
        if memory_service.is_available():
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user content style preferences brand context {request.topic}",
                user_email=user_id if current_user else None
            )
        
        prompt = f"""Based on this topic: "{request.topic}"

Generate 5-7 variations or related topic ideas that would make great content. Each should be:
- Specific and actionable
- Engaging for the target audience
- Suitable for LinkedIn and blog posts

Return a JSON object with a "topics" array of topic strings.

User context: {user_context if user_context else "No specific context available."}"""
        
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content strategist who helps create engaging topic ideas for professional content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        topics = data.get("topics", [])
        
        return {
            "success": True,
            "topics": topics
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error brainstorming: {e}")
        return {
            "success": False,
            "error": f"Failed to brainstorm topics: {str(e)}"
        }


@app.post("/api/aigis-marketing/outline")
async def generate_outline(
    request: AigisMarketingRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Step 2: Generate outline with key points for the selected topic.
    """
    try:
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] 📋 Generating outline for: {request.topic}")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required."
            )
        
        # Get user context
        user_context = ""
        if memory_service.is_available():
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user content style preferences brand context {request.topic}",
                user_email=user_id if current_user else None
            )
        
        style_instructions = {
            "thought-leadership": "Professional, authoritative, educational, easy to understand.",
            "company-content": "Professional, engaging, aligned with company values.",
            "personal-blog": "Conversational, authentic, relatable."
        }
        style_guide = style_instructions.get(request.style, style_instructions["thought-leadership"])
        
        prompt = f"""Create a detailed outline for an article on: "{request.topic}"

Style: {style_guide}

Generate 5-7 key points/takeaways that will form the structure of the article. Each point should be:
- Clear and specific
- Actionable or insightful
- Flow logically from one to the next

Return a JSON object with an "outline" array of point strings.

User context: {user_context if user_context else "No specific context available."}"""
        
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content creator who creates well-structured outlines for professional articles."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        outline = data.get("outline", [])
        
        return {
            "success": True,
            "outline": outline
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error generating outline: {e}")
        return {
            "success": False,
            "error": f"Failed to generate outline: {str(e)}"
        }


@app.post("/api/aigis-marketing/draft")
async def generate_draft(
    request: dict,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Step 3: Generate full draft article based on the outline.
    """
    try:
        topic = request.get("topic", "")
        outline = request.get("outline", [])
        style = request.get("style", "thought-leadership")
        
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] ✍️ Generating draft for: {topic}")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required."
            )
        
        # Get user context
        user_context = ""
        if memory_service.is_available():
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user content style preferences brand context {topic}",
                user_email=user_id if current_user else None
            )
        
        style_instructions = {
            "thought-leadership": """Professional, authoritative, educational, easy to understand (ELI5 style when appropriate).
            Structure: Framework-based, structured, concise with clear call to action.""",
            "company-content": """Professional, engaging, aligned with company values.
            Structure: Clear value proposition, benefits, call to action.""",
            "personal-blog": """Conversational, authentic, relatable.
            Structure: Story-driven, personal anecdotes, lessons learned."""
        }
        style_guide = style_instructions.get(style, style_instructions["thought-leadership"])
        
        outline_text = "\n".join([f"{i+1}. {point}" for i, point in enumerate(outline)])
        
        prompt = f"""Write a complete, well-structured article (800-1200 words) based on this outline:

TOPIC: {topic}

OUTLINE:
{outline_text}

STYLE GUIDE:
{style_guide}

Requirements:
- Follow the outline structure
- Be engaging and easy to understand
- Include a clear call to action
- Use the appropriate tone for {style}
- Suitable for LinkedIn and blog posting
- Also generate:
  * An imagePrompt: description of an appropriate image
  * An excerpt: 2-3 sentence excerpt for blog preview (150-200 characters)
  * Tags: 5-7 relevant tags/hashtags

Return a JSON object with:
- "draft": the full article text
- "imagePrompt": image description
- "excerpt": blog preview excerpt
- "tags": array of tags

User context: {user_context if user_context else "No specific context available."}"""
        
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content creator specializing in creating high-quality, engaging content for LinkedIn and blogs."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        
        return {
            "success": True,
            "draft": data.get("draft", ""),
            "imagePrompt": data.get("imagePrompt", ""),
            "excerpt": data.get("excerpt", ""),
            "tags": data.get("tags", [])
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error generating draft: {e}")
        return {
            "success": False,
            "error": f"Failed to generate draft: {str(e)}"
        }


@app.post("/api/aigis-marketing/suggestions", response_model=AigisMarketingSuggestionsResponse)
async def get_aigis_marketing_suggestions(
    request: AigisMarketingSuggestionsRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Generate contextual topic suggestions and recommendations based on user's Hyperspell context.
    Analyzes user's context (e.g., medical youtube channel, student, marketer) and suggests relevant content types.
    """
    try:
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] 💡 Generating contextual suggestions for user: {user_id}")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required. Please set OPENAI_API_KEY in your .env file."
            )
        
        # Get comprehensive user context from Memory (S3 + Mem0)
        user_context = ""
        if memory_service.is_available() and current_user:
            user_context = await get_memory_context(
                memory_service=memory_service,
                query=f"user background profession industry work expertise content topics brand company business documents uploaded",
                user_email=user_id
            )
            print(f"[API] 📋 Retrieved user context length: {len(user_context)} characters")
            if user_context:
                print(f"[API] 📋 User context preview: {user_context[:500]}...")
            else:
                print(f"[API] ⚠️ No user context retrieved from Memory - will use generic suggestions")
        elif not current_user:
            print(f"[API] ⚠️ No authenticated user - using generic suggestions")
        
        # Build the prompt based on whether we have context
        if user_context and user_context.strip():
            suggestions_prompt = f"""Analyze this user context step by step:

USER CONTEXT:
{user_context}

STEP 1: Extract and list ONLY the topics/industries/professions explicitly mentioned in the context above. List them here:
- [List each topic you find]

STEP 2: Generate 5-7 content suggestions that match ONLY the topics from STEP 1.

CRITICAL: 
- If healthcare/medical/health/epidemiology/healthtech is NOT in your STEP 1 list → DO NOT include ANY healthcare suggestions
- Only suggest content for topics actually found in STEP 1
- DO NOT add topics not in STEP 1
- Be strict: if it's not explicitly mentioned, don't include it

Welcome message: Mention which specific topics from the context informed these suggestions.

Return JSON:
{{
  "welcomeMessage": "Brief explanation mentioning specific topics from context",
  "suggestions": ["Suggestion 1", "Suggestion 2", ...]
}}"""
        else:
            # No context available - provide generic suggestions
            suggestions_prompt = """You are an expert content strategist. The user has no specific context available yet.

Generate 5-7 general, versatile content creation suggestions that work for most professionals:
- Convert expertise into educational content
- Share insights and lessons learned
- Create how-to guides based on experience
- Write thought leadership pieces
- Document processes and frameworks
- Share case studies or examples
- Create informative articles

Also provide a brief welcome message explaining they can upload documents or provide more context for personalized suggestions.

Return your response in this JSON format:
{
  "welcomeMessage": "Welcome message mentioning they can provide more context",
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3", "Suggestion 4", "Suggestion 5"]
}"""
        
        print(f"[API] 🤖 Analyzing user context and generating personalized suggestions...")
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a content strategist who provides suggestions based ONLY on what's explicitly stated in the user's context. You do not add topics not mentioned. You do not assume or infer. You strictly match suggestions to what's in the provided context."
                },
                {
                    "role": "user",
                    "content": suggestions_prompt
                }
            ],
            temperature=0.8,
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        
        suggestions_data = json.loads(response.choices[0].message.content)
        suggestions = suggestions_data.get("suggestions", [])
        welcome_message = suggestions_data.get("welcomeMessage", "Here are some content ideas tailored for you:")
        
        print(f"[API] ✓ Generated {len(suggestions)} personalized suggestions")
        
        return AigisMarketingSuggestionsResponse(
            success=True,
            suggestions=suggestions,
            welcomeMessage=welcome_message
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error generating suggestions: {e}")
        return AigisMarketingSuggestionsResponse(
            success=False,
            error=f"Failed to generate suggestions: {str(e)}"
        )


@app.post("/api/aigis-marketing/post", response_model=dict)
async def post_aigis_marketing_content(
    request: AigisMarketingPostRequest,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Post Aigis Marketing content to specified platforms (LinkedIn, blog, etc.)
    """
    try:
        user_id = current_user.email if current_user else "anonymous_user"
        print(f"[API] 📤 Posting Aigis Marketing content to: {', '.join(request.platforms)}")
        
        # For now, return success (actual posting would require platform APIs)
        # In production, this would:
        # 1. Post to LinkedIn via LinkedIn API
        # 2. Post to WordPress/Substack via their APIs
        # 3. Generate and attach image if needed
        
        return {
            "success": True,
            "message": f"Content prepared for posting to {', '.join(request.platforms)}",
            "platforms": request.platforms,
            "note": "Actual posting requires platform API integration. Content is ready for manual posting."
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[API] ❌ Error posting Aigis Marketing content: {e}")
        return {
            "success": False,
            "error": f"Failed to post content: {str(e)}"
        }


@app.post("/api/marketing-post/update-performance")
async def update_post_performance(
    post_id: str = Form(...),
    views: Optional[int] = Form(None),
    likes: Optional[int] = Form(None),
    comments: Optional[int] = Form(None),
    shares: Optional[int] = Form(None),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Update performance metrics for a post.
    This allows the system to learn from which posts perform well.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        user_id = current_user.email
        
        if not memory_service.is_available():
            return {"success": False, "message": "Hyperspell not available"}
        
        # Calculate engagement rate if we have the data
        engagement_rate = 0.0
        if views and views > 0:
            total_engagement = (likes or 0) + (comments or 0) + (shares or 0)
            engagement_rate = total_engagement / views
        
        # Search for the post in Hyperspell memory
        search_result = await memory_service.query_memories(
            user_id=user_id,
            query=f"post_id {post_id} marketing post",
            max_results=5
        )
        
        if not search_result or not search_result.get("results"):
            # Try to find by topic or caption if post_id not found
            print(f"[API] Post ID not found, searching by content...")
            return {"success": False, "message": "Post not found in memory"}
        
        # Update the post memory with performance data
        performance_data = {
            "views": views or 0,
            "likes": likes or 0,
            "comments": comments or 0,
            "shares": shares or 0,
            "engagement_rate": engagement_rate,
            "updated_at": datetime.now().isoformat()
        }
        
        # Save updated performance as a new memory entry (Hyperspell doesn't support updates directly)
        performance_memory = f"""Post Performance Update

Post ID: {post_id}
Views: {views or 0}
Likes: {likes or 0}
Comments: {comments or 0}
Shares: {shares or 0}
Engagement Rate: {engagement_rate:.4f} ({engagement_rate*100:.2f}%)
Updated: {datetime.now().isoformat()}

Performance Data:
{json.dumps(performance_data, indent=2)}
"""
        
        result = await memory_service.add_text_memory(
            user_id=user_id,
            text=performance_memory,
            collection="post_performance"
        )
        
        if result:
            print(f"[API] ✓ Post performance updated in Hyperspell: {post_id}")
            return {
                "success": True,
                "message": "Performance metrics saved",
                "engagement_rate": engagement_rate
            }
        else:
            return {"success": False, "message": "Failed to save performance metrics"}
        
    except Exception as e:
        print(f"[API] Error updating post performance: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/linkedin/scrape-and-score")
async def scrape_and_score_linkedin_posts(
    keyword: Optional[str] = None,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Scrape LinkedIn posts by keyword, score them, and save to Hyperspell.
    High-scoring posts will be used to generate better suggestions.
    """
    try:
        print(f"[API] 🔍 Scraping LinkedIn posts for keyword: {keyword or 'trending'}")
        
        # Scrape posts
        if keyword:
            posts = await linkedin_scraper.scrape_posts_by_keyword(keyword, limit=limit)
        else:
            posts = await linkedin_scraper.scrape_trending_posts(limit=limit)
        
        if not posts:
            return {"success": False, "message": "No posts found", "posts": []}
        
        # Save to Hyperspell if available
        saved_count = 0
        if memory_service.is_available():
            user_id = current_user.email if current_user else "anonymous_user"
            
            for post in posts:
                try:
                    # Format post data for Hyperspell
                    post_memory = f"""LinkedIn Scored Post - Score: {post['score']}/100

Post ID: {post['post_id']}
Content: {post['content']}
Author: {post['author']}
Post URL: {post['post_url']}
Keyword: {keyword or 'trending'}

Engagement Metrics:
- Likes: {post['likes']}
- Comments: {post['comments']}
- Shares: {post['shares']}
- Views: {post.get('views', 0)}
- Engagement Rate: {post.get('engagement_rate', 0)}%
- Total Engagement: {post.get('total_engagement', 0)}
- Score: {post['score']}/100

Hashtags: {', '.join(post.get('hashtags', []))}
Industry: {post.get('industry', 'N/A')}
Posted At: {post.get('posted_at', 'N/A')}
Scraped At: {post.get('scraped_at', datetime.now().isoformat())}

Full Data:
{json.dumps(post, indent=2)}
"""
                    
                    result = await memory_service.add_text_memory(
                        user_id=user_id,
                        text=post_memory,
                        collection="linkedin_scored_posts"
                    )
                    
                    if result:
                        saved_count += 1
                except Exception as e:
                    print(f"[API] ⚠️ Failed to save post {post.get('post_id')}: {e}")
        
        print(f"[API] ✓ Scraped {len(posts)} posts, saved {saved_count} to Hyperspell")
        
        return {
            "success": True,
            "message": f"Scraped {len(posts)} posts, saved {saved_count} to memory",
            "posts": posts,
            "top_score": posts[0]["score"] if posts else 0
        }
        
    except Exception as e:
        print(f"[API] Error scraping LinkedIn posts: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/marketing-post/suggestions", response_model=MarketingPostSuggestionsResponse)
async def get_marketing_post_suggestions(
    current_user: Optional[User] = Depends(get_current_user),
    count: int = 5
):
    """
    Get AI-generated marketing post topic suggestions based on Hyperspell memory context.
    Uses user's uploaded documents and memories to suggest relevant, personalized topics.
    """
    try:
        print(f"[API] 💡 Generating marketing post suggestions...")
        
        if not openai_service:
            raise HTTPException(
                status_code=503,
                detail="OpenAI service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        # CRITICAL: Require authentication for personalized suggestions
        if not current_user:
            print(f"[API] ⚠️ No user authenticated - returning generic suggestions")
            # Return generic suggestions if not authenticated
            suggestions_list = [
                {"topic": "Product launch announcement", "context": "General marketing topic", "reasoning": "Effective for building excitement"},
                {"topic": "Behind-the-scenes company culture", "context": "General marketing topic", "reasoning": "Builds brand authenticity"},
                {"topic": "Customer success story", "context": "General marketing topic", "reasoning": "Social proof and engagement"},
                {"topic": "Industry tips and best practices", "context": "General marketing topic", "reasoning": "Educational content drives engagement"},
                {"topic": "Company values and mission", "context": "General marketing topic", "reasoning": "Builds brand connection"}
            ]
            suggestions = [
                MarketingPostSuggestion(
                    topic=s.get("topic", ""),
                    context=s.get("context"),
                    reasoning=s.get("reasoning"),
                    score=None,
                    source="generic"
                )
                for s in suggestions_list[:count]
            ]
            return MarketingPostSuggestionsResponse(
                suggestions=suggestions,
                user_context_used=None
            )
        
        # Get user context from Memory (documents are stored in S3 + Mem0)
        # CRITICAL: Use consistent normalization to ensure memories persist across deployments
        user_id = get_user_id_from_request(current_user)
        print(f"[API] Using normalized user_id for Memory: {user_id}")
        print(f"[API] User details - username: {current_user.username}, email: {current_user.email}, id: {current_user.id}")
        user_context = ""
        post_performance_context = ""
        
        # Always try to get ALL context from Memory (S3 + Mem0) if user is logged in
        # This includes documents, competitors, previously generated posts, user context, etc.
        # Run queries in parallel to speed up response time
        user_context = ""
        post_performance_context = ""
        linkedin_posts_context = ""
        high_scoring_posts = []
        
        if memory_service.is_available() and current_user:
            print(f"[API] Getting ALL memories from Mem0 for user: {user_id}")
            print(f"[API] Using normalized email '{user_id}' to query Memory (S3 + Mem0)")
            print(f"[API] Make sure memories were saved with the same email format!")
            
            # Run all Memory queries in parallel for faster response
            import asyncio
            tasks = []
            
            # Task 1: Get all memories - use normalized user_id
            tasks.append(memory_service.get_all_memories_context(user_id))
            
            # Task 2: Get post performance context - use normalized user_id
            tasks.append(get_post_performance_context(
                memory_service=memory_service,
                user_id=user_id
            ))
            
            # Task 3: Get LinkedIn posts - use normalized user_id
            async def get_linkedin_posts():
                try:
                    return await memory_service.query_memories(
                        user_id=user_id,
                        query="LinkedIn Scored Post high score engagement metrics",
                        max_results=10
                    )
                except Exception as e:
                    print(f"[API] ⚠️ Error fetching LinkedIn posts: {e}")
                    return None
            tasks.append(get_linkedin_posts())
            
            # Run all queries in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Extract results
            user_context = results[0] if not isinstance(results[0], Exception) else ""
            post_performance_context = results[1] if not isinstance(results[1], Exception) else ""
            linkedin_search = results[2] if not isinstance(results[2], Exception) else None
            
            if user_context:
                print(f"[API] ✓ Retrieved all user memories ({len(user_context)} chars)")
            else:
                print(f"[API] ⚠️ No memories found in Hyperspell for user: {user_id}")
                print(f"[API] This might mean:")
                print(f"[API]   1. No documents/competitors/posts have been added to Hyperspell")
                print(f"[API]   2. Items were added but not indexed yet")
                print(f"[API]   3. The user_id doesn't match (stored vs queried)")
                print(f"[API]   4. Email format mismatch - stored with different case/format")
                print(f"[API] DEBUG: User email from DB: '{current_user.email}'")
                print(f"[API] DEBUG: Normalized user_id used: '{user_id}'")
                print(f"[API] TIP: Make sure documents/competitors were saved with the same email format!")
            
            # Process LinkedIn posts if found
            if linkedin_search and linkedin_search.get("results") and isinstance(linkedin_search.get("results"), list):
                    results = linkedin_search.get("results", [])
                    for result in results:
                        if isinstance(result, dict):
                            content = result.get("content", result.get("text", ""))
                            # Extract score from content
                            score_match = re.search(r'Score: ([\d.]+)/100', content)
                            if score_match:
                                score = float(score_match.group(1))
                                # Only include posts with score > 50
                                if score >= 50:
                                    # Extract content snippet
                                    content_match = re.search(r'Content: (.+?)(?:\n|$)', content)
                                    content_text = content_match.group(1) if content_match else ""
                                    
                                    high_scoring_posts.append({
                                        "score": score,
                                        "content": content_text[:200] + "..." if len(content_text) > 200 else content_text
                                    })
                    
                    # Sort by score and take top 5
                    high_scoring_posts.sort(key=lambda x: x["score"], reverse=True)
                    high_scoring_posts = high_scoring_posts[:5]
                    
                    if high_scoring_posts:
                        linkedin_posts_context = "HIGH-SCORING LINKEDIN POSTS (use these as inspiration):\n"
                        for i, post in enumerate(high_scoring_posts, 1):
                            linkedin_posts_context += f"{i}. Score: {post['score']}/100 - {post['content']}\n"
                        print(f"[API] ✓ Found {len(high_scoring_posts)} high-scoring LinkedIn posts")
        
        # Build prompt for generating suggestions
        context_section = ""
        if user_context:
            context_section = f"""
USER CONTEXT (ALL Hyperspell memories - includes uploaded documents, competitors, previously generated posts, brand guidelines, business information, and any other stored context):
{user_context}

CRITICAL: Use ALL of this context to create highly personalized and relevant marketing post suggestions. Reference specific details from:
- Uploaded documents and brand context
- Competitor information
- Previously generated posts and their performance
- Any other stored memories

Make suggestions that align with the user's actual brand, business, competitors, and content history."""
        else:
            context_section = """
No user context found in Hyperspell memories. Suggest general marketing post topics that are versatile and engaging."""
        
        performance_section = ""
        if post_performance_context:
            performance_section = f"""
POST PERFORMANCE CONTEXT (learn from what worked):
{post_performance_context}

Use insights from high-performing posts to suggest similar topics that are likely to perform well."""
        
        linkedin_section = ""
        if linkedin_posts_context:
            linkedin_section = f"""
{linkedin_posts_context}

IMPORTANT: Base your suggestions on these high-scoring LinkedIn posts. Extract key themes, topics, and content styles that made these posts successful. Each suggestion should be inspired by these high-performing posts and include a score estimate (0-100) based on how similar it is to the high-scoring posts."""
        
        suggestions_prompt = f"""Generate {count} creative and engaging marketing post topic suggestions for social media (Instagram, LinkedIn, Twitter).

{context_section}
{performance_section}
{linkedin_section}

Requirements:
- Each suggestion should be specific, actionable, and engaging
- Topics should be suitable for visual marketing posts
- CRITICAL: If user context is provided above, you MUST use ALL of it to create personalized suggestions
- Reference specific details from: uploaded documents, competitors, previously generated posts, brand information, business context
- If performance data is available, prioritize topics similar to high-performing posts
- Include a brief explanation of why each topic is relevant, specifically referencing the user's actual context (documents, competitors, posts, etc.)
- Make suggestions diverse (mix of product highlights, tips, behind-the-scenes, educational content, competitor-inspired content, etc.)
- Each topic should be 5-15 words
- The "context" field should explain how the suggestion relates to the user's actual context from their Hyperspell memories (documents, competitors, posts, etc.)

Return the suggestions in this JSON format:
{{
  "suggestions": [
    {{
      "topic": "Topic suggestion here",
      "context": "Why this is relevant based on the user's brand context from Memory (which includes uploaded documents, brand guidelines, and business information)",
      "reasoning": "Brief explanation of why this topic would work well",
      "score": 85.5,
      "source": "linkedin_scored"
    }}
  ]
}}

IMPORTANT FOR CONTEXT FIELD:
- If user context is provided above, ALWAYS reference specific details from ALL memories in the "context" field
- Mention specific elements from: uploaded documents, competitors, previously generated posts, brand information, business details
- Reference competitor names, document topics, post themes, or other specific details from the memories
- If no context is available, you can say "General marketing topic" but prefer to use context when available
- The context field should show HOW the suggestion relates to the user's actual memories (documents, competitors, posts, etc.)

IMPORTANT: 
- If high-scoring LinkedIn posts are provided, base suggestions on those and set source to "linkedin_scored"
- Include a score (0-100) for each suggestion based on similarity to high-scoring posts
- If no LinkedIn posts available, set source to "ai_generated" and estimate score based on topic quality

Return ONLY valid JSON, no additional text."""

        try:
            response = await openai_service.client.chat.completions.create(
                model=openai_service.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert social media marketer who creates highly relevant, personalized marketing post topics based on user context and brand information."
                    },
                    {
                        "role": "user",
                        "content": suggestions_prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            import json
            suggestions_data = json.loads(response.choices[0].message.content)
            
            # Validate and format suggestions
            suggestions_list = suggestions_data.get("suggestions", [])
            if not suggestions_list:
                # Fallback: generate simple suggestions
                suggestions_list = [
                    {"topic": "Product launch announcement", "context": "General marketing topic", "reasoning": "Effective for building excitement"},
                    {"topic": "Behind-the-scenes company culture", "context": "General marketing topic", "reasoning": "Builds brand authenticity"},
                    {"topic": "Customer success story", "context": "General marketing topic", "reasoning": "Social proof and engagement"},
                    {"topic": "Industry tips and best practices", "context": "General marketing topic", "reasoning": "Educational content drives engagement"},
                    {"topic": "Company values and mission", "context": "General marketing topic", "reasoning": "Builds brand connection"}
                ]
            
            # Limit to requested count
            suggestions_list = suggestions_list[:count]
            
            # Convert to Pydantic models
            suggestions = []
            for s in suggestions_list:
                # If we have high-scoring posts, try to match score
                score = s.get("score")
                if not score and high_scoring_posts:
                    # Estimate score based on similarity to high-scoring posts
                    # Simple heuristic: if topic matches keywords from high-scoring posts
                    topic_lower = s.get("topic", "").lower()
                    avg_score = sum(p["score"] for p in high_scoring_posts) / len(high_scoring_posts)
                    # If topic seems related, use average score, otherwise lower
                    if any(keyword in topic_lower for keyword in ["ai", "business", "leadership", "innovation", "technology"]):
                        score = avg_score * 0.9
                    else:
                        score = avg_score * 0.7
                
                suggestions.append(
                    MarketingPostSuggestion(
                        topic=s.get("topic", ""),
                        context=s.get("context"),
                        reasoning=s.get("reasoning"),
                        score=round(score, 2) if score else None,
                        source=s.get("source", "linkedin_scored" if high_scoring_posts else "ai_generated")
                    )
                )
            
            print(f"[API] ✓ Generated {len(suggestions)} marketing post suggestions")
            
            return MarketingPostSuggestionsResponse(
                suggestions=suggestions,
                user_context_used=user_context[:200] + "..." if user_context and len(user_context) > 200 else user_context
            )
            
        except json.JSONDecodeError as e:
            print(f"[API] ⚠️ Failed to parse suggestions JSON: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate suggestions. Please try again."
            )
        except Exception as e:
            print(f"[API] ⚠️ Error generating suggestions: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate suggestions: {str(e)}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Marketing post suggestions error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/smart-composition", response_model=SmartVideoCompositionResponse)
async def create_smart_video_composition(request: SmartVideoCompositionRequest):
    """
    Create a smart, informative video by:
    1. Generating images from prompts
    2. Intelligently composing them into a Veo 3 video
    3. Using AI to determine optimal placement and transitions
    """
    try:
        print(f"[API] Creating smart video composition with {len(request.image_prompts)} images")
        
        # Step 1: Generate images (prefer Nano Banana for superior quality)
        image_results = await image_generation_service.generate_multiple_images(
            request.image_prompts,
            model="nanobanana",  # Superior text rendering (94% accuracy) and photorealism
            size="1024x1024",
            quality="medium"
        )
        
        image_urls = [r.get("image_url") for r in image_results if r.get("image_url")]
        image_descriptions = [r.get("revised_prompt", prompt) for r, prompt in zip(image_results, request.image_prompts) if r.get("image_url")]
        
        if not image_urls:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any images"
            )
        
        print(f"[API] Generated {len(image_urls)} images successfully")
        
        # Step 2: Create smart video composition
        composition_data = await video_composition_service.create_smart_video_script(
            video_prompt=request.video_prompt,
            image_urls=image_urls,
            image_descriptions=image_descriptions,
            target_duration=request.target_duration,
            style=request.style
        )
        
        print(f"[API] Created smart video script: {composition_data['enhanced_prompt'][:100]}...")
        
        # Step 3: Generate video using Veo 3 or Sora
        video_job_id = None
        video_model = "veo-3"
        
        if request.use_veo3 and veo3_service.project_id:
            try:
                print(f"[API] Generating video with Veo 3...")
                veo3_result = await veo3_service.generate_video(
                    prompt=composition_data["enhanced_prompt"],
                    duration=request.target_duration,
                    resolution="1280x720",
                    image_urls=image_urls,
                    style=request.style
                )
                video_job_id = veo3_result.get("job_id")
                video_model = "veo-3"
                print(f"[API] Veo 3 video job created: {video_job_id}")
            except Exception as veo3_error:
                print(f"[API] Veo 3 generation failed, falling back to Sora: {veo3_error}")
                request.use_veo3 = False
        
        if not video_job_id and openai_service:
            try:
                print(f"[API] Generating video with Sora...")
                sora_result = await openai_service.generate_sora_video(
                    prompt=composition_data["enhanced_prompt"],
                    model=SORA_MODEL_DEFAULT,
                    size="1280x720",
                    seconds=request.target_duration
                )
                video_job_id = sora_result.get("job_id")
                video_model = "sora-2"
                print(f"[API] Sora video job created: {video_job_id}")
            except Exception as sora_error:
                print(f"[API] Sora generation also failed: {sora_error}")
        
        return SmartVideoCompositionResponse(
            topic=request.video_prompt,
            image_urls=image_urls,
            image_descriptions=image_descriptions,
            video_script=composition_data["enhanced_prompt"],
            composition_data=composition_data,
            video_job_id=video_job_id,
            video_model=video_model,
            generated_images=image_results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Smart composition error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/informational", response_model=InformationalVideoResponse)
async def create_informational_video(request: InformationalVideoRequest):
    """
    Create informational videos in Instagram reel style by automatically learning from Instagram profile:
    1. Scrape Instagram profile to understand brand/style/context
    2. AI analyzes profile and generates topic/content ideas
    3. AI-generated image prompts based on learned context
    4. Gemini 3 Pro Image generation
    5. Informational video script creation
    6. Video generation with Veo 3
    
    Style: Clean, professional, informative content similar to educational Instagram reels
    """
    try:
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required for informational video generation"
            )
        
        print(f"[API] Creating informational video for Instagram profile: @{request.username}")
        print(f"[API] Target duration: {request.target_duration} seconds")
        
        # Step 1: Scrape Instagram profile to learn context (with graceful fallback)
        print(f"[API] 📱 Scraping Instagram profile to learn context...")
        profile_context = {}
        try:
            profile_context = await instagram_service.get_profile_context(request.username)
        except Exception as profile_error:
            print(f"[API] ⚠️ Could not scrape Instagram profile: {profile_error}")
            print(f"[API] Continuing with AI-generated context based on username...")
            # Create minimal profile context from username
            profile_context = {
                "username": request.username,
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
        
        # If profile context is empty or missing username, use fallback
        if not profile_context or not profile_context.get('username'):
            print(f"[API] ⚠️ Profile context unavailable, using username-based context generation...")
            profile_context = {
                "username": request.username,
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
        
        # Step 2: Get document context if provided
        document_context = ""
        if request.document_ids and len(request.document_ids) > 0:
            print(f"[API] 📄 Retrieving context from {len(request.document_ids)} document(s)...")
            try:
                document_context = document_service.get_documents_context(request.document_ids)
                print(f"[API] ✓ Document context retrieved ({len(document_context)} characters)")
            except Exception as doc_error:
                print(f"[API] ⚠️ Error retrieving document context: {doc_error}")
                document_context = ""
        
        # Step 3: Research profile context using AI (works even with minimal context)
        print(f"[API] 🤖 Analyzing profile context with AI...")
        page_context_summary = await openai_service.research_profile_context(profile_context, document_context)
        
        # Step 3.5: Enhance with Hyperspell memory context (reusable helper)
        memory_query = f"{request.username} {profile_context.get('biography', '')[:100]} {document_context[:100] if document_context else ''}".strip()
        if memory_query:
            memory_context = await get_memory_context(
                memory_service=memory_service,
                query=memory_query,
                user_email=None
            )
            if memory_context:
                page_context_summary = f"""{memory_context}

{page_context_summary}"""
        
        # If AI research also fails, use username as fallback
        if not page_context_summary or len(page_context_summary.strip()) < 10:
            print(f"[API] ⚠️ AI research failed, using username-based context...")
            page_context_summary = f"Content for {request.username} - informational and educational style"
        
        print(f"[API] Profile context learned: {page_context_summary[:200]}...")
        
        # Step 3: Generate a topic and image prompts based on the learned context
        print(f"[API] 📝 Generating content ideas and image prompts from learned context...")
        
        image_prompt_generation = f"""Based on this Instagram profile analysis, create content for an informational video:

PROFILE CONTEXT:
{page_context_summary}

PROFILE DETAILS:
- Username: @{profile_context.get('username', '')}
- Full Name: {profile_context.get('full_name', '')}
- Bio: {profile_context.get('biography', '')}
- Business Category: {profile_context.get('business_category', 'N/A')}
- Followers: {profile_context.get('followers', 0):,}

Create exactly 1 detailed image prompt that:
1. Represents the key theme from this profile's content style
2. Aligns with the account's brand identity and messaging
3. Is suitable for an informational/educational video style (like Instagram reels)
4. Works well with image generation (photorealistic, clear visuals)
5. Supports the narrative flow of a {request.target_duration}-second informational video
6. Matches the aesthetic and style of this Instagram account

Also suggest a main topic for the video that aligns with this profile's content themes.

Return a JSON object with:
- "topic": Main topic/subject for the informational video
- "image_prompts": Array with exactly 1 detailed image prompt string
- "key_points": Array of 1-3 key points to cover in the video"""

        try:
            response = await openai_service.client.chat.completions.create(
                model=openai_service.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at analyzing Instagram profiles and creating visual prompts for informational content that aligns with their brand identity and content style."
                    },
                    {
                        "role": "user",
                        "content": image_prompt_generation
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "content_generation",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string",
                                    "description": "Main topic/subject for the informational video"
                                },
                                "image_prompts": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1,
                                    "maxItems": 1,
                                    "description": "Array with exactly 1 detailed image prompt"
                                },
                                "key_points": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 1,
                                    "maxItems": 3,
                                    "description": "Key points to cover in the video"
                                }
                            },
                            "required": ["topic", "image_prompts", "key_points"],
                            "additionalProperties": False
                        }
                    }
                },
                temperature=0.7
            )
            
            import json
            content_data = json.loads(response.choices[0].message.content)
            topic = content_data["topic"]
            image_prompts = content_data["image_prompts"]
            key_points = content_data["key_points"]
            
        except Exception as e:
            print(f"[API] ⚠️ AI content generation failed, using fallback: {e}")
            # Fallback: Create simple prompt based on profile
            topic = f"About {profile_context.get('full_name', profile_context.get('username', 'this account'))}"
            image_prompts = [
                f"Professional illustration related to {profile_context.get('biography', 'content')[:50]}, clean and modern style, informative design matching this account's aesthetic"
            ]
            key_points = ["Key concept 1"]
        
        print(f"[API] Generated topic: {topic}")
        print(f"[API] Generated {len(image_prompts)} image prompts")
        print(f"[API] Generated {len(key_points)} key points")
        
        # Step 2: Generate images using Gemini 3 Pro Image via Vertex AI (same auth as Veo 3)
        print(f"[API] 🎨 Generating images with Gemini 3 Pro Image (Vertex AI)...")
        image_results = await image_generation_service.generate_multiple_images(
            image_prompts,
            model="gemini-3-pro-image",  # Gemini 3 Pro Image via Vertex AI
            size="1024x1024",
            quality="high"  # Quality parameter (not used by Gemini but kept for compatibility)
        )
        
        image_urls = [r.get("image_url") for r in image_results if r.get("image_url")]
        image_descriptions = [r.get("revised_prompt", prompt) for r, prompt in zip(image_results, image_prompts) if r.get("image_url")]
        
        if not image_urls:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate any images. Check GOOGLE_CLOUD_PROJECT_ID configuration. Image generation uses Gemini 3 Pro Image via Vertex AI (same as Veo 3)."
            )
        
        print(f"[API] ✓ Generated {len(image_urls)} images successfully")
        
        # Step 3: Create informational video script in Instagram reel style
        print(f"[API] 📹 Creating informational video script...")
        
        informational_script_prompt = f"""Create an {request.target_duration}-second informational video script in the style of popular Instagram educational reels.

TOPIC: {topic}

LEARNED PROFILE CONTEXT:
{page_context_summary}

KEY POINTS:
{chr(10).join(f"- {point}" for point in key_points)}

GENERATED IMAGES:
{chr(10).join(f"Image {i+1}: {desc}" for i, desc in enumerate(image_descriptions))}

STYLE REQUIREMENTS:
- Clean, professional, informative tone
- Fast-paced but clear delivery
- Visual storytelling with smooth transitions
- Text overlays and graphics that enhance understanding
- Engaging and shareable format
- Aligns with company brand identity

Create a detailed Veo 3 video prompt that:
1. Incorporates the generated images naturally
2. Uses smooth transitions and visual effects
3. Maintains an informative, educational tone
4. Includes text/graphics overlays in the description
5. Fits exactly {request.target_duration} seconds
6. Matches the company's brand style

Return a JSON object with:
- "video_prompt": Complete Veo 3 prompt for the video
- "narrative_structure": How the video flows
- "image_integration": How images are used
- "text_overlays": Suggested text overlays/key points"""

        try:
            script_response = await openai_service.client.chat.completions.create(
                model=openai_service.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert video director specializing in creating engaging, informative Instagram-style educational content that incorporates images and text overlays."
                    },
                    {
                        "role": "user",
                        "content": informational_script_prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "informational_video_script",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "video_prompt": {
                                    "type": "string",
                                    "description": "Complete Veo 3 prompt for the informational video"
                                },
                                "narrative_structure": {
                                    "type": "string",
                                    "description": "How the video narrative flows"
                                },
                                "image_integration": {
                                    "type": "string",
                                    "description": "How the generated images are integrated"
                                },
                                "text_overlays": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "Suggested text overlays or key points"
                                }
                            },
                            "required": ["video_prompt", "narrative_structure", "image_integration"]
                        }
                    }
                },
                temperature=0.7
            )
            
            script_data = json.loads(script_response.choices[0].message.content)
            video_script = script_data["video_prompt"]
            
        except Exception as e:
            print(f"[API] ⚠️ Script generation failed, using composition service: {e}")
            # Fallback: Use video composition service
            composition_data = await video_composition_service.create_smart_video_script(
                video_prompt=f"Create an informative {request.target_duration}-second video about {topic}",
                image_urls=image_urls,
                image_descriptions=image_descriptions,
                target_duration=request.target_duration,
                style="informative"
            )
            video_script = composition_data["enhanced_prompt"]
            script_data = {
                "narrative_structure": composition_data.get("narrative_structure", ""),
                "image_integration": composition_data.get("composition_notes", ""),
                "text_overlays": []
            }
        
        print(f"[API] ✓ Video script created: {video_script[:100]}...")
        
        # Step 4: Generate video with Veo 3 (always use Veo 3 for informational videos)
        video_job_id = None
        video_model = "veo-3"
        
        if not veo3_service.project_id:
            raise HTTPException(
                status_code=400,
                detail="Veo 3 is required for informational videos. Please configure GOOGLE_CLOUD_PROJECT_ID."
            )
        
        # Validate Veo 3 duration constraints (4-60 seconds)
        target_duration = request.target_duration or 8
        veo3_duration = max(4, min(60, target_duration))
        if veo3_duration != target_duration:
            print(f"[API] ⚠️ Veo 3 duration adjusted from {target_duration}s to {veo3_duration}s (must be 4-60 seconds)")
        
        # Guardrail: Warn if duration is very long (may take significant time)
        if veo3_duration > 30:
            print(f"[API] ⚠️ Veo 3 generation with {veo3_duration}s duration may take 3-5 minutes")
        
        try:
            print(f"[API] 🎬 Generating video with Veo 3...")
            print(f"[API]   Duration: {veo3_duration}s (Veo 3 supports 4-60 seconds)")
            veo3_result = await veo3_service.generate_video(
                prompt=video_script,
                duration=veo3_duration,
                resolution="1280x720",
                image_urls=image_urls[:1] if image_urls else None  # Use only 1 image
            )
            video_job_id = veo3_result.get("job_id")
            video_model = veo3_result.get("model", "veo-3")
            print(f"[API] ✓ Veo 3 video job created: {video_job_id}")
        except Exception as veo3_error:
            print(f"[API] ❌ Veo 3 generation failed: {veo3_error}")
            raise HTTPException(
                status_code=500,
                detail=f"Veo 3 video generation failed: {str(veo3_error)}"
            )
        
        return InformationalVideoResponse(
            topic=topic,
            company_context=page_context_summary,
            generated_images=image_results,
            image_urls=image_urls,
            image_prompts=image_prompts,
            video_script=video_script,
            video_job_id=video_job_id,
            video_model=video_model,
            composition_data={
                "narrative_structure": script_data.get("narrative_structure", ""),
                "image_integration": script_data.get("image_integration", ""),
                "text_overlays": script_data.get("text_overlays", []),
                "key_points": key_points,
                "learned_from": f"@{request.username}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (PDF, DOCX, TXT)"""
    try:
        # Validate file type
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed types: PDF, DOC, DOCX, TXT"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {max_size / (1024 * 1024)}MB limit"
            )
        
        # Save and process document
        result = await document_service.save_document(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Document upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents")
async def list_documents():
    """List all uploaded documents"""
    try:
        documents = document_service.get_all_documents()
        return {"documents": documents}
    except Exception as e:
        print(f"[API] Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}")
async def get_document(document_id: str):
    """Get document metadata and text content"""
    try:
        document = document_service.get_document(document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/documents/{document_id}/text")
async def get_document_text(document_id: str):
    """Get just the text content of a document"""
    try:
        text = document_service.get_document_text(document_id)
        if text is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"text": text}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error getting document text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/competitors/find")
async def find_competitors(
    request: FindCompetitorsRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Find competitors based on brand context document, website, or stored memory context.
    Analyzes the context to understand the brand and suggests relevant competitors.
    """
    try:
        document_id = request.document_id
        website_url = request.website_url
        use_context = request.use_context
        
        document_text = ""
        
        # Priority: document_id > use_context (memory) > website_url
        if document_id:
            # Get document text
            document_text = document_service.get_document_text(document_id)
            if not document_text:
                raise HTTPException(status_code=404, detail="Document not found or has no text content")
            print(f"[API] Finding competitors based on document: {document_id}")
        elif use_context and current_user:
            # Get context from user's stored memories
            user_id = normalize_user_id(current_user)
            print(f"[API] Finding competitors using stored context for user: {user_id}")
            document_text = await memory_service.get_all_memories_context(user_id)
            if not document_text or len(document_text.strip()) < 50:
                raise HTTPException(status_code=400, detail="No brand context found. Please add a website or upload a document first.")
        elif website_url:
            # Scrape website for context (fallback)
            print(f"[API] Finding competitors based on website: {website_url}")
            # Use existing scraped context from memory
            if current_user:
                user_id = normalize_user_id(current_user)
                document_text = await memory_service.get_all_memories_context(user_id)
            if not document_text or len(document_text.strip()) < 50:
                raise HTTPException(status_code=400, detail="No brand context found for this website. Please re-analyze the website.")
        else:
            raise HTTPException(status_code=400, detail="Please provide a document_id, website_url, or set use_context=true")
        
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key is required for competitor analysis. Please set OPENAI_API_KEY in your backend/.env file."
            )
        
        print(f"[API] Context text length: {len(document_text)} characters")
        
        # Use OpenAI to analyze brand context and find competitors
        prompt = f"""Based on the following brand context, identify and suggest relevant competitors that this brand would be trying to beat or learn from.

BRAND CONTEXT:
{document_text[:8000]}  # Limit to 8000 chars to avoid token limits

Your task:
1. Analyze the brand's industry, target audience, products/services, and positioning
2. Identify 5-10 relevant competitors that:
   - Operate in the same or similar space
   - Target similar audiences
   - Offer similar products/services
   - Would be direct or indirect competitors
3. For each competitor, provide:
   - Company/brand name
   - Brief reason why they're a competitor (1-2 sentences)
   - Platform handles if relevant (Instagram, LinkedIn, etc.)

Return your response as a JSON array of objects with this structure:
[
  {{
    "name": "Competitor Name",
    "reason": "Why this is a relevant competitor",
    "platforms": ["instagram_handle", "linkedin_handle"]
  }}
]

Focus on competitors that would be valuable to analyze and learn from. Be specific and actionable."""

        # Call OpenAI to find competitors
        response = await openai_service.client.chat.completions.create(
            model=openai_service.model,
            messages=[
                {"role": "system", "content": "You are an expert market researcher who identifies competitors based on brand context. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse the response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response (might be wrapped in markdown code blocks)
        # Remove markdown code blocks if present
        json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(1)
        else:
            # Try to find JSON array directly
            json_match = re.search(r'(\[.*\])', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(1)
        
        competitors = json.loads(response_text)
        
        # Validate and format the response
        if not isinstance(competitors, list):
            raise ValueError("Response is not a list")
        
        # Limit to 10 competitors
        competitors = competitors[:10]
        
        print(f"[API] Found {len(competitors)} competitors")
        
        return {
            "competitors": competitors,
            "document_id": document_id,
            "source": "document" if document_id else ("context" if use_context else "website")
        }
        
    except json.JSONDecodeError as e:
        print(f"[API] JSON decode error: {str(e)}")
        print(f"[API] Response text: {response_text[:500]}")
        raise HTTPException(status_code=500, detail=f"Failed to parse competitor analysis: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error finding competitors: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to find competitors: {str(e)}")


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        success = document_service.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"status": "success", "message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/context")
async def get_documents_context(document_ids: List[str]):
    """Get combined text context from multiple documents"""
    try:
        context = document_service.get_documents_context(document_ids)
        return {"context": context}
    except Exception as e:
        print(f"[API] Error getting documents context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/options", response_model=VideoOptionsResponse)
async def get_video_options(request: VideoOptionsRequest):
    """
    Generate multiple video options from documents for user to choose from.
    Context is handled by frontend localStorage.
    """
    try:
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required. Please set OPENAI_API_KEY in your backend/.env file."
            )
        
        print(f"[API] Generating {request.num_options} video options from {len(request.document_ids)} document(s)")
        
        # Get document context
        document_context = document_service.get_documents_context(request.document_ids)
        if not document_context or len(document_context.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Documents appear to be empty or could not be processed."
            )
        
        # Enhance with Hyperspell memory context (reusable helper)
        memory_query = document_context[:200] if document_context else ""
        memory_context = await get_memory_context(
            memory_service=memory_service,
            query=memory_query,
            user_email=None
        )
        if hyperspell_context:
            document_context = f"""{hyperspell_context}

{document_context}"""
            print(f"[API] ✓ Enhanced document context with Hyperspell memories")
        
        # Generate video options with video model
        video_model = getattr(request, 'video_model', 'sora-2') or 'sora-2'
        print(f"[API] Generating video options with model: {video_model}")
        options = await openai_service.generate_video_options(
            document_context=document_context,
            num_options=request.num_options or 3,
            video_model=video_model
        )
        
        print(f"[API] Context handled by frontend localStorage")
        
        return {"options": options}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error generating video options: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/video/from-documents", response_model=DocumentVideoResponse)
async def create_video_from_documents(request: DocumentVideoRequest):
    """
    Create marketing videos from uploaded documents.
    Uses document content as context to generate personalized marketing videos.
    """
    try:
        if not openai_service:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key required for video generation. Please set OPENAI_API_KEY in your backend/.env file."
            )
        
        print(f"[API] Creating marketing video from {len(request.document_ids)} document(s)")
        if request.topic:
            print(f"[API] Topic (user-specified): {request.topic}")
        else:
            print(f"[API] Topic: AI will decide based on document content")
        if request.duration:
            print(f"[API] Duration (user-specified): {request.duration} seconds")
        else:
            print(f"[API] Duration: AI will decide optimal duration")
        
        # Step 1: Get document context
        print(f"[API] 📄 Retrieving context from documents...")
        try:
            document_context = document_service.get_documents_context(request.document_ids)
            print(f"[API] ✓ Document context retrieved ({len(document_context)} characters)")
        except Exception as doc_error:
            print(f"[API] ⚠️ Error retrieving document context: {doc_error}")
            raise HTTPException(
                status_code=400,
                detail=f"Failed to retrieve document context: {str(doc_error)}"
            )
        
        if not document_context or len(document_context.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Documents appear to be empty or could not be processed. Please ensure your documents contain readable text."
            )
        
        # Get Hyperspell memory context for enhanced personalization (reusable helper)
        memory_query = f"{request.topic or ''} {document_context[:200] if document_context else ''}".strip()
        memory_context = await get_memory_context(
            memory_service=memory_service,
            query=memory_query,
            user_email=None  # Can add user auth later
        )
        user_context_summary = hyperspell_context  # Use Hyperspell context
        
        # Step 1.6: Enhance document context with Hyperspell memory (reusable helper)
        if hyperspell_context:
            document_context = f"""{hyperspell_context}

{document_context}"""
            print(f"[API] ✓ Enhanced document context with Hyperspell memories ({len(hyperspell_context)} chars)")
        
        # Step 1.5: Web research - Extract companies and research them
        web_research_context = ""
        try:
            print(f"[API] 🔍 Starting web research for companies in documents...")
            research_data = await web_research_service.research_companies_from_document(document_context)
            
            if research_data.get("companies_found"):
                main_company = research_data.get("main_company")
                if main_company:
                    print(f"[API] ✓ Found {len(research_data['companies_found'])} companies")
                    print(f"[API] 🎯 Main company identified: {main_company} (user's company)")
                else:
                    print(f"[API] ✓ Found {len(research_data['companies_found'])} companies: {', '.join(research_data['companies_found'][:3])}")
                
                web_research_context = web_research_service.format_research_for_ai(research_data)
                print(f"[API] 📊 Web research context: {len(web_research_context)} characters")
            else:
                print(f"[API] ℹ️ No companies found in documents for web research")
        except Exception as web_error:
            print(f"[API] ⚠️ Web research error (continuing without it): {web_error}")
            import traceback
            traceback.print_exc()
        
        # Combine document context with web research
        if web_research_context:
            document_context = f"{document_context}\n\n{web_research_context}"
            print(f"[API] ✓ Enhanced document context with web research (total: {len(document_context)} chars)")
        
        # Note: Hyperspell context was already added earlier in the function
        # Context is handled by frontend localStorage
        print(f"[API] Context will be saved in frontend localStorage")
        
        # Step 2: Generate video options first (if not already chosen)
        video_options = None
        if not request.topic and not request.duration:  # If user hasn't specified, generate options
            try:
                print(f"[API] 📋 Generating video options for user selection...")
                video_options = await openai_service.generate_video_options(
                    document_context=document_context,
                    num_options=3
                )
                print(f"[API] ✓ Generated {len(video_options)} video options")
            except Exception as options_error:
                print(f"[API] ⚠️ Could not generate options, proceeding with single script: {options_error}")
        
        # Check if script is pre-approved (user has already reviewed and approved it)
        video_model = request.video_model or "sora-2"
        print(f"[API] 📹 Video model from request: {request.video_model}")
        print(f"[API] 📹 Selected video model: {video_model}")
        print(f"[API] 📹 Script approved: {request.approved}")
        
        # Initialize script_result to avoid NameError
        script_result = None
        video_script = None
        sora_prompt = None
        linkedin_optimization = ""
        key_insights = ""
        document_analysis = ""
        
        if request.approved and request.script:
            # User has approved the script - skip generation and go straight to video
            print(f"[API] ✓ Using pre-approved script ({len(request.script)} characters)")
            video_script = request.script
            sora_prompt = request.script  # Use script as prompt
            # Create minimal script_result for approved scripts
            script_result = {
                "script": request.script,
                "sora_prompt": request.script,
                "ai_decisions": {
                    "duration": request.duration or (60 if (video_model == "veo-3" or video_model == "veo3") else 8),
                    "topic": request.topic or "Professional Content",
                    "audience": request.target_audience or "Professional Audience"
                },
                "linkedin_optimization": "",
                "key_insights": "",
                "document_analysis": ""
            }
        else:
            # Step 3: Generate LinkedIn-optimized video script from document context
            # Note: document_context already includes Hyperspell context from earlier in the function
            platform = request.platform or "linkedin"
            print(f"[API] 📝 Generating {platform.upper()}-optimized video script from document context...")
            print(f"[API] 📊 Using deep document analysis with {len(document_context)} characters of context (includes Hyperspell memories)")
            
            try:
                # Determine optimal duration based on video model
                # For Veo 3, AI can choose any duration 4-60 seconds based on content needs
                # For Sora 2, must be 4, 8, or 12 seconds
                video_model_for_script = request.video_model or "sora-2"
                
                # If Veo 3 and no duration specified, let AI decide optimal duration (4-60 seconds)
                # If Sora 2 and no duration specified, AI must choose from 4, 8, or 12 seconds
                duration_for_script = request.duration
                if not duration_for_script:
                    if video_model_for_script == "veo-3" or video_model_for_script == "veo3":
                        print(f"[API] 📏 Veo 3 selected - AI will determine optimal duration (4-60 seconds) based on content complexity")
                    else:
                        print(f"[API] 📏 Sora 2 selected - AI will determine optimal duration (4, 8, or 12 seconds only)")
                
                # Use the new LinkedIn-optimized script generation method with user context
                script_result = await openai_service.generate_linkedin_optimized_script(
                    document_context=document_context,  # Pass full context - method handles optimization
                    topic=request.topic,
                    duration=duration_for_script,
                    target_audience=request.target_audience,
                    key_message=request.key_message,
                    video_model=video_model_for_script,  # Pass video model so AI can make appropriate duration decisions
                    user_context=user_context_summary  # Pass user context for personalization
                )
                
                video_script = script_result["script"]
                sora_prompt = script_result["sora_prompt"]
                linkedin_optimization = script_result.get("linkedin_optimization", "")
                key_insights = script_result.get("key_insights", "")
                document_analysis = script_result.get("document_analysis", "")
                
                print(f"[API] ✓ LinkedIn-optimized script generated ({len(video_script)} characters)")
                print(f"[API] ✓ Sora prompt optimized ({len(sora_prompt)} characters)")
            
            except Exception as script_error:
                print(f"[API] ⚠️ Script generation error: {str(script_error)}")
                import traceback
                traceback.print_exc()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to generate LinkedIn-optimized video script: {str(script_error)}"
                )
        
        # Step 4: Generate video using selected model (Sora or Veo 3) - ONLY if script is approved
        video_job = None
        
        # Only generate video if script is pre-approved
        if request.approved and request.script:
            print(f"[API] 🎬 Generating video with {video_model} using approved script...")
        elif not request.approved:
            print(f"[API] ⏸️ Script generated. Waiting for user approval before generating video.")
            print(f"[API]   Selected video model: {video_model} (will be used when script is approved)")
        
        if request.approved:
            try:
                # Get AI-decided duration from script result, or use provided/default
                # When script is pre-approved, script_result might be minimal, so handle both cases
                if script_result and isinstance(script_result, dict):
                    ai_decisions = script_result.get("ai_decisions", {})
                else:
                    ai_decisions = {}
                # Default duration: 8s for Sora, 60s for Veo 3 (to ensure quality longer videos)
                default_duration = 60 if (video_model == "veo-3" or video_model == "veo3") else 8
                video_duration = ai_decisions.get("duration") if ai_decisions else (request.duration or default_duration)
                
                print(f"[API] 🔍 Initial video_duration: {video_duration}s (from AI: {ai_decisions.get('duration') if ai_decisions else 'N/A'}, request: {request.duration}, default: {default_duration})")
                
                # CRITICAL FOR VEO 3: Force override if duration is 4, 8, or 12 (Sora constraints)
                # ALWAYS ensure Veo 3 gets at least 50 seconds for quality content
                if (video_model == "veo-3" or video_model == "veo3"):
                    original_duration = video_duration
                    # ALWAYS override to at least 50 seconds for Veo 3
                    if video_duration in [4, 8, 12]:
                        print(f"[API] ⚠️ CRITICAL: Duration {video_duration}s is a Sora constraint. FORCING Veo 3 to 50s for quality content.")
                        video_duration = 50
                    elif video_duration < 50:  # Changed from 30 to 50 to ensure longer videos
                        print(f"[API] ⚠️ Duration {video_duration}s is too short for Veo 3. Overriding to 50s for quality content.")
                        video_duration = 50
                    elif video_duration > 148:
                        print(f"[API] ⚠️ Duration {video_duration}s exceeds Veo 3 maximum. Clamping to 148s.")
                        video_duration = 148
                    
                    if original_duration != video_duration:
                        print(f"[API] ✅ Veo 3 duration OVERRIDDEN: {original_duration}s -> {video_duration}s")
                    else:
                        print(f"[API] ✅ Veo 3 duration confirmed: {video_duration}s (no override needed)")
                
                if video_model == "veo-3" or video_model == "veo3":
                    # Use Veo 3 for video generation
                    if not veo3_service.project_id:
                        print(f"[API] ⚠️ Veo 3 not configured, falling back to Sora 2")
                        video_model = "sora-2"
                    else:
                        # Validate Veo 3 duration constraints
                        # Initial generation: 4, 6, or 8 seconds
                        # Can be extended up to 148 seconds using extension feature
                        valid_initial_durations = [4, 6, 8]
                        target_duration = video_duration
                        
                        print(f"[API] 🎯 Veo 3 target_duration: {target_duration}s")
                        
                        # CRITICAL: After override, target_duration should ALWAYS be >= 50 for Veo 3
                        # So this should ALWAYS trigger the extension path
                        # CRITICAL: After override, target_duration should ALWAYS be >= 50 for Veo 3
                        # So we should ALWAYS use the extension path
                        if target_duration <= 8:
                            # This should NEVER happen after the override, but handle it just in case
                            print(f"[API] ⚠️ WARNING: target_duration is {target_duration}s (should be >= 50 after override)!")
                            print(f"[API] ⚠️ FORCING to extension path anyway for quality content")
                            # Force extension path even if target_duration <= 8
                            veo3_duration = 8
                            # Calculate extensions needed (even for short videos, extend to at least 15s)
                            import math
                            min_target = max(target_duration, 15)  # At least 15 seconds
                            remaining_seconds = min_target - 8
                            extension_count = min(20, math.ceil(remaining_seconds / 7))
                            needs_extension = extension_count > 0
                            print(f"[API] 📹 Veo 3: Forced extension path - Generating {veo3_duration}s initial video, will extend {extension_count} times (7s each) to reach ~{8 + (extension_count * 7)}s")
                        else:
                            # Need extension: start with 8 seconds, then extend
                            veo3_duration = 8  # Start with maximum initial generation
                            # Calculate how many 7-second extensions needed
                            remaining_seconds = target_duration - 8
                            # Calculate extension count: (remaining_seconds / 7) rounded up, max 20
                            import math
                            extension_count = min(20, math.ceil(remaining_seconds / 7))
                            needs_extension = extension_count > 0
                            print(f"[API] 📹 Veo 3: Generating {veo3_duration}s initial video, will extend {extension_count} times (7s each) to reach ~{8 + (extension_count * 7)}s")
                            print(f"[API] 📹 Extension calculation: target={target_duration}s, remaining={remaining_seconds}s, extensions={extension_count}")
                        
                        # Guardrail: Warn if duration is very long
                        if veo3_duration > 30:
                            print(f"[API] ⚠️ Veo 3 generation with {veo3_duration}s duration may take 3-5 minutes")
                        
                        try:
                            print(f"[API] 🎥 Using Veo 3 for video generation (duration: {veo3_duration}s)")
                            veo3_result = await veo3_service.generate_video(
                                prompt=sora_prompt[:2000],  # Veo 3 has prompt length limits
                                duration=veo3_duration,
                                resolution="1280x720"
                            )
                            
                            # Store extension metadata for automatic extension after base video completes
                            if needs_extension and extension_count > 0:
                                extension_metadata = {
                                    "needs_extension": needs_extension,
                                    "extension_count": extension_count,
                                    "target_duration": target_duration,
                                    "current_duration": veo3_duration,
                                    "extensions_completed": 0,
                                    "original_job_id": veo3_result.get("job_id"),
                                    "base_job_id": veo3_result.get("job_id")
                                }
                                if not hasattr(veo3_service, '_extension_cache'):
                                    veo3_service._extension_cache = {}
                                job_id_for_cache = veo3_result.get("job_id")
                                veo3_service._extension_cache[job_id_for_cache] = extension_metadata
                                print(f"[API] ✓ Veo 3 video generation started (will auto-extend {extension_count} times after base video completes)")
                            else:
                                print(f"[API] ✓ Veo 3 video generation started (no extensions needed)")
                            
                            video_job = {
                                "job_id": veo3_result.get("job_id"),
                                "status": veo3_result.get("status", "queued"),
                                "progress": veo3_result.get("progress", 0),
                                "model": veo3_result.get("model", "veo-3"),
                                "video_url": veo3_result.get("video_url"),
                                "created_at": veo3_result.get("created_at", 0),
                                "needs_extension": needs_extension,
                                "extension_count": extension_count,
                                "target_duration": target_duration,
                                "current_duration": veo3_duration
                            }
                            
                            print(f"[API] ✓ Veo 3 video generation started: {video_job['job_id']}")
                            if needs_extension and extension_count > 0:
                                print(f"[API] ✓ Base video generation started (will auto-extend {extension_count} times)")
                            else:
                                print(f"[API] ✓ Base video generation started (no extensions needed)")
                            
                            # Veo 3 generation successful - return early, don't fall through to Sora
                            return {
                                "success": True,
                                "video_job": video_job,
                                "script": video_script,
                                "sora_prompt": sora_prompt,
                                "linkedin_optimization": linkedin_optimization,
                                "key_insights": key_insights,
                                "document_analysis": document_analysis,
                                "video_options": video_options
                            }
                        except Exception as veo3_error:
                            error_str = str(veo3_error)
                            # Check if it's a content policy violation
                            if "Content Policy Violation" in error_str or "violate" in error_str.lower() or "usage guidelines" in error_str.lower():
                                print(f"[API] ❌ Veo 3 generation failed due to content policy violation")
                                print(f"[API]   Error: {error_str}")
                                print(f"[API]   This prompt contains words that violate Vertex AI's usage guidelines.")
                                print(f"[API]   Even after sanitization, some terms may still trigger content filters.")
                                print(f"[API]   Falling back to Sora 2 (more lenient content policy)...")
                                video_model = "sora-2"
                            else:
                                print(f"[API] ❌ Veo 3 generation failed, falling back to Sora 2: {veo3_error}")
                                video_model = "sora-2"
                
                # Use Sora 2 (default or fallback)
                if video_model == "sora-2":
                    # CRITICAL: Sora only supports 4, 8, or 12 seconds - validate and clamp
                    # IMPORTANT: This validation ONLY applies to Sora, NOT Veo 3
                    valid_durations = [4, 8, 12]
                    original_duration = video_duration
                    if video_duration not in valid_durations:
                        # Find nearest valid duration
                        video_duration = min(valid_durations, key=lambda x: abs(x - video_duration))
                        print(f"[API] ⚠️ CRITICAL: Adjusted duration from {original_duration}s to valid Sora duration: {video_duration}s")
                    
                    # Double-check validation before Sora API call
                    if video_duration not in valid_durations:
                        video_duration = 8  # Safe fallback
                        print(f"[API] ⚠️ CRITICAL: Forced duration to safe fallback: {video_duration}s")
                    
                    assert video_duration in valid_durations, f"Duration must be one of {valid_durations}, got {video_duration}"
                    
                    print(f"[API] Using video duration: {video_duration} seconds (VALIDATED for Sora 2)")
                    if ai_decisions.get("duration"):
                        print(f"[API] ✓ Duration decided by AI based on content analysis")
                # Note: Veo 3 generation is handled above and returns early if successful
                # This elif block should never be reached for Veo 3, but keeping for safety
                elif video_model == "veo-3" or video_model == "veo3":
                    # This should not happen - Veo 3 should have been handled above
                    print(f"[API] ⚠️ WARNING: Veo 3 reached fallback block - this should not happen")
                    print(f"[API] ⚠️ Veo 3 generation should have completed above. This is a logic error.")
                    raise HTTPException(
                        status_code=500,
                        detail="Veo 3 generation logic error - please check backend logs"
                    )
                
            except Exception as video_error:
                print(f"[API] ⚠️ Video generation error: {str(video_error)}")
                import traceback
                traceback.print_exc()
                # Don't fail completely - return script even if video generation fails
                print(f"[API] Returning script without video (user can retry video generation)")
        
        # Create summary of document context for response
        context_summary = document_context[:500] + "..." if len(document_context) > 500 else document_context
        
        # Record video generation in user context (if user is authenticated)
        if user_id:
            try:
                ai_decisions_dict = script_result.get("ai_decisions", {}) if script_result else {}
                user_context_service.record_video_generation(user_id, {
                    "topic": ai_decisions_dict.get("topic") or request.topic,
                    "platform": request.platform or "linkedin",
                    "video_model": video_model,
                    "duration": ai_decisions_dict.get("duration") or request.duration or 8,
                    "script": video_script[:500] if video_script else "",
                    "approved": request.approved,
                    "edited": bool(request.script and request.script != video_script)
                })
            except Exception as ctx_error:
                print(f"[API] ⚠️ Could not record user context: {ctx_error}")
        
        # Ensure script_result is always a dict for response
        if not script_result:
            script_result = {"ai_decisions": {}}
        
        return DocumentVideoResponse(
            script=video_script,
            video_job=video_job,
            document_context_summary=context_summary,
            linkedin_optimization=linkedin_optimization,
            key_insights=key_insights,
            document_analysis=document_analysis,
            ai_decisions=script_result.get("ai_decisions", {}) if script_result else {},
            video_options=video_options
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error creating video from documents: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ===== USER CONTEXT & PREFERENCES ENDPOINTS =====

@app.post("/api/user/preferences", response_model=UserPreferencesResponse)
async def update_user_preferences(request: UserPreferencesRequest):
    """
    Update user preferences for personalized content generation.
    These preferences will be used to enhance future script and video generation.
    """
    try:
        # TODO: Get user_id from authentication token
        user_id = "guest_user"  # Placeholder - replace with actual user ID from auth
        
        # Update preferences
        preferences_dict = request.dict(exclude_none=True)
        user_context_service.update_preferences(user_id, preferences_dict)
        
        return UserPreferencesResponse(
            preferences=preferences_dict,
            message="Preferences updated successfully. These will be used to personalize future content generation."
        )
    except Exception as e:
        print(f"[API] Error updating user preferences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/context", response_model=UserContextResponse)
async def get_user_context():
    """
    Get comprehensive user context including preferences, content history, and behavioral patterns.
    """
    try:
        # TODO: Get user_id from authentication token
        user_id = "guest_user"  # Placeholder - replace with actual user ID from auth
        
        context_dict = user_context_service.get_user_context(user_id)
        
        # Convert dict to JSON string for the response
        import json
        context_str = json.dumps(context_dict, indent=2)
        
        return UserContextResponse(context=context_str)
    except Exception as e:
        print(f"[API] Error getting user context: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/user/preferred-settings")
async def get_preferred_settings():
    """
    Get user's preferred settings for auto-filling forms (video model, duration, platform, etc.)
    """
    try:
        # TODO: Get user_id from authentication token
        user_id = "guest_user"  # Placeholder - replace with actual user ID from auth
        
        settings = user_context_service.get_preferred_settings(user_id)
        
        return settings
    except Exception as e:
        print(f"[API] Error getting preferred settings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== HYPERSPELL ENDPOINTS ====================

# Memory endpoints - using MemoryService (S3 + Mem0) directly

@app.post("/api/memory/query")
async def query_memories(
    query: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Query memory layer for relevant context.
    
    Request body:
    {
        "query": "What is the project deadline?",
        "max_results": 5
    }
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available. Please check S3 and Mem0 configuration."
            )
        
        # Normalize user_id consistently
        user_id = normalize_user_id(current_user)
        query_text = query.get("query", "")
        max_results = query.get("max_results", 5)
        
        if not query_text:
            raise HTTPException(status_code=400, detail="Query text is required")
        
        result = await memory_service.query_memories(user_id, query_text, max_results)
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to query memories. Please ensure memories are stored."
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error querying memories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/upload")
async def upload_to_memory(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a document to memory layer.
    Supported formats: PDF, DOCX, TXT, etc.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available. Please check S3 and Mem0 configuration."
            )
        
        # Normalize user_id consistently
        user_id = normalize_user_id(current_user)
        print(f"[API] Uploading document to Memory (S3 + Mem0) for user: {user_id}")
        
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        try:
            # Extract text from document first (for PDFs, DOCX, etc.)
            file_ext = os.path.splitext(file.filename)[1].lower()
            text_content = None
            
            # For PDF, DOCX, DOC, TXT - extract text and save as text memory
            if file_ext in ('.pdf', '.docx', '.doc', '.txt', '.md'):
                try:
                    text_content = await document_service.extract_text(tmp_path, file.content_type or '')
                    print(f"[API] Extracted {len(text_content)} characters from {file.filename}")
                except Exception as e:
                    print(f"[API] Warning: Failed to extract text from {file.filename}: {e}")
            
            # If we have extracted text, append it to unified brand context memory
            if text_content and len(text_content.strip()) > 0:
                print(f"[API] Appending document to unified brand context memory")
                document_content = f"Document: {file.filename}\n\n{text_content}"
                result = await memory_service.append_to_unified_brand_context(
                    user_id=user_id,
                    new_content=document_content,
                    content_type="document"
                )
                
                if result is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to save document to unified brand context."
                    )
                
                resource_id = result.get("resource_id")
                if not resource_id:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to save document: Invalid resource_id returned."
                    )
                
                return {
                    "success": True,
                    "resource_id": resource_id,
                    "filename": file.filename,
                    "message": "Document added to unified brand context successfully",
                    "context_updated": True,
                    "verified": True
                }
            else:
                # Fallback: Upload binary file to S3
                print(f"[API] Uploading binary file to S3 (text extraction not available)")
                result = await memory_service.upload_document(
                    user_id=user_id,
                    file_path=tmp_path,
                    filename=file.filename
                )
                
                if result is None:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to upload document."
                    )
                
                return {
                    "success": True,
                    "resource_id": result.get("resource_id"),
                    "filename": result.get("filename"),
                    "message": "Document uploaded successfully to memory layer",
                    "verified": True
                }
        finally:
            # Clean up temporary file
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error uploading to memory: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/memory/add-memory")
async def add_memory(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Add a text memory to memory layer.
    For brand context related content (competitors, brand info, etc.), uses unified brand context.
    For other content, uses regular memory storage.
    
    Request body:
    {
        "text": "Your memory text here...",
        "collection": "optional_collection_name"
    }
    """
    try:
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available. Please check S3 and Mem0 configuration."
            )
        
        text = request.get("text", "").strip()
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        collection = request.get("collection", "user_memories")
        # Normalize user_id consistently
        user_id = normalize_user_id(current_user) if current_user else "anonymous"
        
        # Brand context related collections should use unified brand context
        brand_context_collections = ["competitors", "brand_context", "brand", "documents", "company", "market"]
        use_unified = collection.lower() in [c.lower() for c in brand_context_collections]
        
        if use_unified:
            print(f"[API] Adding to unified brand context for user: {user_id} (collection: {collection})")
            result = await memory_service.append_to_unified_brand_context(
                user_id=user_id,
                new_content=text,
                content_type=collection
            )
            message = "Content added to unified brand context successfully"
        else:
            print(f"[API] Adding text memory for user: {user_id} (collection: {collection})")
            result = await memory_service.add_text_memory(
                user_id=user_id,
                text=text,
                collection=collection
            )
            message = "Memory added successfully"
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to add memory."
            )
        
        resource_id = result.get("resource_id")
        if not resource_id:
            raise HTTPException(
                status_code=500,
                detail="Failed to add memory: Invalid resource_id returned."
            )
        
        return {
            "success": True,
            "resource_id": resource_id,
            "message": message,
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "collection": collection,
            "context_updated": use_unified,
            "verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error adding memory: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to add memory: {str(e)}")


@app.get("/api/memory/status")
async def get_memory_status():
    """
    Check memory service status and availability.
    Public endpoint - no authentication required.
    """
    try:
        available = memory_service.is_available()
        s3_available = memory_service.s3_service.is_available() if hasattr(memory_service, 's3_service') else False
        mem0_available = memory_service.mem0_service.is_available() if hasattr(memory_service, 'mem0_service') else False
        
        return {
            "available": available,
            "s3_available": s3_available,
            "mem0_available": mem0_available,
            "message": "Memory service is available" if available else "Memory service is not configured. Check S3 and Mem0 configuration."
        }
    except Exception as e:
        print(f"[API] Error checking memory status: {str(e)}")
        return {
            "available": False,
            "message": f"Error checking status: {str(e)}"
        }


# ===== BRAND WEBSITE ANALYSIS ENDPOINT =====

@app.post("/api/brand/scrape-website")
async def analyze_brand_website(
    request: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a brand's website and add the extracted information to brand context.
    
    Request body:
    {
        "url": "https://yourcompany.com"
    }
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        url = request.get("url", "").strip()
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")
        
        # Validate URL format
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid URL format. Please include http:// or https://")
        
        print(f"[API] Analyzing website: {url}")
        
        # Use web research service to scrape website content
        import httpx
        from bs4 import BeautifulSoup
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                html_content = response.text
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"Failed to access website: {e.response.status_code}")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to connect to website: {str(e)}")
        
        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else url
        title = title.strip() if title else url
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Extract meta keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        keywords = meta_keywords.get('content', '') if meta_keywords else ''
        
        # Extract Open Graph data
        og_title = soup.find('meta', property='og:title')
        og_description = soup.find('meta', property='og:description')
        og_site_name = soup.find('meta', property='og:site_name')
        
        # Extract main text content
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
        
        # Get text from main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'main', 'main-content']) or soup.body
        
        text_content = ""
        if main_content:
            # Get all paragraphs and headings
            for elem in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
                text = elem.get_text(strip=True)
                if text and len(text) > 20:  # Filter out short snippets
                    text_content += text + "\n\n"
        
        # Limit text content
        text_content = text_content[:10000] if text_content else ""
        
        # Build brand context from scraped data
        brand_context_parts = [
            f"WEBSITE: {url}",
            f"TITLE: {title}",
        ]
        
        if og_site_name:
            brand_context_parts.append(f"BRAND NAME: {og_site_name.get('content', '')}")
        
        if description or (og_description and og_description.get('content')):
            desc = description or og_description.get('content', '')
            brand_context_parts.append(f"DESCRIPTION: {desc}")
        
        if keywords:
            brand_context_parts.append(f"KEYWORDS: {keywords}")
        
        if text_content:
            brand_context_parts.append(f"\nWEBSITE CONTENT:\n{text_content}")
        
        brand_context_text = "\n".join(brand_context_parts)
        
        print(f"[API] Extracted {len(brand_context_text)} characters from website")
        
        # Save to memory service (unified brand context)
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available. Please check S3 and Mem0 configuration."
            )
        
        user_id = normalize_user_id(current_user)
        print(f"[API] Saving website content to unified brand context for user: {user_id}")
        
        result = await memory_service.append_to_unified_brand_context(
            user_id=user_id,
            new_content=brand_context_text,
            content_type="website"
        )
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to save website content to brand context."
            )
        
        resource_id = result.get("resource_id")
        
        return {
            "success": True,
            "url": url,
            "title": title,
            "description": description or (og_description.get('content', '') if og_description else ''),
            "resource_id": resource_id,
            "message": "Website analyzed and added to brand context successfully",
            "content_length": len(brand_context_text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error analyzing website: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze website: {str(e)}")


@app.get("/api/memory/documents")
async def list_user_documents(
    current_user: User = Depends(get_current_user)
):
    """
    List all documents uploaded by the user.
    Returns documents stored in memory (Mem0) with metadata.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available."
            )
        
        user_id = normalize_user_id(current_user)
        print(f"[API] Listing documents for user: {user_id}")
        
        # List memories filtered by content_type="document"
        documents = await memory_service.mem0_service.list_memories(
            user_id=user_id,
            content_type="document",
            limit=100
        )
        
        # Format response
        formatted_docs = []
        for doc in documents:
            formatted_docs.append({
                "id": doc.get("id"),
                "resource_id": doc.get("id"),  # For compatibility
                "filename": doc.get("filename") or "Unknown",
                "content_preview": doc.get("content_preview", ""),
                "content_length": doc.get("content_length", 0),
                "created_at": doc.get("created_at"),
                "metadata": doc.get("metadata", {})
            })
        
        print(f"[API] Found {len(formatted_docs)} documents for user {user_id}")
        return {
            "success": True,
            "documents": formatted_docs,
            "count": len(formatted_docs)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error listing documents: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/api/memory/documents/{resource_id}")
async def delete_user_document(
    resource_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a document and its associated context from memory.
    Removes the document from Mem0 (and optionally from S3 if stored there).
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available."
            )
        
        user_id = normalize_user_id(current_user)
        print(f"[API] Deleting document {resource_id} for user: {user_id}")
        
        # Delete from Mem0
        success = await memory_service.mem0_service.delete_memory(
            user_id=user_id,
            memory_id=resource_id
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete document from memory."
            )
        
        # Note: S3 files are not automatically deleted as they may be referenced by multiple memories
        # If you want to delete S3 files too, you'd need to track the S3 key in metadata
        
        print(f"[API] Successfully deleted document {resource_id} for user {user_id}")
        return {
            "success": True,
            "message": "Document and its context have been removed successfully",
            "resource_id": resource_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error deleting document: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.post("/api/memory/summaries")
async def get_context_summaries(
    current_user: User = Depends(get_current_user)
):
    """
    Get all 4 context summaries (Overall, Brand, Competitor, Market) using the same approach as marketing posts.
    Uses get_all_memories_context() to get all memories, then GPT to summarize for each section.
    """
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        if not memory_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Memory service is not available. Please check S3 and Mem0 configuration."
            )
        
        if not openai_service:
            raise HTTPException(
                status_code=503,
                detail="OpenAI service is not available. Please set OPENAI_API_KEY environment variable."
            )
        
        # Use normalized email as user_id (same as marketing posts)
        # CRITICAL: Normalize user_id consistently - Mem0 stores with lowercase email
        user_id = normalize_user_id(current_user)
        print(f"[API] Getting context summaries for user: {user_id}")
        
        # Step 1: Get unified brand context from Memory (S3 + Mem0)
        print(f"[API] Getting unified brand context from Memory (S3 + Mem0)...")
        all_memories_context = await memory_service.get_all_memories_context(user_id)
        
        if not all_memories_context or len(all_memories_context.strip()) < 10:
            print(f"[API] No unified brand context found for user: {user_id}")
            print(f"[API] DEBUG: Memory service available: {memory_service.is_available()}")
            print(f"[API] DEBUG: Mem0 service available: {memory_service.mem0_service.is_available() if hasattr(memory_service, 'mem0_service') else 'N/A'}")
            return {
                "overall_summary": "No context available. Upload documents, add competitors, or generate posts to build your brand context.",
                "brand_context": "No brand context available. Upload documents about your brand, products, or services.",
                "competitor_context": "No competitor information available. Add competitors to see competitive analysis.",
                "market_context": "No market context available. Add market research or industry information."
            }
        
        print(f"[API] ✓ Retrieved unified brand context ({len(all_memories_context)} chars)")
        
        # Use unified context for all summaries (brand context contains all user information)
        combined_brand_context = all_memories_context
        combined_competitor_context = all_memories_context
        
        # Step 2: Use GPT to generate summaries for each section (all using the same context)
        import asyncio
        
        async def generate_summary(prompt: str, section_name: str) -> str:
            """Helper to generate a summary using Claude (Bedrock) or OpenAI"""
            try:
                # Custom system message for specific contexts
                system_message = f"You are an expert at analyzing and summarizing brand context. Extract and summarize relevant information for {section_name}."
                if "competitor" in section_name.lower():
                    system_message = "You are an expert at identifying and summarizing competitor information. Your task is to extract ALL competitor names, competitive analysis, and competitive landscape information from the provided context. Be thorough and list specific competitor names when found."
                elif "brand" in section_name.lower():
                    system_message = "You are an expert at identifying and summarizing brand information. Your task is to extract ALL brand-specific details including brand guidelines, company information, products, services, company values, brand identity, and business context from the provided context. Be thorough and include specific brand details when found."
                
                summary = None
                llm_used = None
                
                # Try Bedrock (Claude Sonnet 4.5) first
                if bedrock_service and bedrock_service.is_available():
                    try:
                        # Use Claude Sonnet 4.5 inference profile ARN
                        sonnet_4_5_arn = "arn:aws:bedrock:us-east-1:222634391096:inference-profile/global.anthropic.claude-sonnet-4-5-20250929-v1:0"
                        print(f"[API] 🤖 Using AWS Bedrock (Claude Sonnet 4.5) for {section_name} summary...")
                        summary = await bedrock_service.generate_text(
                            prompt=prompt,
                            system_message=system_message,
                            max_tokens=500,
                            temperature=0.7,
                            model=sonnet_4_5_arn,
                            use_converse_api=True  # Required for Sonnet 4.5
                        )
                        if summary:
                            llm_used = "AWS Bedrock (Claude Sonnet 4.5)"
                            print(f"[API] ✅ {section_name} summary generated with {llm_used} ({len(summary)} chars)")
                            return summary
                    except Exception as bedrock_error:
                        print(f"[API] ⚠️ AWS Bedrock failed for {section_name}, trying Anthropic Claude API: {bedrock_error}")
                else:
                    print(f"[API] ℹ️ AWS Bedrock not available for {section_name}, trying Anthropic Claude API...")
                
                # Fallback to Anthropic Claude API
                if not summary and openai_service and openai_service.claude_available:
                    try:
                        print(f"[API] 🤖 Using Anthropic Claude API (direct) for {section_name} summary...")
                        summary = await openai_service.generate_text_with_claude(
                            prompt=prompt,
                            system_message=system_message,
                            max_tokens=500,
                            temperature=0.7
                        )
                        if summary:
                            llm_used = "Anthropic Claude API (direct)"
                            print(f"[API] ✅ {section_name} summary generated with {llm_used} ({len(summary)} chars)")
                            return summary
                    except Exception as claude_error:
                        print(f"[API] ⚠️ Anthropic Claude API failed for {section_name} (may have hit usage limits), falling back to OpenAI: {claude_error}")
                else:
                    if not summary:
                        print(f"[API] ℹ️ Anthropic Claude API not available for {section_name}, using OpenAI...")
                
                # Final fallback to OpenAI
                if not summary:
                    print(f"[API] 🤖 Using OpenAI ({openai_service.model}) for {section_name} summary...")
                    completion = await openai_service.client.chat.completions.create(
                        model=openai_service.model,
                        messages=[
                            {
                                "role": "system",
                                "content": system_message
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    summary = completion.choices[0].message.content.strip()
                    llm_used = f"OpenAI ({openai_service.model})"
                    print(f"[API] ✅ {section_name} summary generated with {llm_used} ({len(summary)} chars)")
                
                return summary
            except Exception as e:
                print(f"[API] Error generating {section_name} summary: {e}")
                return f"Error generating {section_name} summary. Please try again."
        
        # Generate all 4 summaries in parallel
        prompts = {
            "overall_summary": f"""Based on the following brand context from all stored memories, provide a comprehensive overall summary (2-3 sentences) that captures the key information about this brand, business, and context:

{all_memories_context[:8000]}

Provide a concise overall summary that gives a high-level view of the brand, business, and stored context.""",
            
            "brand_context": f"""Based on the following context from all stored memories (including brand-specific queries), extract and summarize ONLY the brand-specific information (brand guidelines, company information, products, services, company values, brand identity, business context):

{combined_brand_context[:8000]}

Focus on brand identity, company information, products, services, and brand values. Provide a clear summary (2-3 sentences).""",
            
            "competitor_context": f"""Based on the following context from all stored memories (including competitor-specific queries), extract and summarize ALL competitor information:

{combined_competitor_context[:8000]}

Look for:
- Lists of competitor names (e.g., "competitors include X, Y, Z")
- Documents or memories tagged with "competitors" or "competitive analysis"
- Any mentions of competing companies, brands, or products
- Competitive landscape information
- Market competitors

IMPORTANT: If you find ANY competitor names, companies, or competitive information, include them in your summary. List the specific competitor names you find.

Provide a clear summary (2-4 sentences) that includes the competitor names and any relevant competitive context. If no competitor information is found, state "No competitor information is found in the provided context." Otherwise, be specific about which competitors were identified.""",
            
            "market_context": f"""Based on the following context from all stored memories, extract and summarize ONLY the market information (market trends, industry analysis, market research, target audience, industry context):

{all_memories_context[:8000]}

Focus on market trends, industry analysis, target audience, and market research. Provide a clear summary (2-3 sentences). If no market information is found, state that."""
        }
        
        # Run all summaries in parallel
        tasks = [
            generate_summary(prompts["overall_summary"], "Overall Summary"),
            generate_summary(prompts["brand_context"], "Brand Context"),
            generate_summary(prompts["competitor_context"], "Competitor Context"),
            generate_summary(prompts["market_context"], "Market Context")
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Extract results (handle exceptions)
        overall_summary = results[0] if not isinstance(results[0], Exception) else "Error generating overall summary."
        brand_context = results[1] if not isinstance(results[1], Exception) else "Error generating brand context summary."
        competitor_context = results[2] if not isinstance(results[2], Exception) else "Error generating competitor context summary."
        market_context = results[3] if not isinstance(results[3], Exception) else "Error generating market context summary."
        
        return {
            "overall_summary": overall_summary,
            "brand_context": brand_context,
            "competitor_context": competitor_context,
            "market_context": market_context
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Error generating context summaries: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# Hyperspell endpoints removed - all functionality now uses MemoryService (S3 + Mem0) directly


# ===== SEO/AEO ENDPOINTS =====
@app.post("/api/seo-aeo/analyze", response_model=SEOAEOSummary)
async def analyze_seo_aeo(request: SEOAEOAnalysisRequest):
    """
    Start SEO/AEO analysis for a brand.
    Analyzes brand mentions in LLM responses, tracks competitors, and identifies sources.
    """
    if not seo_aeo_service:
        raise HTTPException(status_code=503, detail="SEO/AEO service not available. OpenAI API key required.")
    
    try:
        # Analyze website if URL provided
        brand_info = None
        if request.brand_url:
            brand_info = await seo_aeo_service.analyze_website(request.brand_url)
        
        # Generate prompts
        prompts = await seo_aeo_service.generate_prompts(
            brand_name=request.brand_name,
            brand_info=brand_info,
            topics=request.topics,
            num_prompts=request.num_prompts
        )
        
        # Analyze prompts (this may take a while, so we'll do it in background)
        # For now, we'll do a smaller batch synchronously and return results
        # In production, you'd want to make this async with job tracking
        
        # Limit to first 20 for initial response (can be made async later)
        sample_prompts = prompts[:min(20, len(prompts))]
        results = await seo_aeo_service.analyze_batch_prompts(
            prompts=sample_prompts,
            brand_name=request.brand_name,
            competitors=request.competitors
        )
        
        # Calculate statistics
        total_tested = len(results)
        brand_mentions = sum(1 for r in results if r.get("brand_mentioned", False))
        mention_rate = (brand_mentions / total_tested * 100) if total_tested > 0 else 0
        
        # Collect all sources
        all_sources = []
        source_counts = {}
        for result in results:
            for source in result.get("sources", []):
                domain = source.get("domain", "")
                if domain:
                    source_counts[domain] = source_counts.get(domain, 0) + 1
                    if domain not in [s.get("domain") for s in all_sources]:
                        source_type = await seo_aeo_service.categorize_source(domain)
                        all_sources.append({
                            "domain": domain,
                            "url": source.get("url", ""),
                            "title": source.get("title"),
                            "snippet": source.get("snippet"),
                            "source_type": source_type
                        })
        
        # Sort sources by count
        top_sources = sorted(
            [{"domain": d, "mention_count": c} for d, c in source_counts.items()],
            key=lambda x: x["mention_count"],
            reverse=True
        )[:10]
        
        # Add source types to top sources
        for source in top_sources:
            source["source_type"] = await seo_aeo_service.categorize_source(source["domain"])
        
        # Calculate competitor stats
        competitor_stats = []
        if request.competitors:
            for competitor in request.competitors:
                mentions = sum(1 for r in results if competitor in r.get("competitors_mentioned", []))
                rate = (mentions / total_tested * 100) if total_tested > 0 else 0
                competitor_stats.append({
                    "competitor": competitor,
                    "mention_rate": round(rate, 1),
                    "total_prompts": total_tested,
                    "mentions": mentions
                })
        
        # Find top competitor
        top_competitor = None
        top_competitor_rate = None
        if competitor_stats:
            top_comp = max(competitor_stats, key=lambda x: x["mention_rate"])
            top_competitor = top_comp["competitor"]
            top_competitor_rate = top_comp["mention_rate"]
        
        # Group by topic (simplified - in production, you'd extract topics from prompts)
        topic_stats = []
        # For now, create a simple topic distribution
        # In production, you'd analyze prompts to extract actual topics
        
        # Format recent results
        recent_results = []
        for result in results[:10]:
            sources_list = [
                SourceCitation(
                    domain=s.get("domain", ""),
                    url=s.get("url", ""),
                    title=s.get("title"),
                    snippet=s.get("snippet")
                )
                for s in result.get("sources", [])
            ]
            recent_results.append(PromptResult(
                prompt=result.get("prompt", ""),
                topic="General",  # Would be extracted from prompt analysis
                brand_mentioned=result.get("brand_mentioned", False),
                response=result.get("response", "")[:200] + "..." if len(result.get("response", "")) > 200 else result.get("response", ""),
                sources=sources_list,
                competitors_mentioned=result.get("competitors_mentioned", []),
                created_at=datetime.now().isoformat()
            ))
        
        return SEOAEOSummary(
            brand_mention_rate=round(mention_rate, 1),
            total_prompts_tested=total_tested,
            total_mentions=brand_mentions,
            top_competitor=top_competitor,
            top_competitor_rate=top_competitor_rate,
            total_sources=len(all_sources)
        )
        
    except Exception as e:
        print(f"[API] Error in SEO/AEO analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze SEO/AEO: {str(e)}")


@app.post("/api/seo-aeo/full-analysis")
async def full_seo_aeo_analysis(request: SEOAEOAnalysisRequest):
    """
    Run full SEO/AEO analysis with all prompts (may take longer).
    Returns complete analysis with all statistics.
    Note: This endpoint may take several minutes to complete depending on num_prompts.
    """
    """
    Run full SEO/AEO analysis with all prompts (may take longer).
    Returns complete analysis with all statistics.
    """
    print(f"[API] SEO/AEO Analysis request received: brand={request.brand_name}, prompts={request.num_prompts}")
    if not seo_aeo_service:
        raise HTTPException(status_code=503, detail="SEO/AEO service not available. OpenAI API key required.")
    
    try:
        print(f"[API] Starting SEO/AEO analysis for brand: {request.brand_name}")
        # Analyze website if URL provided
        brand_info = None
        if request.brand_url:
            print(f"[API] Analyzing website: {request.brand_url}")
            brand_info = await seo_aeo_service.analyze_website(request.brand_url)
            print(f"[API] Website analysis complete")
        
        # Generate prompts
        print(f"[API] Generating {request.num_prompts} prompts...")
        prompts = await seo_aeo_service.generate_prompts(
            brand_name=request.brand_name,
            brand_info=brand_info,
            topics=request.topics,
            num_prompts=request.num_prompts
        )
        print(f"[API] Generated {len(prompts)} prompts")
        
        # Analyze all prompts (this is the time-consuming part)
        print(f"[API] Starting batch analysis of {len(prompts)} prompts...")
        results = await seo_aeo_service.analyze_batch_prompts(
            prompts=prompts,
            brand_name=request.brand_name,
            competitors=request.competitors,
            max_concurrent=5
        )
        print(f"[API] Batch analysis complete: {len(results)} results")
        
        # Calculate statistics
        total_tested = len(results)
        brand_mentions = sum(1 for r in results if r.get("brand_mentioned", False))
        mention_rate = (brand_mentions / total_tested * 100) if total_tested > 0 else 0
        
        # Collect all sources
        all_sources = []
        source_counts = {}
        for result in results:
            for source in result.get("sources", []):
                domain = source.get("domain", "")
                if domain:
                    source_counts[domain] = source_counts.get(domain, 0) + 1
                    if domain not in [s.get("domain") for s in all_sources]:
                        source_type = await seo_aeo_service.categorize_source(domain)
                        all_sources.append({
                            "domain": domain,
                            "url": source.get("url", ""),
                            "title": source.get("title"),
                            "snippet": source.get("snippet"),
                            "source_type": source_type
                        })
        
        # Sort sources by count
        top_sources = sorted(
            [{"domain": d, "mention_count": c} for d, c in source_counts.items()],
            key=lambda x: x["mention_count"],
            reverse=True
        )[:10]
        
        # Add source types to top sources
        for source in top_sources:
            source["source_type"] = await seo_aeo_service.categorize_source(source["domain"])
        
        # Calculate competitor stats
        competitor_stats = []
        top_competitor = None
        top_competitor_rate = None
        
        if request.competitors:
            for competitor in request.competitors:
                mentions = sum(1 for r in results if competitor in r.get("competitors_mentioned", []))
                rate = (mentions / total_tested * 100) if total_tested > 0 else 0
                competitor_stats.append({
                    "competitor": competitor,
                    "mention_rate": round(rate, 1),
                    "total_prompts": total_tested,
                    "mentions": mentions
                })
            
            if competitor_stats:
                top_comp = max(competitor_stats, key=lambda x: x["mention_rate"])
                top_competitor = top_comp["competitor"]
                top_competitor_rate = top_comp["mention_rate"]
        
        # Format recent results
        recent_results = []
        for result in results[:20]:
            sources_list = [
                SourceCitation(
                    domain=s.get("domain", ""),
                    url=s.get("url", ""),
                    title=s.get("title"),
                    snippet=s.get("snippet")
                )
                for s in result.get("sources", [])
            ]
            recent_results.append(PromptResult(
                prompt=result.get("prompt", ""),
                topic="General",  # Would be extracted from prompt analysis
                brand_mentioned=result.get("brand_mentioned", False),
                response=result.get("response", "")[:200] + "..." if len(result.get("response", "")) > 200 else result.get("response", ""),
                sources=sources_list,
                competitors_mentioned=result.get("competitors_mentioned", []),
                created_at=datetime.now().isoformat()
            ))
        
        # Create topic stats (simplified - in production, extract from prompts)
        topic_stats = []
        
        # Return summary with all data
        result = {
            "brand_mention_rate": round(mention_rate, 1),
            "total_prompts_tested": total_tested,
            "total_mentions": brand_mentions,
            "top_competitor": top_competitor,
            "top_competitor_rate": top_competitor_rate,
            "total_sources": len(all_sources),
            "topics": topic_stats,
            "competitors": competitor_stats,
            "top_sources": top_sources,
            "recent_results": [r.dict() if hasattr(r, 'dict') else r for r in recent_results]
        }
        print(f"[API] SEO/AEO Analysis complete: {total_tested} prompts tested, {brand_mentions} mentions ({mention_rate:.1f}%)")
        return result
        
    except Exception as e:
        print(f"[API] Error in full SEO/AEO analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to run full analysis: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
