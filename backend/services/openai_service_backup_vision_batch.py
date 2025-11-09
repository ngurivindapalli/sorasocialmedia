from openai import AsyncOpenAI
from typing import Dict, Optional
import os
import base64
from models.schemas import StructuredSoraScript, ThumbnailAnalysis


class OpenAIService:
    """Service for OpenAI API interactions - Whisper + GPT-4 Vision + Structured Outputs (Build Hours Features)"""
    
    def __init__(self, api_key: str, fine_tuned_model: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key)
        # Use fine-tuned model if provided, otherwise use gpt-4o-2024-08-06 (supports Structured Outputs)
        self.model = fine_tuned_model or "gpt-4o-2024-08-06"
        print(f"[OpenAI] Using model: {self.model}")
        print(f"[OpenAI] Build Hours: Structured Outputs enabled ✓")
    
    async def transcribe_video(self, video_path: str) -> str:
        """Transcribe video using Whisper API"""
        try:
            # Get file size to check if video is valid
            file_size = os.path.getsize(video_path)
            print(f"[OpenAI] Transcribing video file: {file_size:,} bytes")
            
            if file_size < 1000:
                return "[No audio detected - video file too small or corrupted]"
            
            with open(video_path, "rb") as audio_file:
                transcript = await self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text",
                    language="en"  # Specify English for better accuracy
                )
            
            # Check if transcription is garbage (repetitive short words)
            words = transcript.strip().split()
            if len(words) > 0 and len(set(words)) <= 3 and len(words) > 5:
                print(f"[OpenAI] Warning: Transcription appears low quality: {transcript[:100]}")
                return "[Audio quality too low for accurate transcription - video may have music/background noise only]"
            
            print(f"[OpenAI] Transcription successful: {len(transcript)} characters")
            return transcript
            
        except Exception as e:
            print(f"[OpenAI] Transcription error: {str(e)}")
            raise Exception(f"Transcription error: {str(e)}")
    
    async def generate_sora_script(self, transcription: str, video_metadata: Dict) -> str:
        """Generate basic Sora script (legacy method for backward compatibility)"""
        try:
            # Check if transcription is valid
            has_valid_transcription = not transcription.startswith("[") and len(transcription) > 20
            
            if has_valid_transcription:
                prompt = f"""Based on this video transcription and metrics, create a detailed Sora AI video generation prompt.

TRANSCRIPTION:
{transcription}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}
- Original Caption: {video_metadata.get('text', 'N/A')}

Create a Sora prompt that captures the core concept, visual style, camera work, timing, and engagement factors."""
            else:
                # No valid transcription - use caption and metrics only
                prompt = f"""Based on this Instagram video's caption and engagement metrics, create a detailed Sora AI video generation prompt.

VIDEO CAPTION:
{video_metadata.get('text', 'No caption available')}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}

NOTE: Audio transcription was not available for this video (may be music-only or no audio).

Create a Sora prompt that captures likely visual style, camera work, timing, and engagement factors based on the caption and popularity metrics."""

            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert video production director creating Sora AI prompts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Sora script generation error: {str(e)}")
    
    
    async def generate_structured_sora_script(self, transcription: str, video_metadata: Dict, thumbnail_analysis: Optional[ThumbnailAnalysis] = None) -> StructuredSoraScript:
        """
        Generate structured Sora script using OpenAI Structured Outputs (Build Hours Feature)
        Guarantees valid, consistent JSON structure matching StructuredSoraScript schema
        """
        try:
            # Build context including thumbnail analysis if available
            context = f"""TRANSCRIPTION:
{transcription}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}
- Original Text: {video_metadata.get('text', 'N/A')}
- Duration: {video_metadata.get('duration', 'Unknown')} seconds"""

            if thumbnail_analysis:
                context += f"""

VISUAL ANALYSIS (from thumbnail):
- Dominant Colors: {', '.join(thumbnail_analysis.dominant_colors)}
- Composition: {thumbnail_analysis.composition}
- Visual Elements: {', '.join(thumbnail_analysis.visual_elements)}
- Style: {thumbnail_analysis.style_assessment}"""

            prompt = f"""Based on this video data, create a comprehensive Sora AI video generation prompt.

{context}

Analyze what made this video successful and create a detailed, structured Sora prompt that captures:
1. Core concept and message
2. Visual style (colors, lighting, mood, references)
3. Camera work (shot types, movements, angles)
4. Timing and pacing structure
5. Engagement optimization based on metrics

Make it actionable and ready for Sora AI."""

            # USE STRUCTURED OUTPUTS - Response Format enforces schema
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert video production director creating detailed, structured Sora AI prompts. Analyze successful viral videos and recreate their essence."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format=StructuredSoraScript,  # Guaranteed valid structure!
                temperature=0.7
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            raise Exception(f"Structured Sora script generation error: {str(e)}")
    
    
    async def analyze_thumbnail_with_vision(self, thumbnail_url: str) -> ThumbnailAnalysis:
        """
        Analyze video thumbnail using GPT-4 Vision API (Build Hours Feature)
        Extracts visual style, colors, composition to enhance Sora prompts
        """
        try:
            completion = await self.client.beta.chat.completions.parse(
                model="gpt-4o",  # Vision-enabled model
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cinematographer analyzing video thumbnails. Identify visual style, composition, colors, and key elements to inform AI video generation."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this video thumbnail. Identify dominant colors, composition style, visual elements, and overall aesthetic. Be specific and detailed."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": thumbnail_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format=ThumbnailAnalysis,  # Structured output for vision analysis
                temperature=0.5
            )
            
            return completion.choices[0].message.parsed
            
        except Exception as e:
            print(f"[OpenAI] Vision API error: {str(e)}")
            raise Exception(f"Thumbnail analysis error: {str(e)}")
