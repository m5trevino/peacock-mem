#!/bin/bash

# Create all __init__.py files for proper Python package structure

cat << 'EOF' > peacock-mem/__init__.py
"""
🦚 Peacock Memory - Modular Memory System
"""

__version__ = "1.0.0"
__author__ = "Peacock Memory Team"
__description__ = "Modular Memory System with Cyberpunk Visuals"
EOF

cat << 'EOF' > peacock-mem/commands/__init__.py
"""
🦚 Peacock Memory - Command Modules
Modular command handlers for the memory system
"""

from .base_command import BaseCommand
from .command_registry import CommandRegistry
from .file_handler import FileHandler
from .import_handler import ImportHandler
from .search_handler import SearchHandler
from .list_handler import ListHandler
from .project_handler import ProjectHandler
from .delete_handler import DeleteHandler
from .mcp_handler import MCPHandler
from .mcp_config_handler import MCPConfigHandler

__all__ = [
    "BaseCommand",
    "CommandRegistry", 
    "FileHandler",
    "ImportHandler",
    "SearchHandler",
    "ListHandler",
    "ProjectHandler",
    "DeleteHandler",
    "MCPHandler",
    "MCPConfigHandler"
]
EOF

cat << 'EOF' > peacock-mem/core/__init__.py
"""
🦚 Peacock Memory - Core System
Database, visuals, and import functionality
"""

from .database import get_client, get_or_create_collection
from .visuals import CyberStyle, get_random_banner, get_random_border
from .importers import import_claude_conversations, import_chatgpt_conversations, import_claude_projects

__all__ = [
    "get_client",
    "get_or_create_collection",
    "CyberStyle",
    "get_random_banner", 
    "get_random_border",
    "import_claude_conversations",
    "import_chatgpt_conversations",
    "import_claude_projects"
]
EOF

cat << 'EOF' > peacock-mem/utils/__init__.py
"""
🦚 Peacock Memory - Utilities
Helper functions and utilities
"""

from .json_detector import detect_json_type, ImportType, analyze_json_structure

__all__ = [
    "detect_json_type",
    "ImportType", 
    "analyze_json_structure"
]
EOF

cat << 'EOF' > peacock-mem/config/__init__.py
"""
🦚 Peacock Memory - Configuration
Configuration management and settings
"""

# Configuration will be added here as needed
EOF

echo "✅ Created all __init__.py files for proper Python package structure"