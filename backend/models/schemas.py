from pydantic import BaseModel, Field
from typing import List, Optional


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


# ===== POSTING SCHEMAS =====
class PostVideoRequest(BaseModel):
    """Request to post content (video or image) to social media"""
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    connection_ids: List[int] = Field(..., description="List of connection IDs to post to")
    platform: Optional[str] = None  # Optional platform filter


class PostVideoResponse(BaseModel):
    """Response from posting"""
    success: bool
    posts: Optional[List[dict]] = None
    errors: Optional[List[str]] = None


# ===== VEO 3 SCHEMAS =====
class Veo3GenerateRequest(BaseModel):
    """Request to generate a Veo 3 video"""
    prompt: str = Field(..., description="Text prompt for video generation")
    duration: int = Field(8, description="Video duration in seconds (4-60)")
    resolution: str = Field("1280x720", description="Video resolution (e.g., '1280x720')")
    image_urls: Optional[List[str]] = Field(None, description="Optional image URLs for image-to-video")
    style: Optional[str] = Field(None, description="Optional style parameter")
    max_extensions: int = Field(1, description="Maximum number of extensions (0-20, default: 1)")


class Veo3GenerateResponse(BaseModel):
    """Response from Veo 3 video generation"""
    job_id: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    model: str = "veo-3"
    created_at: Optional[int] = None


class Veo3StatusResponse(BaseModel):
    """Response from Veo 3 status check"""
    job_id: str
    status: str
    progress: int
    video_url: Optional[str] = None
    error: Optional[str] = None


class Veo3ExtendRequest(BaseModel):
    """Request to extend a Veo 3 video"""
    base_job_id: str = Field(..., description="Job ID of the base video to extend")
    extension_seconds: int = Field(7, description="Seconds to add per extension (1-30)")
    max_extensions: int = Field(1, description="Maximum number of extensions (1-20)")


class Veo3ExtendResponse(BaseModel):
    """Response from Veo 3 video extension"""
    job_id: str
    operation_name: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    model: str = "veo-3.1-generate-preview"
    created_at: Optional[int] = None
    is_extension: bool = True
    extension_seconds: int
    base_job_id: str


class Veo3GenerateWithContextRequest(BaseModel):
    """Request to generate Veo 3 video with context"""
    prompt: str
    duration: int = 8
    resolution: str = "1280x720"
    context: Optional[dict] = None


class Veo3GenerateWithContextResponse(BaseModel):
    """Response from Veo 3 video generation with context"""
    job_id: str
    status: str
    progress: int = 0
    video_url: Optional[str] = None
    model: str = "veo-3"


# ===== MARKETING POST SCHEMAS =====
class MarketingPostRequest(BaseModel):
    """Request to create a marketing post"""
    topic: str = Field(..., description="Topic for the marketing post")
    brand_context: Optional[str] = Field(None, description="Brand context information")
    aspect_ratio: Optional[str] = Field("1:1", description="Image aspect ratio")
    include_hashtags: Optional[bool] = Field(True, description="Whether to include hashtags")
    platform: Optional[str] = Field("instagram", description="Platform for the post (instagram or linkedin)")
    image_prompt: Optional[str] = Field(None, description="Custom image prompt for generation")
    caption: Optional[str] = Field(None, description="Custom caption for the post")
    caption_style: Optional[str] = Field("engaging", description="Caption style: engaging, professional, casual, humorous, educational")
    auto_post: Optional[bool] = Field(False, description="Whether to automatically post to social media")


class MarketingPostSuggestion(BaseModel):
    """A single marketing post suggestion"""
    topic: str
    caption: Optional[str] = None
    context: Optional[str] = None
    reasoning: Optional[str] = None
    score: Optional[float] = None
    source: Optional[str] = None
    hashtags: Optional[List[str]] = None


class MarketingPostResponse(BaseModel):
    """Response from marketing post creation"""
    topic: Optional[str] = None
    caption: Optional[str] = None
    image_base64: Optional[str] = None
    image_url: Optional[str] = None
    image_prompt: Optional[str] = None
    hashtags: Optional[List[str]] = None
    full_caption: Optional[str] = None
    post_id: Optional[str] = None
    post_url: Optional[str] = None
    error: Optional[str] = None
    is_first_post: Optional[bool] = None
    success: bool = True


class MarketingPostSuggestionsResponse(BaseModel):
    """Response with multiple marketing post suggestions"""
    suggestions: List[MarketingPostSuggestion]
    user_context_used: Optional[str] = None


# ===== AIGIS MARKETING SCHEMAS =====
class AigisMarketingRequest(BaseModel):
    """Request for Aigis marketing content"""
    topic: str
    context: Optional[str] = None


class AigisMarketingResponse(BaseModel):
    """Response from Aigis marketing"""
    content: str
    success: bool = True


class AigisMarketingPostRequest(BaseModel):
    """Request to create Aigis marketing post"""
    topic: str
    context: Optional[str] = None


class AigisMarketingSuggestionsRequest(BaseModel):
    """Request for Aigis marketing suggestions"""
    count: int = Field(5, description="Number of suggestions")
    context: Optional[str] = None


