"""
Auto-Layout Algorithm for Architecture Diagrams

Based on Mermaid.js fCOSE approach:
- Uses direction constraints (L/R/T/B) to determine relative positions
- BFS traversal to assign grid positions
- Group containment with padding
"""

from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import deque

from architecture_parser import (
    ArchitectureDiagram, Direction, Service, Group, Junction, Edge, Layer
)


@dataclass
class LayoutConfig:
    """Layout configuration"""
    node_width: float = 80
    node_height: float = 80
    node_spacing_x: float = 120  # Horizontal gap between nodes
    node_spacing_y: float = 100  # Vertical gap between nodes
    group_padding: float = 40    # Padding inside groups
    canvas_padding: float = 50   # Padding around entire diagram
    # Layer-specific settings
    layer_height: float = 140    # Height of each layer row
    layer_spacing: float = 60    # Vertical gap between layers
    layer_label_width: float = 120  # Width reserved for layer label on left


class ArchitectureLayout:
    """Constraint-based auto-layout for architecture diagrams"""

    def __init__(self, config: Optional[LayoutConfig] = None):
        self.config = config or LayoutConfig()

    def layout(self, diagram: ArchitectureDiagram) -> ArchitectureDiagram:
        """Calculate positions for all nodes"""
        # Check if this is a layered diagram
        if diagram.is_layered():
            return self._layout_layered(diagram)

        # Standard layout for non-layered diagrams
        # Step 1: Build adjacency lists from edges
        adj = self._build_adjacency(diagram)

        # Step 2: Assign grid positions using BFS
        grid_pos = self._assign_grid_positions(diagram, adj)

        # Step 3: Convert grid to pixel positions
        self._apply_grid_positions(diagram, grid_pos)

        # Step 4: Calculate group bounds
        self._calculate_group_bounds(diagram)

        # Step 5: Center the diagram
        self._center_diagram(diagram)

        return diagram

    def _layout_layered(self, diagram: ArchitectureDiagram) -> ArchitectureDiagram:
        """Layout for layered flow diagrams (like Agentic AI)"""
        cfg = self.config
        layers = diagram.get_layers_ordered()

        # Calculate total width needed
        max_services_per_layer = 0
        for layer in layers:
            children = diagram.get_children(layer.id)
            max_services_per_layer = max(max_services_per_layer, len(children))

        total_width = cfg.layer_label_width + max_services_per_layer * (cfg.node_width + cfg.node_spacing_x)
        services_area_width = max_services_per_layer * (cfg.node_width + cfg.node_spacing_x)

        # Position each layer and its services
        y_offset = cfg.canvas_padding

        for layer in layers:
            children = diagram.get_children(layer.id)

            # Layer position (left side label area)
            layer.x = cfg.canvas_padding + cfg.layer_label_width / 2
            layer.y = y_offset + cfg.layer_height / 2
            layer.width = cfg.layer_label_width - 20
            layer.height = cfg.layer_height - 20

            # Position services horizontally within the layer
            services_start_x = cfg.canvas_padding + cfg.layer_label_width + cfg.node_spacing_x / 2
            num_children = len(children)

            # Center single nodes (like output) relative to the max width
            if num_children == 1:
                center_x = services_start_x + services_area_width / 2
                node = diagram.get_node(children[0])
                if node:
                    node.x = center_x
                    node.y = y_offset + cfg.layer_height / 2
            else:
                for i, child_id in enumerate(children):
                    node = diagram.get_node(child_id)
                    if node:
                        node.x = services_start_x + i * (cfg.node_width + cfg.node_spacing_x) + cfg.node_width / 2
                        node.y = y_offset + cfg.layer_height / 2

            y_offset += cfg.layer_height + cfg.layer_spacing

        return diagram

    def _build_adjacency(self, diagram: ArchitectureDiagram) -> Dict[str, List[Tuple[str, Direction, Direction]]]:
        """Build adjacency list from edges"""
        adj: Dict[str, List[Tuple[str, Direction, Direction]]] = {}

        for edge in diagram.edges:
            if edge.source_id not in adj:
                adj[edge.source_id] = []
            if edge.target_id not in adj:
                adj[edge.target_id] = []

            # Add bidirectional connections with direction info
            adj[edge.source_id].append((edge.target_id, edge.source_dir, edge.target_dir))
            adj[edge.target_id].append((edge.source_id, edge.target_dir, edge.source_dir))

        return adj

    def _assign_grid_positions(
        self,
        diagram: ArchitectureDiagram,
        adj: Dict[str, List[Tuple[str, Direction, Direction]]]
    ) -> Dict[str, Tuple[int, int]]:
        """Assign grid (row, col) positions using BFS with direction constraints"""

        grid_pos: Dict[str, Tuple[int, int]] = {}
        visited: Set[str] = set()

        # Get all node IDs
        all_nodes = set(diagram.services.keys()) | set(diagram.junctions.keys())

        # Start BFS from first node or first service
        if not all_nodes:
            return grid_pos

        start_node = list(all_nodes)[0]

        # BFS queue: (node_id, row, col)
        queue = deque([(start_node, 0, 0)])
        visited.add(start_node)
        grid_pos[start_node] = (0, 0)

        # Track occupied positions
        occupied: Set[Tuple[int, int]] = {(0, 0)}

        while queue:
            node_id, row, col = queue.popleft()

            # Process neighbors
            for neighbor_id, from_dir, to_dir in adj.get(node_id, []):
                if neighbor_id in visited:
                    continue

                # Calculate neighbor position based on direction
                new_row, new_col = self._get_neighbor_position(
                    row, col, from_dir, to_dir, occupied
                )

                visited.add(neighbor_id)
                grid_pos[neighbor_id] = (new_row, new_col)
                occupied.add((new_row, new_col))
                queue.append((neighbor_id, new_row, new_col))

        # Handle disconnected nodes
        for node_id in all_nodes - visited:
            # Find empty position
            row, col = self._find_empty_position(occupied)
            grid_pos[node_id] = (row, col)
            occupied.add((row, col))

        return grid_pos

    def _get_neighbor_position(
        self,
        row: int,
        col: int,
        from_dir: Direction,
        to_dir: Direction,
        occupied: Set[Tuple[int, int]]
    ) -> Tuple[int, int]:
        """Calculate neighbor position based on edge directions"""

        # Direction determines relative position
        # from_dir = port on source node
        # to_dir = port on target node

        # L->R means target is to the RIGHT of source
        # R->L means target is to the LEFT of source
        # T->B means target is BELOW source
        # B->T means target is ABOVE source

        delta_row, delta_col = 0, 0

        # Determine horizontal offset based on from_dir
        if from_dir == Direction.RIGHT:
            delta_col = 1  # Target is to the right
        elif from_dir == Direction.LEFT:
            delta_col = -1  # Target is to the left

        # Determine vertical offset based on from_dir
        if from_dir == Direction.BOTTOM:
            delta_row = 1  # Target is below
        elif from_dir == Direction.TOP:
            delta_row = -1  # Target is above

        new_row = row + delta_row
        new_col = col + delta_col

        # Handle conflicts - find nearby empty cell
        attempts = 0
        while (new_row, new_col) in occupied and attempts < 20:
            # Spiral outward to find empty spot
            if attempts % 4 == 0:
                new_col += 1
            elif attempts % 4 == 1:
                new_row += 1
            elif attempts % 4 == 2:
                new_col -= 1
            else:
                new_row -= 1
            attempts += 1

        return new_row, new_col

    def _find_empty_position(self, occupied: Set[Tuple[int, int]]) -> Tuple[int, int]:
        """Find an empty grid position"""
        row, col = 0, 0
        while (row, col) in occupied:
            col += 1
            if col > 10:
                col = 0
                row += 1
        return row, col

    def _apply_grid_positions(
        self,
        diagram: ArchitectureDiagram,
        grid_pos: Dict[str, Tuple[int, int]]
    ):
        """Convert grid positions to pixel coordinates"""
        cfg = self.config

        # Find grid bounds
        min_row = min(pos[0] for pos in grid_pos.values()) if grid_pos else 0
        min_col = min(pos[1] for pos in grid_pos.values()) if grid_pos else 0

        # Normalize to start from 0
        for node_id, (row, col) in grid_pos.items():
            norm_row = row - min_row
            norm_col = col - min_col

            # Calculate pixel position (center of node)
            x = cfg.canvas_padding + norm_col * (cfg.node_width + cfg.node_spacing_x) + cfg.node_width / 2
            y = cfg.canvas_padding + norm_row * (cfg.node_height + cfg.node_spacing_y) + cfg.node_height / 2

            # Apply to node
            node = diagram.get_node(node_id)
            if node:
                node.x = x
                node.y = y

    def _calculate_group_bounds(self, diagram: ArchitectureDiagram):
        """Calculate group bounds based on children"""
        cfg = self.config

        for group in diagram.groups.values():
            children = diagram.get_children(group.id)
            if not children:
                # Empty group - default size
                group.width = cfg.node_width + cfg.group_padding * 2
                group.height = cfg.node_height + cfg.group_padding * 2
                continue

            # Find bounding box of children
            min_x = float('inf')
            min_y = float('inf')
            max_x = float('-inf')
            max_y = float('-inf')

            for child_id in children:
                child = diagram.get_node(child_id)
                if child:
                    child_left = child.x - child.width / 2
                    child_right = child.x + child.width / 2
                    child_top = child.y - child.height / 2
                    child_bottom = child.y + child.height / 2

                    min_x = min(min_x, child_left)
                    min_y = min(min_y, child_top)
                    max_x = max(max_x, child_right)
                    max_y = max(max_y, child_bottom)

            # Set group bounds with padding
            group.x = (min_x + max_x) / 2
            group.y = (min_y + max_y) / 2
            group.width = (max_x - min_x) + cfg.group_padding * 2
            group.height = (max_y - min_y) + cfg.group_padding * 2

    def _center_diagram(self, diagram: ArchitectureDiagram):
        """Center diagram around origin or specified canvas"""
        # Find bounds
        all_nodes = list(diagram.services.values()) + list(diagram.junctions.values())
        if not all_nodes:
            return

        min_x = min(n.x - n.width / 2 for n in all_nodes)
        min_y = min(n.y - n.height / 2 for n in all_nodes)

        # Shift to ensure positive coordinates with padding
        offset_x = self.config.canvas_padding - min_x
        offset_y = self.config.canvas_padding - min_y

        for node in all_nodes:
            node.x += offset_x
            node.y += offset_y

        for group in diagram.groups.values():
            group.x += offset_x
            group.y += offset_y


if __name__ == '__main__':
    from architecture_parser import ArchitectureParser

    test_input = """
    architecture
        group api(cloud)[API]

        service db(database)[Database] in api
        service disk1(disk)[Storage] in api
        service disk2(disk)[Storage] in api
        service server(server)[Server] in api

        db:L -- R:server
        disk1:T -- B:server
        disk2:T -- B:db
    """

    parser = ArchitectureParser()
    diagram = parser.parse(test_input)

    layout = ArchitectureLayout()
    layout.layout(diagram)

    print("\nLayout Results:")
    for s in diagram.services.values():
        print(f"  {s.id}: ({s.x:.0f}, {s.y:.0f})")
    for g in diagram.groups.values():
        print(f"  Group {g.id}: ({g.x:.0f}, {g.y:.0f}) {g.width:.0f}x{g.height:.0f}")
