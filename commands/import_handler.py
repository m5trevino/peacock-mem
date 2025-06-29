"""
🦚 Peacock Memory - Import Handler
Smart JSON import for Claude conversations, ChatGPT, and Claude projects
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import questionary
from datetime import datetime
import hashlib

from commands.base_command import BaseCommand
from core.database import get_client, get_or_create_collection
from utils.json_detector import detect_json_type, ImportType
from core.importers import import_claude_conversations, import_chatgpt_conversations, import_claude_projects

class ImportHandler(BaseCommand):
    """Handle import commands for JSON files"""
    
    def get_aliases(self) -> List[str]:
        return ["import"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute import command"""
        parts = command_input.strip().split()
        
        if len(parts) == 1:
            # Interactive mode
            return self._interactive_import()
        else:
            # Direct file paths provided
            file_paths = []
            for part in parts[1:]:
                if part.startswith('@'):
                    file_paths.append(part[1:])
                else:
                    file_paths.append(part)
            
            return self._import_files(file_paths)
    
    def _interactive_import(self) -> str:
        """Interactive import mode"""
        file_path = questionary.path(
            "📁 Enter path to JSON file:",
            validate=lambda x: Path(x).exists() or "File not found"
        ).ask()
        
        if not file_path:
            return self.format_warning(["Import cancelled"])
        
        return self._import_files([file_path])
    
    def _import_files(self, file_paths: List[str]) -> str:
        """Import multiple JSON files"""
        results = []
        total_imported = {
            "conversations": 0,
            "messages": 0,
            "projects": 0,
            "documents": 0
        }
        failed_files = []
        
        for file_path_str in file_paths:
            try:
                file_path = Path(file_path_str).expanduser().resolve()
                
                if not file_path.exists():
                    failed_files.append(f"{file_path.name}: File not found")
                    continue
                
                # Load and detect JSON type
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                import_type = detect_json_type(json_data)
                
                if import_type == ImportType.UNKNOWN:
                    failed_files.append(f"{file_path.name}: Unknown JSON format")
                    continue
                
                # Import based on detected type
                result = self._import_by_type(json_data, import_type, file_path.name)
                results.append(result)
                
                # Update totals
                if import_type == ImportType.CLAUDE_CONVERSATIONS:
                    total_imported["conversations"] += result.get("conversations", 0)
                    total_imported["messages"] += result.get("messages", 0)
                elif import_type == ImportType.CHATGPT_CONVERSATIONS:
                    total_imported["conversations"] += result.get("conversations", 0)
                    total_imported["messages"] += result.get("messages", 0)
                elif import_type == ImportType.CLAUDE_PROJECTS:
                    total_imported["projects"] += result.get("projects", 0)
                    total_imported["documents"] += result.get("documents", 0)
                
            except Exception as e:
                failed_files.append(f"{Path(file_path_str).name}: {str(e)}")
        
        # Format results
        success_msgs = []
        if total_imported["conversations"] > 0:
            success_msgs.append(f"💬 {total_imported['conversations']} conversations imported")
        if total_imported["messages"] > 0:
            success_msgs.append(f"📝 {total_imported['messages']} messages processed")
        if total_imported["projects"] > 0:
            success_msgs.append(f"📁 {total_imported['projects']} projects imported")
        if total_imported["documents"] > 0:
            success_msgs.append(f"📄 {total_imported['documents']} documents processed")
        
        if failed_files:
            success_msgs.append(f"⚠️ {len(failed_files)} files failed:")
            success_msgs.extend([f"  - {fail}" for fail in failed_files[:3]])
            if len(failed_files) > 3:
                success_msgs.append(f"  ... and {len(failed_files) - 3} more")
        
        if not success_msgs:
            return self.format_error(["No files were successfully imported"])
        
        return self.format_success(success_msgs)
    
    def _import_by_type(self, json_data: Dict[str, Any], import_type: ImportType, filename: str) -> Dict[str, int]:
        """Import JSON data based on detected type"""
        progress_msgs = [f"🔍 Detected: {import_type.value}", f"📁 Processing: {filename}"]
        print(self.format_progress(progress_msgs))
        
        if import_type == ImportType.CLAUDE_CONVERSATIONS:
            return import_claude_conversations(json_data)
        elif import_type == ImportType.CHATGPT_CONVERSATIONS:
            return import_chatgpt_conversations(json_data)
        elif import_type == ImportType.CLAUDE_PROJECTS:
            return import_claude_projects(json_data)
        else:
            return {}
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Import Handler - Smart JSON Import

Usage:
  import                           Interactive mode
  import @/path/to/file.json      Import single file
  import @file1.json @file2.json  Import multiple files

Supported Formats:
  - Claude conversations (conversations.json)
  - ChatGPT conversations (conversations.json)
  - Claude projects (projects.json)

Features:
  - Automatic format detection
  - Batch processing
  - Progress tracking
  - Error handling
  - Direct ChromaDB import (fast search)

Examples:
  import
  import @~/Downloads/claude-conversations.json
  import @chatgpt.json @claude-projects.json @conversations.json
        """
        return self.format_info([help_text.strip()])
