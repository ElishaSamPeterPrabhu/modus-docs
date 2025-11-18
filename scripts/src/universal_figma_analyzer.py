"""
Universal Figma Analyzer
Analyzes any type of Figma page and identifies all Modus components and layout patterns
"""

import json
from typing import Dict, Any, List, Optional, Tuple
import re
from layout_reconstruction import LayoutReconstructor, LayoutNode, create_llm_summary, create_compact_llm_summary
from modus_component_mapper import ModusComponentMapper, ModusComponent
from figma_data_filter import FigmaDataFilter
import os

class UniversalFigmaAnalyzer:
    """Analyzes any Figma design and maps to appropriate Modus components"""
    
    def __init__(self):
        # Complete Modus component mapping based on modus-wc-2.0 source code
        self.modus_components = {
            # Form Elements
            'button': 'modus-wc-button',
            'input': 'modus-wc-text-input',
            'text-input': 'modus-wc-text-input',
            'textfield': 'modus-wc-text-input',
            'textarea': 'modus-wc-textarea',
            'text-area': 'modus-wc-textarea',
            'number-input': 'modus-wc-number-input',
            'numeric': 'modus-wc-number-input',
            'select': 'modus-wc-select',
            'dropdown': 'modus-wc-select',
            'checkbox': 'modus-wc-checkbox',
            'check': 'modus-wc-checkbox',
            'radio': 'modus-wc-radio',
            'radio-button': 'modus-wc-radio',
            'switch': 'modus-wc-switch',
            'toggle': 'modus-wc-switch',
            'slider': 'modus-wc-slider',
            'range': 'modus-wc-slider',
            'date': 'modus-wc-date',
            'date-picker': 'modus-wc-date',
            'calendar': 'modus-wc-date',
            'time': 'modus-wc-time-input',
            'time-input': 'modus-wc-time-input',
            'time-picker': 'modus-wc-time-input',
            'autocomplete': 'modus-wc-autocomplete',
            'typeahead': 'modus-wc-autocomplete',
            'search': 'modus-wc-autocomplete',
            'label': 'modus-wc-input-label',
            'input-label': 'modus-wc-input-label',
            'feedback': 'modus-wc-input-feedback',
            'input-feedback': 'modus-wc-input-feedback',
            'error': 'modus-wc-input-feedback',
            'help': 'modus-wc-input-feedback',
            'validation': 'modus-wc-input-feedback',
            
            # Navigation
            'navbar': 'modus-wc-navbar',
            'navigation': 'modus-wc-navbar',
            'nav': 'modus-wc-navbar',
            'header': 'modus-wc-navbar',
            'topbar': 'modus-wc-navbar',
            'sidebar': 'modus-wc-side-navigation',
            'sidenav': 'modus-wc-side-navigation',
            'side-navigation': 'modus-wc-side-navigation',
            'side navigation': 'modus-wc-side-navigation',
            'breadcrumb': 'modus-wc-breadcrumbs',
            'breadcrumbs': 'modus-wc-breadcrumbs',
            'tabs': 'modus-wc-tabs',
            'tab': 'modus-wc-tabs',
            'tabbed': 'modus-wc-tabs',
            'pagination': 'modus-wc-pagination',
            'pager': 'modus-wc-pagination',
            'page-numbers': 'modus-wc-pagination',
            'menu': 'modus-wc-menu',
            'menu-item': 'modus-wc-menu-item',
            'dropdown-menu': 'modus-wc-dropdown-menu',
            'dropdown menu': 'modus-wc-dropdown-menu',
            'context-menu': 'modus-wc-dropdown-menu',
            
            # Display & Feedback
            'alert': 'modus-wc-alert',
            'notification': 'modus-wc-alert',
            'message': 'modus-wc-alert',
            'warning': 'modus-wc-alert',
            'toast': 'modus-wc-toast',
            'snackbar': 'modus-wc-toast',
            'modal': 'modus-wc-modal',
            'dialog': 'modus-wc-modal',
            'popup': 'modus-wc-modal',
            'overlay': 'modus-wc-modal',
            'tooltip': 'modus-wc-tooltip',
            'hint': 'modus-wc-tooltip',
            'popover': 'modus-wc-tooltip',
            'badge': 'modus-wc-badge',
            'tag': 'modus-wc-chip',
            'chip': 'modus-wc-chip',
            'pill': 'modus-wc-chip',
            'progress': 'modus-wc-progress',
            'progress-bar': 'modus-wc-progress',
            'loading-bar': 'modus-wc-progress',
            'loader': 'modus-wc-loader',
            'spinner': 'modus-wc-loader',
            'loading': 'modus-wc-loader',
            'skeleton': 'modus-wc-skeleton',
            'skeleton-loader': 'modus-wc-skeleton',
            'placeholder': 'modus-wc-skeleton',
            
            # Content
            'card': 'modus-wc-card',
            'tile': 'modus-wc-card',
            'panel': 'modus-wc-card',
            'accordion': 'modus-wc-accordion',
            'collapsible': 'modus-wc-accordion',
            'expandable': 'modus-wc-accordion',
            'collapse': 'modus-wc-collapse',
            'expand': 'modus-wc-collapse',
            'table': 'modus-wc-table',
            'data-table': 'modus-wc-table',
            'grid': 'modus-wc-table',
            'data-grid': 'modus-wc-table',
            'divider': 'modus-wc-divider',
            'separator': 'modus-wc-divider',
            'line': 'modus-wc-divider',
            'hr': 'modus-wc-divider',
            'avatar': 'modus-wc-avatar',
            'profile': 'modus-wc-avatar',
            'user-image': 'modus-wc-avatar',
            'icon': 'modus-wc-icon',
            'glyph': 'modus-wc-icon',
            'typography': 'modus-wc-typography',
            'text': 'modus-wc-typography',
            'heading': 'modus-wc-typography',
            'title': 'modus-wc-typography',
            
            # Interactive
            'rating': 'modus-wc-rating',
            'stars': 'modus-wc-rating',
            'rate': 'modus-wc-rating',
            'stepper': 'modus-wc-stepper',
            'steps': 'modus-wc-stepper',
            'wizard': 'modus-wc-stepper',
            'progress-steps': 'modus-wc-stepper',
            'toolbar': 'modus-wc-toolbar',
            'tool-bar': 'modus-wc-toolbar',
            'action-bar': 'modus-wc-toolbar',
            'theme-switcher': 'modus-wc-theme-switcher',
            'theme-toggle': 'modus-wc-theme-switcher',
            'dark-mode': 'modus-wc-theme-switcher'
        }
        
        # Component detection confidence levels
        self.CONFIDENCE_LEVELS = {
            'exact_name': 0.95,
            'pattern_match': 0.85,
            'structure_match': 0.75,
            'visual_match': 0.65,
            'default': 0.5
        }
        
        # Initialize enhanced layout reconstructor and component mapper
        self.layout_reconstructor = LayoutReconstructor()
        self.component_mapper = ModusComponentMapper()
        
    def analyze_with_layout_reconstruction(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced analysis using layout reconstruction and improved component mapping
        
        Args:
            node: Root Figma node from API
            
        Returns:
            Analysis result with reconstructed layout and mapped components
        """
        # Step 0: Filter the raw Figma data to remove unnecessary properties
        filter = FigmaDataFilter()
        filtered_node = filter.filter_figma_data(node)
        filter_stats = filter.get_statistics()
        
        # Validate filtered_node is a dictionary
        if not isinstance(filtered_node, dict):
            return {
                'error': f'Filtered node is not a dictionary: {type(filtered_node).__name__}',
                'components': [],
                'layout_tree': None
            }
        
        # Step 1: Reconstruct the layout from filtered data
        layout_tree = self.layout_reconstructor.reconstruct_layout(filtered_node)
        
        if not layout_tree:
            return {
                'error': 'Failed to reconstruct layout',
                'components': [],
                'layout_tree': None
            }
        
        # Step 2: Map layout to Modus components
        modus_components = self.component_mapper.map_layout_to_components(layout_tree)
        
        # Step 3: Create component map for fast lookups
        component_map = {comp.original_node_id: comp.to_dict() for comp in modus_components}
        
        # Step 4: Generate LLM-ready summary
        llm_summary = create_llm_summary(layout_tree, component_map)
        
        # Step 4b: Generate ultra-compact summary
        compact_summary = create_compact_llm_summary(layout_tree, component_map)
        
        # Step 5: Analyze page patterns
        page_pattern = self._detect_page_pattern_from_layout(layout_tree)
        
        # Step 6: Generate implementation guide
        implementation_guide = self._generate_implementation_from_layout(
            layout_tree,
            modus_components,
            page_pattern
        )
        
        # Step 7: Get statistics
        layout_stats = self.layout_reconstructor.get_statistics()
        mapping_stats = self.component_mapper.get_statistics()
        
        return {
            'llm_summary': llm_summary,  # The concise version for LLM
            'compact_summary': compact_summary,  # Ultra-compact version
            'components': [comp.to_dict() for comp in modus_components],
            'page_pattern': page_pattern,
            'implementation_guide': implementation_guide,
            'statistics': {
                'layout': layout_stats,
                'mapping': mapping_stats,
                'filtering': filter_stats  # Add filtering statistics
            },
            # Optional: Include full tree for debugging (but not for LLM)
            '_debug_full_tree': layout_tree.to_dict() if os.getenv('INCLUDE_DEBUG_TREE') else None
        }
    
    def analyze_for_llm(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze Figma design and return a clean, focused output optimized for LLM consumption.
        Provides essential layout and component information without overwhelming detail.
        
        Args:
            node: Root Figma node from API
            
        Returns:
            Balanced analysis with layout structure, components, and implementation guidance
        """
        # Step 1: Filter and reconstruct layout
        filter = FigmaDataFilter()
        filtered_node = filter.filter_figma_data(node)
        
        if not isinstance(filtered_node, dict):
            return {
                'error': f'Invalid node type: {type(filtered_node).__name__}',
                'suggestion': 'Please provide a valid Figma node object'
            }
        
        layout_tree = self.layout_reconstructor.reconstruct_layout(filtered_node)
        if not layout_tree:
            return {
                'error': 'Failed to analyze layout',
                'suggestion': 'Check if the Figma data is valid'
            }
        
        # Step 2: Map to Modus components
        modus_components = self.component_mapper.map_layout_to_components(layout_tree)
        
        # Step 3: Build hierarchical layout structure with components
        # Use concise structure to prevent context overflow when combined with undetected components
        layout_structure = self._build_concise_layout_structure(layout_tree, modus_components)
        
        # Step 4: Create component summary
        components_summary = self._create_component_summary(modus_components)
        
        # Step 5: Detect page patterns and layout type
        page_analysis = self._analyze_page_for_llm(layout_tree, modus_components)
        
        # Step 6: Generate implementation guide
        implementation = self._generate_implementation_guide_for_llm(
            layout_tree, 
            modus_components, 
            page_analysis
        )
        
        # Step 7: Get mapping statistics including undetected components
        mapping_stats = self.component_mapper.get_statistics()
        undetected_info = self._format_undetected_components(mapping_stats.get('undetected_nodes', []))
        
        # Step 8: Create focused output with all essential information
        return {
            'page_info': {
                'name': node.get('name', 'Untitled'),
                'layout_type': page_analysis['layout_type'],
                'has_navigation': page_analysis['has_navigation'],
                'has_sidebar': page_analysis['has_sidebar'],
                'component_count': len(modus_components),
                'undetected_count': mapping_stats.get('undetected', 0)
            },
            'layout_structure': layout_structure,
            'components': components_summary,
            'undetected_components': undetected_info,
            'implementation': implementation,
            'modus_imports': self._get_required_imports_from_components(modus_components),
            'mapping_summary': {
                'total_nodes_analyzed': mapping_stats.get('total_components', 0),
                'successfully_mapped': len(modus_components),
                'undetected': mapping_stats.get('undetected', 0),
                'detection_rate': f"{mapping_stats.get('detection_rate', 0):.1f}%"
            }
        }
    
    def _detect_page_pattern_from_layout(self, layout_tree: LayoutNode) -> Dict[str, Any]:
        """Detect page-level patterns from the reconstructed layout"""
        patterns = []
        
        # Check for common page layouts
        if layout_tree.layout_type == 'VERTICAL':
            children_patterns = [
                child.metadata.get('pattern', '')
                for child in layout_tree.children
            ]
            
            # Header-Content-Footer pattern
            if ('navigation' in children_patterns[:2] and 
                len(layout_tree.children) >= 2):
                patterns.append('header-content-footer')
            
            # Sidebar layout
            if layout_tree.children and layout_tree.children[0].layout_type == 'HORIZONTAL':
                first_row = layout_tree.children[0]
                if any(child.metadata.get('pattern') == 'sidebar' for child in first_row.children):
                    patterns.append('sidebar-layout')
        
        # Grid layout
        if layout_tree.layout_type == 'GRID' or any(
            child.layout_type == 'GRID' for child in layout_tree.children
        ):
            patterns.append('grid-layout')
        
        # Dashboard pattern (multiple cards/metrics)
        card_count = sum(
            1 for child in self._get_all_nodes(layout_tree)
            if child.metadata.get('pattern') == 'card_grid'
        )
        if card_count >= 3:
            patterns.append('dashboard')
        
        return {
            'patterns': patterns,
            'primary_pattern': patterns[0] if patterns else 'custom',
            'layout_type': layout_tree.layout_type
        }
    
    def _detect_simple_page_pattern(self, layout_tree: LayoutNode) -> str:
        """Detect the primary page pattern in simple terms"""
        all_nodes = self._get_all_nodes(layout_tree)
        
        # Check for common patterns by node names
        has_navbar = any(
            any(keyword in node.type.lower() or node.name.lower() for keyword in ['nav', 'header', 'navbar', 'navigation', 'topbar'])
            for node in all_nodes
        )
        
        has_sidebar = any(
            any(keyword in node.type.lower() or node.name.lower() for keyword in ['sidebar', 'sidenav', 'side nav', 'aside', 'menu'])
            for node in all_nodes
        )
        
        # NEW: Better grid detection using layout_type
        has_grid = any(
            node.layout_type == 'GRID' or 
            (node.metadata and node.metadata.get('layout_grids'))
            for node in all_nodes
        )
        
        # Check for table/data patterns
        has_table = any(
            any(keyword in node.type.lower() or node.name.lower() for keyword in ['table', 'data-table', 'data grid'])
            for node in all_nodes
        )
        
        # NEW: Check for form patterns
        has_form = any(
            any(keyword in node.type.lower() or node.name.lower() for keyword in ['form', 'input', 'field', 'textfield'])
            for node in all_nodes
        )
        
        # NEW: Check layout structure more intelligently
        root_layout = layout_tree.layout_type
        immediate_children = layout_tree.children
        
        # Dashboard pattern: typically has navbar + sidebar + main content area
        if has_sidebar and has_navbar:
            return "dashboard-layout"
        
        # Admin panel: sidebar with multiple sections
        elif has_sidebar and len(immediate_children) >= 2:
            return "sidebar-layout"
        
        # Standard app layout: header + content
        elif has_navbar and root_layout == 'VERTICAL':
            return "header-main-layout"
        
        # Data view: tables or grids
        elif has_table or (has_grid and not has_form):
            return "data-grid-layout"
        
        # Form page
        elif has_form and root_layout == 'VERTICAL':
            return "form-layout"
        
        # Grid layout (cards, tiles)
        elif has_grid:
            return "grid-layout"
        
        # Basic layouts
        elif root_layout == 'VERTICAL':
            return "vertical-stack"
        elif root_layout == 'HORIZONTAL':
            return "horizontal-layout"
        else:
            return "custom-layout"
    
    def _generate_implementation_from_layout(
        self, 
        layout_tree: LayoutNode, 
        components: List[ModusComponent],
        page_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate implementation guide based on layout and components"""
        
        # CSS framework recommendations
        css_framework = self._recommend_css_framework(layout_tree)
        
        # Structure recommendations
        structure = self._generate_component_structure(layout_tree, components)
        
        # Layout CSS
        layout_css = self._generate_layout_css(layout_tree)
        
        return {
            'css_framework': css_framework,
            'structure': structure,
            'layout_css': layout_css,
            'responsive_hints': self._generate_responsive_hints(layout_tree),
            'component_hierarchy': self._build_component_hierarchy(components)
        }
    
    def _generate_simple_structure(self, layout_tree: LayoutNode, components: List[ModusComponent]) -> List[Dict[str, Any]]:
        """Generate a simplified structure showing only important containers and components"""
        # Create a mapping of node names to components (not IDs which might be None)
        comp_map = {}
        for comp in components:
            if comp.original_node_name:
                comp_map[comp.original_node_name] = comp
        
        structure = []
        
        def process_important_nodes(node: LayoutNode, level: int = 0) -> Optional[Dict[str, Any]]:
            # Skip deeply nested or unimportant nodes
            if level > 3:
                return None
            
            # Try to find component by node name/type
            comp = comp_map.get(node.type)
            
            # Only include if it's a component or important container
            is_important = (
                comp is not None or 
                node.layout_type in ['VERTICAL', 'HORIZONTAL', 'GRID'] or
                any(keyword in node.type.lower() for keyword in ['header', 'main', 'sidebar', 'footer', 'nav', 'content'])
            )
            
            if not is_important and level > 1:
                return None
            
            item = {
                'type': comp.component_type if comp else f"{node.layout_type.lower()}-container",
                'name': node.type
            }
            
            # Add properties only if component
            if comp and comp.properties:
                props = {k: v for k, v in comp.properties.items() if v}
                if props:
                    item['props'] = props
            
            # Process children
            children = []
            for child in node.children:
                child_item = process_important_nodes(child, level + 1)
                if child_item:
                    children.append(child_item)
            
            if children:
                item['children'] = children
                
            return item
        
        root = process_important_nodes(layout_tree)
        if root:
            structure.append(root)
            
        return structure
    
    def _generate_quick_start_code(self, components_by_type: Dict[str, List], layout: str) -> str:
        """Generate simple starter code"""
        code_lines = []
        
        # Basic structure based on layout
        if layout == "dashboard-layout":
            code_lines.extend([
                "<div className='dashboard-container'>",
                "  <ModusNavbar />",
                "  <div className='dashboard-body'>",
                "    <ModusSideNavigation />",
                "    <main className='dashboard-content'>",
                "      {/* Main content area */}",
                "    </main>",
                "  </div>",
                "</div>"
            ])
        elif layout == "sidebar-layout":
            code_lines.extend([
                "<div className='app-container'>",
                "  <ModusSideNavigation />",
                "  <main className='main-content'>",
                "    {/* Your content here */}",
                "  </main>",
                "</div>"
            ])
        elif layout == "header-main-layout":
            code_lines.extend([
                "<div className='app-container'>",
                "  <ModusNavbar />",
                "  <main className='main-content'>",
                "    {/* Your content here */}",
                "  </main>",
                "</div>"
            ])
        elif layout == "data-grid-layout":
            code_lines.extend([
                "<div className='data-view-container'>",
                "  <ModusTable />",
                "  {/* Additional data components */}",
                "</div>"
            ])
        else:
            code_lines.extend([
                "<div className='app-container'>",
                "  {/* Your layout here */}",
                "</div>"
            ])
            
        return '\n'.join(code_lines)
    
    def _get_required_imports(self, components_by_type: Dict[str, List]) -> List[str]:
        """Get list of required Modus imports"""
        imports = []
        
        for comp_type in components_by_type.keys():
            # Convert modus-wc-button to ModusButton format
            parts = comp_type.split('-')
            if len(parts) >= 3 and parts[0] == 'modus' and parts[1] == 'wc':
                component_name = 'Modus' + ''.join(part.capitalize() for part in parts[2:])
                imports.append(component_name)
                
        return sorted(imports)
    
    def _recommend_css_framework(self, layout_tree: LayoutNode) -> Dict[str, Any]:
        """Recommend CSS framework based on layout patterns"""
        recommendations = []
        
        # Check for grid usage
        grid_nodes = [
            node for node in self._get_all_nodes(layout_tree)
            if node.layout_type == 'GRID'
        ]
        
        if grid_nodes:
            recommendations.append({
                'type': 'CSS Grid',
                'reason': f'Found {len(grid_nodes)} grid layouts',
                'confidence': 0.9
            })
        
        # Check for flex usage
        flex_nodes = [
            node for node in self._get_all_nodes(layout_tree)
            if node.layout_type in ['HORIZONTAL', 'VERTICAL']
        ]
        
        if len(flex_nodes) > len(grid_nodes):
            recommendations.append({
                'type': 'Flexbox',
                'reason': f'Found {len(flex_nodes)} flex layouts',
                'confidence': 0.95
            })
        
        # Check for responsive patterns
        if layout_tree.metadata.get('has_row_groups'):
            recommendations.append({
                'type': 'Responsive Grid System',
                'reason': 'Multiple row groups detected',
                'confidence': 0.8
            })
        
        return {
            'primary': recommendations[0] if recommendations else {'type': 'Flexbox', 'confidence': 0.7},
            'all': recommendations
        }
    
    def _generate_component_structure(self, layout_tree: LayoutNode, components: List[ModusComponent]) -> List[Dict[str, Any]]:
        """Generate structured component layout"""
        structure = []
        
        # Group components by their layout context
        component_map = {comp.original_node_id: comp for comp in components}
        
        def process_node(node: LayoutNode, level: int = 0) -> Optional[Dict[str, Any]]:
            component = component_map.get(node.id)
            
            item = {
                'id': node.id,
                'type': component.component_type if component else 'container',
                'layout_type': node.layout_type,
                'level': level,
                'children': []
            }
            
            if component:
                item['component'] = component.component_type
                item['properties'] = component.properties
                item['css'] = component.layout_css
            
            # Process children
            for child in node.children:
                child_item = process_node(child, level + 1)
                if child_item:
                    item['children'].append(child_item)
            
            return item
        
        root_structure = process_node(layout_tree)
        if root_structure:
            structure.append(root_structure)
        
        return structure
    
    def _generate_layout_css(self, layout_tree: LayoutNode) -> Dict[str, Any]:
        """Generate CSS for the entire layout"""
        css_rules = {}
        
        def generate_css_for_node(node: LayoutNode, parent_selector: str = '') -> None:
            selector = f"{parent_selector} .node-{node.id}".strip()
            
            rules = {}
            
            # Layout type specific CSS
            if node.layout_type == 'HORIZONTAL':
                rules.update({
                    'display': 'flex',
                    'flex-direction': 'row',
                    'align-items': 'center'
                })
            elif node.layout_type == 'VERTICAL':
                rules.update({
                    'display': 'flex',
                    'flex-direction': 'column'
                })
            elif node.layout_type == 'GRID':
                rules.update({
                    'display': 'grid',
                    'grid-template-columns': f"repeat({node.metadata.get('columns', 1)}, 1fr)",
                    'gap': '1rem'
                })
            
            # Add spacing
            if node.metadata.get('item_spacing'):
                rules['gap'] = f"{node.metadata['item_spacing']}px"
            
            css_rules[selector] = rules
            
            # Process children
            for child in node.children:
                generate_css_for_node(child, selector)
        
        generate_css_for_node(layout_tree)
        
        return css_rules
    
    def _generate_responsive_hints(self, layout_tree: LayoutNode) -> List[Dict[str, Any]]:
        """Generate responsive design hints"""
        hints = []
        
        # Check for components that might need responsive behavior
        all_nodes = self._get_all_nodes(layout_tree)
        
        # Grid layouts
        grid_nodes = [n for n in all_nodes if n.layout_type == 'GRID']
        if grid_nodes:
            hints.append({
                'type': 'grid-responsive',
                'message': 'Grid layouts should adapt columns on smaller screens',
                'css': '@media (max-width: 768px) { grid-template-columns: 1fr; }'
            })
        
        # Row groups
        row_groups = [n for n in all_nodes if n.type == 'ROW_GROUP']
        if row_groups:
            hints.append({
                'type': 'row-stack',
                'message': 'Row groups should stack vertically on mobile',
                'css': '@media (max-width: 768px) { flex-direction: column; }'
            })
        
        # Sidebar layouts
        sidebar_nodes = [n for n in all_nodes if n.metadata.get('pattern') == 'sidebar']
        if sidebar_nodes:
            hints.append({
                'type': 'sidebar-collapse',
                'message': 'Sidebar should be collapsible on mobile',
                'suggestion': 'Use modus-side-navigation with responsive prop'
            })
        
        return hints
    
    def _build_component_hierarchy(self, components: List[ModusComponent]) -> List[Dict[str, Any]]:
        """Build hierarchical view of components"""
        # Components are already hierarchical from the mapper
        hierarchy = []
        
        # Get root components (no parent)
        root_components = [
            comp for comp in components
            if not any(comp in c.children for c in components)
        ]
        
        def build_hierarchy_item(comp: ModusComponent) -> Dict[str, Any]:
            return {
                'type': comp.component_type,
                'name': comp.original_node_name,
                'properties': comp.properties,
                'detection_method': comp.detection_method,
                'confidence': comp.confidence,
                'children': [build_hierarchy_item(child) for child in comp.children]
            }
        
        for root in root_components:
            hierarchy.append(build_hierarchy_item(root))
        
        return hierarchy
    
    def _get_all_nodes(self, node: LayoutNode) -> List[LayoutNode]:
        """Get all nodes in the tree"""
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes
        
    def analyze(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze any Figma node and return comprehensive layout and component information
        """
        # Extract all components and layouts
        components = []
        layout_structure = self._extract_layout_structure(node)
        modus_mapping = []
        
        # Walk through the tree and identify components
        self._identify_components(node, components, modus_mapping)
        
        # Analyze page patterns
        page_patterns = self._analyze_page_patterns(layout_structure)
        
        # Generate implementation guide
        implementation_guide = self._generate_implementation_guide(components, modus_mapping, page_patterns)
        
        return {
            'page_info': {
                'name': node.get('name', 'Unnamed'),
                'type': node.get('type', 'Unknown'),
                'dimensions': self._extract_dimensions(node)
            },
            'layout_structure': layout_structure,
            'components_found': components,
            'modus_mapping': modus_mapping,
            'page_patterns': page_patterns,
            'implementation_guide': implementation_guide,
            'statistics': {
                'total_components': len(components),
                'modus_components': len([m for m in modus_mapping if m['modus_component'] != 'custom']),
                'custom_components': len([m for m in modus_mapping if m['modus_component'] == 'custom']),
                'layout_depth': self._calculate_depth(layout_structure)
            }
        }
    
    def _extract_layout_structure(self, node: Dict[str, Any], depth: int = 0, parent_bounds: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract hierarchical layout structure"""
        structure = {
            'name': node.get('name', ''),
            'type': node.get('type', ''),
            'role': self._determine_role(node),
            'layout': self._extract_layout_properties(node, parent_bounds),
            'style': self._extract_styles(node),
            'children': []
        }
        
        # Process children
        children = node.get('children', [])
        current_bounds = node.get('absoluteBoundingBox')
        
        for child in children:
            if child.get('visible', True):
                child_structure = self._extract_layout_structure(child, depth + 1, current_bounds)
                if child_structure:
                    structure['children'].append(child_structure)
        
        return structure
    
    def _extract_layout_properties(self, node: Dict[str, Any], parent_bounds: Optional[Dict] = None) -> Dict[str, Any]:
        """Extract layout properties including position, size, and constraints"""
        layout = {}
        
        # Get absolute bounds
        if 'absoluteBoundingBox' in node:
            bounds = node['absoluteBoundingBox']
            layout['position'] = {
                'x': bounds.get('x', 0),
                'y': bounds.get('y', 0)
            }
            layout['dimensions'] = {
                'width': bounds.get('width', 0),
                'height': bounds.get('height', 0)
            }
            
            # Calculate relative position
            if parent_bounds:
                layout['position']['relative_x'] = bounds['x'] - parent_bounds['x']
                layout['position']['relative_y'] = bounds['y'] - parent_bounds['y']
        
        # Extract layout mode
        if node.get('layoutMode'):
            layout['display'] = 'flex'
            layout['flexDirection'] = 'row' if node['layoutMode'] == 'HORIZONTAL' else 'column'
            
            # Extract spacing
            if node.get('itemSpacing'):
                layout['gap'] = f"{node['itemSpacing']}px"
            
            # Extract padding
            padding_keys = ['paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft']
            paddings = [node.get(key, 0) for key in padding_keys]
            if any(paddings):
                layout['padding'] = ' '.join(f"{p}px" for p in paddings)
            
            # Extract alignment
            if node.get('primaryAxisAlignItems'):
                align_map = {
                    'MIN': 'flex-start',
                    'CENTER': 'center',
                    'MAX': 'flex-end',
                    'SPACE_BETWEEN': 'space-between'
                }
                layout['justifyContent'] = align_map.get(node['primaryAxisAlignItems'], 'flex-start')
            
            if node.get('counterAxisAlignItems'):
                align_map = {
                    'MIN': 'flex-start',
                    'CENTER': 'center',
                    'MAX': 'flex-end'
                }
                layout['alignItems'] = align_map.get(node['counterAxisAlignItems'], 'flex-start')
        
        # Extract constraints
        if 'constraints' in node:
            layout['constraints'] = node['constraints']
        
        return layout
    
    def _extract_styles(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract visual styles"""
        styles = {}
        
        # Extract fills (background)
        if node.get('fills'):
            for fill in node['fills']:
                if fill.get('visible', True) and fill.get('type') == 'SOLID':
                    color = fill.get('color', {})
                    r = int(color.get('r', 0) * 255)
                    g = int(color.get('g', 0) * 255)
                    b = int(color.get('b', 0) * 255)
                    a = fill.get('opacity', color.get('a', 1))
                    styles['backgroundColor'] = f"rgba({r}, {g}, {b}, {a})"
                    break
        
        # Extract strokes (border)
        if node.get('strokes'):
            for stroke in node['strokes']:
                if stroke.get('visible', True):
                    color = stroke.get('color', {})
                    r = int(color.get('r', 0) * 255)
                    g = int(color.get('g', 0) * 255)
                    b = int(color.get('b', 0) * 255)
                    a = stroke.get('opacity', color.get('a', 1))
                    weight = node.get('strokeWeight', 1)
                    styles['border'] = f"{weight}px solid rgba({r}, {g}, {b}, {a})"
                    break
        
        # Extract corner radius
        if node.get('cornerRadius'):
            styles['borderRadius'] = f"{node['cornerRadius']}px"
        
        # Extract effects (shadows, etc.)
        if node.get('effects'):
            shadows = []
            for effect in node['effects']:
                if effect.get('visible', True) and effect.get('type') == 'DROP_SHADOW':
                    color = effect.get('color', {})
                    r = int(color.get('r', 0) * 255)
                    g = int(color.get('g', 0) * 255)
                    b = int(color.get('b', 0) * 255)
                    a = color.get('a', 1)
                    x = effect.get('offset', {}).get('x', 0)
                    y = effect.get('offset', {}).get('y', 0)
                    blur = effect.get('radius', 0)
                    shadows.append(f"{x}px {y}px {blur}px rgba({r}, {g}, {b}, {a})")
            
            if shadows:
                styles['boxShadow'] = ', '.join(shadows)
        
        # Extract opacity
        if node.get('opacity') is not None and node['opacity'] < 1:
            styles['opacity'] = node['opacity']
        
        return styles
    
    def _determine_role(self, node: Dict[str, Any]) -> str:
        """Determine the semantic role of a node"""
        name_lower = node.get('name', '').lower()
        node_type = node.get('type', '')
        
        # Check component instance
        if node_type == 'INSTANCE':
            return self._identify_component_type(node)
        
        # Layout patterns
        layout_patterns = {
            'header': ['header', 'navbar', 'navigation', 'topbar', 'app bar'],
            'footer': ['footer', 'bottom'],
            'sidebar': ['sidebar', 'sidenav', 'side navigation', 'aside'],
            'main': ['main', 'content', 'body', 'page'],
            'section': ['section', 'segment', 'block'],
            'container': ['container', 'wrapper', 'holder'],
            'row': ['row', 'horizontal'],
            'column': ['column', 'col', 'vertical']
        }
        
        for role, patterns in layout_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return role
        
        # UI element patterns
        element_patterns = {
            'form': ['form', 'input-group'],
            'list': ['list', 'items'],
            'grid': ['grid', 'table'],
            'hero': ['hero', 'banner', 'jumbotron'],
            'feature': ['feature', 'benefit'],
            'cta': ['cta', 'call-to-action'],
            'testimonial': ['testimonial', 'review'],
            'pricing': ['pricing', 'plan'],
            'faq': ['faq', 'question'],
            'gallery': ['gallery', 'images'],
            'stats': ['stats', 'metrics', 'numbers']
        }
        
        for role, patterns in element_patterns.items():
            if any(pattern in name_lower for pattern in patterns):
                return role
        
        # Default based on type
        if node_type == 'TEXT':
            return 'text'
        elif node_type in ['FRAME', 'GROUP']:
            return 'container'
        else:
            return 'element'
    
    def _identify_components(self, node: Dict[str, Any], components: List[Dict], modus_mapping: List[Dict], path: str = ""):
        """Recursively identify all components in the tree"""
        current_path = f"{path}/{node.get('name', '')}" if path else node.get('name', '')
        
        # Check if this is a component
        if self._is_component(node):
            component_info = {
                'name': node.get('name', 'Unknown'),
                'type': node.get('type', ''),
                'path': current_path,
                'component_type': self._identify_component_type(node),
                'properties': self._extract_component_properties(node)
            }
            components.append(component_info)
            
            # Map to Modus component
            modus_component = self._map_to_modus(component_info['component_type'])
            if modus_component:
                modus_mapping.append({
                    'figma_component': component_info['name'],
                    'modus_component': modus_component,
                    'properties': component_info['properties'],
                    'path': current_path
                })
        
        # Recursively process children
        for child in node.get('children', []):
            if isinstance(child, dict) and child.get('visible', True):
                self._identify_components(child, components, modus_mapping, current_path)
    
    def _is_component(self, node: Dict[str, Any]) -> bool:
        """Check if a node represents a component"""
        node_type = node.get('type', '')
        name_lower = node.get('name', '').lower()
        
        # Skip decorative elements
        decorative_patterns = [
            'line', 'divider', 'separator', 'fingerprint', 
            'decoration', 'ornament', 'background', 'blur',
            'shadow', 'glow', 'gradient', 'mask', 'overlay'
        ]
        
        if any(pattern in name_lower for pattern in decorative_patterns):
            return False
        
        # Direct component types
        if node_type in ['COMPONENT', 'INSTANCE']:
            return True
        
        # Check for component-like patterns
        component_indicators = [
            'button', 'input', 'select', 'checkbox', 'radio', 'switch',
            'card', 'modal', 'dropdown', 'tabs', 'accordion', 'table',
            'alert', 'badge', 'chip', 'tooltip', 'progress', 'spinner'
        ]
        
        if any(indicator in name_lower for indicator in component_indicators):
            return True
        
        # Check if it has component-like structure
        children = node.get('children', [])
        if children and node_type == 'FRAME':
            # Check for common component patterns
            child_types = [child.get('type') for child in children if isinstance(child, dict)]
            
            # Button pattern: text inside a frame
            if len(child_types) == 1 and child_types[0] == 'TEXT':
                return True
            
            # Input pattern: frame with text
            if 'TEXT' in child_types and any('placeholder' in str(child.get('name', '')).lower() for child in children if isinstance(child, dict)):
                return True
        
        return False
    
    def _identify_component_type(self, node: Dict[str, Any]) -> str:
        """Identify the type of component"""
        name_lower = node.get('name', '').lower()
        
        # Check children for more context
        children = node.get('children', [])
        child_names = [child.get('name', '').lower() for child in children if isinstance(child, dict)]
        all_text = ' '.join(child_names + [name_lower])
        
        # Component type patterns
        patterns = {
            'button': ['button', 'btn', 'cta', 'action'],
            'input': ['input', 'textfield', 'text field', 'textbox'],
            'textarea': ['textarea', 'text area', 'multiline'],
            'select': ['select', 'dropdown', 'picker', 'combobox'],
            'checkbox': ['checkbox', 'check box', 'check'],
            'radio': ['radio', 'radio button', 'option'],
            'switch': ['switch', 'toggle', 'on/off'],
            'slider': ['slider', 'range'],
            'card': ['card', 'tile', 'panel'],
            'table': ['table', 'grid', 'data table'],
            'modal': ['modal', 'dialog', 'popup', 'overlay'],
            'alert': ['alert', 'notification', 'message', 'warning', 'error', 'success'],
            'tabs': ['tab', 'tabs', 'tabbed'],
            'accordion': ['accordion', 'collapse', 'expandable'],
            'navbar': ['navbar', 'navigation', 'nav bar', 'header'],
            'breadcrumb': ['breadcrumb', 'breadcrumbs'],
            'badge': ['badge', 'tag', 'label'],
            'chip': ['chip', 'tag'],
            'tooltip': ['tooltip', 'hint', 'popover'],
            'progress': ['progress', 'loading', 'progress bar'],
            'spinner': ['spinner', 'loader', 'loading'],
            'pagination': ['pagination', 'pager', 'page'],
            'avatar': ['avatar', 'profile', 'user'],
            'icon': ['icon'],
            'sidebar': ['sidebar', 'sidenav', 'side navigation'],
            'toolbar': ['toolbar', 'tool bar'],
            'menu': ['menu', 'dropdown menu'],
            'form': ['form'],
            'list': ['list'],
            'divider': ['divider', 'separator', 'line'],
            'stepper': ['stepper', 'steps', 'wizard'],
            'rating': ['rating', 'stars', 'rate'],
            'autocomplete': ['autocomplete', 'typeahead', 'search'],
            'date-picker': ['date', 'calendar', 'datepicker']
        }
        
        for comp_type, keywords in patterns.items():
            if any(keyword in all_text for keyword in keywords):
                return comp_type
        
        return 'custom'
    
    def _extract_component_properties(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """Extract component-specific properties"""
        props = {}
        
        # Extract text content
        texts = self._extract_all_text(node)
        if texts:
            props['text'] = texts
        
        # Extract state indicators
        name_lower = node.get('name', '').lower()
        states = ['hover', 'active', 'disabled', 'selected', 'focused', 'error', 'success']
        for state in states:
            if state in name_lower:
                props['state'] = state
                break
        
        # Extract size variants
        sizes = ['small', 'medium', 'large', 'sm', 'md', 'lg', 'xl', 'xs']
        for size in sizes:
            if size in name_lower:
                props['size'] = size
                break
        
        # Extract color variants
        colors = ['primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark']
        for color in colors:
            if color in name_lower:
                props['variant'] = color
                break
        
        return props
    
    def _extract_all_text(self, node: Dict[str, Any]) -> List[str]:
        """Extract all text from a node tree"""
        texts = []
        
        # Validate node is a dictionary
        if not isinstance(node, dict):
            return texts
        
        if node.get('type') == 'TEXT' and 'characters' in node:
            texts.append(node['characters'])
        
        for child in node.get('children', []):
            texts.extend(self._extract_all_text(child))
        
        return texts
    
    def _map_to_modus(self, component_type: str) -> Optional[str]:
        """Map component type to Modus component"""
        return self.modus_components.get(component_type)
    
    def _analyze_page_patterns(self, layout_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall page patterns"""
        patterns = {
            'layout_type': 'unknown',
            'has_header': False,
            'has_footer': False,
            'has_sidebar': False,
            'has_navigation': False,
            'content_sections': [],
            'forms_found': 0,
            'tables_found': 0,
            'cards_found': 0,
            'modals_found': 0
        }
        
        def analyze_node(node: Dict):
            role = node.get('role', '')
            
            if role == 'header':
                patterns['has_header'] = True
            elif role == 'footer':
                patterns['has_footer'] = True
            elif role == 'sidebar':
                patterns['has_sidebar'] = True
            elif role in ['navbar', 'navigation']:
                patterns['has_navigation'] = True
            elif role == 'section':
                patterns['content_sections'].append(node.get('name', 'Unknown Section'))
            elif role == 'form':
                patterns['forms_found'] += 1
            elif role == 'table':
                patterns['tables_found'] += 1
            elif role == 'card':
                patterns['cards_found'] += 1
            elif role == 'modal':
                patterns['modals_found'] += 1
            
            for child in node.get('children', []):
                analyze_node(child)
        
        analyze_node(layout_structure)
        
        # Determine layout type
        if patterns['has_sidebar']:
            patterns['layout_type'] = 'sidebar-layout'
        elif patterns['has_header'] and patterns['has_footer']:
            patterns['layout_type'] = 'header-content-footer'
        elif patterns['has_header']:
            patterns['layout_type'] = 'header-content'
        else:
            patterns['layout_type'] = 'single-page'
        
        return patterns
    
    def _calculate_depth(self, node: Dict[str, Any], current_depth: int = 0) -> int:
        """Calculate maximum depth of the layout tree"""
        if not node.get('children'):
            return current_depth
        
        max_child_depth = current_depth
        for child in node['children']:
            if isinstance(child, dict):
                child_depth = self._calculate_depth(child, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
        
        return max_child_depth
    
    def _extract_dimensions(self, node: Dict[str, Any]) -> Dict[str, float]:
        """Extract dimensions from node"""
        if 'absoluteBoundingBox' in node:
            bounds = node['absoluteBoundingBox']
            return {
                'width': bounds.get('width', 0),
                'height': bounds.get('height', 0)
            }
        return {'width': 0, 'height': 0}
    
    def _generate_implementation_guide(self, components: List[Dict], modus_mapping: List[Dict], patterns: Dict) -> Dict[str, Any]:
        """Generate implementation guide"""
        guide = {
            'layout_recommendation': self._get_layout_recommendation(patterns),
            'component_summary': self._get_component_summary(modus_mapping),
            'implementation_steps': self._get_implementation_steps(patterns, modus_mapping),
            'code_structure': self._get_code_structure(patterns, modus_mapping)
        }
        
        return guide
    
    def _get_layout_recommendation(self, patterns: Dict) -> str:
        """Get layout recommendation based on patterns"""
        layout_type = patterns['layout_type']
        
        recommendations = {
            'sidebar-layout': "Use a flex container with sidebar and main content area. Consider modus-side-navigation for the sidebar.",
            'header-content-footer': "Use a vertical flex layout with header (modus-navbar), main content area, and footer.",
            'header-content': "Use modus-navbar for header and a main content container below.",
            'single-page': "Use a simple container layout with sections for different content areas."
        }
        
        return recommendations.get(layout_type, "Use a flexible container-based layout.")
    
    def _get_component_summary(self, modus_mapping: List[Dict]) -> Dict[str, List[str]]:
        """Summarize components by type"""
        summary = {}
        
        for mapping in modus_mapping:
            modus_comp = mapping['modus_component']
            if modus_comp not in summary:
                summary[modus_comp] = []
            summary[modus_comp].append(mapping['figma_component'])
        
        return summary
    
    def _get_implementation_steps(self, patterns: Dict, modus_mapping: List[Dict]) -> List[str]:
        """Generate implementation steps"""
        steps = []
        
        # Layout setup
        if patterns['has_header']:
            steps.append("1. Set up modus-navbar for the header/navigation")
        
        if patterns['has_sidebar']:
            steps.append("2. Implement modus-side-navigation for the sidebar")
        
        steps.append(f"{len(steps) + 1}. Create main content area with {patterns['layout_type']} layout")
        
        # Component implementation
        if patterns['forms_found'] > 0:
            steps.append(f"{len(steps) + 1}. Implement {patterns['forms_found']} form(s) using modus form components")
        
        if patterns['tables_found'] > 0:
            steps.append(f"{len(steps) + 1}. Set up {patterns['tables_found']} modus-table component(s)")
        
        if patterns['cards_found'] > 0:
            steps.append(f"{len(steps) + 1}. Create {patterns['cards_found']} modus-card component(s)")
        
        if patterns['modals_found'] > 0:
            steps.append(f"{len(steps) + 1}. Implement {patterns['modals_found']} modus-modal component(s)")
        
        return steps
    
    def _get_code_structure(self, patterns: Dict, modus_mapping: List[Dict]) -> str:
        """Generate basic code structure"""
        # Generate a React-style component structure
        imports = set()
        
        # Add imports based on components found
        for mapping in modus_mapping:
            component = mapping['modus_component']
            if component != 'custom':
                imports.add(f"import {{ {component.replace('modus-', 'Modus')} }} from '@trimble-oss/modus-react-components';")
        
        # Generate basic structure
        code = "// Imports\n"
        code += "\n".join(sorted(imports)) + "\n\n"
        
        code += "// Component Structure\n"
        code += "export const Page = () => {\n"
        code += "  return (\n"
        code += "    <div className='page-container'>\n"
        
        if patterns['has_header']:
            code += "      <ModusNavbar />\n"
        
        if patterns['has_sidebar']:
            code += "      <div className='layout-with-sidebar'>\n"
            code += "        <ModusSideNavigation />\n"
            code += "        <main className='main-content'>\n"
            code += "          {/* Page content */}\n"
            code += "        </main>\n"
            code += "      </div>\n"
        else:
            code += "      <main className='main-content'>\n"
            code += "        {/* Page content */}\n"
            code += "      </main>\n"
        
        if patterns['has_footer']:
            code += "      <footer>{/* Footer content */}</footer>\n"
        
        code += "    </div>\n"
        code += "  );\n"
        code += "};"
        
        return code

    def _build_concise_layout_structure(self, layout_tree: LayoutNode, components: List[ModusComponent]) -> Dict[str, Any]:
        """Build a concise layout structure optimized for LLM context"""
        # Map components for quick lookup
        comp_map = {comp.original_node_id: comp for comp in components if comp.original_node_id}
        
        def should_include_node(node: LayoutNode, depth: int) -> bool:
            """Determine if a node should be included in the concise structure"""
            # Always include root and first 2 levels
            if depth <= 2:
                return True
            
            # Include if it's a component
            if comp_map.get(node.id):
                return True
            
            # Include important layout containers
            if node.type in ['FRAME', 'GROUP'] and len(node.children) > 0:
                # Check if any child is a component
                has_component_child = any(
                    comp_map.get(child.id) or should_include_node(child, depth + 1)
                    for child in node.children[:5]  # Check first 5 children
                )
                return has_component_child
            
            return False
        
        def build_concise_node(node: LayoutNode, depth: int = 0, seen_patterns: Dict[str, int] = None) -> Optional[Dict[str, Any]]:
            if seen_patterns is None:
                seen_patterns = {}
            
            # Hard depth limit
            if depth > 5:
                return None
            
            # Skip if node shouldn't be included
            if not should_include_node(node, depth):
                return None
            
            # Check for repetitive patterns
            pattern_key = f"{node.type}:{node.name}"
            if pattern_key in seen_patterns and seen_patterns[pattern_key] > 5:
                return None  # Skip after 5 similar elements
            seen_patterns[pattern_key] = seen_patterns.get(pattern_key, 0) + 1
            
            # Build basic node info
            node_info = {
                'id': node.id,
                'name': node.name or node.type,
                'layout': node.layout_type
            }
            
            # Add component info if found
            component = comp_map.get(node.id)
            if component:
                node_info['component'] = {
                    'type': component.component_type,
                    'properties': {k: v for k, v in component.properties.items() if v}
                }
            
            # Add dimensions only for top levels and components
            if depth < 3 or component:
                if node.original_node and 'absoluteBoundingBox' in node.original_node:
                    bounds = node.original_node['absoluteBoundingBox']
                    node_info['dimensions'] = {
                        'width': round(bounds.get('width', 0)),
                        'height': round(bounds.get('height', 0))
                    }
            
            # Add spacing if significant
            if node.metadata.get('item_spacing'):
                node_info['spacing'] = node.metadata['item_spacing']
            
            # Process children intelligently
            if node.children:
                # Handle special case of repetitive patterns
                if len(node.children) > 20:
                    # Check if all children are similar
                    first_child = node.children[0]
                    if all(child.name == first_child.name for child in node.children):
                        # All children have same name - collapse them
                        children = [{
                            'name': f"{first_child.name or first_child.type} (×{len(node.children)})",
                            'type': 'REPEATED_PATTERN',
                            'count': len(node.children),
                            'note': f'Collapsed {len(node.children)} identical elements'
                        }]
                    else:
                        # Show first few and indicate more
                        children = []
                        for i, child in enumerate(node.children[:3]):
                            child_node = build_concise_node(child, depth + 1, seen_patterns.copy())
                            if child_node:
                                children.append(child_node)
                        if len(node.children) > 3:
                            children.append({
                                'name': f'... and {len(node.children) - 3} more items',
                                'type': 'TRUNCATED',
                                'count': len(node.children) - 3
                            })
                else:
                    # Normal processing for smaller sets
                    children = []
                    for child in node.children[:5]:  # Limit to first 5
                        child_node = build_concise_node(child, depth + 1, seen_patterns.copy())
                        if child_node:
                            children.append(child_node)
                
                if children:
                    node_info['children'] = children
            
            return node_info
        
        return build_concise_node(layout_tree) or {'error': 'Failed to build layout structure'}
    
    def _build_layout_structure_with_components(self, layout_tree: LayoutNode, components: List[ModusComponent]) -> Dict[str, Any]:
        """Build a hierarchical layout structure that includes component information"""
        # Map components by both ID and name for better matching
        comp_by_id = {comp.original_node_id: comp for comp in components if comp.original_node_id}
        comp_by_name = {comp.original_node_name: comp for comp in components}
        
        def build_node_info(node: LayoutNode, depth: int = 0) -> Optional[Dict[str, Any]]:
            # Allow deeper nesting for more details
            if depth > 6:
                return None
            
            # Find associated component
            component = comp_by_id.get(node.id) or comp_by_name.get(node.type) or comp_by_name.get(node.name)
            
            # Build node info - ALWAYS include node ID
            node_info = {
                'id': node.id,  # Include node ID for fetching more details
                'name': node.name or node.type,
                'type': node.type,
                'layout': node.layout_type
            }
            
            # Add component info if found
            if component:
                node_info['component'] = {
                    'type': component.component_type,
                    'properties': {k: v for k, v in component.properties.items() if v}
                }
            
            # Add layout metadata if relevant
            if node.metadata.get('item_spacing'):
                node_info['spacing'] = node.metadata['item_spacing']
            
            # Always add dimensions for all nodes
            if node.original_node and 'absoluteBoundingBox' in node.original_node:
                bounds = node.original_node['absoluteBoundingBox']
                node_info['dimensions'] = {
                    'width': round(bounds.get('width', 0)),
                    'height': round(bounds.get('height', 0))
                }
            
            # Add more details from metadata
            if node.metadata:
                if node.metadata.get('primary_axis_align'):
                    node_info['alignItems'] = node.metadata['primary_axis_align']
                if node.metadata.get('counter_axis_align'):
                    node_info['justifyContent'] = node.metadata['counter_axis_align']
                if node.metadata.get('padding'):
                    node_info['padding'] = node.metadata['padding']
            
            # Process children
            children = []
            for child in node.children:
                child_info = build_node_info(child, depth + 1)
                if child_info:
                    children.append(child_info)
            
            if children:
                node_info['children'] = children
            
            return node_info
        
        return build_node_info(layout_tree) or {}
    
    def _create_component_summary(self, components: List[ModusComponent]) -> Dict[str, List[Dict[str, Any]]]:
        """Create a summary of components grouped by type"""
        summary = {}
        
        for comp in components:
            comp_type = comp.component_type
            if comp_type not in summary:
                summary[comp_type] = []
            
            comp_info = {
                'id': comp.original_node_id,  # Include node ID for fetching more details
                'name': comp.original_node_name,
                'confidence': round(comp.confidence, 2)
            }
            
            # Only add non-empty properties
            if comp.properties:
                filtered_props = {k: v for k, v in comp.properties.items() if v}
                if filtered_props:
                    comp_info['properties'] = filtered_props
            
            # Add layout context if available
            if comp.layout_css:
                comp_info['layout_hints'] = comp.layout_css
            
            summary[comp_type].append(comp_info)
        
        return summary
    
    def _analyze_page_for_llm(self, layout_tree: LayoutNode, components: List[ModusComponent]) -> Dict[str, Any]:
        """Analyze page patterns and structure for LLM"""
        all_nodes = self._get_all_nodes(layout_tree)
        comp_types = [comp.component_type for comp in components]
        
        # Detect navigation components
        has_navigation = any(
            'navbar' in comp_type for comp_type in comp_types
        ) or any(
            any(keyword in node.type.lower() or keyword in node.name.lower() 
                for keyword in ['nav', 'header', 'navigation'])
            for node in all_nodes
        )
        
        # Detect sidebar
        has_sidebar = any(
            'side-navigation' in comp_type for comp_type in comp_types
        ) or any(
            any(keyword in node.type.lower() or keyword in node.name.lower() 
                for keyword in ['sidebar', 'sidenav', 'side'])
            for node in all_nodes
        )
        
        # Detect data components
        has_data_components = any(
            comp_type in ['modus-wc-table', 'modus-wc-data-table'] 
            for comp_type in comp_types
        )
        
        # Detect forms
        has_forms = any(
            comp_type in ['modus-wc-text-input', 'modus-wc-select', 'modus-wc-checkbox'] 
            for comp_type in comp_types
        )
        
        # Determine layout type
        if has_sidebar and has_navigation:
            layout_type = "dashboard"
        elif has_sidebar:
            layout_type = "sidebar-content"
        elif has_navigation and layout_tree.layout_type == 'VERTICAL':
            layout_type = "header-content"
        elif has_data_components:
            layout_type = "data-view"
        elif has_forms:
            layout_type = "form-page"
        elif layout_tree.layout_type == 'GRID':
            layout_type = "grid-layout"
        else:
            layout_type = "custom"
        
        return {
            'layout_type': layout_type,
            'has_navigation': has_navigation,
            'has_sidebar': has_sidebar,
            'has_data_components': has_data_components,
            'has_forms': has_forms,
            'primary_layout_mode': layout_tree.layout_type
        }
    
    def _generate_implementation_guide_for_llm(self, layout_tree: LayoutNode, components: List[ModusComponent], page_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate practical implementation guidance without code"""
        layout_type = page_analysis['layout_type']
        
        # Generate CSS recommendations
        css_approach = self._recommend_css_approach(layout_tree)
        
        # Generate component placement hints
        component_placement = self._generate_component_placement(components, layout_type)
        
        return {
            'css_approach': css_approach,
            'component_placement': component_placement,
            'responsive_considerations': self._get_responsive_hints(layout_type)
        }
    
    def _generate_layout_code(self, layout_type: str, page_analysis: Dict[str, Any]) -> str:
        """Generate specific layout code based on detected pattern"""
        if layout_type == "dashboard":
            return """<div className="dashboard-container">
  <ModusNavbar className="dashboard-header" />
  <div className="dashboard-body">
    <ModusSideNavigation className="dashboard-sidebar" />
    <main className="dashboard-main">
      <div className="content-wrapper">
        {/* Main dashboard content */}
      </div>
    </main>
  </div>
</div>"""
        
        elif layout_type == "sidebar-content":
            return """<div className="app-layout">
  <ModusSideNavigation className="app-sidebar" />
  <main className="app-content">
    {/* Main content area */}
  </main>
</div>"""
        
        elif layout_type == "header-content":
            return """<div className="app-layout">
  <ModusNavbar className="app-header" />
  <main className="app-content">
    <div className="content-container">
      {/* Page content */}
    </div>
  </main>
</div>"""
        
        elif layout_type == "data-view":
            return """<div className="data-view-layout">
  <div className="data-header">
    <h1>Data View</h1>
    <div className="data-actions">
      {/* Action buttons */}
    </div>
  </div>
  <ModusTable className="data-table" />
</div>"""
        
        elif layout_type == "form-page" or layout_type == "form-layout":
            return """<div className="form-layout">
  <div className="form-container">
    <form className="modus-form">
      {/* Form fields */}
      <div className="form-actions">
        <ModusButton type="submit">Submit</ModusButton>
      </div>
    </form>
  </div>
</div>"""
        
        else:
            return """<div className="page-layout">
  {/* Custom layout implementation */}
</div>"""
    
    def _recommend_css_approach(self, layout_tree: LayoutNode) -> Dict[str, str]:
        """Recommend CSS approach based on layout analysis"""
        all_nodes = self._get_all_nodes(layout_tree)
        
        # Count layout types
        flex_count = sum(1 for node in all_nodes if node.layout_type in ['HORIZONTAL', 'VERTICAL'])
        grid_count = sum(1 for node in all_nodes if node.layout_type == 'GRID')
        
        if grid_count > flex_count * 0.3:
            return {
                'primary': 'CSS Grid',
                'reasoning': f'Found {grid_count} grid layouts',
                'example': 'display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));'
            }
        else:
            return {
                'primary': 'Flexbox',
                'reasoning': f'Found {flex_count} flex layouts',
                'example': 'display: flex; flex-direction: column; gap: 1rem;'
            }
    
    def _generate_component_placement(self, components: List[ModusComponent], layout_type: str) -> List[str]:
        """Generate hints for component placement"""
        hints = []
        comp_types = {comp.component_type for comp in components}
        
        if 'modus-wc-navbar' in comp_types:
            hints.append("Place ModusNavbar at the top of the layout")
        
        if 'modus-wc-side-navigation' in comp_types:
            hints.append("Position ModusSideNavigation on the left side with fixed width")
        
        if 'modus-wc-table' in comp_types:
            hints.append("ModusTable should be in the main content area with proper overflow handling")
        
        if 'modus-wc-button' in comp_types:
            button_count = sum(1 for comp in components if comp.component_type == 'modus-wc-button')
            if button_count > 1:
                hints.append(f"Group {button_count} buttons together in action areas")
        
        if 'modus-wc-alert' in comp_types:
            hints.append("Position alerts at the top of content areas or as toast notifications")
        
        return hints
    
    def _get_responsive_hints(self, layout_type: str) -> List[str]:
        """Get responsive design hints based on layout type"""
        hints = []
        
        if layout_type in ["dashboard", "sidebar-content"]:
            hints.append("Hide sidebar on mobile, show hamburger menu")
            hints.append("Stack dashboard panels vertically on small screens")
        
        if layout_type == "data-view":
            hints.append("Make table horizontally scrollable on mobile")
            hints.append("Consider card view for mobile data display")
        
        if layout_type == "grid-layout":
            hints.append("Reduce grid columns on smaller screens")
            hints.append("Use CSS Grid auto-fit for responsive columns")
        
        return hints
    
    def _format_undetected_components(self, undetected_nodes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Format undetected components for developer feedback"""
        if not undetected_nodes:
            return {
                'count': 0,
                'message': 'All components were successfully mapped to Modus components!'
            }
        
        # Group by reason categories
        by_reason = {}
        for node in undetected_nodes:
            for reason in node.get('possible_reasons', ['Unknown']):
                if reason not in by_reason:
                    by_reason[reason] = []
                by_reason[reason].append({
                    'name': node['name'],
                    'type': node['type']
                })
        
        # Sort by frequency and limit output
        sorted_reasons = sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True)[:5]  # Top 5 reasons
        
        # Create more concise summary
        reason_summary = []
        for reason, nodes in sorted_reasons:
            # Group similar names
            name_counts = {}
            for node in nodes:
                name = node['name']
                if name not in name_counts:
                    name_counts[name] = 0
                name_counts[name] += 1
            
            # Show only 2 unique examples
            examples = []
            for name, count in list(name_counts.items())[:2]:
                if count > 1:
                    examples.append(f"{name} (×{count})")
                else:
                    examples.append(name)
            
            reason_summary.append({
                'reason': reason,
                'count': len(nodes),
                'examples': examples
            })
        
        return {
            'count': len(undetected_nodes),
            'summary': f'{len(undetected_nodes)} elements unmapped',
            'by_reason': reason_summary
        }
    
    def _get_required_imports_from_components(self, components: List[ModusComponent]) -> List[str]:
        """Get clean import list from components"""
        imports = set()
        
        for comp in components:
            # Convert modus-wc-button to ModusButton format
            parts = comp.component_type.split('-')
            if len(parts) >= 3 and parts[0] == 'modus' and parts[1] == 'wc':
                component_name = 'Modus' + ''.join(part.capitalize() for part in parts[2:])
                imports.add(component_name)
        
        return sorted(list(imports))


# Export function for use in server.py
def analyze_universal_figma(node: Dict[str, Any]) -> Dict[str, Any]:
    """Main entry point for universal Figma analysis"""
    analyzer = UniversalFigmaAnalyzer()
    return analyzer.analyze(node) 