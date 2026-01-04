from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class VideoAnalysisRequest(BaseModel):
    username: str = Field(..., description="Instagram username to analyze")
    video_limit: Optional[int] = Field(3, description="Number of videos to analyze (default: 3, max: 10)")


class MultiUserAnalysisRequest(BaseModel):
    """Request for analyzing multiple Instagram users and creating a combined script"""
    usernames: List[str] = Field(..., description="List of Instagram usernames (2-5 users)", min_length=2, max_length=5)
    videos_per_user: Optional[int] = Field(2, description="Number of top videos per user (default: 2)")
    combine_style: Optional[str] = Field("fusion", description="How to combine: 'fusion' (blend both styles) or 'sequence' (sequential story)")


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


class VideoAnalysisResponse(BaseModel):
    """Response with scraped videos and analysis"""
    username: str
    scraped_videos: List[ScrapedVideo]
    analyzed_videos: List[VideoResult]


class CombinedVideoResult(BaseModel):
    """Combined analysis from multiple users"""
    usernames: List[str]
    total_videos_analyzed: int
    individual_results: List[VideoResult]
    combined_sora_script: str
    combined_structured_script: Optional[StructuredSoraScript] = None
    fusion_notes: str = Field(description="Explanation of how the styles were combined")


# ===== VEO 3 & VIDEO GENERATION SCHEMAS =====
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


class Veo3GenerateWithContextRequest(BaseModel):
    """Request to generate a Veo video with Mem0 context"""
    topic: str = Field(..., description="Topic or subject for the video")
    duration: Optional[int] = Field(8, description="Initial video duration in seconds (4-8)")
    max_extensions: Optional[int] = Field(0, description="Maximum number of extensions (0-20, each adds 7 seconds)")
    resolution: Optional[str] = Field("1280x720", description="Video resolution")
    llm_provider: Optional[str] = Field("openai", description="LLM provider: 'openai' or 'claude'")
    wait_for_completion: Optional[bool] = Field(True, description="Wait for video and all extensions to complete before returning")


class Veo3GenerateWithContextResponse(BaseModel):
    """Response from Veo 3 video generation with context"""
    job_id: str
    status: str
    video_url: Optional[str] = None
    progress: Optional[int] = 0
    model: str = "veo-3"
    script: Optional[str] = None
    script_saved: Optional[bool] = False
    extensions_completed: Optional[int] = 0
    final_duration: Optional[int] = None


# ===== MARKETING POST SCHEMAS =====
class MarketingPostRequest(BaseModel):
    """Request to create a marketing post"""
    topic: str = Field(..., description="Topic for the marketing post")
    brand_context: Optional[str] = Field(None, description="Brand context information")
    image_prompt: Optional[str] = Field(None, description="Optional image prompt (will be generated if not provided)")
    caption_style: Optional[str] = Field("engaging", description="Style for the caption")
    include_hashtags: Optional[bool] = Field(True, description="Include hashtags in caption")
    style: Optional[str] = Field(None, description="Visual style")


class MarketingPostResponse(BaseModel):
    """Response from marketing post creation"""
    success: bool
    image_url: Optional[str] = None
    caption: Optional[str] = None
    post_id: Optional[str] = None
    error: Optional[str] = None


class MarketingPostSuggestion(BaseModel):
    """Marketing post suggestion"""
    topic: str
    description: Optional[str] = None


class MarketingPostSuggestionsResponse(BaseModel):
    """Response with marketing post suggestions"""
    success: bool
    suggestions: List[MarketingPostSuggestion]
    error: Optional[str] = None


# ===== AIGIS MARKETING SCHEMAS =====
class AigisMarketingRequest(BaseModel):
    """Request for Aigis Marketing content generation"""
    topic: str = Field(..., description="Topic for content")
    style: Optional[str] = Field(None, description="Content style")


