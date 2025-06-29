"""
🦚 Peacock Memory - Delete Handler
Interactive deletion with multiple options
"""

from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import (
    get_all_projects, 
    get_project_contents, 
    list_by_type, 
    delete_item, 
    delete_collection,
    get_client
)

class DeleteHandler(BaseCommand):
    """Handle delete and remove commands"""
    
    def get_aliases(self) -> List[str]:
        return ["delete", "remove", "del", "rm"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute delete command"""
        return self._interactive_delete()
    
    def _interactive_delete(self) -> str:
        """Interactive deletion interface"""
        delete_choices = [
            questionary.Choice("🔸 Single item", "single"),
            questionary.Choice("🔸 Multiple items", "multiple"),
            questionary.Choice("📁 Entire project", "project"),
            questionary.Choice("🗂️ All items of a type", "bulk_type"),
            questionary.Choice("⚠️ Everything (nuclear option)", "nuclear")
        ]
        
        choice = questionary.select(
            "🗑️ What do you want to delete?",
            choices=delete_choices
        ).ask()
        
        if not choice:
            return self.format_warning(["Delete operation cancelled"])
        
        return self.format_info([f"Delete {choice} - Coming soon!"])
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Delete Handler - Interactive Deletion

Usage:
  delete                   Interactive delete interface
  remove                   Same as delete
  del                      Quick alias
  rm                       Unix-style alias

Coming soon: Full deletion functionality
        """
        return self.format_info([help_text.strip()])
