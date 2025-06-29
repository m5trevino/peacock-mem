"""
🦚 Peacock Memory - Visual System
Cyberpunk styling, random banners, and decorative borders
"""

import random
import subprocess
import os
import sys
from typing import Dict, List

# Check if we're running in MCP mode
MCP_MODE = any(arg in ['mcp', '--mcp', 'mcp-server'] for arg in sys.argv)

# CYBERPUNK STYLING SYSTEM
class CyberStyle:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # CYBERPUNK COLORS
    NEON_GREEN = '\033[92m'
    NEON_CYAN = '\033[96m'
    NEON_PURPLE = '\033[95m'
    NEON_YELLOW = '\033[93m'
    NEON_RED = '\033[91m'
    MATRIX_GREEN = '\033[32m'
    ELECTRIC_BLUE = '\033[94m'
    HOT_PINK = '\033[35m'

# MASSIVE CYBERPUNK CFONTS ARSENAL
CYBERPUNK_CFONTS = [
    "cfonts 'PEACOCKMEMORY' -f pallet -g yellow,red --align center --max-length 7",
    "cfonts 'PEACOCKMEMORY' -f slick -g green,cyan --align center --max-length 7",
    "cfonts 'PEACOCKMEMORY' -f shade -g red,magenta --align center --max-length 7",
    "cfonts 'PEACOCKMEMORY' -f simple3d -g cyan,magenta --align center --max-length 7",
    "cfonts 'PEACOCKMEMORY' -f simple -g blue,magenta --align center --max-length 7",
]

def get_random_banner() -> str:
    """Get random cfont banner command"""
    if MCP_MODE:
        return ""  # No banners in MCP mode
    return random.choice(CYBERPUNK_CFONTS)

def get_random_border() -> Dict[str, str]:
    """Get random decorative border that adapts to content width"""
    border_styles = [
        {"char": "═", "corner_tl": "╔", "corner_tr": "╗", "corner_bl": "╚", "corner_br": "╝", "side": "║"},
        {"char": "━", "corner_tl": "┏", "corner_tr": "┓", "corner_bl": "┗", "corner_br": "┛", "side": "┃"},
        {"char": "─", "corner_tl": "┌", "corner_tr": "┐", "corner_bl": "└", "corner_br": "┘", "side": "│"},
    ]
    
    return random.choice(border_styles)

def create_border(content_lines: List[str], border_style: Dict[str, str]) -> Dict[str, str]:
    """Create dynamic border based on content width"""
    if MCP_MODE:
        return {"top": "", "bottom": "", "side": "", "width": 0}
        
    if not content_lines:
        width = 50
    else:
        # Find longest line (strip ANSI codes for accurate length)
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        max_width = max(len(ansi_escape.sub('', line)) for line in content_lines)
        width = max(max_width + 4, 50)
    
    top = border_style["corner_tl"] + border_style["char"] * (width - 2) + border_style["corner_tr"]
    bottom = border_style["corner_bl"] + border_style["char"] * (width - 2) + border_style["corner_br"]
    
    return {
        "top": top,
        "bottom": bottom,
        "side": border_style["side"],
        "width": width
    }

def display_banner():
    """Display random banner"""
    if MCP_MODE:
        return  # No banners in MCP mode
        
    banner_cmd = get_random_banner()
    try:
        subprocess.run(banner_cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        pass  # Silent fail

def format_grouped_output(lines: List[str], message_type: str = "info") -> str:
    """Format multiple lines with grouped border and colors"""
    if MCP_MODE:
        # Plain text output for MCP mode
        return "\n".join(lines)
        
    if not lines:
        return ""
    
    # Color mapping
    color_map = {
        "success": CyberStyle.NEON_GREEN,
        "error": CyberStyle.NEON_RED,
        "info": CyberStyle.NEON_CYAN,
        "warning": CyberStyle.NEON_YELLOW,
        "highlight": CyberStyle.NEON_PURPLE,
        "progress": CyberStyle.ELECTRIC_BLUE,
        "data": CyberStyle.MATRIX_GREEN
    }
    
    color = color_map.get(message_type, CyberStyle.NEON_CYAN)
    border_style = get_random_border()
    
    # Apply color to all lines
    colored_lines = [f"{color}{CyberStyle.BOLD}{line}{CyberStyle.RESET}" for line in lines]
    
    # Create dynamic border
    border = create_border(lines, border_style)
    
    # Build output with proper padding
    output = f"\n{border['top']}\n"
    for line in colored_lines:
        # Pad line to border width
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_line = ansi_escape.sub('', line)
        padding = border['width'] - len(clean_line) - 4
        output += f"{border['side']} {line}{' ' * max(0, padding)} {border['side']}\n"
    output += f"{border['bottom']}\n"
    
    return output

def format_single_message(message: str, message_type: str = "info") -> str:
    """Format single message with border and color"""
    return format_grouped_output([message], message_type)
