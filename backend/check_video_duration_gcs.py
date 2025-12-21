"""
Check video duration directly from GCS
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

def check_video_from_gcs(gcs_uri):
    """Check video duration from GCS URI"""
    try:
        import tempfile
        try:
            from moviepy.editor import VideoFileClip
        except ImportError as e:
            print(f"moviepy import error: {e}")
            raise ImportError("moviepy not installed")
        
        # Parse GCS URI
        if not gcs_uri.startswith("gs://"):
            print(f"Invalid GCS URI: {gcs_uri}")
            return None
        
        path_parts = gcs_uri[5:].split("/", 1)
        bucket_name = path_parts[0]
        blob_path = path_parts[1] if len(path_parts) > 1 else ""
        
        print(f"Downloading from GCS: {bucket_name}/{blob_path}")
        
        # Download from GCS
        client = storage.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT_ID'))
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        
        # Download to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
            blob.download_to_filename(temp_file.name)
            temp_path = temp_file.name
        
        print(f"✓ Downloaded to: {temp_path}")
        print(f"  File size: {os.path.getsize(temp_path):,} bytes")
        
        # Get duration
        clip = VideoFileClip(temp_path)
        duration = clip.duration
        fps = clip.fps
        size = clip.size
        clip.close()
        
        print(f"\n✓ Video Duration: {duration:.2f} seconds ({duration/60:.2f} minutes)")
        print(f"  FPS: {fps}")
        print(f"  Resolution: {size[0]}x{size[1]}")
        
        # Expected duration
        expected_duration = 8 + (8 * 7)  # 8s initial + 8 extensions of 7s each
        print(f"\n  Expected duration (8s + 8×7s): {expected_duration}s")
        print(f"  Actual duration: {duration:.2f}s")
        print(f"  Difference: {abs(duration - expected_duration):.2f}s")
        
        # Cleanup
        os.unlink(temp_path)
        return duration
        
    except ImportError:
        print("moviepy not installed. Install with: pip install moviepy")
        return None
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Based on the logs, the video should be at:
    # gs://igvideogen-veo3-videos/videos/{operation_id}/sample_0.mp4
    # But we need to find the actual path. Let me list the bucket to find recent videos.
    
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', 'igvideogen')
    bucket_name = f"{project_id}-veo3-videos"
    
    print("=" * 60)
    print("  Veo 3 Video Duration Checker (GCS)")
    print("=" * 60)
    print(f"Project: {project_id}")
    print(f"Bucket: {bucket_name}")
    print("")
    
    try:
        client = storage.Client(project=project_id)
        bucket = client.bucket(bucket_name)
        
        # List recent videos
        print("Finding recent videos in bucket...")
        blobs = list(bucket.list_blobs(prefix="videos/", max_results=10))
        
        if not blobs:
            print("No videos found in bucket")
        else:
            # Get the most recent video
            latest_blob = max(blobs, key=lambda b: b.time_created)
            gcs_uri = f"gs://{bucket_name}/{latest_blob.name}"
            
            print(f"Most recent video: {latest_blob.name}")
            print(f"Created: {latest_blob.time_created}")
            print(f"Size: {latest_blob.size:,} bytes")
            print("")
            
            duration = check_video_from_gcs(gcs_uri)
            
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
                    
    except Exception as e:
        print(f"Error accessing GCS: {e}")
        import traceback
        traceback.print_exc()

