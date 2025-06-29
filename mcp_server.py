#!/usr/bin/env python3
"""
🦚 Peacock Memory - MCP Server (HTTP-based like your working example)
"""

import json
import sys
import time
import threading
import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Configuration
HOST = "127.0.0.1"
PORT = 8000
START_TIME = time.time()

def debug_log(level, message, **data):
    """Debug logging like your working MCP"""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    elapsed = time.time() - START_TIME
    log_line = f"[{timestamp}] [{level}] {message}"
    if data:
        log_line += f" | {data}"
    log_line += f" | +{elapsed:.1f}s"
    print(log_line, file=sys.stderr)

class PeacockMemoryHandler(BaseHTTPRequestHandler):
    """HTTP handler for Peacock Memory MCP"""
    
    def log_message(self, format, *args):
        """Override logging"""
        debug_log("HTTP", f"{self.command} {self.path} -> {args[1] if len(args) > 1 else '200'}")

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle POST requests"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))
            
            endpoint = self.path
            debug_log("REQUEST", f"Processing {endpoint}")
            
            if endpoint == "/search":
                result = self.handle_search(request_data)
            elif endpoint == "/add":
                result = self.handle_add(request_data)
            elif endpoint == "/health":
                result = self.handle_health()
            else:
                result = {"success": False, "error": f"Unknown endpoint: {endpoint}"}
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response_json = json.dumps(result, indent=2)
            self.wfile.write(response_json.encode('utf-8'))
            
            debug_log("RESPONSE", f"Completed {endpoint}", success=result.get("success", False))
            
        except Exception as e:
            debug_log("ERROR", f"Request error: {e}")
            self.send_error(500, f"Internal Server Error: {str(e)}")

    def handle_search(self, request_data):
        """Handle search requests"""
        try:
            from core.database import search_all_collections
            
            query = request_data.get('query', '')
            limit = request_data.get('limit', 10)
            
            if not query:
                return {"success": False, "error": "Query required"}
            
            debug_log("SEARCH", f"Searching for: {query}")
            results = search_all_collections(query, limit)
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            debug_log("ERROR", f"Search error: {e}")
            return {"success": False, "error": str(e)}

    def handle_add(self, request_data):
        """Handle add memory requests"""
        try:
            from core.database import add_file_to_collection
            
            content = request_data.get('content', '')
            disposition = request_data.get('disposition', 'Note')
            project = request_data.get('project')
            
            if not content:
                return {"success": False, "error": "Content required"}
            
            collection_name = f"project_{project}" if project else "global_files"
            
            file_id = add_file_to_collection(
                collection_name=collection_name,
                file_path="mcp_input",
                content=content,
                disposition=disposition,
                project=project
            )
            
            debug_log("ADD", f"Added to {collection_name}")
            
            return {
                "success": True,
                "file_id": file_id,
                "collection": collection_name
            }
            
        except Exception as e:
            debug_log("ERROR", f"Add error: {e}")
            return {"success": False, "error": str(e)}

    def handle_health(self):
        """Handle health check"""
        try:
            from core.database import get_client
            
            client = get_client()
            collections = client.list_collections()
            
            return {
                "success": True,
                "status": "healthy",
                "collections": len(collections),
                "uptime": f"{time.time() - START_TIME:.1f}s"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

def start_server():
    """Start the HTTP server"""
    debug_log("INIT", f"Starting Peacock Memory MCP on {HOST}:{PORT}")
    
    server = HTTPServer((HOST, PORT), PeacockMemoryHandler)
    
    def run_server():
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            debug_log("SHUTDOWN", "Server stopping...")
            server.shutdown()
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    return server

def main():
    """Main entry point"""
    debug_log("INIT", "🦚 Peacock Memory MCP Server starting...")
    
    # Start server
    server = start_server()
    
    try:
        debug_log("READY", "Server ready - Press Ctrl+C to stop")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        debug_log("SHUTDOWN", "🦚 Peacock Memory MCP shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
