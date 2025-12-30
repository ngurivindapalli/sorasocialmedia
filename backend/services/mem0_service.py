"""
Mem0 Service - Memory and context management
Replaces Hyperspell memory functionality
"""

import os
from typing import Optional, Dict, List
from datetime import datetime
import asyncio

try:
    # The package is installed as 'mem0ai' but imported as 'mem0'
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("[Warning] Mem0 SDK not installed. Install with: pip install mem0ai")


class Mem0Service:
    """Service for interacting with Mem0 for memory and context management"""
    
    def __init__(self, vector_db: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize Mem0 service
        
        Args:
            vector_db: Vector database type (e.g., 's3_vectors', 'chroma', 'pinecone')
            config: Optional Mem0 configuration dict
        """
        self.available = False
        
        if not MEM0_AVAILABLE:
            print("[Mem0] SDK not available. Install with: pip install mem0ai")
            return
        
        try:
            # Default to ChromaDB (local) for simplicity - S3 vectors requires additional setup
            if vector_db is None:
                vector_db = 'chroma'  # Default to local ChromaDB
                print("[Mem0] Using ChromaDB as vector database (local)")
            
            # Configure persistent ChromaDB storage location
            # This ensures memories persist across backend restarts
            import os
            from pathlib import Path
            
            # Create persistent directory for ChromaDB in backend directory
            backend_dir = Path(__file__).parent.parent  # Go up from services/ to backend/
            chroma_persist_dir = backend_dir / "chroma_db"
            chroma_persist_dir.mkdir(exist_ok=True)
            
            # Set ChromaDB persistence directory
            chroma_persist_path = str(chroma_persist_dir.absolute())
            
            # Build config - simple ChromaDB config with persistent storage
            mem0_config = config or {}
            
            # Configure Mem0 with persistent ChromaDB
            if not mem0_config:
                # Use ChromaDB config with persistent directory
                mem0_config = {
                    "vector_store": {
                        "provider": "chroma",
                        "config": {
                            "collection_name": "mem0_memories",
                            "path": chroma_persist_path,  # Persistent storage location
                            "persist_directory": chroma_persist_path
                        }
                    }
                }
                print(f"[Mem0] Configuring ChromaDB with persistent storage: {chroma_persist_path}")
            
            # Initialize Mem0 with persistent config
            try:
                self.memory = Memory.from_config(mem0_config)
            except Exception as config_error:
                # Fallback: try simple initialization (Mem0 might handle persistence differently)
                print(f"[Mem0] WARNING: Config initialization failed, trying simple init: {config_error}")
                # Set environment variable for ChromaDB persistence
                os.environ['CHROMA_PERSIST_DIRECTORY'] = chroma_persist_path
                self.memory = Memory()
            
            self.available = True
            print(f"[Mem0] OK Mem0 service initialized with persistent storage (vector_db: {vector_db})")
            print(f"[Mem0] ChromaDB data will persist at: {chroma_persist_path}")
            
        except Exception as e:
            print(f"[Mem0] ERROR: Error initializing Mem0 service: {e}")
            import traceback
            traceback.print_exc()
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Mem0 service is available"""
        return self.available
    
    def _normalize_user_id(self, user_id: str) -> str:
        """Normalize user ID for consistency with Mem0 agent_id"""
        return user_id.lower().strip()
    
    async def add_memory(
        self,
        user_id: str,
        text: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Add a memory to Mem0
        
        Args:
            user_id: User identifier (email)
            text: Text content to store
            metadata: Optional metadata dictionary
            
        Returns:
            Dict with memory info (id, created_at) or None if failed
        """
        if not self.available:
            print("[Mem0] Service not available for adding memory")
            return None
        
        try:
            # Normalize user_id for consistency
            normalized_user_id = self._normalize_user_id(user_id)
            
            def add_sync():
                # Mem0 uses agent_id to scope memories per user
                result = self.memory.add(
                    messages=[{"role": "user", "content": text}],
                    agent_id=normalized_user_id,  # Use normalized ID
                    metadata=metadata or {}
                )
                return result
            
            result = await asyncio.to_thread(add_sync)
            
            # Mem0 returns a dict with 'results' array containing memory objects
            memory_ids = []
            if isinstance(result, dict):
                # Check for results array (Mem0 format)
                if 'results' in result and isinstance(result['results'], list):
                    memory_ids = [mem.get('id') for mem in result['results'] if isinstance(mem, dict) and 'id' in mem]
                    if memory_ids:
                        print(f"[Mem0] OK Memory added for user {normalized_user_id}: {len(memory_ids)} memories created (first ID: {memory_ids[0]})")
                # Fallback: check for direct id
                elif 'id' in result:
                    memory_ids = [result['id']]
                elif 'memory_id' in result:
                    memory_ids = [result['memory_id']]
            elif hasattr(result, 'id'):
                memory_ids = [result.id]
            
            # Use first memory ID or generate fallback
            if memory_ids:
                memory_id = memory_ids[0]
                print(f"[Mem0] OK Memory ID: {memory_id} for user {normalized_user_id}")
                return {
                    'resource_id': str(memory_id),
                    'user_id': normalized_user_id,
                    'added_at': datetime.now().isoformat(),
                    'text_preview': text[:100] + "..." if len(text) > 100 else text,
                    'verified': True,
                    'all_memory_ids': memory_ids  # Include all IDs if multiple were created
                }
            else:
                # Generate fallback ID
                fallback_id = f"mem0_{datetime.now().timestamp()}"
                print(f"[Mem0] WARNING: Memory added but no ID in expected format. Result type: {type(result)}")
                if isinstance(result, dict):
                    print(f"[Mem0] Result keys: {list(result.keys())}")
                print(f"[Mem0] Using fallback ID: {fallback_id}")
                return {
                    'resource_id': fallback_id,
                    'user_id': normalized_user_id,
                    'added_at': datetime.now().isoformat(),
                    'verified': False
                }
                
        except Exception as e:
            print(f"[Mem0] ERROR: Error adding memory: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> Optional[Dict]:
        """
        Search memories for a user with improved relevance
        
        Args:
            user_id: User identifier (will be normalized)
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dict with search results (memories, answer) or None if failed
        """
        if not self.available:
            print("[Mem0] Service not available for searching memories")
            return None
        
        # Normalize user_id for consistency (Mem0 uses agent_id)
        normalized_user_id = user_id.lower().strip()
        
        try:
            def search_sync():
                # Mem0 search with user-specific agent_id
                results = self.memory.search(
                    query=query,
                    agent_id=normalized_user_id,  # Ensure consistent user ID
                    limit=limit
                )
                return results
            
            results = await asyncio.to_thread(search_sync)
            
            # Format results - Mem0 returns list or dict
            memories = []
            if isinstance(results, list):
                memories = results
            elif isinstance(results, dict):
                # Check different possible keys
                memories = results.get('memories', []) or results.get('results', []) or []
                # If results dict contains memory objects directly
                if not memories and 'memory' in results:
                    memories = [results]
            
            # Extract and format memory content
            answer_parts = []
            for memory in memories:
                if isinstance(memory, dict):
                    # Extract memory content (Mem0 stores in 'memory' field)
                    content = memory.get('memory', '') or memory.get('content', '') or str(memory)
                    if content and content.strip():
                        answer_parts.append(content.strip())
                else:
                    content = str(memory).strip()
                    if content:
                        answer_parts.append(content)
            
            answer = "\n\n".join(answer_parts) if answer_parts else ""
            
            if memories:
                print(f"[Mem0] Found {len(memories)} relevant memories for user {normalized_user_id} (query: '{query[:50]}...')")
            
            return {
                'query': query,
                'answer': answer,
                'memories': memories,
                'count': len(memories),
                'user_id': normalized_user_id
            }
            
        except Exception as e:
            print(f"[Mem0] ERROR: Error searching memories for user {normalized_user_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def get_all_memories(self, user_id: str) -> str:
        """
        Get all memories for a user as a single context string
        Uses multiple query strategies to retrieve comprehensive context
        
        Args:
            user_id: User identifier (normalized to lowercase)
            
        Returns:
            Combined context string from all memories
        """
        if not self.available:
            return ""
        
        # Normalize user_id for consistency
        normalized_user_id = user_id.lower().strip()
        
        try:
            # Strategy: Use multiple semantic queries to get diverse memories
            queries = [
                "user background profession skills experience education",
                "brand company business products services",
                "documents uploaded content context",
                "*"  # Fallback: try to get all
            ]
            
            all_memories = []
            seen_ids = set()
            
            for query in queries:
                try:
                    results = await self.search_memories(normalized_user_id, query, limit=25)
                    
                    if results and results.get('memories'):
                        memories = results['memories']
                        for mem in memories:
                            if isinstance(mem, dict):
                                mem_id = mem.get('id') or mem.get('memory_id')
                                if mem_id and mem_id not in seen_ids:
                                    seen_ids.add(mem_id)
                                    all_memories.append(mem)
                    
                    # If we got results, we have enough context
                    if len(all_memories) >= 50:
                        break
                        
                except Exception as e:
                    print(f"[Mem0] Query '{query}' failed: {e}")
                    continue
            
            # Format all memories into context string
            if all_memories:
                context_parts = []
                for mem in all_memories:
                    if isinstance(mem, dict):
                        content = mem.get('memory', '') or mem.get('content', '') or str(mem)
                        if content and content.strip():
                            context_parts.append(content.strip())
                
                combined_context = "\n\n".join(context_parts)
                
                if combined_context and len(combined_context.strip()) > 10:
                    print(f"[Mem0] OK Retrieved {len(all_memories)} unique memories for user {normalized_user_id} ({len(combined_context)} chars)")
                    return combined_context
            
            return ""
            
        except Exception as e:
            print(f"[Mem0] ERROR: Error getting all memories: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """
        Delete a memory
        
        Args:
            user_id: User identifier
            memory_id: Memory ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not self.available:
            return False
        
        try:
            def delete_sync():
                self.memory.delete(memory_id=memory_id, agent_id=user_id)
            
            await asyncio.to_thread(delete_sync)
            print(f"[Mem0] OK Memory deleted: {memory_id}")
            return True
            
        except Exception as e:
            print(f"[Mem0] ERROR: Error deleting memory: {e}")
            return False

