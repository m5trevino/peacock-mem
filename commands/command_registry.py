"""
🦚 Peacock Memory - Command Registry
Auto-discovery and routing for modular commands
"""

import importlib
import pkgutil
from typing import Dict, List, Optional
from pathlib import Path

from commands.base_command import BaseCommand
from commands.import_handler import ImportHandler
from commands.search_handler import SearchHandler
from commands.list_handler import ListHandler
from commands.project_handler import ProjectHandler
from commands.delete_handler import DeleteHandler
from commands.mcp_handler import MCPHandler
from commands.file_handler import FileHandler
from commands.mcp_config_handler import MCPConfigHandler
from core.visuals import format_single_message

class CommandRegistry:
    """Registry for auto-discovering and routing commands"""
    
    def __init__(self):
        self.handlers: Dict[str, BaseCommand] = {}
        self.aliases: Dict[str, str] = {}
        self._load_handlers()
    
    def _load_handlers(self):
        """Load all command handlers"""
        # Manually instantiate handlers (can be made auto-discovery later)
        handler_classes = [
            ImportHandler,
            SearchHandler,
            ListHandler,
            ProjectHandler,
            DeleteHandler,
            MCPHandler,
            FileHandler,
            MCPConfigHandler
        ]
        
        for handler_class in handler_classes:
            try:
                handler = handler_class()
                handler_name = handler.__class__.__name__
                self.handlers[handler_name] = handler
                
                # Register aliases
                for alias in handler.get_aliases():
                    self.aliases[alias.lower()] = handler_name
                    
            except Exception as e:
                print(f"Failed to load handler {handler_class.__name__}: {e}")
    
    def get_handler(self, command_input: str) -> Optional[BaseCommand]:
        """Get appropriate handler for command"""
        if not command_input:
            return None
            
        # Check for @ commands (file handler)
        if command_input.strip().startswith('@'):
            return self.handlers.get('FileHandler')
        
        # Extract command word
        command_word = command_input.strip().split()[0].lower()
        
        # Find handler by alias
        handler_name = self.aliases.get(command_word)
        if handler_name:
            return self.handlers.get(handler_name)
        
        return None
    
    def execute_command(self, command_input: str) -> Optional[str]:
        """Execute command through appropriate handler"""
        if not command_input.strip():
            return None
        
        handler = self.get_handler(command_input)
        if not handler:
            return format_single_message(
                f"Unknown command: {command_input.split()[0]}. Type 'help' for available commands.",
                "error"
            )
        
        try:
            return handler.execute(command_input)
        except Exception as e:
            return format_single_message(
                f"Error executing command: {str(e)}",
                "error"
            )
    
    def get_all_commands(self) -> Dict[str, List[str]]:
        """Get all available commands and their aliases"""
        commands = {}
        for handler_name, handler in self.handlers.items():
            commands[handler_name] = handler.get_aliases()
        return commands
    
    def get_help(self, command: Optional[str] = None) -> str:
        """Get help for specific command or all commands"""
        if command:
            handler = self.get_handler(command)
            if handler:
                return handler.get_help()
            else:
                return format_single_message(f"Unknown command: {command}", "error")
        
        # Return help for all commands
        help_lines = [
            "🦚 Peacock Memory - Available Commands:",
            "",
            "📁 File Management:",
            "  @/path/to/file.py    - Add single file",
            "  @/path/to/dir/       - Add directory (interactive)",
            "",
            "📥 Import:",
            "  import               - Import JSON files (Claude/ChatGPT/Projects)",
            "",
            "🔍 Search:",
            "  search               - Search through memory",
            "",
            "📋 List:",
            "  list                 - List items by category",
            "",
            "📁 Projects:",
            "  projects, project    - Browse/create projects",
            "",
            "🗑️ Delete:",
            "  delete, remove       - Delete items",
            "",
            "🌐 MCP:",
            "  mcp                  - Start MCP server",
            "  mcp-config           - Configure Claude Desktop for MCP",
            "",
            "Type any command for interactive menus!"
        ]
        
        return format_single_message("\n".join(help_lines), "info")