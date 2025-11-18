#!/usr/bin/env python3
"""
Component Parser Module

This module handles parsing of Stencil.js component source files to extract
properties, events, methods, slots, story examples, and usage scripts with their documentation.
"""

import os
import re
import json
from typing import Dict, Any, List, Optional

def parse_stencil_component(file_content: str) -> Dict[str, Any]:
    """
    Parse a Stencil.js component file to extract all component information.
    
    Args:
        file_content: The complete source code of the component file
        
    Returns:
        Dictionary containing component description, properties, events, methods, slots,
        story examples, and usage scripts
    """
    doc = {
        "description": "", 
        "properties": [], 
        "events": [], 
        "methods": [], 
        "slots": [],
        "examples": {},
        "scripts": []
    }
    
    lines = file_content.split('\n')
    
    # Extract component description from JSDoc before @Component (if it exists)
    component_description = extract_component_description(lines)
    doc["description"] = component_description
    
    # Parse properties, events, and methods
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Handle @Prop decorators
        if line.startswith('@Prop'):
            prop_info = extract_prop_info(lines, i)
            if prop_info:
                doc["properties"].append(prop_info)
                i = prop_info.get('end_line', i) + 1
                continue
        
        # Handle @Event and @StencilEvent decorators
        elif line.startswith('@Event') or line.startswith('@StencilEvent'):
            event_info = extract_event_info(lines, i)
            if event_info:
                doc["events"].append(event_info)
                i = event_info.get('end_line', i) + 1
                continue
        
        # Handle @Method decorators
        elif line.startswith('@Method'):
            method_info = extract_method_info(lines, i)
            if method_info:
                doc["methods"].append(method_info)
                i = method_info.get('end_line', i) + 1
                continue
        
        i += 1
    
    # Extract slots from render function
    slots = extract_slots(lines)
    doc["slots"] = slots
    
    return doc

def extract_component_description(lines: List[str]) -> str:
    """Extract component description from JSDoc before @Component."""
    for i, line in enumerate(lines):
        if "@Component" in line:
            # Look backwards for JSDoc
            j = i - 1
            while j >= 0 and lines[j].strip() == "":
                j -= 1
            if j >= 0 and lines[j].strip().endswith("*/"):
                k = j
                while k >= 0 and not lines[k].strip().startswith("/**"):
                    k -= 1
                if k >= 0:
                    jsdoc_lines = [lines[l] for l in range(k, j+1)]
                    clean_lines = []
                    for line in jsdoc_lines:
                        clean = line.strip().lstrip('/*').lstrip('*').rstrip('*/').strip()
                        if clean and not clean.startswith('@'):
                            clean_lines.append(clean)
                    return " ".join(clean_lines)
            break
    return ""

