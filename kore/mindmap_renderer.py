"""
Mindmap SVG Renderer

Uses a simple horizontal tree layout algorithm inspired by Reingold-Tilford.
Root is centered, children spread left and right.
"""

from dataclasses import dataclass
from kore_parser import MindmapNode, Mindmap


@dataclass
class LayoutNode:
    """Node with calculated position"""
    text: str
    x: float = 0
    y: float = 0
    width: float = 0
    height: float = 0
    children: list = None
    depth: int = 0

    def __post_init__(self):
        if self.children is None:
            self.children = []


# Layout constants
NODE_PADDING_X = 16
NODE_PADDING_Y = 8
NODE_HEIGHT = 32
CHAR_WIDTH = 8
LEVEL_GAP_X = 40
SIBLING_GAP_Y = 16
MIN_NODE_WIDTH = 60

# Colors by depth
COLORS = [
    "#3B82F6",  # blue - root
    "#10B981",  # green
    "#F59E0B",  # amber
    "#EF4444",  # red
    "#8B5CF6",  # purple
    "#EC4899",  # pink
]


def get_node_width(text: str) -> float:
    """Calculate node width based on text length"""
    return max(MIN_NODE_WIDTH, len(text) * CHAR_WIDTH + NODE_PADDING_X * 2)


def build_layout_tree(node: MindmapNode, depth: int = 0) -> LayoutNode:
    """Convert MindmapNode to LayoutNode with dimensions"""
    layout = LayoutNode(
        text=node.text,
        depth=depth,
        width=get_node_width(node.text),
        height=NODE_HEIGHT,
    )
    for child in node.children:
        layout.children.append(build_layout_tree(child, depth + 1))
    return layout


def calculate_subtree_height(node: LayoutNode) -> float:
    """Calculate total height of a subtree"""
    if not node.children:
        return node.height

    total = sum(calculate_subtree_height(c) for c in node.children)
    total += SIBLING_GAP_Y * (len(node.children) - 1)
    return max(node.height, total)


def layout_subtree(node: LayoutNode, x: float, y: float, direction: int = 1):
    """
    Layout a subtree starting from (x, y).
    direction: 1 = right, -1 = left
    """
    node.x = x
    node.y = y

    if not node.children:
        return

    # Calculate total height of children
    total_height = sum(calculate_subtree_height(c) for c in node.children)
    total_height += SIBLING_GAP_Y * (len(node.children) - 1)

    # Start position for children (centered vertically relative to parent)
    child_y = y - total_height / 2 + calculate_subtree_height(node.children[0]) / 2

    for child in node.children:
        # Gap is between edges, not centers
        if direction > 0:
            child_x = x + node.width / 2 + LEVEL_GAP_X + child.width / 2
        else:
            child_x = x - node.width / 2 - LEVEL_GAP_X - child.width / 2

        subtree_h = calculate_subtree_height(child)
        layout_subtree(child, child_x, child_y, direction)
        child_y += subtree_h + SIBLING_GAP_Y


def layout_mindmap(mindmap: Mindmap, width: float, height: float) -> LayoutNode:
    """
    Layout mindmap with root in center.
    Children split left and right.
    """
    root = build_layout_tree(mindmap.root)

    # Position root at center
    root.x = width / 2
    root.y = height / 2

    if not root.children:
        return root

    # Split children: odd indices go left, even go right
    left_children = root.children[1::2]
    right_children = root.children[::2]

    # Layout right children
    if right_children:
        total_h = sum(calculate_subtree_height(c) for c in right_children)
        total_h += SIBLING_GAP_Y * (len(right_children) - 1)

        child_y = root.y - total_h / 2 + calculate_subtree_height(right_children[0]) / 2

        for child in right_children:
            # Gap is between edges
            child_x = root.x + root.width / 2 + LEVEL_GAP_X + child.width / 2
            subtree_h = calculate_subtree_height(child)
            layout_subtree(child, child_x, child_y, direction=1)
            child_y += subtree_h + SIBLING_GAP_Y

    # Layout left children
    if left_children:
        total_h = sum(calculate_subtree_height(c) for c in left_children)
        total_h += SIBLING_GAP_Y * (len(left_children) - 1)

        child_y = root.y - total_h / 2 + calculate_subtree_height(left_children[0]) / 2

        for child in left_children:
            # Gap is between edges
            child_x = root.x - root.width / 2 - LEVEL_GAP_X - child.width / 2
            subtree_h = calculate_subtree_height(child)
            layout_subtree(child, child_x, child_y, direction=-1)
            child_y += subtree_h + SIBLING_GAP_Y

    return root


def collect_connectors(node: LayoutNode, parent: LayoutNode = None) -> list:
    """Collect all connectors (draw first, behind nodes)"""
    connectors = []
    color = COLORS[node.depth % len(COLORS)]

    if parent is not None:
        # Connect from edge of parent to edge of child
        if node.x > parent.x:
            # Child is to the right
            start_x = parent.x + parent.width / 2
            end_x = node.x - node.width / 2
        else:
            # Child is to the left
            start_x = parent.x - parent.width / 2
            end_x = node.x + node.width / 2

        mid_x = (start_x + end_x) / 2
        connectors.append(
            f'<path d="M {start_x} {parent.y} C {mid_x} {parent.y}, {mid_x} {node.y}, {end_x} {node.y}" '
            f'stroke="{color}" stroke-width="2" fill="none" opacity="0.6"/>'
        )

    for child in node.children:
        connectors.extend(collect_connectors(child, node))

    return connectors


def collect_nodes(node: LayoutNode) -> list:
    """Collect all nodes (draw after connectors)"""
    nodes = []
    color = COLORS[node.depth % len(COLORS)]

    rx = 6
    x = node.x - node.width / 2
    y = node.y - node.height / 2

    # Node rectangle
    nodes.append(
        f'<rect x="{x}" y="{y}" width="{node.width}" height="{node.height}" '
        f'rx="{rx}" fill="{color}"/>'
    )

    # Text
    nodes.append(
        f'<text x="{node.x}" y="{node.y + 5}" '
        f'text-anchor="middle" fill="white" font-family="system-ui, sans-serif" '
        f'font-size="14" font-weight="500">{node.text}</text>'
    )

    for child in node.children:
        nodes.extend(collect_nodes(child))

    return nodes


def render_mindmap_svg(mindmap: Mindmap, width: int = 800, height: int = 600) -> str:
    """Render mindmap as SVG string"""
    root = layout_mindmap(mindmap, width, height)

    # Collect connectors and nodes separately
    connectors = collect_connectors(root)
    nodes = collect_nodes(root)

    # Draw connectors first (behind), then nodes (front)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    text {{ user-select: none; }}
  </style>
  <rect width="100%" height="100%" fill="#1a1a2e"/>
  <g>
{chr(10).join(connectors)}
{chr(10).join(nodes)}
  </g>
</svg>'''

    return svg


def save_mindmap_svg(mindmap: Mindmap, filename: str, width: int = 800, height: int = 600):
    """Save mindmap to SVG file"""
    svg = render_mindmap_svg(mindmap, width, height)
    with open(filename, 'w') as f:
        f.write(svg)
    print(f"Saved: {filename}")
