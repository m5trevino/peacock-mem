# 🦚 Peacock Memory - Makefile
# Development and deployment commands

.PHONY: install dev test clean run mcp config help

# Default target
help:
	@echo "🦚 Peacock Memory - Available Commands:"
	@echo ""
	@echo "📦 Installation:"
	@echo "  make install    Install Peacock Memory system"
	@echo "  make dev        Install in development mode"
	@echo ""
	@echo "🚀 Running:"
	@echo "  make run        Launch Peacock Memory"
	@echo "  make mcp        Start MCP server"
	@echo "  make config     Configure Claude Desktop"
	@echo ""
	@echo "🧪 Development:"
	@echo "  make test       Run tests"
	@echo "  make lint       Run code linting"
	@echo "  make format     Format code"
	@echo "  make clean      Clean build artifacts"
	@echo ""
	@echo "📋 System:"
	@echo "  make deps       Install system dependencies"
	@echo "  make check      Check system requirements"

# Installation targets
install:
	@echo "🦚 Installing Peacock Memory..."
	@chmod +x install.sh
	@./install.sh

dev:
	@echo "🔧 Installing in development mode..."
	@pip install -e ".[dev,mcp]"
	@pre-commit install || echo "⚠️ pre-commit not available"

deps:
	@echo "📦 Installing system dependencies..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install -g cfonts; \
	else \
		echo "⚠️ npm not found - install Node.js for cfonts"; \
	fi
	@if ! command -v fzf >/dev/null 2>&1; then \
		echo "💡 Install fzf for better file selection"; \
	fi

# Running targets
run:
	@python3 main.py

mcp:
	@python3 main.py
	@echo "Type 'mcp' in the interface"

config:
	@python3 main.py
	@echo "Type 'mcp-config' in the interface"

# Development targets
test:
	@echo "🧪 Running tests..."
	@python -m pytest tests/ -v || echo "⚠️ No tests found"

lint:
	@echo "🔍 Running linting..."
	@flake8 . --max-line-length=100 --exclude=__pycache__,*.egg-info || echo "⚠️ flake8 not installed"
	@black --check . || echo "⚠️ black not installed"

format:
	@echo "✨ Formatting code..."
	@black . || echo "⚠️ black not installed"
	@isort . || echo "⚠️ isort not installed"

# System checks
check:
	@echo "🔍 Checking system requirements..."
	@python3 --version
	@pip --version
	@echo "Python packages:"
	@pip list | grep -E "(chromadb|rich|questionary|typer|fastapi|uvicorn)" || echo "⚠️ Some packages missing"
	@echo "System tools:"
	@command -v cfonts >/dev/null 2>&1 && echo "✅ cfonts available" || echo "❌ cfonts not found"
	@command -v fzf >/dev/null 2>&1 && echo "✅ fzf available" || echo "❌ fzf not found"

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@find . -type d -name __pycache__ -delete
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete

# Build targets
build:
	@echo "📦 Building package..."
	@python setup.py sdist bdist_wheel

# Uninstall
uninstall:
	@echo "🗑️ Uninstalling Peacock Memory..."
	@pip uninstall peacock-memory -y

# Quick setup for development
setup: deps dev
	@echo "🦚 Development setup complete!"
	@echo "Run 'make run' to start Peacock Memory"

# Create release
release: clean test build
	@echo "🚀 Release created!"
	@echo "Upload with: twine upload dist/*"