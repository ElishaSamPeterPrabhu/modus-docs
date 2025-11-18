"""
Figma Data Filter
Filters unnecessary data from Figma API responses for LLM consumption
"""

from typing import Dict, Any, List, Set, Optional
import json

class FigmaDataFilter:
    """
    Filters Figma API data to remove unnecessary properties and reduce JSON size
    Optimized for LLM analysis while preserving layout and component information
    """
    
    def __init__(self):
        # Essential properties to keep for layout understanding
        self.essential_properties = {
            'id', 'name', 'type', 'visible',
            'children',  # For hierarchy
            'absoluteBoundingBox',  # For positioning
            'layoutMode', 'layoutAlign', 'itemSpacing',  # For auto-layout
            'constraints',  # Basic constraints only
            'componentId', 'mainComponent',  # For component instances
            'characters', 'style',  # For text
            'opacity',  # Basic visibility
            'clipsContent',  # Layout behavior
            'locked', 'isMask',  # Important flags
            
            # NEW: Additional auto-layout properties
            'primaryAxisAlignItems',  # Main axis alignment
            'counterAxisAlignItems',  # Cross axis alignment
            'primaryAxisSizingMode',  # AUTO or FIXED
            'counterAxisSizingMode',  # AUTO or FIXED
            'layoutWrap',  # Wrap behavior
            'layoutGrow',  # Flex grow
            'layoutPositioning',  # ABSOLUTE or AUTO
            
            # NEW: Grid layout properties (Figma 2023+)
            'layoutGrids',  # Layout grids
            'gridStyleId',  # Grid style reference
            
            # NEW: Important for accurate reconstruction
            'inferredAutoLayout',  # Figma's smart layout detection
            'numberOfFixedChildren',  # For scrolling frames
            'overflowDirection',  # Scroll behavior
            
            # Component properties
            'componentPropertyDefinitions',  # Keep for component analysis
            'variantProperties',  # For variant components
        }
        
        # Properties to completely remove (too verbose for LLM)
        self.remove_properties = {
            'styles',  # Complex style references
            'effects',  # Shadows, blurs etc - very verbose
            'exportSettings',  # Multiple export configs
            'transitionNodeID', 'transitionDuration', 'transitionEasing',  # Prototyping
            'overflowDirection',  # Rarely needed
            'numberOfFixedChildren',  # Internal data
            'overlayPositionType', 'overlayBackgroundInteraction',  # Prototyping
            'preserveRatio',  # Image specific
            'reactions',  # Prototyping interactions
            'playbackSettings',  # Animation data
            'individualStrokeWeights',  # Detailed stroke data
            'strokeDashes',  # Vector details
            'relativeTransform',  # Complex transform matrix
            'size',  # Redundant with absoluteBoundingBox
            'counterAxisSizingMode', 'primaryAxisSizingMode',  # Complex layout
            'paddingLeft', 'paddingRight', 'paddingTop', 'paddingBottom',  # Use simplified
            'gridStyleId', 'backgroundStyleId', 'fillStyleId', 'strokeStyleId',  # Style IDs
            'textAutoResize',  # Text specific
            'layoutVersion',  # Internal versioning
            'componentPropertyDefinitions',  # Complex component data
            'componentProperties',  # Component variants
            'overrides',  # Component overrides
            'prototypeDevice',  # Device preview settings
            'flowStartingPoints',  # Prototype flows
        }
        
        # Properties to simplify
        self.simplify_properties = {
            'fills': self._simplify_fills,
            'strokes': self._simplify_strokes,
            'constraints': self._simplify_constraints,
            'style': self._simplify_text_style,
            'layoutGrids': self._simplify_grids,
            'blendMode': self._simplify_blend_mode
        }
        
        # Vector node types that often contain complex path data
        self.vector_types = {
            'VECTOR', 'LINE', 'REGULAR_POLYGON', 'ELLIPSE', 
            'STAR', 'BOOLEAN_OPERATION'
        }
        
        # Statistics tracking
        self.stats = {
            'total_nodes': 0,
            'filtered_nodes': 0,
            'removed_properties': 0,
            'simplified_properties': 0,
            'vector_nodes_simplified': 0,
            'original_size': 0,
            'filtered_size': 0
        }
    
    def filter_figma_data(self, node: Dict[str, Any], max_depth: Optional[int] = None) -> Dict[str, Any]:
        """
        Filter Figma node data recursively
        
        Args:
            node: Figma node data
            max_depth: Maximum depth to process (None for unlimited)
            
        Returns:
            Filtered node data optimized for LLM consumption
        """
        if not node:
            return {}
        
        # Validate input type
        if not isinstance(node, dict):
            # Log error and return empty dict
            print(f"Warning: Expected dict for node, got {type(node).__name__}")
            return {}
        
        # Track statistics
        self.stats['total_nodes'] += 1
        
        # Start with empty filtered node
        filtered = {}
        
        # Process each property
        for key, value in node.items():
            # Skip removed properties
            if key in self.remove_properties:
                self.stats['removed_properties'] += 1
                continue
            
            # Handle children recursively
            if key == 'children' and value:
                if max_depth is None or max_depth > 0:
                    next_depth = None if max_depth is None else max_depth - 1
                    filtered_children = []
                    for child in value:
                        # Validate child is a dictionary
                        if not isinstance(child, dict):
                            print(f"Warning: Skipping non-dict child: {type(child).__name__}")
                            continue
                        # Skip invisible nodes
                        if child.get('visible', True):
                            filtered_child = self.filter_figma_data(child, next_depth)
                            if filtered_child:  # Only add non-empty children
                                filtered_children.append(filtered_child)
                    if filtered_children:
                        filtered['children'] = filtered_children
            
            # Simplify certain properties
            elif key in self.simplify_properties:
                simplified = self.simplify_properties[key](value)
                if simplified is not None:
                    filtered[key] = simplified
                    self.stats['simplified_properties'] += 1
            
            # Keep essential properties
            elif key in self.essential_properties:
                filtered[key] = value
            
            # For other properties, apply smart filtering
            else:
                # Skip complex objects unless they're important
                if isinstance(value, dict) and len(str(value)) > 200:
                    continue
                if isinstance(value, list) and len(str(value)) > 500:
                    continue
                # Keep simple values
                if isinstance(value, (str, int, float, bool)) or \
                   (isinstance(value, (dict, list)) and len(str(value)) < 100):
                    filtered[key] = value
        
        # Special handling for vector nodes
        if node.get('type') in self.vector_types:
            self._handle_vector_node(filtered)
            self.stats['vector_nodes_simplified'] += 1
        
        # Add layout hints for better understanding
        self._add_layout_hints(filtered, node)
        
        self.stats['filtered_nodes'] += 1
        return filtered
    
    def _simplify_fills(self, fills: List[Dict[str, Any]]) -> Optional[str]:
        """Simplify fill information to just the primary color"""
        if not fills:
            return None
        
        for fill in fills:
            if fill.get('visible', True) and fill.get('type') == 'SOLID':
                color = fill.get('color', {})
                opacity = fill.get('opacity', 1.0)
                r = int(color.get('r', 0) * 255)
                g = int(color.get('g', 0) * 255) 
                b = int(color.get('b', 0) * 255)
                if opacity < 1:
                    return f"rgba({r},{g},{b},{opacity:.2f})"
                return f"rgb({r},{g},{b})"
        
        # For gradients, just indicate type
        gradient_types = [f.get('type') for f in fills if f.get('type') in ['GRADIENT_LINEAR', 'GRADIENT_RADIAL']]
        if gradient_types:
            return f"gradient:{gradient_types[0]}"
        
        return None
    
    def _simplify_strokes(self, strokes: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Simplify stroke information"""
        if not strokes:
            return None
        
        for stroke in strokes:
            if stroke.get('visible', True):
                color = stroke.get('color', {})
                r = int(color.get('r', 0) * 255)
                g = int(color.get('g', 0) * 255)
                b = int(color.get('b', 0) * 255)
                return {
                    'color': f"rgb({r},{g},{b})",
                    'weight': stroke.get('weight', 1)
                }
        return None
    
    def _simplify_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify constraints to essential information"""
        return {
            'h': constraints.get('horizontal', 'LEFT'),
            'v': constraints.get('vertical', 'TOP')
        }
    
    def _simplify_text_style(self, style: Dict[str, Any]) -> Dict[str, Any]:
        """Simplify text style to essential properties"""
        if not style:
            return {}
        
        simplified = {}
        
        # Keep only essential text properties
        if 'fontSize' in style:
            simplified['size'] = style['fontSize']
        if 'fontFamily' in style:
            simplified['font'] = style['fontFamily']
        if 'fontWeight' in style:
            simplified['weight'] = style['fontWeight']
        if 'textAlignHorizontal' in style:
            simplified['align'] = style['textAlignHorizontal']
        
        return simplified
    
    def _simplify_grids(self, grids: List[Dict[str, Any]]) -> Optional[str]:
        """Simplify grid information"""
        if not grids:
            return None
        
        grid_types = []
        for grid in grids:
            if grid.get('visible', True):
                pattern = grid.get('pattern', 'GRID')
                grid_types.append(pattern)
        
        return ','.join(grid_types) if grid_types else None
    
    def _simplify_blend_mode(self, blend_mode: str) -> Optional[str]:
        """Only keep non-normal blend modes"""
        if blend_mode and blend_mode != 'PASS_THROUGH' and blend_mode != 'NORMAL':
            return blend_mode
        return None
    
    def _handle_vector_node(self, filtered: Dict[str, Any]) -> None:
        """Special handling for vector nodes to remove complex path data"""
        # Remove vector-specific complex properties
        vector_properties = ['vectorPaths', 'vectorNetwork', 'fillGeometry', 'strokeGeometry']
        for prop in vector_properties:
            if prop in filtered:
                del filtered[prop]
        
        # Add simplified indicator
        filtered['_simplified'] = 'vector_paths_removed'
    
    def _add_layout_hints(self, filtered: Dict[str, Any], original: Dict[str, Any]) -> None:
        """Add helpful layout hints for LLM understanding"""
        node_type = original.get('type', '')
        
        # Add semantic hints based on name patterns
        name = str(original.get('name') or '').lower()
        if any(pattern in name for pattern in ['header', 'nav', 'toolbar']):
            filtered['_hint'] = 'navigation'
        elif any(pattern in name for pattern in ['button', 'btn', 'cta']):
            filtered['_hint'] = 'interactive'
        elif any(pattern in name for pattern in ['card', 'tile', 'panel']):
            filtered['_hint'] = 'container'
        elif any(pattern in name for pattern in ['input', 'field', 'form']):
            filtered['_hint'] = 'form_element'
        
        # Add layout pattern hints
        if original.get('layoutMode') == 'HORIZONTAL':
            filtered['_layout_hint'] = 'row'
        elif original.get('layoutMode') == 'VERTICAL':
            filtered['_layout_hint'] = 'column'
        elif node_type == 'FRAME' and original.get('children'):
            # Infer layout from children positions
            children = original['children']
            if len(children) > 2:
                if self._is_grid_layout(children):
                    filtered['_layout_hint'] = 'grid'
    
    def _is_grid_layout(self, children: List[Dict[str, Any]]) -> bool:
        """Check if children are arranged in a grid pattern"""
        if len(children) < 4:
            return False
        
        # Get positions
        positions = []
        for child in children:
            # Ensure child is a dictionary before checking properties
            if isinstance(child, dict) and 'absoluteBoundingBox' in child:
                bounds = child['absoluteBoundingBox']
                positions.append((bounds.get('x', 0), bounds.get('y', 0)))
        
        if len(positions) < 4:
            return False
        
        # Check for regular spacing patterns
        x_positions = sorted(set(x for x, _ in positions))
        y_positions = sorted(set(y for _, y in positions))
        
        # Grid-like if we have multiple rows and columns
        return len(x_positions) >= 2 and len(y_positions) >= 2
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        if self.stats['original_size'] > 0:
            reduction = (1 - self.stats['filtered_size'] / self.stats['original_size']) * 100
        else:
            reduction = 0
        
        return {
            **self.stats,
            'reduction_percentage': round(reduction, 2)
        }
    
    def estimate_token_reduction(self, original_json: str, filtered_json: str) -> Dict[str, int]:
        """Estimate token reduction for LLM processing"""
        # Rough estimation: 1 token ≈ 4 characters
        original_tokens = len(original_json) // 4
        filtered_tokens = len(filtered_json) // 4
        
        return {
            'original_tokens': original_tokens,
            'filtered_tokens': filtered_tokens,
            'tokens_saved': original_tokens - filtered_tokens,
            'reduction_percentage': round((1 - filtered_tokens / original_tokens) * 100, 2)
        } 