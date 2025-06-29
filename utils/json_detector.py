"""
🦚 Peacock Memory - JSON Type Detection
Detect JSON format for smart import routing
"""

from enum import Enum
from typing import Dict, Any, List

class ImportType(Enum):
    """Import type enumeration"""
    CLAUDE_CONVERSATIONS = "Claude Conversations"
    CHATGPT_CONVERSATIONS = "ChatGPT Conversations"
    CLAUDE_PROJECTS = "Claude Projects"
    UNKNOWN = "Unknown Format"

def detect_json_type(json_data: Dict[str, Any]) -> ImportType:
    """Detect JSON type based on structure"""
    
    if _is_claude_conversations(json_data):
        return ImportType.CLAUDE_CONVERSATIONS
    elif _is_chatgpt_conversations(json_data):
        return ImportType.CHATGPT_CONVERSATIONS
    elif _is_claude_projects(json_data):
        return ImportType.CLAUDE_PROJECTS
    else:
        return ImportType.UNKNOWN

def _is_claude_conversations(json_data: Dict[str, Any]) -> bool:
    """Check if JSON matches Claude conversations format"""
    try:
        # Claude conversations typically have a root-level array or dict with conversations
        if isinstance(json_data, list):
            # Check if it's a list of conversations
            if len(json_data) > 0:
                first_item = json_data[0]
                if isinstance(first_item, dict):
                    # Look for typical Claude conversation fields
                    claude_fields = ['uuid', 'name', 'created_at', 'updated_at', 'chat_messages']
                    return any(field in first_item for field in claude_fields)
        
        elif isinstance(json_data, dict):
            # Check if it has conversation-like structure
            if 'conversations' in json_data:
                return True
            
            # Check for direct conversation fields
            claude_fields = ['uuid', 'name', 'created_at', 'updated_at', 'chat_messages']
            if any(field in json_data for field in claude_fields):
                return True
            
            # Check if values are conversations
            for value in json_data.values():
                if isinstance(value, list) and len(value) > 0:
                    first_conv = value[0]
                    if isinstance(first_conv, dict):
                        if any(field in first_conv for field in claude_fields):
                            return True
        
        return False
    except (KeyError, TypeError, IndexError):
        return False

def _is_chatgpt_conversations(json_data: Dict[str, Any]) -> bool:
    """Check if JSON matches ChatGPT conversations format"""
    try:
        # ChatGPT export typically has specific structure
        if isinstance(json_data, list):
            if len(json_data) > 0:
                first_item = json_data[0]
                if isinstance(first_item, dict):
                    # Look for ChatGPT-specific fields
                    chatgpt_fields = ['title', 'create_time', 'mapping', 'conversation_id']
                    return any(field in first_item for field in chatgpt_fields)
        
        elif isinstance(json_data, dict):
            # Check for direct ChatGPT fields
            chatgpt_fields = ['title', 'create_time', 'mapping', 'conversation_id']
            if any(field in json_data for field in chatgpt_fields):
                return True
            
            # Check if it has mapping structure (typical of ChatGPT)
            if 'mapping' in json_data:
                mapping = json_data['mapping']
                if isinstance(mapping, dict):
                    # Check if mapping contains message nodes
                    for node in mapping.values():
                        if isinstance(node, dict) and 'message' in node:
                            return True
        
        return False
    except (KeyError, TypeError, IndexError):
        return False

def _is_claude_projects(json_data: Dict[str, Any]) -> bool:
    """Check if JSON matches Claude projects format"""
    try:
        # Claude projects typically have projects array or project-specific fields
        if isinstance(json_data, dict):
            # Look for project-specific top-level keys
            project_keys = ['projects', 'project_name', 'documents', 'knowledge_docs']
            if any(key in json_data for key in project_keys):
                return True
            
            # Check if it has projects array
            if 'projects' in json_data and isinstance(json_data['projects'], list):
                return True
            
            # Check for individual project structure
            project_fields = ['name', 'description', 'documents', 'created_at']
            if any(field in json_data for field in project_fields):
                # Additional check for documents structure
                if 'documents' in json_data and isinstance(json_data['documents'], list):
                    return True
        
        elif isinstance(json_data, list):
            # Check if it's a list of projects
            if len(json_data) > 0:
                first_item = json_data[0]
                if isinstance(first_item, dict):
                    project_fields = ['name', 'description', 'documents', 'created_at']
                    return any(field in first_item for field in project_fields)
        
        return False
    except (KeyError, TypeError, IndexError):
        return False

def analyze_json_structure(json_data: Dict[str, Any], max_depth: int = 3) -> Dict[str, Any]:
    """Analyze JSON structure for debugging"""
    def analyze_value(value, depth=0):
        if depth > max_depth:
            return "..."
        
        if isinstance(value, dict):
            return {
                "type": "dict",
                "keys": list(value.keys())[:10],  # First 10 keys
                "sample": {k: analyze_value(v, depth+1) for k, v in list(value.items())[:3]}
            }
        elif isinstance(value, list):
            return {
                "type": "list",
                "length": len(value),
                "sample": [analyze_value(item, depth+1) for item in value[:3]]
            }
        else:
            return {
                "type": type(value).__name__,
                "value": str(value)[:100] if isinstance(value, str) else value
            }
    
    return analyze_value(json_data)

def get_import_suggestions(json_data: Dict[str, Any]) -> List[str]:
    """Get suggestions for unknown JSON formats"""
    suggestions = []
    
    structure = analyze_json_structure(json_data)
    
    if isinstance(json_data, dict):
        keys = json_data.keys()
        
        if any('message' in str(key).lower() for key in keys):
            suggestions.append("This might be a conversation format - check message structure")
        
        if any('project' in str(key).lower() for key in keys):
            suggestions.append("This might be a project format - check for documents or files")
        
        if any('chat' in str(key).lower() for key in keys):
            suggestions.append("This appears to be chat data - verify conversation format")
    
    elif isinstance(json_data, list) and len(json_data) > 0:
        first_item = json_data[0]
        if isinstance(first_item, dict):
            keys = first_item.keys()
            
            if any('conversation' in str(key).lower() for key in keys):
                suggestions.append("List of conversations detected - check conversation format")
            
            if any('project' in str(key).lower() for key in keys):
                suggestions.append("List of projects detected - verify project structure")
    
    if not suggestions:
        suggestions.append("Unknown format - ensure JSON matches Claude/ChatGPT export structure")
    
    return suggestions