def extract_prop_info(lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
    """Extract property information from @Prop decorator."""
    jsdoc_description = _extract_jsdoc_before_line(lines, start_idx)
    
    # Collect property declaration lines until semicolon
    prop_lines = []
    j = start_idx
    while j < len(lines):
        prop_lines.append(lines[j])
        if ';' in lines[j]:
            break
        j += 1
    
    prop_text = ' '.join(prop_lines).strip()
    
    # Extract mutable flag
    mutable = 'mutable: true' in prop_text
    
    # Updated regex to handle properties with or without explicit type annotations
    # Handles both: @Prop() propName: type = default; and @Prop() propName = default;
    prop_match = re.search(r'@Prop\([^)]*\)\s*(\w+[?!]?)\s*(?::\s*([^=;]+?))?\s*=\s*([^;]+?);', prop_text, re.DOTALL)
    if not prop_match:
        # Try pattern with type but no default
        prop_match = re.search(r'@Prop\([^)]*\)\s*(\w+[?!]?)\s*:\s*([^=;]+?);', prop_text, re.DOTALL)
    
    if prop_match:
        prop_name = prop_match.group(1).replace('?', '').replace('!', '')
        
        # Handle different match patterns
        if prop_match.lastindex == 3:  # Has default value
            if prop_match.group(2):  # Has explicit type
                prop_type = prop_match.group(2).strip()
            else:  # No explicit type, infer from default
                prop_default = prop_match.group(3).strip()
                # Infer type from default value
                if prop_default == 'true' or prop_default == 'false':
                    prop_type = 'boolean'
                elif prop_default.startswith("'") or prop_default.startswith('"'):
                    prop_type = 'string'
                elif prop_default.replace('.', '').replace('-', '').isdigit():
                    prop_type = 'number'
                else:
                    prop_type = 'any'
            prop_default = prop_match.group(3).strip()
        elif prop_match.lastindex == 2:  # Has type but no default
            prop_type = prop_match.group(2).strip()
            prop_default = None
        else:
            prop_type = 'any'
            prop_default = None
        
        return {
            "name": prop_name,
            "type": prop_type,
            "description": jsdoc_description,
            "default": prop_default,
            "mutable": mutable,
            "end_line": j
        }
    return None

def extract_event_info(lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
    """Extract event information from @Event or @StencilEvent decorator."""
    jsdoc_description = _extract_jsdoc_before_line(lines, start_idx)
    
    # Collect all lines until we find a line ending with "};" or ">;"
    event_lines = []
    j = start_idx
    while j < len(lines):
        event_lines.append(lines[j])
        if lines[j].strip().endswith('};') or lines[j].strip().endswith('>;'):
            break
        j += 1
    
    event_text = ' '.join(event_lines).strip()
    
    # Extract event name and detail type - handle both @Event and @StencilEvent
    name_match = re.search(r'@(?:Event|StencilEvent)\(\)\s*(\w+)!?', event_text)
    emitter_match = re.search(r'EventEmitter<(.+?)>', event_text, re.DOTALL)
    
    if name_match:
        event_name = name_match.group(1)
        event_detail = "void"
        
        if emitter_match:
            event_detail = emitter_match.group(1).strip()
            event_detail = re.sub(r'\s+', ' ', event_detail)  # Clean up whitespace
        
        return {
            "name": event_name,
            "detail": event_detail,
            "description": jsdoc_description,
            "end_line": j
        }
    return None

def extract_method_info(lines: List[str], start_idx: int) -> Optional[Dict[str, Any]]:
    """Extract method information from @Method decorator."""
    jsdoc_description = _extract_jsdoc_before_line(lines, start_idx)
    
    # Collect method signature lines
    method_lines = []
    j = start_idx + 1
    brace_count = 0
    found_signature = False
    
    while j < len(lines):
        line = lines[j]
        method_lines.append(line)
        
        # Count braces to find complete method signature
        if '(' in line:
            found_signature = True
            brace_count += line.count('(')
        if ')' in line:
            brace_count -= line.count(')')
        
        if found_signature and brace_count == 0:
            break
        j += 1
    
    method_text = ' '.join(method_lines).strip()
    
    # Extract method name, parameters, and return type
    method_match = re.search(r'(?:async\s+)?(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^{]+?))?(?:\s*{)?', method_text)
    if method_match:
        method_name = method_match.group(1)
        method_params = method_match.group(2).strip() if method_match.group(2) else ""
        method_return = method_match.group(3).strip() if method_match.group(3) else "void"
        
        return {
            "name": method_name,
            "signature": f"({method_params})",
            "parameters": method_params,
            "returnType": method_return,
            "description": jsdoc_description,
            "end_line": j
        }
    return None

def extract_slots(lines: List[str]) -> List[Dict[str, str]]:
    """Extract slots from render function."""
    slots = []
    in_render = False
    
    for line in lines:
        if 'render()' in line:
            in_render = True
        if in_render and ('</Host>' in line or 'return' in line and '}' in line):
            in_render = False
        if in_render:
            slot_matches = re.findall(r'<slot\s*(?:name="([^"]*)")?', line)
            for match in slot_matches:
                slot_name = match if match else "default"
                if not any(slot["name"] == slot_name for slot in slots):
                    slots.append({
                        "name": slot_name,
                        "description": f"Slot for {slot_name} content"
                    })
    return slots

def _extract_jsdoc_before_line(lines: List[str], line_index: int) -> str:
    """Extract JSDoc comment before a given line."""
    jsdoc_description = ""
    j = line_index - 1
    while j >= 0 and lines[j].strip() == "":
        j -= 1
    if j >= 0 and lines[j].strip().endswith("*/"):
        k = j
        while k >= 0 and not lines[k].strip().startswith("/**"):
            k -= 1
        if k >= 0:
            jsdoc_lines = [lines[l] for l in range(k, j+1)]
            clean_lines = []
            for jsdoc_line in jsdoc_lines:
                clean = jsdoc_line.strip().lstrip('/*').lstrip('*').rstrip('*/').strip()
                if clean and not clean.startswith('@'):
                    clean_lines.append(clean)
            jsdoc_description = " ".join(clean_lines)
    return jsdoc_description

def extract_story_examples(story_file_path: str) -> Dict[str, Any]:
    """
    Extract examples from Storybook story files.
    
    Args:
        story_file_path: Path to the .stories.ts file
        
    Returns:
        Dictionary containing story examples and usage patterns
    """
    if not os.path.exists(story_file_path):
        return {}
    
    with open(story_file_path, 'r', encoding='utf-8') as f:
        story_content = f.read()
    
    examples = {
        "basic": None,
        "variations": [],
        "args": {},
        "argTypes": {},
        "usage": []
    }
    
    # Extract default args
    args_match = re.search(r'args:\s*{([^}]+)}', story_content, re.DOTALL)
    if args_match:
        args_text = args_match.group(1)
        # Parse args into dictionary
        arg_matches = re.findall(r"'?(\w+)'?\s*:\s*([^,]+)(?:,|$)", args_text)
        for key, value in arg_matches:
            examples["args"][key] = value.strip()
    
    # Extract argTypes (control definitions)
    argTypes_match = re.search(r'argTypes:\s*{([^}]+)}', story_content, re.DOTALL)
    if argTypes_match:
        argTypes_text = argTypes_match.group(1)
        argType_matches = re.findall(r"(\w+):\s*{([^}]+)}", argTypes_text)
        for key, value in argType_matches:
            control_match = re.search(r'control:\s*{\s*type:\s*[\'"](\w+)[\'"]', value)
            if control_match:
                examples["argTypes"][key] = {
                    "control": control_match.group(1),
                    "options": []
                }
                # Extract options if present
                options_match = re.search(r'options:\s*\[([^\]]+)\]', value)
                if options_match:
                    options = [opt.strip().strip("'\"") for opt in options_match.group(1).split(',')]
                    examples["argTypes"][key]["options"] = options
    
    # Extract template example
    template_match = re.search(r'return html`([^`]+)`', story_content, re.DOTALL)
    if template_match:
        examples["basic"] = template_match.group(1).strip()
    
    # Extract event handlers
    events_match = re.search(r'handles:\s*\[([^\]]+)\]', story_content)
    if events_match:
        events = [evt.strip().strip("'\"") for evt in events_match.group(1).split(',')]
        examples["events"] = events
    
    return examples

def generate_usage_scripts(component_doc: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate common usage scripts for the component based on its properties and events.
    
    Args:
        component_doc: Parsed component documentation
        
    Returns:
        List of usage script examples
    """
    scripts = []
    tag_name = component_doc.get("tag", "modus-component")
    
    # Basic usage example
    basic_props = []
    for prop in component_doc.get("properties", []):
        if prop.get("default") is None and "?" not in str(prop.get("type", "")):
            # Required prop
            basic_props.append(f'{prop["name"]}="example-{prop["name"]}"')
    
    basic_usage = f'<{tag_name} {" ".join(basic_props)}></{tag_name}>'
    scripts.append({
        "title": "Basic Usage",
        "code": basic_usage,
        "description": "Minimal required properties"
    })
    
    # Event handling example
    if component_doc.get("events"):
        event_handlers = []
        for event in component_doc["events"]:
            event_name = event["name"]
            handler_name = f'handle{event_name[0].upper() + event_name[1:]}'
            event_handlers.append(f'on{event_name[0].upper() + event_name[1:]}={{(e) => {handler_name}(e.detail)}}')
        
        event_example = f'<{tag_name} {" ".join(event_handlers)}></{tag_name}>'
        scripts.append({
            "title": "Event Handling",
            "code": event_example,
            "description": "Handling component events"
        })
    
    # Method calling example
    if component_doc.get("methods"):
        method_script = f"""// Get component reference
const component = document.querySelector('{tag_name}');

// Call methods"""
        for method in component_doc["methods"]:
            method_name = method["name"]
            params = method.get("parameters", "")
            method_script += f"\nawait component.{method_name}({params});"
        
        scripts.append({
            "title": "Calling Methods",
            "code": method_script,
            "description": "How to call component methods"
        })
    
    return scripts

def get_component_documentation(component_name: str) -> Dict[str, Any]:
    """
    Get enhanced parsed documentation for a specific component including story examples.
    
    Args:
        component_name: Name of the component (e.g., 'modus-wc-table')
        
    Returns:
        Dictionary containing enhanced component documentation or error message
    """
    # Get the project root directory (go up from scripts/src/ to project root)
    script_dir = os.path.dirname(os.path.abspath(__file__))  # scripts/src/
    scripts_dir = os.path.dirname(script_dir)  # scripts/
    project_root = os.path.dirname(scripts_dir)  # project root
    
    # Path to the Modus 2.0 source
    modus_src_path = os.path.join(project_root, "data", "modus-wc-2.0", "src", "components", component_name)
    
    # Component source file
    component_file = os.path.join(modus_src_path, f"{component_name}.tsx")
    
    if not os.path.exists(component_file):
        # Fallback to cached JSON if source not available
        component_docs_path = os.path.join(project_root, f"component-docs/{component_name}.json")
        
        if not os.path.exists(component_docs_path):
            return {"error": f"Documentation for '{component_name}' not found."}
            
        try:
            with open(component_docs_path, "r") as f:
                documentation = json.load(f)
                return documentation
        except Exception as e:
            return {"error": f"Failed to load documentation for '{component_name}': {str(e)}"}
    
    try:
        # Parse component source
        with open(component_file, 'r', encoding='utf-8') as f:
            component_content = f.read()
        
        doc = parse_stencil_component(component_content)
        
        # Add component tag name
        doc["tag"] = component_name
        
        # Extract story examples if available
        story_file = os.path.join(modus_src_path, f"{component_name}.stories.ts")
        if os.path.exists(story_file):
            # Get the full story file content
            with open(story_file, 'r', encoding='utf-8') as f:
                story_content = f.read()
            
            # Extract structured examples
            doc["examples"] = extract_story_examples(story_file)
            
            # Add the full story content for complete reference
            doc["storyExample"] = {
                "template": doc["examples"].get("basic", ""),
                "args": doc["examples"].get("args", {}),
                "argTypes": doc["examples"].get("argTypes", {}),
                "events": doc["examples"].get("events", []),
                "fullContent": story_content  # Include the complete story file
            }
        
        # Add usage scripts for common patterns
        doc["scripts"] = generate_usage_scripts(doc)
        
        return doc
        
    except Exception as e:
        return {"error": f"Failed to parse component '{component_name}': {str(e)}"}

def update_component_data_cache():
    """
    Update the cached component data by parsing all available components.
    This should be called when component source files are updated.
    
    Returns:
        Dictionary with update status and component count
    """
    components_dir = os.path.join("data", "modus-wc-2.0", "src", "components")
    
    if not os.path.exists(components_dir):
        return {"error": f"Components directory not found: {components_dir}"}
    
    updated_components = []
    errors = []
    
    # Find all component directories
    for item in os.listdir(components_dir):
        component_dir = os.path.join(components_dir, item)
        if os.path.isdir(component_dir):
            component_file = os.path.join(component_dir, f"{item}.tsx")
            if os.path.exists(component_file):
                try:
                    doc = get_component_documentation(item)
                    if "error" not in doc:
                        # Save to component-docs directory
                        output_file = os.path.join("component-docs", f"{item}.json")
                        with open(output_file, 'w') as f:
                            json.dump(doc, f, indent=2)
                        updated_components.append(item)
                    else:
                        errors.append(f"{item}: {doc['error']}")
                except Exception as e:
                    errors.append(f"{item}: {str(e)}")
    
    return {
        "updated_components": updated_components,
        "component_count": len(updated_components),
        "errors": errors
    }

if __name__ == "__main__":
    # Test the parser
    result = get_component_documentation("modus-wc-table")
    # Save the result to JSON
    with open('component-docs/modus-wc-select.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # Commented out print statements
    # print(f"Properties: {len(result.get('properties', []))}")
    # print(f"Events: {len(result.get('events', []))}")
    # print(f"Methods: {len(result.get('methods', []))}")
    # print(f"Slots: {len(result.get('slots', []))}") 