#!/usr/bin/env python3
"""
Update Modus Components and Extract Documentation

This script:
1. Ensures Modus Web Components 2.0 source is available (auto-clones from GitHub if needed)
2. Uses local source from data/modus-wc-2.0 (or clones from prod branch if missing)
3. Extracts component properties, events, methods, slots, and story examples
4. Updates the component-docs JSON files

Auto-cloning: If data/modus-wc-2.0 doesn't exist, it will automatically clone
from https://github.com/trimble-oss/modus-wc-2.0.git (prod branch)
"""

import os
import sys
import json
import subprocess
import re
from typing import Dict, Any, List
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import our enhanced parser
from component_parser import get_component_documentation

# Configuration - Use local Modus 2.0 source
MODUS_LOCAL_DIR = "./data/modus-wc-2.0"
COMPONENT_DOCS_DIR = "./component-docs"
MODUS_SRC_PATH = "src/components"
MODUS_REPO_URL = "https://github.com/trimble-oss/modus-wc-2.0.git"
MODUS_BRANCH = "main"

def ensure_modus_source():
    """Ensure Modus 2.0 source is available, clone if necessary, and pull latest changes"""
    if os.path.exists(MODUS_LOCAL_DIR):
        print(f"📁 Found existing Modus 2.0 source at {MODUS_LOCAL_DIR}")
        print(f"🔄 Pulling latest changes from {MODUS_BRANCH} branch...")
        
        try:
            # First, fetch the latest changes
            fetch_command = ["git", "-C", MODUS_LOCAL_DIR, "fetch", "origin", MODUS_BRANCH]
            print(f"🔄 Fetching latest changes...")
            subprocess.run(fetch_command, capture_output=True, text=True, check=True)
            
            # Then try to pull with merge strategy
            pull_command = ["git", "-C", MODUS_LOCAL_DIR, "pull", "--no-rebase", "origin", MODUS_BRANCH]
            print(f"🔄 Running: {' '.join(pull_command)}")
            result = subprocess.run(pull_command, capture_output=True, text=True, check=True)
            
            if "Already up to date" in result.stdout:
                print(f"✅ Repository is already up to date")
            else:
                print(f"✅ Successfully pulled latest changes")
                print(f"   {result.stdout.strip()}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Warning: Failed to pull latest changes: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            
            # Try to reset to the remote branch as a fallback
            try:
                print(f"🔄 Attempting to reset to origin/{MODUS_BRANCH}...")
                reset_command = ["git", "-C", MODUS_LOCAL_DIR, "reset", "--hard", f"origin/{MODUS_BRANCH}"]
                subprocess.run(reset_command, capture_output=True, text=True, check=True)
                print(f"✅ Successfully reset to latest origin/{MODUS_BRANCH}")
                return True
            except subprocess.CalledProcessError as reset_error:
                print(f"⚠️  Warning: Failed to reset to remote branch: {reset_error}")
                print(f"🔄 Git conflicts detected. Re-cloning repository for fresh start...")
                
                # Remove the existing directory and re-clone
                try:
                    subprocess.run(["rm", "-rf", MODUS_LOCAL_DIR], check=True)
                    print(f"🗑️  Removed existing repository")
                    # Fall through to the clone section below
                    return clone_fresh_repository()
                except Exception as cleanup_error:
                    print(f"⚠️  Warning: Failed to cleanup existing repository: {cleanup_error}")
                    print(f"💡 Continuing with existing local version...")
                    return True
        except Exception as e:
            print(f"⚠️  Warning: Unexpected error pulling changes: {e}")
            print(f"💡 Continuing with existing local version...")
            return True
    
    print(f"📥 Modus 2.0 source not found locally. Cloning from {MODUS_REPO_URL}...")
    return clone_fresh_repository()

def clone_fresh_repository():
    """Clone a fresh copy of the Modus repository"""
    print(f"🌿 Branch: {MODUS_BRANCH}")
    
    try:
        # Create data directory if it doesn't exist
        data_dir = os.path.dirname(MODUS_LOCAL_DIR)
        os.makedirs(data_dir, exist_ok=True)
        
        # Clone the repository
        clone_command = [
            "git", "clone", 
            "--branch", MODUS_BRANCH,
            "--single-branch",
            "--depth", "1",  # Shallow clone for faster download
            MODUS_REPO_URL,
            MODUS_LOCAL_DIR
        ]
        
        print(f"🔄 Running: {' '.join(clone_command)}")
        result = subprocess.run(clone_command, capture_output=True, text=True, check=True)
        
        print(f"✅ Successfully cloned Modus 2.0 from {MODUS_BRANCH} branch")
        
        # Verify the clone was successful
        components_path = os.path.join(MODUS_LOCAL_DIR, MODUS_SRC_PATH)
        if os.path.exists(components_path):
            component_count = len([d for d in os.listdir(components_path) 
                                 if os.path.isdir(os.path.join(components_path, d)) 
                                 and d.startswith('modus-wc-')])
            print(f"📦 Found {component_count} Modus components in cloned repository")
            return True
        else:
            print(f"❌ Error: Components directory not found after cloning at {components_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error cloning repository: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        print(f"💡 Make sure you have git installed and can access {MODUS_REPO_URL}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def process_all_components():
    """Process all components in the local Modus 2.0 repository"""
    components_path = os.path.join(MODUS_LOCAL_DIR, MODUS_SRC_PATH)
    
    if not os.path.exists(components_path):
        print(f"❌ Components directory not found at {components_path}")
        return
    
    print(f"\n📝 Extracting component documentation from {components_path}...")
    
    # Create output directory if it doesn't exist
    os.makedirs(COMPONENT_DOCS_DIR, exist_ok=True)
    
    processed_count = 0
    updated_count = 0
    
    # Get all component directories
    component_dirs = [d for d in os.listdir(components_path) 
                     if os.path.isdir(os.path.join(components_path, d)) 
                     and d.startswith('modus-wc-')]
    
    for component_name in component_dirs:
        component_dir = os.path.join(components_path, component_name)
        tsx_file = os.path.join(component_dir, f"{component_name}.tsx")
        
        # Check if the main .tsx file exists
        if os.path.exists(tsx_file):
            print(f"  🔍 Processing: {component_name}")
            
            # Use enhanced parser to get component info
            component_info = get_component_documentation(component_name)
            
            if component_info and 'error' not in component_info:
                tag_name = component_info.get('tag', component_name)
                output_file = os.path.join(COMPONENT_DOCS_DIR, f"{tag_name}.json")
                
                # Check if file needs updating
                update_needed = True
                if os.path.exists(output_file):
                    try:
                        with open(output_file, 'r') as f:
                            existing_data = json.load(f)
                        # Simple comparison - could be more sophisticated
                        if existing_data == component_info:
                            update_needed = False
                    except:
                        # If we can't read the existing file, update it
                        update_needed = True
                
                if update_needed:
                    # Save to JSON file
                    with open(output_file, 'w') as f:
                        json.dump(component_info, f, indent=2)
                    print(f"    ✅ Updated: {tag_name} - Props: {len(component_info.get('properties', []))}, Events: {len(component_info.get('events', []))}, Methods: {len(component_info.get('methods', []))}")
                    updated_count += 1
                else:
                    print(f"    ⏭️  Unchanged: {tag_name}")
                
                processed_count += 1
            else:
                print(f"    ❌ Failed to parse: {component_name}")
                if component_info and 'error' in component_info:
                    print(f"       Error: {component_info['error']}")
        else:
            print(f"  ⚠️  No .tsx file found for: {component_name}")
    
    print(f"\n✅ Processed {processed_count} components, updated {updated_count}")

def update_component_mapper():
    """Update the component mapper with any new components"""
    print("\n🔄 Updating component mapper...")
    
    # Read all component docs
    all_components = []
    for file in os.listdir(COMPONENT_DOCS_DIR):
        if file.endswith('.json'):
            with open(os.path.join(COMPONENT_DOCS_DIR, file), 'r') as f:
                data = json.load(f)
                if 'tag' in data:
                    all_components.append(data['tag'])
    
    # Update the modus_component_mapper.py NAME_MAPPINGS if needed
    mapper_file = './src/modus_component_mapper.py'
    if os.path.exists(mapper_file):
        print(f"  Found {len(all_components)} components")
        print(f"  Components: {', '.join(sorted(all_components)[:10])}...")
        
        # Create a summary file
        summary_file = os.path.join(COMPONENT_DOCS_DIR, '_all_components.json')
        with open(summary_file, 'w') as f:
            json.dump({
                "total": len(all_components),
                "components": sorted(all_components),
                "last_updated": str(os.path.getmtime(MODUS_LOCAL_DIR))
            }, f, indent=2)
        print(f"  📄 Created summary at {summary_file}")

def cleanup_old_temp():
    """Clean up old temporary directory if it exists"""
    temp_dir = "./temp_modus_repo"
    if os.path.exists(temp_dir):
        print("\n🧹 Cleaning up old temporary files...")
        subprocess.run(["rm", "-rf", temp_dir], check=True)

def main():
    """Main execution function"""
    print("🚀 Modus Component Update Tool (v2.0)")
    print("=" * 50)
    
    try:
        # Step 0: Ensure Modus 2.0 source is available (clone if needed)
        if not ensure_modus_source():
            print(f"\n❌ Failed to obtain Modus 2.0 source. Cannot continue.")
            return
        
        # Step 1: Extract component documentation
        process_all_components()
        
        # Step 2: Update component mapper
        update_component_mapper()
        
        # Step 3: Cleanup old temp directory
        cleanup_old_temp()
        
        print("\n✅ All done! Component documentation has been updated.")
        print(f"💡 Modus 2.0 source available at: {MODUS_LOCAL_DIR}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 