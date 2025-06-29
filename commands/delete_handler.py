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
    get_client,
    get_database_stats
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
        
        if choice == "single":
            return self._delete_single_item()
        elif choice == "multiple":
            return self._delete_multiple_items()
        elif choice == "project":
            return self._delete_project()
        elif choice == "bulk_type":
            return self._delete_by_type()
        elif choice == "nuclear":
            return self._nuclear_delete()
        
        return self.format_error(["Invalid selection"])
    
    def _delete_single_item(self) -> str:
        """Delete single item"""
        # Get all items across all collections
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
                        
                        # Create display name
                        if metadata.get('file_path'):
                            filename = metadata['file_path'].split('/')[-1]
                            display_name = f"📄 {filename} ({metadata.get('disposition', 'Unknown')})"
                        else:
                            preview = doc[:50] + "..." if len(doc) > 50 else doc
                            display_name = f"📝 {metadata.get('disposition', 'Unknown')}: {preview}"
                        
                        all_items.append({
                            "display": display_name,
                            "collection": collection_info.name,
                            "id": all_data["ids"][i],
                            "metadata": metadata
                        })
            except:
                continue
        
        if not all_items:
            return self.format_warning(["No items found to delete"])
        
        # Sort by collection and type
        all_items.sort(key=lambda x: (x["collection"], x["metadata"].get("disposition", "")))
        
        # Create choices
        choices = []
        for item in all_items:
            collection_display = item["collection"].replace("project_", "").replace("_", " ").title()
            choice_text = f"{item['display']} | {collection_display}"
            choices.append(questionary.Choice(choice_text, item))
        
        selected = questionary.select(
            "🗑️ Select item to delete:",
            choices=choices
        ).ask()
        
        if not selected:
            return self.format_warning(["Delete cancelled"])
        
        # Confirm deletion
        confirm = questionary.confirm(
            f"⚠️ Really delete: {selected['display']}?",
            default=False
        ).ask()
        
        if not confirm:
            return self.format_warning(["Delete cancelled"])
        
        # Delete the item
        try:
            success = delete_item(selected["collection"], selected["id"])
            if success:
                return self.format_success([
                    f"✅ Deleted: {selected['display']}",
                    f"📁 From: {selected['collection']}"
                ])
            else:
                return self.format_error(["❌ Failed to delete item"])
        except Exception as e:
            return self.format_error([f"❌ Delete error: {str(e)}"])
    
    def _delete_multiple_items(self) -> str:
        """Delete multiple items"""
        # Get all items
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
                        
                        if metadata.get('file_path'):
                            filename = metadata['file_path'].split('/')[-1]
                            display_name = f"📄 {filename} ({metadata.get('disposition', 'Unknown')})"
                        else:
                            preview = doc[:50] + "..." if len(doc) > 50 else doc
                            display_name = f"📝 {metadata.get('disposition', 'Unknown')}: {preview}"
                        
                        all_items.append({
                            "display": display_name,
                            "collection": collection_info.name,
                            "id": all_data["ids"][i],
                            "metadata": metadata
                        })
            except:
                continue
        
        if not all_items:
            return self.format_warning(["No items found to delete"])
        
        # Create choices for multiple selection
        choices = []
        for item in all_items:
            collection_display = item["collection"].replace("project_", "").replace("_", " ").title()
            choice_text = f"{item['display']} | {collection_display}"
            choices.append(questionary.Choice(choice_text, item))
        
        selected_items = questionary.checkbox(
            "🗑️ Select items to delete (use space to select):",
            choices=choices
        ).ask()
        
        if not selected_items:
            return self.format_warning(["No items selected"])
        
        # Confirm deletion
        confirm = questionary.confirm(
            f"⚠️ Really delete {len(selected_items)} items?",
            default=False
        ).ask()
        
        if not confirm:
            return self.format_warning(["Delete cancelled"])
        
        # Delete items
        deleted_count = 0
        failed_count = 0
        
        for item in selected_items:
            try:
                success = delete_item(item["collection"], item["id"])
                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        result_msgs = [f"✅ Deleted {deleted_count} items"]
        if failed_count > 0:
            result_msgs.append(f"❌ Failed to delete {failed_count} items")
        
        return self.format_success(result_msgs)
    
    def _delete_project(self) -> str:
        """Delete entire project"""
        projects = get_all_projects()
        
        if not projects:
            return self.format_warning(["No projects found"])
        
        # Create project choices
        choices = []
        for project in projects:
            choice_text = f"{project['name']} ({project['item_count']} items) - {project['description'][:50] if project['description'] else 'No description'}"
            choices.append(questionary.Choice(choice_text, project))
        
        selected_project = questionary.select(
            "🗑️ Select project to delete:",
            choices=choices
        ).ask()
        
        if not selected_project:
            return self.format_warning(["Delete cancelled"])
        
        # Confirm deletion
        confirm = questionary.confirm(
            f"⚠️ Really delete project '{selected_project['name']}' and all {selected_project['item_count']} items?",
            default=False
        ).ask()
        
        if not confirm:
            return self.format_warning(["Delete cancelled"])
        
        # Delete project collection
        try:
            success = delete_collection(selected_project["collection_name"])
            if success:
                return self.format_success([
                    f"✅ Deleted project: {selected_project['name']}",
                    f"🗑️ Removed {selected_project['item_count']} items"
                ])
            else:
                return self.format_error(["❌ Failed to delete project"])
        except Exception as e:
            return self.format_error([f"❌ Delete error: {str(e)}"])
    
    def _delete_by_type(self) -> str:
        """Delete all items of specific type"""
        type_choices = [
            questionary.Choice("💻 All Codebase files", "codebase"),
            questionary.Choice("💬 All Conversations", "conversations"),
            questionary.Choice("💡 All Ideas", "ideas"),
            questionary.Choice("📋 All Brainstorm/Planning", "brainstorm"),
            questionary.Choice("📝 All Notes", "notes"),
            questionary.Choice("📖 All Man Pages", "manpages")
        ]
        
        selected_type = questionary.select(
            "🗑️ Select type to delete:",
            choices=type_choices
        ).ask()
        
        if not selected_type:
            return self.format_warning(["Delete cancelled"])
        
        # Get items of this type
        items = list_by_type(selected_type)
        
        if not items:
            return self.format_warning([f"No {selected_type} found"])
        
        # Confirm deletion
        confirm = questionary.confirm(
            f"⚠️ Really delete ALL {len(items)} {selected_type} items?",
            default=False
        ).ask()
        
        if not confirm:
            return self.format_warning(["Delete cancelled"])
        
        # Delete items
        deleted_count = 0
        failed_count = 0
        
        for item in items:
            try:
                success = delete_item(item["collection"], item["id"])
                if success:
                    deleted_count += 1
                else:
                    failed_count += 1
            except:
                failed_count += 1
        
        result_msgs = [f"✅ Deleted {deleted_count} {selected_type} items"]
        if failed_count > 0:
            result_msgs.append(f"❌ Failed to delete {failed_count} items")
        
        return self.format_success(result_msgs)
    
    def _nuclear_delete(self) -> str:
        """Delete everything (nuclear option)"""
        stats = get_database_stats()
        
        warning_msgs = [
            "⚠️ NUCLEAR DELETE WARNING ⚠️",
            "",
            "This will delete EVERYTHING:",
            f"📁 {stats['projects']} projects",
            f"📄 {stats['total_documents']} total documents",
            f"🗂️ {stats['total_collections']} collections",
            "",
            "THIS CANNOT BE UNDONE!"
        ]
        
        print(self.format_warning(warning_msgs))
        
        # Triple confirmation
        confirm1 = questionary.confirm(
            "⚠️ Are you absolutely sure you want to delete EVERYTHING?",
            default=False
        ).ask()
        
        if not confirm1:
            return self.format_info(["Nuclear delete cancelled"])
        
        confirm2 = questionary.text(
            "Type 'DELETE EVERYTHING' to confirm:"
        ).ask()
        
        if confirm2 != "DELETE EVERYTHING":
            return self.format_info(["Nuclear delete cancelled - incorrect confirmation"])
        
        confirm3 = questionary.confirm(
            "⚠️ FINAL WARNING: This will destroy all your memory data. Continue?",
            default=False
        ).ask()
        
        if not confirm3:
            return self.format_info(["Nuclear delete cancelled"])
        
        # Delete everything
        try:
            client = get_client()
            collections = client.list_collections()
            
            deleted_collections = 0
            for collection_info in collections:
                try:
                    client.delete_collection(collection_info.name)
                    deleted_collections += 1
                except:
                    pass
            
            return self.format_success([
                "💥 NUCLEAR DELETE COMPLETE",
                f"🗑️ Deleted {deleted_collections} collections",
                f"📄 Removed {stats['total_documents']} documents",
                "",
                "🦚 Peacock Memory database is now empty"
            ])
            
        except Exception as e:
            return self.format_error([f"❌ Nuclear delete error: {str(e)}"])
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Delete Handler - Interactive Deletion

Usage:
  delete                   Interactive delete interface
  remove                   Same as delete
  del                      Quick alias
  rm                       Unix-style alias

Delete Options:
  - Single item           Delete one specific item
  - Multiple items        Select multiple items to delete
  - Entire project        Delete project and all contents
  - All items of type     Delete all codebase/ideas/notes/etc
  - Everything            Nuclear option - delete all data

Safety Features:
  - Multiple confirmations for destructive operations
  - Preview of what will be deleted
  - Item counts and descriptions
  - Special confirmation for nuclear delete

Tips:
  - Single item deletion shows file names and previews
  - Multiple selection uses checkbox interface
  - Project deletion removes entire collection
  - Type deletion affects all items of that disposition
  - Nuclear delete requires typing 'DELETE EVERYTHING'
        """
        return self.format_info([help_text.strip()])