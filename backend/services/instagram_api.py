import instaloader
import os
from typing import List, Dict, Optional
import requests

class InstagramAPIService:
    """Service for fetching Instagram videos - uses instaloader scraping"""
    
    def __init__(self):
        print("[IG] Using Instagram scraping (instaloader)")
        self._init_scraper()
    
    def _init_scraper(self):
        # Configure instaloader with better user agent and rate limiting
        self.loader = instaloader.Instaloader(
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            quiet=True,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            request_timeout=60,
            max_connection_attempts=3
        )
        
        # Set additional session headers to mimic real browser
        self.loader.context._session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
        
        # Try to login with Instagram credentials if provided (helps avoid blocking)
        ig_username = os.getenv('INSTAGRAM_USERNAME')
        ig_password = os.getenv('INSTAGRAM_PASSWORD')
        
        # Strip quotes if present (handles passwords with # characters)
        if ig_username:
            ig_username = ig_username.strip().strip('"').strip("'")
        if ig_password:
            ig_password = ig_password.strip().strip('"').strip("'")
        
        # Store credentials for retry if needed
        self.ig_username = ig_username
        self.ig_password = ig_password
        
        if ig_username and ig_password:
            print(f"[IG] Found credentials: username={ig_username}, password_length={len(ig_password)}")
            try:
                print(f"[IG] Attempting login as @{ig_username}...")
                self.loader.login(ig_username, ig_password)
                print(f"[IG] ✓ Successfully logged in as @{ig_username}")
                self.logged_in = True
            except Exception as login_error:
                print(f"[IG] ⚠️ Login failed: {login_error}")
                print(f"[IG] Continuing without authentication. This may cause rate limiting.")
                self.logged_in = False
        else:
            if not ig_username:
                print("[IG] ⚠️ INSTAGRAM_USERNAME not set in .env file")
            if not ig_password:
                print("[IG] ⚠️ INSTAGRAM_PASSWORD not set in .env file")
            print("[IG] Running without authentication (may be rate-limited).")
            print("[IG] Tip: Set INSTAGRAM_USERNAME and INSTAGRAM_PASSWORD in backend/.env to avoid blocking.")
            self.logged_in = False
        
        print("[IG] Initialized with browser-like headers to avoid blocking")
    
    async def get_profile_context(self, username: str) -> Dict:
        """Extract profile context using scraping"""
        try:
            print(f"[IG] Extracting profile context for: {username}")
            
            import time
            import random
            time.sleep(random.uniform(1.5, 3.0))
            
            profile = instaloader.Profile.from_username(self.loader.context, username)
            
            # Extract profile information
            context = {
                "username": profile.username,
                "full_name": profile.full_name or "",
                "biography": profile.biography or "",
                "external_url": profile.external_url or "",
                "is_business_account": profile.is_business_account,
                "business_category": profile.business_category_name or "",
                "followers": profile.followers,
                "following": profile.followees,
                "posts_count": profile.mediacount,
                "is_verified": profile.is_verified,
                "profile_pic_url": profile.profile_pic_url or ""
            }
            
            print(f"[IG] Profile context extracted: {context['full_name']}, Business: {context['is_business_account']}, Category: {context['business_category']}")
            return context
            
        except Exception as e:
            print(f"[IG] Error extracting profile context: {str(e)}")
            return {
                "username": username,
                "full_name": "",
                "biography": "",
                "external_url": "",
                "is_business_account": False,
                "business_category": "",
                "followers": 0,
                "following": 0,
                "posts_count": 0,
                "is_verified": False,
                "profile_pic_url": ""
            }
    
    async def get_user_videos(self, username: str, limit: int = 1) -> List[Dict]:
        """Fetch videos from Instagram profile using scraping"""
        videos = []
        
        try:
            print(f"[IG] Loading profile: {username}")
            
            # Add delay to avoid rate limiting
            import time
            import random
            time.sleep(random.uniform(1.5, 3.0))  # Random delay 1.5-3 seconds
            
            profile = instaloader.Profile.from_username(self.loader.context, username)
            print(f"[IG] Profile loaded. Username: {profile.username}, Full name: {profile.full_name}")
            
            post_count = 0
            checked_posts = 0
            
            # Iterate through posts with rate limit protection
            try:
                for post in profile.get_posts():
                    checked_posts += 1
                    print(f"[IG] Checking post {checked_posts}, shortcode: {post.shortcode}, is_video: {post.is_video}")
                    
                    try:
                        # Only process video posts
                        if not post.is_video:
                            continue
                        
                        post_count += 1
                        print(f"[IG] Found video #{post_count}")
                        
                        # Access video URL through the node data structure
                        try:
                            # Method 1: Direct access
                            video_url = post.video_url
                        except:
                            try:
                                # Method 2: Through node
                                video_url = post._node['video_url']
                            except:
                                print(f"[IG] Could not get video URL for post {post.shortcode}")
                                continue
                        
                        # Get metrics safely
                        try:
                            likes = post.likes
                        except:
                            likes = 0
                        
                        try:
                            video_views = post.video_view_count
                        except:
                            video_views = 0
                        
                        try:
                            caption = post.caption if post.caption else ""
                            if len(caption) > 200:
                                caption = caption[:200] + "..."
                        except:
                            caption = ""
                        
                        # Get thumbnail URL for Vision API
                        try:
                            thumbnail_url = post.url  # Display URL (image/thumbnail)
                        except:
                            thumbnail_url = None
                        
                        video_data = {
                            "id": post.shortcode,
                            "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
                            "video_url": video_url,
                            "thumbnail_url": thumbnail_url,  # For Vision API analysis
                            "views": video_views,
                            "likes": likes,
                            "text": caption,
                            "duration": 0  # Instagram doesn't expose duration easily
                        }
                        
                        videos.append(video_data)
                        print(f"[IG] Successfully added video: {post.shortcode}")
                        
                        # Stop if we have enough videos
                        if len(videos) >= limit:
                            break
                                
                    except Exception as post_error:
                        print(f"[IG] Error processing individual post: {str(post_error)}")
                        import traceback
                        traceback.print_exc()
                        continue
                    
                    # Safety limit - stop after checking 20 posts
                    if checked_posts >= 20:
                        print(f"[IG] Checked 20 posts, stopping")
                        break
            
            except KeyError as rate_limit_error:
                # Instagram rate limited us - return what we have
                if videos:
                    print(f"[IG] ⚠️ Instagram rate limit reached after checking {checked_posts} posts. Returning {len(videos)} video(s) found so far.")
                else:
                    raise Exception(f"Instagram blocked request after {checked_posts} posts. Please try again in a few minutes or use a different account.")
            
            if not videos:
                raise Exception(f"No videos found in the first {checked_posts} posts from @{username}")
            
            print(f"[IG] Successfully found {len(videos)} video(s)")
            return videos
            
        except instaloader.exceptions.ProfileNotExistsException:
            raise Exception(f"Instagram profile '@{username}' does not exist")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            raise Exception(f"Profile '@{username}' is private. Cannot access without login.")
        except instaloader.exceptions.ConnectionException as e:
            error_msg = str(e)
            if "401" in error_msg:
                # 401 = Unauthorized - try to re-login if credentials are available
                if self.ig_username and self.ig_password and not self.logged_in:
                    print(f"[IG] Got 401 error, attempting to re-login...")
                    try:
                        self.loader.login(self.ig_username, self.ig_password)
                        print(f"[IG] ✓ Re-login successful")
                        self.logged_in = True
                        # Retry the request
                        return await self.get_user_videos(username, limit)
                    except Exception as relogin_error:
                        print(f"[IG] ⚠️ Re-login failed: {relogin_error}")
                
                if self.logged_in:
                    raise Exception(f"Instagram authentication failed even after login. Your credentials may be incorrect or your account may need verification. Error: {error_msg}")
                else:
                    raise Exception(f"⚠️ Instagram blocked the request (401 Unauthorized).\n\n🔧 Solutions:\n1. Add Instagram login credentials to backend/.env:\n   INSTAGRAM_USERNAME=your_username\n   INSTAGRAM_PASSWORD=\"your_password\" (use quotes if password has #)\n2. Verify your credentials are correct\n3. Try a different Instagram account\n4. Wait 10-15 minutes (rate limiting)\n\nAuthenticated requests are much less likely to be blocked!")
            elif "429" in error_msg:
                if self.logged_in:
                    raise Exception(f"Instagram rate limit reached even with authentication. Please wait 10-15 minutes and try again.")
                else:
                    raise Exception(f"⚠️ Instagram rate limit reached (429).\n\n🔧 Solutions:\n1. Add Instagram login credentials to backend/.env to reduce rate limiting\n2. Wait 10-15 minutes before trying again\n3. Try a different Instagram account")
            raise Exception(f"Instagram connection error: {str(e)}")
        except Exception as e:
            print(f"[IG] Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error fetching Instagram videos: {str(e)}")
    
    async def download_video(self, video_url: str, video_id: str) -> str:
        """Download Instagram video to temporary file"""
        os.makedirs("temp", exist_ok=True)
        file_path = f"temp/ig_{video_id}.mp4"
        
        try:
            print(f"[IG] Downloading video: {video_id}")
            response = requests.get(video_url, timeout=90, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            with open(file_path, "wb") as f:
                f.write(response.content)
            
            print(f"[IG] Video downloaded: {file_path} ({len(response.content)} bytes)")
            return file_path
        except Exception as e:
            raise Exception(f"Error downloading Instagram video: {str(e)}")
