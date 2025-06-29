# 🦚 Peacock Memory

**Modular Memory System with Cyberpunk Visuals and MCP Integration**

A street-smart, modular memory system built for developers who demand speed, style, and substance. Every command is isolated, every interaction is visual, and every search is semantic.

## ✨ Features

### 🎯 Core Functionality
- **Modular Architecture**: Each command is its own isolated module
- **Semantic Search**: ChromaDB-powered vector similarity search
- **Smart Import**: Auto-detects Claude conversations, ChatGPT exports, and Claude projects
- **Project Management**: Organize code, notes, and ideas by project
- **Interactive UI**: Clean questionary-based interfaces with cyberpunk styling

### 🎨 Visual Experience
- **80+ Random Banners**: Unique cfont banner on every launch
- **Decorative Borders**: Random ornate borders around all output
- **Cyberpunk Colors**: Neon greens, electric blues, hot pinks
- **Grouped Output**: Related messages grouped with single borders
- **Progress Indicators**: Visual feedback for long operations

### 🔌 MCP Integration
- **Model Context Protocol**: Native Claude Desktop integration
- **REST API**: FastAPI-based MCP server
- **Auto-Configuration**: One-command Claude Desktop setup
- **Real-time Memory**: Bidirectional memory access with Claude

## 🚀 Quick Start

### Installation

```bash
# Clone and setup
git clone <repository>
cd peacock-mem
pip install -r requirements.txt
python setup.py install

# Or install with MCP support
pip install -e ".[mcp]"
```

### First Run

```bash
# Launch Peacock Memory
pea-mem

# You'll see a random cyberpunk banner and input box
> @/path/to/your/code.py
> import @/path/to/conversations.json
> search
> projects
```

## 📝 Commands

### 📁 File Management
```bash
@/path/to/file.py     # Add single file with disposition
@/path/to/directory/  # Interactive directory browser (fzf)
```

### 📥 Import
```bash
import                           # Interactive import
import @conversations.json       # Smart JSON detection
import @chatgpt.json @claude.json @projects.json  # Batch import
```

### 🔍 Search
```bash
search                # Interactive search with category filters
```

### 📋 List & Browse
```bash
list                  # Browse by category
projects              # Project management interface
```

### 🗑️ Delete
```bash
delete                # Interactive deletion (single/multiple/bulk)
remove                # Same as delete
```

### 🌐 MCP Server
```bash
mcp                   # Start MCP server with banner
mcp-config            # Configure Claude Desktop integration
```

## 🏗️ Architecture

### Modular Command System
```
commands/
├── base_command.py          # Abstract base class
├── command_registry.py      # Auto-discovery & routing
├── file_handler.py          # @ commands
├── import_handler.py        # Smart JSON import
├── search_handler.py        # Semantic search
├── list_handler.py          # Browse & list
├── project_handler.py       # Project management
├── delete_handler.py        # Interactive deletion
├── mcp_handler.py           # MCP server
└── mcp_config_handler.py    # Claude Desktop config
```

### Core System
```
core/
├── database.py              # ChromaDB operations
├── visuals.py               # Cyberpunk styling system
└── importers.py             # Import logic
```

### Benefits
- **Fault Isolation**: One broken command doesn't affect others
- **Easy Extension**: Drop new command file → auto-discovered
- **Independent Testing**: Test each command module separately
- **Clean Recovery**: Fix single command without system restart

## 🎨 Visual System

### Random Banners (80+ variations)
- Gradient combinations (green→cyan, red→magenta)
- Transition effects (3-color flows)
- Single color classics (neon blues, electric greens)
- Background combinations (cyan on magenta)
- Special effects (rainbow, candy, system)

### Decorative Borders
```
╔═════════════════════════════════════════╗
║ Your content here                       ║
╚═════════════════════════════════════════╝

┍━━━━━━━━━━━━━━━━━━━━━━»•» 🌺 «•«━━━━┑
│ Grouped output with ornate borders     │
┕━━━━━»•» 🌺 «•«━━━━━━━━━━━━━━━━━━━━━━━━┙
```

### Color Scheme
- **Success**: Neon Green (`\033[92m`)
- **Error**: Neon Red (`\033[91m`)
- **Info**: Neon Cyan (`\033[96m`)
- **Warning**: Neon Yellow (`\033[93m`)
- **Highlight**: Neon Purple (`\033[95m`)
- **Progress**: Electric Blue (`\033[94m`)
- **Data**: Matrix Green (`\033[32m`)

## 🔌 MCP Integration

### Setup Claude Desktop
```bash
# In Peacock Memory
> mcp-config

# Start MCP server
> mcp

# Restart Claude Desktop
# MCP server now available in Claude
```

### API Endpoints
- `GET /` - Server status
- `GET /health` - Database health
- `GET /collections` - List collections
- `POST /search` - Search memory
- `POST /add_memory` - Add new memory

## 📊 File Dispositions

### Project-Required
- **Codebase**: Source code files
- **Plan/Brainstorm**: Planning documents

### Global
- **Idea**: Saved concepts
- **Note**: General notes
- **man-page**: Documentation

## 🔍 Search Types

- **Everything**: All collections
- **Conversations**: Claude/ChatGPT imports
- **Codebase**: Source code files
- **Ideas**: Saved concepts
- **Brainstorm**: Planning documents
- **Notes**: General notes
- **Man pages**: Documentation

## 📁 Database Structure

```
~/peacock_db/
├── project_<name>/          # Project collections
├── conversations/           # Imported conversations
├── global_files/           # Non-project files
└── chroma.sqlite3          # ChromaDB storage
```

## 🛠️ Development

### Adding New Commands

1. Create new handler in `commands/`
2. Inherit from `BaseCommand`
3. Implement required methods
4. Add to `command_registry.py`

```python
from commands.base_command import BaseCommand

class MyHandler(BaseCommand):
    def get_aliases(self) -> List[str]:
        return ["mycommand", "mc"]
    
    def execute(self, command_input: str) -> Optional[str]:
        return self.format_success(["Command executed!"])
    
    def get_help(self) -> str:
        return self.format_info(["Help text here"])
```

### Visual Formatting
```python
# Use inherited methods
self.format_success(["Success message"])
self.format_error(["Error message"])
self.format_info(["Info message"])
self.format_data(["Data output"])
```

## 🔧 Dependencies

### Core
- `chromadb>=0.4.0` - Vector database
- `rich>=13.0.0` - Terminal formatting
- `questionary>=2.0.0` - Interactive prompts
- `typer>=0.9.0` - CLI framework

### Optional (MCP)
- `fastapi>=0.100.0` - API server
- `uvicorn>=0.20.0` - ASGI server

### System
- `cfonts` - ASCII art banners (npm install -g cfonts)
- `fzf` - File selection (optional, falls back to questionary)

## 📜 License

MIT License - Build something real with it.

## 🦚 Philosophy

**"Be quick, but don't hurry."** - John Wooden