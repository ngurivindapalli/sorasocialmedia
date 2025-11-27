"""
Test Veo 3 Video Generation Directly
This script tests Veo 3 without needing Instagram scraping
"""

import requests
import time
import json

API_URL = "http://localhost:8000"

def test_veo3_generation():
    """Test Veo 3 video generation with a simple prompt"""
    
    print("🎬 Testing Veo 3 Video Generation")
    print("=" * 50)
    
    # Test prompt
    prompt = "A beautiful sunset over the ocean with waves gently crashing on the shore, cinematic quality, 4K resolution"
    
    print(f"\n📝 Prompt: {prompt}")
    print(f"⏱️  Duration: 8 seconds")
    print(f"📐 Resolution: 1280x720")
    print("\n📤 Sending request to Veo 3 API...")
    
    try:
        # Step 1: Generate video
        response = requests.post(
            f"{API_URL}/api/veo3/generate",
            json={
                "prompt": prompt,
                "duration": 8,
                "resolution": "1280x720"
            },
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        job_id = data.get('job_id') or data.get('operation_name')
        
        print(f"✅ Video generation started!")
        print(f"🆔 Job ID: {job_id}")
        print(f"📊 Status: {data.get('status', 'unknown')}")
        print(f"\n⏳ Polling for completion...")
        
        # Step 2: Poll for status
        max_attempts = 60  # 5 minutes max (60 * 5 seconds)
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            time.sleep(5)  # Wait 5 seconds between checks
            
            status_response = requests.get(f"{API_URL}/api/veo3/status/{job_id}")
            
            if status_response.status_code != 200:
                print(f"❌ Status check failed: {status_response.status_code}")
                print(f"Response: {status_response.text}")
                break
            
            status_data = status_response.json()
            status = status_data.get('status', 'unknown')
            progress = status_data.get('progress', 0)
            done = status_data.get('done', False)
            
            print(f"  [{attempt}] Status: {status}, Progress: {progress}%", end='\r')
            
            if done or status == 'completed':
                print(f"\n✅ Video generation completed!")
                
                video_urls = status_data.get('video_urls', [])
                if video_urls:
                    print(f"📹 Video URL(s): {video_urls[0]}")
                    
                    # Step 3: Download video
                    print(f"\n📥 Downloading video...")
                    download_response = requests.get(f"{API_URL}/api/veo3/download/{job_id}")
                    
                    if download_response.status_code == 200:
                        filename = f"veo3_test_{int(time.time())}.mp4"
                        with open(filename, 'wb') as f:
                            f.write(download_response.content)
                        print(f"✅ Video saved as: {filename}")
                        print(f"📊 Size: {len(download_response.content) / 1024 / 1024:.2f} MB")
                        return filename
                    else:
                        print(f"❌ Download failed: {download_response.status_code}")
                        print(f"Response: {download_response.text}")
                else:
                    print(f"⚠️ No video URLs in response")
                    print(f"Full response: {json.dumps(status_data, indent=2)}")
                
                break
            
            if status == 'failed' or status == 'error':
                error = status_data.get('error', 'Unknown error')
                print(f"\n❌ Video generation failed: {error}")
                break
        
        if attempt >= max_attempts:
            print(f"\n⏰ Timeout: Video generation took longer than expected")
            print(f"   Check status manually: GET {API_URL}/api/veo3/status/{job_id}")
        
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection Error: Make sure the backend server is running on {API_URL}")
        print(f"   Start it with: cd backend && python main.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n" + "=" * 50)
    print("Veo 3 Direct Test Script")
    print("=" * 50)
    print("\nThis script tests Veo 3 video generation directly")
    print("without needing Instagram scraping.\n")
    
    test_veo3_generation()
    
    print("\n" + "=" * 50)
    print("Test Complete!")
    print("=" * 50)

