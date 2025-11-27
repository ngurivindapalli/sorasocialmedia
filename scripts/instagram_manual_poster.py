#!/usr/bin/env python3
"""
Instagram Manual Poster
Posts videos to Instagram using browser automation.
Your credentials are only used locally and never sent to any server.

Installation:
    pip install playwright
    playwright install chromium

Usage:
    python instagram_manual_poster.py --username YOUR_USERNAME --video VIDEO_PATH --caption "Your caption"
"""

from playwright.sync_api import sync_playwright
import argparse
import time
import getpass
import sys
from pathlib import Path


def post_to_instagram(username, password, video_path, caption):
    """Post a video to Instagram using browser automation"""
    
    # Validate video file exists
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)
    
    print(f"\n🚀 Starting Instagram post automation...")
    print(f"   Username: {username}")
    print(f"   Video: {video_path}")
    print(f"   Caption: {caption[:50]}...")
    print(f"\n⚠️  A browser window will open. Please DO NOT close it manually.")
    print(f"   The script will handle everything automatically.\n")
    
    with sync_playwright() as p:
        try:
            # Launch browser (visible, not headless, so you can see what's happening)
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Step 1: Login to Instagram
            print("📱 Step 1: Logging into Instagram...")
            page.goto("https://www.instagram.com/accounts/login/")
            time.sleep(3)
            
            # Fill in credentials
            username_input = page.wait_for_selector('input[name="username"]', timeout=10000)
            username_input.fill(username)
            
            password_input = page.wait_for_selector('input[name="password"]', timeout=10000)
            password_input.fill(password)
            
            # Click login button
            login_button = page.wait_for_selector('button[type="submit"]', timeout=10000)
            login_button.click()
            
            print("   ✓ Credentials submitted, waiting for login...")
            time.sleep(5)
            
            # Check if login was successful (look for home page)
            if "accounts/login" in page.url:
                print("❌ Login failed. Please check your credentials.")
                browser.close()
                sys.exit(1)
            
            print("   ✓ Login successful!")
            
            # Step 2: Navigate to create post
            print("\n📸 Step 2: Opening create post dialog...")
            
            # Try multiple selectors for the "New post" button
            create_selectors = [
                'svg[aria-label="New post"]',
                'svg[aria-label="New"]',
                'a[href="#"] svg[aria-label*="New"]',
                'button[aria-label*="New post"]'
            ]
            
            create_clicked = False
            for selector in create_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        element.click()
                        create_clicked = True
                        break
                except:
                    continue
            
            if not create_clicked:
                # Alternative: Navigate directly to create post
                page.goto("https://www.instagram.com/")
                time.sleep(3)
                # Try clicking via text or other methods
                page.click('text=Create', timeout=5000)
            
            time.sleep(3)
            
            # Step 3: Upload video
            print("📤 Step 3: Uploading video...")
            
            # Find file input (it's usually hidden)
            file_input = page.query_selector('input[type="file"]')
            if not file_input:
                print("   ⚠️  File input not found, trying alternative method...")
                # Try creating file input and triggering click
                page.evaluate("""
                    const input = document.createElement('input');
                    input.type = 'file';
                    input.accept = 'video/*';
                    input.style.display = 'none';
                    document.body.appendChild(input);
                    input.click();
                """)
                file_input = page.wait_for_selector('input[type="file"]', timeout=5000)
            
            # Upload the video file
            file_input.set_input_files(video_path)
            print("   ✓ Video selected")
            time.sleep(5)  # Wait for video to process
            
            # Step 4: Add caption
            print("✍️  Step 4: Adding caption...")
            
            # Find caption input (may take a moment to appear)
            caption_selectors = [
                'textarea[aria-label*="Write a caption"]',
                'textarea[aria-label*="caption"]',
                'textarea[placeholder*="Write a caption"]',
                'textarea[placeholder*="caption"]'
            ]
            
            caption_added = False
            for selector in caption_selectors:
                try:
                    caption_input = page.wait_for_selector(selector, timeout=5000)
                    if caption_input:
                        caption_input.fill(caption)
                        caption_added = True
                        print("   ✓ Caption added")
                        break
                except:
                    continue
            
            if not caption_added:
                print("   ⚠️  Could not find caption input, continuing without caption...")
            
            time.sleep(2)
            
            # Step 5: Post
            print("🚀 Step 5: Posting video...")
            
            # Find share/post button
            share_selectors = [
                'button:has-text("Share")',
                'button:has-text("Post")',
                'button[type="submit"]',
                'div[role="button"]:has-text("Share")'
            ]
            
            posted = False
            for selector in share_selectors:
                try:
                    share_button = page.query_selector(selector)
                    if share_button and share_button.is_visible():
                        share_button.click()
                        posted = True
                        print("   ✓ Post button clicked!")
                        break
                except:
                    continue
            
            if not posted:
                print("   ⚠️  Could not find Share button. Please click 'Share' manually.")
                print("   Waiting 30 seconds for you to post manually...")
                time.sleep(30)
            else:
                time.sleep(5)
            
            print("\n✅ Posting process completed!")
            print("   Check your Instagram to confirm the video was posted.\n")
            
            # Keep browser open for a few seconds so you can see the result
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
        description='Post videos to Instagram using browser automation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python instagram_manual_poster.py --username myusername --video ./video.mp4 --caption "Check out this video!"
  python instagram_manual_poster.py -u myusername -v ./video.mp4 -c "My amazing video"
        """
    )
    parser.add_argument('-u', '--username', required=True, help='Instagram username')
    parser.add_argument('-v', '--video', required=True, help='Path to video file')
    parser.add_argument('-c', '--caption', required=True, help='Post caption')
    
    args = parser.parse_args()
    
    # Get password securely
    password = getpass.getpass("Enter your Instagram password (won't be stored): ")
    
    if not password:
        print("❌ Password is required.")
        sys.exit(1)
    
    # Post the video
    post_to_instagram(args.username, password, args.video, args.caption)


if __name__ == "__main__":
    main()