class AigisMarketingResponse(BaseModel):
    """Response from Aigis Marketing content generation"""
    success: bool
    content: Optional[str] = None
    outline: Optional[List[str]] = None
    draft: Optional[str] = None
    imagePrompt: Optional[str] = None
    excerpt: Optional[str] = None
    tags: Optional[List[str]] = None
    error: Optional[str] = None


class AigisMarketingPostRequest(BaseModel):
    """Request for Aigis Marketing post"""
    topic: str = Field(..., description="Topic for the post")
    style: Optional[str] = Field(None, description="Post style")


class AigisMarketingSuggestionsRequest(BaseModel):
    """Request for Aigis Marketing suggestions"""
    pass  # No fields needed


class AigisMarketingSuggestionsResponse(BaseModel):
    """Response with Aigis Marketing suggestions"""
    success: bool
    suggestions: List[str]
    welcomeMessage: str
    error: Optional[str] = None


# ===== USER AUTH SCHEMAS =====
class UserSignupRequest(BaseModel):
    """User signup request"""
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    """User login request"""
    email: str
    password: str


class SocialMediaConnectionResponse(BaseModel):
    """Social media connection response"""
    platform: str
    connected: bool
    username: Optional[str] = None


# ===== VIDEO POSTING SCHEMAS =====
class PostVideoRequest(BaseModel):
    """Request to post a video"""
    video_url: str
    platform: str
    caption: Optional[str] = None


class PostVideoResponse(BaseModel):
    """Response from video posting"""
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None


class ManualInstagramPostRequest(BaseModel):
    """Request for manual Instagram post"""
    image_url: str
    caption: str


class ManualInstagramPostResponse(BaseModel):
    """Response from manual Instagram post"""
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None


# ===== IMAGE GENERATION SCHEMAS =====
class ImageGenerateRequest(BaseModel):
    """Request to generate an image"""
    prompt: str = Field(..., description="Text description of the image")
    model: Optional[str] = Field("nanobanana", description="Model to use")
    size: Optional[str] = Field("1024x1024", description="Image size")
    quality: Optional[str] = Field("medium", description="Image quality")
    style: Optional[str] = Field(None, description="Style preset")
    n: Optional[int] = Field(1, description="Number of images")
    aspect_ratio: Optional[str] = Field(None, description="Aspect ratio")


