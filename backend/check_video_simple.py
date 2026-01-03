"""
Simple video duration check using file size estimation
"""
import os
from google.cloud import storage
from pathlib import Path

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
print("  Veo 3 Video Analysis")
print("=" * 60)
print(f"Project: {project_id}")
print(f"Bucket: {bucket_name}")
print("")

try:
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)
    
    # List recent videos
    print("Finding recent videos in bucket...")
    blobs = list(bucket.list_blobs(prefix="videos/", max_results=5))
    
    if not blobs:
        print("No videos found in bucket")
    else:
        print(f"\nFound {len(blobs)} video(s):\n")
        
        for i, blob in enumerate(sorted(blobs, key=lambda b: b.time_created, reverse=True)[:3], 1):
            print(f"{i}. {blob.name}")
            print(f"   Created: {blob.time_created}")
            print(f"   Size: {blob.size:,} bytes ({blob.size / 1024 / 1024:.2f} MB)")
            
            # Estimate duration based on file size
            # Typical bitrate for 720p video: ~2-5 Mbps
            # For 1280x720 at 30fps, roughly 2-3 MB per second
            # More accurate: ~2.5 MB per second for good quality
            estimated_duration = blob.size / (2.5 * 1024 * 1024)  # 2.5 MB per second
            
            print(f"   Estimated duration: ~{estimated_duration:.1f} seconds ({estimated_duration/60:.1f} minutes)")
            
            # Expected duration calculation
            expected_duration = 8 + (8 * 7)  # 8s initial + 8 extensions of 7s each = 64s
            print(f"   Expected duration (8s + 8×7s): {expected_duration}s")
            
            if abs(estimated_duration - expected_duration) < 10:
                print(f"   ✓ Duration matches expected range!")
            elif estimated_duration >= 50:
                print(f"   ✓ Video appears to be extended (50+ seconds)")
            elif estimated_duration >= 30:
                print(f"   ⚠ Video may be partially extended (30-50 seconds)")
            else:
                print(f"   ⚠ Video appears to be initial generation only (<30 seconds)")
            
            print("")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()





















