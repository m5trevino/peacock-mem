#!/bin/bash

# Create the main peacock-mem directory structure
echo "🦚 Creating Peacock Memory directory structure..."

mkdir -p peacock-mem/{commands,core,utils,config}

# Create all the command files
touch peacock-mem/commands/__init__.py
touch peacock-mem/commands/base_command.py
touch peacock-mem/commands/command_registry.py
touch peacock-mem/commands/import_handler.py
touch peacock-mem/commands/search_handler.py
touch peacock-mem/commands/list_handler.py
touch peacock-mem/commands/project_handler.py
touch peacock-mem/commands/delete_handler.py
touch peacock-mem/commands/mcp_handler.py
touch peacock-mem/commands/file_handler.py
touch peacock-mem/commands/mcp_config_handler.py

# Create core system files
touch peacock-mem/core/__init__.py
touch peacock-mem/core/database.py
touch peacock-mem/core/visuals.py
touch peacock-mem/core/importers.py

# Create utility files
touch peacock-mem/utils/__init__.py
touch peacock-mem/utils/json_detector.py
touch peacock-mem/utils/file_utils.py

# Create config files
touch peacock-mem/config/__init__.py
touch peacock-mem/config/settings.py

# Main application files
touch peacock-mem/main.py
touch peacock-mem/setup.py
touch peacock-mem/requirements.txt
touch peacock-mem/README.md

echo "🦚 Directory structure created successfully!"
echo "📁 peacock-mem/"
echo "├── commands/           # Modular command handlers"
echo "├── core/              # Core system components"
echo "├── utils/             # Utility functions"
echo "├── config/            # Configuration files"
echo "├── main.py            # Main application entry"
echo "├── setup.py           # Package setup"
echo "├── requirements.txt   # Dependencies"
echo "└── README.md          # Documentation"