class ImageGenerateResponse(BaseModel):
    """Response from image generation"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    error: Optional[str] = None


# ===== VIDEO COMPOSITION SCHEMAS =====
class SmartVideoCompositionRequest(BaseModel):
    """Request for smart video composition"""
    topic: str
    duration: Optional[int] = Field(8, description="Video duration")


class SmartVideoCompositionResponse(BaseModel):
    """Response from smart video composition"""
    success: bool
    video_url: Optional[str] = None
    error: Optional[str] = None


class InformationalVideoRequest(BaseModel):
    """Request for informational video"""
    topic: str
    duration: Optional[int] = Field(8, description="Video duration")


class InformationalVideoResponse(BaseModel):
    """Response from informational video"""
    success: bool
    video_url: Optional[str] = None
    error: Optional[str] = None


class DocumentVideoRequest(BaseModel):
    """Request for document-based video"""
    document_id: str
    duration: Optional[int] = Field(8, description="Video duration")


class DocumentVideoResponse(BaseModel):
    """Response from document-based video"""
    success: bool
    video_url: Optional[str] = None
    error: Optional[str] = None


# ===== VIDEO OPTIONS SCHEMAS =====
class VideoOptionsRequest(BaseModel):
    """Request for video options"""
    topic: str
    duration: Optional[int] = Field(8, description="Video duration")


class VideoOptionsResponse(BaseModel):
    """Response with video options"""
    options: List[str]
    error: Optional[str] = None


class ScriptApprovalRequest(BaseModel):
    """Request for script approval"""
    script: str
    approved: bool


# ===== USER PREFERENCES SCHEMAS =====
class UserPreferencesRequest(BaseModel):
    """Request to update user preferences"""
    preferences: Dict


class UserPreferencesResponse(BaseModel):
    """Response with user preferences"""
    preferences: Dict
    error: Optional[str] = None


class UserContextResponse(BaseModel):
    """Response with user context"""
    context: str
    error: Optional[str] = None


# ===== COMPETITOR ANALYSIS SCHEMAS =====
class FindCompetitorsRequest(BaseModel):
    """Request to find competitors"""
    document_id: str


# ===== INTEGRATION SCHEMAS =====
class IntegrationConnectionResponse(BaseModel):
    """Integration connection response"""
    id: int
    platform: str
    platform_user_email: Optional[str] = None
    is_active: bool
    connected_at: str


class NotionPageResponse(BaseModel):
    """Notion page response"""
    id: str
    title: str
    url: str


class GoogleDriveFileResponse(BaseModel):
    """Google Drive file response"""
    id: str
    name: str
    mimeType: str
    webViewLink: Optional[str] = None


class JiraIssueResponse(BaseModel):
    """Jira issue response"""
    id: str
    key: str
    summary: str
    status: str


class ImportContentRequest(BaseModel):
    """Request to import content from integrations"""
    integration_id: int
    item_ids: List[str]
    collection: Optional[str] = None


# ===== SORA VIDEO JOB SCHEMA =====
class SoraVideoJob(BaseModel):
    """Sora video generation job status"""
    job_id: str
    status: str
    progress: Optional[int] = None
    model: str
    video_url: Optional[str] = None
    created_at: int


# ===== SEO/AEO (Answer Engine Optimization) SCHEMAS =====
class SEOAEOAnalysisRequest(BaseModel):
    """Request to start SEO/AEO analysis"""
    brand_name: str = Field(..., description="Brand name to track")
    brand_url: Optional[str] = Field(None, description="Brand website URL (optional)")
    competitors: Optional[List[str]] = Field(None, description="List of competitor names")
    topics: Optional[List[str]] = Field(None, description="Optional list of topics to analyze")
    num_prompts: Optional[int] = Field(100, description="Number of prompts to test (default: 100)")


class SourceCitation(BaseModel):
    """Source citation from LLM response"""
    domain: str
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None


class PromptResult(BaseModel):
    """Result from testing a prompt"""
    prompt: str
    topic: str
    brand_mentioned: bool
    response: str
    sources: List[SourceCitation]
    competitors_mentioned: List[str]
    created_at: str


class TopicMentionStats(BaseModel):
    """Brand mention statistics by topic"""
    topic: str
    mention_rate: float
    total_prompts: int
    mentions: int


class CompetitorStats(BaseModel):
    """Competitor mention statistics"""
    competitor: str
    mention_rate: float
    total_prompts: int
    mentions: int


class SourceStats(BaseModel):
    """Source citation statistics"""
    domain: str
    mention_count: int
    source_type: Optional[str] = None  # e.g., "Website", "Community", "Code Repository"


class SEOAEOAnalysisResponse(BaseModel):
    """Response from SEO/AEO analysis"""
    success: bool
    analysis_id: Optional[str] = None
    brand_name: str
    brand_mention_rate: float
    total_prompts_tested: int
    total_mentions: int
    top_competitor: Optional[str] = None
    top_competitor_rate: Optional[float] = None
    total_sources: int
    topics: List[TopicMentionStats]
    competitors: List[CompetitorStats]
    top_sources: List[SourceStats]
    recent_results: List[PromptResult]
    error: Optional[str] = None


class SEOAEOSummary(BaseModel):
    """Summary of SEO/AEO analysis"""
    brand_mention_rate: float
    total_prompts_tested: int
    total_mentions: int
    top_competitor: Optional[str] = None
    top_competitor_rate: Optional[float] = None
    total_sources: int


class SEOAEOStatusRequest(BaseModel):
    """Request to check analysis status"""
    analysis_id: str


class SEOAEOStatusResponse(BaseModel):
    """Response with analysis status"""
    analysis_id: str
    status: str  # "running", "completed", "failed"
    progress: Optional[int] = None
    results: Optional[SEOAEOSummary] = None
    error: Optional[str] = None
