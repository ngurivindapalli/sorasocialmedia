"""
Script to check the duration of a Veo 3 video
"""
import requests
import tempfile
import os
import sys

def check_video_duration(job_id):
    """Download video and check its duration"""
    try:
        # Download video from API
        url = f"http://localhost:8000/api/veo3/download/{job_id}"
        print(f"Downloading video from: {url}")
        
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        print(f"✓ Download successful")
        print(f"  Status: {response.status_code}")
        print(f"  Content-Type: {response.headers.get('Content-Type')}")
        print(f"  Content-Length: {len(response.content):,} bytes")
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            temp_file.write(response.content)
            temp_path = temp_file.name
        
        print(f"  Saved to: {temp_path}")
        print(f"  File size: {os.path.getsize(temp_path):,} bytes")
        
        # Try to get duration using moviepy
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(temp_path)
            duration = clip.duration
            fps = clip.fps
            size = clip.size
            clip.close()
            
            print(f"\n✓ Video Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
            print(f"  FPS: {fps}")
            print(f"  Resolution: {size[0]}x{size[1]}")
            
            # Expected duration calculation
            expected_duration = 8 + (8 * 7)  # 8s initial + 8 extensions of 7s each
            print(f"\n  Expected duration (8s + 8×7s): {expected_duration}s")
            print(f"  Actual duration: {duration:.2f}s")
            print(f"  Difference: {abs(duration - expected_duration):.2f}s")
            
            # Cleanup
            os.unlink(temp_path)
            return duration
            
        except ImportError:
            print("\n⚠️ moviepy not installed. Install with: pip install moviepy")
            print("  Cannot determine video duration without moviepy")
            # Try ffprobe as fallback
            try:
                import subprocess
                import json
                result = subprocess.run(
                    ['ffprobe', '-v', 'quiet', '-print_format', 'json', '-show_format', temp_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    duration = float(data['format']['duration'])
                    print(f"\n✓ Video Duration (via ffprobe): {duration:.2f} seconds ({duration/60:.2f} minutes)")
                    os.unlink(temp_path)
                    return duration
            except:
                pass
            
            # Keep file for manual inspection
            print(f"\n  Video saved at: {temp_path}")
            print("  You can check duration manually or install moviepy/ffmpeg")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
    else:
        # Default job ID from user's message
        job_id = "projects/igvideogen/locations/us-central1/publishers/google/models/veo-3.1-generate-001/operations/5da3eab2-6eb9-4338-bece-b79509cb86f9"
    
    print("=" * 60)
    print("  Veo 3 Video Duration Checker")
    print("=" * 60)
    print(f"Job ID: {job_id[:80]}...")
    print("")
    
    duration = check_video_duration(job_id)
    
    if duration:
        print("\n" + "=" * 60)
        print("  Summary")
        print("=" * 60)
        print(f"Video Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        if duration >= 60:
            print("✓ Video is 60+ seconds - extensions appear to have worked!")
        elif duration >= 50:
            print("✓ Video is 50+ seconds - most extensions completed")
        elif duration >= 30:
            print("⚠ Video is 30+ seconds - some extensions may have completed")
        else:
            print("⚠ Video is less than 30 seconds - extensions may not have worked")





















