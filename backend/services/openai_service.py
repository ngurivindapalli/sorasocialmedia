from openai import AsyncOpenAI
from typing import Dict, Optional, List
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
    """Service for OpenAI and Claude API interactions - Whisper + GPT-4 Vision + Claude + Structured Outputs
    Enhanced with Hyperspell memory integration for context-aware responses"""
    
    def __init__(self, api_key: str, anthropic_key: Optional[str] = None, fine_tuned_model: Optional[str] = None, hyperspell_service=None):
        self.client = AsyncOpenAI(api_key=api_key)
        # Use fine-tuned model if provided, otherwise use gpt-4o-2024-08-06 (supports Structured Outputs)
        self.model = fine_tuned_model or "gpt-4o-2024-08-06"
        print(f"[OpenAI] Using model: {self.model}")
        print(f"[OpenAI] Build Hours: Structured Outputs enabled OK")
        
        # Store Hyperspell service for memory integration
        self.hyperspell_service = hyperspell_service
        
        # Initialize Claude client if available
        if ANTHROPIC_AVAILABLE and anthropic_key:
            self.claude_client = AsyncAnthropic(api_key=anthropic_key)
            self.claude_available = True
            hyperspell_status = "with Hyperspell memory" if (hyperspell_service and hyperspell_service.is_available()) else ""
            print(f"[Claude] Claude API initialized OK {hyperspell_status}")
        else:
            self.claude_client = None
            self.claude_available = False
            if not ANTHROPIC_AVAILABLE:
                print(f"[Claude] Anthropic SDK not available")
            elif not anthropic_key:
                print(f"[Claude] Anthropic API key not provided")
    
    async def _get_hyperspell_context(self, user_id: str, query: str) -> str:
        """
        Helper method to get Hyperspell memory context for AI prompts
        
        Args:
            user_id: User identifier
            query: Query string to search memories
            
        Returns:
            Formatted context string or empty string if unavailable
        """
        if not self.hyperspell_service or not self.hyperspell_service.is_available():
            return ""
        
        try:
            context = await self.hyperspell_service.get_context_summary(user_id, query)
            return context
        except Exception as e:
            print(f"[OpenAI+Hyperspell] Error fetching memory context: {e}")
            return ""
    
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
    
    async def research_profile_context(self, profile_context: Dict, document_context: str = "") -> str:
        """
        Use GPT-4 to research and understand the profile/page context from profile information.
        Works for all account types: business accounts, personal brands, creators, influencers, etc.
        Analyzes bio, account type, and other profile data to create comprehensive context.
        Optionally includes document context for additional information.
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
            
            # Add document context to prompt if provided
            doc_context_section = ""
            if document_context and len(document_context.strip()) > 0:
                doc_context_section = f"""

ADDITIONAL DOCUMENT CONTEXT:
The following documents were provided by the user to provide additional context about their brand, products, services, or content strategy. Use this information to enhance your understanding of their brand identity and content themes:

{document_context[:5000]}  # Limit to first 5000 chars to avoid token limits

