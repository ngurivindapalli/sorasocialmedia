from pydantic import BaseModel, Field
from typing import List, Optional


class VideoAnalysisRequest(BaseModel):
    username: str = Field(..., description="Instagram username to analyze")
    video_limit: Optional[int] = Field(3, description="Number of videos to analyze (default: 3, max: 10)")
    video_seconds: Optional[int] = Field(8, description="Duration of generated videos in seconds (5-16, default: 8)")
    llm_provider: Optional[str] = Field("openai", description="LLM provider for script generation: 'openai' or 'claude'")


class MultiUserAnalysisRequest(BaseModel):
    """Request for analyzing multiple Instagram users and creating a combined script"""
    usernames: List[str] = Field(..., description="List of Instagram usernames (2-5 users)", min_length=2, max_length=5)
    videos_per_user: Optional[int] = Field(2, description="Number of top videos per user (default: 2)")
    combine_style: Optional[str] = Field("fusion", description="How to combine: 'fusion' (blend both styles) or 'sequence' (sequential story)")
    video_seconds: Optional[int] = Field(12, description="Duration of combined video in seconds (5-16, default: 12)")
    llm_provider: Optional[str] = Field("openai", description="LLM provider for script generation: 'openai' or 'claude'")


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
    page_context: Optional[str] = Field(None, description="AI-learned context about the page/profile")
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
    combined_sora_video_job: Optional[SoraVideoJob] = None  # Sora video for combined script
