"""
Post Memory Helper - Utilities for saving and retrieving posts from Hyperspell memory
Tracks post history, performance, and uses that context for future posts
"""

import json
from typing import Dict, Optional, List
from datetime import datetime
from services.hyperspell_service import HyperspellService


async def save_post_to_memory(
    hyperspell_service: HyperspellService,
    user_id: str,
    post_data: Dict,
    collection: str = "user_posts"
) -> Optional[str]:
    """
    Save a post to Hyperspell memory with structured metadata
    
    Args:
        hyperspell_service: HyperspellService instance
        user_id: User identifier
        post_data: Dictionary containing post information:
            - topic: Post topic
            - caption: Post caption
            - hashtags: List of hashtags
            - image_prompt: Image prompt used
            - created_at: Timestamp
            - post_id: Optional post ID from platform
            - post_url: Optional post URL
            - is_first_post: Whether this is the user's first post
            - performance: Optional performance metrics (views, likes, engagement_rate)
    
    Returns:
        Resource ID if successful, None otherwise
    """
    if not hyperspell_service.is_available():
        print("[PostMemory] Hyperspell not available, skipping post save")
        return None
    
    try:
        # Format post data as structured JSON for Hyperspell
        post_memory = {
            "type": "marketing_post",
            "user_id": user_id,
            "topic": post_data.get("topic", ""),
            "caption": post_data.get("caption", ""),
            "hashtags": post_data.get("hashtags", []),
            "image_prompt": post_data.get("image_prompt", ""),
            "created_at": post_data.get("created_at", datetime.now().isoformat()),
            "post_id": post_data.get("post_id"),
            "post_url": post_data.get("post_url"),
            "is_first_post": post_data.get("is_first_post", False),
            "performance": post_data.get("performance", {}),
            "caption_style": post_data.get("caption_style", "engaging"),
            "aspect_ratio": post_data.get("aspect_ratio", "1:1")
        }
        
        # Create a searchable text representation
        # Include user_id prominently for filtering
        memory_text = f"""Marketing Post - {post_data.get('topic', 'Unknown Topic')}
User ID: {user_id}

Caption: {post_data.get('caption', '')}
Hashtags: {', '.join(post_data.get('hashtags', []))}
Image Prompt: {post_data.get('image_prompt', '')}
Created: {post_data.get('created_at', datetime.now().isoformat())}
Post ID: {post_data.get('post_id', 'N/A')}
Post URL: {post_data.get('post_url', 'N/A')}
Is First Post: {post_data.get('is_first_post', False)}

Performance Metrics:
{json.dumps(post_data.get('performance', {}), indent=2)}

Full Metadata:
{json.dumps(post_memory, indent=2)}
"""
        
        # Save to Hyperspell
        result = await hyperspell_service.add_text_memory(
            user_id=user_id,
            text=memory_text,
            collection=collection
        )
        
        if result:
            print(f"[PostMemory] ✓ Post saved to Hyperspell memory: {result.get('resource_id')}")
            return result.get('resource_id')
        else:
            print(f"[PostMemory] ⚠️ Failed to save post to Hyperspell")
            return None
            
    except Exception as e:
        print(f"[PostMemory] Error saving post to memory: {e}")
        import traceback
        traceback.print_exc()
        return None


