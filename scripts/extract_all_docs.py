#!/usr/bin/env python3
"""
Extract Consolidated Modus Documentation

This script extracts essential documentation from the Modus Web Components repository:
- Component READMEs
- Getting started guides (Storybook documentation)

The extracted documentation is organized into a consolidated structure with:
- docs/components/ - Component README files
- docs/getting-started/ - Getting started guides
- docs/component-docs/ - Component specifications (from data/)
"""

import os
import sys
import json
import shutil
from typing import Dict, Any, List
from pathlib import Path
import re

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Configuration
MODUS_LOCAL_DIR = "./data/modus-wc-2.0"
DOCS_OUTPUT_DIR = "./docs"

def ensure_output_dir():
    """Ensure the output directory structure exists"""
    os.makedirs(DOCS_OUTPUT_DIR, exist_ok=True)
    os.makedirs("./component-docs", exist_ok=True)

def extract_framework_docs():
    """Extract framework .mdx files only"""
    print("📚 Extracting framework .mdx files...")
    
    framework_files = [
        ("src/stories/frameworks/react.mdx", "react.mdx"),
        ("src/stories/frameworks/angular.mdx", "angular.mdx"),
        ("src/stories/frameworks/vue.mdx", "vue.mdx")
    ]
    
    extracted_count = 0
    
    for source_path, output_filename in framework_files:
        full_source_path = os.path.join(MODUS_LOCAL_DIR, source_path)
        output_path = os.path.join(DOCS_OUTPUT_DIR, output_filename)
        
        if os.path.exists(full_source_path):
            try:
                shutil.copy2(full_source_path, output_path)
                print(f"  ✅ {source_path} -> {output_filename}")
                extracted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to copy {source_path}: {e}")
        else:
            print(f"  ⚠️  Not found: {source_path}")
    
    print(f"  📊 Extracted {extracted_count} framework .mdx files")

def extract_general_docs():
    """Extract general documentation files"""
    print("📄 Extracting general documentation...")
    
    general_docs = [
        ("README.md", "main-README.md"),
        ("CONTRIBUTING.md", "CONTRIBUTING.md"),
        ("CODE-GUIDELINES.md", "CODE-GUIDELINES.md"),
        ("RELEASING.md", "RELEASING.md"),
        ("SECURITY.md", "SECURITY.md"),
        ("LICENSE", "LICENSE.txt"),
        ("docs/build-scripts.md", "build-scripts.md"),
        ("docs/considerations.md", "considerations.md"),
        ("docs/custom-themes.md", "custom-themes.md"),
        ("docs/project-design.md", "project-design.md"),
        ("docs/responsive-design.md", "responsive-design.md")
    ]
    
    extracted_count = 0
    
    for source_file, output_file in general_docs:
        source_path = os.path.join(MODUS_LOCAL_DIR, source_file)
        output_path = os.path.join(DOCS_OUTPUT_DIR, "general", output_file)
        
        if os.path.exists(source_path):
            try:
                shutil.copy2(source_path, output_path)
                print(f"  ✅ {source_file} -> {output_file}")
                extracted_count += 1
            except Exception as e:
                print(f"  ❌ Failed to copy {source_file}: {e}")
        else:
            print(f"  ⚠️  Not found: {source_file}")
    
    print(f"  📊 Extracted {extracted_count} general documentation files")

def extract_storybook_docs():
    """Extract Storybook documentation files"""
    print("📖 Extracting Storybook documentation...")
    
    stories_dir = os.path.join(MODUS_LOCAL_DIR, "src/stories")
    getting_started_output = DOCS_OUTPUT_DIR
    
    extracted_count = 0
    
    if os.path.exists(stories_dir):
        for file in os.listdir(stories_dir):
            if file.endswith('.mdx'):
                source_path = os.path.join(stories_dir, file)
                output_path = os.path.join(getting_started_output, file)
                
                try:
                    shutil.copy2(source_path, output_path)
                    print(f"  ✅ stories/{file}")
                    extracted_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to copy stories/{file}: {e}")
    
    print(f"  📊 Extracted {extracted_count} Storybook documentation files")

def extract_icons_info():
    """Extract icons information and create icons documentation"""
    print("🎨 Extracting icons documentation...")
    
    icons_dir = os.path.join(MODUS_LOCAL_DIR, "src/icons")
    icons_output = os.path.join(DOCS_OUTPUT_DIR, "icons")
    
    if not os.path.exists(icons_dir):
        print("  ❌ Icons directory not found")
        return
    
    # Get all icon files
    icon_files = [f for f in os.listdir(icons_dir) if f.endswith('.icon.tsx')]
    
    # Create icons documentation
    icons_data = {
        "total_icons": len(icon_files),
        "icons": [],
        "categories": {}
    }
    
    for icon_file in icon_files:
        icon_name = icon_file.replace('.icon.tsx', '')
        
        # Try to categorize icons
        category = "general"
        if "outline" in icon_name:
            category = "outline"
        elif "solid" in icon_name:
            category = "solid"
        elif "dark" in icon_name or "light" in icon_name:
            category = "theme"
        elif "logo" in icon_name:
            category = "branding"
        
        icon_info = {
            "name": icon_name,
            "filename": icon_file,
            "category": category
        }
        
        icons_data["icons"].append(icon_info)
        
        if category not in icons_data["categories"]:
            icons_data["categories"][category] = []
        icons_data["categories"][category].append(icon_name)
    
    # Save icons documentation
    icons_doc_path = os.path.join(icons_output, "icons-catalog.json")
    with open(icons_doc_path, 'w') as f:
        json.dump(icons_data, f, indent=2)
    
    # Copy the modus-icon-usage.mdx if it exists
    icon_usage_source = os.path.join(MODUS_LOCAL_DIR, "src/stories/modus-icon-usage.mdx")
    if os.path.exists(icon_usage_source):
        icon_usage_output = os.path.join(icons_output, "modus-icon-usage.mdx")
        shutil.copy2(icon_usage_source, icon_usage_output)
        print(f"  ✅ Copied icon usage documentation")
    
    print(f"  📊 Cataloged {len(icon_files)} icons across {len(icons_data['categories'])} categories")

