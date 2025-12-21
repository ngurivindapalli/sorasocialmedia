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
        print(f"[OpenAI] Build Hours: Structured Outputs enabled OK")
    
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

            # USE STRUCTURED OUTPUTS - Fixed API path
            completion = await self.client.chat.completions.create(
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
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "sora_script",
                        "strict": True,
                        "schema": StructuredSoraScript.model_json_schema()
                    }
                },
                temperature=0.7
            )
            
            # Parse the JSON response into our Pydantic model
            import json
            response_data = json.loads(completion.choices[0].message.content)
            return StructuredSoraScript(**response_data)
            
        except Exception as e:
            raise Exception(f"Structured Sora script generation error: {str(e)}")
    
    
    async def analyze_thumbnail_with_vision(self, thumbnail_url: str) -> ThumbnailAnalysis:
        """
        Analyze video thumbnail using GPT-4 Vision API (Build Hours Feature)
        Extracts visual style, colors, composition to enhance Sora prompts
        """
        try:
            # Download the image and convert to base64 (Instagram URLs need authentication)
            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(thumbnail_url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                image_data = response.content
            
            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{image_base64}"
            
            completion = await self.client.chat.completions.create(
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
                                "text": "Analyze this video thumbnail. Identify dominant colors (list 3-5), composition style, visual elements (list 3-7), and overall aesthetic. Return ONLY a JSON object with keys: dominant_colors (array), composition (string), visual_elements (array), style_assessment (string)."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "thumbnail_analysis",
                        "strict": True,
                        "schema": ThumbnailAnalysis.model_json_schema()
                    }
                },
                temperature=0.5
            )
            
            # Parse JSON response
            import json
            response_data = json.loads(completion.choices[0].message.content)
            return ThumbnailAnalysis(**response_data)
            
        except Exception as e:
            print(f"[OpenAI] Vision API error: {str(e)}")
            raise Exception(f"Thumbnail analysis error: {str(e)}")
    
    
    async def create_combined_script(self, results: list, usernames: list, combine_style: str = "fusion") -> str:
        """
        Create a combined Sora script that fuses the best elements from multiple creators.
        """
        try:
            # Build summary of all analyzed videos
            video_summaries = []
            for i, result in enumerate(results):
                summary = f"""
Video {i+1}:
- Engagement: {result.views:,} views, {result.likes:,} likes
- Caption: {result.original_text[:100]}...
- Transcription: {result.transcription[:200]}...
- Individual Sora Script: {result.sora_script[:300]}...
"""
                video_summaries.append(summary)
            
            combined_summary = "\n".join(video_summaries)
            
            if combine_style == "fusion":
                instruction = """Analyze all these successful videos and create ONE UNIFIED Sora prompt that FUSES the best elements from each creator's style.

Blend:
- Visual aesthetics and color palettes
- Pacing and energy levels
- Camera techniques
- Engagement hooks
- Storytelling approaches

Create a single, cohesive Sora prompt that combines the strengths of all these viral videos into one powerful concept."""
            else:  # sequence
                instruction = """Analyze all these successful videos and create ONE SEQUENTIAL Sora prompt that tells a story using elements from each creator.

Structure it as a narrative journey that:
- Opens with the style of the first creator
- Transitions through elements of each subsequent creator
- Builds to a climax using the most engaging techniques
- Creates a cohesive multi-part story

Create a single Sora prompt for a video that flows through these different styles."""
            
            prompt = f"""{instruction}

CREATORS: {', '.join(['@' + u for u in usernames])}

ANALYZED VIDEOS:
{combined_summary}

Create a comprehensive Sora AI prompt that captures the combined power of these successful creators."""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a master video director who can analyze multiple successful creators and blend their styles into powerful new concepts. You understand what makes videos go viral and can synthesize the best elements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8  # Higher creativity for fusion
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Combined script generation error: {str(e)}")
    
    
    async def create_combined_structured_script(self, results: list, usernames: list, combine_style: str = "fusion") -> StructuredSoraScript:
        """
        Create a combined STRUCTURED Sora script using Structured Outputs.
        """
        try:
            # Build comprehensive analysis
            analysis_text = f"COMBINING {len(results)} VIDEOS FROM: {', '.join(['@' + u for u in usernames])}\n\n"
            
            for i, result in enumerate(results):
                analysis_text += f"""
VIDEO {i+1} - {result.views:,} views, {result.likes:,} likes:
Caption: {result.original_text}
Key Content: {result.transcription[:300]}
"""
                if result.thumbnail_analysis:
                    analysis_text += f"Visual Style: {result.thumbnail_analysis.style_assessment}\n"
                    analysis_text += f"Colors: {', '.join(result.thumbnail_analysis.dominant_colors)}\n"
            
            if combine_style == "fusion":
                instruction = "Create a FUSION Sora prompt that blends all these styles into one cohesive, powerful video concept."
            else:
                instruction = "Create a SEQUENTIAL Sora prompt that tells a story flowing through these different creator styles."
            
            prompt = f"""{instruction}

{analysis_text}

Synthesize the best visual elements, pacing, camera work, and engagement hooks from all these successful videos into ONE structured Sora prompt."""
            
            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a master video director creating structured Sora prompts by analyzing and combining successful creator styles."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "combined_sora_script",
                        "strict": True,
                        "schema": StructuredSoraScript.model_json_schema()
                    }
                },
                temperature=0.8
            )
            
            import json
            response_data = json.loads(completion.choices[0].message.content)
            return StructuredSoraScript(**response_data)
            
        except Exception as e:
            raise Exception(f"Combined structured script error: {str(e)}")
