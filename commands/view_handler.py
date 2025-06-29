"""
🦚 Peacock Memory - View Handler
View complete files from memory
"""

from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import get_client, get_all_projects, get_project_contents, list_by_type

class ViewHandler(BaseCommand):
    """Handle view file commands"""
    
    def get_aliases(self) -> List[str]:
        return ["view", "show", "cat", "v"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute view command"""
        return self._interactive_view()
    
    def _interactive_view(self) -> str:
        """Interactive file viewing interface"""
        view_choices = [
            questionary.Choice("📁 Browse by project", "project"),
            questionary.Choice("💻 Browse codebase files", "codebase"),
            questionary.Choice("💬 Browse conversations", "conversations"),
            questionary.Choice("💡 Browse ideas", "ideas"),
            questionary.Choice("📋 Browse brainstorm/planning", "brainstorm"),
            questionary.Choice("📝 Browse notes", "notes"),
            questionary.Choice("📖 Browse man pages", "manpages"),
            questionary.Choice("🌐 Browse all files", "all")
        ]
        
        choice = questionary.select(
            "📄 What do you want to view?",
            choices=view_choices
        ).ask()
        
        if not choice:
            return self.format_warning(["View operation cancelled"])
        
        if choice == "project":
            return self._view_by_project()
        elif choice == "all":
            return self._view_all_files()
        else:
            return self._view_by_type(choice)
    
    def _view_by_project(self) -> str:
        """View files by project"""
        projects = get_all_projects()
        
        if not projects:
            return self.format_warning(["No projects found"])
        
        # Create project choices
        choices = []
        for project in projects:
            choice_text = f"{project['name']} ({project['item_count']} items)"
            choices.append(questionary.Choice(choice_text, project['name']))
        
        selected_project = questionary.select(
            "📁 Select project:",
            choices=choices
        ).ask()
        
        if not selected_project:
            return self.format_warning(["View cancelled"])
        
        # Get project contents
        contents = get_project_contents(selected_project)
        
        if contents['count'] == 0:
            return self.format_warning([f"No items found in project: {selected_project}"])
        
        return self._select_and_view_item(contents['items'], f"Project: {selected_project}")
    
    def _view_by_type(self, item_type: str) -> str:
        """View files by type"""
        items = list_by_type(item_type)
        
        if not items:
            return self.format_warning([f"No {item_type} found"])
        
        return self._select_and_view_item(items, f"Type: {item_type.title()}")
    
    def _view_all_files(self) -> str:
        """View all files across all collections"""
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
                            "id": all_data["ids"][i],
                            "collection": collection_info.name,
                            "content": doc,
                            "metadata": metadata,
                            "preview": doc[:150] + "..." if len(doc) > 150 else doc
                        })
            except:
                continue
        
        if not all_items:
            return self.format_warning(["No files found"])
        
        return self._select_and_view_item(all_items, "All Files")
    
    def _select_and_view_item(self, items: List[dict], context: str) -> str:
        """Select and view specific item"""
        # Create choices for items
        choices = []
        for item in items:
            metadata = item.get('metadata', {})
            
            # Create display name
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                language = metadata.get('language', 'unknown')
                lines = metadata.get('lines', 'unknown')
                display_name = f"📄 {filename} ({language}, {lines} lines)"
            else:
                disposition = metadata.get('disposition', 'Unknown')
                created_date = metadata.get('created', 'Unknown')[:10] if metadata.get('created') else 'Unknown'
                preview = item['preview'][:50] + "..." if len(item['preview']) > 50 else item['preview']
                display_name = f"📝 {disposition} ({created_date}): {preview}"
            
            # Add collection info
            collection_display = item['collection'].replace('project_', '').replace('_', ' ').title()
            choice_text = f"{display_name} | {collection_display}"
            
            choices.append(questionary.Choice(choice_text, item))
        
        # Sort choices by type and name
        choices.sort(key=lambda x: (x.value['metadata'].get('disposition', ''), x.title))
        
        selected = questionary.select(
            f"📄 Select file to view ({context}):",
            choices=choices
        ).ask()
        
        if not selected:
            return self.format_warning(["View cancelled"])
        
        return self._display_full_content(selected, context)
    
    def _display_full_content(self, item: dict, context: str) -> str:
        """Display full content of selected item"""
        metadata = item.get('metadata', {})
        
        # Build header info
        header_msgs = [
            f"📄 Viewing File - {context}",
            ""
        ]
        
        # Add metadata info
        if metadata.get('file_path'):
            filename = metadata['file_path'].split('/')[-1]
            header_msgs.extend([
                f"📁 File: {filename}",
                f"📂 Full Path: {metadata['file_path']}",
                f"💻 Language: {metadata.get('language', 'unknown')}",
                f"📊 Lines: {metadata.get('lines', 'unknown')}",
                f"📏 Size: {metadata.get('size', len(item['content']))} characters"
            ])
        else:
            header_msgs.extend([
                f"🏷️ Type: {metadata.get('disposition', 'Unknown')}",
                f"📊 Size: {len(item['content'])} characters"
            ])
        
        if metadata.get('created'):
            created_date = metadata['created'][:19].replace('T', ' ')
            header_msgs.append(f"📅 Created: {created_date}")
        
        if metadata.get('project'):
            header_msgs.append(f"📁 Project: {metadata['project']}")
        
        collection_display = item['collection'].replace('project_', '').replace('_', ' ').title()
        header_msgs.append(f"🗂️ Collection: {collection_display}")
        
        header_msgs.extend([
            "",
            "═" * 80,
            "📄 FULL CONTENT:",
            "═" * 80
        ])
        
        # Add content
        content_lines = item['content'].split('\n')
        
        # Add line numbers for code files
        if metadata.get('language') and metadata.get('language') != 'unknown':
            numbered_lines = []
            for i, line in enumerate(content_lines, 1):
                numbered_lines.append(f"{i:4d} | {line}")
            content_lines = numbered_lines
        
        # Combine header and content
        all_msgs = header_msgs + content_lines + ["", "═" * 80]
        
        # Ask what to do next
        next_choices = [
            questionary.Choice("🔙 Back to file list", "back"),
            questionary.Choice("🏠 Back to main view menu", "menu"),
            questionary.Choice("❌ Exit", "exit")
        ]
        
        next_action = questionary.select(
            "What would you like to do next?",
            choices=next_choices
        ).ask()
        
        result = self.format_data(all_msgs)
        
        if next_action == "back":
            # Go back to the same file list
            if "Project:" in context:
                project_name = context.replace("Project: ", "")
                contents = get_project_contents(project_name)
                result += "\n" + self._select_and_view_item(contents['items'], context)
            elif "Type:" in context:
                item_type = context.replace("Type: ", "").lower()
                items = list_by_type(item_type)
                result += "\n" + self._select_and_view_item(items, context)
            elif context == "All Files":
                result += "\n" + self._view_all_files()
        elif next_action == "menu":
            result += "\n" + self._interactive_view()
        
        return result
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 View Handler - View Complete Files

Usage:
  view                     Interactive file viewer
  show                     Same as view
  cat                      Unix-style alias
  v                        Quick alias

Browse Options:
  - By project            View files within specific projects
  - By type               View all codebase/ideas/notes/etc
  - All files             Browse everything

Features:
  - Full file content display
  - Metadata information (file path, language, size, etc)
  - Line numbers for code files
  - Creation dates and project info
  - Navigation back to file lists
  - Clean formatting with separators

File Information Shown:
  - Original file path and name
  - Programming language detection
  - File size and line count
  - Creation timestamp
  - Project assignment
  - Collection location

Navigation:
  - View file → Back to list → Back to menu
  - Seamless browsing experience
  - Exit at any point

Tips:
  - Code files show line numbers
  - Use project view for organized browsing
  - Type view for finding specific content types
  - All files view for comprehensive search
        """
        return self.format_info([help_text.strip()])