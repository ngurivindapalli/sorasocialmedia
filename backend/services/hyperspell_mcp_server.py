"""
Hyperspell MCP Server - Model Context Protocol Server for Hyperspell
Exposes Hyperspell functionality via MCP for AI clients like Claude Desktop, Cursor, etc.

This server implements the MCP protocol over stdio, allowing AI clients to interact with Hyperspell.
"""

import os
import sys
import json
import asyncio
from typing import Dict, Optional, List, Any
from datetime import datetime

from services.hyperspell_service import HyperspellService


class HyperspellMCPServer:
    """MCP Server that exposes Hyperspell tools and resources to AI clients"""
    
    def __init__(self, hyperspell_service: Optional[HyperspellService] = None):
        """
        Initialize Hyperspell MCP Server
        
        Args:
            hyperspell_service: Optional HyperspellService instance. If not provided, will create one.
        """
        self.hyperspell_service = hyperspell_service or HyperspellService()
        self.available = self.hyperspell_service.is_available()
        
        if not self.hyperspell_service.is_available():
            print("[Hyperspell MCP] Hyperspell service not available. Set HYPERSPELL_API_KEY environment variable.", file=sys.stderr)
            return
        
        print("[Hyperspell MCP] OK MCP Server initialized", file=sys.stderr)
    
    def _handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP protocol requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "hyperspell-mcp",
                            "version": "1.0.0"
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "search",
                                "description": "Search all memories indexed by Hyperspell. Set 'answer' to true to directly answer the query, or to 'false' to simply get all memories related to the query.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "query": {
                                            "type": "string",
                                            "description": "Search query to find relevant memories"
                                        },
                                        "answer": {
                                            "type": "boolean",
                                            "description": "Whether to return an LLM-generated answer (true) or just search results (false)",
                                            "default": True
                                        },
                                        "max_results": {
                                            "type": "integer",
                                            "description": "Maximum number of results to return",
                                            "default": 5
                                        }
                                    },
                                    "required": ["query"]
                                }
                            },
                            {
                                "name": "add_memory",
                                "description": "Add text, markdown, or JSON to the Hyperspell index so it can be searched later. Returns the source and resource_id that can be used to later retrieve the processed memory.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {
                                            "type": "string",
                                            "description": "Text, markdown, or JSON content to add to Hyperspell"
                                        },
                                        "collection": {
                                            "type": "string",
                                            "description": "Optional collection name to organize memories",
                                            "default": "user_memories"
                                        }
                                    },
                                    "required": ["text"]
                                }
                            },
                            {
                                "name": "get_memory",
                                "description": "Retrieve a memory that has been previously indexed by resource_id.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "resource_id": {
                                            "type": "string",
                                            "description": "Resource ID of the memory to retrieve"
                                        }
                                    },
                                    "required": ["resource_id"]
                                }
                            },
                            {
                                "name": "upload_file",
                                "description": "Upload a file to the Hyperspell index. Returns the source and resource_id that can be used to later retrieve the processed memory.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "file_path": {
                                            "type": "string",
                                            "description": "Path to the file to upload"
                                        },
                                        "collection": {
                                            "type": "string",
                                            "description": "Optional collection name to organize memories",
                                            "default": "user_documents"
                                        }
                                    },
                                    "required": ["file_path"]
                                }
                            },
                            {
                                "name": "list_integrations",
                                "description": "List all available integrations in Hyperspell",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            {
                                "name": "connect_integration",
                                "description": "Get a signed URL to connect to a given integration. Use list_integrations to find the correct integration_id.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "integration_id": {
                                            "type": "string",
                                            "description": "Integration ID from list_integrations"
                                        }
                                    },
                                    "required": ["integration_id"]
                                }
                            },
                            {
                                "name": "user_info",
                                "description": "Get basic info about the current user, including which integrations are currently enabled and which ones are available.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Run async tool calls
                result = asyncio.run(self._call_tool(tool_name, arguments))
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2)
                            }
                        ]
                    }
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool asynchronously"""
        try:
            if tool_name == "search":
                query = arguments.get("query", "")
                answer = arguments.get("answer", True)
                max_results = arguments.get("max_results", 5)
                
                user_id = self.hyperspell_service.user_id
                result = await self.hyperspell_service.query_memories(
                    user_id=user_id,
                    query=query,
                    max_results=max_results
                )
                
                if result:
                    if answer and result.get("answer"):
                        return {
                            "answer": result["answer"],
                            "query": query,
                            "results_count": len(result.get("results", []))
                        }
                    else:
                        return {
                            "query": query,
                            "results": result.get("results", [])[:max_results]
                        }
                else:
                    return {"error": "No results found", "query": query}
            
            elif tool_name == "add_memory":
                text = arguments.get("text", "")
                collection = arguments.get("collection", "user_memories")
                
                user_id = self.hyperspell_service.user_id
                result = await self.hyperspell_service.add_text_memory(
                    user_id=user_id,
                    text=text,
                    collection=collection
                )
                
                if result:
                    return {
                        "success": True,
                        "resource_id": result.get("resource_id"),
                        "collection": collection,
                        "added_at": result.get("added_at")
                    }
                else:
                    return {"error": "Failed to add memory"}
            
            elif tool_name == "get_memory":
                resource_id = arguments.get("resource_id", "")
                # Note: get_memory would require additional Hyperspell API support
                return {
                    "error": "get_memory not yet implemented",
                    "resource_id": resource_id,
                    "note": "This feature requires additional Hyperspell API support"
                }
            
            elif tool_name == "upload_file":
                file_path = arguments.get("file_path", "")
                collection = arguments.get("collection", "user_documents")
                
                if not os.path.exists(file_path):
                    return {"error": f"File not found: {file_path}"}
                
                user_id = self.hyperspell_service.user_id
                result = await self.hyperspell_service.upload_document(
                    user_id=user_id,
                    file_path=file_path,
                    filename=os.path.basename(file_path)
                )
                
                if result:
                    return {
                        "success": True,
                        "resource_id": result.get("resource_id"),
                        "filename": result.get("filename"),
                        "uploaded_at": result.get("uploaded_at")
                    }
                else:
                    return {"error": "Failed to upload file"}
            
            elif tool_name == "list_integrations":
                # Placeholder - would need Hyperspell API for integrations
                return {
                    "integrations": [],
                    "message": "Integration listing requires additional Hyperspell API support"
                }
            
            elif tool_name == "connect_integration":
                integration_id = arguments.get("integration_id", "")
                # Placeholder - would need Hyperspell API for integration connections
                return {
                    "error": "Integration connection requires additional Hyperspell API support",
                    "integration_id": integration_id
                }
            
            elif tool_name == "user_info":
                return {
                    "user_id": self.hyperspell_service.user_id,
                    "available": self.hyperspell_service.is_available(),
                    "integrations_enabled": [],
                    "integrations_available": []
                }
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def run(self):
        """Run the MCP server using stdio"""
        if not self.available:
            print("[Hyperspell MCP] Server not available. Check configuration.", file=sys.stderr)
            sys.exit(1)
        
        print("[Hyperspell MCP] Starting MCP server (stdio mode)...", file=sys.stderr)
        print("[Hyperspell MCP] Ready to accept requests", file=sys.stderr)
        
        # Read from stdin, write to stdout
        for line in sys.stdin:
            try:
                request = json.loads(line.strip())
                response = self._handle_request(request)
                print(json.dumps(response), flush=True)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response), flush=True)


def main():
    """Main entry point for running the MCP server standalone"""
    server = HyperspellMCPServer()
    server.run()


if __name__ == "__main__":
    main()
