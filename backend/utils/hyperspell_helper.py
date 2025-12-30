"""
Memory Helper - Reusable utility for integrating memory context from S3 + Mem0
into any endpoint or service
"""
from typing import Optional
from services.memory_service import MemoryService


async def get_memory_context(
    memory_service: MemoryService,
    query: str,
    user_email: Optional[str] = None
) -> str:
    """
    Get memory context for any query using MemoryService (S3 + Mem0).
    This is a reusable helper that can be called from any endpoint.
    
    Args:
        memory_service: The MemoryService instance (S3 + Mem0)
        query: Query string to search memories (e.g., topic, user input, context)
        user_email: User email to query their specific memories
        
    Returns:
        Formatted context string from memory service, or empty string if unavailable
    """
    if not memory_service or not memory_service.is_available():
        print(f"[Memory] Service not available")
        return ""
    
    if not user_email:
        print(f"[Memory] No user email provided, skipping query")
        return ""
    
    try:
        user_id = user_email
        query_text = query.strip() if query else "all documents and memories"
        
        print(f"[Memory] Querying memories from Mem0 for user: {user_id}")
        print(f"[Memory] Query: {query_text[:100]}...")
        
        # Try get_context_summary first (more specific)
        context = await memory_service.get_context_summary(user_id, query_text)
        
        # If no context found, try get_all_memories as fallback (broader search)
        if not context or len(context.strip()) == 0:
            print(f"[Memory] No context from get_context_summary, trying get_all_memories...")
            if hasattr(memory_service, 'get_all_memories'):
                context = await memory_service.get_all_memories(user_id)
        
        if context and len(context.strip()) > 0:
            print(f"[Memory] OK Retrieved context from Mem0 ({len(context)} chars)")
            print(f"[Memory] Context preview: {context[:200]}...")
            return context
        else:
            print(f"[Memory] WARNING: No relevant memories found for query: {query_text[:50]}...")
            return ""
            
    except Exception as e:
        print(f"[Memory] WARNING: Error querying memories from Mem0 (non-critical): {e}")
        import traceback
        traceback.print_exc()
        return ""


# Alias for backwards compatibility
get_hyperspell_context = get_memory_context







