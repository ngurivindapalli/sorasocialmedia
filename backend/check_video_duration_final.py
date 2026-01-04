"""
Check video duration using moviepy
"""
import os
import tempfile
from google.cloud import storage
from pathlib import Path
from moviepy.editor import VideoFileClip

# Load .env
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ[key] = value

project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'igvideogen')
bucket_name = f"{project_id}-veo3-videos"

print("=" * 60)
print("  Veo 3 Video Duration Check")
print("=" * 60)

try:
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    
    # Find the most recent video
    blobs = list(bucket.list_blobs(prefix="videos/", max_results=5))
    if not blobs:
        print("No videos found")
    else:
        latest_blob = max(blobs, key=lambda b: b.time_created)
        print(f"Video: {latest_blob.name}")
        print(f"Size: {latest_blob.size:,} bytes ({latest_blob.size / 1024 / 1024:.2f} MB)")
        print("")
        
        # Download and check duration
        print("Downloading video...")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            latest_blob.download_to_filename(temp_file.name)
            temp_path = temp_file.name
        
        print("Analyzing video...")
        clip = VideoFileClip(temp_path)
        duration = clip.duration
        fps = clip.fps
        size = clip.size
        clip.close()
        
        # Cleanup
        os.unlink(temp_path)
        
        print("")
        print("=" * 60)
        print("  Results")
        print("=" * 60)
        print(f"Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"FPS: {fps}")
        print(f"Resolution: {size[0]}x{size[1]}")
        print("")
        
        # Expected duration
        expected_duration = 8 + (8 * 7)  # 8s initial + 8 extensions of 7s each
        print(f"Expected duration (8s + 8×7s): {expected_duration}s")
        print(f"Actual duration: {duration:.2f}s")
        print(f"Difference: {abs(duration - expected_duration):.2f}s")
        print("")
        
        if abs(duration - expected_duration) < 5:
            print("✓✓✓ PERFECT! Video duration matches expected (all extensions completed)! ✓✓✓")
        elif duration >= 60:
            print("✓✓ Video is 60+ seconds - extensions appear to have worked!")
        elif duration >= 50:
            print("✓ Video is 50+ seconds - most extensions completed")
        elif duration >= 30:
            print("⚠ Video is 30+ seconds - some extensions may have completed")
        elif duration >= 8:
            print("⚠ Video is 8-30 seconds - only initial generation, extensions may not have worked")
        else:
            print("⚠ Video is less than 8 seconds - something went wrong")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()






















