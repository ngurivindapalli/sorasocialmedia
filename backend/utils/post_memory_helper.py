"""
Post Memory Helper - Utilities for saving and retrieving posts from Memory Service
Tracks post history, performance, and uses that context for future posts
"""

import json
from typing import Dict, Optional, List
from datetime import datetime


async def save_post_to_memory(
    memory_service=None,
    user_id: str = "",
    post_data: Dict = None,
    collection: str = "user_posts"
) -> Optional[str]:
    """
    Save a post to Memory Service with structured metadata
    
    Args:
        memory_service: MemoryService instance
        user_id: User identifier
        post_data: Dictionary containing post information
        collection: Collection name (not used with MemoryService, kept for compatibility)
    
    Returns:
        Resource ID if successful, None otherwise
    """
    if not memory_service or not hasattr(memory_service, 'is_available') or not memory_service.is_available():
        print("[PostMemory] Memory service not available, skipping post save")
        return None
    
    if not post_data:
        post_data = {}
    
    try:
        # Format post data as structured JSON
        post_memory = {
            "type": "marketing_post",
            "user_id": user_id,
            "topic": post_data.get("topic", ""),
            "caption": post_data.get("caption", ""),
            "hashtags": post_data.get("hashtags", []),
            "image_prompt": post_data.get("image_prompt", ""),
            "image_url": post_data.get("image_url"),
            "created_at": post_data.get("created_at", datetime.now().isoformat()),
            "post_id": post_data.get("post_id"),
            "post_url": post_data.get("post_url"),
            "is_first_post": post_data.get("is_first_post", False),
            "performance": post_data.get("performance", {}),
            "caption_style": post_data.get("caption_style", "engaging"),
            "aspect_ratio": post_data.get("aspect_ratio", "1:1")
        }
        
        # Create a searchable text representation
        memory_text = f"""Marketing Post - {post_data.get('topic', 'Unknown Topic')}
User ID: {user_id}

Caption: {post_data.get('caption', '')}
Hashtags: {', '.join(post_data.get('hashtags', []))}
Image Prompt: {post_data.get('image_prompt', '')}
Created: {post_data.get('created_at', datetime.now().isoformat())}
Post ID: {post_data.get('post_id', 'N/A')}
Is First Post: {post_data.get('is_first_post', False)}

Performance Metrics:
{json.dumps(post_data.get('performance', {}), indent=2)}
"""
        
        # Save to Memory Service
        result = await memory_service.add_text_memory(
            user_id=user_id,
            text=memory_text
        )
        
        if result:
            print(f"[PostMemory] ✓ Post saved to memory")
            return str(result) if result else None
        else:
            print(f"[PostMemory] ⚠️ Failed to save post to memory")
            return None
            
    except Exception as e:
        print(f"[PostMemory] Error saving post to memory: {e}")
        return None


async def is_first_post(memory_service=None, user_id: str = "") -> bool:
    """
    Check if this is the user's first marketing post
    
    Args:
        memory_service: MemoryService instance
        user_id: User identifier
    
    Returns:
        True if no previous posts found, False otherwise
    """
    if not memory_service or not hasattr(memory_service, 'is_available') or not memory_service.is_available():
        return False
    
    try:
        # Query for any previous posts by this user
        results = await memory_service.query_memories(
            user_id=user_id,
            query=f"marketing post user_id {user_id}",
            max_results=1
        )
        
        return len(results) == 0
        
    except Exception as e:
        print(f"[PostMemory] Error checking first post: {e}")
        return False


async def get_post_history_from_memory(
    memory_service=None,
    user_id: str = "",
    query: str = "marketing posts",
    max_results: int = 10
) -> List[Dict]:
    """
    Get post history for a user from Memory Service
    
    Args:
        memory_service: MemoryService instance (or hyperspell_service for backward compatibility)
        user_id: User identifier
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        List of post data dictionaries
    """
    # Handle both memory_service and hyperspell_service for backward compatibility
    service = memory_service
    if not service or not hasattr(service, 'is_available') or not service.is_available():
        print("[PostMemory] Memory service not available")
        return []
    
    try:
        # Query memories for posts
        results = await service.query_memories(
            user_id=user_id,
            query=query,
            max_results=max_results
        )
        
        # Parse results into post data
        posts = []
        for memory in results:
            try:
                # Try to extract structured data from memory
                if isinstance(memory, dict):
                    if 'metadata' in memory:
                        posts.append(memory['metadata'])
                    else:
                        posts.append(memory)
                elif hasattr(memory, 'metadata'):
                    posts.append(memory.metadata)
            except Exception:
                continue
        
        print(f"[PostMemory] ✓ Retrieved {len(posts)} posts from memory")
        return posts
        
    except Exception as e:
        print(f"[PostMemory] Error getting post history: {e}")
        return []


async def get_post_performance_context(
    memory_service=None,
    hyperspell_service=None,
    user_id: str = ""
) -> str:
    """
    Get context about previous posts and their performance for generating new posts
    
    Args:
        memory_service: MemoryService instance (preferred)
        hyperspell_service: For backward compatibility (deprecated)
        user_id: User identifier
    
    Returns:
        Formatted context string about post history and performance
    """
    # Use memory_service if provided, fall back to hyperspell_service
    service = memory_service or hyperspell_service
    if not service or not hasattr(service, 'is_available') or not service.is_available():
        return ""
    
    try:
        # Get post history for this specific user
        posts = await get_post_history_from_memory(
            memory_service=service,
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
                views = performance.get("views", 0)
                likes = performance.get("likes", 0)
                engagement_rate = performance.get("engagement_rate", 0)
                
                if engagement_rate > 0.05 or (views > 1000 and likes > 50):
                    high_performing_posts.append(post)
                elif engagement_rate < 0.01 or (views < 100 and likes < 5):
                    low_performing_posts.append(post)
        
        # Build context string
        context_parts = [f"POST HISTORY ({total_posts} previous posts):"]
        
        if high_performing_posts:
            context_parts.append("\nHIGH PERFORMING POSTS (learn from these):")
            for post in high_performing_posts[:3]:
                perf = post.get("performance", {})
                context_parts.append(f"- Topic: {post.get('topic', 'Unknown')}")
                context_parts.append(f"  Caption style: {post.get('caption_style', 'engaging')}")
                context_parts.append(f"  Performance: {perf.get('views', 0)} views, {perf.get('likes', 0)} likes")
        
        if low_performing_posts:
            context_parts.append("\nLOW PERFORMING POSTS (avoid these patterns):")
            for post in low_performing_posts[:2]:
                context_parts.append(f"- Topic: {post.get('topic', 'Unknown')}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"[PostMemory] Error getting performance context: {e}")
        return ""


async def find_existing_post_with_image(
    memory_service=None,
    user_id: str = "",
    topic: str = ""
) -> Optional[Dict]:
    """
    Find an existing post with similar topic that has an image
    
    Args:
        memory_service: MemoryService instance
        user_id: User identifier
        topic: Topic to search for
    
    Returns:
        Post data dictionary if found, None otherwise
    """
    if not memory_service or not hasattr(memory_service, 'is_available') or not memory_service.is_available():
        return None
    
    try:
        # Search for posts with similar topic
        results = await memory_service.query_memories(
            user_id=user_id,
            query=f"marketing post {topic} image",
            max_results=5
        )
        
        for memory in results:
            if isinstance(memory, dict) and memory.get('image_url'):
                return memory
            elif hasattr(memory, 'metadata') and memory.metadata.get('image_url'):
                return memory.metadata
        
        return None
        
    except Exception as e:
        print(f"[PostMemory] Error finding existing post: {e}")
        return None
