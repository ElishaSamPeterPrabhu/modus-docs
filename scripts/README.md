# Documentation Generation Scripts

This directory contains automated tools for maintaining and updating Modus Web Components documentation.

## 📁 Scripts Overview

### `update_modus_components.py`
**Purpose**: Updates component specifications and documentation from the latest Modus Web Components source.

**Features**:
- Automatically fetches latest source from GitHub main branch
- Handles git conflicts with intelligent fallback strategies
- Extracts component properties, events, methods, and slots
- Updates JSON specifications for all components
- Creates comprehensive component catalog

**Usage**:
```bash
python scripts/update_modus_components.py
```

**Output**:
- Updates `docs/component-docs/` with latest component specifications
- Creates `docs/component-docs/_all_components.json` summary file

### `extract_all_docs.py`
**Purpose**: Extracts essential documentation from the Modus repository in a consolidated structure.

**Features**:
- Copies component README files
- Organizes Storybook documentation (getting-started guides)
- Creates consolidated documentation structure

**Usage**:
```bash
python scripts/extract_all_docs.py
```

**Output**:
- Populates `docs/` directory with consolidated documentation structure:
  - `docs/components/` - Component README files
  - `docs/getting-started/` - Getting started guides
  - `docs/component-docs/` - Component specifications

## 🔧 Core Modules (`src/` directory)

### `component_parser.py`
- Parses Modus component source files
- Extracts TypeScript interfaces and component metadata
- Handles Stencil component decorators
- Generates structured component documentation

### `universal_figma_analyzer.py`
- Advanced Figma design analysis
- Layout reconstruction and component mapping
- Integration with Modus component specifications

### `modus_component_mapper.py`
- Maps Figma designs to Modus components
- Provides intelligent component suggestions
- Handles component property mapping

### `figma_data_filter.py`
- Filters and processes Figma API data
- Cleans and structures design information
- Prepares data for component analysis

### `layout_reconstruction.py`
- Reconstructs layout hierarchies from Figma designs
- Identifies component relationships and nesting
- Generates structural component trees

## 🚀 Usage Examples

### Basic Update Workflow
```bash
# Update component specifications from latest source
python scripts/update_modus_components.py

# Extract all documentation
python scripts/extract_all_docs.py

# Verify results
ls -la docs/
```

### Development Workflow
```bash
# Install dependencies
pip install -r requirements.txt

# Run individual scripts
python scripts/update_modus_components.py
python scripts/extract_all_docs.py

# Check output
cat docs/component-docs/_all_components.json
```

## 📊 Script Output Details

### Component Documentation Update
```
🚀 Modus Component Update Tool (v2.0)
==================================================
📁 Found existing Modus 2.0 source at ./data/modus-wc-2.0
🔄 Pulling latest changes from main branch...
✅ Successfully pulled latest changes
📝 Extracting component documentation...
✅ Processed 44 components, updated X
```

### Documentation Extraction
```
🚀 Modus Documentation Extraction Tool
==================================================
📚 Extracting framework documentation...
📄 Extracting general documentation...
🎨 Extracting icons documentation...
📦 Extracting component README files...
✅ Documentation extraction complete!
📊 Created index with 123 total files
```

## 🛠️ Configuration

### Environment Variables
- `MODUS_REPO_URL`: Override default Modus repository URL
- `MODUS_BRANCH`: Override default branch (main)
- `DOCS_OUTPUT_DIR`: Override documentation output directory

### Script Configuration
Both scripts include configuration constants at the top:

```python
# update_modus_components.py
MODUS_LOCAL_DIR = "./data/modus-wc-2.0"
COMPONENT_DOCS_DIR = "./docs/component-docs"
MODUS_BRANCH = "main"

# extract_all_docs.py
MODUS_LOCAL_DIR = "./data/modus-wc-2.0"
DOCS_OUTPUT_DIR = "./docs"
```

## 🔍 Troubleshooting

### Common Issues

**Git conflicts during update**:
- Scripts automatically handle conflicts by re-cloning
- Check internet connection and GitHub access

**Missing dependencies**:
```bash
pip install -r requirements.txt
```

**Permission errors**:
- Ensure write permissions to output directories
- Check file system permissions

**Source not found**:
- Run `update_modus_components.py` first to fetch source
- Verify network connectivity

### Debug Mode
Add verbose logging to scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Notes

- **First run**: Downloads ~50MB Modus source repository
- **Subsequent runs**: Only pulls latest changes (much faster)
- **Documentation extraction**: Processes ~123 files in seconds
- **Component parsing**: Analyzes 44 components efficiently

## 🔄 Automation

### GitHub Actions Example
```yaml
name: Update Documentation
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  update-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: python scripts/update_modus_components.py
      - run: python scripts/extract_all_docs.py
      - run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add .
          git diff --staged --quiet || git commit -m "Update documentation"
          git push
```

### Cron Job Example
```bash
# Update documentation daily at midnight
0 0 * * * cd /path/to/modus-document-code && python scripts/update_modus_components.py && python scripts/extract_all_docs.py
```

## 📝 Contributing to Scripts

When modifying scripts:
1. Maintain backward compatibility
2. Add appropriate error handling
3. Update documentation
4. Test with various scenarios
5. Follow existing code style

See `CONTRIBUTING.md` for detailed guidelines.