def extract_component_readmes():
    """Extract individual component README files"""
    print("📦 Extracting component README files...")
    
    components_dir = os.path.join(MODUS_LOCAL_DIR, "src/components")
    components_output = os.path.join(DOCS_OUTPUT_DIR, "components")
    
    if not os.path.exists(components_dir):
        print("  ❌ Components directory not found")
        return
    
    extracted_count = 0
    
    for item in os.listdir(components_dir):
        component_path = os.path.join(components_dir, item)
        
        if os.path.isdir(component_path) and item.startswith('modus-wc-'):
            readme_path = os.path.join(component_path, "readme.md")
            
            if os.path.exists(readme_path):
                output_filename = f"{item}-README.md"
                output_path = os.path.join(components_output, output_filename)
                
                try:
                    shutil.copy2(readme_path, output_path)
                    print(f"  ✅ {item}/readme.md -> {output_filename}")
                    extracted_count += 1
                except Exception as e:
                    print(f"  ❌ Failed to copy {item}/readme.md: {e}")
    
    print(f"  📊 Extracted {extracted_count} component README files")

def extract_examples():
    """Extract framework integration examples"""
    print("💡 Extracting framework examples...")
    
    examples_output = os.path.join(DOCS_OUTPUT_DIR, "examples")
    
    example_sources = [
        ("integrations/react/test-react-v18/src/examples", "react"),
        ("integrations/vue/test-app/src/examples", "vue")
    ]
    
    extracted_count = 0
    
    for source_path, framework in example_sources:
        full_source_path = os.path.join(MODUS_LOCAL_DIR, source_path)
        framework_output = os.path.join(examples_output, framework)
        
        if os.path.exists(full_source_path):
            os.makedirs(framework_output, exist_ok=True)
            
            try:
                for file in os.listdir(full_source_path):
                    if file.endswith(('.tsx', '.vue', '.ts', '.js')):
                        source_file = os.path.join(full_source_path, file)
                        output_file = os.path.join(framework_output, file)
                        shutil.copy2(source_file, output_file)
                        extracted_count += 1
                
                print(f"  ✅ Extracted {framework} examples")
            except Exception as e:
                print(f"  ❌ Failed to extract {framework} examples: {e}")
        else:
            print(f"  ⚠️  Examples not found: {source_path}")
    
    print(f"  📊 Extracted {extracted_count} example files")

def create_documentation_index():
    """Create an index of all extracted documentation"""
    print("📋 Creating documentation index...")
    
    index = {
        "extraction_info": {
            "timestamp": str(os.path.getmtime(MODUS_LOCAL_DIR)),
            "source": MODUS_LOCAL_DIR,
            "output": DOCS_OUTPUT_DIR
        },
        "structure": {},
        "file_count": 0
    }
    
    # Walk through the output directory and catalog everything
    for root, dirs, files in os.walk(DOCS_OUTPUT_DIR):
        if files:  # Only include directories with files
            rel_path = os.path.relpath(root, DOCS_OUTPUT_DIR)
            if rel_path == ".":
                rel_path = "root"
            
            index["structure"][rel_path] = {
                "files": files,
                "count": len(files)
            }
            index["file_count"] += len(files)
    
    # Save index
    index_path = os.path.join(DOCS_OUTPUT_DIR, "_documentation_index.json")
    with open(index_path, 'w') as f:
        json.dump(index, f, indent=2)
    
    print(f"  📊 Created index with {index['file_count']} total files")

def main():
    """Main execution function"""
    print("🚀 Modus Documentation Extraction Tool (Consolidated with Frameworks)")
    print("=" * 60)
    
    # Check if Modus source exists
    if not os.path.exists(MODUS_LOCAL_DIR):
        print(f"❌ Modus source not found at {MODUS_LOCAL_DIR}")
        print("💡 Please run update_modus_components.py first to get the source code")
        return
    
    try:
        # Step 1: Ensure output directory structure
        ensure_output_dir()
        
        # Step 2: Extract framework .mdx files
        extract_framework_docs()
        
        # Step 3: Extract Storybook documentation (getting-started)
        extract_storybook_docs()
        
        print("\n✅ Documentation extraction complete!")
        print(f"📁 All documentation available at: {DOCS_OUTPUT_DIR}")
        print("📋 Structure:")
        print("   docs/                    - Framework .mdx files and getting-started guides")
        print("   component-docs/          - Component specifications")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
