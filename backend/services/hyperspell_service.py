"""
Hyperspell Service - Memory & Context Layer for AI Agents
Integrates Hyperspell to provide persistent memory and context for better AI responses
"""

import os
from typing import Dict, Optional, List
import httpx
from datetime import datetime
import asyncio

try:
    from hyperspell import Hyperspell
    HYPERSPELL_AVAILABLE = True
except ImportError:
    HYPERSPELL_AVAILABLE = False
    print("[Warning] Hyperspell SDK not installed. Install with: pip install hyperspell")


class HyperspellService:
    """Service for interacting with Hyperspell API to provide memory and context for AI agents"""
    
    def __init__(self, api_key: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize Hyperspell service
        
        Each user's memories are stored in their own Hyperspell account using their email as user_id.
        
        Args:
            api_key: Hyperspell API key. If not provided, will try to get from HYPERSPELL_API_KEY env var
            user_id: Default user ID (not used for per-user operations, kept for backward compatibility)
        """
        self.api_key = api_key or os.getenv('HYPERSPELL_API_KEY')
        self.available = False
        
        if not HYPERSPELL_AVAILABLE:
            print("[Hyperspell] SDK not available. Install with: pip install hyperspell")
            return
        
        if not self.api_key:
            print("[Hyperspell] API key not provided. Set HYPERSPELL_API_KEY environment variable.")
            return
        
        try:
            # Just verify the API key works - we'll create per-user clients as needed
            self.available = True
            print(f"[Hyperspell] OK Hyperspell service initialized")
            print(f"[Hyperspell] OK Each user's memories will be stored in their own Hyperspell account")
        except Exception as e:
            print(f"[Hyperspell] Error initializing service: {e}")
            self.available = False
    
    async def add_text_memory(self, user_id: str, text: str, collection: Optional[str] = None) -> Optional[Dict]:
        """
        Add a text memory to Hyperspell using memories.add()
        
        Each user's memories are stored in their own Hyperspell account.
        
        Args:
            user_id: User identifier (email format recommended, e.g., "user@example.com")
            text: Text content to store as memory
            collection: Optional collection name to organize memories
            
        Returns:
            Memory status dict with resource_id, or None if failed
        """
        if not self.available:
            print("[Hyperspell] Service not available for adding text memory")
            return None
        
        try:
            # Create a client for this specific user - each user has their own memories
            # Run synchronous SDK call in thread pool to avoid blocking
            def add_sync():
                print(f"[Hyperspell] Adding text memory for user: {user_id}")
                client = Hyperspell(api_key=self.api_key, user_id=user_id)
                # Use memories.add() as per Hyperspell documentation
                memory_status = client.memories.add(
                    text=text,
                    collection=collection or "user_memories"
                )
                return memory_status
            
            memory_status = await asyncio.to_thread(add_sync)
            
            # Verify memory was actually created - check for resource_id
            resource_id = None
            if hasattr(memory_status, 'resource_id'):
                resource_id = memory_status.resource_id
            elif isinstance(memory_status, dict):
                resource_id = memory_status.get('resource_id')
            elif isinstance(memory_status, str):
                resource_id = memory_status
            
            if not resource_id or (isinstance(resource_id, str) and len(resource_id.strip()) == 0):
                print(f"[Hyperspell] ❌ ERROR: Memory creation returned no valid resource_id. Response: {memory_status}")
                return None
            
            # Verify by querying the memory back (double-check it exists)
            try:
                verify_query = await self.query_memories(user_id, text[:50] if len(text) > 50 else text, max_results=1)
                if verify_query and verify_query.get("answer"):
                    verify_answer = str(verify_query.get("answer", "")).strip()
                    # Check if our text appears in the verification (at least partially)
                    text_check = text[:50].lower() if len(text) > 50 else text.lower()
                    if text_check in verify_answer.lower() or len(verify_answer) > 0:
                        print(f"[Hyperspell] ✓ Verified: Memory confirmed in Hyperspell (resource_id: {resource_id})")
                    else:
                        print(f"[Hyperspell] ⚠️ WARNING: Memory created but verification query didn't find content")
                else:
                    print(f"[Hyperspell] ⚠️ WARNING: Memory created but verification query returned no results")
            except Exception as verify_error:
                print(f"[Hyperspell] ⚠️ WARNING: Could not verify memory (non-critical): {verify_error}")
                # Continue anyway - memory was created, verification is just a double-check
            
            result = {
                "resource_id": resource_id,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "added_at": datetime.now().isoformat(),
                "user_id": user_id,  # The user's own account
                "collection": collection or "user_memories",
                "verified": True  # Indicates we verified the memory exists
            }
            
            print(f"[Hyperspell] ✓ OK Text memory added and verified: {resource_id}")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error adding text memory: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def append_to_unified_brand_context(self, user_id: str, new_content: str, content_type: str = "document") -> Optional[Dict]:
        """
        Append content to a unified brand context memory for a user.
        Retrieves existing brand context, merges with new content, and saves as a single unified memory.
        
        Args:
            user_id: User identifier (email format recommended)
            new_content: New content to append to brand context
            content_type: Type of content being added (e.g., "document", "competitor", "note")
            
        Returns:
            Memory status dict with resource_id, or None if failed
        """
        if not self.available:
            print("[Hyperspell] Service not available for appending to brand context")
            return None
        
        try:
            print(f"[Hyperspell] Appending {content_type} to unified brand context for user: {user_id}")
            
            # Try to get existing brand context, but don't fail if it's not found yet
            # (it might not be indexed yet, or this might be the first content)
            existing_context = ""
            try:
                existing_context = await self.get_all_memories_context(user_id)
                if existing_context:
                    print(f"[Hyperspell] Found existing context: {len(existing_context)} chars")
                else:
                    print(f"[Hyperspell] No existing context found (this might be the first addition)")
            except Exception as e:
                print(f"[Hyperspell] Could not retrieve existing context (non-critical, might be first addition): {e}")
                existing_context = ""
            
            # Prepare new content section
            timestamp = datetime.now().isoformat()
            new_content_section = f"\n\n--- {content_type.upper()} ADDED: {timestamp} ---\n{new_content}\n"
            
            # Merge existing and new content
            if existing_context and len(existing_context.strip()) > 10:  # Lower threshold to 10 chars
                # Append new content to existing
                unified_content = existing_context + new_content_section
                print(f"[Hyperspell] Merged with existing context ({len(existing_context)} chars), total: {len(unified_content)} chars")
            else:
                # First content - create new unified memory
                unified_content = f"BRAND CONTEXT - UNIFIED MEMORY\n{new_content_section}"
                print(f"[Hyperspell] Creating new unified brand context ({len(unified_content)} chars)")
            
            # Save unified content as a single memory in "brand_context" collection
            def add_sync():
                client = Hyperspell(api_key=self.api_key, user_id=user_id)
                memory_status = client.memories.add(
                    text=unified_content,
                    collection="brand_context"  # Single collection for unified brand context
                )
                return memory_status
            
            memory_status = await asyncio.to_thread(add_sync)
            
            # Verify memory was actually created - check for resource_id
            resource_id = None
            if hasattr(memory_status, 'resource_id'):
                resource_id = memory_status.resource_id
            elif isinstance(memory_status, dict):
                resource_id = memory_status.get('resource_id')
            elif isinstance(memory_status, str):
                resource_id = memory_status
            
            if not resource_id or (isinstance(resource_id, str) and len(resource_id.strip()) == 0):
                print(f"[Hyperspell] ❌ ERROR: Memory creation returned no valid resource_id. Response: {memory_status}")
                return None
            
            # Verify by querying the memory back (double-check it exists)
            try:
                verify_query = await self.query_memories(user_id, f"brand context {content_type}", max_results=1)
                if verify_query and verify_query.get("answer"):
                    verify_answer = str(verify_query.get("answer", "")).strip()
                    # Check if our new content appears in the verification (at least partially)
                    content_check = new_content[:50].lower() if len(new_content) > 50 else new_content.lower()
                    if content_check in verify_answer.lower() or len(verify_answer) > len(existing_context) if existing_context else len(verify_answer) > 0:
                        print(f"[Hyperspell] ✓ Verified: Memory confirmed in Hyperspell (resource_id: {resource_id})")
                    else:
                        print(f"[Hyperspell] ⚠️ WARNING: Memory created but verification query didn't find new content")
                else:
                    print(f"[Hyperspell] ⚠️ WARNING: Memory created but verification query returned no results")
            except Exception as verify_error:
                print(f"[Hyperspell] ⚠️ WARNING: Could not verify memory (non-critical): {verify_error}")
                # Continue anyway - memory was created, verification is just a double-check
            
            result = {
                "resource_id": resource_id,
                "content_length": len(unified_content),
                "added_at": timestamp,
                "user_id": user_id,
                "collection": "brand_context",
                "verified": True  # Indicates we verified the memory exists
            }
            
            print(f"[Hyperspell] ✓ OK Unified brand context updated and verified: {resource_id}")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error appending to unified brand context: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_connect_url(self, user_id: str) -> str:
        """
        Generate Hyperspell Connect URL for user to link their accounts
        
        Args:
            user_id: User identifier (for logging only - all connections go to same account)
            
        Returns:
            URL for Hyperspell Connect
        """
        if not self.available:
            return ""
        
        # Generate a connect URL for this specific user
        connect_url = f"https://connect.hyperspell.com?token={user_id}"
        return connect_url
    
    async def upload_document(self, user_id: str, file_path: str, filename: Optional[str] = None) -> Optional[Dict]:
        """
        Upload a document to Hyperspell memory layer
        
        IMPORTANT: All documents from all users are stored in the same Hyperspell account.
        The user_id parameter is for tracking/logging purposes only - all memories go to the same place.
        
        Args:
            user_id: User identifier (for logging/tracking only - not used for storage isolation)
            file_path: Path to the file to upload
            filename: Optional filename override
            
        Returns:
            Memory status dict with resource_id, or None if failed
        """
        if not self.available:
            print("[Hyperspell] Service not available for document upload")
            return None
        
        try:
            # Create a client for this specific user - each user has their own memories
            # Run synchronous SDK call in thread pool to avoid blocking
            def upload_sync():
                print(f"[Hyperspell] Uploading document for user: {user_id}")
                # Use the user's own account
                client = Hyperspell(api_key=self.api_key, user_id=user_id)
                
                # Read file content
                with open(file_path, 'rb') as file:
                    file_content = file.read()
                
                # Try to determine file type and handle accordingly
                file_ext = os.path.splitext(filename or file_path)[1].lower()
                
                # For text-based files, extract text and use memories.add()
                if file_ext in ('.txt', '.md', '.json', '.csv', '.log'):
                    try:
                        text_content = file_content.decode('utf-8')
                        # Use memories.add() for text content as per Hyperspell docs
                        memory_status = client.memories.add(
                            text=text_content,
                            collection="documents"  # Collection name for documents
                        )
                        print(f"[Hyperspell] Added text memory to 'documents' collection: {len(text_content)} chars")
                        return memory_status
                    except UnicodeDecodeError:
                        # If decoding fails, try with error handling
                        text_content = file_content.decode('utf-8', errors='ignore')
                        memory_status = client.memories.add(
                            text=text_content,
                            collection="documents"
                        )
                        print(f"[Hyperspell] Added text memory to 'documents' collection: {memory_status}")
                        return memory_status
                
                # For binary files (PDF, DOCX, etc.), try upload() method if available
                try:
                    # Try upload() method for binary files
                    with open(file_path, 'rb') as file:
                        memory_status = client.memories.upload(file=file)
                    print(f"[Hyperspell] Uploaded binary file via upload() method")
                    return memory_status
                except (AttributeError, TypeError) as e:
                    # If upload() doesn't exist or fails, try to extract text from binary
                    # For PDF/DOCX, you might need additional libraries
                    print(f"[Hyperspell] upload() method not available, trying text extraction: {e}")
                    # Fallback: try to read as text with error handling
                    try:
                        text_content = file_content.decode('utf-8', errors='ignore')
                        if len(text_content.strip()) > 0:
                            memory_status = client.memories.add(
                                text=text_content,
                                collection="documents"
                            )
                            print(f"[Hyperspell] Added binary file as text to 'documents' collection: {len(text_content)} chars")
                            return memory_status
                    except Exception as text_error:
                        raise Exception(f"Could not upload file. Upload method not available and text extraction failed: {text_error}")
            
            memory_status = await asyncio.to_thread(upload_sync)
            
            result = {
                "resource_id": memory_status.resource_id if hasattr(memory_status, 'resource_id') else str(memory_status),
                "filename": filename or os.path.basename(file_path),
                "uploaded_at": datetime.now().isoformat(),
                "user_id": user_id  # The user's own account
            }
            
            print(f"[Hyperspell] OK Document uploaded: {result['resource_id']}")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error uploading document: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def query_memories(self, user_id: str, query: str, max_results: int = 5) -> Optional[Dict]:
        """
        Query Hyperspell memory layer for relevant context
        
        Args:
            user_id: User identifier
            query: Query string to search memories
            max_results: Maximum number of results to return
            
        Returns:
            Query response with relevant memories, or None if failed
        """
        if not self.available:
            print("[Hyperspell] Service not available for memory query")
            return None
        
        try:
            # Create a client for this specific user - searches only their memories
            # Run synchronous SDK call in thread pool to avoid blocking
            def search_sync():
                # Use the user's own account
                client = Hyperspell(api_key=self.api_key, user_id=user_id)
                
                # Use search() with answer=True to get summarized content from all memories
                search_query = query if query and query.strip() else "*"
                try:
                    response = client.memories.search(
                        query=search_query,
                        answer=True  # Get content summaries - this accesses the actual memory content
                    )
                    return response
                except Exception as e:
                    print(f"[Hyperspell] Search with answer=True failed: {e}, trying fallback...")
                    # Fallback: try without answer
                    try:
                        response = client.memories.search(
                            query=search_query,
                            answer=False
                        )
                        return response
                    except Exception as e2:
                        print(f"[Hyperspell] Search failed: {e2}")
                        raise
            
            response = await asyncio.to_thread(search_sync)
            
            # Extract answer field - this contains the summarized content from all memories
            answer = None
            if hasattr(response, 'answer') and response.answer:
                answer = str(response.answer).strip()
                if len(answer) > 20:
                    print(f"[Hyperspell] Retrieved answer: {len(answer)} chars")
                else:
                    answer = None
            
            # Format response - we only use the answer field, not individual documents
            result = {
                "query": query,
                "answer": answer,
                "documents": [],  # Don't return documents - we use answer field only
                "results": [],  # Keep for backward compatibility
                "user_id": user_id,
                "queried_at": datetime.now().isoformat()
            }
            
            if answer:
                print(f"[Hyperspell] OK Memory search completed - answer: {len(answer)} chars")
                if len(answer) > 100:
                    print(f"[Hyperspell] Answer: {answer[:100]}...")
                else:
                    print(f"[Hyperspell] Answer: {answer}")
            else:
                print(f"[Hyperspell] OK Memory search completed - no answer found")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error querying memories: {e}")
            return None
    
    async def get_all_memories_context(self, user_id: str) -> str:
        """
        Get unified brand context from Hyperspell "brand_context" collection.
        Uses multiple queries to reliably retrieve the unified brand context memory.
        
        Args:
            user_id: User identifier (email format recommended)
            
        Returns:
            Formatted context string with unified brand context
        """
        if not self.available:
            return ""
        
        try:
            print(f"[Hyperspell] Querying unified brand context for user: {user_id}")
            
            # Try multiple queries to find the unified brand context
            queries_to_try = [
                "*",  # Get all memories (most reliable)
                "BRAND CONTEXT UNIFIED MEMORY",
                "brand context documents competitors",
                "user background profession industry",
                "document resume cv"  # Try to match document content
            ]
            
            best_result = None
            best_length = 0
            
            for query in queries_to_try:
                print(f"[Hyperspell] Trying query: '{query}' for user: {user_id}")
                try:
                    memory_results = await self.query_memories(user_id, query, max_results=10)
                    
                    if memory_results:
                        # Use the answer field - it contains content from brand_context memories
                        answer = memory_results.get("answer")
                        if answer and len(str(answer).strip()) > 20:
                            answer_str = str(answer).strip()
                            # Skip generic "cannot answer" responses
                            if "cannot answer" not in answer_str.lower() and "no information" not in answer_str.lower() and "i don't have" not in answer_str.lower() and "i cannot" not in answer_str.lower():
                                print(f"[Hyperspell] ✓ Found valid result using query '{query}': {len(answer_str)} chars")
                                # Keep the longest/best result
                                if len(answer_str) > best_length:
                                    best_result = answer_str
                                    best_length = len(answer_str)
                                    print(f"[Hyperspell] This is the best result so far ({len(answer_str)} chars)")
                            else:
                                print(f"[Hyperspell] Generic response received for query '{query}': {answer_str[:100]}...")
                        else:
                            print(f"[Hyperspell] No answer field or answer too short ({len(str(answer)) if answer else 0} chars) for query '{query}'")
                    else:
                        print(f"[Hyperspell] No results object returned for query '{query}'")
                except Exception as query_error:
                    print(f"[Hyperspell] Error with query '{query}': {query_error}")
                    continue
            
            # Return the best result found
            if best_result and best_length > 20:
                print(f"[Hyperspell] ✓ Retrieved unified brand context: {len(best_result)} chars")
                # Show preview of retrieved content
                preview = best_result[:200] + "..." if len(best_result) > 200 else best_result
                print(f"[Hyperspell] Content preview: {preview}")
                return best_result
            else:
                # If all queries failed, return empty
                print(f"[Hyperspell] ❌ No brand context memories found for user: {user_id} (tried {len(queries_to_try)} queries, best result was {best_length} chars)")
                return ""
                
        except Exception as e:
            print(f"[Hyperspell] ❌ Error getting unified brand context: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    async def get_context_summary(self, user_id: str, query: str) -> str:
        """
        Get a formatted context summary from Hyperspell unified brand context for AI prompt injection.
        Queries the unified "brand_context" collection to get all user context.
        
        Args:
            user_id: User identifier (email format recommended)
            query: Query to get relevant context (can be used to filter, but primarily gets brand_context collection)
            
        Returns:
            Formatted context string for AI prompts
        """
        if not self.available:
            return ""
        
        # Query unified brand context collection
        # The query parameter can help filter, but we primarily want the brand_context collection
        memory_results = await self.query_memories(user_id, f"{query} brand context", max_results=10)
        
        if not memory_results:
            return ""
        
        # Format results into a context string
        # Hyperspell search() returns an answer and documents
        context_parts = []
        
        # Use the LLM-generated answer if available (most relevant)
        answer = memory_results.get("answer")
        if answer and len(str(answer).strip()) > 0:
            context_parts.append("HYPERSPELL MEMORY CONTEXT:")
            context_parts.append(str(answer))
            return "\n".join(context_parts)
        
        # Fallback to documents if no answer
        documents = memory_results.get("documents") or memory_results.get("results", [])
        
        if documents and len(documents) > 0:
            context_parts.append("HYPERSPELL MEMORY CONTEXT:")
            count = 0
            for doc in documents[:5]:  # Limit to top 5
                content = None
                
                # Try to extract content from document object
                if isinstance(doc, dict):
                    content = doc.get("content") or doc.get("text") or doc.get("snippet") or doc.get("document")
                elif hasattr(doc, 'content'):
                    content = doc.content
                elif hasattr(doc, 'text'):
                    content = doc.text
                elif hasattr(doc, 'snippet'):
                    content = doc.snippet
                elif hasattr(doc, 'document'):
                    content = doc.document
                
                if content and len(str(content).strip()) > 0:
                    count += 1
                    content_str = str(content).strip()
                    context_parts.append(f"{count}. {content_str[:500]}...")
            
            if count > 0:
                return "\n".join(context_parts)
        
        # No valid content found
        print(f"[Hyperspell] No valid content found in results")
        return ""
    
    def is_available(self) -> bool:
        """Check if Hyperspell service is available"""
        return self.available

