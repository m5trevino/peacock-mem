#!/usr/bin/env python3
"""
🦚 Peacock Memory - Main Application Entry Point
Modular Command-Based Memory System
"""

import sys
import os
import random
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.absolute()))

from core.visuals import CyberStyle, get_random_banner, format_grouped_output, display_banner
from core.database import get_client
from commands.command_registry import CommandRegistry
from rich.console import Console

console = Console()

class PeacockMemory:
    def __init__(self):
        self.registry = CommandRegistry()
        self.running = True
        
    def display_startup_banner(self):
        """Display random cyberpunk banner on startup"""
        banner = get_random_banner()
        os.system(banner)
        
    def get_input_with_border(self):
        """Get user input with random decorative border"""
        # Create input prompt with cyberpunk styling
        prompt_lines = [f"{CyberStyle.HOT_PINK}{CyberStyle.BOLD}Enter Command:{CyberStyle.RESET}"]
        bordered_prompt = format_grouped_output(prompt_lines, "highlight")
        
        print(bordered_prompt, end="")
        
        try:
            user_input = input(" ")
            return user_input.strip()
        except KeyboardInterrupt:
            return "exit"
            
    def process_command(self, command_input: str):
        """Process user command through registry"""
        if not command_input:
            return
            
        if command_input.lower() in ['exit', 'quit', 'q']:
            self.running = False
            shutdown_msg = format_grouped_output([
                "🦚 Peacock Memory shutting down... Stay real, G!"
            ], "success")
            console.print(shutdown_msg)
            return
            
        # Process through command registry
        try:
            result = self.registry.execute_command(command_input)
            if result:
                console.print(result)
        except Exception as e:
            error_msg = format_grouped_output([
                f"❌ Error: {str(e)}"
            ], "error")
            console.print(error_msg)
    
    def run(self):
        """Main application loop"""
        # Display startup banner
        self.display_startup_banner()
        
        # Welcome message
        welcome_lines = [
            "🦚 Peacock Memory System Ready",
            "Commands: @file, import, search, list, projects, delete, mcp, mcp-config",
            "Type 'exit' to quit"
        ]
        welcome_msg = format_grouped_output(welcome_lines, "info")
        console.print(welcome_msg)
        
        # Main loop
        while self.running:
            try:
                command_input = self.get_input_with_border()
                self.process_command(command_input)
            except KeyboardInterrupt:
                self.running = False
                shutdown_msg = format_grouped_output([
                    "🦚 Peacock Memory shutting down... Stay real, G!"
                ], "success")
                console.print(shutdown_msg)
            except Exception as e:
                error_msg = format_grouped_output([
                    f"❌ Unexpected error: {str(e)}"
                ], "error")
                console.print(error_msg)

def main():
    """Entry point"""
    app = PeacockMemory()
    app.run()

if __name__ == "__main__":
    main()