class AigisMarketingSuggestionsResponse(BaseModel):
    """Response with Aigis marketing suggestions"""
    suggestions: List[str]


# ===== IMAGE GENERATION SCHEMAS =====
class ImageGenerateRequest(BaseModel):
    """Request to generate an image"""
    prompt: str
    model: Optional[str] = Field("nanobanana", description="Image generation model")
    size: Optional[str] = Field("1024x1024", description="Image size")
    quality: Optional[str] = Field("standard", description="Image quality")
    aspect_ratio: Optional[str] = Field("1:1", description="Aspect ratio")
    n: Optional[int] = Field(1, description="Number of images")
    style: Optional[str] = Field(None, description="Optional style parameter")


class ImageGenerateResponse(BaseModel):
    """Response from image generation"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    revised_prompt: Optional[str] = None
    model: str
    size: str
    success: bool = True


# ===== USER SCHEMAS =====
class UserSignupRequest(BaseModel):
    """Request to sign up a new user"""
    username: str
    email: str
    password: str


class UserLoginRequest(BaseModel):
    """Request to login"""
    email: str
    password: str


class SocialMediaConnectionResponse(BaseModel):
    """Response for social media connection"""
    id: int
    platform: str
    account_username: Optional[str] = None
    account_id: Optional[str] = None
    is_active: bool
    connected_at: str
    last_used_at: Optional[str] = None


# ===== ADDITIONAL SCHEMAS =====
class ManualInstagramPostRequest(BaseModel):
    """Request to manually post to Instagram"""
    image_url: str
    caption: str
    access_token: str


class ManualInstagramPostResponse(BaseModel):
    """Response from manual Instagram post"""
    success: bool
    post_id: Optional[str] = None
    error: Optional[str] = None


class SmartVideoCompositionRequest(BaseModel):
    """Request for smart video composition"""
    topic: str
    duration: Optional[int] = 30


class SmartVideoCompositionResponse(BaseModel):
    """Response from smart video composition"""
    composition: dict
    success: bool = True


class InformationalVideoRequest(BaseModel):
    """Request for informational video"""
    topic: str
    documents: Optional[List[str]] = None


class InformationalVideoResponse(BaseModel):
    """Response from informational video"""
    video_job_id: str
    script: str
    success: bool = True


class DocumentVideoRequest(BaseModel):
    """Request for document-based video"""
    document_ids: List[str]
    topic: Optional[str] = None


class DocumentVideoResponse(BaseModel):
    """Response from document video"""
    video_job: dict
    script: str
    success: bool = True


class VideoOptionsRequest(BaseModel):
    """Request for video options"""
    prompt: str
    duration: Optional[int] = 8


class VideoOptionsResponse(BaseModel):
    """Response with video options"""
    options: List[dict]


class ScriptApprovalRequest(BaseModel):
    """Request to approve a script"""
    script: str
    approved: bool


class UserPreferencesRequest(BaseModel):
    """Request to update user preferences"""
    preferences: dict


class UserPreferencesResponse(BaseModel):
    """Response with user preferences"""
    preferences: dict


class UserContextResponse(BaseModel):
    """Response with user context"""
    context: str


class FindCompetitorsRequest(BaseModel):
    """Request to find competitors"""
    industry: str
    location: Optional[str] = None


class IntegrationConnectionResponse(BaseModel):
    """Response for integration connection"""
    id: int
    platform: str
    connected: bool
    platform_user_email: Optional[str] = None
    connected_at: Optional[str] = None
    last_synced_at: Optional[str] = None


class NotionPageResponse(BaseModel):
    """Response for Notion page"""
    page_id: str
    title: str
    content: str


class GoogleDriveFileResponse(BaseModel):
    """Response for Google Drive file"""
    file_id: str
    name: str
    content: str


class JiraIssueResponse(BaseModel):
    """Response for Jira issue"""
    issue_id: str
    title: str
    description: str


class ImportContentRequest(BaseModel):
    """Request to import content"""
    source: str
    content: str


class SEOAEOAnalysisRequest(BaseModel):
    """Request for SEO/AEO analysis"""
    query: str
    domain: Optional[str] = None


class SEOAEOAnalysisResponse(BaseModel):
    """Response from SEO/AEO analysis"""
    analysis: dict
    success: bool = True


class SEOAEOStatusRequest(BaseModel):
    """Request for SEO/AEO status"""
    job_id: str


class SEOAEOStatusResponse(BaseModel):
    """Response with SEO/AEO status"""
    status: str
    progress: int
    result: Optional[dict] = None


class SEOAEOSummary(BaseModel):
    """SEO/AEO summary"""
    summary: str


class PromptResult(BaseModel):
    """Prompt result"""
    result: str


class TopicMentionStats(BaseModel):
    """Topic mention statistics"""
    topic: str
    mentions: int


class CompetitorStats(BaseModel):
    """Competitor statistics"""
    competitor: str
    stats: dict


class SourceStats(BaseModel):
    """Source statistics"""
    source: str
    stats: dict


class SourceCitation(BaseModel):
    """Source citation"""
    source: str
    citation: str