IMPORTANT: Integrate insights from the document context above into your analysis. Reference specific details, messaging, or brand elements from the documents when relevant."""
            
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
Format as a clear, structured summary that can be used to inform video content creation that matches their style and audience.{doc_context_section}"""

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
                
                # Enhance prompt with Hyperspell memory if available
                enhanced_prompt = prompt
                if self.hyperspell_service and self.hyperspell_service.is_available():
                    # Extract query from transcription or metadata for memory lookup
                    memory_query = transcription[:200] if transcription and len(transcription) > 20 else video_metadata.get('text', '')[:200]
                    if memory_query:
                        # Use provided user_id or fallback to metadata or default
                        lookup_user_id = user_id or video_metadata.get('user_id', 'default_user')
                        hyperspell_context = await self._get_hyperspell_context(lookup_user_id, memory_query)
                        if hyperspell_context:
                            enhanced_prompt = f"""{hyperspell_context}

{prompt}"""
                            print(f"[Claude+Hyperspell] Enhanced prompt with memory context ({len(hyperspell_context)} chars)")
                
                message = await self.claude_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    temperature=0.7,
                    system="You are an expert video production director creating Sora AI prompts. Use any provided memory context to personalize the prompt.",
                    messages=[
                        {"role": "user", "content": enhanced_prompt}
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
    
    
    async def generate_structured_sora_script(self, transcription: str, video_metadata: Dict, thumbnail_analysis: Optional[ThumbnailAnalysis] = None, target_duration: int = 8, page_context: Optional[str] = None, user_id: Optional[str] = None) -> StructuredSoraScript:
        """
        Generate structured Sora script using OpenAI Structured Outputs (Build Hours Feature)
        Guarantees valid, consistent JSON structure matching StructuredSoraScript schema
        
        Args:
            target_duration: Target video duration in seconds (5-16)
        """
        try:
            # Enhance page_context with Hyperspell memory if available
            enhanced_page_context = page_context or ""
            if user_id and self.hyperspell_service and self.hyperspell_service.is_available():
                try:
                    # Build query from transcription and metadata
                    memory_query = f"{transcription[:200]} {video_metadata.get('text', '')[:100]}".strip()
                    if memory_query:
                        hyperspell_context = await self._get_hyperspell_context(user_id, memory_query)
                        if hyperspell_context:
                            enhanced_page_context = f"""{hyperspell_context}

{enhanced_page_context}"""
                            print(f"[OpenAI+Hyperspell] Enhanced structured script with memory context")
                except Exception as e:
                    print(f"[OpenAI+Hyperspell] Memory query skipped: {e}")
            
            # Build context including page context and thumbnail analysis if available
            context = ""
            if enhanced_page_context:
                context += f"""PAGE/PROFILE CONTEXT (Enhanced with Hyperspell Memory):
{enhanced_page_context}

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

            prompt = f"""Based on this video data and page/profile context, create a highly detailed, marketable Sora AI video generation prompt optimized for maximum engagement and professional quality.

{context}

IMPORTANT: The generated video MUST be exactly {target_duration} seconds long. Structure your timing and pacing to fit this duration precisely.

MARKETING & ENGAGEMENT FOCUS:
Analyze what made this video successful and create a comprehensive, structured Sora prompt that captures:

1. CORE CONCEPT & MESSAGE (aligned with page/profile context):
   - What is the central message or story?
   - How does it align with the account's brand identity and audience?
   - What makes this concept compelling and shareable?
   - Include specific hooks or attention-grabbing elements

2. VISUAL STYLE (colors, lighting, mood, references):
   - Match the account's visual identity and aesthetic
   - Choose colors that evoke the right emotions and align with brand
   - Lighting that creates the desired mood (professional, energetic, contemplative, etc.)
   - Visual references that resonate with the target audience
   - Professional quality suitable for social media engagement

3. CINEMATIC CAMERA WORK (shot types, movements, angles):
   - Dynamic camera movements that maintain viewer attention
   - Shot progression that tells a visual story
   - Angles that create engagement and visual interest
   - Transitions that flow naturally and reinforce the narrative
   - Professional cinematography suitable for viral content

4. PRECISE TIMING & PACING (MUST fit {target_duration} seconds exactly):
   - Break down the {target_duration}-second timeline into specific moments
   - Opening hook (first 2-3 seconds) - must grab attention immediately
   - Value delivery (middle section) - core message and insights
   - Closing impact (final 2-3 seconds) - memorable takeaway or call-to-action
   - Pacing that maintains engagement throughout

5. ENGAGEMENT OPTIMIZATION:
   - Visual elements that stop the scroll
   - Moments designed for maximum impact
   - Text overlay opportunities for key statistics or quotes
   - Visual metaphors that reinforce the message
   - Elements that encourage sharing and commenting

6. AUTHENTICITY & BRAND ALIGNMENT:
   - Consistency with the page/profile context (works for business, personal, creator, influencer accounts, etc.)
   - Visual style that feels authentic to the account
   - Messaging that resonates with the account's audience
   - Professional quality that matches the account's standards

7. MARKETABLE ELEMENTS:
   - Include specific visual details that make the video shareable
   - Create "wow moments" that prompt engagement
   - Use visual storytelling techniques that amplify the message
   - Professional aesthetic that builds credibility
   - Dynamic elements that maintain viewer attention

The video should feel authentic to the page/account while maximizing engagement potential through professional cinematography, compelling visuals, and strategic pacing.

In the full_prompt field, explicitly state "Create a {target_duration}-second video..." at the beginning, then provide an extremely detailed, cinematic description that Sora can use to generate a high-quality, marketable video.

Make it actionable, specific, and optimized for social media engagement."""

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
        
        Available models:
        - "sora-2" (default): Fast model for quick results
        - "sora-2-pro": Higher quality model for professional results
        - "sora-4" or newer: Use if available in your OpenAI account
        
        To use a different model, pass it in the model parameter.
        API Docs: https://platform.openai.com/docs/guides/video-generation
        """
        try:
            # CRITICAL: Validate duration - Sora only supports 4, 8, or 12 seconds
            valid_durations = [4, 8, 12]
            original_seconds = seconds
            if seconds not in valid_durations:
                # Clamp to nearest valid duration
                seconds = min(valid_durations, key=lambda x: abs(x - seconds))
                print(f"[Sora] WARNING CRITICAL: Duration {original_seconds}s is invalid. Clamped to {seconds}s (valid Sora values: {valid_durations})")
            
            # Final safety check
            if seconds not in valid_durations:
                seconds = 8  # Safe fallback
                print(f"[Sora] WARNING CRITICAL: Forced duration to safe fallback: {seconds}s")
            
            print(f"[Sora] Starting video generation with {model}")
            print(f"[Sora] Prompt: {prompt[:100]}...")
            print(f"[Sora] Size: {size}, Duration: {seconds}s (VALIDATED)")
            
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
    
    async def generate_video_options(
        self,
        document_context: str,
        num_options: int = 3,
        video_model: str = "sora-2"
    ) -> List[Dict[str, str]]:
        """
        Generate multiple video options from document context.
        Returns a list of video options with different approaches, topics, and styles.
        """
        try:
            print(f"[Video Options] Generating {num_options} video options from {len(document_context)} chars of context")
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            
            if is_veo3:
                duration_instruction = """4. DURATION: Choose a duration from 40-60 seconds for quality content
   - CRITICAL: DO NOT choose 4, 8, or 12 seconds - those are Sora 2 constraints ONLY
   - Minimum: 40 seconds for quality content
   - Recommended: 45-50 seconds for standard content
   - Complex topics: 50-60 seconds
   - Examples: 40, 45, 50, 55, 60 seconds (NOT 4, 8, or 12)"""
                duration_example = "[40-60]"
            else:
                duration_instruction = "4. DURATION: Choose ONE of: 4, 8, or 12 seconds (Sora only supports these)"
                duration_example = "[4, 8, or 12]"
            
            options_prompt = f"""Analyze this document content and generate {num_options} distinct video options, each with a different approach, topic, and style:

DOCUMENT CONTENT:
{document_context[:15000]}

VIDEO MODEL: {video_model or "sora-2"}

For each option, provide:
1. TITLE: A compelling title for this video option
2. TOPIC: The main topic/theme
3. APPROACH: The style/angle (e.g., "Educational tutorial", "Problem-solution story", "Quick tips", "Case study", "Thought leadership")
{duration_instruction}
5. TARGET AUDIENCE: Who this option targets
6. KEY MESSAGE: The main takeaway
7. WHY THIS WORKS: Why this option would perform well on LinkedIn

Format your response as:
OPTION 1:
TITLE: [title]
TOPIC: [topic]
APPROACH: [approach]
DURATION: {duration_example}
TARGET AUDIENCE: [audience]
KEY MESSAGE: [message]
WHY THIS WORKS: [reasoning]

OPTION 2:
...

Generate {num_options} distinct options that offer different value propositions."""
            
            system_message = "You are an expert LinkedIn content strategist. You create multiple distinct video options from document content, each with unique angles and value propositions."
            if is_veo3:
                system_message += " CRITICAL: You are creating options for Veo 3. Choose durations from 40-60 seconds (NOT 4, 8, or 12). These are quality, postable videos that need longer durations."
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": options_prompt
                    }
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            options_text = response.choices[0].message.content
            print(f"[Video Options] OK Generated options text ({len(options_text)} chars)")
            
            # Parse options
            options = []
            import re
            option_blocks = re.split(r'OPTION\s+\d+:', options_text, flags=re.IGNORECASE)
            
            for i, block in enumerate(option_blocks[1:], 1):  # Skip first empty block
                option = {}
                title_match = re.search(r'TITLE:\s*(.+?)(?:\n|TOPIC|$)', block, re.IGNORECASE)
                topic_match = re.search(r'TOPIC:\s*(.+?)(?:\n|APPROACH|$)', block, re.IGNORECASE)
                approach_match = re.search(r'APPROACH:\s*(.+?)(?:\n|DURATION|$)', block, re.IGNORECASE)
                duration_match = re.search(r'DURATION:\s*(\d+)', block, re.IGNORECASE)
                audience_match = re.search(r'TARGET AUDIENCE:\s*(.+?)(?:\n|KEY MESSAGE|$)', block, re.IGNORECASE)
                message_match = re.search(r'KEY MESSAGE:\s*(.+?)(?:\n|WHY|$)', block, re.IGNORECASE)
                why_match = re.search(r'WHY THIS WORKS:\s*(.+?)(?:\n|OPTION|$)', block, re.IGNORECASE)
                
                if title_match:
                    option['title'] = title_match.group(1).strip()
                if topic_match:
                    option['topic'] = topic_match.group(1).strip()
                if approach_match:
                    option['approach'] = approach_match.group(1).strip()
                if duration_match:
                    duration = int(duration_match.group(1))
                    # Validate duration based on video model (is_veo3 is defined above)
                    if is_veo3:
                        # Veo 3: Force to 40-60 seconds, override 4, 8, 12
                        if duration in [4, 8, 12]:
                            print(f"[Video Options] WARNING Option {i}: AI chose {duration}s for Veo 3. Forcing to 45s.")
                            duration = 45
                        elif duration < 40:
                            print(f"[Video Options] WARNING Option {i}: Duration {duration}s too short for Veo 3. Overriding to 40s.")
                            duration = 40
                        elif duration > 60:
                            duration = 60
                        option['duration'] = duration
                    else:
                        # Sora: Validate to 4, 8, 12
                        valid_durations = [4, 8, 12]
                        if duration not in valid_durations:
                            duration = min(valid_durations, key=lambda x: abs(x - duration))
                        option['duration'] = duration
                if audience_match:
                    option['target_audience'] = audience_match.group(1).strip()
                if message_match:
                    option['key_message'] = message_match.group(1).strip()
                if why_match:
                    option['why_this_works'] = why_match.group(1).strip()
                
                if option:
                    option['id'] = f"option_{i}"
                    options.append(option)
            
            print(f"[Video Options] OK Parsed {len(options)} video options")
            return options[:num_options]  # Return up to num_options
            
        except Exception as e:
            print(f"[Video Options] Error generating options: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return a single default option on error
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            default_duration = 45 if is_veo3 else 8
            return [{
                "id": "option_1",
                "title": "Professional Insights Video",
                "topic": "Key insights from your documents",
                "approach": "Educational content",
                "duration": default_duration,
                "target_audience": "LinkedIn professionals",
                "key_message": "Derived from document content",
                "why_this_works": "Educational content performs well on LinkedIn"
            }]
    
    async def generate_linkedin_optimized_script(
        self,
        document_context: str,
        topic: Optional[str] = None,
        duration: Optional[int] = None,
        target_audience: Optional[str] = None,
        key_message: Optional[str] = None,
        video_model: Optional[str] = "sora-2",
        user_context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a LinkedIn-optimized video script using deep document context analysis.
        This method analyzes document content comprehensively and creates scripts optimized
        for LinkedIn engagement, including hooks, storytelling, and performance best practices.
        
        Returns a dictionary with:
        - script: The final video script
        - sora_prompt: Optimized Sora prompt for video generation
        - linkedin_optimization: Analysis of why this will perform well on LinkedIn
        - key_insights: Key insights extracted from documents
        """
        try:
            print(f"[LinkedIn Script] Generating LinkedIn-optimized script from {len(document_context)} chars of context")
            
            # Step 1: Deep document analysis - extract key insights and AI decisions
            topic_instruction = f"TOPIC/THEME: {topic}" if topic else "TOPIC/THEME: [AI DECISION REQUIRED - Analyze documents and determine the best video topic/theme]"
            audience_instruction = f"TARGET AUDIENCE: {target_audience}" if target_audience else "TARGET AUDIENCE: [AI DECISION REQUIRED - Determine who would benefit most from this content]"
            message_instruction = f"KEY MESSAGE: {key_message}" if key_message else "KEY MESSAGE: [AI DECISION REQUIRED - Determine the most compelling key message]"
            
            # Duration instruction based on video model
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            if duration:
                duration_instruction = f"DURATION: {duration} seconds"
            elif is_veo3:
                duration_instruction = """DURATION: [AI DECISION REQUIRED - Choose optimal duration from 4-60 seconds based on content complexity. 
IMPORTANT FOR VEO 3:
- For simple concepts: 15-25 seconds
- For standard educational content: 25-40 seconds (RECOMMENDED)
- For complex topics with multiple insights: 40-60 seconds
- LinkedIn performs best with longer, value-dense content (30-60 seconds)
- Don't rush - use the full duration to deliver complete value
- Ensure all key points are covered without cutting off important information"""
            else:
                duration_instruction = "DURATION: [AI DECISION REQUIRED - Choose ONE of: 4, 8, or 12 seconds only. Sora only supports these durations. This is a hard constraint - you MUST choose exactly 4, 8, or 12 seconds.]"
            
            # Add user context if available
            user_context_section = ""
            if user_context and len(user_context.strip()) > 0:
                user_context_section = f"""

USER CONTEXT & PREFERENCES (for personalization):
{user_context}

IMPORTANT: Use this user context to personalize the script. Align with their brand voice, content style, successful topics, and behavioral patterns. This context represents what has worked well for this user in the past.
"""
            
            analysis_prompt = f"""Analyze this document content deeply to extract the most valuable insights for LinkedIn video content and make strategic decisions:

DOCUMENT CONTENT:
{document_context[:15000]}  # Use more context for better analysis

{topic_instruction}
{audience_instruction}
{message_instruction}
{duration_instruction}
{user_context_section}

YOUR TASK - Extract and decide:

1. VIDEO TOPIC/THEME (if not provided):
   - What is the BEST video topic/theme based on the document content?
   - What would be most engaging and valuable for LinkedIn professionals?
   - Consider: educational content, marketing insights, thought leadership, product/service highlights

2. TARGET AUDIENCE (if not provided):
   - Who would benefit most from this content?
   - What professional demographic would find this most valuable?
   - Be specific (e.g., "B2B SaaS founders", "Marketing directors at enterprise companies")

3. KEY MESSAGE (if not provided):
   - What is the most compelling key message or call-to-action?
   - What should viewers learn, understand, or do after watching?

4. OPTIMAL DURATION (if not provided):
   - CRITICAL: Duration depends on the video generation model:
   - If using Sora 2: You MUST choose ONE of: 4, 8, or 12 seconds only (Sora API limitation)
   - If using Veo 3: You can choose ANY duration from 4-60 seconds based on content needs
   - FOR VEO 3 - CRITICAL RULES (READ CAREFULLY):
     * ABSOLUTE RULE: DO NOT choose 4, 8, or 12 seconds - those are Sora 2 constraints ONLY
     * If you choose 4, 8, or 12, the system will FORCE it to 40 seconds
     * Veo 3 supports 4-148 seconds (8s initial + automatic extensions in 7s increments)
     * MINIMUM: 30 seconds for quality content (NOT 4, 8, or 12)
     * Simple concepts: 35-50 seconds (NOT 4, 8, or 12)
     * Standard educational content: 50-80 seconds (RECOMMENDED - NOT 8 or 12)
     * Complex topics, detailed insights: 80-148 seconds (NOT 12)
     * Examples of CORRECT durations: 40, 50, 60, 70, 80, 90, 100, 120, 148 seconds
     * Examples of WRONG durations: 4, 8, 12 seconds (NEVER use these for Veo 3)
     * IMPORTANT: Longer videos (50-148s) perform MUCH better on LinkedIn - prioritize quality and completeness
     * Veo 3 will automatically extend videos beyond 8 seconds using extension feature
     * This is for quality, postable videos - use longer durations
     * Don't rush - ensure the full value is delivered with proper pacing
   - Consider LinkedIn engagement patterns but prioritize content completeness
   - Don't cut off important information - choose duration that allows full value delivery

5. KEY INSIGHTS: The 3-5 most important, actionable insights from the documents
6. UNIQUE VALUE: What makes this content unique or differentiated?
7. PROFESSIONAL ANGLE: How to frame this for a LinkedIn professional audience
8. ENGAGEMENT HOOKS: What questions, statistics, or statements would capture attention immediately?
9. STORY STRUCTURE: What narrative arc would be most compelling (problem-solution, insight-story, transformation)?

Be specific and reference actual details from the documents. Think like a LinkedIn content strategist who knows what performs well."""
            
            analysis_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert LinkedIn content strategist with deep knowledge of what performs well on LinkedIn. You analyze document content to extract the most engaging, professional insights for video content."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            document_analysis = analysis_response.choices[0].message.content
            print(f"[LinkedIn Script] OK Document analysis complete ({len(document_analysis)} chars)")
            
            # Validate user-provided duration if given - check video model first!
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            if duration is not None:
                if is_veo3:
                    # Veo 3: validate range (4-60) but don't clamp to Sora values
                    if duration < 4:
                        duration = 4
                        print(f"[LinkedIn Script] WARNING User-provided duration adjusted to minimum Veo 3: {duration}s")
                    elif duration > 60:
                        duration = 60
                        print(f"[LinkedIn Script] WARNING User-provided duration adjusted to maximum Veo 3: {duration}s")
                    else:
                        print(f"[LinkedIn Script] OK User-provided Veo 3 duration: {duration}s (valid range: 4-60)")
                else:
                    # Sora only supports 4, 8, 12
                    valid_durations = [4, 8, 12]
                    if duration not in valid_durations:
                        duration = min(valid_durations, key=lambda x: abs(x - duration))
                        print(f"[LinkedIn Script] WARNING User-provided duration adjusted to nearest valid Sora value: {duration}s")
            
            # Extract AI decisions from analysis if not provided - look for structured responses
            ai_topic = topic
            ai_duration = duration
            ai_audience = target_audience
            ai_message = key_message
            
            # Parse analysis to extract AI decisions if they weren't provided
            needs_ai_decisions = not topic or duration is None or not target_audience or not key_message
            if needs_ai_decisions:
                # Determine duration constraints based on video model
                is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
                duration_constraint = "4-60 seconds (choose optimal duration based on content complexity)" if is_veo3 else "MUST be one of: 4, 8, or 12 seconds only"
                
                # Ask AI to explicitly state its decisions in a structured format
                if is_veo3:
                    duration_guidance = """   - For Veo 3: Choose optimal duration from 4-148 seconds based on content complexity
   - CRITICAL: DO NOT choose 4, 8, or 12 seconds - those are Sora 2 constraints ONLY
   - Veo 3 supports 4-148 seconds (8s initial + automatic extensions in 7s increments)
   - MINIMUM: 30 seconds for quality content (NOT 4, 8, or 12)
   - Simple concepts: 40-50 seconds (NOT 4, 8, or 12)
   - Standard educational content: 50-80 seconds (RECOMMENDED - NOT 8 or 12)
   - Complex topics with multiple insights: 80-148 seconds (NOT 12)
   - LinkedIn performs best with longer, value-dense content (50-148 seconds)
   - Examples of GOOD Veo 3 durations: 40, 50, 60, 70, 80, 90, 100, 120, 148 seconds
   - Examples of BAD Veo 3 durations: 4, 8, 12 seconds (those are Sora only - NEVER use these)
   - If you choose 4, 8, or 12, the system will FORCE it to 40 seconds
   - Veo 3 automatically extends videos beyond 8 seconds - choose longer durations confidently
   - Don't rush - use the full duration to deliver complete value
   - Ensure all key points are covered without cutting off important information"""
                else:
                    duration_guidance = """   - For Sora 2: MUST be exactly 4, 8, or 12 seconds (hard API constraint)
   - Consider content complexity: simple (4-8s), standard (8-12s), complex (12s max)
   - Don't cut off important information - work within the 12-second limit"""
                
                if is_veo3:
                    decisions_prompt = f"""Based on the following document analysis, explicitly state your decisions for:
1. VIDEO TOPIC/THEME (one clear topic)
2. OPTIMAL DURATION ({duration_constraint})
{duration_guidance}

CRITICAL REMINDER FOR VEO 3 - READ CAREFULLY:
- You are using Veo 3, which supports 4-148 seconds (8s initial + automatic extensions)
- ABSOLUTE RULE: DO NOT choose 4, 8, or 12 seconds - those are Sora 2 constraints ONLY
- If you choose 4, 8, or 12, the system will FORCE it to 40 seconds
- MINIMUM: 30 seconds for quality content
- Choose 50-80 seconds for standard content (RECOMMENDED)
- Choose 80-148 seconds for complex content
- Examples of CORRECT choices: 40, 50, 60, 70, 80, 90, 100, 120, 148 seconds
- Examples of WRONG choices: 4, 8, 12 seconds (NEVER use these for Veo 3)
- Veo 3 automatically extends videos beyond 8 seconds - choose longer durations confidently
- This is for quality, postable videos - use longer durations

3. TARGET AUDIENCE (specific professional demographic)
4. KEY MESSAGE (main takeaway)

DOCUMENT ANALYSIS:
{document_analysis[:5000]}

VIDEO MODEL: Veo 3 (supports 4-148 seconds with automatic extension - choose 50-148 seconds for quality postable videos)

Format your response as:
TOPIC: [your decision]
DURATION: [number] seconds (MUST be 30-148 for Veo 3, NOT 4, 8, or 12 - choose 50-80 for quality)
AUDIENCE: [specific audience]
MESSAGE: [key message]"""
                else:
                    decisions_prompt = f"""Based on the following document analysis, explicitly state your decisions for:
1. VIDEO TOPIC/THEME (one clear topic)
2. OPTIMAL DURATION ({duration_constraint})
{duration_guidance}
3. TARGET AUDIENCE (specific professional demographic)
4. KEY MESSAGE (main takeaway)

DOCUMENT ANALYSIS:
{document_analysis[:5000]}

VIDEO MODEL: {video_model or "sora-2"}

Format your response as:
TOPIC: [your decision]
DURATION: [number] seconds
AUDIENCE: [specific audience]
MESSAGE: [key message]"""
                
                # Create model-specific system message
                if is_veo3:
                    system_message = """You are a strategic LinkedIn content planner. You are creating content for Veo 3, which supports 4-148 second videos.

CRITICAL FOR VEO 3 - ABSOLUTE RULES:
- NEVER choose 4, 8, or 12 seconds - those are Sora constraints ONLY
- If you choose 4, 8, or 12, the system will FORCE it to 40 seconds
- Veo 3 supports 4-148 seconds (8s initial + automatic extensions in 7s increments)
- MINIMUM: 30 seconds for quality content
- Choose 50-80 seconds for standard educational content (RECOMMENDED)
- Choose 80-148 seconds for complex topics
- Longer videos (50-148s) perform MUCH better on LinkedIn
- Veo 3 automatically extends videos beyond 8 seconds - choose longer durations confidently
- Use the full duration to deliver complete value
- Examples: Choose 40, 50, 60, 70, 80, 90, 100, 120, 148 seconds - NOT 4, 8, or 12

Make clear, decisive choices that use Veo 3's full capabilities for quality, postable videos."""
                else:
                    system_message = "You are a strategic LinkedIn content planner. Make clear, decisive choices for video content based on document analysis. For Sora 2, you MUST choose exactly 4, 8, or 12 seconds only."
                
                decisions_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_message
                        },
                        {
                            "role": "user",
                            "content": decisions_prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                decisions_text = decisions_response.choices[0].message.content
                print(f"[LinkedIn Script] AI Decisions extracted: {decisions_text[:200]}")
                
                # Parse decisions
                import re
                if not ai_topic:
                    topic_match = re.search(r'TOPIC:\s*(.+?)(?:\n|DURATION|$)', decisions_text, re.IGNORECASE)
                    if topic_match:
                        ai_topic = topic_match.group(1).strip()
                
                if ai_duration is None:
                    duration_match = re.search(r'DURATION:\s*(\d+)\s*seconds?', decisions_text, re.IGNORECASE)
                    if duration_match:
                        raw_duration = int(duration_match.group(1))
                        # Check if Veo 3 or Sora 2
                        is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
                        if is_veo3:
                            # Veo 3 supports 4-60 seconds - validate range
                            if raw_duration < 4:
                                ai_duration = 4
                                print(f"[LinkedIn Script] WARNING Adjusted AI decision from {raw_duration}s to minimum Veo 3 duration: {ai_duration}s")
                            elif raw_duration > 60:
                                ai_duration = 60
                                print(f"[LinkedIn Script] WARNING Adjusted AI decision from {raw_duration}s to maximum Veo 3 duration: {ai_duration}s")
                            else:
                                ai_duration = raw_duration
                                print(f"[LinkedIn Script] OK Veo 3 duration: {ai_duration}s (within 4-60 range)")
                        else:
                            # Sora only supports 4, 8, or 12 seconds - clamp to nearest valid value
                            valid_durations = [4, 8, 12]
                            if raw_duration not in valid_durations:
                                # Find nearest valid duration
                                ai_duration = min(valid_durations, key=lambda x: abs(x - raw_duration))
                                print(f"[LinkedIn Script] WARNING Adjusted AI decision from {raw_duration}s to valid Sora value: {ai_duration}s")
                            else:
                                ai_duration = raw_duration
                
                if not ai_audience:
                    audience_match = re.search(r'AUDIENCE:\s*(.+?)(?:\n|MESSAGE|$)', decisions_text, re.IGNORECASE)
                    if audience_match:
                        ai_audience = audience_match.group(1).strip()
                
                if not ai_message:
                    message_match = re.search(r'MESSAGE:\s*(.+?)(?:\n|$)', decisions_text, re.IGNORECASE)
                    if message_match:
                        ai_message = message_match.group(1).strip()
            
            # Use AI decisions or provided values with fallbacks
            final_topic = ai_topic or "Professional Insights"
            # For Veo 3, default to MUCH longer duration (60s) if AI didn't decide; for Sora, default to 8s
            # CRITICAL: If AI chose 4, 8, or 12 for Veo 3, FORCE override to 50 seconds (quality content)
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            if is_veo3:
                if ai_duration is not None and ai_duration in [4, 8, 12]:
                    print(f"[LinkedIn Script] WARNING CRITICAL: AI chose {ai_duration}s for Veo 3 (Sora constraint). FORCING to 50s for quality content.")
                    raw_duration = 50
                elif ai_duration is not None and ai_duration < 30:
                    print(f"[LinkedIn Script] WARNING AI chose {ai_duration}s for Veo 3 (too short). Overriding to 50s for quality content.")
                    raw_duration = 50
                elif ai_duration is not None and ai_duration > 148:
                    print(f"[LinkedIn Script] WARNING AI chose {ai_duration}s for Veo 3 (exceeds max). Clamping to 148s.")
                    raw_duration = 148
                else:
                    raw_duration = ai_duration if ai_duration is not None else 60
                    print(f"[LinkedIn Script] OK Veo 3 duration: {raw_duration}s (will be extended automatically if > 8s)")
            else:
                raw_duration = ai_duration if ai_duration is not None else 8
            final_audience = ai_audience or "LinkedIn professionals"
            final_message = ai_message or "Derived from document insights"
            
            # Validate duration based on video model
            is_veo3 = video_model and (video_model.lower() == "veo-3" or video_model.lower() == "veo3")
            
            if is_veo3:
                # Veo 3 supports 4-148 seconds (8s initial + extensions) - validate range but DON'T clamp to Sora values
                if raw_duration < 4:
                    final_duration = 4
                    print(f"[LinkedIn Script] WARNING Adjusted duration to minimum Veo 3: {final_duration}s")
                elif raw_duration > 148:
                    final_duration = 148
                    print(f"[LinkedIn Script] WARNING Adjusted duration to maximum Veo 3: {final_duration}s")
                else:
                    final_duration = raw_duration
                    # Encourage longer durations for Veo 3
                    if final_duration < 30:
                        print(f"[LinkedIn Script] INFO Veo 3 selected: Consider longer durations (50-148s) for better content quality")
                print(f"[LinkedIn Script] OK Veo 3 duration: {final_duration}s (valid range: 4-148, will be extended automatically if > 8s)")
            else:
                # Sora 2: CRITICAL - ALWAYS validate and clamp to Sora-supported values (4, 8, 12 ONLY)
                valid_durations = [4, 8, 12]
                print(f"[LinkedIn Script] DEBUG: raw_duration={raw_duration}, valid_durations={valid_durations}")
                
                if raw_duration not in valid_durations:
                    # Find nearest valid duration
                    original = raw_duration
                    final_duration = min(valid_durations, key=lambda x: abs(x - raw_duration))
                    print(f"[LinkedIn Script] WARNING CRITICAL: Clamped duration from {original}s to valid Sora value: {final_duration}s")
                else:
                    final_duration = raw_duration
                    print(f"[LinkedIn Script] DEBUG: Duration {final_duration}s is already valid")
                
                # Final safety check - MUST be valid for Sora
                if final_duration not in valid_durations:
                    print(f"[LinkedIn Script] WARNING CRITICAL ERROR: Duration {final_duration}s is still invalid! Forcing to 8s")
                    final_duration = 8  # Safe fallback
                
                # Triple-check: Force validation one more time
                final_duration = min(valid_durations, key=lambda x: abs(x - final_duration)) if final_duration not in valid_durations else final_duration
            
            print(f"[LinkedIn Script] Final decisions - Topic: {final_topic}, Duration: {final_duration}s ({'Veo 3' if is_veo3 else 'Sora 2'}), Audience: {final_audience}")
            
            # Add user context to script generation if available
            user_context_for_script = ""
            if user_context and len(user_context.strip()) > 0:
                user_context_for_script = f"""

USER CONTEXT & PREFERENCES:
{user_context}

PERSONALIZATION INSTRUCTIONS:
- Match the user's brand voice and content style preferences
- Reference successful topics that have worked for this user
- Align with their behavioral patterns (preferred duration, platform, etc.)
- Use their established messaging patterns and visual style preferences
- Ensure consistency with their brand identity and content themes
"""
            
            # Step 2: Generate advertising-quality script with deep research integration
            # Check if document_context contains web research (it should be appended)
            has_research = "COMPANY RESEARCH" in document_analysis or "COMPETITORS" in document_analysis or "ADVERTISING METHODS" in document_analysis
            
            research_emphasis = ""
            if has_research:
                research_emphasis = """
CRITICAL: The document analysis above includes comprehensive web research with:
- Company information and brand positioning
- Competitor analysis and market positioning
- Advertising methods and marketing strategies
- Industry insights and trends

YOU MUST USE THIS RESEARCH DATA:
- Reference specific company details, statistics, and insights from the research
- Incorporate competitor positioning and market differentiators
- Use advertising methods and marketing strategies discovered in research
- Leverage industry trends and data points for credibility
- Make the script feel informed by real market intelligence, not generic
- Use specific numbers, facts, and insights from the research to build authority
"""
            
            script_prompt = f"""You are a world-class advertising creative director creating a premium {final_duration}-second video script for professional marketing/advertising purposes.

This script must be ADVERTISING-QUALITY: compelling, persuasive, data-driven, and designed to drive action.

COMPREHENSIVE CONTEXT & RESEARCH:
{document_analysis}
{research_emphasis}
{user_context_for_script}

STRATEGIC BRIEF:
TOPIC: {final_topic}
DURATION: {final_duration} seconds (CRITICAL: Use EVERY SECOND - create dense, value-packed content)
AUDIENCE: {final_audience}
KEY MESSAGE: {final_message}
VIDEO MODEL: {'Veo 3 (supports 4-60 seconds - use full duration for quality)' if is_veo3 else 'Sora 2 (4, 8, or 12 seconds only)'}

ADVERTISING QUALITY STANDARDS:
- PREMIUM CONTENT: This is not a quick social post - it's professional advertising content
- DENSE VALUE: Every second must deliver value, insight, or emotional connection
- RESEARCH-BACKED: Use specific data, statistics, and insights from the research above
- COMPLETE NARRATIVE: Full story arc with proper development, not rushed or truncated
- MULTI-LAYERED: Hook → Problem → Insight → Solution → Proof → Transformation → CTA
- PROFESSIONAL DEPTH: Include multiple supporting points, examples, and evidence
- Use the FULL {final_duration} seconds - don't create a 12-second script for a 30-second video

ADVANCED MARKETING & ENGAGEMENT STRATEGY:

1. POWERFUL OPENING HOOK (First 2-3 seconds - CRITICAL):
   - Start with a counterintuitive insight, shocking statistic, or bold contrarian statement
   - Create immediate "pattern interrupt" - something unexpected that stops scrolling
   - Use specific numbers, percentages, or surprising facts from documents
   - Examples: "90% of companies fail at this...", "The #1 mistake I see...", "This changed everything..."
   - Must create cognitive dissonance or curiosity gap that demands resolution

2. VALUE-DENSE STRUCTURE (Inverted Pyramid):
   - Lead with the MOST valuable, actionable insight immediately
   - Front-load the "gold" - don't make viewers wait
   - Each sentence should deliver value or build toward value
   - Professional but conversational - like talking to a smart colleague
   - Use power words: "proven", "data-driven", "research shows", "case study reveals"

3. COMPELLING STORYTELLING ARCHITECTURE:
   - Problem/Challenge: Set up the pain point or opportunity (from documents)
   - Discovery/Insight: Reveal the key insight or solution (with specific details)
   - Transformation/Outcome: Show the impact or result (use data/examples from documents)
   - Use specific examples, case studies, or data points from the documents
   - Create emotional resonance through relatable professional scenarios
   - Build narrative momentum with clear cause-and-effect relationships

4. VISUAL STORYTELLING & CINEMATIC ELEMENTS:
   - Describe dynamic, professional visuals that amplify the message
   - Use visual metaphors that make abstract concepts tangible
   - Professional aesthetic: clean, modern, LinkedIn-appropriate
   - Suggest specific visual transitions that reinforce narrative flow
   - Include text overlays for key statistics or quotes
   - Visual rhythm that matches the script's pacing

5. PSYCHOLOGICAL ENGAGEMENT TRIGGERS:
   - Social proof: Reference specific statistics, studies, or examples from documents
   - Authority: Cite credible sources or data points when available
   - Scarcity/Urgency: Highlight timely insights or emerging trends
   - Relatability: Use "you" language and address viewer directly
   - Curiosity gaps: Pose questions that create "need to know" moments
   - Pattern breaks: Challenge conventional wisdom with contrarian insights

6. LINKEDIN OPTIMIZATION BEST PRACTICES:
   - Professional authenticity: Smart but not pretentious
   - Educational value: Teach something actionable
   - Personal connection: Share insights, not just information
   - Clear takeaways: Viewers should have specific actions or learnings
   - Silent-friendly: Works perfectly without sound (visual + text overlays)
   - Share-worthy: Creates "I need to share this" moments
   - Comment-worthy: Ends with question or insight that prompts discussion

7. MARKETING PSYCHOLOGY:
   - Use power phrases: "Here's what I learned...", "The data shows...", "Most people don't realize..."
   - Create "aha moments" that reframe understanding
   - Use contrast: "Most do X, but successful ones do Y"
   - Include specific, concrete details from documents (numbers, names, examples)
   - Build credibility through specificity and evidence

Create TWO comprehensive, advertising-quality outputs:

SCRIPT (for video narration/subtitles - {final_duration} seconds):
- Premium, professional advertising tone - authoritative but accessible
- Paced perfectly for {final_duration} seconds (approximately {final_duration * 2.5} to {final_duration * 3.5} words depending on pacing)
- CRITICAL: Use the FULL {final_duration} seconds - this is not a 12-second script
- Include ALL key insights from document analysis AND research - be comprehensive, not brief
- Structure for {final_duration}-second video:
  * Powerful Hook (3-5s): Pattern interrupt with research-backed statistic
  * Value Bomb (40-50% of duration): Core insights, data, and value delivery
  * Story/Evidence (20-30%): Specific examples, case studies, research findings
  * Differentiation (10-15%): How this differs from competitors (use research)
  * Actionable Takeaway (10-15%): Clear, specific next steps
  * Strong CTA (3-5s): Compelling call-to-action
- Every word should serve engagement, value delivery, or persuasion
- Use active voice, short sentences for impact, longer for explanation
- Include multiple supporting points, examples, data points, and research insights
- Build depth: layer insights, add nuance, provide context, reference research
- Don't rush - use the full {final_duration} seconds to deliver maximum value
- Include specific numbers, statistics, competitor insights, and concrete examples from research
- Create a complete narrative arc with proper pacing and development
- Reference company information, competitor positioning, and advertising methods from research
- Make it feel like premium advertising content, not generic social media

SORA PROMPT (for video generation - be EXTREMELY detailed, advertising-quality):
- Premium, cinematic visual description for professional advertising content
- Professional, high-production-value cinematography style
- Dynamic camera movements: smooth pans, zooms, tracking shots, professional dolly movements
- Visual elements that reinforce the message at each moment with research data visualization
- Include specific visual transitions that match script pacing and narrative flow
- Describe text overlays for key statistics, quotes, and data points from research
- Professional color palette and lighting: premium brand aesthetic
- Format: "Create a {final_duration}-second professional advertising video showing [detailed description]..."
- Be VERY specific about timing: "At 0-5 seconds show...", "At 10-15 seconds transition to...", "At 20-25 seconds reveal..."
- Include visual metaphors that make abstract concepts tangible
- Professional aesthetic: clean, modern, premium brand quality, high production value
- Data visualization: Show statistics, charts, comparisons, competitor analysis visually
- Visual storytelling that matches the research-backed narrative
- Professional text overlays for key insights, statistics, and differentiators
- Premium visual effects: smooth transitions, professional color grading, cinematic quality

ADVERTISING QUALITY ASSESSMENT:
Explain why this script will perform well as advertising content based on:
- Research integration: How research data is used to build authority
- Engagement hooks: Pattern interrupts and curiosity gaps
- Value delivery structure: Dense, comprehensive value throughout
- Professional audience alignment: How it speaks to the target audience
- Visual storytelling approach: How visuals amplify the message
- Differentiation: How competitor insights are used to highlight advantages
- Shareability factors: What makes this share-worthy
- Advertising psychology: Persuasion techniques used
- Brand positioning: How it aligns with brand voice and positioning"""
            
            script_response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a world-class advertising creative director and copywriter. You create premium, advertising-quality video scripts that:
- Use comprehensive research data (company info, competitors, market insights, advertising methods)
- Are data-driven and research-backed, not generic
- Deliver dense value and compelling narratives
- Use the FULL duration specified (don't create short scripts for long videos)
- Feel like professional advertising content, not casual social media
- Incorporate specific statistics, insights, and examples from research
- Reference competitor positioning and market differentiators
- Build authority through specificity and evidence
Your scripts drive action, build brand authority, and maximize engagement through strategic use of research insights."""
                    },
                    {
                        "role": "user",
                        "content": script_prompt
                    }
                ],
                temperature=0.85,  # Slightly higher for more creative, engaging content
                max_tokens=6000  # Significantly increased for much richer, longer, advertising-quality scripts
            )
            
            full_response = script_response.choices[0].message.content
            print(f"[LinkedIn Script] OK Script generated ({len(full_response)} chars)")
            
            # Parse the response to extract script, Sora prompt, and optimization notes
            # The AI is instructed to format it clearly, but we'll parse it intelligently
            script_parts = self._parse_linkedin_script_response(full_response, final_duration)
            
            return {
                "script": script_parts["script"],
                "sora_prompt": script_parts["sora_prompt"],
                "linkedin_optimization": script_parts["optimization_notes"],
                "key_insights": document_analysis[:500] + "..." if len(document_analysis) > 500 else document_analysis,
                "document_analysis": document_analysis,
                "ai_decisions": {
                    "topic": final_topic,
                    "duration": final_duration,
                    "audience": final_audience,
                    "key_message": final_message
                }
            }
            
        except Exception as e:
            print(f"[LinkedIn Script] Error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate LinkedIn-optimized script: {str(e)}")
    
    def _parse_linkedin_script_response(self, response_text: str, duration: int) -> Dict[str, str]:
        """Parse the AI response to extract script, Sora prompt, and optimization notes"""
        try:
            # Look for clear section markers
            script = ""
            sora_prompt = ""
            optimization_notes = ""
            
            # Try to find sections by keywords
            lines = response_text.split('\n')
            current_section = None
            
            for i, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Detect section headers
                if 'script' in line_lower and ('for video' in line_lower or 'narration' in line_lower):
                    current_section = 'script'
                    continue
                elif 'sora prompt' in line_lower or 'visual' in line_lower and 'description' in line_lower:
                    current_section = 'sora'
                    continue
                elif 'optimization' in line_lower or 'linkedin' in line_lower and 'performance' in line_lower:
                    current_section = 'optimization'
                    continue
                
                # Collect content based on current section
                if current_section == 'script':
                    script += line + '\n'
                elif current_section == 'sora':
                    sora_prompt += line + '\n'
                elif current_section == 'optimization':
                    optimization_notes += line + '\n'
            
            # Fallback: if sections not clearly marked, split intelligently
            if not script or not sora_prompt:
                # Look for common patterns
                if '---' in response_text:
                    parts = response_text.split('---')
                    script = parts[0].strip() if len(parts) > 0 else ""
                    sora_prompt = parts[1].strip() if len(parts) > 1 else ""
                    optimization_notes = parts[2].strip() if len(parts) > 2 else ""
                else:
                    # Split by approximate thirds
                    text_length = len(response_text)
                    script = response_text[:text_length//2].strip()
                    sora_prompt = response_text[text_length//2:text_length*3//4].strip()
                    optimization_notes = response_text[text_length*3//4:].strip()
            
            # Ensure Sora prompt starts properly
            if sora_prompt and not sora_prompt.lower().startswith('create'):
                sora_prompt = f"Create a {duration}-second professional LinkedIn video showing {sora_prompt.strip()}"
            
            # Clean up extra whitespace
            script = script.strip()
            sora_prompt = sora_prompt.strip() if sora_prompt else script[:4000]  # Fallback to script if no separate prompt
            optimization_notes = optimization_notes.strip() if optimization_notes else "Optimized for LinkedIn engagement with strong hooks and value-first structure."
            
            return {
                "script": script,
                "sora_prompt": sora_prompt,
                "optimization_notes": optimization_notes
            }
            
        except Exception as e:
            print(f"[LinkedIn Script] Error parsing response: {str(e)}")
            # Fallback: return the whole response as script
            # Use a valid Sora duration (8 seconds as default)
            fallback_duration = 8
            if duration and duration in [4, 8, 12]:
                fallback_duration = duration
            return {
                "script": response_text,
                "sora_prompt": f"Create a {fallback_duration}-second professional LinkedIn video: {response_text[:3000]}",
                "optimization_notes": "LinkedIn-optimized script with engagement hooks and professional value delivery.",
                "ai_decisions": {
                    "topic": "Professional Insights",
                    "duration": fallback_duration,
                    "audience": "LinkedIn professionals",
                    "key_message": "Derived from document insights"
                }
            }
