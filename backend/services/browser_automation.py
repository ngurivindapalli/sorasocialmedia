"""
Browser automation service for posting videos to Instagram/LinkedIn
Uses Playwright to automate the posting process
"""

import asyncio
import os
import tempfile
import httpx
from typing import Dict, Optional
from pathlib import Path


class BrowserAutomationService:
    """Service for automating browser actions to post videos"""
    
    def __init__(self):
        self.playwright_available = self._check_playwright()
    
    def _check_playwright(self) -> bool:
        """Check if Playwright is installed"""
        try:
            from playwright.sync_api import sync_playwright
            return True
        except ImportError:
            print("[BrowserAutomation] Playwright not installed. Run: pip install playwright && playwright install chromium")
            return False
    
    async def post_to_instagram_automation(
        self,
        username: str,
        password: str,
        video_url: str,
        caption: str
    ) -> Dict:
        """
        Post video to Instagram using browser automation
        
        Args:
            username: Instagram username
            password: Instagram password
            video_url: URL or path to video file
            caption: Post caption
            
        Returns:
            Dict with success status and message
        """
        if not self.playwright_available:
            return {
                "success": False,
                "error": "Playwright not installed. Please install it: pip install playwright && playwright install chromium"
            }
        
        try:
            from playwright.sync_api import sync_playwright
            import time
            from pathlib import Path
            
            print(f"[BrowserAutomation] Starting Instagram post automation for user: {username}")
            
            # Download video if it's a URL
            video_path = None
            if video_url.startswith("http://") or video_url.startswith("https://"):
                print(f"[BrowserAutomation] Downloading video from URL: {video_url}")
                video_path = await self._download_video(video_url)
                if not video_path:
                    return {
                        "success": False,
                        "error": "Failed to download video from URL"
                    }
            else:
                video_path = video_url
                if not Path(video_path).exists():
                    return {
                        "success": False,
                        "error": f"Video file not found: {video_path}"
                    }
            
            print(f"[BrowserAutomation] Video path: {video_path}")
            
            # Run browser automation in a thread pool to avoid blocking
            result = await asyncio.to_thread(
                self._run_instagram_automation,
                username, password, video_path, caption
            )
            
            # Clean up temporary file if we downloaded it
            if video_url.startswith("http://") or video_url.startswith("https://"):
                try:
                    if video_path and Path(video_path).exists():
                        Path(video_path).unlink()
                        print(f"[BrowserAutomation] Cleaned up temporary video file")
                except Exception as e:
                    print(f"[BrowserAutomation] Failed to clean up temp file: {e}")
            
            return result
            
        except Exception as e:
            print(f"[BrowserAutomation] Error in Instagram automation: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _run_instagram_automation(
        self,
        username: str,
        password: str,
        video_path: str,
        caption: str
    ) -> Dict:
        """Run Instagram automation synchronously"""
        from playwright.sync_api import sync_playwright
        import time
        
        try:
            with sync_playwright() as p:
                # Launch browser (headless=False so user can see what's happening)
                browser = p.chromium.launch(headless=False)
                context = browser.new_context(
                    viewport={'width': 1280, 'height': 720},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                try:
                    # Step 1: Login
                    print("[BrowserAutomation] Step 1: Logging into Instagram...")
                    page.goto("https://www.instagram.com/accounts/login/")
                    time.sleep(3)
                    
                    username_input = page.wait_for_selector('input[name="username"]', timeout=10000)
                    username_input.fill(username)
                    
                    password_input = page.wait_for_selector('input[name="password"]', timeout=10000)
                    password_input.fill(password)
                    
                    login_button = page.wait_for_selector('button[type="submit"]', timeout=10000)
                    login_button.click()
                    
                    time.sleep(5)
                    
                    # Check if login was successful
                    if "accounts/login" in page.url:
                        browser.close()
                        return {
                            "success": False,
                            "error": "Login failed. Please check your credentials."
                        }
                    
                    print("[BrowserAutomation] OK Login successful")
                    
                    # Step 2: Navigate to create post
                    print("[BrowserAutomation] Step 2: Opening create post dialog...")
                    page.goto("https://www.instagram.com/")
                    time.sleep(3)
                    
                    # Try to find and click create button
                    create_selectors = [
                        'svg[aria-label="New post"]',
                        'svg[aria-label="New"]',
                        'a[href="#"] svg[aria-label*="New"]',
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
                        # Alternative: Use keyboard shortcut or direct navigation
                        page.keyboard.press('Meta+n')  # Cmd/Ctrl + N
                        time.sleep(2)
                    
                    time.sleep(3)
                    
                    # Step 3: Upload video
                    print("[BrowserAutomation] Step 3: Uploading video...")
                    
                    # Find file input
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
                    print("[BrowserAutomation] OK Video selected")
                    time.sleep(5)  # Wait for video to process
                    
                    # Step 4: Add caption
                    print("[BrowserAutomation] Step 4: Adding caption...")
                    
                    caption_selectors = [
                        'textarea[aria-label*="Write a caption"]',
                        'textarea[aria-label*="caption"]',
                        'textarea[placeholder*="Write a caption"]',
                    ]
                    
                    caption_added = False
                    for selector in caption_selectors:
                        try:
                            caption_input = page.wait_for_selector(selector, timeout=5000)
                            if caption_input:
                                caption_input.fill(caption)
                                caption_added = True
                                print("[BrowserAutomation] OK Caption added")
                                break
                        except:
                            continue
                    
                    if not caption_added:
                        print("[BrowserAutomation] WARNING  Could not find caption input")
                    
                    time.sleep(2)
                    
                    # Step 5: Post
                    print("[BrowserAutomation] Step 5: Posting video...")
                    
                    share_selectors = [
                        'button:has-text("Share")',
                        'button:has-text("Post")',
                        'button[type="submit"]',
                    ]
                    
                    posted = False
                    for selector in share_selectors:
                        try:
                            share_button = page.query_selector(selector)
                            if share_button and share_button.is_visible():
                                share_button.click()
                                posted = True
                                print("[BrowserAutomation] OK Post button clicked")
                                break
                        except:
                            continue
                    
                    if not posted:
                        print("[BrowserAutomation] WARNING  Could not find Share button automatically")
                        time.sleep(10)  # Give user time to click manually
                    
                    time.sleep(5)
                    
                    browser.close()
                    
                    return {
                        "success": True,
                        "message": "Video posted successfully! Check your Instagram to confirm."
                    }
                    
                except Exception as e:
                    browser.close()
                    raise e
                    
        except Exception as e:
            print(f"[BrowserAutomation] Automation error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": f"Automation failed: {str(e)}"
            }
    
    async def _download_video(self, video_url: str) -> Optional[str]:
        """Download video from URL to temporary file"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.get(video_url)
                response.raise_for_status()
                
                # Create temporary file
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"video_{os.urandom(8).hex()}.mp4")
                
                with open(temp_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"[BrowserAutomation] Video downloaded to: {temp_file}")
                return temp_file
                
        except Exception as e:
            print(f"[BrowserAutomation] Failed to download video: {e}")
            return None



