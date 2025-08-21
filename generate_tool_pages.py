#!/usr/bin/env python3
"""
Generate individual HTML pages for each BBTools tool
Extracts information from shell scripts to create documentation
"""

import os
import glob
import re
from datetime import datetime

BBTOOLS_DIR = r"C:\releases\bbmap"
WEBSITE_DIR = r"C:\releases\bbmap_website"
TOOLS_DIR = os.path.join(WEBSITE_DIR, "tools")

def extract_tool_info(shell_script_path):
    """Extract description, usage, and parameters from shell script"""
    
    try:
        with open(shell_script_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except:
        return None, None, None
    
    # Extract description
    desc_match = re.search(r'Description:\s*(.*?)(?=\n\nUsage:|Parameters:|Usage:)', content, re.DOTALL)
    description = desc_match.group(1).strip() if desc_match else ""
    description = description.replace('\n', ' ')  # Make single line
    
    # Extract usage
    usage_match = re.search(r'Usage:\s*(.*?)(?=\n\n|\nParameters:|\nInput)', content, re.DOTALL)
    usage = usage_match.group(1).strip() if usage_match else ""
    
    # Extract author and last modified
    author_match = re.search(r'Written by (.*)', content)
    author = author_match.group(1) if author_match else "Brian Bushnell"
    
    modified_match = re.search(r'Last modified (.*)', content)
    last_modified = modified_match.group(1) if modified_match else ""
    
    return description, usage, last_modified


def generate_tool_page(tool_name, description, usage, last_modified):
    """Generate an HTML page for a tool"""
    
    # Clean up tool name for display
    display_name = tool_name.upper().replace('_', ' ')
    if display_name.startswith('BB'):
        display_name = 'BB' + display_name[2:].title()
    
    # Get current version from version.json if it exists
    version = "39.34"  # Default
    version_file = os.path.join(WEBSITE_DIR, "data", "version.json")
    if os.path.exists(version_file):
        try:
            import json
            with open(version_file, 'r') as f:
                data = json.load(f)
                version = data.get('version', version)
        except:
            pass
    
    template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{display_name} - BBTools</title>
    <meta name="description" content="{description[:155] if description else display_name + ' - BBTools bioinformatics tool'}">
    <link rel="stylesheet" href="../styles.css">
    <style>
        .tool-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 3rem 0;
            margin-bottom: 2rem;
        }}
        .tool-nav {{
            background: #f8f9fa;
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}
        .tool-nav a {{
            margin: 0 1rem;
            color: #667eea;
            text-decoration: none;
        }}
        .tool-nav a:hover {{
            text-decoration: underline;
        }}
        .usage-box {{
            background: #f4f4f4;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin: 1rem 0;
            font-family: monospace;
            overflow-x: auto;
        }}
        .info-box {{
            background: #e8f4fd;
            border: 1px solid #bee5f0;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <nav class="tool-nav">
        <div class="container">
            <a href="../index.html">← BBTools Home</a>
            <a href="../index.html#tools">All Tools</a>
            <a href="https://github.com/bbushnell/BBTools/blob/master/{tool_name}.sh" target="_blank">View Source</a>
        </div>
    </nav>
    
    <header class="tool-header">
        <div class="container">
            <h1>{display_name}</h1>
            <p>{description if description else 'A tool in the BBTools suite'}</p>
        </div>
    </header>
    
    <main class="container">
        <section id="usage">
            <h2>Usage</h2>
            <div class="usage-box">
                {usage if usage else f'{tool_name}.sh [parameters]'}
            </div>
        </section>
        
        <section id="description">
            <h2>About This Tool</h2>
            <p>{description if description else f'{display_name} is part of the BBTools suite of bioinformatics tools.'}</p>
            <div class="info-box">
                <strong>Last Updated:</strong> {last_modified if last_modified else 'See source'}<br>
                <strong>Author:</strong> Brian Bushnell<br>
                <strong>Version:</strong> BBTools v{version}
            </div>
        </section>
        
        <section id="examples">
            <h2>Examples</h2>
            <p>For detailed parameters and examples, run:</p>
            <div class="usage-box">{tool_name}.sh</div>
            <p>This will display the help message with all available options.</p>
        </section>
        
        <section id="links">
            <h2>Additional Resources</h2>
            <ul>
                <li><a href="https://github.com/bbushnell/BBTools/tree/master/docs">Documentation</a></li>
                <li><a href="https://sourceforge.net/projects/bbmap/">Download BBTools</a></li>
                <li><a href="../index.html#citation">How to Cite</a></li>
            </ul>
        </section>
    </main>
    
    <footer>
        <div class="container">
            <p>BBTools by Brian Bushnell | <a href="https://bbmap.org">bbmap.org</a></p>
        </div>
    </footer>
</body>
</html>"""
    
    return template


def main():
    """Generate pages for all tools"""
    
    print("Generating tool pages...")
    print(f"Reading from: {BBTOOLS_DIR}")
    print(f"Writing to: {TOOLS_DIR}")
    
    # Ensure tools directory exists
    os.makedirs(TOOLS_DIR, exist_ok=True)
    
    # Get all shell scripts
    shell_scripts = glob.glob(os.path.join(BBTOOLS_DIR, "*.sh"))
    
    generated = 0
    skipped = 0
    
    for script_path in shell_scripts:
        tool_name = os.path.basename(script_path).replace('.sh', '')
        
        # Skip certain utility scripts
        if tool_name in ['calcmem', 'javasetup', 'memdetect', 'Xcalcmem']:
            skipped += 1
            continue
        
        description, usage, last_modified = extract_tool_info(script_path)
        
        if description or usage:  # Generate page if we have some info
            html = generate_tool_page(tool_name, description, usage, last_modified)
            output_file = os.path.join(TOOLS_DIR, f"{tool_name}.html")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            print(f"  Generated: {tool_name}.html")
            generated += 1
        else:
            print(f"  Skipped: {tool_name} (no description found)")
            skipped += 1
    
    print(f"\nSummary:")
    print(f"  Generated: {generated} pages")
    print(f"  Skipped: {skipped} scripts")
    print(f"\nTool pages created in: {TOOLS_DIR}")
    print("\nRun deploy.sh to publish changes to bbmap.org")


if __name__ == "__main__":
    main()