"""
Test script to create and post a test post to LinkedIn
"""
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
# Try to use production URL first, fallback to localhost
API_URL = os.getenv("API_URL") or os.getenv("BACKEND_URL") or "http://localhost:8000"
BACKEND_URL = os.getenv("FRONTEND_URL") or os.getenv("BACKEND_URL") or "https://aigismarketing.com"

# If API_URL doesn't start with http, assume it's a relative path
if not API_URL.startswith("http"):
    API_URL = f"https://{API_URL}" if not API_URL.startswith("localhost") else f"http://{API_URL}"

def get_linkedin_connections():
    """Get all LinkedIn connections"""
    try:
        response = requests.get(f"{API_URL}/api/connections")
        response.raise_for_status()
        connections = response.json()
        
        # Filter for LinkedIn connections
        linkedin_connections = [c for c in connections if c.get("platform") == "linkedin" and c.get("is_active")]
        
        if not linkedin_connections:
            print("ERROR: No active LinkedIn connections found")
            print("\nTo connect LinkedIn:")
            print(f"   1. Go to: {BACKEND_URL}/dashboard?tab=settings")
            print("   2. Click 'Connect LinkedIn'")
            print("   3. Complete OAuth flow")
            return None
        
        print(f"OK: Found {len(linkedin_connections)} LinkedIn connection(s):")
        for conn in linkedin_connections:
            print(f"   - ID: {conn['id']}, Username: {conn.get('account_username', 'N/A')}")
        
        return linkedin_connections
    except Exception as e:
        print(f"ERROR: Error getting connections: {e}")
        return None

def create_test_post(connection_id, test_type="text"):
    """Create and post a test post to LinkedIn"""
    
    # Test caption
    caption = """Test Post from Aigis Marketing

This is a test post to verify LinkedIn integration is working correctly.

If you see this, the posting functionality is working!

#TestPost #AigisMarketing #LinkedInAPI"""
    
    # For text-only post
    if test_type == "text":
        payload = {
            "connection_ids": [connection_id],
            "caption": caption,
            "video_url": None,
            "image_url": None
        }
    # For image post (if you have an image URL)
    elif test_type == "image" and os.getenv("TEST_IMAGE_URL"):
        payload = {
            "connection_ids": [connection_id],
            "caption": caption,
            "video_url": None,
            "image_url": os.getenv("TEST_IMAGE_URL")
        }
    # For video post (if you have a video URL)
    elif test_type == "video" and os.getenv("TEST_VIDEO_URL"):
        payload = {
            "connection_ids": [connection_id],
            "caption": caption,
            "video_url": os.getenv("TEST_VIDEO_URL"),
            "image_url": None
        }
    else:
        print("WARNING: Using text-only post (no image/video URL provided)")
        payload = {
            "connection_ids": [connection_id],
            "caption": caption,
            "video_url": None,
            "image_url": None
        }
    
    try:
        print(f"\nPosting to LinkedIn (connection ID: {connection_id})...")
        print(f"Caption: {caption[:100]}...")
        
        response = requests.post(
            f"{API_URL}/api/post/video",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get("success"):
            print("\nPOST SUCCESSFUL!")
            for post in result.get("posts", []):
                if post.get("success"):
                    print(f"   Post ID: {post.get('post_id')}")
                    print(f"   Post URL: {post.get('post_url')}")
                    print(f"   Platform: {post.get('platform')}")
                    return post.get("post_url")
        else:
            print("\nPOST FAILED!")
            for post in result.get("posts", []):
                if not post.get("success"):
                    print(f"   Error: {post.get('error')}")
            if result.get("errors"):
                for error in result.get("errors"):
                    print(f"   Error: {error}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"   Error details: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"   Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return None

def main():
    print("=" * 60)
    print("LinkedIn Test Post Script")
    print("=" * 60)
    
    # Step 1: Get LinkedIn connections
    print("\nStep 1: Checking for LinkedIn connections...")
    connections = get_linkedin_connections()
    
    if not connections:
        return
    
    # Step 2: Use first LinkedIn connection
    connection = connections[0]
    connection_id = connection["id"]
    
    print(f"\nStep 2: Using connection ID: {connection_id}")
    print(f"   Username: {connection.get('account_username', 'N/A')}")
    
    # Step 3: Create test post
    print(f"\nStep 3: Creating test post...")
    post_url = create_test_post(connection_id, test_type="text")
    
    if post_url:
        print("\n" + "=" * 60)
        print("SUCCESS! Test post created and published to LinkedIn")
        print(f"View your post: {post_url}")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("FAILED! Could not create test post")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("   1. Check that LinkedIn connection is active")
        print("   2. Verify access token is valid (may need to reconnect)")
        print("   3. Check backend logs for detailed error messages")
        print("   4. Ensure w_member_social permission is granted")

if __name__ == "__main__":
    main()
