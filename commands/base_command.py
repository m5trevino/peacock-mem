"""
🦚 Peacock Memory - Base Command Interface
Abstract base class for all command handlers
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from core.visuals import format_grouped_output, format_single_message

class BaseCommand(ABC):
    """Base class for all command handlers"""
    
    def __init__(self):
        self.name = self.__class__.__name__.replace("Handler", "").lower()
        self.aliases = []
    
    @abstractmethod
    def get_aliases(self) -> List[str]:
        """Return list of command aliases this handler responds to"""
        pass
    
    @abstractmethod
    def execute(self, command_input: str) -> Optional[str]:
        """Execute the command and return formatted output"""
        pass
    
    @abstractmethod
    def get_help(self) -> str:
        """Return help text for this command"""
        pass
    
    def format_success(self, messages: List[str]) -> str:
        """Format success messages"""
        return format_grouped_output(messages, "success")
    
    def format_error(self, messages: List[str]) -> str:
        """Format error messages"""
        return format_grouped_output(messages, "error")
    
    def format_info(self, messages: List[str]) -> str:
        """Format info messages"""
        return format_grouped_output(messages, "info")
    
    def format_warning(self, messages: List[str]) -> str:
        """Format warning messages"""
        return format_grouped_output(messages, "warning")
    
    def format_data(self, messages: List[str]) -> str:
        """Format data messages"""
        return format_grouped_output(messages, "data")
    
    def format_progress(self, messages: List[str]) -> str:
        """Format progress messages"""
        return format_grouped_output(messages, "progress")
    
    def parse_arguments(self, command_input: str) -> Dict[str, Any]:
        """Parse command arguments - override in subclasses as needed"""
        parts = command_input.strip().split()
        return {
            "command": parts[0] if parts else "",
            "args": parts[1:] if len(parts) > 1 else []
        }
    
    def validate_input(self, command_input: str) -> bool:
        """Validate command input - override in subclasses as needed"""
        return bool(command_input.strip())
    
    def matches_command(self, command_input: str) -> bool:
        """Check if this handler matches the given command"""
        if not command_input:
            return False
            
        command_word = command_input.strip().split()[0].lower()
        aliases = [alias.lower() for alias in self.get_aliases()]
        
        return command_word in aliases