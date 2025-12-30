"""
Helper utilities for Veo video generation with Mem0 context integration
"""
import asyncio
import time
from typing import Dict, Optional
from services.veo3_service import Veo3Service


async def wait_for_video_completion_with_extensions(
    veo3_service: Veo3Service,
    job_id: str,
    max_extensions: int = 0,
    check_interval: int = 10,
    max_wait_time: int = 1800,  # 30 minutes max
    initial_duration: int = 8
) -> Dict:
    """
    Wait for a Veo video to complete, including all extensions.
    
    Args:
        veo3_service: Veo3Service instance
        job_id: Initial job ID
        max_extensions: Maximum number of extensions to wait for (0 = no extensions)
        check_interval: Seconds between status checks
        max_wait_time: Maximum total wait time in seconds
        initial_duration: Initial video duration in seconds (default 8)
        
    Returns:
        Dict with final video status and video_url
    """
    start_time = time.time()
    current_job_id = job_id
    extensions_completed = 0
    
    # Initialize extension cache if needed
    if not hasattr(veo3_service, '_extension_cache'):
        veo3_service._extension_cache = {}
    
    # Store extension metadata
    extension_metadata = {
        'base_job_id': job_id,
        'needs_extension': max_extensions > 0,
        'extension_count': max_extensions,
        'extensions_completed': 0,
        'current_duration': initial_duration,
        'last_extension_job_id': None,
        'extension_attempted': False,
        'extension_failed': False
    }
    veo3_service._extension_cache[job_id] = extension_metadata
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > max_wait_time:
            raise Exception(f"Video generation timed out after {max_wait_time} seconds")
        
        # Check status of current job
        print(f"[VeoHelper] Checking status of job: {current_job_id[:50]}...")
        status = await veo3_service.get_video_status(current_job_id)
        status_value = status.get("status")
        
        if status_value == "failed":
            error_msg = status.get("error", "Unknown error")
            raise Exception(f"Video generation failed: {error_msg}")
        
        if status_value == "completed":
            print(f"[VeoHelper] ✅ Video completed! ({current_job_id[:50]}...)")
            
            # Check if we need to extend
            if extensions_completed < max_extensions:
                print(f"[VeoHelper] Extending video ({extensions_completed + 1}/{max_extensions})...")
                
                try:
                    # Get the base video status and download the video bytes
                    base_status = await veo3_service.get_video_status(current_job_id)
                    base_video_url = base_status.get("video_url")
                    
                    if not base_video_url:
                        raise Exception("Base video URL not available yet")
                    
                    print(f"[VeoHelper] Base video URL: {base_video_url}")
                    print(f"[VeoHelper] Downloading base video bytes for extension...")
                    
                    # Download the video bytes using the service method
                    base_video_bytes = await veo3_service.get_video_bytes(current_job_id, base_status)
                    print(f"[VeoHelper] Downloaded base video ({len(base_video_bytes)} bytes)")
                    
                    # Save to temporary file for extend_video method
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                        temp_file.write(base_video_bytes)
                        temp_video_path = temp_file.name
                    
                    try:
                        # Use Vertex AI API to extend (the extend_video method uses Vertex AI API directly)
                        extension_result = await veo3_service.extend_video(
                            video_url=temp_video_path,  # Use temp file path
                            extension_seconds=7,
                            max_extensions=1
                        )
                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(temp_video_path)
                        except:
                            pass
                    
                    extensions_completed += 1
                    current_job_id = extension_result.get("job_id")
                    
                    # Update metadata
                    extension_metadata['extensions_completed'] = extensions_completed
                    extension_metadata['current_duration'] = initial_duration + (extensions_completed * 7)
                    extension_metadata['last_extension_job_id'] = current_job_id
                    extension_metadata['extension_attempted'] = True
                    extension_metadata['extension_failed'] = False
                    veo3_service._extension_cache[current_job_id] = extension_metadata
                    veo3_service._extension_cache[job_id] = extension_metadata
                    
                    print(f"[VeoHelper] ✅ Extension {extensions_completed} started: {current_job_id[:50]}...")
                    # Continue loop to wait for this extension
                    await asyncio.sleep(check_interval)
                    continue
                    
                except Exception as ext_error:
                    print(f"[VeoHelper] ⚠️ Extension failed: {ext_error}")
                    extension_metadata['extension_failed'] = True
                    extension_metadata['extension_error'] = str(ext_error)
                    # Return current completed video (without this extension)
                    break
            else:
                # All done!
                print(f"[VeoHelper] ✅ All extensions completed! Final duration: ~{initial_duration + (extensions_completed * 7)}s")
                break
        
        # Still in progress
        progress = status.get("progress", 0)
        print(f"[VeoHelper] ⏳ Video in progress... ({progress}%) - elapsed: {int(elapsed)}s")
        await asyncio.sleep(check_interval)
    
    # Get final status
    final_status = await veo3_service.get_video_status(current_job_id)
    return {
        "job_id": current_job_id,
        "status": final_status.get("status"),
        "video_url": final_status.get("video_url"),
        "extensions_completed": extensions_completed,
        "final_duration": initial_duration + (extensions_completed * 7)
    }
