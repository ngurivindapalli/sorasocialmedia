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
            
            result = {
                "resource_id": memory_status.resource_id if hasattr(memory_status, 'resource_id') else str(memory_status),
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "added_at": datetime.now().isoformat(),
                "user_id": user_id,  # The user's own account
                "collection": collection or "user_memories"
            }
            
            print(f"[Hyperspell] OK Text memory added: {result['resource_id']}")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error adding text memory: {e}")
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
                print(f"[Hyperspell] Querying ALL memories for user: {user_id} (query: '{query}')")
                # Use the user's own account
                client = Hyperspell(api_key=self.api_key, user_id=user_id)
                
                # Use search() method to get all memories
                # For getting everything, use "*" as query and don't limit sources
                try:
                    # First try: search all memories without specifying sources
                    # This should get everything regardless of collection
                    search_query = query if query and query.strip() else "*"
                    response = client.memories.search(
                        query=search_query,
                        answer=False  # Don't use answer mode, get raw documents
                    )
                    print(f"[Hyperspell] Search successful, got response")
                    return response
                except Exception as e:
                    print(f"[Hyperspell] Search without answer failed: {e}, trying with answer...")
                    try:
                        # Fallback: try with answer=True
                        search_query = query if query and query.strip() else "*"
                        response = client.memories.search(
                            query=search_query,
                            answer=True
                        )
                        return response
                    except Exception as e2:
                        print(f"[Hyperspell] Search with answer failed: {e2}, trying with sources...")
                        # Final fallback: try with vault source
                        search_query = query if query and query.strip() else "*"
                        response = client.memories.search(
                            query=search_query,
                            sources=["vault"],
                            answer=False
                        )
                        return response
            
            response = await asyncio.to_thread(search_sync)
            
            # Extract answer and documents from QueryResult
            answer = None
            documents = []
            
            if hasattr(response, 'answer') and response.answer:
                answer = response.answer
            elif hasattr(response, 'answer') and response.answer is not None:
                answer = str(response.answer)
            
            # Extract documents from QueryResult
            if hasattr(response, 'documents') and response.documents:
                documents = response.documents
            elif hasattr(response, 'results') and response.results:
                # If results is a list of documents
                if isinstance(response.results, list):
                    documents = response.results
                else:
                    documents = [response.results]
            
            # Format response according to Hyperspell SDK structure
            result = {
                "query": query,
                "answer": answer,
                "documents": documents,  # Store actual documents
                "results": documents,  # Keep for backward compatibility
                "user_id": user_id,
                "queried_at": datetime.now().isoformat()
            }
            
            print(f"[Hyperspell] OK Memory search completed")
            if result.get("answer"):
                print(f"[Hyperspell] Answer: {result['answer'][:100]}...")
            if documents:
                print(f"[Hyperspell] Found {len(documents)} documents")
            else:
                print(f"[Hyperspell] No documents found in response")
            return result
            
        except Exception as e:
            print(f"[Hyperspell] Error querying memories: {e}")
            return None
    
    async def get_all_memories_context(self, user_id: str) -> str:
        """
        Get ALL memories for a user as context (documents, competitors, posts, etc.)
        Uses a very broad query to retrieve everything.
        
        Args:
            user_id: User identifier (email format recommended)
            
        Returns:
            Formatted context string with all user memories
        """
        if not self.available:
            return ""
        
        print(f"[Hyperspell] Getting ALL memories for user: {user_id}")
        
        # Use a very broad query to get all memories
        # Try multiple broad queries to catch everything
        all_context_parts = []
        
        # Use a single very broad query to get ALL memories
        # No need to search for specific collections - just get everything
        seen_content = set()  # Track content we've already added to avoid duplicates
        
        try:
            # Query with "*" to get everything, with high max_results
            memory_results = await self.query_memories(user_id, "*", max_results=100)
            
            if memory_results:
                # Extract answer if available (but skip generic "cannot answer" responses)
                answer = memory_results.get("answer")
                if answer and len(str(answer).strip()) > 0:
                    answer_str = str(answer).strip()
                    # Skip generic "cannot answer" responses
                    if "cannot answer" not in answer_str.lower() and "no information" not in answer_str.lower():
                        if answer_str not in seen_content:
                            all_context_parts.append(answer_str)
                            seen_content.add(answer_str)
                
                # Extract all documents/memories
                documents = memory_results.get("documents") or memory_results.get("results", [])
                print(f"[Hyperspell] Processing {len(documents)} memory items")
                
                for i, doc in enumerate(documents):
                    content = None
                    
                    # Debug: print what type of object we have
                    print(f"[Hyperspell] Document {i+1} type: {type(doc)}")
                    if isinstance(doc, dict):
                        print(f"[Hyperspell] Document {i+1} keys: {list(doc.keys())[:10]}")
                    
                    # Try multiple ways to extract content
                    if isinstance(doc, dict):
                        # Try all possible keys
                        content = (doc.get("content") or doc.get("text") or doc.get("snippet") or 
                                 doc.get("document") or doc.get("memory") or doc.get("data") or
                                 doc.get("body") or doc.get("value") or doc.get("message"))
                        
                        # If still no content, try converting the whole dict to string (excluding metadata)
                        if not content:
                            # Try to get the actual content by excluding known metadata keys
                            metadata_keys = {'id', 'score', 'metadata', 'created_at', 'updated_at', 'collection', 'source'}
                            content_dict = {k: v for k, v in doc.items() if k not in metadata_keys}
                            if content_dict:
                                # Join all non-metadata values
                                content = ' '.join(str(v) for v in content_dict.values() if v and str(v).strip())
                    elif hasattr(doc, '__dict__'):
                        # It's an object, try to get attributes
                        attrs = ['content', 'text', 'snippet', 'document', 'memory', 'data', 'body', 'value']
                        for attr in attrs:
                            if hasattr(doc, attr):
                                content = getattr(doc, attr)
                                if content:
                                    break
                        
                        # Special handling for Hyperspell Memory objects
                        if not content and hasattr(doc, 'text'):
                            # Memory objects might have text as a list or dict
                            text_attr = getattr(doc, 'text', None)
                            if isinstance(text_attr, list) and len(text_attr) > 0:
                                # If text is a list, extract from first item
                                if isinstance(text_attr[0], dict):
                                    content = text_attr[0].get('text') or str(text_attr[0])
                                else:
                                    content = str(text_attr[0])
                            elif isinstance(text_attr, dict):
                                content = text_attr.get('text') or str(text_attr)
                            elif text_attr:
                                content = str(text_attr)
                    elif hasattr(doc, 'content'):
                        content = doc.content
                    elif hasattr(doc, 'text'):
                        content = doc.text
                    elif hasattr(doc, 'snippet'):
                        content = doc.snippet
                    elif hasattr(doc, 'document'):
                        content = doc.document
                    elif hasattr(doc, 'memory'):
                        content = doc.memory
                    else:
                        # Last resort: convert to string
                        content = str(doc)
                    
                    if content:
                        # Handle content that might be a list or dict
                        if isinstance(content, list):
                            # If content is a list, extract text from items
                            content_parts = []
                            for item in content:
                                if isinstance(item, dict):
                                    item_text = item.get('text') or item.get('content') or str(item)
                                    if item_text:
                                        content_parts.append(str(item_text))
                                else:
                                    content_parts.append(str(item))
                            content_str = ' '.join(content_parts).strip()
                        elif isinstance(content, dict):
                            # If content is a dict, extract text field
                            content_str = str(content.get('text') or content.get('content') or content).strip()
                        else:
                            content_str = str(content).strip()
                        
                        if len(content_str) > 0:
                            # Use first 200 chars as hash to avoid exact duplicates (more specific)
                            content_hash = content_str[:200]
                            if content_hash not in seen_content:
                                all_context_parts.append(content_str)
                                seen_content.add(content_hash)
                                print(f"[Hyperspell] ✓ Added memory item {i+1} ({len(content_str)} chars): {content_str[:100]}...")
                        else:
                            print(f"[Hyperspell] ⚠️ Document {i+1} content is empty after processing")
                    else:
                        print(f"[Hyperspell] ⚠️ Document {i+1} has no extractable content")
                            
        except Exception as e:
            print(f"[Hyperspell] Error getting all memories: {e}")
            import traceback
            traceback.print_exc()
        
        if all_context_parts:
            result = "\n\n".join(all_context_parts)
            print(f"[Hyperspell] ✓ Retrieved {len(all_context_parts)} memory items ({len(result)} chars)")
            return result
        else:
            print(f"[Hyperspell] ⚠️ No memories found for user")
            return ""
    
    async def get_context_summary(self, user_id: str, query: str) -> str:
        """
        Get a formatted context summary from Hyperspell for AI prompt injection
        Uses search() with answer=True to get LLM-generated context
        
        Args:
            user_id: User identifier (email format recommended)
            query: Query to get relevant context
            
        Returns:
            Formatted context string for AI prompts
        """
        if not self.available:
            return ""
        
        memory_results = await self.query_memories(user_id, query)
        
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

