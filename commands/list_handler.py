"""
🦚 Peacock Memory - List Handler
List items by category and type
"""

from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import list_by_type, get_all_projects, get_project_contents, get_database_stats

class ListHandler(BaseCommand):
    """Handle list commands"""
    
    def get_aliases(self) -> List[str]:
        return ["list", "ls", "l"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute list command"""
        return self._interactive_list()
    
    def _interactive_list(self) -> str:
        """Interactive list interface"""
        list_choices = [
            questionary.Choice("📁 All Projects", "projects"),
            questionary.Choice("💻 Files in Project", "project_files"),
            questionary.Choice("💬 All Conversations", "conversations"),
            questionary.Choice("💻 All Codebase Files", "codebase"),
            questionary.Choice("💡 All Ideas", "ideas"),
            questionary.Choice("📋 All Brainstorm/Planning", "brainstorm"),
            questionary.Choice("📝 All Notes", "notes"),
            questionary.Choice("📖 All Man Pages", "manpages"),
            questionary.Choice("📊 Database Overview", "overview")
        ]
        
        choice = questionary.select(
            "📋 What do you want to list?",
            choices=list_choices
        ).ask()
        
        if not choice:
            return self.format_warning(["List operation cancelled"])
        
        if choice == "projects":
            return self._list_projects()
        elif choice == "project_files":
            return self._list_project_files()
        elif choice == "overview":
            return self._show_overview()
        else:
            return self._list_by_category(choice)
    
    def _list_projects(self) -> str:
        """List all projects"""
        projects = get_all_projects()
        
        if not projects:
            return self.format_warning(["No projects found"])
        
        # Sort by creation date (newest first)
        projects.sort(key=lambda x: x.get('created', ''), reverse=True)
        
        header_msgs = [
            f"📁 All Projects ({len(projects)} total)",
            ""
        ]
        
        project_msgs = []
        for i, project in enumerate(projects, 1):
            created_date = project.get('created', 'Unknown')[:10] if project.get('created') else 'Unknown'
            
            project_msgs.extend([
                f"🔸 Project #{i}: {project['name']}",
                f"📝 Description: {project['description'] or 'No description'}",
                f"📊 Items: {project['item_count']}",
                f"📅 Created: {created_date}",
                "─" * 50
            ])
        
        all_msgs = header_msgs + project_msgs
        return self.format_data(all_msgs)
    
    def _list_project_files(self) -> str:
        """List files in specific project"""
        projects = get_all_projects()
        
        if not projects:
            return self.format_warning(["No projects found"])
        
        # Let user select project
        project_choices = []
        for project in projects:
            project_choices.append(questionary.Choice(
                f"{project['name']} ({project['item_count']} items)",
                project['name']
            ))
        
        selected_project = questionary.select(
            "📁 Select project:",
            choices=project_choices
        ).ask()
        
        if not selected_project:
            return self.format_warning(["No project selected"])
        
        # Get project contents
        contents = get_project_contents(selected_project)
        
        if contents['count'] == 0:
            return self.format_warning([f"No items found in project: {selected_project}"])
        
        header_msgs = [
            f"📁 Project: {selected_project}",
            f"📊 Total Items: {contents['count']}",
            ""
        ]
        
        item_msgs = []
        for i, item in enumerate(contents['items'], 1):
            metadata = item.get('metadata', {})
            
            # Format item info
            item_type = metadata.get('disposition', metadata.get('type', 'Unknown'))
            created_date = metadata.get('created', 'Unknown')[:10] if metadata.get('created') else 'Unknown'
            
            file_info = ""
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                language = metadata.get('language', 'unknown')
                lines = metadata.get('lines', 0)
                file_info = f"📄 {filename} ({language}, {lines} lines)"
            
            item_msgs.extend([
                f"🔸 Item #{i}: {item_type}",
                file_info if file_info else f"📝 Content preview available",
                f"📅 Created: {created_date}",
                f"📄 Preview: {item['preview']}",
                "─" * 50
            ])
        
        all_msgs = header_msgs + item_msgs
        return self.format_data(all_msgs)
    
    def _list_by_category(self, category: str) -> str:
        """List items by category"""
        items = list_by_type(category)
        
        if not items:
            return self.format_warning([f"No {category} found"])
        
        # Category display names
        category_names = {
            "conversations": "Conversations",
            "codebase": "Codebase Files",
            "ideas": "Ideas",
            "brainstorm": "Brainstorm/Planning",
            "notes": "Notes",
            "manpages": "Man Pages"
        }
        
        category_display = category_names.get(category, category.title())
        
        header_msgs = [
            f"📋 All {category_display} ({len(items)} total)",
            ""
        ]
        
        item_msgs = []
        for i, item in enumerate(items, 1):
            metadata = item.get('metadata', {})
            collection_name = item['collection'].replace('project_', '').replace('_', ' ').title()
            
            created_date = metadata.get('created', 'Unknown')[:10] if metadata.get('created') else 'Unknown'
            
            # Format based on item type
            if category == "codebase":
                filename = metadata.get('file_path', 'Unknown').split('/')[-1]
                language = metadata.get('language', 'unknown')
                lines = metadata.get('lines', 0)
                
                item_msgs.extend([
                    f"🔸 File #{i}: {filename}",
                    f"💻 Language: {language} | Lines: {lines}",
                    f"📁 Collection: {collection_name}",
                    f"📅 Created: {created_date}",
                    f"📄 Preview: {item['preview']}",
                    "─" * 50
                ])
            else:
                item_msgs.extend([
                    f"🔸 Item #{i}",
                    f"📁 Collection: {collection_name}",
                    f"📅 Created: {created_date}",
                    f"📄 Preview: {item['preview']}",
                    "─" * 50
                ])
        
        all_msgs = header_msgs + item_msgs
        return self.format_data(all_msgs)
    
    def _show_overview(self) -> str:
        """Show database overview/statistics"""
        stats = get_database_stats()
        
        overview_msgs = [
            "📊 Peacock Memory Database Overview",
            "",
            f"📁 Total Collections: {stats['total_collections']}",
            f"🏷️  Projects: {stats['projects']}",
            f"📄 Total Documents: {stats['total_documents']}",
            "",
            "📋 By Category:",
            f"  💻 Codebase Files: {stats['by_type']['codebase']}",
            f"  💬 Conversations: {stats['by_type']['conversations']}",
            f"  💡 Ideas: {stats['by_type']['ideas']}",
            f"  📋 Brainstorm/Planning: {stats['by_type']['brainstorm']}",
            f"  📝 Notes: {stats['by_type']['notes']}",
            f"  📖 Man Pages: {stats['by_type']['manpages']}",
            "",
            f"💾 Database Location: ~/peacock_db/"
        ]
        
        return self.format_data(overview_msgs)
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 List Handler - Browse Memory Contents

Usage:
  list                     Interactive list interface
  ls                       Same as list
  l                        Quick alias for list

List Options:
  - All Projects          Show all projects with stats
  - Files in Project      Browse specific project contents
  - All Conversations     Show all imported conversations
  - All Codebase Files    Show all code files
  - All Ideas             Show all saved ideas
  - All Brainstorm/Planning  Show planning documents
  - All Notes             Show all notes
  - All Man Pages         Show documentation
  - Database Overview     Statistics and summary

Features:
  - Organized by category
  - Metadata display (dates, file info, etc.)
  - Content previews
  - Item counts and statistics
  - Project-specific filtering

Tips:
  - Use overview to see database statistics
  - Project files show detailed file information
  - Previews help identify specific items
  - Created dates show chronological order
        """
        return self.format_info([help_text.strip()])