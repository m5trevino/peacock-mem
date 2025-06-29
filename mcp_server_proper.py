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
                        },
                        "scope": {
                            "type": "string",
                            "description": "Search scope",
                            "enum": ["everything", "codebase", "conversations", "ideas", "brainstorm", "notes", "manpages"],
                            "default": "everything"
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
            },
            {
                "name": "view_file",
                "description": "View complete content of a specific file from memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Search for file by name or content to identify which file to view"
                        },
                        "file_index": {
                            "type": "integer",
                            "description": "Index of file from search results to view (1-based)",
                            "default": 1
                        }
                    },
                    "required": ["search_query"]
                }
            },
            {
                "name": "list_files",
                "description": "List files by category or project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Category to list",
                            "enum": ["codebase", "conversations", "ideas", "brainstorm", "notes", "manpages", "all"],
                            "default": "all"
                        },
                        "project": {
                            "type": "string",
                            "description": "Specific project name to list files from (optional)"
                        }
                    }
                }
            },
            {
                "name": "delete_item",
                "description": "Delete specific item from memory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "search_query": {
                            "type": "string",
                            "description": "Search query to find item to delete"
                        },
                        "confirm": {
                            "type": "boolean",
                            "description": "Confirmation that you want to delete the item",
                            "default": false
                        }
                    },
                    "required": ["search_query", "confirm"]
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
            elif tool_name == "view_file":
                return await self._view_file(arguments)
            elif tool_name == "list_files":
                return await self._list_files(arguments)
            elif tool_name == "delete_item":
                return await self._delete_item(arguments)
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
            from core.database import search_all_collections, search_by_type
            
            query = args.get("query", "")
            limit = args.get("limit", 10)
            scope = args.get("scope", "everything")
            
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
            
            if scope == "everything":
                results = search_all_collections(query, limit)
            else:
                results = search_by_type(query, scope, limit)
            
            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No results found for: {query} in scope: {scope}"
                        }
                    ]
                }
            
            # Format results
            result_text = f"🔍 Search Results for: '{query}' (Scope: {scope})\n\n"
            
            for i, result in enumerate(results, 1):
                collection = result['collection'].replace('project_', '').replace('_', ' ').title()
                relevance = f"{result['relevance']:.3f}"
                metadata = result.get('metadata', {})
                
                result_text += f"🔸 Result #{i} (Relevance: {relevance})\n"
                result_text += f"📁 Collection: {collection}\n"
                
                if metadata.get('file_path'):
                    filename = metadata['file_path'].split('/')[-1]
                    result_text += f"📄 File: {filename}\n"
                    if metadata.get('language'):
                        result_text += f"💻 Language: {metadata['language']}\n"
                
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
    
    async def _view_file(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """View file implementation"""
        try:
            from core.database import search_all_collections
            
            search_query = args.get("search_query", "")
            file_index = args.get("file_index", 1)
            
            if not search_query:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Search query is required to find file"
                        }
                    ],
                    "isError": True
                }
            
            # Search for files
            results = search_all_collections(search_query, 10)
            
            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No files found matching: {search_query}"
                        }
                    ]
                }
            
            if file_index < 1 or file_index > len(results):
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"File index {file_index} out of range. Found {len(results)} files."
                        }
                    ],
                    "isError": True
                }
            
            # Get the selected file
            selected_file = results[file_index - 1]
            metadata = selected_file.get('metadata', {})
            
            # Build full content view
            result_text = f"📄 VIEWING FILE #{file_index}\n"
            result_text += "═" * 60 + "\n\n"
            
            # File info
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                result_text += f"📁 File: {filename}\n"
                result_text += f"📂 Path: {metadata['file_path']}\n"
                if metadata.get('language'):
                    result_text += f"💻 Language: {metadata['language']}\n"
                if metadata.get('lines'):
                    result_text += f"📊 Lines: {metadata['lines']}\n"
            
            if metadata.get('disposition'):
                result_text += f"🏷️ Type: {metadata['disposition']}\n"
            
            if metadata.get('created'):
                result_text += f"📅 Created: {metadata['created'][:19].replace('T', ' ')}\n"
            
            collection = selected_file['collection'].replace('project_', '').replace('_', ' ').title()
            result_text += f"🗂️ Collection: {collection}\n"
            
            result_text += "\n" + "═" * 60 + "\n"
            result_text += "📄 FULL CONTENT:\n"
            result_text += "═" * 60 + "\n\n"
            
            # Add content with line numbers for code
            content = selected_file['document']
            if metadata.get('language') and metadata.get('language') != 'unknown':
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    result_text += f"{i:4d} | {line}\n"
            else:
                result_text += content
            
            result_text += "\n" + "═" * 60
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            debug_log("View file error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"View file error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _list_files(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """List files implementation"""
        try:
            from core.database import list_by_type, get_project_contents, get_client
            
            category = args.get("category", "all")
            project = args.get("project")
            
            if project:
                # List files in specific project
                contents = get_project_contents(project)
                if contents['count'] == 0:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"No files found in project: {project}"
                            }
                        ]
                    }
                
                result_text = f"📁 Files in Project: {project} ({contents['count']} items)\n\n"
                
                for i, item in enumerate(contents['items'], 1):
                    metadata = item.get('metadata', {})
                    
                    if metadata.get('file_path'):
                        filename = metadata['file_path'].split('/')[-1]
                        language = metadata.get('language', 'unknown')
                        lines = metadata.get('lines', 'unknown')
                        result_text += f"🔸 #{i} 📄 {filename} ({language}, {lines} lines)\n"
                    else:
                        disposition = metadata.get('disposition', 'Unknown')
                        result_text += f"🔸 #{i} 📝 {disposition}\n"
                    
                    result_text += f"   Preview: {item['preview']}\n\n"
                
            elif category == "all":
                # List all files
                client = get_client()
                collections = client.list_collections()
                
                all_items = []
                for collection_info in collections:
                    collection = client.get_collection(collection_info.name)
                    try:
                        all_data = collection.get()
                        if all_data["documents"]:
                            for i, doc in enumerate(all_data["documents"]):
                                metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}
                                all_items.append({
                                    "collection": collection_info.name,
                                    "metadata": metadata,
                                    "preview": doc[:100] + "..." if len(doc) > 100 else doc
                                })
                    except:
                        continue
                
                if not all_items:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": "No files found"
                            }
                        ]
                    }
                
                result_text = f"🌐 All Files ({len(all_items)} total)\n\n"
                
                for i, item in enumerate(all_items, 1):
                    metadata = item.get('metadata', {})
                    collection = item['collection'].replace('project_', '').replace('_', ' ').title()
                    
                    if metadata.get('file_path'):
                        filename = metadata['file_path'].split('/')[-1]
                        result_text += f"🔸 #{i} 📄 {filename} | {collection}\n"
                    else:
                        disposition = metadata.get('disposition', 'Unknown')
                        result_text += f"🔸 #{i} 📝 {disposition} | {collection}\n"
                    
                    result_text += f"   Preview: {item['preview']}\n\n"
                
            else:
                # List by category
                items = list_by_type(category)
                
                if not items:
                    return {
                        "content": [
                            {
                                "type": "text",
                                "text": f"No {category} files found"
                            }
                        ]
                    }
                
                result_text = f"📋 {category.title()} Files ({len(items)} total)\n\n"
                
                for i, item in enumerate(items, 1):
                    metadata = item.get('metadata', {})
                    collection = item['collection'].replace('project_', '').replace('_', ' ').title()
                    
                    if metadata.get('file_path'):
                        filename = metadata['file_path'].split('/')[-1]
                        language = metadata.get('language', 'unknown')
                        result_text += f"🔸 #{i} 📄 {filename} ({language}) | {collection}\n"
                    else:
                        result_text += f"🔸 #{i} 📝 {metadata.get('disposition', 'Unknown')} | {collection}\n"
                    
                    result_text += f"   Preview: {item['preview']}\n\n"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result_text
                    }
                ]
            }
            
        except Exception as e:
            debug_log("List files error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"List files error: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _delete_item(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Delete item implementation"""
        try:
            from core.database import search_all_collections, delete_item
            
            search_query = args.get("search_query", "")
            confirm = args.get("confirm", False)
            
            if not search_query:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Search query is required to find item to delete"
                        }
                    ],
                    "isError": True
                }
            
            if not confirm:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "⚠️ Deletion requires explicit confirmation. Set 'confirm' to true to proceed."
                        }
                    ],
                    "isError": True
                }
            
            # Search for items
            results = search_all_collections(search_query, 5)
            
            if not results:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"No items found matching: {search_query}"
                        }
                    ]
                }
            
            if len(results) > 1:
                result_text = f"⚠️ Found {len(results)} items matching '{search_query}':\n\n"
                for i, result in enumerate(results, 1):
                    metadata = result.get('metadata', {})
                    if metadata.get('file_path'):
                        filename = metadata['file_path'].split('/')[-1]
                        result_text += f"{i}. 📄 {filename}\n"
                    else:
                        result_text += f"{i}. 📝 {metadata.get('disposition', 'Unknown')}\n"
                    result_text += f"   Preview: {result['preview']}\n\n"
                
                result_text += "Please be more specific in your search query to target a single item."
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            
            # Delete the single matching item
            item = results[0]
            
            # Extract collection and ID from the search result
            # We need to find the actual item in the collection
            from core.database import get_client
            client = get_client()
            collection = client.get_collection(item['collection'])
            all_data = collection.get()
            
            # Find the item by content match
            item_id = None
            for i, doc in enumerate(all_data["documents"]):
                if doc == item['document']:
                    item_id = all_data["ids"][i]
                    break
            
            if not item_id:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Could not find item ID for deletion"
                        }
                    ],
                    "isError": True
                }
            
            # Perform deletion
            success = delete_item(item['collection'], item_id)
            
            if success:
                metadata = item.get('metadata', {})
                item_name = metadata.get('file_path', metadata.get('disposition', 'Unknown item'))
                
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"✅ Successfully deleted: {item_name}\nFrom collection: {item['collection']}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "❌ Failed to delete item"
                        }
                    ],
                    "isError": True
                }
            
        except Exception as e:
            debug_log("Delete item error", error=str(e))
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Delete item error: {str(e)}"
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