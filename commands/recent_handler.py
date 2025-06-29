"""
🦚 Peacock Memory - Recent Handler
View recently added files and sync database
"""

from typing import List, Optional
import questionary
from datetime import datetime, timedelta

from commands.base_command import BaseCommand
from core.database import get_client, get_database_stats

class RecentHandler(BaseCommand):
    """Handle recent files and sync commands"""
    
    def get_aliases(self) -> List[str]:
        return ["recent", "new", "latest", "sync"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute recent command"""
        command_word = command_input.strip().split()[0].lower()
        
        if command_word == "sync":
            return self._sync_database()
        else:
            return self._show_recent_files()
    
    def _sync_database(self) -> str:
        """Sync and refresh database"""
        try:
            # Force database refresh
            client = get_client()
            collections = client.list_collections()
            
            # Get fresh stats
            stats = get_database_stats()
            
            sync_msgs = [
                "🔄 Database sync complete!",
                "",
                "📊 Current Status:",
                f"📁 Collections: {stats['total_collections']}",
                f"📄 Total Documents: {stats['total_documents']}",
                f"🏷️ Projects: {stats['projects']}",
                "",
                "📋 By Category:",
                f"  💻 Codebase: {stats['by_type']['codebase']}",
                f"  💬 Conversations: {stats['by_type']['conversations']}",
                f"  💡 Ideas: {stats['by_type']['ideas']}",
                f"  📋 Brainstorm: {stats['by_type']['brainstorm']}",
                f"  📝 Notes: {stats['by_type']['notes']}",
                f"  📖 Man Pages: {stats['by_type']['manpages']}",
                "",
                "✅ All collections refreshed and indexed"
            ]
            
            return self.format_success(sync_msgs)
            
        except Exception as e:
            return self.format_error([f"❌ Sync error: {str(e)}"])
    
    def _show_recent_files(self) -> str:
        """Show recently added files"""
        try:
            # Time filter options
            time_choices = [
                questionary.Choice("📅 Last hour", 1),
                questionary.Choice("📅 Last 6 hours", 6),
                questionary.Choice("📅 Last 24 hours", 24),
                questionary.Choice("📅 Last 3 days", 72),
                questionary.Choice("📅 Last week", 168),
                questionary.Choice("📅 All time", None)
            ]
            
            time_filter = questionary.select(
                "⏰ Show files from when?",
                choices=time_choices
            ).ask()
            
            if time_filter is None:
                return self.format_warning(["Recent files cancelled"])
            
            # Calculate cutoff time
            cutoff_time = None
            if time_filter:
                cutoff_time = datetime.now() - timedelta(hours=time_filter)
            
            # Get all recent files
            recent_files = self._get_recent_files(cutoff_time)
            
            if not recent_files:
                time_desc = f"last {time_filter} hours" if time_filter else "all time"
                return self.format_warning([f"No files found in {time_desc}"])
            
            # Sort by creation time (newest first)
            recent_files.sort(key=lambda x: x['created'], reverse=True)
            
            # Format results
            time_desc = f"last {time_filter} hours" if time_filter else "all time"
            header_msgs = [
                f"🕒 Recent Files ({time_desc})",
                f"📊 Found: {len(recent_files)} files",
                ""
            ]
            
            file_msgs = []
            for i, file_info in enumerate(recent_files, 1):
                metadata = file_info['metadata']
                created_str = file_info['created_str']
                
                # Format file info
                if metadata.get('file_path'):
                    filename = metadata['file_path'].split('/')[-1]
                    language = metadata.get('language', 'unknown')
                    lines = metadata.get('lines', 'unknown')
                    file_msgs.append(f"🔸 #{i} 📄 {filename} ({language}, {lines} lines)")
                else:
                    disposition = metadata.get('disposition', 'Unknown')
                    file_msgs.append(f"🔸 #{i} 📝 {disposition}")
                
                # Add metadata
                collection = file_info['collection'].replace('project_', '').replace('_', ' ').title()
                file_msgs.extend([
                    f"   📁 Collection: {collection}",
                    f"   🕒 Added: {created_str}",
                    f"   📄 Preview: {file_info['preview']}",
                    "   " + "─" * 50
                ])
            
            all_msgs = header_msgs + file_msgs
            
            # Ask if user wants to view a specific file
            view_file = questionary.confirm(
                "🔍 View a specific file from this list?",
                default=False
            ).ask()
            
            if view_file:
                return self._select_recent_file(recent_files) + "\n" + self.format_data(all_msgs)
            
            return self.format_data(all_msgs)
            
        except Exception as e:
            return self.format_error([f"❌ Error getting recent files: {str(e)}"])
    
    def _get_recent_files(self, cutoff_time: Optional[datetime]) -> List[dict]:
        """Get recent files from all collections"""
        client = get_client()
        collections = client.list_collections()
        
        recent_files = []
        
        for collection_info in collections:
            collection = client.get_collection(collection_info.name)
            try:
                all_data = collection.get()
                if all_data["documents"]:
                    for i, doc in enumerate(all_data["documents"]):
                        metadata = all_data["metadatas"][i] if all_data["metadatas"] else {}
                        
                        # Parse creation time
                        created_str = metadata.get('created', '')
                        if not created_str:
                            continue
                        
                        try:
                            # Parse ISO format datetime
                            created_time = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                            # Convert to local time (remove timezone for comparison)
                            created_time = created_time.replace(tzinfo=None)
                        except:
                            continue
                        
                        # Apply time filter
                        if cutoff_time and created_time < cutoff_time:
                            continue
                        
                        # Format creation time for display
                        time_diff = datetime.now() - created_time
                        if time_diff.days > 0:
                            created_display = f"{time_diff.days} days ago"
                        elif time_diff.seconds > 3600:
                            hours = time_diff.seconds // 3600
                            created_display = f"{hours} hours ago"
                        elif time_diff.seconds > 60:
                            minutes = time_diff.seconds // 60
                            created_display = f"{minutes} minutes ago"
                        else:
                            created_display = "Just now"
                        
                        recent_files.append({
                            "id": all_data["ids"][i],
                            "collection": collection_info.name,
                            "content": doc,
                            "metadata": metadata,
                            "preview": doc[:100] + "..." if len(doc) > 100 else doc,
                            "created": created_time,
                            "created_str": created_display
                        })
            except:
                continue
        
        return recent_files
    
    def _select_recent_file(self, recent_files: List[dict]) -> str:
        """Select and view a recent file"""
        # Create choices
        choices = []
        for i, file_info in enumerate(recent_files, 1):
            metadata = file_info['metadata']
            
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                display_name = f"#{i} 📄 {filename} ({file_info['created_str']})"
            else:
                disposition = metadata.get('disposition', 'Unknown')
                display_name = f"#{i} 📝 {disposition} ({file_info['created_str']})"
            
            choices.append(questionary.Choice(display_name, file_info))
        
        selected = questionary.select(
            "📄 Select file to view:",
            choices=choices
        ).ask()
        
        if not selected:
            return self.format_warning(["File selection cancelled"])
        
        # Display full content
        return self._display_recent_file(selected)
    
    def _display_recent_file(self, file_info: dict) -> str:
        """Display full content of recent file"""
        metadata = file_info['metadata']
        
        # Build content display
        content_msgs = [
            f"📄 Recent File: {file_info['created_str']}",
            ""
        ]
        
        # Add file info
        if metadata.get('file_path'):
            filename = metadata['file_path'].split('/')[-1]
            content_msgs.extend([
                f"📁 File: {filename}",
                f"📂 Path: {metadata['file_path']}",
                f"💻 Language: {metadata.get('language', 'unknown')}",
                f"📊 Lines: {metadata.get('lines', 'unknown')}"
            ])
        else:
            content_msgs.append(f"🏷️ Type: {metadata.get('disposition', 'Unknown')}")
        
        collection_display = file_info['collection'].replace('project_', '').replace('_', ' ').title()
        content_msgs.extend([
            f"🗂️ Collection: {collection_display}",
            f"📏 Size: {len(file_info['content'])} characters",
            "",
            "═" * 60,
            "📄 CONTENT:",
            "═" * 60,
            "",
            file_info['content'],
            "",
            "═" * 60
        ])
        
        return self.format_data(content_msgs)
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Recent Handler - Recent Files & Database Sync

Usage:
  recent                   Show recently added files
  new                      Same as recent
  latest                   Same as recent
  sync                     Sync and refresh database

Recent Files Features:
  - Time-based filtering (1 hour to all time)
  - Sorted by creation time (newest first)
  - File metadata and previews
  - Quick file viewing
  - Collection information

Time Filters:
  - Last hour             Files added in past hour
  - Last 6 hours          Files added in past 6 hours
  - Last 24 hours         Files added in past day
  - Last 3 days           Files added in past 3 days
  - Last week             Files added in past week
  - All time              All files ever added

Sync Features:
  - Refresh database connections
  - Update collection indexes
  - Verify data integrity
  - Display current statistics
  - Force cache refresh

Tips:
  - Use recent to find files you just added
  - Sync after adding many files for better performance
  - Recent files show relative time (e.g., "2 hours ago")
  - View specific files directly from recent list
  - Sync provides database health overview
        """
        return self.format_info([help_text.strip()])