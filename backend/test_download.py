"""
Test downloading the actual Sora video we created earlier
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

async def test_download():
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    
    # Use the video ID from our earlier successful test
    job_id = "video_691287461c6c81919f385e8d953587ee0930648ef607f515"
    
    print(f"[TEST] Checking status of video: {job_id}")
    
    try:
        # Check status first
        video = await client.videos.retrieve(job_id)
        print(f"  - Status: {video.status}")
        
        if video.status != 'completed':
            print(f"[ERROR] Video not completed yet: {video.status}")
            return
        
        print(f"[TEST] Downloading video content...")
        
        # Try downloading
        content = await client.videos.download_content(job_id)
        
        print(f"[INFO] Content type: {type(content)}")
        print(f"[INFO] Content attributes: {dir(content)}")
        
        # Try different ways to get bytes
        if hasattr(content, 'read'):
            print("[TEST] Using content.read()")
            video_bytes = await content.read()
        elif hasattr(content, 'content'):
            print("[TEST] Using content.content")
            video_bytes = content.content
        elif hasattr(content, 'aread'):
            print("[TEST] Using content.aread()")
            video_bytes = await content.aread()
        else:
            print("[TEST] Content is already bytes")
            video_bytes = content
        
        print(f"[SUCCESS] Downloaded {len(video_bytes):,} bytes")
        
        # Try saving to file
        with open('test_download.mp4', 'wb') as f:
            f.write(video_bytes)
        
        print(f"[SUCCESS] Saved to test_download.mp4")
        
    except Exception as e:
        print(f"[ERROR] {str(e)}")
        print(f"[ERROR] Type: {type(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_download())
