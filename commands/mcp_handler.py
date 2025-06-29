"""
🦚 Peacock Memory - MCP Handler
Launch MCP server with minimal output for Claude Desktop compatibility
"""

import subprocess
import sys
import os
import signal
from typing import List, Optional
from pathlib import Path

from commands.base_command import BaseCommand
from core.database import get_client

class MCPHandler(BaseCommand):
    """Handle MCP server commands"""
    
    def __init__(self):
        super().__init__()
        self.server_process = None
    
    def get_aliases(self) -> List[str]:
        return ["mcp"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute MCP command"""
        # NO VISUALS - direct server start for Claude Desktop compatibility
        return self._start_mcp_server()
    
    def _start_mcp_server(self) -> str:
        """Start the MCP server with minimal output"""
        try:
            # Check if required dependencies are available
            missing_deps = self._check_dependencies()
            if missing_deps:
                print(f"Missing dependencies: {', '.join(missing_deps)}", file=sys.stderr)
                return ""
            
            # Start FastAPI server immediately - no visual noise
            self._run_mcp_server()
            
            return ""  # No return message for MCP mode
            
        except KeyboardInterrupt:
            print("MCP Server stopped", file=sys.stderr)
            return ""
        except Exception as e:
            print(f"MCP Server error: {str(e)}", file=sys.stderr)
            return ""
    
    def _check_dependencies(self) -> List[str]:
        """Check for required dependencies"""
        missing = []
        
        try:
            import fastapi
        except ImportError:
            missing.append("fastapi")
        
        try:
            import uvicorn
        except ImportError:
            missing.append("uvicorn")
        
        return missing
    
    def _get_database_info(self) -> dict:
        """Get database information"""
        try:
            client = get_client()
            collections = client.list_collections()
            
            total_docs = 0
            for collection_info in collections:
                collection = client.get_collection(collection_info.name)
                all_data = collection.get()
                total_docs += len(all_data["documents"]) if all_data["documents"] else 0
            
            return {
                "db_path": str(Path.home() / "peacock_db"),
                "collections": len(collections),
                "documents": total_docs
            }
        except Exception:
            return {
                "db_path": str(Path.home() / "peacock_db"),
                "collections": 0,
                "documents": 0
            }
    
    def _run_mcp_server(self):
        """Run the actual MCP server with no visual output"""
        import uvicorn
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import JSONResponse
        import json
        
        app = FastAPI(
            title="🦚 Peacock Memory MCP Server",
            description="Model Context Protocol server for Peacock Memory System",
            version="1.0.0"
        )
        
        @app.get("/")
        def root():
            return {
                "name": "peacock-memory-mcp",
                "version": "1.0.0",
                "description": "🦚 Peacock Memory MCP Server",
                "status": "running"
            }
        
        @app.get("/health")
        def health():
            stats = self._get_database_info()
            return {
                "status": "healthy",
                "database": "connected",
                "collections": stats["collections"],
                "documents": stats["documents"],
                "db_path": stats["db_path"]
            }
        
        @app.get("/collections")
        def list_collections():
            try:
                client = get_client()
                collections = client.list_collections()
                return {
                    "collections": [
                        {
                            "name": c.name,
                            "metadata": c.metadata
                        } for c in collections
                    ],
                    "count": len(collections)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/search")
        def search_memory(query: dict):
            try:
                from core.database import search_all_collections
                
                search_query = query.get("query", "")
                limit = query.get("limit", 10)
                
                if not search_query:
                    raise HTTPException(status_code=400, detail="Query is required")
                
                results = search_all_collections(search_query, limit)
                
                return {
                    "query": search_query,
                    "results": results,
                    "count": len(results)
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/add_memory")
        def add_memory(memory: dict):
            try:
                from core.database import add_file_to_collection
                
                content = memory.get("content", "")
                disposition = memory.get("disposition", "Note")
                file_path = memory.get("file_path", "mcp_input")
                project = memory.get("project")
                
                if not content:
                    raise HTTPException(status_code=400, detail="Content is required")
                
                collection_name = f"project_{project}" if project else "global_files"
                
                file_id = add_file_to_collection(
                    collection_name=collection_name,
                    file_path=file_path,
                    content=content,
                    disposition=disposition,
                    project=project
                )
                
                return {
                    "status": "success",
                    "file_id": file_id,
                    "collection": collection_name
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        
        # Handle graceful shutdown
        def signal_handler(sig, frame):
            print("MCP Server shutting down...", file=sys.stderr)
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start server with minimal logging
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000,
            log_level="error"  # Minimal logging
        )
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 MCP Handler - Model Context Protocol Server

Usage:
  mcp                      Start MCP server (no visuals for Claude Desktop)

Server Info:
  - Host: 127.0.0.1
  - Port: 8000
  - Protocol: HTTP/REST
  - Database: ChromaDB (~/peacock_db)
        """
        return self.format_info([help_text.strip()])
