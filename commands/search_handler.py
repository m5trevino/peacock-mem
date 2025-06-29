"""
🦚 Peacock Memory - Search Handler
Smart search across all memory types with filtering
"""

from typing import List, Optional
import questionary

from commands.base_command import BaseCommand
from core.database import search_all_collections, search_by_type

class SearchHandler(BaseCommand):
    """Handle search commands"""
    
    def get_aliases(self) -> List[str]:
        return ["search", "find", "s"]
    
    def execute(self, command_input: str) -> Optional[str]:
        """Execute search command"""
        # Interactive search menu
        return self._interactive_search()
    
    def _interactive_search(self) -> str:
        """Interactive search interface"""
        # Search scope selection
        search_choices = [
            questionary.Choice("🌐 Everything", "everything"),
            questionary.Choice("💬 Conversations only", "conversations"),
            questionary.Choice("💻 Codebase only", "codebase"),
            questionary.Choice("💡 Ideas only", "ideas"),
            questionary.Choice("📋 Brainstorm/Planning only", "brainstorm"),
            questionary.Choice("📝 Notes only", "notes"),
            questionary.Choice("📖 Man pages only", "manpages"),
            questionary.Choice("🔀 Multiple categories", "multiple")
        ]
        
        search_scope = questionary.select(
            "🔍 What do you want to search?",
            choices=search_choices
        ).ask()
        
        if not search_scope:
            return self.format_warning(["Search cancelled"])
        
        # Handle multiple categories
        if search_scope == "multiple":
            category_choices = [
                questionary.Choice("💬 Conversations", "conversations"),
                questionary.Choice("💻 Codebase", "codebase"),
                questionary.Choice("💡 Ideas", "ideas"),
                questionary.Choice("📋 Brainstorm/Planning", "brainstorm"),
                questionary.Choice("📝 Notes", "notes"),
                questionary.Choice("📖 Man pages", "manpages")
            ]
            
            selected_categories = questionary.checkbox(
                "Select categories to search:",
                choices=category_choices
            ).ask()
            
            if not selected_categories:
                return self.format_warning(["No categories selected"])
        
        # Get search query
        query = questionary.text(
            "🔍 Enter search query:",
            validate=lambda x: len(x.strip()) > 0 or "Search query cannot be empty"
        ).ask()
        
        if not query:
            return self.format_warning(["Search cancelled"])
        
        # Get result limit
        limit_str = questionary.text(
            "📊 Results limit (default 10):",
            default="10"
        ).ask()
        
        try:
            limit = int(limit_str) if limit_str and limit_str.isdigit() else 10
        except ValueError:
            limit = 10
        
        # Perform search
        if search_scope == "everything":
            results = search_all_collections(query, limit)
            return self._format_search_results(results, query, "everything")
        elif search_scope == "multiple":
            all_results = []
            for category in selected_categories:
                results = search_by_type(query, category, limit // len(selected_categories))
                all_results.extend(results)
            
            # Sort by relevance and limit
            all_results.sort(key=lambda x: x["relevance"], reverse=True)
            all_results = all_results[:limit]
            
            return self._format_search_results(all_results, query, f"multiple ({', '.join(selected_categories)})")
        else:
            results = search_by_type(query, search_scope, limit)
            return self._format_search_results(results, query, search_scope)
    
    def _format_search_results(self, results: List[dict], query: str, scope: str) -> str:
        """Format search results for display"""
        if not results:
            return self.format_warning([
                f"🔍 No results found for: '{query}'",
                f"📋 Searched in: {scope}",
                "💡 Try different keywords or broader search scope"
            ])
        
        # Header
        header_msgs = [
            f"🔍 Search Results for: '{query}'",
            f"📋 Scope: {scope}",
            f"📊 Found: {len(results)} results"
        ]
        
        # Results
        result_msgs = []
        for i, result in enumerate(results, 1):
            relevance_score = f"{result['relevance']:.3f}"
            collection_name = result['collection'].replace('project_', '').replace('_', ' ').title()
            
            # Format metadata info
            metadata = result.get('metadata', {})
            meta_info = []
            
            if metadata.get('disposition'):
                meta_info.append(f"Type: {metadata['disposition']}")
            if metadata.get('created'):
                created_date = metadata['created'][:10]  # Just date part
                meta_info.append(f"Created: {created_date}")
            if metadata.get('file_path'):
                filename = metadata['file_path'].split('/')[-1]
                meta_info.append(f"File: {filename}")
            if metadata.get('language'):
                meta_info.append(f"Lang: {metadata['language']}")
            
            meta_str = " | ".join(meta_info) if meta_info else "No metadata"
            
            result_msgs.extend([
                f"",
                f"🔸 Result #{i} (Relevance: {relevance_score})",
                f"📁 Collection: {collection_name}",
                f"ℹ️  {meta_str}",
                f"📄 Preview: {result['preview']}",
                "─" * 60
            ])
        
        # Combine all messages
        all_msgs = header_msgs + [""] + result_msgs
        
        return self.format_data(all_msgs)
    
    def get_help(self) -> str:
        """Return help text"""
        help_text = """
🦚 Search Handler - Smart Memory Search

Usage:
  search                   Interactive search interface
  find                     Same as search
  s                        Quick alias for search

Search Scopes:
  - Everything            Search all collections
  - Conversations         Chat logs and conversations
  - Codebase             Source code files
  - Ideas                Saved ideas and concepts
  - Brainstorm/Planning  Planning documents
  - Notes                General notes
  - Man pages            Manual pages and documentation
  - Multiple categories   Custom combination

Features:
  - Semantic similarity search
  - Relevance scoring
  - Metadata filtering
  - Preview snippets
  - Configurable result limits

Tips:
  - Use specific keywords for better results
  - Try different search scopes if no results
  - Relevance scores help identify best matches
  - Preview shows context around matches
        """
        return self.format_info([help_text.strip()])