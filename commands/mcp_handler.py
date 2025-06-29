"""
🦚 Peacock Memory - MCP Handler
Launch proper MCP server (JSON-RPC over stdio)
"""

import subprocess
import sys
import os
from typing import List, Optional
from pathlib import Path

from commands.base_command import BaseCommand

class MCPHandler(BaseCommand):
    """Handle MCP server commands"""
    
    def get_aliases(self) -> List[str]:
        return ["mcp"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute MCP command"""
        return self._start_mcp_server()
    
    def _start_mcp_server(self) -> str:
        """Start the proper MCP server"""
        try:
            # Path to the proper MCP server
            server_path = Path(__file__).parent.parent / "mcp_server_proper.py"
            
            if not server_path.exists():
                return self.format_error([
                    "❌ MCP server file not found",
                    f"Expected: {server_path}",
                    "💡 Make sure mcp_server_proper.py exists"
                ])
            
            # Check dependencies
            missing_deps = self._check_dependencies()
            if missing_deps:
                return self.format_error([
                    f"❌ Missing dependencies: {', '.join(missing_deps)}",
                    "💡 Run: pip install -r requirements.txt"
                ])
            
            # Start the server
            success_msgs = [
                "🦚 Starting Peacock Memory MCP Server...",
                f"📁 Server: {server_path}",
                "🔌 Protocol: JSON-RPC over stdio",
                "",
                "🚀 Server starting in background...",
                "💡 Check Claude Desktop for MCP connection",
                "",
                "⚠️ Server will run until you close this terminal",
                "   Press Ctrl+C to stop the server"
            ]
            
            print(self.format_success(success_msgs))
            
            # Execute the server (this will block)
            try:
                subprocess.run([sys.executable, str(server_path)], check=True)
            except KeyboardInterrupt:
                return self.format_info(["🦚 MCP Server stopped"])
            except subprocess.CalledProcessError as e:
                return self.format_error([
                    f"❌ MCP Server failed: {e}",
                    "💡 Check the logs above for details"
                ])
            
            return ""
            
        except Exception as e:
            return self.format_error([
                f"❌ Error starting MCP server: {str(e)}",
                "💡 Check that all dependencies are installed"
            ])
    
    def _check_dependencies(self) -> List[str]:
        """Check for required dependencies"""
        missing = []
        
        try:
            import chromadb
        except ImportError:
            missing.append("chromadb")
        
        return missing
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 MCP Handler - Model Context Protocol Server

Usage:
  mcp                      Start MCP server (proper JSON-RPC protocol)

Server Info:
  - Protocol: JSON-RPC over stdio (proper MCP)
  - Database: ChromaDB (~/peacock_db)
  - Tools: search_memory, add_memory, list_projects

Setup Process:
  1. Run: pea-mem → mcp-config (configure Claude Desktop)
  2. Run: pea-mem → mcp (start server)
  3. Restart Claude Desktop
  4. MCP tools available in Claude

Troubleshooting:
  - Ensure Claude Desktop is configured (mcp-config)
  - Check that ChromaDB is accessible
  - Verify no port conflicts (this uses stdio, not HTTP)
  - Restart Claude Desktop after configuration changes
        """
        return self.format_info([help_text.strip()])