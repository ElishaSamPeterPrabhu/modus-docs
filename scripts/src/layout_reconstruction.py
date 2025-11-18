"""
Layout Reconstruction Module
Reconstructs structured layout from Figma's coordinate-based nodes
Implements intelligent row grouping and layout inference
"""

from typing import Dict, Any, List, Optional

# A small tolerance to group elements into the same row.
Y_TOLERANCE = 5

class LayoutNode:
    """Our custom, simplified node for the reconstructed layout tree."""
    def __init__(self, figma_node: Dict[str, Any]):
        # Validate input type
        if not isinstance(figma_node, dict):
            # Create a minimal valid node if input is invalid
            print(f"Warning: LayoutNode received non-dict input: {type(figma_node).__name__}")
            figma_node = {"id": "invalid", "name": "Invalid Node", "type": "ERROR"}
        
        self.id: str = figma_node.get('id')
        self.name: str = figma_node.get('name')
        self.type: str = figma_node.get('type')
        # The computed layout: 'ABSOLUTE', 'HORIZONTAL', 'VERTICAL', 'ROW_GROUP', 'GRID'
        self.layout_type: str = 'ABSOLUTE' 
        self.children: List['LayoutNode'] = []
        # A reference to the original Figma node for later analysis (e.g., styles)
        self.original_node: Dict[str, Any] = figma_node
        # Metadata for storing additional inferred properties
        self.metadata: Dict[str, Any] = {}

    def to_dict(self) -> Dict[str, Any]:
        """Converts the LayoutNode and its children to a dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "layout_type": self.layout_type,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children]
        }

class LayoutReconstructor:
    """
    Reconstructs a structured layout from a flat list of Figma nodes
    by analyzing their spatial relationships.
    """
    def __init__(self):
        self.stats = {
            'total_nodes': 0,
            'auto_layout_nodes': 0,
            'inferred_layout_nodes': 0,
            'skipped_nodes': 0
        }
    
    def reconstruct_layout(self, root_figma_node: Dict[str, Any]) -> Optional[LayoutNode]:
        """
        Main entry point for the reconstruction process.
        
        Args:
            root_figma_node: The root frame/node from the Figma API.
            
        Returns:
            The root of our new, structured layout tree, or None if input is invalid.
        """
        if not root_figma_node:
            return None
        return self._process_node(root_figma_node)

    def _process_node(self, figma_node: Dict[str, Any]) -> LayoutNode:
        """
        Recursively processes a Figma node and its children to build the layout tree.
        """
        self.stats['total_nodes'] += 1
        layout_node = LayoutNode(figma_node)

        children = figma_node.get('children')
        if not children:
            return layout_node

        # --- Step 1: Prioritize Figma's Auto Layout ---
        layout_mode = figma_node.get('layoutMode')
        if layout_mode in ['HORIZONTAL', 'VERTICAL', 'GRID']:
            self.stats['auto_layout_nodes'] += 1
            layout_node.layout_type = layout_mode
            # With Auto Layout, the order is already correct. Just process the children.
            # Filter out non-dict children
            valid_children = [child for child in children if isinstance(child, dict)]
            if len(valid_children) < len(children):
                print(f"Warning: Skipped {len(children) - len(valid_children)} non-dict children in {figma_node.get('name', 'Unknown')}")
            layout_node.children = [self._process_node(child) for child in valid_children]
            
            # Store all auto-layout metadata
            layout_node.metadata['item_spacing'] = figma_node.get('itemSpacing', 0)
            layout_node.metadata['auto_layout'] = True
            
            # NEW: Store additional auto-layout properties
            layout_node.metadata['primary_axis_align'] = figma_node.get('primaryAxisAlignItems')
            layout_node.metadata['counter_axis_align'] = figma_node.get('counterAxisAlignItems')
            layout_node.metadata['primary_axis_sizing'] = figma_node.get('primaryAxisSizingMode')
            layout_node.metadata['counter_axis_sizing'] = figma_node.get('counterAxisSizingMode')
            layout_node.metadata['layout_wrap'] = figma_node.get('layoutWrap')
            
            # NEW: Special handling for GRID layout
            if layout_mode == 'GRID':
                # Extract grid-specific properties
                layout_node.metadata['grid_style_id'] = figma_node.get('gridStyleId')
                layout_node.metadata['layout_grids'] = figma_node.get('layoutGrids', [])
                
                # Infer columns from children positions if not explicit
                if valid_children:
                    columns = self._infer_grid_columns(valid_children)
                    layout_node.metadata['columns'] = columns
            
            return layout_node

        # --- Step 2: Check for inferred auto-layout ---
        inferred = figma_node.get('inferredAutoLayout')
        if inferred:
            # Figma has detected this could be auto-layout
            self.stats['inferred_layout_nodes'] += 1
            layout_node.layout_type = inferred.get('layoutMode', 'ABSOLUTE')
            layout_node.metadata['inferred'] = True
            layout_node.metadata['item_spacing'] = inferred.get('itemSpacing', 0)
            
            # Process children with inferred layout
            valid_children = [child for child in children if isinstance(child, dict)]
            layout_node.children = [self._process_node(child) for child in valid_children]
            return layout_node

        # --- Step 3: Heuristic Inference for non-Auto Layout Frames ---
        
        # Filter out non-dict children before processing
        valid_children = [child for child in children if isinstance(child, dict)]
        if len(valid_children) < len(children):
            print(f"Warning: Skipped {len(children) - len(valid_children)} non-dict children in {figma_node.get('name', 'Unknown')}")
        
        # Sort nodes top-to-bottom, then left-to-right.
        def sort_key(node):
            # Use absoluteBoundingBox for accurate positioning
            bounds = node.get('absoluteBoundingBox', {'x': 0, 'y': 0})
            return (bounds.get('y', 0), bounds.get('x', 0))
        


        sorted_children = sorted(valid_children, key=sort_key)

        if not sorted_children:
            return layout_node

        # --- Step 3: Group Sorted Nodes into Rows ---
        rows: List[List[Dict[str, Any]]] = []
        if sorted_children:
            current_row = [sorted_children[0]]
            last_node_y = sort_key(sorted_children[0])[0]

            for i in range(1, len(sorted_children)):
                current_node = sorted_children[i]
                current_node_y = sort_key(current_node)[0]

                # If the current node is vertically aligned with the last node, add it to the current row.
                if abs(current_node_y - last_node_y) <= Y_TOLERANCE:
                    current_row.append(current_node)
                else:
                    # Otherwise, the row is finished. Push it and start a new one.
                    rows.append(current_row)
                    current_row = [current_node]
                    last_node_y = current_node_y
            rows.append(current_row) # Add the last row

        # --- Step 4: Build the final layout tree for this node ---
        if len(rows) > 1:
            # If we have multiple rows, treat this node as a vertical container of rows.
            layout_node.layout_type = 'VERTICAL'
            layout_node.metadata['has_row_groups'] = True
            layout_node.metadata['inferred'] = True
            layout_node.metadata['row_count'] = len(rows)
            
            for index, row_nodes in enumerate(rows):
                # Sort each row by X to ensure correct horizontal order
                sorted_row_nodes = sorted(row_nodes, key=lambda n: n.get('absoluteBoundingBox', {'x': 0}).get('x', 0))

                if len(sorted_row_nodes) == 1:
                    # Single item in row, add directly
                    layout_node.children.append(self._process_node(sorted_row_nodes[0]))
                else:
                    # Multiple items, create a synthetic row group
                    row_group_node = LayoutNode({
                        'id': f"{figma_node.get('id')}-row-{index}",
                        'name': f"Inferred Row {index + 1}",
                        'type': 'GROUP' # Use a generic type for the synthetic node
                    })
                    row_group_node.layout_type = 'ROW_GROUP' # Our custom type for an inferred row
                    row_group_node.metadata['inferred'] = True
                    row_group_node.metadata['item_count'] = len(sorted_row_nodes)
                    row_group_node.children = [self._process_node(node) for node in sorted_row_nodes]
                    layout_node.children.append(row_group_node)

        elif len(rows) == 1:
            # If there's only one row, treat this node as a horizontal container.
            layout_node.layout_type = 'HORIZONTAL'
            layout_node.metadata['inferred'] = True
            sorted_row_nodes = sorted(rows[0], key=lambda n: n.get('absoluteBoundingBox', {'x': 0}).get('x', 0))
            layout_node.children = [self._process_node(node) for node in sorted_row_nodes]

        return layout_node
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'auto_layout_percentage': (
                self.stats['auto_layout_nodes'] / self.stats['total_nodes'] * 100
                if self.stats['total_nodes'] > 0 else 0
            ),
            'inference_percentage': (
                self.stats['inferred_layout_nodes'] / self.stats['total_nodes'] * 100
                if self.stats['total_nodes'] > 0 else 0
            )
        }
    
    def _infer_grid_columns(self, children: List[Dict[str, Any]]) -> int:
        """Infer number of columns in a grid from children positions"""
        if not children:
            return 1
        
        # Get unique X positions
        x_positions = set()
        for child in children:
            bounds = child.get('absoluteBoundingBox', {})
            if bounds:
                x_positions.add(round(bounds.get('x', 0)))
        
        return len(x_positions) if x_positions else 1


def create_llm_summary(
    layout_node: LayoutNode, 
    component_map: Dict[str, Any],
    max_depth: int = 5,
    current_depth: int = 0,
    skip_pure_containers: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Recursively traverses the layout tree and creates a concise summary
    for an LLM, enriching nodes with detected component information. This is the
    function that solves the "too much data" problem.

    Args:
        layout_node: The current node in the layout tree.
        component_map: A dictionary mapping node IDs to detected component info.
        max_depth: Maximum depth to traverse (default: 5)
        current_depth: Current depth in traversal
        skip_pure_containers: Skip containers with no components inside

    Returns:
        A simplified dictionary representing the subtree, ready for an LLM.
    """
    # Stop at max depth
    if current_depth >= max_depth:
        return None
    
    detected_component = component_map.get(layout_node.id)
    
    # Skip pure layout nodes that have no meaningful children
    if skip_pure_containers and not detected_component and layout_node.type in ['VECTOR', 'GROUP']:
        # Check if any child has a component
        has_component_child = any(
            component_map.get(child.id) for child in layout_node.children
        )
        if not has_component_child and len(layout_node.children) > 5:
            # Too many non-component children, skip
            return None

    summary = {
        "name": layout_node.name,
        "layout": layout_node.layout_type
    }

    if detected_component:
        summary["component"] = detected_component.get("component_type", "custom")
        # Add any other important component properties here
        if detected_component.get("properties"):
            summary["properties"] = detected_component.get("properties")
    else:
        # It's a container or a non-component element
        summary["component"] = "container" if layout_node.children else "element"

    # Only include children for meaningful containers
    if layout_node.children and (
        layout_node.layout_type in ['VERTICAL', 'HORIZONTAL', 'ROW_GROUP', 'GRID'] or
        detected_component or
        current_depth < 3  # Always show first 3 levels
    ):
        children = []
        for child in layout_node.children:
            child_summary = create_llm_summary(
                child, 
                component_map, 
                max_depth, 
                current_depth + 1,
                skip_pure_containers
            )
            if child_summary:
                children.append(child_summary)
        
        # Only add children if we have some
        if children:
            summary["children"] = children
        elif detected_component:
            # Component with no visible children, still include it
            pass
        else:
            # Container with no meaningful children, skip it
            return None

    return summary


