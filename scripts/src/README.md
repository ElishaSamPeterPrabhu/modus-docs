# Source Code

This folder contains the core Python modules for Figma-to-Modus component analysis:

## Modules

- **component_parser.py** - Parses Modus component documentation from source files
- **figma_node_analyzer.py** - Analyzes individual Figma nodes to identify component types
- **figma_page_analyzer.py** - Analyzes full Figma pages with multiple components
- **figma_smart_analyzer.py** - Smart detection to automatically determine if analyzing a page or component

## Usage

These modules are imported by the main `server.py` MCP server to provide Figma analysis functionality. 