from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
import asyncio
from dotenv import load_dotenv

from services.instagram_api import InstagramAPIService
from services.openai_service import OpenAIService
from services.linkedin_api import LinkedInAPIService
from services.oauth_service import OAuthService
from services.posting_service import PostingService
from services.email_service import EmailService
from services.browser_automation import BrowserAutomationService
from services.veo3_service import Veo3Service
from services.image_generation_service import ImageGenerationService
from services.video_composition_service import VideoCompositionService
from models.schemas import (
    VideoAnalysisRequest, VideoAnalysisResponse, ScrapedVideo, VideoResult,
    UserSignupRequest, UserLoginRequest, SocialMediaConnectionResponse,
    PostVideoRequest, PostVideoResponse,
    ManualInstagramPostRequest, ManualInstagramPostResponse,
    Veo3GenerateRequest, Veo3GenerateResponse, Veo3StatusResponse,
    ImageGenerateRequest, ImageGenerateResponse,
    SmartVideoCompositionRequest, SmartVideoCompositionResponse,
    InformationalVideoRequest, InformationalVideoResponse
)
from database import init_db, get_db, User, SocialMediaConnection, PostHistory
from auth_utils import get_password_hash, verify_password, create_access_token, get_current_user
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import uuid

# Load environment variables (try .env file first, then system environment)
# Get the directory where main.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(BASE_DIR, '.env')
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

