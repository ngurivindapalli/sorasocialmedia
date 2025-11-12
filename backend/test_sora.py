"""
Test Sora API access with your OpenAI key
"""
import asyncio
from openai import AsyncOpenAI
import os

# Read API key from .env
env_path = os.path.join(os.path.dirname(__file__), '.env')
OPENAI_API_KEY = None

try:
    with open(env_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line.startswith('OPENAI_API_KEY='):
                OPENAI_API_KEY = line.split('=', 1)[1].strip()
                break
except Exception as e:
    print(f"[ERROR] Failed to read .env: {e}")
    exit(1)

if not OPENAI_API_KEY:
    print("[ERROR] No API key found")
    exit(1)

print(f"[INFO] Using API key: {OPENAI_API_KEY[:20]}...")

async def test_sora():
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    # Check if videos attribute exists
    print(f"[TEST] Has 'videos' attribute: {hasattr(client, 'videos')}")
    
    if not hasattr(client, 'videos'):
        print("[ERROR] Videos API not available in SDK")
        print("[INFO] Please ensure openai>=2.7.0 is installed")
        return
    
    try:
        print("[TEST] Attempting to create a simple video...")
        video_job = await client.videos.create(
            model='sora-2',
            prompt="A simple test: the words 'Hello World' appear in sparkling letters",
            size='1280x720',
            seconds='8'  # Valid values: 4, 8, 12
        )
        
        print(f"[SUCCESS] Video job created!")
        print(f"  - Job ID: {video_job.id}")
        print(f"  - Status: {video_job.status}")
        print(f"  - Model: {video_job.model}")
        print(f"  - Progress: {getattr(video_job, 'progress', 0)}%")
        
        # Poll until complete (max 2 minutes)
        max_attempts = 24  # 2 minutes at 5 second intervals
        attempt = 0
        
        while video_job.status in ['queued', 'in_progress'] and attempt < max_attempts:
            attempt += 1
            await asyncio.sleep(5)
            video_job = await client.videos.retrieve(video_job.id)
            progress = getattr(video_job, 'progress', 0)
            print(f"  - [{attempt}] Status: {video_job.status}, Progress: {progress}%")
        
        if video_job.status == 'completed':
            print(f"[SUCCESS] Video generation completed!")
            print(f"  - Can download from: /api/sora/download/{video_job.id}")
        else:
            print(f"[INFO] Video status: {video_job.status}")
            
    except Exception as e:
        print(f"[ERROR] Sora API call failed: {str(e)}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        
        # Check if it's a 404 or permission issue
        if "404" in str(e):
            print("[INFO] Sora API might not be available for your account yet")
        elif "permission" in str(e).lower() or "access" in str(e).lower():
            print("[INFO] Your API key may not have Sora access enabled")
        else:
            print("[INFO] Unexpected error - check OpenAI API status")

if __name__ == "__main__":
    asyncio.run(test_sora())
