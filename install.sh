#!/bin/bash

echo "🦚 Installing Peacock Memory System..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

# Install cfonts if npm is available
if command -v npm &> /dev/null; then
    echo "📦 Installing cfonts for ASCII banners..."
    npm install -g cfonts
else
    echo "⚠️ npm not found - cfonts banners will be skipped"
    echo "💡 Install Node.js and run: npm install -g cfonts"
fi

# Install fzf if not available
if ! command -v fzf &> /dev/null; then
    echo "📦 fzf not found - file selection will use questionary fallback"
    echo "💡 Install fzf for better file selection experience"
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   Debian/Ubuntu: sudo apt install fzf"
        echo "   Arch: sudo pacman -S fzf"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "   macOS: brew install fzf"
    fi
fi

# Install Python dependencies
echo "🔧 Installing Python dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "📦 Installing Peacock Memory package..."
pip install -e .

# Create desktop entry (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]] && [ -d "$HOME/.local/share/applications" ]; then
    echo "🖥️ Creating desktop entry..."
    cat << EOF > "$HOME/.local/share/applications/peacock-memory.desktop"
[Desktop Entry]
Name=Peacock Memory
Comment=🦚 Modular Memory System with Cyberpunk Visuals
Exec=pea-mem
Icon=terminal
Terminal=true
Type=Application
Categories=Development;Utility;
EOF
fi

echo ""
echo "✅ Peacock Memory installation complete!"
echo ""
echo "🚀 Quick Start:"
echo "   pea-mem                    # Launch main interface"
echo "   pea-mem → @/path/to/file   # Add files"
echo "   pea-mem → import           # Import conversations/projects"
echo "   pea-mem → search           # Search memory"
echo "   pea-mem → mcp              # Start MCP server"
echo "   pea-mem → mcp-config       # Setup Claude Desktop"
echo ""
echo "📚 Documentation: README.md"
echo "🦚 Ready to build some real shit!"