app = FastAPI(title="Instagram Video to Sora Script Generator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:5173",
        "https://web-production-2b02d.up.railway.app",
        "https://*.vercel.app",
        "*"  # Allow all origins in production (you can restrict this later)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize services
instagram_service = InstagramAPIService()
linkedin_service = LinkedInAPIService()
oauth_service = OAuthService()
posting_service = PostingService()
email_service = EmailService()
browser_automation_service = BrowserAutomationService()
veo3_service = Veo3Service()
image_generation_service = ImageGenerationService()
video_composition_service = VideoCompositionService()
# Check for fine-tuned model in environment
fine_tuned_model = os.getenv("OPENAI_FINE_TUNED_MODEL")
# Only initialize OpenAI service if API key is available
openai_service = None
if OPENAI_API_KEY:
    openai_service = OpenAIService(api_key=OPENAI_API_KEY, anthropic_key=ANTHROPIC_API_KEY, fine_tuned_model=fine_tuned_model)
else:
    print("[INFO] OpenAI service not initialized - API key missing")

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
            "veo3": "✓ Active" if veo3_service.project_id else "⚠ Disabled - GOOGLE_CLOUD_PROJECT_ID not set",
            "image_generation": "✓ Active" if (image_generation_service.nanobanana_api_key or image_generation_service.openai_api_key) else "⚠ Disabled - NANOBANANA_API_KEY or OPENAI_API_KEY not set",
            "nanobanana": "✓ Active" if image_generation_service.nanobanana_api_key else "⚠ Disabled - NANOBANANA_API_KEY not set (superior text rendering)",
            "smart_composition": "✓ Active" if video_composition_service.openai_client else "⚠ Disabled",
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
        
        # Step 2: Research profile/page context using GPT-4 (works for all account types)
        print(f"[API] 🔍 Researching profile context (works for all account types)...")
        page_context = await openai_service.research_profile_context(profile_context)
        print(f"[API] ✓ Profile context researched: {len(page_context)} characters")
        
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
        
        # Step 4: Process each video with Build Hours features (analysis phase)
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
                
                # Generate regular Sora script (always works as fallback) with page context
                llm_provider = request.llm_provider or "openai"
                print(f"[API] Generating Sora script with page context using {llm_provider}...")
                sora_script = await openai_service.generate_sora_script(
                    transcription=transcription,
                    video_metadata={
                        'views': video['views'],
                        'likes': video['likes'],
                        'text': video['text']
                    },
                    target_duration=request.video_seconds or 8,
                    page_context=page_context,
                    llm_provider=llm_provider
                )
                
                # Try to generate structured Sora script (OpenAI Build Hours) with page context
                structured_sora = None
                try:
                    print(f"[API] 📐 Generating structured Sora script with page context (Build Hours: Structured Outputs)...")
                    structured_sora = await openai_service.generate_structured_sora_script(
                        transcription=transcription,
                        video_metadata={
                            'views': video['views'],
                            'likes': video['likes'],
                            'text': video['text'],
                            'duration': video.get('duration', 0)
                        },
                        thumbnail_analysis=thumbnail_analysis,  # Include Vision API data
                        target_duration=request.video_seconds or 8,  # Pass user's desired duration
                        page_context=page_context
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
                
                # Determine which video model to use
                video_model = request.video_model or "sora-2"
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
                        try:
                            print(f"[API] 🎥 Calling Veo 3 service.generate_video()...")
                            veo3_result = await veo3_service.generate_video(
                                prompt=video_prompt,
                                duration=sora_seconds,
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
                    print(f"[API] 🎬 Using Sora 2 for video generation...")
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
            
            # Clamp video_seconds to valid range (5-16) and closest valid value
            user_seconds = multi_request.video_seconds or 12
            user_seconds = max(5, min(16, user_seconds))  # Clamp to 5-16
            # Round to nearest valid value (4, 8, 12)
            if user_seconds <= 6:
                video_seconds = 4
            elif user_seconds <= 10:
                video_seconds = 8
            else:
                video_seconds = 12
            
            # Determine which video model to use for combined video
            video_model = multi_request.video_model or "sora-2-pro"
            print(f"[API] 🎬 Generating combined video using {video_model}...")
            
            if video_model == "veo-3":
                # Use Veo 3 for combined video
                if not veo3_service.project_id:
                    print(f"[API] ⚠️ Veo 3 not configured, falling back to Sora 2 Pro")
                    video_model = "sora-2-pro"
                else:
                    try:
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
            
            # Use Sora 2 Pro for combined videos (default or fallback)
            if video_model and video_model.startswith("sora"):
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

@app.post("/api/auth/signup")
async def signup(request: UserSignupRequest, db: Session = Depends(get_db)):
    """Create a new user account"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == request.username).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = db.query(User).filter(User.email == request.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        # Create new user
        hashed_password = get_password_hash(request.password)
        new_user = User(
            username=request.username,
            email=request.email,
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
    except Exception as e:
        print(f"[AUTH] Signup error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to create account: {str(e)}")


@app.post("/api/auth/login")
async def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    """Login user and return JWT token"""
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
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
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
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
    
    # Redirect to frontend success page
    from fastapi.responses import RedirectResponse
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return RedirectResponse(url=f"{frontend_url}/dashboard?connected={platform}")


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
                    caption=request.caption,
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
        
        return Veo3GenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Veo 3 generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/veo3/status/{job_id:path}", response_model=Veo3StatusResponse)
async def get_veo3_status(job_id: str):
    """Check the status of a Veo 3 video generation job
    
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
        
        status = await veo3_service.get_video_status(job_id)
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


@app.post("/api/image/generate", response_model=ImageGenerateResponse)
async def generate_image(request: ImageGenerateRequest):
    """
    Generate an image using DALL-E 3 or other image generation models
    """
    try:
        if not image_generation_service.openai_api_key and request.model.startswith("dall-e"):
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not configured for image generation. Set OPENAI_API_KEY in your .env file"
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
        
        return ImageGenerateResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] Image generation error: {str(e)}")
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
        
        # Step 1: Scrape Instagram profile to learn context
        print(f"[API] 📱 Scraping Instagram profile to learn context...")
        profile_context = await instagram_service.get_profile_context(request.username)
        
        if not profile_context or not profile_context.get('username'):
            raise HTTPException(
                status_code=404,
                detail=f"Instagram profile @{request.username} not found or could not be accessed"
            )
        
        # Step 2: Research profile context using AI
        print(f"[API] 🤖 Analyzing profile context with AI...")
        page_context_summary = await openai_service.research_profile_context(profile_context)
        
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
                detail="Failed to generate any images. Check NANOBANANA_API_KEY configuration."
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
        
        try:
            print(f"[API] 🎬 Generating video with Veo 3...")
            veo3_result = await veo3_service.generate_video(
                prompt=video_script,
                duration=request.target_duration,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
