import os
import requests
import json
import base64
import time
from pathlib import Path

API_URL = "http://localhost:8000"

# Sample topics for generating posts
SAMPLE_TOPICS = [
    'AI-powered productivity tools',
    'Sustainable fashion trends',
    'Tech startup innovation',
    'Digital marketing strategies',
    'Remote work culture',
    'E-commerce growth',
    'Social media engagement',
    'Content creation tips',
    'Business automation',
    'Creative design inspiration'
]

def wait_for_backend(max_retries=30, delay=2):
    """Wait for backend to be available"""
    print("⏳ Waiting for backend server to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_URL}/api/health", timeout=2)
            if response.status_code == 200:
                print("✅ Backend server is ready!\n")
                return True
        except:
            pass
        if i < max_retries - 1:
            print(f"   Attempt {i + 1}/{max_retries}...")
            time.sleep(delay)
    print("❌ Backend server not available. Please start the backend first.")
    return False

def generate_static_posts():
    # Create directory for static posts
    posts_dir = Path("frontend/public/static-posts")
    posts_dir.mkdir(parents=True, exist_ok=True)
    
    posts = []
    
    print("🎨 Generating marketing posts...\n")
    
    for i, topic in enumerate(SAMPLE_TOPICS):
        print(f"Generating post {i + 1}/{len(SAMPLE_TOPICS)}: {topic}")
        
        try:
            response = requests.post(
                f"{API_URL}/api/marketing-post/create",
                json={
                    "topic": topic,
                    "caption_style": "engaging",
                    "aspect_ratio": "1:1",
                    "include_hashtags": True,
                    "post_to_instagram": False
                },
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"  ✗ Error: {response.status_code} - {response.text}")
                # Create placeholder
                posts.append({
                    "id": i,
                    "topic": topic,
                    "caption": f"Engaging content about {topic}. Discover how this topic can transform your business and drive results.",
                    "image": None,
                    "hashtags": [],
                    "image_prompt": None
                })
                continue
            
            post_data = response.json()
            
            # Save image
            image_path = None
            if post_data.get("image_base64"):
                image_buffer = base64.b64decode(post_data["image_base64"])
                image_filename = f"post-{i + 1}.png"
                image_path = f"static-posts/{image_filename}"
                full_image_path = posts_dir / image_filename
                full_image_path.write_bytes(image_buffer)
                print(f"  ✓ Image saved: {image_path}")
            elif post_data.get("image_url"):
                # Download image from URL
                img_response = requests.get(post_data["image_url"], timeout=30)
                if img_response.status_code == 200:
                    image_filename = f"post-{i + 1}.png"
                    image_path = f"static-posts/{image_filename}"
                    full_image_path = posts_dir / image_filename
                    full_image_path.write_bytes(img_response.content)
                    print(f"  ✓ Image saved: {image_path}")
            
            # Create post metadata
            post_metadata = {
                "id": i,
                "topic": topic,
                "caption": post_data.get("full_caption") or post_data.get("caption", ""),
                "image": image_path,
                "hashtags": post_data.get("hashtags", []),
                "image_prompt": post_data.get("image_prompt")
            }
            
            posts.append(post_metadata)
            print(f"\n✅ Post {i + 1} complete!")
            print(f"   Topic: {topic}")
            print(f"   Image: {image_path or 'Gradient placeholder'}")
            print(f"   Caption length: {len(post_metadata['caption'])} chars")
            
            # Wait before next post to avoid rate limiting
            if i < len(SAMPLE_TOPICS) - 1:
                print(f"\n⏳ Waiting 3 seconds before next post...")
                time.sleep(3)
            
        except Exception as error:
            print(f"\n❌ Error generating post {i + 1}: {str(error)}")
            # Create a placeholder post
            posts.append({
                "id": i,
                "topic": topic,
                "caption": f"Engaging content about {topic}. Discover how this topic can transform your business and drive results.",
                "image": None,
                "hashtags": [],
                "image_prompt": None
            })
            print(f"   Using placeholder for post {i + 1}")
            
            # Wait before next post even on error
            if i < len(SAMPLE_TOPICS) - 1:
                print(f"\n⏳ Waiting 2 seconds before next post...")
                time.sleep(2)
    
    # Save posts metadata as JSON
    metadata_path = posts_dir / "posts.json"
    with open(metadata_path, "w") as f:
        json.dump(posts, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"✅ All posts generated!")
    print(f"{'='*60}")
    print(f"📁 Posts saved to: {posts_dir}")
    print(f"📄 Metadata saved to: {metadata_path}")
    print(f"\nTotal posts: {len(posts)}")
    print(f"Posts with images: {sum(1 for p in posts if p.get('image'))}")
    print(f"Placeholder posts: {sum(1 for p in posts if not p.get('image'))}")

if __name__ == "__main__":
    generate_static_posts()

