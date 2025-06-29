#!/usr/bin/env python3
"""
🦚 Peacock Memory - Proper MCP Server
Implements actual MCP protocol (JSON-RPC over stdio)
"""

import json
import sys
import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

def debug_log(message: str, **data):
    """Debug logging to stderr"""
    log_data = {"message": message, **data}
    print(f"DEBUG: {json.dumps(log_data)}", file=sys.stderr, flush=True)

class MCPServer:
    """Proper MCP Server implementation"""
    
    def __init__(self):
        self.tools = [
            {
                "name": "search_memory",
                "description": "Search through Peacock Memory database",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results",
                            "default": 10
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "add_memory",
                "description": "Add content to Peacock Memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "Content to add"
                        },
                        "disposition": {
                            "type": "string",
                            "description": "Content type",
                            "enum": ["Codebase", "Plan/Brainstorm", "Idea", "Note", "man-page"],
                            "default": "Note"
                        },
                        "project": {
                            "type": "string",
                            "description": "Project name (optional)"
                        }
                    },
                    "required": ["content"]
                }
            },
            {
                "name": "list_projects",
                "description": "List all projects in Peacock Memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            }
        ]
    
    async def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        debug_log("Handling initialize request", params=params)
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                }
            },
            "serverInfo": {
                "name": "peacock-memory",
                "version": "1.0.0"
            }
        }
    
    async def handle_notifications_initialized(self, params: Dict[str, Any]) -> None:
        """Handle notifications/initialized - no response needed"""
        debug_log("Received initialized notification")
        return None
    
    async def handle_tools_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        debug_log("Listing tools")
        return {"tools": self.tools}
    
    async def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        debug_log("Tool call", tool=tool_name, args=arguments)
        
        try:
            if tool_name == "search_memory":
                return await self._search_memory(arguments)
            elif tool_name == "add_memory":
                return await self._add_memory(arguments)
            elif tool_name == "list_projects":
                return await self._list_projects(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Unknown tool: {tool_name}"
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            debug_log("Tool call error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _search_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search memory implementation"""
        try:
            from core.database import search_all_collections
            
            query = args.get("query", "")
            limit = args.get("limit", 10)
            
            if not query:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Search query is required"
                        }
                    ],
                    "isError": True
                }
            
            results = search_all_collections(query, limit)
            
            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No results found for: {query}"
                        }
                    ]
                }
            
            # Format results
            result_text = f"🔍 Search Results for: '{query}'\n\n"
            
            for i, result in enumerate(results, 1):
                collection = result['collection'].replace('project_', '').replace('_', ' ').title()
                relevance = f"{result['relevance']:.3f}"
                
                result_text += f"🔸 Result #{i} (Relevance: {relevance})\n"
                result_text += f"📁 Collection: {collection}\n"
                result_text += f"📄 Preview: {result['preview']}\n"
                result_text += "─" * 50 + "\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            debug_log("Search error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Search error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _add_memory(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Add memory implementation"""
        try:
            from core.database import add_file_to_collection
            
            content = args.get("content", "")
            disposition = args.get("disposition", "Note")
            project = args.get("project")
            
            if not content:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Content is required"
                        }
                    ],
                    "isError": True
                }
            
            collection_name = f"project_{project}" if project else "global_files"
            
            file_id = add_file_to_collection(
                collection_name=collection_name,
                file_path="mcp_input",
                content=content,
                disposition=disposition,
                project=project
            )
            
            result_text = f"✅ Added to Peacock Memory\n"
            result_text += f"📁 Collection: {collection_name}\n"
            result_text += f"🏷️ Disposition: {disposition}\n"
            result_text += f"📊 Content: {len(content)} characters\n"
            
            if project:
                result_text += f"🏷️ Project: {project}\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            debug_log("Add memory error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Add memory error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _list_projects(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List projects implementation"""
        try:
            from core.database import get_all_projects
            
            projects = get_all_projects()
            
            if not projects:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "No projects found in Peacock Memory"
                        }
                    ]
                }
            
            result_text = f"📁 Peacock Memory Projects ({len(projects)} total)\n\n"
            
            for i, project in enumerate(projects, 1):
                created_date = project.get('created', 'Unknown')[:10] if project.get('created') else 'Unknown'
                
                result_text += f"🔸 Project #{i}: {project['name']}\n"
                result_text += f"📝 Description: {project['description'] or 'No description'}\n"
                result_text += f"📊 Items: {project['item_count']}\n"
                result_text += f"📅 Created: {created_date}\n"
                result_text += "─" * 40 + "\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            debug_log("List projects error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"List projects error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming MCP request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        debug_log("Handling request", method=method, id=request_id)
        
        try:
            # Handle notifications (no response needed)
            if method == "notifications/initialized":
                await self.handle_notifications_initialized(params)
                return None
            
            # Handle requests that need responses
            if method == "initialize":
                result = await self.handle_initialize(params)
            elif method == "tools/list":
                result = await self.handle_tools_list(params)
            elif method == "tools/call":
                result = await self.handle_tools_call(params)
            else:
                debug_log("Unknown method", method=method)
                # Only return error response if this was a request (has id)
                if request_id is not None:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                return None
            
            # Only return response if this was a request (has id)
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            return None
            
        except Exception as e:
            debug_log("Request handling error", error=str(e))
            # Only return error response if this was a request (has id)
            if request_id is not None:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
            return None

async def main():
    """Main MCP server loop"""
    debug_log("🦚 Peacock Memory MCP Server starting...")
    
    server = MCPServer()
    
    try:
        while True:
            # Read line from stdin
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            
            if not line:
                debug_log("EOF received, shutting down")
                break
            
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse JSON-RPC request
                request = json.loads(line)
                debug_log("Received request", request=request)
                
                # Handle request
                response = await server.handle_request(request)
                
                if response:
                    # Send response
                    response_json = json.dumps(response)
                    print(response_json, flush=True)
                    debug_log("Sent response", response=response)
                
            except json.JSONDecodeError as e:
                debug_log("JSON decode error", error=str(e), line=line)
                continue
            except Exception as e:
                debug_log("Request processing error", error=str(e))
                continue
    
    except KeyboardInterrupt:
        debug_log("🦚 Peacock Memory MCP shutting down...")
    except Exception as e:
        debug_log("Fatal error", error=str(e))

if __name__ == "__main__":
    asyncio.run(main())