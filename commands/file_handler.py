"""
🦚 Peacock Memory - File Handler
Handles @ commands for adding files and directories
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import add_file_to_collection, get_all_projects, create_project

class FileHandler(BaseCommand):
    """Handle @ file and directory commands"""
    
    def get_aliases(self) -> List[str]:
        return ["@"]  # Special case - handled by command_input.startswith('@')
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute @ command"""
        if not command_input.startswith('@'):
            return self.format_error(["Invalid @ command format"])
        
        path_str = command_input[1:].strip()
        if not path_str:
            return self.format_error(["No path provided after @"])
        
        path = Path(path_str).expanduser().resolve()
        
        if not path.exists():
            return self.format_error([f"Path does not exist: {path}"])
        
        if path.is_file():
            return self._handle_single_file(path)
        elif path.is_dir():
            return self._handle_directory(path)
        else:
            return self.format_error([f"Path is neither file nor directory: {path}"])
    
    def _handle_single_file(self, file_path: Path) -> str:
        """Handle single file addition"""
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Get disposition
            disposition = self._get_disposition()
            if not disposition:
                return self.format_warning(["File addition cancelled"])
            
            # Handle project assignment for Codebase and Plan/Brainstorm
            project = None
            if disposition in ["Codebase", "Plan/Brainstorm"]:
                project = self._get_project_assignment()
                if project is None:  # User cancelled
                    return self.format_warning(["File addition cancelled"])
            
            # Determine collection name
            collection_name = f"project_{project}" if project else "global_files"
            
            # Add to database
            file_id = add_file_to_collection(
                collection_name=collection_name,
                file_path=str(file_path),
                content=content,
                disposition=disposition,
                project=project
            )
            
            success_msgs = [
                f"✅ Added file: {file_path.name}",
                f"📁 Disposition: {disposition}",
                f"📊 Size: {len(content)} chars, {len(content.split())} lines"
            ]
            
            if project:
                success_msgs.append(f"🏷️ Project: {project}")
            
            return self.format_success(success_msgs)
            
        except Exception as e:
            return self.format_error([f"Error adding file: {str(e)}"])
    
    def _handle_directory(self, dir_path: Path) -> str:
        """Handle directory with file picker"""
        try:
            # Get all files in directory (recursive)
            all_files = []
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    # Skip hidden files and common non-text files
                    if not file_path.name.startswith('.'):
                        all_files.append(file_path)
            
            if not all_files:
                return self.format_warning([f"No files found in directory: {dir_path}"])
            
            # Use fzf for file selection if available, otherwise questionary
            selected_files = self._select_files_with_fzf(all_files, dir_path)
            
            if not selected_files:
                return self.format_warning(["No files selected"])
            
            # Get disposition for all selected files
            disposition = self._get_disposition()
            if not disposition:
                return self.format_warning(["File addition cancelled"])
            
            # Handle project assignment
            project = None
            if disposition in ["Codebase", "Plan/Brainstorm"]:
                project = self._get_project_assignment()
                if project is None:
                    return self.format_warning(["File addition cancelled"])
            
            # Add all selected files
            collection_name = f"project_{project}" if project else "global_files"
            added_files = []
            failed_files = []
            
            for file_path in selected_files:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    add_file_to_collection(
                        collection_name=collection_name,
                        file_path=str(file_path),
                        content=content,
                        disposition=disposition,
                        project=project
                    )
                    added_files.append(file_path.name)
                except Exception as e:
                    failed_files.append(f"{file_path.name}: {str(e)}")
            
            # Format results
            result_msgs = [
                f"✅ Successfully added {len(added_files)} files",
                f"📁 Disposition: {disposition}"
            ]
            
            if project:
                result_msgs.append(f"🏷️ Project: {project}")
            
            if failed_files:
                result_msgs.append(f"⚠️ Failed: {len(failed_files)} files")
                result_msgs.extend([f"  - {fail}" for fail in failed_files[:3]])
                if len(failed_files) > 3:
                    result_msgs.append(f"  ... and {len(failed_files) - 3} more")
            
            return self.format_success(result_msgs)
            
        except Exception as e:
            return self.format_error([f"Error processing directory: {str(e)}"])
    
    def _select_files_with_fzf(self, files: List[Path], base_dir: Path) -> List[Path]:
        """Use fzf for file selection, fallback to questionary"""
        try:
            # Prepare file list for fzf
            file_list = []
            for file_path in files:
                rel_path = file_path.relative_to(base_dir)
                file_list.append(str(rel_path))
            
            # Create temporary file with file list
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
                tmp_file.write('\n'.join(file_list))
                tmp_file_path = tmp_file.name
            
            # Use fzf for selection
            fzf_cmd = [
                'fzf',
                '--multi',
                '--preview', f'head -20 "{base_dir}/{{}}"',
                '--preview-window', 'right:50%',
                '--prompt', '🦚 Select files: ',
                '--header', 'Tab: select, Enter: confirm'
            ]
            
            result = subprocess.run(
                fzf_cmd,
                stdin=open(tmp_file_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Clean up temp file
            os.unlink(tmp_file_path)
            
            if result.returncode == 0:
                selected_rel_paths = result.stdout.strip().split('\n')
                selected_files = [base_dir / rel_path for rel_path in selected_rel_paths if rel_path]
                return selected_files
            else:
                # Fallback to questionary if fzf fails
                return self._select_files_with_questionary(files, base_dir)
                
        except (subprocess.SubprocessError, FileNotFoundError):
            # fzf not available, use questionary
            return self._select_files_with_questionary(files, base_dir)
    
    def _select_files_with_questionary(self, files: List[Path], base_dir: Path) -> List[Path]:
        """Fallback file selection with questionary"""
        choices = []
        for file_path in files[:50]:  # Limit to 50 files for questionary
            rel_path = file_path.relative_to(base_dir)
            choices.append(questionary.Choice(str(rel_path), file_path))
        
        if len(files) > 50:
            print(f"⚠️ Showing first 50 of {len(files)} files. Use fzf for better selection.")
        
        selected = questionary.checkbox(
            "Select files to add:",
            choices=choices
        ).ask()
        
        return selected if selected else []
    
    def _get_disposition(self) -> Optional[str]:
        """Get file disposition from user"""
        choices = [
            "Codebase",
            "Plan/Brainstorm", 
            "Idea",
            "Note",
            "man-page"
        ]
        
        return questionary.select(
            "🏷️ Disposition of file?",
            choices=choices
        ).ask()
    
    def _get_project_assignment(self) -> Optional[str]:
        """Get project assignment for Codebase and Plan/Brainstorm"""
        projects = get_all_projects()
        
        choices = []
        for project in projects:
            choices.append(questionary.Choice(
                f"{project['name']} ({project['item_count']} items)",
                project['name']
            ))
        
        choices.append(questionary.Choice("➕ Create New Project", "NEW_PROJECT"))
        
        selection = questionary.select(
            "📁 Assign to project:",
            choices=choices
        ).ask()
        
        if not selection:
            return None
        
        if selection == "NEW_PROJECT":
            return self._create_new_project()
        
        return selection
    
    def _create_new_project(self) -> Optional[str]:
        """Create new project"""
        name = questionary.text("📁 Project name:").ask()
        if not name:
            return None
        
        description = questionary.text("📝 Description (optional):").ask()
        
        try:
            create_project(name, description or "")
            return name
        except Exception as e:
            print(f"Error creating project: {e}")
            return None
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 File Handler - Add files and directories

Usage:
  @/path/to/file.py        Add single file
  @/path/to/directory/     Add directory (interactive selection)

File Dispositions:
  - Codebase              Requires project assignment
  - Plan/Brainstorm       Requires project assignment  
  - Idea                  Global storage
  - Note                  Global storage
  - man-page              Global storage

Examples:
  @~/my_script.py
  @/home/user/project/
  @./current_dir/
        """
        return self.format_info([help_text.strip()])