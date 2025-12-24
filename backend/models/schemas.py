from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class VideoAnalysisRequest(BaseModel):
    username: str = Field(..., description="Instagram username to analyze")
    video_limit: Optional[int] = Field(3, description="Number of videos to analyze (default: 3, max: 10)")
    video_seconds: Optional[int] = Field(8, description="Duration of generated videos in seconds (5-16 for Sora 2, 4-60 for Veo 3, default: 8)")
    llm_provider: Optional[str] = Field("openai", description="LLM provider for script generation: 'openai' or 'claude'")
    video_model: Optional[str] = Field("sora-2", description="Video generation model: 'sora-2' or 'veo-3'")
    document_ids: Optional[List[str]] = Field(default=[], description="Optional document IDs to include as context")


class MultiUserAnalysisRequest(BaseModel):
    """Request for analyzing multiple Instagram users and creating a combined script"""
    usernames: List[str] = Field(..., description="List of Instagram usernames (2-5 users)", min_length=2, max_length=5)
    videos_per_user: Optional[int] = Field(2, description="Number of top videos per user (default: 2)")
    combine_style: Optional[str] = Field("fusion", description="How to combine: 'fusion' (blend both styles) or 'sequence' (sequential story)")
    video_seconds: Optional[int] = Field(12, description="Duration of combined video in seconds (5-16 for Sora 2 Pro, 4-60 for Veo 3, default: 12)")
    llm_provider: Optional[str] = Field("openai", description="LLM provider for script generation: 'openai' or 'claude'")
    video_model: Optional[str] = Field("sora-2-pro", description="Video generation model: 'sora-2-pro' or 'veo-3'")
    document_ids: Optional[List[str]] = Field(default=[], description="Optional document IDs to include as context")


class ScrapedVideo(BaseModel):
    """Video metadata from Instagram"""
    id: str
    post_url: str
    video_url: str
    thumbnail_url: Optional[str] = None  # For Vision API
    views: int
    likes: int
    text: str
    duration: float


# ===== STRUCTURED OUTPUTS (OpenAI Build Hours Feature) =====
class SoraVisualStyle(BaseModel):
    """Visual style and aesthetics for Sora"""
    model_config = {"extra": "forbid"}
    primary_colors: List[str] = Field(description="Main color palette (e.g., 'warm orange', 'deep blue')")
    lighting: str = Field(description="Lighting style (e.g., 'cinematic golden hour', 'natural daylight', 'dramatic contrast')")
    mood: str = Field(description="Overall mood and atmosphere")
    visual_references: str = Field(description="Style references or inspirations")


class SoraCameraWork(BaseModel):
    """Camera movements and shot composition"""
    model_config = {"extra": "forbid"}
    shot_types: List[str] = Field(description="Types of shots (e.g., 'close-up', 'wide establishing', 'medium')")
    camera_movements: List[str] = Field(description="Camera movements (e.g., 'slow pan', 'smooth tracking', 'static')")
    angles: List[str] = Field(description="Camera angles (e.g., 'eye-level', 'low-angle', 'overhead')")


class SoraTiming(BaseModel):
    """Pacing and timing structure"""
    model_config = {"extra": "forbid"}
    total_duration: str = Field(description="Total video duration (e.g., '15 seconds', '30 seconds')")
    pacing: str = Field(description="Pacing style (e.g., 'fast-paced', 'slow and contemplative', 'dynamic with cuts')")
    key_moments: List[str] = Field(description="Key moments and transitions throughout the video")


class StructuredSoraScript(BaseModel):
    """Complete structured Sora prompt using OpenAI Structured Outputs"""
    model_config = {"extra": "forbid"}
    core_concept: str = Field(description="Main concept and message of the video")
    visual_style: SoraVisualStyle
    camera_work: SoraCameraWork
    timing: SoraTiming
    full_prompt: str = Field(description="Complete Sora-ready prompt combining all elements")
    engagement_notes: str = Field(description="Why this approach will perform well based on original video metrics")


class ThumbnailAnalysis(BaseModel):
    """Vision API analysis of video thumbnail"""
    model_config = {"extra": "forbid"}
    dominant_colors: List[str] = Field(description="Dominant colors detected in thumbnail")
    composition: str = Field(description="Composition and framing analysis")
    visual_elements: List[str] = Field(description="Key visual elements detected")
    style_assessment: str = Field(description="Overall visual style assessment")


class SoraVideoJob(BaseModel):
    """Sora video generation job status"""
    job_id: str
    status: str  # queued, in_progress, completed, failed
    progress: Optional[int] = None
    model: str
    video_url: Optional[str] = None  # URL to download completed video
    created_at: int
    

