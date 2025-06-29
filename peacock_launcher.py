#!/usr/bin/env python3
"""
🦚 Peacock Memory Launcher
Wrapper to fix entry point issues
"""
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

def main():
    """Entry point for pea-mem command"""
    from main import main as app_main
    app_main()

if __name__ == "__main__":
    main()
