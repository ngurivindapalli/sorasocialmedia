from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from services.instagram_api import InstagramAPIService
from services.openai_service import OpenAIService
from models.schemas import VideoAnalysisRequest, VideoAnalysisResponse, ScrapedVideo, VideoResult

load_dotenv()

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required. Please set it in backend/.env file")

print(f"[DEBUG] Using API key: {OPENAI_API_KEY[:20]}...{OPENAI_API_KEY[-4:]}")

app = FastAPI(title="Instagram Video to Sora Script Generator")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
instagram_service = InstagramAPIService()
# Check for fine-tuned model in environment
fine_tuned_model = os.getenv("OPENAI_FINE_TUNED_MODEL")
openai_service = OpenAIService(api_key=OPENAI_API_KEY, fine_tuned_model=fine_tuned_model)


@app.get("/")
async def root():
    return {
        "message": "Instagram Video to Sora Script Generator with OpenAI Build Hours", 
        "status": "running",
        "build_hours_features": {
            "structured_outputs": "✓ Active - Validated Pydantic schemas for consistent Sora prompts",
            "vision_api": "✓ Active - GPT-4 Vision analyzes thumbnails for visual context",
            "batch_api": "✓ Available - Process multiple videos at 50% cost (24hr turnaround)",
            "fine_tuning": "Available via /api/finetune endpoints"
        },
        "model": openai_service.model
    }


@app.post("/api/analyze", response_model=VideoAnalysisResponse)
async def analyze_videos(request: VideoAnalysisRequest):
    """
    Scrape videos from Instagram, transcribe them, and generate Sora scripts with OpenAI Build Hours features.
    """
    try:
        # Step 1: Scrape videos from Instagram
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
        
        # Step 2: Process each video with Build Hours features
        analyzed_results = []
        
        for video in videos:
            try:
                print(f"[API] Processing video: {video['id']}")
                
                # Download video
                video_path = await instagram_service.download_video(video['video_url'], video['id'])
                
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
                
                # Generate regular Sora script (always works as fallback)
                print(f"[API] Generating Sora script...")
                sora_script = await openai_service.generate_sora_script(
                    transcription=transcription,
                    video_metadata={
                        'views': video['views'],
                        'likes': video['likes'],
                        'text': video['text']
                    }
                )
                
                # BUILD HOURS FEATURE: Structured Outputs - Generate validated structured script
                structured_sora = None
                try:
                    print(f"[API] 📐 Generating structured Sora script (Build Hours: Structured Outputs)...")
                    structured_sora = await openai_service.generate_structured_sora_script(
                        transcription=transcription,
                        video_metadata={
                            'views': video['views'],
                            'likes': video['likes'],
                            'text': video['text'],
                            'duration': video.get('duration', 0)
                        },
                        thumbnail_analysis=thumbnail_analysis  # Include Vision API data
                    )
                    print(f"[API] ✓ Structured output generated successfully")
                except Exception as struct_error:
                    print(f"[API] Structured output failed (non-critical): {struct_error}")
                    import traceback
                    traceback.print_exc()
                
                analyzed_results.append(VideoResult(
                    video_id=video['id'],
                    post_url=video['post_url'],
                    views=video['views'],
                    likes=video['likes'],
                    original_text=video['text'],
                    transcription=transcription,
                    sora_script=sora_script,
                    structured_sora_script=structured_sora,  # Build Hours: Structured Outputs
                    thumbnail_analysis=thumbnail_analysis  # Build Hours: Vision API
                ))
                
                print(f"[API] Successfully processed video: {video['id']}")
                
                # Cleanup
                if os.path.exists(video_path):
                    os.remove(video_path)
                    
            except Exception as video_error:
                print(f"[API] Error processing video {video['id']}: {video_error}")
                import traceback
                traceback.print_exc()
                continue
        
        return VideoAnalysisResponse(
            username=request.username,
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
        
        # Step 1: Scrape videos from each user
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
        
        # Step 2: Process each video
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
                
                # Generate regular Sora script
                sora_script = await openai_service.generate_sora_script(
                    transcription=transcription,
                    video_metadata={
                        "views": video['views'],
                        "likes": video['likes'],
                        "original_text": video['text'],
                        "username": video['source_username']
                    }
                )
                
                # Try structured output
                structured_script = None
                try:
                    structured_script = await openai_service.generate_structured_sora_script(
                        transcription=transcription,
                        video_metadata={
                            "views": video['views'],
                            "likes": video['likes'],
                            "original_text": video['text'],
                            "username": video['source_username']
                        },
                        thumbnail_analysis=thumbnail_analysis
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
        
        combined_script = await openai_service.create_combined_script(
            results=all_results,
            usernames=multi_request.usernames,
            combine_style=multi_request.combine_style
        )
        
        # Try to generate structured combined script
        combined_structured = None
        try:
            combined_structured = await openai_service.create_combined_structured_script(
                results=all_results,
                usernames=multi_request.usernames,
                combine_style=multi_request.combine_style
            )
        except Exception as e:
            print(f"[API] Combined structured output skipped: {e}")
        
        return CombinedVideoResult(
            usernames=multi_request.usernames,
            total_videos_analyzed=len(all_results),
            individual_results=all_results,
            combined_sora_script=combined_script,
            combined_structured_script=combined_structured,
            fusion_notes=f"Combined {len(all_results)} top-performing videos using {multi_request.combine_style} style"
        )
        
    except Exception as e:
        print(f"[API] Multi-user analysis error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "x_api": "configured" if os.getenv("X_BEARER_TOKEN") else "missing",
        "openai_api": "configured" if OPENAI_API_KEY else "missing",
        "fine_tuned_model": os.getenv("OPENAI_FINE_TUNED_MODEL") or "not configured"
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