class VideoResult(BaseModel):
    """Analyzed video with transcription and Sora script"""
    video_id: str
    post_url: str
    views: int
    likes: int
    original_text: str
    transcription: str
    sora_script: str
    structured_sora_script: Optional[StructuredSoraScript] = None  # Structured Outputs format
    thumbnail_analysis: Optional[ThumbnailAnalysis] = None  # Vision API analysis
    sora_video_job: Optional[SoraVideoJob] = None  # Sora video generation job


class VideoAnalysisResponse(BaseModel):
    """Response with scraped videos and analysis"""
    username: str
    scraped_videos: List[ScrapedVideo]
    analyzed_videos: List[VideoResult]
    page_context: Optional[str] = None  # AI-learned context about the profile/page


class CombinedVideoResult(BaseModel):
    """Combined analysis from multiple users"""
    usernames: List[str]
    total_videos_analyzed: int
    individual_results: List[VideoResult]
    combined_sora_script: str
    combined_structured_script: Optional[StructuredSoraScript] = None
    fusion_notes: str = Field(description="Explanation of how the styles were combined")


# ===== OAUTH & SOCIAL MEDIA CONNECTION SCHEMAS =====
class UserSignupRequest(BaseModel):
    """User signup request"""
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    """User login request"""
    email: str
    password: str


class FindCompetitorsRequest(BaseModel):
    """Request to find competitors based on brand context"""
    document_id: str


# ===== INTEGRATION SCHEMAS =====
class IntegrationConnectionResponse(BaseModel):
    id: int
    platform: str
    platform_user_email: Optional[str] = None
    is_active: bool
    connected_at: str
    last_synced_at: Optional[str] = None


class NotionPageResponse(BaseModel):
    id: str
    title: str
    url: Optional[str] = None
    last_edited_time: Optional[str] = None


class GoogleDriveFileResponse(BaseModel):
    id: str
    name: str
    mime_type: str
    modified_time: Optional[str] = None
    size: Optional[str] = None
    web_view_link: Optional[str] = None


class JiraIssueResponse(BaseModel):
    id: str
    key: str
    summary: str
    status: Optional[str] = None
    project: Optional[str] = None
    issue_type: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    created: Optional[str] = None
    updated: Optional[str] = None
    url: Optional[str] = None


class ImportContentRequest(BaseModel):
    integration_id: int
    item_ids: List[str] = Field(..., description="List of page/file IDs to import")
    collection: Optional[str] = Field("documents", description="Hyperspell collection name")


class SocialMediaConnectionResponse(BaseModel):
    """Social media connection response"""
    id: int
    platform: str
    account_username: str
    account_id: str
    is_active: bool
    connected_at: str
    last_used_at: Optional[str] = None


class PostVideoRequest(BaseModel):
    """Request to post video to social media"""
    connection_ids: List[int] = Field(..., description="List of connection IDs to post to")
    video_url: str = Field(..., description="URL to the video file")
    caption: str = Field(..., description="Post caption")
    job_id: Optional[str] = Field(None, description="Sora video job ID if applicable")


class PostVideoResponse(BaseModel):
    """Response after posting video"""
    success: bool
    posts: List[Dict] = Field(..., description="List of post results per platform")
    errors: Optional[List[str]] = None


class ManualInstagramPostRequest(BaseModel):
    """Request for manual Instagram posting using browser automation"""
    video_url: str = Field(..., description="URL to the video file")
    caption: str = Field(..., description="Post caption")
    username: str = Field(..., description="Instagram username")
    password: str = Field(..., description="Instagram password (used only for browser automation)")


class ManualInstagramPostResponse(BaseModel):
    """Response after manual Instagram posting"""
    success: bool
    message: str
    error: Optional[str] = None


# ===== VEO 3 & IMAGE GENERATION SCHEMAS =====
class Veo3GenerateRequest(BaseModel):
    """Request to generate a video using Veo 3"""
    prompt: str = Field(..., description="Text description of the video")
    duration: Optional[int] = Field(8, description="Video duration in seconds (4-60)")
    resolution: Optional[str] = Field("1280x720", description="Video resolution")
    image_urls: Optional[List[str]] = Field(None, description="Optional list of image URLs to incorporate")
    style: Optional[str] = Field(None, description="Style preset (cinematic, realistic, artistic)")


class Veo3GenerateResponse(BaseModel):
    """Response from Veo 3 video generation"""
    job_id: str
    status: str
    video_url: Optional[str] = None
    progress: Optional[int] = 0
    model: str = "veo-3"
    estimated_time: Optional[int] = None


class Veo3StatusResponse(BaseModel):
    """Status of a Veo 3 video generation job"""
    job_id: str
    status: str
    progress: Optional[int] = 0
    video_url: Optional[str] = None
    error: Optional[str] = None
    needs_extension: Optional[bool] = False
    extension_count: Optional[int] = 0
    extensions_completed: Optional[int] = 0
    is_extension: Optional[bool] = False


