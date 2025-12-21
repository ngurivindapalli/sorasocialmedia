"""
Hyperspell Helper - Reusable utility for integrating Hyperspell memory context
into any endpoint or service
"""
from typing import Optional
from services.hyperspell_service import HyperspellService


async def get_hyperspell_context(
    hyperspell_service: HyperspellService,
    query: str,
    user_email: Optional[str] = None
) -> str:
    """
    Get Hyperspell memory context for any query.
    This is a reusable helper that can be called from any endpoint.
    
    Args:
        hyperspell_service: The HyperspellService instance
        query: Query string to search memories (e.g., topic, user input, context)
        user_email: User email to query their specific memories
        
    Returns:
        Formatted context string from Hyperspell, or empty string if unavailable
    """
    if not hyperspell_service or not hyperspell_service.is_available():
        print(f"[Hyperspell] Service not available")
        return ""
    
    if not user_email:
        print(f"[Hyperspell] No user email provided, skipping query")
        return ""
    
    try:
        user_id = user_email
        query_text = query.strip() if query else "all documents and memories"
        
        print(f"[Hyperspell] Querying memories for user: {user_id}")
        print(f"[Hyperspell] Query: {query_text[:100]}...")
        
        context = await hyperspell_service.get_context_summary(user_id, query_text)
        
        if context and len(context.strip()) > 0:
            print(f"[Hyperspell] ✓ Retrieved context ({len(context)} chars)")
            print(f"[Hyperspell] Context preview: {context[:200]}...")
            return context
        else:
            print(f"[Hyperspell] ⚠️ No relevant memories found for query: {query_text[:50]}...")
            return ""
            
    except Exception as e:
        print(f"[Hyperspell] ⚠️ Error querying memories (non-critical): {e}")
        import traceback
        traceback.print_exc()
        return ""







