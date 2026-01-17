"""
Parser for Mermaid Architecture Diagram Syntax

Syntax:
    architecture-beta
    group {id}({icon})[{label}] (in {parent})?
    service {id}({icon})[{label}] (in {parent})?
    junction {id} (in {parent})?
    {id}:{dir} -- {dir}:{id}
    {id}:{dir} --> {dir}:{id}
"""

import re
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from enum import Enum


class Direction(Enum):
    LEFT = 'L'
    RIGHT = 'R'
    TOP = 'T'
    BOTTOM = 'B'


# Supported icons
ICONS = {
    # Infrastructure
    'cloud', 'server', 'database', 'disk', 'storage',
    # AI/ML
    'brain', 'neural', 'ai',
    # Data
    'api', 'sensor', 'logs', 'search', 'query',
    # Communication
    'wifi', 'globe', 'web',
    # Process
    'gear', 'cog', 'settings', 'tools',
    # Actions
    'lightbulb', 'idea', 'output',
    # Flow
    'decision', 'loop', 'error', 'check',
    # Generic
    'box', 'node',
}


@dataclass
class Layer:
    """Horizontal layer for flow diagrams"""
    id: str
    icon: Optional[str] = None
    label: Optional[str] = None
    order: int = 0  # Vertical order (0 = top)
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


@dataclass
class Group:
    id: str
    icon: Optional[str] = None
    label: Optional[str] = None
    parent: Optional[str] = None
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0


@dataclass
class Service:
    id: str
    icon: Optional[str] = None
    label: Optional[str] = None
    parent: Optional[str] = None
    x: float = 0
    y: float = 0
    width: float = 80
    height: float = 80


@dataclass
class Junction:
    id: str
    parent: Optional[str] = None
    x: float = 0
    y: float = 0
    width: float = 20
    height: float = 20


@dataclass
class Edge:
    source_id: str
    source_dir: Direction
    target_id: str
    target_dir: Direction
    label: Optional[str] = None
    has_arrow: bool = True


@dataclass
class ArchitectureDiagram:
    groups: Dict[str, Group] = field(default_factory=dict)
    services: Dict[str, Service] = field(default_factory=dict)
    junctions: Dict[str, Junction] = field(default_factory=dict)
    edges: List[Edge] = field(default_factory=list)
    layers: Dict[str, Layer] = field(default_factory=dict)

    def get_node(self, node_id: str):
        """Get any node by ID"""
        if node_id in self.services:
            return self.services[node_id]
        if node_id in self.junctions:
            return self.junctions[node_id]
        if node_id in self.groups:
            return self.groups[node_id]
        if node_id in self.layers:
            return self.layers[node_id]
        return None

    def get_children(self, parent_id: str) -> List[str]:
        """Get all children of a group or layer"""
        children = []
        for s in self.services.values():
            if s.parent == parent_id:
                children.append(s.id)
        for j in self.junctions.values():
            if j.parent == parent_id:
                children.append(j.id)
        for g in self.groups.values():
            if g.parent == parent_id:
                children.append(g.id)
        return children

    def is_layered(self) -> bool:
        """Check if this is a layered diagram"""
        return len(self.layers) > 0

    def get_layers_ordered(self) -> List[Layer]:
        """Get layers in order"""
        return sorted(self.layers.values(), key=lambda l: l.order)


class ArchitectureParser:
    """Parser for Mermaid Architecture Diagram syntax"""

    # Regex patterns
    PATTERN_LAYER = re.compile(
        r'layer\s+(\w+)(?:\(([^)]+)\))?(?:\[([^\]]+)\])?'
    )
    PATTERN_GROUP = re.compile(
        r'group\s+(\w+)(?:\(([^)]+)\))?(?:\[([^\]]+)\])?(?:\s+in\s+(\w+))?'
    )
    PATTERN_SERVICE = re.compile(
        r'service\s+(\w+)(?:\(([^)]+)\))?(?:\[([^\]]+)\])?(?:\s+in\s+(\w+))?'
    )
    PATTERN_JUNCTION = re.compile(
        r'junction\s+(\w+)(?:\s+in\s+(\w+))?'
    )
    PATTERN_EDGE = re.compile(
        r'(\w+):([LRTB])\s*(--?>?)\s*([LRTB]):(\w+)'
    )

    def parse(self, text: str) -> ArchitectureDiagram:
        """Parse architecture diagram text"""
        diagram = ArchitectureDiagram()
        layer_order = 0

        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Skip diagram type declaration
            if line.startswith('architecture'):
                continue

            # Try to match each pattern
            if self._parse_layer(line, diagram, layer_order):
                layer_order += 1
                continue
            if self._parse_group(line, diagram):
                continue
            if self._parse_service(line, diagram):
                continue
            if self._parse_junction(line, diagram):
                continue
            if self._parse_edge(line, diagram):
                continue

        return diagram

    def _parse_layer(self, line: str, diagram: ArchitectureDiagram, order: int) -> bool:
        match = self.PATTERN_LAYER.match(line)
        if match:
            id_, icon, label = match.groups()
            diagram.layers[id_] = Layer(
                id=id_,
                icon=icon,
                label=label,
                order=order
            )
            return True
        return False

    def _parse_group(self, line: str, diagram: ArchitectureDiagram) -> bool:
        match = self.PATTERN_GROUP.match(line)
        if match:
            id_, icon, label, parent = match.groups()
            diagram.groups[id_] = Group(
                id=id_,
                icon=icon,
                label=label,
                parent=parent
            )
            return True
        return False

    def _parse_service(self, line: str, diagram: ArchitectureDiagram) -> bool:
        match = self.PATTERN_SERVICE.match(line)
        if match:
            id_, icon, label, parent = match.groups()
            diagram.services[id_] = Service(
                id=id_,
                icon=icon,
                label=label,
                parent=parent
            )
            return True
        return False

    def _parse_junction(self, line: str, diagram: ArchitectureDiagram) -> bool:
        match = self.PATTERN_JUNCTION.match(line)
        if match:
            id_, parent = match.groups()
            diagram.junctions[id_] = Junction(
                id=id_,
                parent=parent
            )
            return True
        return False

    def _parse_edge(self, line: str, diagram: ArchitectureDiagram) -> bool:
        match = self.PATTERN_EDGE.match(line)
        if match:
            source_id, source_dir, arrow, target_dir, target_id = match.groups()
            diagram.edges.append(Edge(
                source_id=source_id,
                source_dir=Direction(source_dir),
                target_id=target_id,
                target_dir=Direction(target_dir),
                has_arrow='>' in arrow
            ))
            return True
        return False

    def parse_file(self, filepath: str) -> ArchitectureDiagram:
        """Parse architecture diagram from file"""
        with open(filepath, 'r') as f:
            return self.parse(f.read())


if __name__ == '__main__':
    # Test parsing
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

    print("Groups:", list(diagram.groups.keys()))
    print("Services:", list(diagram.services.keys()))
    print("Edges:", len(diagram.edges))
    for edge in diagram.edges:
        print(f"  {edge.source_id}:{edge.source_dir.value} -> {edge.target_id}:{edge.target_dir.value}")