def create_compact_llm_summary(
    layout_node: LayoutNode,
    component_map: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Creates an ultra-compact summary focusing only on components and their layout relationships.
    Perfect for LLM context windows.
    """
    def extract_components(node: LayoutNode, depth: int = 0) -> List[Dict[str, Any]]:
        """Extract only nodes with detected components"""
        results = []
        
        detected = component_map.get(node.id)
        if detected:
            item = {
                "name": node.name,
                "component": detected.get("component_type"),
                "layout_context": node.layout_type,
                "depth": depth
            }
            if detected.get("properties"):
                item["properties"] = detected.get("properties")
            results.append(item)
        
        # Recurse for children
        for child in node.children:
            results.extend(extract_components(child, depth + 1))
        
        return results
    
    # Build component hierarchy
    components = extract_components(layout_node)
    
    # Group by depth for better understanding
    hierarchy = {}
    for comp in components:
        depth = comp.pop("depth")
        if depth not in hierarchy:
            hierarchy[depth] = []
        hierarchy[depth].append(comp)
    
    return {
        "page_layout": layout_node.layout_type,
        "total_components": len(components),
        "component_hierarchy": hierarchy,
        "layout_patterns": {
            "has_row_groups": any(n.layout_type == "ROW_GROUP" for n in _get_all_nodes(layout_node)),
            "has_grid": any(n.layout_type == "GRID" for n in _get_all_nodes(layout_node)),
            "uses_auto_layout": any(n.metadata.get("auto_layout") for n in _get_all_nodes(layout_node))
        }
    }


def _get_all_nodes(node: LayoutNode) -> List[LayoutNode]:
    """Helper to get all nodes in tree"""
    nodes = [node]
    for child in node.children:
        nodes.extend(_get_all_nodes(child))
    return nodes 