async def get_post_history_from_memory(
    hyperspell_service: HyperspellService,
    user_id: str,
    query: str = "marketing posts history",
    max_results: int = 10
) -> List[Dict]:
    """
    Retrieve post history from Hyperspell memory
    
    Args:
        hyperspell_service: HyperspellService instance
        user_id: User identifier
        query: Search query for posts
        max_results: Maximum number of posts to retrieve
    
    Returns:
        List of post dictionaries with metadata
    """
    if not hyperspell_service.is_available():
        return []
    
    try:
        # Include user_id in query to filter posts for this specific user
        # Since all memories are in one account, we need to filter by user_id in the text
        user_specific_query = f"{query} user_id {user_id}"
        
        # Search for posts in Hyperspell
        search_result = await hyperspell_service.query_memories(
            user_id=user_id,
            query=user_specific_query,
            max_results=max_results
        )
        
        if not search_result:
            return []
        
        # Parse results - extract post information
        posts = []
        results = search_result.get("results", [])
        
        for result in results:
            if isinstance(result, dict):
                # Try to extract post data from result
                content = result.get("content", result.get("text", result.get("snippet", "")))
                
                # Filter by user_id - only include posts that match this user
                if f'"user_id": "{user_id}"' not in content and f'"user_id": "{user_id}"' not in content.replace(' ', ''):
                    # Also check for user_id in the text format
                    if f"user_id {user_id}" not in content.lower():
                        continue  # Skip posts from other users
                
                # Try to parse JSON metadata if present
                try:
                    # Look for JSON in the content
                    if "Full Metadata:" in content:
                        json_start = content.find("{", content.find("Full Metadata:"))
                        if json_start != -1:
                            json_end = content.rfind("}") + 1
                            if json_end > json_start:
                                metadata_str = content[json_start:json_end]
                                metadata = json.loads(metadata_str)
                                # Double-check user_id matches
                                if metadata.get("user_id") == user_id:
                                    posts.append(metadata)
                                continue
                except:
                    pass
                
                # Fallback: extract basic info from text
                post_data = {
                    "topic": "",
                    "caption": "",
                    "created_at": "",
                    "performance": {}
                }
                
                # Extract topic
                if "Marketing Post -" in content:
                    topic_start = content.find("Marketing Post -") + len("Marketing Post -")
                    topic_end = content.find("\n", topic_start)
                    if topic_end != -1:
                        post_data["topic"] = content[topic_start:topic_end].strip()
                
                # Extract caption
                if "Caption:" in content:
                    caption_start = content.find("Caption:") + len("Caption:")
                    caption_end = content.find("\n", caption_start)
                    if caption_end != -1:
                        post_data["caption"] = content[caption_start:caption_end].strip()
                
                # Extract performance
                if "Performance Metrics:" in content:
                    perf_start = content.find("Performance Metrics:") + len("Performance Metrics:")
                    perf_end = content.find("\n\n", perf_start)
                    if perf_end == -1:
                        perf_end = content.find("Full Metadata:", perf_start)
                    if perf_end != -1:
                        perf_text = content[perf_start:perf_end].strip()
                        try:
                            post_data["performance"] = json.loads(perf_text)
                        except:
                            pass
                
                posts.append(post_data)
        
        print(f"[PostMemory] ✓ Retrieved {len(posts)} posts from Hyperspell memory")
        return posts
        
    except Exception as e:
        print(f"[PostMemory] Error retrieving post history: {e}")
        import traceback
        traceback.print_exc()
        return []


async def is_first_post(
    hyperspell_service: HyperspellService,
    user_id: str
) -> bool:
    """
    Check if this is the user's first post
    
    Args:
        hyperspell_service: HyperspellService instance
        user_id: User identifier
    
    Returns:
        True if this is the first post, False otherwise
    """
    if not hyperspell_service.is_available():
        return True  # Assume first post if Hyperspell not available
    
    try:
        # Search for any previous posts for this specific user
        # Include user_id in query to filter
        search_result = await hyperspell_service.query_memories(
            user_id=user_id,
            query=f"marketing posts history first post user_id {user_id}",
            max_results=5
        )
        
        # If no results or empty results, it's the first post
        if not search_result or not search_result.get("results"):
            print(f"[PostMemory] ✓ This is the first post for user: {user_id}")
            return True
        
        # Filter results to only include posts from this user
        results = search_result.get("results", [])
        user_posts = []
        
        for result in results:
            if isinstance(result, dict):
                content = result.get("content", result.get("text", ""))
                # Check if this post belongs to this user
                if f'"user_id": "{user_id}"' in content or f"user_id {user_id}" in content.lower():
                    user_posts.append(result)
        
        # If no posts found for this user, it's the first post
        if len(user_posts) == 0:
            print(f"[PostMemory] ✓ This is the first post for user: {user_id}")
            return True
        
        # Check if any result indicates a first post
        for result in user_posts:
            content = result.get("content", result.get("text", ""))
            if "Is First Post: True" in content or "is_first_post: true" in content.lower():
                # Found a first post, so this is not the first
                print(f"[PostMemory] Previous posts found, this is not the first post")
                return False
        
        # If we found posts for this user, it's not the first
        print(f"[PostMemory] Previous posts found ({len(user_posts)}), this is not the first post")
        return False
        
    except Exception as e:
        print(f"[PostMemory] Error checking if first post: {e}")
        # On error, assume it's the first post to be safe
        return True


