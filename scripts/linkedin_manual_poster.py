#!/usr/bin/env python3
"""
LinkedIn Manual Poster
Posts videos to LinkedIn using browser automation.
Your credentials are only used locally and never sent to any server.

Installation:
    pip install playwright
    playwright install chromium

Usage:
    python linkedin_manual_poster.py --username YOUR_EMAIL --video VIDEO_PATH --caption "Your caption"
"""

from playwright.sync_api import sync_playwright
import argparse
import time
import getpass
import sys
from pathlib import Path


def post_to_linkedin(username, password, video_path, caption):
    """Post a video to LinkedIn using browser automation"""
    
    # Validate video file exists
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"\n🚀 Starting LinkedIn post automation...")
    print(f"   Email: {username}")
    print(f"   Video: {video_path}")
    print(f"   Caption: {caption[:50]}...")
    print(f"\n⚠️  A browser window will open. Please DO NOT close it manually.")
    print(f"   The script will handle everything automatically.\n")
    
    with sync_playwright() as p:
        try:
            # Launch browser (visible, not headless)
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Step 1: Login to LinkedIn
            print("📱 Step 1: Logging into LinkedIn...")
            page.goto("https://www.linkedin.com/login")
            time.sleep(3)
            
            # Fill in credentials
            username_input = page.wait_for_selector('input[name="session_key"]', timeout=10000)
            username_input.fill(username)
            
            password_input = page.wait_for_selector('input[name="session_password"]', timeout=10000)
            password_input.fill(password)
            
            # Click login button
            login_button = page.wait_for_selector('button[type="submit"]', timeout=10000)
            login_button.click()
            
            print("   ✓ Credentials submitted, waiting for login...")
            time.sleep(5)
            
            # Check if login was successful
            if "login" in page.url.lower():
                print("❌ Login failed. Please check your credentials.")
                browser.close()
                sys.exit(1)
            
            print("   ✓ Login successful!")
            
            # Step 2: Navigate to feed
            print("\n📸 Step 2: Opening create post dialog...")
            page.goto("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            # Step 3: Click "Start a post" button
            start_post_selectors = [
                'button[aria-label*="Start a post"]',
                'button:has-text("Start a post")',
                'div[aria-label*="Start a post"]',
                'span:has-text("Start a post")'
            ]
            
            post_clicked = False
            for selector in start_post_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        # Scroll into view
                        element.scroll_into_view_if_needed()
                        time.sleep(1)
                        element.click()
                        post_clicked = True
                        break
                except:
                    continue
            
            if not post_clicked:
                # Try clicking on the text directly
                try:
                    page.click('text=Start a post', timeout=5000)
                    post_clicked = True
                except:
                    pass
            
            if not post_clicked:
                print("   ⚠️  Could not find 'Start a post' button. Please click it manually.")
                print("   Waiting 10 seconds...")
                time.sleep(10)
            
            time.sleep(3)
            
            # Step 4: Upload video
            print("📤 Step 3: Uploading video...")
            
            # Find the media/photo/video button
            media_selectors = [
                'button[aria-label*="Add media"]',
                'button[aria-label*="Photo"]',
                'button[aria-label*="Video"]',
                'svg[aria-label*="Add media"]',
                'button:has-text("Media")'
            ]
            
            media_clicked = False
            for selector in media_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        element.click()
                        media_clicked = True
                        break
                except:
                    continue
            
            if not media_clicked:
                print("   ⚠️  Could not find media button. Trying file input directly...")
            
            time.sleep(2)
            
            # Find and use file input
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                # Create file input if not found
                page.evaluate("""
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'video/*';
                    input.style.display = 'none';
                    document.body.appendChild(input);
                    input.click();
                """)
                file_input = page.wait_for_selector('input[type="file"]', timeout=5000)
            
            file_input.set_input_files(video_path)
            print("   ✓ Video selected")
            time.sleep(5)  # Wait for video to upload/process
            
            # Step 5: Add caption
            print("✍️  Step 4: Adding caption...")
            
            # Find caption/comment input
            caption_selectors = [
                'div[contenteditable="true"][aria-label*="post"]',
                'div[contenteditable="true"][aria-label*="What"]',
                'div[contenteditable="true"][role="textbox"]',
                'div[data-placeholder*="What"]'
            ]
            
            caption_added = False
            for selector in caption_selectors:
                try:
                    caption_input = page.wait_for_selector(selector, timeout=5000)
                    if caption_input:
                        caption_input.click()
                        time.sleep(1)
                        caption_input.fill(caption)
                        caption_added = True
                        print("   ✓ Caption added")
                        break
                except:
                    continue
            
            if not caption_added:
                print("   ⚠️  Could not find caption input. Please add caption manually.")
            
            time.sleep(3)
            
            # Step 6: Post
            print("🚀 Step 5: Posting video...")
            
            # Find post button
            post_selectors = [
                'button:has-text("Post")',
                'button[aria-label*="Post"]',
                'button[data-control-name*="share"]',
                'span:has-text("Post")'
            ]
            
            posted = False
            for selector in post_selectors:
                try:
                    post_button = page.query_selector(selector)
                    if post_button and post_button.is_visible():
                        post_button.click()
                        posted = True
                        print("   ✓ Post button clicked!")
                        break
                except:
                    continue
            
            if not posted:
                print("   ⚠️  Could not find Post button. Please click 'Post' manually.")
                print("   Waiting 30 seconds for you to post manually...")
                time.sleep(30)
            else:
                time.sleep(5)
            
            print("\n✅ Posting process completed!")
            print("   Check your LinkedIn to confirm the video was posted.\n")
            
            # Keep browser open for a few seconds
            time.sleep(5)
            browser.close()
            
        except Exception as e:
            print(f"\n❌ Error occurred: {str(e)}")
            print("   The browser window will remain open so you can troubleshoot.")
            input("   Press Enter to close the browser...")
            browser.close()
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Post videos to LinkedIn using browser automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linkedin_manual_poster.py --username user@example.com --video ./video.mp4 --caption "Check out this video!"
  python linkedin_manual_poster.py -u user@example.com -v ./video.mp4 -c "My amazing video"
        """
    )
    parser.add_argument('-u', '--username', required=True, help='LinkedIn email/username')
    parser.add_argument('-v', '--video', required=True, help='Path to video file')
    parser.add_argument('-c', '--caption', required=True, help='Post caption')
    
    args = parser.parse_args()
    
    # Get password securely
    password = getpass.getpass("Enter your LinkedIn password (won't be stored): ")
    
    if not password:
        print("❌ Password is required.")
        sys.exit(1)
    
    # Post the video
    post_to_linkedin(args.username, password, args.video, args.caption)


if __name__ == "__main__":
    main()



