"""
🦚 Peacock Memory - Project Handler
Browse and create projects with file viewing
"""

from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import get_all_projects, get_project_contents, create_project

class ProjectHandler(BaseCommand):
    """Handle project commands"""
    
    def get_aliases(self) -> List[str]:
        return ["projects", "project", "proj"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute project command"""
        return self._interactive_projects()
    
    def _interactive_projects(self) -> str:
        """Interactive project interface"""
        projects = get_all_projects()
        
        choices = []
        
        # Add existing projects
        for project in projects:
            choices.append(questionary.Choice(
                f"📁 {project['name']} ({project['item_count']} items) - {project['description'][:50] if project['description'] else 'No description'}",
                f"select_{project['name']}"
            ))
        
        # Add create new project option
        choices.append(questionary.Choice("➕ Create New Project", "create_new"))
        
        if not projects:
            return self._create_project_flow()
        
        selection = questionary.select(
            "📁 Select project or create new:",
            choices=choices
        ).ask()
        
        if not selection:
            return self.format_warning(["Project operation cancelled"])
        
        if selection == "create_new":
            return self._create_project_flow()
        elif selection.startswith("select_"):
            project_name = selection.replace("select_", "")
            return self._browse_project(project_name)
        
        return self.format_error(["Invalid selection"])
    
    def _create_project_flow(self) -> str:
        """Create new project flow"""
        name = questionary.text(
            "📁 Project name:",
            validate=lambda x: len(x.strip()) > 0 or "Project name cannot be empty"
        ).ask()
        
        if not name:
            return self.format_warning(["Project creation cancelled"])
        
        description = questionary.text("📝 Description (optional):").ask()
        
        try:
            create_project(name, description or "")
            return self.format_success([
                f"✅ Created project: {name}",
                f"📝 Description: {description or 'No description'}",
                "💡 Use @/path/to/file with 'Codebase' or 'Plan/Brainstorm' disposition to add files"
            ])
        except Exception as e:
            return self.format_error([f"Error creating project: {str(e)}"])
    
    def _browse_project(self, project_name: str) -> str:
        """Browse project contents with file viewing option"""
        contents = get_project_contents(project_name)
        
        if contents['count'] == 0:
            return self.format_warning([
                f"📁 Project '{project_name}' is empty",
                "💡 Use @/path/to/file with 'Codebase' or 'Plan/Brainstorm' to add files"
            ])
        
        # Create choices for project items
        choices = []
        for item in contents['items']:
            metadata = item.get('metadata', {})
            
            # Format item display
            item_type = metadata.get('disposition', metadata.get('type', 'Unknown'))
            
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                language = metadata.get('language', 'unknown')
                display_text = f"📄 {filename} ({item_type}, {language})"
            else:
                preview = item['preview'][:50] + "..." if len(item['preview']) > 50 else item['preview']
                display_text = f"📝 {item_type}: {preview}"
            
            choices.append(questionary.Choice(display_text, item['id']))
        
        # Add back option
        choices.append(questionary.Choice("🔙 Back to project list", "back"))
        
        selection = questionary.select(
            f"📁 Project: {project_name} ({contents['count']} items)",
            choices=choices
        ).ask()
        
        if not selection:
            return self.format_warning(["Project browsing cancelled"])
        
        if selection == "back":
            return self._interactive_projects()
        
        # Find selected item
        selected_item = None
        for item in contents['items']:
            if item['id'] == selection:
                selected_item = item
                break
        
        if not selected_item:
            return self.format_error(["Selected item not found"])
        
        return self._display_item(selected_item, project_name)
    
    def _display_item(self, item: dict, project_name: str) -> str:
        """Display individual item with option to view full content"""
        metadata = item.get('metadata', {})
        
        # Format item info
        info_msgs = [
            f"📁 Project: {project_name}",
            f"🏷️  Type: {metadata.get('disposition', metadata.get('type', 'Unknown'))}",
        ]
        
        if metadata.get('file_path'):
            filename = metadata['file_path'].split('/')[-1]
            info_msgs.extend([
                f"📄 File: {filename}",
                f"💻 Language: {metadata.get('language', 'unknown')}",
                f"📊 Lines: {metadata.get('lines', 'unknown')}",
                f"📏 Size: {metadata.get('size', 'unknown')} characters"
            ])
        
        if metadata.get('created'):
            created_date = metadata['created'][:19].replace('T', ' ')
            info_msgs.append(f"📅 Created: {created_date}")
        
        info_msgs.extend([
            "",
            "📄 Content Preview:",
            "─" * 60,
            item['preview'],
            "─" * 60
        ])
        
        # Ask if user wants to see full content
        show_full = questionary.confirm(
            "🔍 View full content?",
            default=False
        ).ask()
        
        if show_full:
            info_msgs.extend([
                "",
                "📄 Full Content:",
                "═" * 60,
                item['content'],
                "═" * 60
            ])
        
        # Ask what to do next
        next_action = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice("🔙 Back to project", "back_project"),
                questionary.Choice("🏠 Back to project list", "back_list"),
                questionary.Choice("❌ Exit", "exit")
            ]
        ).ask()
        
        result = self.format_data(info_msgs)
        
        if next_action == "back_project":
            result += "\n" + self._browse_project(project_name)
        elif next_action == "back_list":
            result += "\n" + self._interactive_projects()
        
        return result
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Project Handler - Project Management

Usage:
  projects                 Interactive project interface
  project                  Same as projects
  proj                     Quick alias

Features:
  - Browse existing projects
  - Create new projects
  - View project contents
  - Read individual files
  - Navigate project hierarchy

Project Structure:
  - Projects contain files and documents
  - Files added with 'Codebase' disposition go to projects
  - Files added with 'Plan/Brainstorm' disposition go to projects
  - Other dispositions (Ideas, Notes, man-pages) are global

Navigation:
  1. Select project or create new
  2. Browse project contents
  3. View individual files
  4. Read full file content if needed
  5. Navigate back through menus

Tips:
  - Empty projects show helpful guidance
  - File metadata includes language and line count
  - Preview shows first part of content
  - Full content view available for each item
  - Use @/path/to/file to add files to projects
        """
        return self.format_info([help_text.strip()])