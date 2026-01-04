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
        Initialize Mem0 service with persistent storage
        
        Args:
            vector_db: Vector database type (e.g., 's3_vectors', 'chroma', 'pinecone')
            config: Optional Mem0 configuration dict
        """
        self.available = False
        
        if not MEM0_AVAILABLE:
            print("[Mem0] SDK not available. Install with: pip install mem0ai")
            return
        
        try:
            import os
            from pathlib import Path
            
            # Check for AWS credentials for S3 vector storage (persistent across deployments)
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")
            aws_bucket = os.getenv("AWS_S3_BUCKET")
            
            # Prefer S3 vectors for persistence (survives deployments)
            # Fallback to ChromaDB if AWS not configured
            if vector_db is None:
                if aws_access_key and aws_secret_key and aws_bucket:
                    vector_db = 's3_vectors'
                    print("[Mem0] Using S3 vectors for persistent storage (survives deployments)")
                else:
                    vector_db = 'chroma'
                    print("[Mem0] Using ChromaDB (local) - AWS credentials not configured for S3 vectors")
                    print("[Mem0] WARNING: Local ChromaDB will be lost on deployment. Configure AWS for persistent storage.")
            
            mem0_config = config or {}
            
            # Configure based on vector_db type
            if not mem0_config:
                if vector_db == 's3_vectors' and aws_access_key and aws_secret_key and aws_bucket:
                    # Use S3 for vector storage (persistent across deployments)
                    # AWS credentials should be set via environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
                    # Mem0 will automatically use them from environment
                    # Mem0 S3 vectors configuration
                    # Try different index name formats - S3 Vectors may have naming restrictions
                    # Index names must be lowercase, alphanumeric, and may have length restrictions
                    index_name = "mem0memories"  # Simplified name without underscores
                    
                    mem0_config = {
                        "vector_store": {
                            "provider": "s3_vectors",
                            "config": {
                                "vector_bucket_name": aws_bucket,
                                "collection_name": index_name,
                                "region_name": aws_region
                                # AWS credentials should be in environment variables
                            }
                        }
                    }
                    print(f"[Mem0] Configuring S3 vectors with bucket: {aws_bucket}, index: {index_name}, region: {aws_region}")
                    # Ensure AWS credentials are in environment for Mem0 to use
                    if aws_access_key:
                        os.environ['AWS_ACCESS_KEY_ID'] = aws_access_key
                    if aws_secret_key:
                        os.environ['AWS_SECRET_ACCESS_KEY'] = aws_secret_key
                    print(f"[Mem0] Configuring S3 vectors with bucket: {aws_bucket} (region: {aws_region})")
                    print(f"[Mem0] AWS credentials will be read from environment variables")
                else:
                    # Fallback to ChromaDB with persistent directory
                    backend_dir = Path(__file__).parent.parent
                    chroma_persist_dir = backend_dir / "chroma_db"
                    chroma_persist_dir.mkdir(exist_ok=True)
                    chroma_persist_path = str(chroma_persist_dir.absolute())
                    
                    mem0_config = {
                        "vector_store": {
                            "provider": "chroma",
                            "config": {
                                "collection_name": "mem0_memories",
                                "path": chroma_persist_path,
                                "persist_directory": chroma_persist_path
                            }
                        }
                    }
                    print(f"[Mem0] Configuring ChromaDB with persistent storage: {chroma_persist_path}")
                    print("[Mem0] NOTE: For production, configure AWS credentials to use S3 vectors (persistent across deployments)")
            
            # Initialize Mem0 with config
            try:
                print(f"[Mem0] Initializing with config: {mem0_config}")
                self.memory = Memory.from_config(mem0_config)
                print(f"[Mem0] ✅ Successfully initialized with config")
            except Exception as config_error:
                # If S3 failed with invalid index name, try alternative index names
                if vector_db == 's3_vectors' and "Invalid index name" in str(config_error):
                    print(f"[Mem0] WARNING: Index name '{index_name}' invalid, trying alternatives...")
                    
                    # Try alternative index names (S3 Vectors naming rules: lowercase, no underscores, 3-63 chars)
                    alternative_indexes = ["memories", "mem0memories", "mem0index", "vectorindex"]
                    
                    for alt_index in alternative_indexes:
                        try:
                            print(f"[Mem0] Trying index name: {alt_index}")
                            alt_config = {
                                "vector_store": {
                                    "provider": "s3_vectors",
                                    "config": {
                                        "vector_bucket_name": aws_bucket,
                                        "collection_name": alt_index,
                                        "region_name": aws_region
                                    }
                                }
                            }
                            self.memory = Memory.from_config(alt_config)
                            print(f"[Mem0] ✅ Successfully initialized with index: {alt_index}")
                            mem0_config = alt_config  # Update for logging
                            break
                        except Exception as alt_error:
                            if "Invalid index name" not in str(alt_error):
                                # Different error - might be progress
                                print(f"[Mem0] Index {alt_index} failed with different error: {alt_error}")
                            continue
                    else:
                        # All alternative indexes failed
                        print(f"[Mem0] ❌ All index name attempts failed")
                        raise config_error
                else:
                    # Other error or not S3 - try fallback
                    print(f"[Mem0] WARNING: Config initialization failed: {config_error}")
                    import traceback
                    traceback.print_exc()
                    
                    # If S3 was requested but failed, this is a problem
                    if vector_db == 's3_vectors':
                        print(f"[Mem0] ❌ CRITICAL: S3 vector initialization failed! Memories will NOT persist.")
                        print(f"[Mem0] Check: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_BUCKET, AWS_REGION")
                        print(f"[Mem0] Bucket name: {aws_bucket}")
                        print(f"[Mem0] Region: {aws_region}")
                        print(f"[Mem0] Access key set: {bool(aws_access_key)}")
                        print(f"[Mem0] Secret key set: {bool(aws_secret_key)}")
                        
                        # Fallback to ChromaDB if S3 completely fails
                        print(f"[Mem0] ⚠️ Falling back to ChromaDB (memories will NOT persist across restarts)")
                        backend_dir = Path(__file__).parent.parent
                        chroma_persist_dir = backend_dir / "chroma_db"
                        chroma_persist_dir.mkdir(exist_ok=True)
                        chroma_persist_path = str(chroma_persist_dir.absolute())
                        os.environ['CHROMA_PERSIST_DIRECTORY'] = chroma_persist_path
                        self.memory = Memory()
                        vector_db = 'chroma'  # Update for logging
                    elif vector_db == 'chroma':
                        backend_dir = Path(__file__).parent.parent
                        chroma_persist_dir = backend_dir / "chroma_db"
                        chroma_persist_dir.mkdir(exist_ok=True)
                        chroma_persist_path = str(chroma_persist_dir.absolute())
                        os.environ['CHROMA_PERSIST_DIRECTORY'] = chroma_persist_path
                        print(f"[Mem0] Falling back to ChromaDB at: {chroma_persist_path}")
                        self.memory = Memory()
                    else:
                        self.memory = Memory()
                        print(f"[Mem0] ⚠️ Using fallback initialization - persistence may be limited")
            
            self.available = True
            storage_type = "S3 (persistent)" if vector_db == 's3_vectors' else "ChromaDB (local)"
            print(f"[Mem0] OK Mem0 service initialized with {storage_type} storage")
            
            # Verify S3 connection if using S3
            if vector_db == 's3_vectors' and self.available:
                try:
                    # Try to verify S3 access by checking if we can list the bucket
                    import boto3
                    s3_client = boto3.client(
                        's3',
                        aws_access_key_id=aws_access_key,
                        aws_secret_access_key=aws_secret_key,
                        region_name=aws_region
                    )
                    # Try to head the bucket to verify access
                    s3_client.head_bucket(Bucket=aws_bucket)
                    print(f"[Mem0] ✅ S3 bucket access verified: {aws_bucket}")
                except Exception as s3_error:
                    print(f"[Mem0] ⚠️ WARNING: Could not verify S3 bucket access: {s3_error}")
                    print(f"[Mem0] Memories may not persist correctly. Check IAM permissions.")
            
        except Exception as e:
            print(f"[Mem0] ERROR: Error initializing Mem0 service: {e}")
            import traceback
            traceback.print_exc()
            self.available = False
    
    def is_available(self) -> bool:
        """Check if Mem0 service is available"""
        return self.available
    
    def _normalize_user_id(self, user_id: str) -> str:
        """
        Normalize user ID for consistency with Mem0 agent_id
        CRITICAL: This ensures memories persist across sessions and deployments
        Always use lowercase email with no whitespace
        """
        if not user_id:
            return "anonymous_user"
        # Normalize: lowercase, strip whitespace, ensure it's an email format
        normalized = user_id.lower().strip()
        # Remove any extra whitespace or special characters that might cause issues
        normalized = normalized.replace(' ', '').replace('\n', '').replace('\t', '')
        return normalized
    
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
        normalized_user_id = self._normalize_user_id(user_id)
        
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
        normalized_user_id = self._normalize_user_id(user_id)
        
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

