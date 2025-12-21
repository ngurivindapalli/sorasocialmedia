"""
Smart Video Composition Service
Intelligently combines generated images into Veo 3 videos
Uses AI to determine optimal image placement, transitions, and narrative flow
"""

import os
from typing import Dict, List, Optional
from openai import AsyncOpenAI


class VideoCompositionService:
    """Service for intelligently composing videos with images"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_client = None
        
        if self.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.openai_api_key)
            print("[VideoComposition] OK Service initialized")
        else:
            print("[VideoComposition] WARNING OpenAI API key not set. Smart composition features limited.")
    
    async def create_smart_video_script(
        self,
        video_prompt: str,
        image_urls: List[str],
        image_descriptions: Optional[List[str]] = None,
        target_duration: int = 8,
        style: str = "informative"
    ) -> Dict:
        """
        Create a smart video script that incorporates images into a Veo 3 video
        
        Args:
            video_prompt: Base video description
            image_urls: List of image URLs to incorporate
            image_descriptions: Optional descriptions of each image
            target_duration: Target video duration in seconds
            style: Composition style ("informative", "cinematic", "educational", "narrative")
            
        Returns:
            Dict with enhanced_prompt, image_timing, and composition_notes
        """
        if not self.openai_client:
            # Fallback: simple concatenation
            return self._create_simple_script(video_prompt, image_urls, target_duration)
        
        print(f"[VideoComposition] Creating smart video script with {len(image_urls)} images")
        print(f"[VideoComposition] Style: {style}, Duration: {target_duration}s")
        
        try:
            # Build context about images
            image_context = ""
            if image_descriptions:
                for i, (url, desc) in enumerate(zip(image_urls, image_descriptions)):
                    image_context += f"\nImage {i+1}: {desc}\nURL: {url}\n"
            else:
                for i, url in enumerate(image_urls):
                    image_context += f"\nImage {i+1}: {url}\n"
            
            # Create intelligent composition prompt
            composition_prompt = f"""You are an expert video director creating a {target_duration}-second video that intelligently incorporates {len(image_urls)} generated images into a cohesive, informative narrative.

BASE VIDEO PROMPT:
{video_prompt}

IMAGES TO INCORPORATE:
{image_context}

STYLE: {style}

Create a detailed video script that:
1. Seamlessly weaves the images into the video narrative
2. Uses smooth transitions between live video and image displays
3. Maintains visual coherence and storytelling flow
4. Optimizes timing: each image should appear at the right moment ({target_duration}s total)
5. Creates an informative, engaging experience

Return a JSON object with:
- "enhanced_prompt": A detailed Veo 3 prompt that describes the full video including image integration
- "image_timing": Array of objects with "image_index", "start_time", "duration", "transition_type"
- "composition_notes": Explanation of the creative choices
- "narrative_structure": How the images support the story

Make it smart, informative, and visually compelling."""

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert video director specializing in creating informative, visually compelling videos that seamlessly integrate static images with dynamic video content."
                    },
                    {
                        "role": "user",
                        "content": composition_prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "video_composition",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "enhanced_prompt": {
                                    "type": "string",
                                    "description": "Complete Veo 3 prompt describing the video with image integration"
                                },
                                "image_timing": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "image_index": {"type": "integer"},
                                            "start_time": {"type": "number"},
                                            "duration": {"type": "number"},
                                            "transition_type": {"type": "string"}
                                        }
                                    }
                                },
                                "composition_notes": {"type": "string"},
                                "narrative_structure": {"type": "string"}
                            },
                            "required": ["enhanced_prompt", "image_timing", "composition_notes"]
                        }
                    }
                },
                temperature=0.7
            )
            
            import json
            composition_data = json.loads(response.choices[0].message.content)
            
            # Add image URLs to timing data
            for timing in composition_data.get("image_timing", []):
                img_idx = timing.get("image_index", 0)
                if 0 <= img_idx < len(image_urls):
                    timing["image_url"] = image_urls[img_idx]
            
            return {
                "enhanced_prompt": composition_data["enhanced_prompt"],
                "image_timing": composition_data["image_timing"],
                "composition_notes": composition_data.get("composition_notes", ""),
                "narrative_structure": composition_data.get("narrative_structure", ""),
                "base_prompt": video_prompt,
                "image_count": len(image_urls)
            }
            
        except Exception as e:
            print(f"[VideoComposition] Smart composition error: {e}")
            # Fallback to simple script
            return self._create_simple_script(video_prompt, image_urls, target_duration)
    
    def _create_simple_script(
        self,
        video_prompt: str,
        image_urls: List[str],
        target_duration: int
    ) -> Dict:
        """Fallback: Create a simple script without AI enhancement"""
        duration_per_image = target_duration / max(len(image_urls), 1)
        
        image_timing = []
        for i, url in enumerate(image_urls):
            image_timing.append({
                "image_index": i,
                "image_url": url,
                "start_time": i * duration_per_image,
                "duration": duration_per_image,
                "transition_type": "fade"
            })
        
        enhanced_prompt = f"{video_prompt}. The video incorporates {len(image_urls)} key images that appear throughout, creating an informative visual narrative."
        
        return {
            "enhanced_prompt": enhanced_prompt,
            "image_timing": image_timing,
            "composition_notes": "Simple sequential image placement (AI enhancement unavailable)",
            "base_prompt": video_prompt,
            "image_count": len(image_urls)
        }
    
    async def generate_informative_video(
        self,
        topic: str,
        image_prompts: List[str],
        target_duration: int = 8,
        style: str = "informative"
    ) -> Dict:
        """
        Complete workflow: Generate images, then create smart video script
        
        Args:
            topic: Main topic/subject of the video
            image_prompts: List of prompts for generating supporting images
            target_duration: Target video duration
            style: Composition style
            
        Returns:
            Dict with image_urls, video_script, and composition_data
        """
        from services.image_generation_service import ImageGenerationService
        
        image_service = ImageGenerationService()
        
        # Generate all images (prefer Nano Banana for superior quality)
        print(f"[VideoComposition] Generating {len(image_prompts)} images for video...")
        image_results = await image_service.generate_multiple_images(
            image_prompts,
            model="nanobanana",  # Superior text rendering and photorealism
            size="1024x1024",
            quality="medium"
        )
        
        image_urls = [r.get("image_url") for r in image_results if r.get("image_url")]
        image_descriptions = [r.get("revised_prompt", prompt) for r, prompt in zip(image_results, image_prompts) if r.get("image_url")]
        
        if not image_urls:
            raise Exception("Failed to generate any images")
        
        # Create smart video script
        base_video_prompt = f"Create an informative {target_duration}-second video about {topic}"
        composition_data = await self.create_smart_video_script(
            video_prompt=base_video_prompt,
            image_urls=image_urls,
            image_descriptions=image_descriptions,
            target_duration=target_duration,
            style=style
        )
        
        return {
            "topic": topic,
            "image_urls": image_urls,
            "image_descriptions": image_descriptions,
            "video_script": composition_data["enhanced_prompt"],
            "composition_data": composition_data,
            "generated_images": image_results
        }

