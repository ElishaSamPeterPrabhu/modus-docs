"""
Modus Component Mapper
Maps reconstructed layout nodes to appropriate Modus components
Uses naming conventions, structural analysis, and style heuristics
"""

from typing import Dict, List, Any, Optional, Tuple
import re
from dataclasses import dataclass, field
from layout_reconstruction import LayoutNode


@dataclass
class ModusComponent:
    """Represents a mapped Modus component"""
    component_type: str  # e.g., 'modus-wc-button'
    original_node_id: str
    original_node_name: str
    properties: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    detection_method: str = 'unknown'  # 'naming', 'structure', 'style'
    layout_css: Dict[str, Any] = field(default_factory=dict)
    children: List['ModusComponent'] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'component_type': self.component_type,
            'original_node_id': self.original_node_id,
            'original_node_name': self.original_node_name,
            'properties': self.properties,
            'confidence': self.confidence,
            'detection_method': self.detection_method,
            'layout_css': self.layout_css,
            'children': [child.to_dict() for child in self.children]
        }


class ModusComponentMapper:
    """Maps layout nodes to Modus components"""
    
    def __init__(self):
        # Component name mappings (order matters - more specific patterns first)
        self.NAME_MAPPINGS = {
            # Buttons
            r'\b(button|btn|cta)\b': 'modus-wc-button',
            
            # Form inputs
            r'\b(input|text\s?field|textfield)\b': 'modus-wc-text-input',
            r'\b(text\s?area|textarea)\b': 'modus-wc-textarea',
            r'\b(number|numeric)\s?(input|field)?\b': 'modus-wc-number-input',
            r'\b(select|dropdown)\b': 'modus-wc-select',
            r'\b(checkbox|check)\b': 'modus-wc-checkbox',
            r'\b(radio|radio\s?button)\b': 'modus-wc-radio',
            r'\b(switch|toggle)\b': 'modus-wc-switch',
            r'\b(slider|range)\b': 'modus-wc-slider',
            r'\b(date|calendar|date\s?picker)\b': 'modus-wc-date',
            r'\b(time|time\s?picker)\b': 'modus-wc-time-input',
            r'\b(search|autocomplete|typeahead)\b': 'modus-wc-autocomplete',
            
            # Navigation (check sidebar patterns first - they're more specific)
            r'\b(side\s*navigation|side-navigation|sidebar|side\s*nav|sidenav|aside)\b': 'modus-wc-side-navigation',
            r'\b(navbar|nav\s*bar|header|top\s*bar|navigation\s*bar)\b': 'modus-wc-navbar',
            r'\b(breadcrumb|breadcrumbs)\b': 'modus-wc-breadcrumbs',
            r'\b(tab|tabs)\b': 'modus-wc-tabs',
            r'\b(pagination|pager)\b': 'modus-wc-pagination',
            
            # Display components
            r'\b(card|tile|panel)\b': 'modus-wc-card',
            r'\b(table|grid)\b': 'modus-wc-table',
            r'\b(alert|notification|message)\b': 'modus-wc-alert',
            r'\b(modal|dialog|popup)\b': 'modus-wc-modal',
            r'\b(tooltip|hint|popover)\b': 'modus-wc-tooltip',
            r'\b(badge)\b': 'modus-wc-badge',
            r'\b(chip|tag|pill)\b': 'modus-wc-chip',
            r'\b(progress|progress\s?bar)\b': 'modus-wc-progress',
            r'\b(loader|spinner|loading)\b': 'modus-wc-loader',
            r'\b(skeleton)\b': 'modus-wc-skeleton',
            
            # Other
            r'\b(avatar|profile\s?pic)\b': 'modus-wc-avatar',
            r'\b(icon)\b': 'modus-wc-icon',
            r'\b(divider|separator)\b': 'modus-wc-divider',
        }
        
        # Structural patterns for component detection
        self.STRUCTURAL_PATTERNS = {
            'modus-wc-button': self._is_button_structure,
            'modus-wc-text-input': self._is_input_structure,
            'modus-wc-card': self._is_card_structure,
            'modus-wc-navbar': self._is_navbar_structure,
            'modus-wc-table': self._is_table_structure,
            'modus-wc-chip': self._is_chip_structure,
            'modus-wc-avatar': self._is_avatar_structure,
        }
        
        self.stats = {
            'total_components': 0,
            'detected_by_name': 0,
            'detected_by_structure': 0,
            'detected_by_style': 0,
            'undetected': 0
        }
        
        # Track undetected nodes for developer feedback
        self.undetected_nodes = []
    
    def map_layout_to_components(self, layout_node: LayoutNode) -> List[ModusComponent]:
        """
        Map a layout tree to Modus components
        
        Args:
            layout_node: Root of the reconstructed layout tree
            
        Returns:
            List of mapped Modus components
        """
        components = []
        self._map_node_recursive(layout_node, components)
        return components
    
    def _map_node_recursive(self, node: LayoutNode, components: List[ModusComponent], 
                          parent_component: Optional[ModusComponent] = None) -> None:
        """Recursively map layout nodes to Modus components"""
        # Validate node
        if not node:
            print(f"Warning: _map_node_recursive received None node")
            return
            
        # Check if node has required attributes
        if not hasattr(node, 'children'):
            print(f"Warning: node missing children attribute - type: {type(node)}, id: {getattr(node, 'id', 'unknown')}")
            return
        
        # Try to identify component
        component = self._identify_component(node)
        
        if component:
            # Add to parent or root list
            if parent_component:
                parent_component.children.append(component)
            else:
                components.append(component)
            
            # Process children with this component as parent
            for child in node.children:
                self._map_node_recursive(child, components, component)
        else:
            # No component identified, process children with same parent
            self.stats['undetected'] += 1
            
            # Track undetected node info for developer feedback (limit to prevent memory issues)
            if len(self.undetected_nodes) < 1000:  # Limit to first 1000 undetected nodes
                self.undetected_nodes.append({
                    'id': node.id,
                    'name': node.name,
                    'type': node.type,
                    'layout_type': node.layout_type,
                    'children_count': len(node.children),
                    'has_text': hasattr(node, 'text') and bool(node.text),
                    'possible_reasons': self._analyze_unmatch_reasons(node)
                })
            
            for child in node.children:
                self._map_node_recursive(child, components, parent_component)
    
    def _identify_component(self, node: LayoutNode) -> Optional[ModusComponent]:
        """Identify if a node represents a Modus component"""
        # Validate node
        if not node:
            print("Warning: _identify_component received None node")
            return None
            
        # Increment stats
        self.stats['total_components'] += 1
        
        # 1. Try naming convention first (highest confidence)
        component_type = self._detect_by_name(node.name)
        if component_type:
            self.stats['detected_by_name'] += 1
            return ModusComponent(
                component_type=component_type,
                original_node_id=node.id,
                original_node_name=node.name,
                confidence=0.95,
                detection_method='naming',
                properties=self._extract_properties(node, component_type)
            )
        
        # 2. Try structural analysis
        component_type = self._detect_by_structure(node)
        if component_type:
            self.stats['detected_by_structure'] += 1
            return ModusComponent(
                component_type=component_type,
                original_node_id=node.id,
                original_node_name=node.name,
                confidence=0.8,
                detection_method='structure',
                properties=self._extract_properties(node, component_type)
            )
        
        # 3. Try style analysis (for simple components)
        component_type = self._detect_by_style(node)
        if component_type:
            self.stats['detected_by_style'] += 1
            return ModusComponent(
                component_type=component_type,
                original_node_id=node.id,
                original_node_name=node.name,
                confidence=0.7,
                detection_method='style',
                properties=self._extract_properties(node, component_type)
            )
        
        return None
    
    def _detect_by_name(self, name: str) -> Optional[str]:
        """Detect component type by name matching"""
        if not name:
            return None
            
        name_lower = name.lower()
        
        # Check for exact Modus component names
        if 'modus-' in name_lower:
            # Extract modus component name
            match = re.search(r'modus-wc-[\w-]+', name_lower)
            if match:
                return match.group(0)
        
        # Check against name patterns
        for pattern, component_type in self.NAME_MAPPINGS.items():
            if re.search(pattern, name_lower, re.IGNORECASE):
                return component_type
        
        return None
    
    def _detect_by_structure(self, node: LayoutNode) -> Optional[str]:
        """Detect component type by structural analysis"""
        
        # NEW: Check for INSTANCE nodes with componentId
        if node.type == 'INSTANCE' and node.original_node:
            component_id = node.original_node.get('componentId')
            if component_id:
                # Try to infer from instance name or component properties
                name = node.name.lower() if node.name else ''
                
                # Check against our name mappings
                for pattern, component_type in self.NAME_MAPPINGS.items():
                    if re.search(pattern, name, re.IGNORECASE):
                        return component_type
                
                # Check variant properties for clues
                variant_props = node.original_node.get('variantProperties', {})
                if variant_props:
                    # Check for common variant property names
                    if 'type' in variant_props:
                        variant_type = variant_props['type'].lower()
                        if 'button' in variant_type:
                            return 'modus-wc-button'
                        elif 'input' in variant_type:
                            return 'modus-wc-text-input'
                        elif 'nav' in variant_type:
                            return 'modus-wc-navbar'
        
        # Continue with existing structural patterns
        for component_type, detector_func in self.STRUCTURAL_PATTERNS.items():
            if detector_func(node):
                return component_type
        return None
    
    def _detect_by_style(self, node: LayoutNode) -> Optional[str]:
        """Detect component type by style analysis"""
        original = node.original_node
        
        # Check for icon-like elements (small square/rectangular shapes)
        bounds = original.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        
        if (node.type in ['RECTANGLE', 'FRAME'] and 
            width == height and
            10 <= width <= 50):
            return 'modus-wc-icon'
        
        # Check for divider (thin horizontal or vertical lines)
        if node.type == 'RECTANGLE':
            if (width > 100 and height <= 2) or (height > 100 and width <= 2):
                return 'modus-wc-divider'
        
        return None
    
    # Structural detection functions
    def _is_button_structure(self, node: LayoutNode) -> bool:
        """Check if node has button-like structure"""
        # Button typically has:
        # - Frame/Rectangle with text child
        # - Reasonable size
        # - Often has background fill and/or border radius
        
        if node.type not in ['FRAME', 'RECTANGLE', 'COMPONENT', 'INSTANCE']:
            return False
        
        # Check size constraints
        bounds = node.original_node.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if width < 50 or height < 24:
            return False
        
        # Check for text child
        has_text_child = any(
            child.type == 'TEXT' 
            for child in node.children
        )
        
        # Check original node for button-like properties
        original = node.original_node
        has_fills = bool(original.get('fills'))
        has_corner_radius = original.get('cornerRadius', 0) > 0
        has_effects = bool(original.get('effects'))
        
        return has_text_child and (has_fills or has_corner_radius or has_effects)
    
    def _is_input_structure(self, node: LayoutNode) -> bool:
        """Check if node has input-like structure"""
        if node.type not in ['FRAME', 'RECTANGLE']:
            return False
        
        bounds = node.original_node.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if width < 100 or height < 30:
            return False
        
        # Input typically has border/stroke
        original = node.original_node
        has_strokes = bool(original.get('strokes'))
        
        # May have placeholder text
        has_text = any(child.type == 'TEXT' for child in node.children)
        
        return has_strokes or (width > height * 3 and has_text)
    
    def _is_card_structure(self, node: LayoutNode) -> bool:
        """Check if node has card-like structure"""
        if node.type not in ['FRAME', 'COMPONENT', 'INSTANCE']:
            return False
        
        # Cards are usually larger containers
        bounds = node.original_node.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if width < 150 or height < 100:
            return False
        
        # Cards often have:
        # - White/light background
        # - Shadow effect
        # - Multiple children (image, title, text, buttons)
        original = node.original_node
        has_background = bool(original.get('fills'))
        has_shadow = any(
            effect.get('type') == 'DROP_SHADOW' 
            for effect in original.get('effects', [])
        )
        has_multiple_children = len(node.children) >= 2
        
        return (has_background or has_shadow) and has_multiple_children
    
    def _is_navbar_structure(self, node: LayoutNode) -> bool:
        """Check if node has navbar-like structure"""
        if node.layout_type != 'HORIZONTAL':
            return False
        
        # Navbar is typically at the top
        bounds = node.original_node.get('absoluteBoundingBox', {})
        if bounds.get('y', 999) > 100:
            return False
        
        # Wide and thin
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        if height > width * 0.2:
            return False
        
        # Has multiple children (nav items)
        return len(node.children) >= 2
    
    def _is_table_structure(self, node: LayoutNode) -> bool:
        """Check if node has table-like structure"""
        # Tables can be detected as GRID layout
        if node.layout_type == 'GRID':
            metadata = node.metadata
            return metadata.get('rows', 0) >= 2 and metadata.get('columns', 0) >= 2
        
        # Or as vertical layout with multiple similar rows
        if node.layout_type == 'VERTICAL' and len(node.children) >= 3:
            # Check if children have similar structure
            first_child = node.children[0]
            if first_child.layout_type == 'HORIZONTAL':
                return all(
                    child.layout_type == 'HORIZONTAL' and 
                    len(child.children) == len(first_child.children)
                    for child in node.children[1:]
                )
        
        return False
    
    def _is_chip_structure(self, node: LayoutNode) -> bool:
        """Check if node has chip-like structure"""
        if node.type not in ['FRAME', 'COMPONENT', 'INSTANCE']:
            return False
        
        bounds = node.original_node.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        # Chips are small, pill-shaped elements
        if width < 40 or height < 20 or height > 40:
            return False
        
        # Has rounded corners
        original = node.original_node
        has_corner_radius = original.get('cornerRadius', 0) >= height / 3
        
        # Has text content
        has_text = any(child.type == 'TEXT' for child in node.children)
        
        return has_corner_radius and has_text
    
    def _is_avatar_structure(self, node: LayoutNode) -> bool:
        """Check if node has avatar-like structure"""
        if node.type not in ['ELLIPSE', 'FRAME', 'RECTANGLE']:
            return False
        
        bounds = node.original_node.get('absoluteBoundingBox', {})
        width = bounds.get('width', 0)
        height = bounds.get('height', 0)
        # Avatars are typically square or circular
        if abs(width - height) > 5:
            return False
        
        # Size constraints
        if width < 24 or width > 150:
            return False
        
        # For frames/rectangles, check if circular
        if node.type in ['FRAME', 'RECTANGLE']:
            original = node.original_node
            corner_radius = original.get('cornerRadius', 0)
            is_circular = corner_radius >= width / 2
            
            # May contain image or text (initials)
            has_content = bool(node.children)
            
            return is_circular and has_content
        
        return True  # ELLIPSE type is likely an avatar
    
    def _extract_properties(self, node: LayoutNode, component_type: str) -> Dict[str, Any]:
        """Extract component-specific properties"""
        props = {}
        original = node.original_node
        
        # NEW: Extract variant properties if available (from INSTANCE nodes)
        if original.get('type') == 'INSTANCE' and original.get('variantProperties'):
            variant_props = original['variantProperties']
            
            # Map common variant properties
            if 'state' in variant_props:
                state = variant_props['state'].lower()
                if state in ['disabled', 'hover', 'active', 'focused']:
                    props['state'] = state
                    if state == 'disabled':
                        props['disabled'] = True
            
            if 'size' in variant_props:
                props['size'] = variant_props['size'].lower()
            
            if 'variant' in variant_props:
                props['variant'] = variant_props['variant'].lower()
            
            if 'type' in variant_props:
                props['type'] = variant_props['type'].lower()
        
        # NEW: Extract component property overrides
        if original.get('componentPropertyReferences'):
            # These are bound properties from the component
            prop_refs = original['componentPropertyReferences']
            if 'visible' in prop_refs:
                props['visible'] = prop_refs['visible']
            if 'characters' in prop_refs:
                props['text'] = prop_refs['characters']
        
        # Common properties
        if component_type == 'modus-wc-button':
            # If we didn't get variant from properties, try to infer
            if 'variant' not in props:
                # Extract button variant based on style
                fills = original.get('fills', [])
                # Ensure fills is a list and contains dicts
                if isinstance(fills, list) and fills and isinstance(fills[0], dict) and fills[0].get('type') == 'SOLID':
                    color = fills[0].get('color', {})
                    # Simple heuristic for button types
                    if self._is_primary_color(color):
                        props['variant'] = 'primary'
                    elif self._is_secondary_color(color):
                        props['variant'] = 'secondary'
                    else:
                        props['variant'] = 'tertiary'
            
            # Extract size if not from variants
            if 'size' not in props:
                bounds = original.get('absoluteBoundingBox', {})
                height = bounds.get('height', 0)
                if height <= 32:
                    props['size'] = 'small'
                elif height >= 48:
                    props['size'] = 'large'
                else:
                    props['size'] = 'medium'
        
        elif component_type == 'modus-wc-text-input':
            # Check for disabled state
            if 'disabled' not in props:
                opacity = original.get('opacity', 1.0)
                if opacity < 0.6:
                    props['disabled'] = True
            
            # Check for error state (red border)
            strokes = original.get('strokes', [])
            # Ensure strokes is a list/array before accessing elements
            if isinstance(strokes, list) and strokes and isinstance(strokes[0], dict) and self._is_error_color(strokes[0].get('color', {})):
                props['invalid'] = True
            
            # NEW: Check for placeholder text
            if node.children:
                for child in node.children:
                    if child.type == 'TEXT' and child.original_node:
                        text = child.original_node.get('characters', '')
                        if text and ('placeholder' in child.name.lower() or opacity < 0.6):
                            props['placeholder'] = text
                            break
        
        elif component_type == 'modus-wc-chip':
            # Extract chip properties
            if 'size' not in props:
                bounds = original.get('absoluteBoundingBox', {})
                height = bounds.get('height', 0)
                props['size'] = 'small' if height <= 24 else 'medium'
            
        elif component_type == 'modus-wc-navbar':
            # Extract navbar properties
            props['position'] = 'fixed' if node.metadata.get('pattern') == 'navigation' else 'static'
        
        elif component_type == 'modus-wc-side-navigation':
            # NEW: Check if collapsed based on width
            bounds = original.get('absoluteBoundingBox', {})
            if bounds and bounds.get('width', 240) < 100:
                props['collapsed'] = True
        
        # NEW: Extract common layout properties
        if original.get('layoutAlign'):
            layout_align = original['layoutAlign']
            if layout_align == 'STRETCH':
                props['fullWidth'] = True
        
        return props
    
    def _extract_layout_css(self, node: LayoutNode) -> Dict[str, Any]:
        """Extract CSS layout properties for positioning"""
        css = {}
        
        # Extract bounds from original node's absoluteBoundingBox
        absolute_box = node.original_node.get('absoluteBoundingBox', {})
        if absolute_box:
            css['position'] = 'absolute'
            css['left'] = f"{absolute_box.get('x', 0)}px"
            css['top'] = f"{absolute_box.get('y', 0)}px"
            css['width'] = f"{absolute_box.get('width', 0)}px"
            css['height'] = f"{absolute_box.get('height', 0)}px"
        
        # Flexbox properties if applicable
        if node.layout_type in ['HORIZONTAL', 'VERTICAL']:
            css['display'] = 'flex'
            css['flexDirection'] = 'row' if node.layout_type == 'HORIZONTAL' else 'column'
            
            # Gap from metadata
            if 'item_spacing' in node.metadata:
                css['gap'] = f"{node.metadata['item_spacing']}px"
        
        elif node.layout_type == 'GRID':
            css['display'] = 'grid'
            metadata = node.metadata
            if 'columns' in metadata:
                css['gridTemplateColumns'] = f"repeat({metadata['columns']}, 1fr)"
            if 'rows' in metadata:
                css['gridTemplateRows'] = f"repeat({metadata['rows']}, 1fr)"
        
        # Extract additional CSS from original node
        original = node.original_node
        
        # Padding
        padding_left = original.get('paddingLeft', 0)
        padding_right = original.get('paddingRight', 0)
        padding_top = original.get('paddingTop', 0)
        padding_bottom = original.get('paddingBottom', 0)
        
        if any([padding_left, padding_right, padding_top, padding_bottom]):
            css['padding'] = f"{padding_top}px {padding_right}px {padding_bottom}px {padding_left}px"
        
        # Alignment
        if 'primaryAxisAlignItems' in original:
            align_map = {
                'MIN': 'flex-start',
                'CENTER': 'center',
                'MAX': 'flex-end',
                'SPACE_BETWEEN': 'space-between'
            }
            css['justifyContent'] = align_map.get(original['primaryAxisAlignItems'], 'flex-start')
        
        if 'counterAxisAlignItems' in original:
            align_map = {
                'MIN': 'flex-start',
                'CENTER': 'center',
                'MAX': 'flex-end'
            }
            css['alignItems'] = align_map.get(original['counterAxisAlignItems'], 'flex-start')
        
        return css
    
    def _is_primary_color(self, color: Dict[str, float]) -> bool:
        """Check if color is likely a primary color (blue-ish)"""
        r, g, b = color.get('r', 0), color.get('g', 0), color.get('b', 0)
        return b > 0.5 and b > r and b > g
    
    def _is_secondary_color(self, color: Dict[str, float]) -> bool:
        """Check if color is likely a secondary color (gray-ish)"""
        r, g, b = color.get('r', 0), color.get('g', 0), color.get('b', 0)
        return abs(r - g) < 0.1 and abs(g - b) < 0.1 and 0.3 < r < 0.8
    
    def _is_error_color(self, color: Dict[str, float]) -> bool:
        """Check if color is likely an error color (red-ish)"""
        r, g, b = color.get('r', 0), color.get('g', 0), color.get('b', 0)
        return r > 0.5 and r > g * 1.5 and r > b * 1.5
    
    def _analyze_unmatch_reasons(self, node: LayoutNode) -> List[str]:
        """Analyze why a node couldn't be matched to a Modus component"""
        reasons = []
        
        # Check node name
        if not node.name or node.name.lower() in ['frame', 'group', 'rectangle', 'vector']:
            reasons.append("Generic Figma element name (Frame/Group/Rectangle)")
        
        # Check if it's likely a layout container
        if node.children and len(node.children) > 2:
            if node.layout_type in ['HORIZONTAL', 'VERTICAL', 'GRID']:
                reasons.append(f"Appears to be a layout container ({node.layout_type})")
        
        # Check if it's a text-only node
        if node.type == 'TEXT' and not node.children:
            reasons.append("Standalone text element (not part of a component)")
        
        # Check if it's a decorative element
        if node.type in ['VECTOR', 'ELLIPSE', 'POLYGON', 'STAR', 'LINE']:
            reasons.append("Decorative/graphic element")
        
        # Check if it's an image
        if node.type == 'RECTANGLE' and hasattr(node, 'fills'):
            reasons.append("Possible image or background element")
        
        # If no specific reason found
        if not reasons:
            reasons.append("No clear component pattern detected")
        
        return reasons
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get mapping statistics"""
        total = self.stats['total_components']
        detected = (self.stats['detected_by_name'] + 
                   self.stats['detected_by_structure'] + 
                   self.stats['detected_by_style'])
        
        return {
            **self.stats,
            'detection_rate': detected / total * 100 if total > 0 else 0,
            'name_detection_rate': self.stats['detected_by_name'] / total * 100 if total > 0 else 0,
            'structure_detection_rate': self.stats['detected_by_structure'] / total * 100 if total > 0 else 0,
            'style_detection_rate': self.stats['detected_by_style'] / total * 100 if total > 0 else 0,
            'undetected_nodes': self.undetected_nodes
        } 