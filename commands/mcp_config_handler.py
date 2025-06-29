"""
🦚 Peacock Memory - MCP Config Handler
Configure Claude Desktop for MCP integration
"""

import json
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from commands.base_command import BaseCommand

class MCPConfigHandler(BaseCommand):
    """Handle MCP configuration for Claude Desktop"""
    
    def get_aliases(self) -> List[str]:
        return ["mcp-config", "mcp-setup", "configure-mcp"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute MCP config command"""
        return self._configure_claude_desktop()
    
    def _configure_claude_desktop(self) -> str:
        """Configure Claude Desktop for MCP integration"""
        try:
            # Get Claude config path
            config_path = self._get_claude_config_path()
            
            if not config_path:
                return self.format_error([
                    "❌ Could not find Claude Desktop config directory",
                    "💡 Make sure Claude Desktop is installed",
                    "📁 Expected path: ~/.config/Claude/"
                ])
            
            config_file = config_path / "claude_desktop_config.json"
            
            # Backup existing config
            backup_result = self._backup_existing_config(config_file)
            
            # Create new config
            new_config = self._create_mcp_config()
            
            # Write config file
            config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2)
            
            success_msgs = [
                "✅ Claude Desktop MCP configuration complete!",
                f"📁 Config written to: {config_file}",
                "",
                "🔧 Configuration details:",
                "  - Server: peacock-memory-mcp",
                "  - Host: 127.0.0.1:8000",
                "  - Protocol: HTTP REST",
                "",
                "🚀 Next steps:",
                "1. Start MCP server: pea-mem → mcp",
                "2. Restart Claude Desktop",
                "3. MCP server will be available in Claude"
            ]
            
            if backup_result:
                success_msgs.insert(2, backup_result)
            
            return self.format_success(success_msgs)
            
        except Exception as e:
            return self.format_error([
                f"❌ Error configuring Claude Desktop: {str(e)}",
                "💡 Make sure you have write permissions to ~/.config/Claude/"
            ])
    
    def _get_claude_config_path(self) -> Optional[Path]:
        """Get Claude Desktop config path"""
        # Check common locations
        possible_paths = [
            Path.home() / ".config" / "Claude",
            Path.home() / "Library" / "Application Support" / "Claude",  # macOS
            Path.home() / "AppData" / "Roaming" / "Claude"  # Windows
        ]
        
        for path in possible_paths:
            if path.exists() or path.parent.exists():
                return path
        
        # Default to ~/.config/Claude
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
    
    def _create_mcp_config(self) -> dict:
        """Create MCP configuration for Claude Desktop"""
        return {
            "mcpServers": {
                "peacock-memory": {
                    "command": "python",
                    "args": [
                        "-c",
                        "import sys; sys.path.append('.'); from commands.mcp_handler import MCPHandler; MCPHandler().execute('mcp')"
                    ],
                    "env": {
                        "PEACOCK_MCP_HOST": "127.0.0.1",
                        "PEACOCK_MCP_PORT": "8000"
                    }
                }
            },
            "defaultModel": "claude-3-sonnet-20240229",
            "appearance": "dark"
        }
    
    def _get_system_info(self) -> dict:
        """Get system information for config"""
        import platform
        import sys
        
        return {
            "platform": platform.system(),
            "python_version": sys.version,
            "python_executable": sys.executable,
            "config_timestamp": datetime.now().isoformat()
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
  3. Creates new config with Peacock Memory MCP server
  4. Sets up proper connection parameters

Configuration Details:
  - Server name: peacock-memory
  - Protocol: HTTP REST (not stdio MCP)
  - Host: 127.0.0.1:8000
  - Auto-discovery of Python executable

File Locations:
  - Linux: ~/.config/Claude/claude_desktop_config.json
  - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json
  - Windows: ~/AppData/Roaming/Claude/claude_desktop_config.json

Setup Process:
  1. Run: pea-mem → mcp-config
  2. Start MCP server: pea-mem → mcp
  3. Restart Claude Desktop
  4. MCP server appears in Claude's available tools

Features:
  - Automatic backup of existing config
  - Cross-platform path detection
  - Error handling and validation
  - Timestamped backups

Troubleshooting:
  - Ensure Claude Desktop is installed
  - Check file permissions in config directory
  - Verify MCP server starts without errors
  - Restart Claude Desktop after configuration
        """
        return