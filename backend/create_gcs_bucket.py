"""
Script to create a Google Cloud Storage bucket for Veo 3 videos
"""
import os
import sys
from pathlib import Path

# Load .env file
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(env_path)
    except ImportError:
        # Manual .env parsing if dotenv not available
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

def create_bucket():
    """Create the GCS bucket for Veo 3 videos"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT_ID', '')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not set in environment")
        return False
    
    bucket_name = f"{project_id}-veo3-videos"
    
    try:
        from google.cloud import storage
        print(f"✓ google-cloud-storage library available")
    except ImportError:
        print("❌ google-cloud-storage library not installed")
        print("   Install it with: pip install google-cloud-storage")
        print("\n   OR create the bucket manually:")
        print(f"   1. Go to: https://console.cloud.google.com/storage/create-bucket?project={project_id}")
        print(f"   2. Bucket name: {bucket_name}")
        print(f"   3. Location: us-central1 (or your preferred region)")
        return False
    
    try:
        # Initialize the storage client
        client = storage.Client(project=project_id)
        
        # Check if bucket already exists
        try:
            bucket = client.bucket(bucket_name)
            if bucket.exists():
                print(f"✓ Bucket '{bucket_name}' already exists!")
                return True
        except Exception:
            pass
        
        # Create the bucket
        print(f"Creating bucket: {bucket_name}...")
        bucket = client.create_bucket(bucket_name, location='us-central1')
        print(f"✓ Bucket '{bucket_name}' created successfully!")
        print(f"   Location: {bucket.location}")
        print(f"   Storage URI: gs://{bucket_name}/videos/")
        return True
        
    except Exception as e:
        print(f"❌ Error creating bucket: {e}")
        print("\n   You can create it manually:")
        print(f"   1. Go to: https://console.cloud.google.com/storage/create-bucket?project={project_id}")
        print(f"   2. Bucket name: {bucket_name}")
        print(f"   3. Location: us-central1 (or your preferred region)")
        return False

if __name__ == "__main__":
    success = create_bucket()
    sys.exit(0 if success else 1)

