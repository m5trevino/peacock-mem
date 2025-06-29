"""
🦚 Peacock Memory - MCP Config Handler
Configure Claude Desktop for proper MCP integration
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import sys

from commands.base_command import BaseCommand

class MCPConfigHandler(BaseCommand):
    """Handle MCP configuration for Claude Desktop"""
    
    def get_aliases(self) -> List[str]:
        return ["mcp-config", "mcp-setup", "configure-mcp"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute MCP config command"""
        return self._configure_claude_desktop()
    
    def _configure_claude_desktop(self) -> str:
        """Configure Claude Desktop for proper MCP integration"""
        try:
            # Get Claude config path
            config_path = self._get_claude_config_path()
            
            if not config_path:
                return self.format_error([
                    "❌ Could not find Claude Desktop config directory",
                    "💡 Make sure Claude Desktop is installed",
                    "📁 Expected paths:",
                    "   Linux: ~/.config/Claude/",
                    "   macOS: ~/Library/Application Support/Claude/",
                    "   Windows: ~/AppData/Roaming/Claude/"
                ])
            
            config_file = config_path / "claude_desktop_config.json"
            
            # Backup existing config
            backup_result = self._backup_existing_config(config_file)
            
            # Create new config with proper MCP setup
            new_config = self._create_proper_mcp_config()
            
            # Write config file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2)
            
            success_msgs = [
                "✅ Claude Desktop MCP configuration complete!",
                f"📁 Config written to: {config_file}",
                "",
                "🔧 Configuration details:",
                "  - Server: peacock-memory",
                "  - Protocol: JSON-RPC over stdio (proper MCP)",
                "  - Command: python mcp_server_proper.py",
                "",
                "🚀 Next steps:",
                "1. Start MCP server: pea-mem → mcp",
                "2. Restart Claude Desktop",
                "3. MCP tools will be available in Claude",
                "",
                "🛠️ Available MCP Tools:",
                "  - search_memory: Search Peacock Memory database",
                "  - add_memory: Add content to memory",
                "  - list_projects: List all projects"
            ]
            
            if backup_result:
                success_msgs.insert(2, backup_result)
            
            return self.format_success(success_msgs)
            
        except Exception as e:
            return self.format_error([
                f"❌ Error configuring Claude Desktop: {str(e)}",
                "💡 Make sure you have write permissions to the config directory"
            ])
    
    def _get_claude_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path"""
        # Check common locations
        possible_paths = [
            Path.home() / ".config" / "Claude",  # Linux
            Path.home() / "Library" / "Application Support" / "Claude",  # macOS
            Path.home() / "AppData" / "Roaming" / "Claude"  # Windows
        ]
        
        for path in possible_paths:
            if path.exists() or path.parent.exists():
                return path
        
        # Default to Linux path
        return Path.home() / ".config" / "Claude"
    
    def _backup_existing_config(self, config_file: Path) -> Optional[str]:
        """Backup existing config file"""
        if not config_file.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = config_file.parent / f"claude_desktop_config_backup_{timestamp}.json"
        
        try:
            shutil.copy2(config_file, backup_file)
            return f"💾 Backed up existing config to: {backup_file.name}"
        except Exception as e:
            return f"⚠️ Could not backup config: {str(e)}"
    
    def _create_proper_mcp_config(self) -> dict:
        """Create proper MCP configuration for Claude Desktop"""
        # Get the path to the MCP server
        server_path = Path(__file__).parent.parent / "mcp_server_proper.py"
        
        return {
            "mcpServers": {
                "peacock-memory": {
                    "command": sys.executable,
                    "args": [str(server_path.absolute())],
                    "env": {}
                }
            }
        }
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 MCP Config Handler - Claude Desktop Integration

Usage:
  mcp-config               Configure Claude Desktop for MCP
  mcp-setup                Same as mcp-config
  configure-mcp            Alternative alias

What this does:
  1. Locates Claude Desktop config directory
  2. Backs up existing claude_desktop_config.json
  3. Creates new config with proper MCP server setup
  4. Uses JSON-RPC over stdio (proper MCP protocol)

Configuration Details:
  - Server name: peacock-memory
  - Protocol: JSON-RPC over stdio (not HTTP)
  - Command: python mcp_server_proper.py
  - Auto-discovery of Python executable

File Locations:
  - Linux: ~/.config/Claude/claude_desktop_config.json
  - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
  - Windows: ~/AppData/Roaming/Claude/claude_desktop_config.json

Setup Process:
  1. Run: pea-mem → mcp-config
  2. Start MCP server: pea-mem → mcp
  3. Restart Claude Desktop
  4. MCP tools appear in Claude's available tools

Available MCP Tools:
  - search_memory: Search through your memory database
  - add_memory: Add new content to memory
  - list_projects: List all your projects

Troubleshooting:
  - Ensure Claude Desktop is installed
  - Check file permissions in config directory
  - Verify MCP server starts without errors
  - Restart Claude Desktop after configuration
  - Check Claude Desktop logs for connection issues
        """
        return self.format_info([help_text.strip()])