class Veo3ExtendRequest(BaseModel):
    """Request to extend a Veo 3 video"""
    base_job_id: str = Field(..., description="Job ID of the base video to extend")
    extension_seconds: Optional[int] = Field(7, description="Seconds to add per extension (typically 7, up to 20 times)")
    max_extensions: Optional[int] = Field(1, description="Maximum number of extensions (1-20, total up to 148 seconds)")


class Veo3ExtendResponse(BaseModel):
    """Response from Veo 3 video extension"""
    job_id: str
    status: str
    progress: Optional[int] = 0
    video_url: Optional[str] = None
    model: str = "veo-3.1-fast-generate-preview"
    is_extension: bool = True
    extension_seconds: int
    base_job_id: str


class ImageGenerateRequest(BaseModel):
    """Request to generate an image"""
    prompt: str = Field(..., description="Text description of the image")
    model: Optional[str] = Field("nanobanana", description="Model to use (nanobanana, dall-e-3, dall-e-2, stable-diffusion)")
    size: Optional[str] = Field("1024x1024", description="Image size")
    quality: Optional[str] = Field("medium", description="Image quality (low, medium, high for Nano Banana; standard, hd for DALL-E 3)")
    style: Optional[str] = Field(None, description="Style preset (vivid, natural for DALL-E 3)")
    n: Optional[int] = Field(1, description="Number of images to generate")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio for Nano Banana (1:1, 16:9, 4:3, 9:16)")


class ImageGenerateResponse(BaseModel):
    """Response from image generation"""
    image_url: Optional[str] = None
    image_urls: Optional[List[str]] = None
    image_base64: Optional[str] = None
    revised_prompt: Optional[str] = None
    model: str
    size: str
    quality: Optional[str] = None
    style: Optional[str] = None
    session_id: Optional[str] = None  # For Nano Banana conversational editing
    aspect_ratio: Optional[str] = None


class MarketingPostRequest(BaseModel):
    """Request to create a marketing post with image"""
    topic: str = Field(..., description="Marketing topic or theme for the post")
    brand_context: Optional[str] = Field(None, description="Optional brand context, tone, or style guidelines")
    image_prompt: Optional[str] = Field(None, description="Custom image prompt (if not provided, will be generated from topic)")
    caption_style: Optional[str] = Field("engaging", description="Caption style: 'engaging', 'professional', 'casual', 'educational'")
    aspect_ratio: Optional[str] = Field("1:1", description="Image aspect ratio: '1:1', '16:9', '9:16', '4:3'")
    include_hashtags: Optional[bool] = Field(True, description="Include relevant hashtags in caption")
    post_to_instagram: Optional[bool] = Field(False, description="Automatically post to Instagram (requires credentials)")
    instagram_username: Optional[str] = Field(None, description="Instagram username for posting")
    instagram_password: Optional[str] = Field(None, description="Instagram password for posting")


class MarketingPostResponse(BaseModel):
    """Response from marketing post creation"""
    success: bool
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    image_prompt: str
    caption: str
    hashtags: Optional[List[str]] = None
    full_caption: Optional[str] = None
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    is_first_post: Optional[bool] = False


class MarketingPostSuggestion(BaseModel):
    """A single marketing post topic suggestion"""
    topic: str = Field(..., description="Suggested topic for the marketing post")
    context: Optional[str] = Field(None, description="Why this suggestion is relevant based on user's documents/memories")
    reasoning: Optional[str] = Field(None, description="Brief explanation of why this topic was suggested")
    score: Optional[float] = Field(None, description="Engagement score (0-100) based on similar high-performing LinkedIn posts")
    source: Optional[str] = Field(None, description="Source of suggestion: 'linkedin_scored', 'user_context', or 'ai_generated'")


class MarketingPostSuggestionsResponse(BaseModel):
    """Response containing marketing post topic suggestions"""
    suggestions: List[MarketingPostSuggestion] = Field(..., description="List of suggested topics")
    user_context_used: Optional[str] = Field(None, description="Summary of user context that influenced suggestions")


class SmartVideoCompositionRequest(BaseModel):
    """Request for smart video composition with images"""
    video_prompt: str = Field(..., description="Base video description")
    image_prompts: List[str] = Field(..., description="Prompts for generating supporting images")
    target_duration: Optional[int] = Field(8, description="Target video duration in seconds")
    style: Optional[str] = Field("informative", description="Composition style (informative, cinematic, educational, narrative)")
    use_veo3: Optional[bool] = Field(True, description="Use Veo 3 for video generation (otherwise use Sora)")


