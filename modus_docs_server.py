#!/usr/bin/env python3
"""
Modus Documentation MCP Server

Provides two tools for accessing Modus documentation:
1. get_modus_implementation_data - Fetches framework integration guides and general docs
2. get_modus_component_data - Fetches component-specific documentation
"""

import json
import logging
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# Configure logging to stderr (NEVER use print() or stdout in MCP servers)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("modus-docs-server")

# Base directory for the documentation
BASE_DIR = Path(__file__).parent.absolute()
DOCS_DIR = BASE_DIR / "docs"
COMPONENT_DOCS_DIR = BASE_DIR / "component-docs"

# Initialize FastMCP server
mcp = FastMCP("modus-docs")


def read_implementation_doc(docs_name: str) -> dict[str, Any]:
    """
    Read implementation documentation from the docs/ folder.
    
    Args:
        docs_name: Name of the document (without .mdx extension)
        
    Returns:
        Dictionary with document content and metadata
    """
    doc_path = DOCS_DIR / f"{docs_name}.mdx"
    
    if not doc_path.exists():
        available_docs = [f.stem for f in DOCS_DIR.glob("*.mdx")]
        return {
            "error": f"Document '{docs_name}' not found",
            "available_documents": available_docs,
            "requested": docs_name
        }
    
    try:
        content = doc_path.read_text(encoding='utf-8')
        return {
            "document_name": docs_name,
            "file_path": str(doc_path),
            "content": content,
            "type": "implementation_guide",
            "format": "mdx"
        }
    except Exception as e:
        return {
            "error": f"Error reading document: {str(e)}",
            "document_name": docs_name
        }


def read_component_doc(component_name: str) -> dict[str, Any]:
    """
    Read component documentation from the component-docs/ folder.
    
    Args:
        component_name: Name of the component (e.g., 'modus-wc-table')
        
    Returns:
        Dictionary with component documentation
    """
    # Handle special case for all components catalog
    if component_name == "_all_components":
        doc_path = COMPONENT_DOCS_DIR / "_all_components.json"
    else:
        doc_path = COMPONENT_DOCS_DIR / f"{component_name}.json"
    
    if not doc_path.exists():
        available_components = [
            f.stem for f in COMPONENT_DOCS_DIR.glob("*.json")
            if not f.name.startswith(".")
        ]
        return {
            "error": f"Component '{component_name}' not found",
            "available_components": available_components,
            "requested": component_name
        }
    
    try:
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        return {
            "component_name": component_name,
            "file_path": str(doc_path),
            "data": content,
            "type": "component_documentation",
            "format": "json"
        }
    except json.JSONDecodeError as e:
        return {
            "error": f"Invalid JSON in component documentation: {str(e)}",
            "component_name": component_name
        }
    except Exception as e:
        return {
            "error": f"Error reading component documentation: {str(e)}",
            "component_name": component_name
        }


@mcp.tool()
def get_modus_implementation_data(docs_name: str) -> str:
    """
    Looks up and parses documentation from the Modus documentation repository.
    
    Retrieves framework integration guides, getting started guides, and general documentation.
    
    Available documents:
    - Framework Integration: "angular", "react", "vue"
    - Guides: "getting-started", "accessibility", "form-inputs", "modus-icon-usage", "styling", "testing"
    
    Args:
        docs_name: The name of the document to retrieve (without .mdx extension).
                  Examples: 'angular', 'react', 'vue', 'getting-started', 'accessibility',
                  'form-inputs', 'modus-icon-usage', 'styling', 'testing'
    
    Returns:
        JSON string containing the document content and metadata
    """
    logger.info(f"Fetching implementation doc: {docs_name}")
    result = read_implementation_doc(docs_name)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_modus_component_data(component_name: str) -> str:
    """
    Looks up and parses component documentation for Modus Web Components.
    
    Retrieves component properties, events, methods, slots, usage examples, and story 
    documentation from the component documentation repository.
    
    Special component names:
    - "_all_components" - Returns catalog of all available components
    
    Component naming format: "modus-wc-{component-name}"
    Examples: "modus-wc-table", "modus-wc-button", "modus-wc-alert"
    
    Args:
        component_name: The name of the Modus component (e.g., 'modus-wc-table', 'modus-wc-button')
                       or '_all_components' for the complete catalog
    
    Returns:
        JSON string containing the component's complete documentation
    """
    logger.info(f"Fetching component doc: {component_name}")
    result = read_component_doc(component_name)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run(transport="http", port=8080)