async def get_post_performance_context(
    hyperspell_service: HyperspellService,
    user_id: str
) -> str:
    """
    Get context about previous posts and their performance for generating new posts
    
    Args:
        hyperspell_service: HyperspellService instance
        user_id: User identifier
    
    Returns:
        Formatted context string about post history and performance
    """
    if not hyperspell_service.is_available():
        return ""
    
    try:
        # Get post history for this specific user
        posts = await get_post_history_from_memory(
            hyperspell_service=hyperspell_service,
            user_id=user_id,
            query=f"marketing posts performance engagement user_id {user_id}",
            max_results=10
        )
        
        if not posts:
            return ""
        
        # Analyze performance
        high_performing_posts = []
        low_performing_posts = []
        total_posts = len(posts)
        
        for post in posts:
            performance = post.get("performance", {})
            if performance:
                # Determine if post performed well
                views = performance.get("views", 0)
                likes = performance.get("likes", 0)
                engagement_rate = performance.get("engagement_rate", 0)
                
                # Simple heuristic: high engagement rate or high absolute numbers
                if engagement_rate > 0.05 or (views > 1000 and likes > 50):
                    high_performing_posts.append(post)
                elif engagement_rate < 0.01 or (views < 100 and likes < 5):
                    low_performing_posts.append(post)
        
        # Build context string
        context_parts = []
        context_parts.append("POST HISTORY & PERFORMANCE CONTEXT:")
        context_parts.append(f"Total posts created: {total_posts}")
        context_parts.append(f"High-performing posts: {len(high_performing_posts)}")
        context_parts.append(f"Low-performing posts: {len(low_performing_posts)}")
        context_parts.append("")
        
        if high_performing_posts:
            context_parts.append("HIGH-PERFORMING POSTS (learn from these):")
            for i, post in enumerate(high_performing_posts[:3], 1):  # Top 3
                context_parts.append(f"{i}. Topic: {post.get('topic', 'N/A')}")
                context_parts.append(f"   Caption: {post.get('caption', '')[:100]}...")
                perf = post.get('performance', {})
                if perf:
                    context_parts.append(f"   Performance: {perf.get('views', 0)} views, {perf.get('likes', 0)} likes, {perf.get('engagement_rate', 0)*100:.1f}% engagement")
                context_parts.append("")
        
        if low_performing_posts:
            context_parts.append("LOW-PERFORMING POSTS (avoid similar approaches):")
            for i, post in enumerate(low_performing_posts[:2], 1):  # Top 2
                context_parts.append(f"{i}. Topic: {post.get('topic', 'N/A')}")
                context_parts.append(f"   Caption: {post.get('caption', '')[:100]}...")
                perf = post.get('performance', {})
                if perf:
                    context_parts.append(f"   Performance: {perf.get('views', 0)} views, {perf.get('likes', 0)} likes, {perf.get('engagement_rate', 0)*100:.1f}% engagement")
                context_parts.append("")
        
        # Extract patterns from high-performing posts
        if high_performing_posts:
            context_parts.append("PATTERNS FROM HIGH-PERFORMING POSTS:")
            topics = [p.get('topic', '') for p in high_performing_posts]
            styles = [p.get('caption_style', '') for p in high_performing_posts]
            hashtags = []
            for p in high_performing_posts:
                hashtags.extend(p.get('hashtags', []))
            
            if topics:
                context_parts.append(f"- Successful topics: {', '.join(set(topics[:5]))}")
            if styles:
                context_parts.append(f"- Successful styles: {', '.join(set(styles))}")
            if hashtags:
                top_hashtags = list(set(hashtags))[:10]
                context_parts.append(f"- Effective hashtags: {', '.join(top_hashtags)}")
        
        context = "\n".join(context_parts)
        print(f"[PostMemory] ✓ Generated post performance context ({len(context)} chars)")
        return context
        
    except Exception as e:
        print(f"[PostMemory] Error generating performance context: {e}")
        return ""

