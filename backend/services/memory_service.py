"""
Unified Memory Service - Combines S3 (documents) + Mem0 (memory)
Drop-in replacement for HyperspellService
"""

from typing import Optional, Dict
from services.s3_service import S3Service
from services.mem0_service import Mem0Service
from datetime import datetime
import asyncio


class MemoryService:
    """
    Unified service that combines S3 for document storage and Mem0 for memory management.
    Provides the same interface as HyperspellService for easy migration.
    """
    
    def __init__(self):
        """Initialize both S3 and Mem0 services"""
        self.s3_service = S3Service()
        self.mem0_service = Mem0Service()
        
        # Service is available if at least S3 works (Mem0 may fail but S3 can still store documents)
        s3_available = self.s3_service.is_available()
        mem0_available = self.mem0_service.is_available()
        self.available = s3_available or mem0_available
        
        if self.available:
            status = []
            if s3_available:
                status.append("S3")
            if mem0_available:
                status.append("Mem0")
            else:
                status.append("Mem0 (unavailable)")
            print(f"[Memory] OK Unified memory service initialized ({' + '.join(status)})")
        else:
            print("[Memory] WARNING: Neither S3 nor Mem0 available. Check configuration.")
    
    def is_available(self) -> bool:
        """Check if service is available"""
        return self.available
    
    # Document storage methods (using S3)
    async def upload_document(
        self,
        user_id: str,
        file_path: str,
        filename: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Upload a document to S3 (replaces Hyperspell document upload)
        
        Args:
            user_id: User identifier
            file_path: Local file path
            filename: Original filename
            
        Returns:
            Dict with upload info (resource_id, filename) or None if failed
        """
        if not self.s3_service.is_available():
            print("[Memory] S3 service not available for document upload")
            return None
        
        try:
            # Generate S3 key
            s3_key = self.s3_service.get_s3_path(user_id, filename or "document", "documents")
            
            # Upload to S3
            result = await self.s3_service.upload_file(
                file_path=file_path,
                s3_key=s3_key,
                metadata={'user_id': user_id, 'filename': filename or 'document'}
            )
            
            if result:
                return {
                    'resource_id': result.get('key'),  # Use S3 key as resource_id
                    'filename': filename or 'document',
                    's3_key': result.get('key'),
                    's3_bucket': result.get('bucket'),
                    'uploaded_at': result.get('uploaded_at')
                }
            return None
            
        except Exception as e:
            print(f"[Memory] ERROR: Error uploading document: {e}")
            return None
    
    # Memory management methods (using Mem0)
    async def add_text_memory(
        self,
        user_id: str,
        text: str,
        collection: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Add a text memory to Mem0 (replaces Hyperspell add_text_memory)
        
        Args:
            user_id: User identifier
            text: Text content
            collection: Collection name (stored as metadata)
            
        Returns:
            Dict with memory info (resource_id) or None if failed
        """
        if not self.mem0_service.is_available():
            print("[Memory] Mem0 service not available for adding memory")
            return None
        
        metadata = {}
        if collection:
            metadata['collection'] = collection
        
        return await self.mem0_service.add_memory(user_id, text, metadata)
    
    async def query_memories(
        self,
        user_id: str,
        query: str,
        max_results: int = 5
    ) -> Optional[Dict]:
        """
        Query memories using Mem0 (replaces Hyperspell query_memories)
        
        Args:
            user_id: User identifier
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            Dict with query results (answer, memories) or None if failed
        """
        if not self.mem0_service.is_available():
            print("[Memory] Mem0 service not available for querying")
            return None
        
        return await self.mem0_service.search_memories(user_id, query, max_results)
    
    async def get_all_memories_context(self, user_id: str) -> str:
        """
        Get all memories as context string (replaces Hyperspell get_all_memories_context)
        
        Args:
            user_id: User identifier
            
        Returns:
            Combined context string from all memories
        """
        if not self.mem0_service.is_available():
            return ""
        
        return await self.mem0_service.get_all_memories(user_id)
    
    async def append_to_unified_brand_context(
        self,
        user_id: str,
        new_content: str,
        content_type: str = "document"
    ) -> Optional[Dict]:
        """
        Append content to unified brand context (replaces Hyperspell append_to_unified_brand_context)
        
        Args:
            user_id: User identifier
            new_content: New content to append
            content_type: Type of content
            
        Returns:
            Dict with memory info (resource_id) or None if failed
        """
        if not self.mem0_service.is_available():
            print("[Memory] Mem0 service not available")
            return None
        
        try:
            # Get existing context
            existing_context = await self.get_all_memories_context(user_id)
            
            # Prepare new content section
            timestamp = datetime.now().isoformat()
            new_content_section = f"\n\n--- {content_type.upper()} ADDED: {timestamp} ---\n{new_content}\n"
            
            # Merge existing and new content
            if existing_context and len(existing_context.strip()) > 10:
                unified_content = existing_context + new_content_section
            else:
                unified_content = f"BRAND CONTEXT - UNIFIED MEMORY\n{new_content_section}"
            
            # Save as new memory with metadata
            metadata = {
                'collection': 'brand_context',
                'content_type': content_type,
                'is_unified': True
            }
            
            result = await self.mem0_service.add_memory(user_id, unified_content, metadata)
            
            if result:
                print(f"[Memory] OK Appended to unified brand context: {result.get('resource_id')}")
            
            return result
            
        except Exception as e:
            print(f"[Memory] ERROR: Error appending to unified brand context: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_context_summary(self, user_id: str, query: str) -> str:
        """
        Get context summary for a query with improved relevance (replaces Hyperspell get_context_summary)
        
        Args:
            user_id: User identifier (normalized internally)
            query: Query string for semantic search
            
        Returns:
            Context summary string optimized for AI prompts
        """
        if not self.mem0_service.is_available():
            return ""
        
        # Use higher limit for better context
        results = await self.query_memories(user_id, query, max_results=10)
        if results and results.get('answer'):
            answer = results['answer']
            # Ensure we have meaningful content
            if len(answer.strip()) > 20:
                print(f"[Memory] OK Retrieved context for query '{query[:50]}...' ({len(answer)} chars)")
                return answer
        return ""

