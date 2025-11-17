from openai import AsyncOpenAI
from typing import Dict, Optional
import os
import base64
from models.schemas import StructuredSoraScript, ThumbnailAnalysis

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    print("[Warning] Anthropic SDK not installed. Claude features will be disabled.")


class OpenAIService:
    """Service for OpenAI and Claude API interactions - Whisper + GPT-4 Vision + Claude + Structured Outputs"""
    
    def __init__(self, api_key: str, anthropic_key: Optional[str] = None, fine_tuned_model: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key)
        # Use fine-tuned model if provided, otherwise use gpt-4o-2024-08-06 (supports Structured Outputs)
        self.model = fine_tuned_model or "gpt-4o-2024-08-06"
        print(f"[OpenAI] Using model: {self.model}")
        print(f"[OpenAI] Build Hours: Structured Outputs enabled ✓")
        
        # Initialize Claude client if available
        if ANTHROPIC_AVAILABLE and anthropic_key:
            self.claude_client = AsyncAnthropic(api_key=anthropic_key)
            self.claude_available = True
            print(f"[Claude] Claude API initialized ✓")
        else:
            self.claude_client = None
            self.claude_available = False
            if not ANTHROPIC_AVAILABLE:
                print(f"[Claude] Anthropic SDK not available")
            elif not anthropic_key:
                print(f"[Claude] Anthropic API key not provided")
    
    async def research_topic_context(self, trend_data: Dict) -> str:
        """
        Use GPT-4 to research and understand the context of a LinkedIn trending topic.
        Analyzes the topic, industry, and related information to create comprehensive context.
        """
        try:
            topic = trend_data.get('topic', '')
            description = trend_data.get('description', '')
            industry = trend_data.get('industry', '')
            hashtags = trend_data.get('hashtags', [])
            sentiment = trend_data.get('sentiment', '')
            
            if not topic and not description:
                return "No topic information available for context analysis."
            
            prompt = f"""Analyze this LinkedIn trending topic and provide comprehensive context:

TOPIC INFORMATION:
- Topic: {topic}
- Description: {description}
- Industry: {industry}
- Hashtags: {', '.join(hashtags)}
- Sentiment: {sentiment}
- Engagement: {trend_data.get('engagement', 'N/A')}

Based on this information, provide:
1. Why this topic is trending and relevant now
2. Key insights and implications for professionals
3. Target audience and their interests
4. Industry context and positioning
5. Key messaging themes that resonate
6. Visual and tone recommendations for professional content

Be specific and detailed. Format as a clear, structured summary that can be used to inform professional video content creation for LinkedIn."""

            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business strategist and content expert specializing in LinkedIn trends and professional content. Analyze trending topics to understand their context and implications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            context_summary = completion.choices[0].message.content
            print(f"[OpenAI] Topic context researched: {len(context_summary)} characters")
            return context_summary
            
        except Exception as e:
            print(f"[OpenAI] Error researching topic context: {str(e)}")
            return f"Topic context: {trend_data.get('topic', '')} - {trend_data.get('description', 'No description available')}"
    
    async def research_profile_context(self, profile_context: Dict) -> str:
        """
        Use GPT-4 to research and understand the profile/page context from profile information.
        Works for all account types: business accounts, personal brands, creators, influencers, etc.
        Analyzes bio, account type, and other profile data to create comprehensive context.
        """
        try:
            bio = profile_context.get('biography', '')
            full_name = profile_context.get('full_name', '')
            business_category = profile_context.get('business_category', '')
            external_url = profile_context.get('external_url', '')
            is_business = profile_context.get('is_business_account', False)
            followers = profile_context.get('followers', 0)
            is_verified = profile_context.get('is_verified', False)
            posts_count = profile_context.get('posts_count', 0)
            
            if not bio and not full_name:
                return "No profile information available for context analysis."
            
            account_type = "Business Account" if is_business else "Personal/Creator Account"
            
            prompt = f"""Analyze this Instagram profile and provide comprehensive context about the page/account:

PROFILE INFORMATION:
- Full Name: {full_name}
- Username: {profile_context.get('username', '')}
- Bio: {bio}
- Account Type: {account_type}
- Business Category: {business_category if business_category else 'N/A (Personal/Creator account)'}
- External URL: {external_url if external_url else 'None'}
- Followers: {followers:,}
- Posts: {posts_count:,}
- Verified: {is_verified}

Based on this information, analyze and provide:
1. What type of account this is (business, personal brand, creator, influencer, artist, etc.)
2. Their main focus/content themes (products, services, lifestyle, niche, expertise, etc.)
3. Their target audience and community
4. Their content voice, style, and aesthetic
5. Key messaging themes and values
6. Content positioning and what makes them unique

IMPORTANT: This works for ALL account types:
- Business accounts: analyze products/services, brand identity, target market
- Personal brands/creators: analyze their niche, content style, audience, expertise
- Influencers: analyze their niche, content themes, audience demographics
- Artists/creatives: analyze their art style, themes, creative direction
- Personal accounts: analyze their interests, lifestyle, content themes

Be specific and detailed. If information is limited, make reasonable inferences based on available data (bio, name, follower count, etc.).
Format as a clear, structured summary that can be used to inform video content creation that matches their style and audience."""

            completion = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a social media strategist and content analyst. Analyze Instagram profiles (business, personal, creator, influencer, etc.) to understand their context, style, audience, and content themes. Work with all account types equally well."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            context_summary = completion.choices[0].message.content
            print(f"[OpenAI] Profile context researched: {len(context_summary)} characters")
            return context_summary
            
        except Exception as e:
            print(f"[OpenAI] Error researching profile context: {str(e)}")
            return f"Profile context: {profile_context.get('full_name', '')} - {profile_context.get('biography', 'No bio available')}"
    
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
    
    async def generate_sora_script(self, transcription: str, video_metadata: Dict, target_duration: int = 8, page_context: Optional[str] = None, llm_provider: str = "openai") -> str:
        """
        Generate basic Sora script (legacy method for backward compatibility)
        
        Args:
            target_duration: Target video duration in seconds (5-16)
        """
        try:
            # Check if transcription is valid
            has_valid_transcription = not transcription.startswith("[") and len(transcription) > 20
            
            # Build context section
            context_section = ""
            if page_context:
                context_section = f"""
PAGE/PROFILE CONTEXT:
{page_context}

This context should inform the video's messaging, tone, and visual style to align with the page/account identity (works for business, personal, creator, influencer accounts, etc.).
"""
            
            if has_valid_transcription:
                prompt = f"""Based on this video transcription, metrics, and page context, create a detailed Sora AI video generation prompt for a {target_duration}-second video.

{context_section}TRANSCRIPTION:
{transcription}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}
- Original Caption: {video_metadata.get('text', 'N/A')}

TARGET DURATION: {target_duration} seconds

Create a Sora prompt that captures the core concept, visual style, camera work, timing, and engagement factors. The prompt should align with the page/profile context provided above. Start the prompt with "Create a {target_duration}-second video..."."""
            else:
                # No valid transcription - use caption and metrics only
                prompt = f"""Based on this Instagram video's caption, engagement metrics, and page context, create a detailed Sora AI video generation prompt for a {target_duration}-second video.

{context_section}VIDEO CAPTION:
{video_metadata.get('text', 'No caption available')}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}

TARGET DURATION: {target_duration} seconds

NOTE: Audio transcription was not available for this video (may be music-only or no audio).

Create a Sora prompt that captures likely visual style, camera work, timing, and engagement factors based on the caption, popularity metrics, and page/profile context. Start the prompt with "Create a {target_duration}-second video..."."""

            # Use OpenAI or Claude based on provider
            if llm_provider.lower() == "claude" and self.claude_available:
                print(f"[Claude] Generating Sora script with Claude...")
                message = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system="You are an expert video production director creating Sora AI prompts.",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return message.content[0].text
            else:
                # Default to OpenAI
                if llm_provider.lower() == "claude":
                    print(f"[Warning] Claude requested but not available, falling back to OpenAI")
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
    
    
    async def generate_structured_sora_script(self, transcription: str, video_metadata: Dict, thumbnail_analysis: Optional[ThumbnailAnalysis] = None, target_duration: int = 8, page_context: Optional[str] = None) -> StructuredSoraScript:
        """
        Generate structured Sora script using OpenAI Structured Outputs (Build Hours Feature)
        Guarantees valid, consistent JSON structure matching StructuredSoraScript schema
        
        Args:
            target_duration: Target video duration in seconds (5-16)
        """
        try:
            # Build context including page context and thumbnail analysis if available
            context = ""
            if page_context:
                context += f"""PAGE/PROFILE CONTEXT:
{page_context}

This context should inform the video's messaging, tone, visual style, and overall approach to align with the page/account identity (works for business, personal, creator, influencer accounts, etc.).

"""
            
            context += f"""TRANSCRIPTION:
{transcription}

VIDEO METRICS:
- Views: {video_metadata.get('views', 0):,}
- Likes: {video_metadata.get('likes', 0):,}
- Original Text: {video_metadata.get('text', 'N/A')}
- Duration: {video_metadata.get('duration', 'Unknown')} seconds

TARGET OUTPUT DURATION: {target_duration} seconds"""

            if thumbnail_analysis:
                context += f"""

VISUAL ANALYSIS (from thumbnail):
- Dominant Colors: {', '.join(thumbnail_analysis.dominant_colors)}
- Composition: {thumbnail_analysis.composition}
- Visual Elements: {', '.join(thumbnail_analysis.visual_elements)}
- Style: {thumbnail_analysis.style_assessment}"""

            prompt = f"""Based on this video data and page/profile context, create a comprehensive Sora AI video generation prompt.

{context}

IMPORTANT: The generated video MUST be exactly {target_duration} seconds long. Structure your timing and pacing to fit this duration precisely.

Analyze what made this video successful and create a detailed, structured Sora prompt that captures:
1. Core concept and message (aligned with the page/profile context)
2. Visual style (colors, lighting, mood, references) that matches the account identity
3. Camera work (shot types, movements, angles)
4. Timing and pacing structure (MUST fit {target_duration} seconds)
5. Engagement optimization based on metrics
6. Consistency with the page/profile context provided (works for business, personal, creator, influencer accounts, etc.)

The video should feel authentic to the page/account while maintaining the successful elements from the analyzed video.
In the full_prompt field, explicitly state "Create a {target_duration}-second video..." at the beginning.
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
    
    
    async def create_combined_script(self, results: list, usernames: list, combine_style: str = "fusion", target_duration: int = 12) -> str:
        """
        Create a combined Sora script that fuses the best elements from multiple creators.
        
        Args:
            target_duration: Target video duration in seconds (5-16)
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
                instruction = f"""Analyze all these successful videos and create ONE UNIFIED Sora prompt for a {target_duration}-second video that FUSES the best elements from each creator's style.

Blend:
- Visual aesthetics and color palettes
- Pacing and energy levels
- Camera techniques
- Engagement hooks
- Storytelling approaches

Create a single, cohesive Sora prompt that combines the strengths of all these viral videos into one powerful {target_duration}-second concept. Start with "Create a {target_duration}-second video..."."""
            else:  # sequence
                instruction = f"""Analyze all these successful videos and create ONE SEQUENTIAL Sora prompt for a {target_duration}-second video that tells a story using elements from each creator.

Structure it as a narrative journey that:
- Opens with the style of the first creator
- Transitions through elements of each subsequent creator
- Builds to a climax using the most engaging techniques
- Creates a cohesive multi-part story

Create a single Sora prompt for a {target_duration}-second video that flows through these different styles. Start with "Create a {target_duration}-second video..."."""
            
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
    
    
    async def create_combined_structured_script(self, results: list, usernames: list, combine_style: str = "fusion", target_duration: int = 12) -> StructuredSoraScript:
        """
        Create a combined STRUCTURED Sora script using Structured Outputs.
        
        Args:
            target_duration: Target video duration in seconds (5-16)
        """
        try:
            # Build comprehensive analysis
            analysis_text = f"COMBINING {len(results)} VIDEOS FROM: {', '.join(['@' + u for u in usernames])}\n"
            analysis_text += f"TARGET OUTPUT DURATION: {target_duration} seconds\n\n"
            
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
                instruction = f"Create a FUSION Sora prompt that blends all these styles into one cohesive, powerful {target_duration}-second video concept."
            else:
                instruction = f"Create a SEQUENTIAL Sora prompt that tells a story flowing through these different creator styles in exactly {target_duration} seconds."
            
            prompt = f"""{instruction}

{analysis_text}

IMPORTANT: The final video MUST be exactly {target_duration} seconds. Structure the timing and pacing accordingly.

Synthesize the best visual elements, pacing, camera work, and engagement hooks from all these successful videos into ONE structured Sora prompt.

In the full_prompt field, start with "Create a {target_duration}-second video..."."""
            
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
    
    
    async def generate_sora_video(self, prompt: str, model: str = "sora-2", size: str = "1280x720", seconds: int = 8) -> dict:
        """
        Generate a video using Sora API (OpenAI Video Generation)
        Returns job info with status and ID for polling
        
        API Docs: https://platform.openai.com/docs/guides/video-generation
        """
        try:
            print(f"[Sora] Starting video generation with {model}")
            print(f"[Sora] Prompt: {prompt[:100]}...")
            print(f"[Sora] Size: {size}, Duration: {seconds}s")
            
            # Create video generation job
            # Note: 'seconds' must be a string according to the API docs
            video_job = await self.client.videos.create(
                model=model,
                prompt=prompt,
                size=size,
                seconds=str(seconds)
            )
            
            print(f"[Sora] Job created: {video_job.id}")
            print(f"[Sora] Status: {video_job.status}")
            print(f"[Sora] Progress: {getattr(video_job, 'progress', 0)}%")
            
            return {
                "job_id": video_job.id,
                "status": video_job.status,
                "progress": getattr(video_job, 'progress', 0),
                "model": video_job.model,
                "created_at": video_job.created_at,
                "size": size,
                "seconds": seconds
            }
            
        except Exception as e:
            print(f"[Sora] Video generation error: {str(e)}")
            raise Exception(f"Sora video generation error: {str(e)}")
    
    
    async def get_sora_video_status(self, job_id: str) -> dict:
        """
        Poll the status of a Sora video generation job
        Possible statuses: queued, in_progress, completed, failed
        """
        try:
            video_job = await self.client.videos.retrieve(job_id)
            
            print(f"[Sora] Status check for {job_id}: {video_job.status} ({getattr(video_job, 'progress', 0)}%)")
            
            result = {
                "job_id": video_job.id,
                "status": video_job.status,
                "progress": getattr(video_job, 'progress', 0),
                "model": video_job.model,
                "created_at": video_job.created_at
            }
            
            # If completed, add download URL
            if video_job.status == "completed":
                result["video_url"] = f"/api/sora/download/{job_id}"
                print(f"[Sora] Video ready for download: {job_id}")
            
            return result
            
        except Exception as e:
            print(f"[Sora] Status check error: {str(e)}")
            raise Exception(f"Failed to get video status: {str(e)}")
    
    
    async def download_sora_video(self, job_id: str) -> bytes:
        """
        Download the completed Sora video as bytes
        Uses the download_content method from the OpenAI SDK
        Returns: HttpxBinaryResponseContent which has .content property
        """
        try:
            print(f"[Sora] Downloading video: {job_id}")
            
            # Download video content from Sora API (returns HttpxBinaryResponseContent)
            response = await self.client.videos.download_content(job_id)
            
            # Use .content property to get bytes (synchronous, already loaded)
            video_bytes = response.content
            
            print(f"[Sora] Downloaded {len(video_bytes):,} bytes")
            return video_bytes
            
        except Exception as e:
            print(f"[Sora] Download error: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
