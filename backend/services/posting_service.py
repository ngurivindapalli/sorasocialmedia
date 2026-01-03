import httpx
from typing import Dict, Optional
from datetime import datetime, timedelta


class PostingService:
    """Service for posting videos to social media platforms"""
    
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
        video_url: str,
        caption: str,
        person_urn: str
    ) -> Dict:
        """
        Post video to LinkedIn
        
        Args:
            access_token: LinkedIn access token
            video_url: URL to the video file
            caption: Post caption
            person_urn: LinkedIn person URN (e.g., "urn:li:person:xxxxx")
            
        Returns:
            Dict with post_id and post_url
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Step 1: Register upload
                register_response = await client.post(
                    "https://api.linkedin.com/v2/assets?action=registerUpload",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "registerUploadRequest": {
                            "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                            "owner": person_urn,
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
                
                # Step 2: Upload video
                # Download video first
                video_response = await client.get(video_url)
                video_response.raise_for_status()
                video_content = video_response.content
                
                upload_video_response = await client.put(
                    upload_url,
                    content=video_content,
                    headers={"Content-Type": "application/octet-stream"}
                )
                upload_video_response.raise_for_status()
                
                # Step 3: Create post
                post_response = await client.post(
                    "https://api.linkedin.com/v2/ugcPosts",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "author": person_urn,
                        "lifecycleState": "PUBLISHED",
                        "specificContent": {
                            "com.linkedin.ugc.ShareContent": {
                                "shareCommentary": {
                                    "text": caption
                                },
                                "shareMediaCategory": "VIDEO",
                                "media": [{
                                    "status": "READY",
                                    "media": asset,
                                    "title": {
                                        "text": caption[:200]
                                    }
                                }]
                            }
                        },
                        "visibility": {
                            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                        }
                    }
                )
                post_response.raise_for_status()
                post_data = post_response.json()
                
                return {
                    "success": True,
                    "post_id": post_data["id"],
                    "post_url": f"https://www.linkedin.com/feed/update/{post_data['id']}/",
                    "platform": "linkedin"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "platform": "linkedin"
            }
    
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