class SmartVideoCompositionResponse(BaseModel):
    """Response from smart video composition"""
    topic: Optional[str] = None
    image_urls: List[str]
    image_descriptions: List[str]
    video_script: str
    composition_data: Dict
    video_job_id: Optional[str] = None
    video_model: str  # "veo-3" or "sora-2"
    generated_images: List[Dict]


class InformationalVideoRequest(BaseModel):
    """Request for creating informational videos - automatically learns from Instagram profile"""
    username: str = Field(..., description="Instagram username to scrape and learn from")
    target_duration: Optional[int] = Field(8, description="Target video duration in seconds (4-60 for Veo 3)")
    document_ids: Optional[List[str]] = Field(default=[], description="Optional document IDs to include as context")


class InformationalVideoResponse(BaseModel):
    """Response from informational video generation"""
    topic: str
    company_context: str
    generated_images: List[Dict]
    image_urls: List[str]
    image_prompts: List[str]
    video_script: str
    video_job_id: Optional[str] = None
    video_model: str
    composition_data: Dict


class DocumentVideoRequest(BaseModel):
    """Request for creating marketing videos from uploaded documents - AI decides everything if not specified"""
    document_ids: List[str] = Field(..., description="List of document IDs to use as context", min_length=1)
    topic: Optional[str] = None  # AI will decide if not provided
    duration: Optional[int] = None  # AI will decide if not provided
    target_audience: Optional[str] = None  # AI will decide if not provided
    key_message: Optional[str] = None  # AI will decide if not provided
    platform: Optional[str] = "linkedin"  # Default to LinkedIn optimization
    script: Optional[str] = None  # Pre-approved script from user
    video_model: Optional[str] = Field("sora-2", description="Video generation model: 'sora-2' or 'veo-3'")
    approved: Optional[bool] = False  # Whether script is pre-approved


class DocumentVideoResponse(BaseModel):
    """Response from document-based video generation"""
    script: str
    video_job: Optional[Dict] = None  # Sora video job information
    document_context_summary: Optional[str] = None
    linkedin_optimization: Optional[str] = Field(None, description="Analysis of LinkedIn performance optimization")
    key_insights: Optional[str] = Field(None, description="Key insights extracted from documents")
    document_analysis: Optional[str] = Field(None, description="Full document analysis")
    ai_decisions: Optional[Dict] = Field(None, description="AI decisions (topic, duration, audience, message)")
    video_options: Optional[List[Dict]] = Field(None, description="Multiple video options for user to choose from")


class VideoOptionsRequest(BaseModel):
    video_model: Optional[str] = Field("sora-2", description="Video generation model: 'sora-2' or 'veo-3'")
    """Request to generate video options from documents"""
    document_ids: List[str] = Field(..., description="List of document IDs to analyze")
    num_options: Optional[int] = Field(3, description="Number of video options to generate (default: 3)")


class VideoOptionsResponse(BaseModel):
    """Response with multiple video options"""
    options: List[Dict] = Field(..., description="List of video options with different approaches")


class ScriptApprovalRequest(BaseModel):
    """Request to approve or edit a script"""
    script: str = Field(..., description="The script (original or edited)")
    approved: bool = Field(..., description="Whether the script is approved")
    original_script: Optional[str] = Field(None, description="Original script if editing")


# ===== USER CONTEXT & PREFERENCES SCHEMAS =====
class UserPreferencesRequest(BaseModel):
    """Request to update user preferences"""
    brand_voice: Optional[str] = Field(None, description="Brand voice description (e.g., 'professional but friendly', 'authoritative', 'conversational')")
    content_style: Optional[str] = Field(None, description="Content style preference (e.g., 'educational', 'entertaining', 'inspirational')")
    target_audience: Optional[str] = Field(None, description="Primary target audience")
    preferred_video_length: Optional[int] = Field(None, description="Preferred video length in seconds")
    video_model_preference: Optional[str] = Field(None, description="Preferred video model: 'sora-2' or 'veo-3'")
    platform_preferences: Optional[Dict[str, bool]] = Field(None, description="Platform preferences (e.g., {'linkedin': True, 'instagram': False})")
    content_themes: Optional[List[str]] = Field(None, description="Preferred content themes")
    brand_colors: Optional[List[str]] = Field(None, description="Brand color palette")
    tone_preferences: Optional[List[str]] = Field(None, description="Tone preferences (e.g., ['professional', 'authentic', 'engaging'])")


class UserPreferencesResponse(BaseModel):
    """Response with user preferences"""
    preferences: Dict
    message: str


class UserContextResponse(BaseModel):
    """Response with comprehensive user context"""
    user_id: str
    preferences: Dict
    content_history: Dict
    behavioral_patterns: Dict
    brand_insights: Dict
    performance_data: Dict
    social_profiles: Dict
    document_insights: Dict
    metadata: Dict
