#!/usr/bin/env python3
"""
Setup script for Modus Document Code repository
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def verify_structure():
    """Verify repository structure"""
    required_dirs = ["docs", "scripts"]
    required_files = ["README.md", "requirements.txt", "scripts/update_modus_components.py"]
    
    print("📁 Verifying repository structure...")
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory found")
        else:
            print(f"❌ Missing {dir_name}/ directory")
            return False
    
    # Verify two-folder structure
    consolidated_dirs = [
        "docs", 
        "component-docs"
    ]
    for dir_name in consolidated_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/ directory found")
        else:
            print(f"❌ Missing {dir_name}/ directory")
            return False
    
    for file_name in required_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name} found")
        else:
            print(f"❌ Missing {file_name}")
            return False
    
    return True

def show_usage():
    """Show usage instructions"""
    print("\n🚀 Setup complete! Here's how to use this repository:")
    print("\n📚 Update documentation:")
    print("   python scripts/update_modus_components.py")
    print("   python scripts/extract_all_docs.py")
    
    print("\n📖 Browse documentation:")
    print("   ls docs/                         # Framework .mdx files and getting-started guides")
    print("   ls component-docs/               # Component specifications")
    
    print("\n🔍 Quick access:")
    print("   cat component-docs/_all_components.json  # Component list")
    
    print("\n📝 For more information:")
    print("   cat README.md")
    print("   cat CONTRIBUTING.md")

def main():
    """Main setup function"""
    print("🚀 Modus Document Code Setup")
    print("=" * 40)
    
    if not check_python_version():
        sys.exit(1)
    
    if not verify_structure():
        print("❌ Repository structure verification failed")
        sys.exit(1)
    
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    show_usage()
    print("\n✅ Setup completed successfully!")

if __name__ == "__main__":
    main()

