import httpx
import os
import base64
from typing import Dict, Optional
from datetime import datetime, timedelta


class PostingService:
    """Service for posting content to social media platforms"""
    
    def __init__(self):
        # LinkedIn Company Page configuration
        self.linkedin_company_id = os.getenv("LINKEDIN_COMPANY_ID", "")
        print(f"[PostingService] Initialized with LinkedIn Company ID: {self.linkedin_company_id or 'Not set'}")
    
    async def post_to_instagram(
        self,
        access_token: str,
        video_url: str,
        caption: str,
        account_id: str
    ) -> Dict:
        """
        Post video to Instagram using Graph API
        
        Args:
            access_token: Instagram access token
            video_url: URL to the video file
            caption: Post caption
            account_id: Instagram account ID
            
        Returns:
            Dict with post_id and post_url
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Step 1: Create media container
                container_response = await client.post(
                    f"https://graph.instagram.com/v18.0/{account_id}/media",
                    params={
                        "media_type": "REELS",
                        "video_url": video_url,
                        "caption": caption,
                        "access_token": access_token
                    }
                )
                container_response.raise_for_status()
                container_id = container_response.json()["id"]
                
                # Step 2: Publish the container
                publish_response = await client.post(
                    f"https://graph.instagram.com/v18.0/{account_id}/media_publish",
                    params={
                        "creation_id": container_id,
                        "access_token": access_token
                    }
                )
                publish_response.raise_for_status()
                post_data = publish_response.json()
                
                return {
                    "success": True,
                    "post_id": post_data["id"],
                    "post_url": f"https://www.instagram.com/reel/{post_data['id']}/",
                    "platform": "instagram"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "instagram"
            }
    
    async def post_to_linkedin(
        self,
        access_token: str,
        video_url: str = None,
        image_url: str = None,
        caption: str = "",
        person_urn: str = None,
        company_id: str = None,
        use_company_page: bool = False
    ) -> Dict:
        """
        Post to LinkedIn (personal profile or company page)
        
        Args:
            access_token: LinkedIn access token
            video_url: URL to the video file (optional)
            image_url: URL or base64 of image (optional)
            caption: Post caption
            person_urn: LinkedIn person URN (e.g., "urn:li:person:xxxxx")
            company_id: LinkedIn company/organization ID (optional, for company page posts)
            use_company_page: If True, post to company page instead of personal
            
        Returns:
            Dict with post_id and post_url
        """
        try:
            # Determine author (company page or personal)
            if use_company_page or company_id:
                company = company_id or self.linkedin_company_id
                if not company:
                    return {
                        "success": False,
                        "error": "LinkedIn Company ID not configured. Set LINKEDIN_COMPANY_ID in environment.",
                        "platform": "linkedin"
                    }
                author_urn = f"urn:li:organization:{company}"
                print(f"[LinkedIn] Posting to company page: {author_urn}")
            else:
                if not person_urn:
                    return {
                        "success": False,
                        "error": "Person URN required for personal posts",
                        "platform": "linkedin"
                    }
                author_urn = person_urn
                print(f"[LinkedIn] Posting to personal profile: {author_urn}")
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Check if we have media (image or video)
                has_media = video_url or image_url
                
                if has_media and video_url:
                    # VIDEO POST - use video upload flow
                    print(f"[LinkedIn] Creating video post...")
                    register_response = await client.post(
                        "https://api.linkedin.com/v2/assets?action=registerUpload",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0"
                        },
                        json={
                            "registerUploadRequest": {
                                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                                "owner": author_urn,
                                "serviceRelationships": [{
                                    "relationshipType": "OWNER",
                                    "identifier": "urn:li:userGeneratedContent"
                                }]
                            }
                        }
                    )
                    register_response.raise_for_status()
                    upload_data = register_response.json()
                    upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    asset = upload_data["value"]["asset"]
                    
                    # Download and upload video
                    video_response = await client.get(video_url)
                    video_response.raise_for_status()
                    
                    await client.put(
                        upload_url,
                        content=video_response.content,
                        headers={"Content-Type": "application/octet-stream"}
                    )
                    
                    # Create video post
                    post_response = await client.post(
                        "https://api.linkedin.com/v2/ugcPosts",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0"
                        },
                        json={
                            "author": author_urn,
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": {"text": caption},
                                    "shareMediaCategory": "VIDEO",
                                    "media": [{
                                        "status": "READY",
                                        "media": asset,
                                        "title": {"text": caption[:200] if caption else "Video Post"}
                                    }]
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }
                    )
                    
                elif has_media and image_url:
                    # IMAGE POST - use image upload flow
                    print(f"[LinkedIn] Creating image post...")
                    
                    # Register image upload
                    register_response = await client.post(
                        "https://api.linkedin.com/v2/assets?action=registerUpload",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0"
                        },
                        json={
                            "registerUploadRequest": {
                                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                                "owner": author_urn,
                                "serviceRelationships": [{
                                    "relationshipType": "OWNER",
                                    "identifier": "urn:li:userGeneratedContent"
                                }]
                            }
                        }
                    )
                    register_response.raise_for_status()
                    upload_data = register_response.json()
                    upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                    asset = upload_data["value"]["asset"]
                    
                    # Get image content (from URL or base64)
                    if image_url.startswith("data:image"):
                        # Base64 image
                        import re
                        match = re.match(r'data:image/\w+;base64,(.+)', image_url)
                        if match:
                            image_content = base64.b64decode(match.group(1))
                        else:
                            raise Exception("Invalid base64 image format")
                    else:
                        # URL
                        img_response = await client.get(image_url)
                        img_response.raise_for_status()
                        image_content = img_response.content
                    
                    # Upload image
                    upload_response = await client.put(
                        upload_url,
                        content=image_content,
                        headers={"Content-Type": "image/png"}
                    )
                    print(f"[LinkedIn] Image upload status: {upload_response.status_code}")
                    
                    # Create image post
                    post_response = await client.post(
                        "https://api.linkedin.com/v2/ugcPosts",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0"
                        },
                        json={
                            "author": author_urn,
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": {"text": caption},
                                    "shareMediaCategory": "IMAGE",
                                    "media": [{
                                        "status": "READY",
                                        "media": asset,
                                        "title": {"text": caption[:100] if caption else "Image Post"}
                                    }]
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }
                    )
                else:
                    # TEXT-ONLY POST
                    print(f"[LinkedIn] Creating text-only post...")
                    post_response = await client.post(
                        "https://api.linkedin.com/v2/ugcPosts",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": "application/json",
                            "X-Restli-Protocol-Version": "2.0.0"
                        },
                        json={
                            "author": author_urn,
                            "lifecycleState": "PUBLISHED",
                            "specificContent": {
                                "com.linkedin.ugc.ShareContent": {
                                    "shareCommentary": {"text": caption},
                                    "shareMediaCategory": "NONE"
                                }
                            },
                            "visibility": {
                                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                            }
                        }
                    )
                
                # Handle response
                if post_response.status_code not in [200, 201]:
                    error_text = post_response.text
                    print(f"[LinkedIn] Post failed: {post_response.status_code} - {error_text}")
                    return {
                        "success": False,
                        "error": f"LinkedIn API error: {post_response.status_code} - {error_text}",
                        "platform": "linkedin"
                    }
                
                post_data = post_response.json()
                post_id = post_data.get("id", "")
                
                # Generate post URL based on author type
                if "organization" in author_urn:
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                else:
                    post_url = f"https://www.linkedin.com/feed/update/{post_id}/"
                
                print(f"[LinkedIn] ✓ Post created successfully: {post_url}")
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "post_url": post_url,
                    "postUrl": post_url,  # Alias for frontend compatibility
                    "platform": "linkedin"
                }
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
            print(f"[LinkedIn] HTTP Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "platform": "linkedin"
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "platform": "linkedin"
            }
    
    async def post_to_linkedin_company(
        self,
        access_token: str,
        caption: str,
        image_url: str = None,
        image_base64: str = None
    ) -> Dict:
        """
        Simplified method to post to the configured LinkedIn company page
        
        Args:
            access_token: LinkedIn access token with w_organization_social scope
            caption: Post text content
            image_url: URL of image to include (optional)
            image_base64: Base64 encoded image (optional, used if image_url not provided)
            
        Returns:
            Dict with post result
        """
        # Use base64 image if URL not provided
        img = image_url or (f"data:image/png;base64,{image_base64}" if image_base64 else None)
        
        return await self.post_to_linkedin(
            access_token=access_token,
            caption=caption,
            image_url=img,
            use_company_page=True
        )
    
    async def post_to_x(
        self,
        access_token: str,
        video_url: str,
        caption: str
    ) -> Dict:
        """
        Post video to X (Twitter)
        
        Args:
            access_token: X access token
            video_url: URL to the video file
            caption: Tweet text
            
        Returns:
            Dict with post_id and post_url
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # X API v2 for posting videos requires media upload
                # This is a simplified version - full implementation requires chunked upload
                
                # For now, post as a tweet with video URL
                # In production, you'd need to implement media upload API
                tweet_response = await client.post(
                    "https://api.twitter.com/2/tweets",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "text": f"{caption}\n\n{video_url}"
                    }
                )
                tweet_response.raise_for_status()
                tweet_data = tweet_response.json()["data"]
                
                return {
                    "success": True,
                    "post_id": tweet_data["id"],
                    "post_url": f"https://twitter.com/i/web/status/{tweet_data['id']}",
                    "platform": "x"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "x"
            }
    
    async def post_to_tiktok(
        self,
        access_token: str,
        video_url: str,
        caption: str
    ) -> Dict:
        """
        Post video to TikTok
        
        Args:
            access_token: TikTok access token
            video_url: URL to the video file
            caption: Video caption
            
        Returns:
            Dict with post_id and post_url
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Download video
                video_response = await client.get(video_url)
                video_response.raise_for_status()
                video_content = video_response.content
                
                # TikTok requires multipart form upload
                files = {
                    "video": ("video.mp4", video_content, "video/mp4")
                }
                data = {
                    "post_info": f'{{"title": "{caption}", "privacy_level": "PUBLIC_TO_EVERYONE", "disable_duet": false, "disable_comment": false, "disable_stitch": false, "video_cover_timestamp_ms": 1000}}'
                }
                
                upload_response = await client.post(
                    "https://open.tiktokapis.com/v2/post/publish/video/init/",
                    headers={
                        "Authorization": f"Bearer {access_token}"
                    },
                    files=files,
                    data=data
                )
                upload_response.raise_for_status()
                upload_data = upload_response.json()["data"]
                
                return {
                    "success": True,
                    "post_id": upload_data.get("publish_id", ""),
                    "post_url": f"https://www.tiktok.com/@user/video/{upload_data.get('publish_id', '')}",
                    "platform": "tiktok"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "tiktok"
            }
































