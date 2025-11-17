import os
import requests
import time

API_URL = "http://localhost:8000"

def generate_background_video():
    """Generate a loopable background video for the landing page"""
    
    prompt = """Abstract digital particles flowing through a dark space, creating smooth waves of light. 
Deep blacks and subtle blue-purple gradients. Minimal, clean, professional aesthetic. 
Slow, continuous motion that loops seamlessly. No text, no objects, just pure ambient motion graphics. 
Cinematic quality, ultra-smooth movement, suitable for website background."""
    
    print("🎬 Generating background video with Sora...")
    print(f"📝 Prompt: {prompt}\n")
    
    try:
        # Create Sora video generation via your backend
        print("📤 Sending request to backend...")
        response = requests.post(f"{API_URL}/api/sora/generate", json={
            "prompt": prompt,
            "duration": 10,  # 10 seconds for seamless loop
            "size": "1280x720"  # 16:9 aspect ratio
        })
        
        if response.status_code != 200:
            print(f"❌ Error: {response.text}")
            return None
            
        data = response.json()
        video_job_id = data.get('job_id')
        
        print(f"✅ Video generation started!")
        print(f"🆔 Job ID: {video_job_id}")
        print(f"\n⏳ Checking status...")
        
        # Poll for completion
        while True:
            status_response = requests.get(f"{API_URL}/api/sora/status/{video_job_id}")
            status_data = status_response.json()
            
            status = status_data.get('status')
            progress = status_data.get('progress', 0)
            
            print(f"📊 Status: {status} ({progress}%)")
            
            if status == "completed":
                print(f"\n🎉 Video generated successfully!")
                print(f"\n💾 Downloading video...")
                
                # Download the video
                video_response = requests.get(f"{API_URL}/api/sora/download/{video_job_id}")
                
                if video_response.status_code != 200:
                    print(f"❌ Download failed: {video_response.text}")
                    return None
                
                output_path = "frontend/public/bg-video.mp4"
                with open(output_path, 'wb') as f:
                    f.write(video_response.content)
                
                print(f"✅ Video saved to: {output_path}")
                print(f"📦 File size: {len(video_response.content) / 1024 / 1024:.2f} MB")
                print(f"\n🎬 You can now use this video in your landing page!")
                return output_path
                
            elif status == "failed":
                error_msg = status_data.get('error', 'Unknown error')
                print(f"❌ Video generation failed: {error_msg}")
                return None
            
            time.sleep(5)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

if __name__ == "__main__":
    generate_background_video()
