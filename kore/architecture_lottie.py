"""
Lottie Renderer for Architecture Diagrams

Converts parsed and laid out architecture diagrams to Lottie JSON format
with animated arrows.
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from architecture_parser import ArchitectureDiagram, Direction, Service, Group, Edge, Layer


@dataclass
class LottieConfig:
    """Lottie output configuration"""
    width: int = 800
    height: int = 600
    fps: int = 60
    duration_seconds: float = 2.0
    background_color: str = "#2B2B2B"

    # Colors (normalized 0-1 for Lottie)
    colors: Dict[str, List[float]] = None

    def __post_init__(self):
        if self.colors is None:
            # ByteByteGo theme defaults
            self.colors = {
                'background': [0.169, 0.169, 0.169],
                'cloud': [0.239, 0.239, 0.239],
                'cloud_stroke': [0.306, 0.804, 0.769],  # Teal
                'server': [0.365, 0.678, 0.886],  # Blue
                'database': [0.0, 0.851, 0.647],  # Green
                'disk': [0.851, 0.275, 0.937],  # Purple
                'arrow': [1.0, 0.420, 0.420],  # Coral
                'text': [1.0, 1.0, 1.0],  # White
                'text_secondary': [0.690, 0.690, 0.690],
                # New icon colors
                'brain': [0.988, 0.549, 0.675],  # Pink/coral for AI
                'neural': [0.988, 0.549, 0.675],
                'ai': [0.988, 0.549, 0.675],
                'api': [0.365, 0.678, 0.886],  # Blue
                'sensor': [0.565, 0.792, 0.976],  # Light blue
                'logs': [0.565, 0.792, 0.976],
                'search': [0.565, 0.792, 0.976],
                'query': [0.565, 0.792, 0.976],
                'wifi': [0.306, 0.804, 0.769],  # Teal
                'globe': [0.306, 0.804, 0.769],
                'web': [0.306, 0.804, 0.769],
                'gear': [0.988, 0.773, 0.318],  # Yellow/gold
                'cog': [0.988, 0.773, 0.318],
                'settings': [0.988, 0.773, 0.318],
                'tools': [0.988, 0.773, 0.318],
                'lightbulb': [0.988, 0.867, 0.318],  # Bright yellow
                'idea': [0.988, 0.867, 0.318],
                'output': [0.565, 0.792, 0.976],
                'decision': [0.988, 0.773, 0.318],
                'loop': [0.565, 0.792, 0.976],
                'error': [1.0, 0.420, 0.420],  # Red/coral
                'check': [0.0, 0.851, 0.647],  # Green
                # Layer colors
                'layer_input': [0.298, 0.475, 0.329],  # Green
                'layer_process': [0.227, 0.318, 0.502],  # Blue
                'layer_action': [0.988, 0.773, 0.318],  # Yellow
                'layer_output': [0.400, 0.318, 0.600],  # Purple
            }


class LottieRenderer:
    """Render architecture diagram to Lottie JSON"""

    # Icon to color mapping
    ICON_COLORS = {
        'server': 'server',
        'database': 'database',
        'disk': 'disk',
        'storage': 'disk',
        'cloud': 'cloud_stroke',
        # AI/ML icons
        'brain': 'brain',
        'neural': 'neural',
        'ai': 'ai',
        # Data icons
        'api': 'api',
        'sensor': 'sensor',
        'logs': 'logs',
        'search': 'search',
        'query': 'query',
        # Communication icons
        'wifi': 'wifi',
        'globe': 'globe',
        'web': 'web',
        # Process icons
        'gear': 'gear',
        'cog': 'cog',
        'settings': 'settings',
        'tools': 'tools',
        # Action icons
        'lightbulb': 'lightbulb',
        'idea': 'idea',
        'output': 'output',
        'decision': 'decision',
        'loop': 'loop',
        'error': 'error',
        'check': 'check',
    }

    def __init__(self, config: Optional[LottieConfig] = None):
        self.config = config or LottieConfig()
        self.layer_idx = 1
        self.assets = []

    def render(self, diagram: ArchitectureDiagram) -> Dict:
        """Render diagram to Lottie JSON"""
        cfg = self.config
        duration_frames = int(cfg.fps * cfg.duration_seconds)

        layers = []
        self.layer_idx = 1

        # Render arrows first (behind other elements)
        for edge in diagram.edges:
            layer = self._render_arrow(edge, diagram, duration_frames)
            if layer:
                layers.append(layer)

        # Render groups
        for group in diagram.groups.values():
            layer = self._render_group(group, duration_frames)
            layers.append(layer)

        # Render layer labels FIRST (so they appear on top of layer boxes)
        for arch_layer in diagram.layers.values():
            if arch_layer.label:
                layer = self._render_layer_label(arch_layer, duration_frames)
                layers.append(layer)

        # Render layer boxes (behind labels)
        for arch_layer in diagram.layers.values():
            layer = self._render_layer(arch_layer, duration_frames)
            layers.append(layer)

        # Render service icons FIRST (in Lottie, first layer = top, so icons need to be before boxes)
        for service in diagram.services.values():
            icon_layer = self._render_service_icon(service, duration_frames)
            if icon_layer:
                layers.append(icon_layer)

        # Render services (boxes) AFTER icons so boxes are below icons
        for service in diagram.services.values():
            layer = self._render_service(service, duration_frames)
            layers.append(layer)

        # Render labels
        for service in diagram.services.values():
            if service.label:
                layer = self._render_label(service, duration_frames)
                layers.append(layer)

        for group in diagram.groups.values():
            if group.label:
                layer = self._render_group_label(group, duration_frames)
                layers.append(layer)

        # Background layer (last = bottom)
        layers.append(self._render_background(duration_frames))

        # Build Lottie JSON
        lottie = {
            "v": "5.7.4",
            "fr": cfg.fps,
            "ip": 0,
            "op": duration_frames,
            "w": cfg.width,
            "h": cfg.height,
            "nm": "Architecture Diagram",
            "ddd": 0,
            "assets": self.assets,
            "fonts": {
                "list": [
                    {
                        "fName": "Arial",
                        "fFamily": "Arial",
                        "fStyle": "Regular",
                        "ascent": 71.5988159179688
                    }
                ]
            },
            "layers": layers
        }

        return lottie

    def _get_color(self, icon: Optional[str]) -> List[float]:
        """Get color for icon type"""
        if icon and icon in self.ICON_COLORS:
            color_key = self.ICON_COLORS[icon]
            return self.config.colors.get(color_key, self.config.colors['server'])
        return self.config.colors['server']

    def _render_service(self, service: Service, duration_frames: int) -> Dict:
        """Render a service node box only (icons rendered separately)"""
        color = self._get_color(service.icon) + [1]  # Add alpha

        # Just the box - icons are rendered as separate layers
        shapes = [
            {
                "ty": "gr",
                "it": [
                    {
                        "ty": "rc",
                        "s": {"a": 0, "k": [service.width, service.height]},
                        "p": {"a": 0, "k": [0, 0]},
                        "r": {"a": 0, "k": 8}
                    },
                    {"ty": "fl", "c": {"a": 0, "k": color}, "o": {"a": 0, "k": 100}},
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "Box"
            }
        ]

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 4,
            "nm": service.id,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [service.x, service.y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": shapes,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_service_icon(self, service: Service, duration_frames: int) -> Optional[Dict]:
        """Render service icon as a separate layer on top of the service box"""
        white = [1, 1, 1, 1]  # RGBA white
        shapes = []

        if service.icon == 'server':
            # Server icon: 3 horizontal bars
            server_items = []
            for y_off in [-18, 0, 18]:
                server_items.append({"ty": "rc", "s": {"a": 0, "k": [50, 10]}, "p": {"a": 0, "k": [0, y_off]}, "r": {"a": 0, "k": 2}})
            server_items.extend([
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ])
            shapes.append({"ty": "gr", "it": server_items, "nm": "ServerIcon"})

        elif service.icon == 'database':
            # Database icon: cylinder shape
            db_items = [
                {"ty": "rc", "s": {"a": 0, "k": [44, 35]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0}},
                {"ty": "el", "s": {"a": 0, "k": [44, 14]}, "p": {"a": 0, "k": [0, -18]}},
                {"ty": "el", "s": {"a": 0, "k": [44, 14]}, "p": {"a": 0, "k": [0, 18]}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 60}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": db_items, "nm": "DBIcon"})

        elif service.icon in ['disk', 'storage']:
            # Disk icon: circle with center dot
            disk_items = [
                {"ty": "el", "s": {"a": 0, "k": [45, 45]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 50}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": disk_items, "nm": "DiskPlatter"})
            # Center hub
            shapes.append({
                "ty": "gr",
                "it": [
                    {"ty": "el", "s": {"a": 0, "k": [14, 14]}, "p": {"a": 0, "k": [0, 0]}},
                    {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 100}},
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "DiskHub"
            })

        elif service.icon in ['brain', 'neural', 'ai']:
            # Brain icon: wavy shape
            brain_items = [
                {"ty": "el", "s": {"a": 0, "k": [40, 35]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "el", "s": {"a": 0, "k": [20, 18]}, "p": {"a": 0, "k": [-12, -8]}},
                {"ty": "el", "s": {"a": 0, "k": [20, 18]}, "p": {"a": 0, "k": [12, -8]}},
                {"ty": "el", "s": {"a": 0, "k": [16, 14]}, "p": {"a": 0, "k": [0, 12]}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": brain_items, "nm": "BrainIcon"})

        elif service.icon in ['gear', 'cog', 'settings']:
            # Gear icon: circle with teeth
            gear_items = [
                {"ty": "el", "s": {"a": 0, "k": [30, 30]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "rc", "s": {"a": 0, "k": [10, 44]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 2}},
                {"ty": "rc", "s": {"a": 0, "k": [44, 10]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 2}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": gear_items, "nm": "GearIcon"})

        elif service.icon in ['lightbulb', 'idea']:
            # Lightbulb icon
            bulb_items = [
                {"ty": "el", "s": {"a": 0, "k": [35, 35]}, "p": {"a": 0, "k": [0, -5]}},
                {"ty": "rc", "s": {"a": 0, "k": [20, 15]}, "p": {"a": 0, "k": [0, 15]}, "r": {"a": 0, "k": 3}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 80}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": bulb_items, "nm": "LightbulbIcon"})

        elif service.icon == 'api':
            # API icon: brackets < >
            api_items = [
                {"ty": "rc", "s": {"a": 0, "k": [45, 30]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 4}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 60}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": api_items, "nm": "APIIcon"})

        elif service.icon in ['search', 'query']:
            # Search icon: circle with handle
            search_items = [
                {"ty": "el", "s": {"a": 0, "k": [32, 32]}, "p": {"a": 0, "k": [-5, -5]}},
                {"ty": "rc", "s": {"a": 0, "k": [8, 20]}, "p": {"a": 0, "k": [12, 12]}, "r": {"a": 0, "k": 3}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": search_items, "nm": "SearchIcon"})

        elif service.icon in ['wifi', 'sensor']:
            # Wifi icon: arcs
            wifi_items = [
                {"ty": "el", "s": {"a": 0, "k": [12, 12]}, "p": {"a": 0, "k": [0, 10]}},
                {"ty": "el", "s": {"a": 0, "k": [30, 20]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "el", "s": {"a": 0, "k": [45, 30]}, "p": {"a": 0, "k": [0, -8]}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 60}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": wifi_items, "nm": "WifiIcon"})

        elif service.icon in ['globe', 'web']:
            # Globe icon: circle with lines
            globe_items = [
                {"ty": "el", "s": {"a": 0, "k": [40, 40]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "el", "s": {"a": 0, "k": [20, 40]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "rc", "s": {"a": 0, "k": [40, 2]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 0}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 60}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": globe_items, "nm": "GlobeIcon"})

        elif service.icon == 'logs':
            # Logs icon: stacked lines
            logs_items = []
            for y_off in [-12, -4, 4, 12]:
                logs_items.append({"ty": "rc", "s": {"a": 0, "k": [40, 6]}, "p": {"a": 0, "k": [0, y_off]}, "r": {"a": 0, "k": 2}})
            logs_items.extend([
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ])
            shapes.append({"ty": "gr", "it": logs_items, "nm": "LogsIcon"})

        elif service.icon in ['tools', 'decision']:
            # Tools/wrench icon
            tools_items = [
                {"ty": "rc", "s": {"a": 0, "k": [12, 40]}, "p": {"a": 0, "k": [-8, 0]}, "r": {"a": 0, "k": 3}},
                {"ty": "rc", "s": {"a": 0, "k": [12, 40]}, "p": {"a": 0, "k": [8, 0]}, "r": {"a": 0, "k": 3}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": tools_items, "nm": "ToolsIcon"})

        elif service.icon == 'loop':
            # Loop/cycle icon: circular arrow
            loop_items = [
                {"ty": "el", "s": {"a": 0, "k": [38, 38]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "rc", "s": {"a": 0, "k": [12, 12]}, "p": {"a": 0, "k": [19, 0]}, "r": {"a": 0, "k": 0}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": loop_items, "nm": "LoopIcon"})

        elif service.icon == 'error':
            # Error icon: X mark
            error_items = [
                {"ty": "rc", "s": {"a": 0, "k": [8, 45]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 2}},
                {"ty": "rc", "s": {"a": 0, "k": [45, 8]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 2}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 80}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 45}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": error_items, "nm": "ErrorIcon"})

        elif service.icon == 'check':
            # Check icon: checkmark
            check_items = [
                {"ty": "el", "s": {"a": 0, "k": [40, 40]}, "p": {"a": 0, "k": [0, 0]}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": check_items, "nm": "CheckIcon"})

        elif service.icon == 'output':
            # Output icon: arrow pointing out
            output_items = [
                {"ty": "rc", "s": {"a": 0, "k": [35, 30]}, "p": {"a": 0, "k": [0, 0]}, "r": {"a": 0, "k": 4}},
                {"ty": "rc", "s": {"a": 0, "k": [10, 20]}, "p": {"a": 0, "k": [5, 0]}, "r": {"a": 0, "k": 2}},
                {"ty": "fl", "c": {"a": 0, "k": white}, "o": {"a": 0, "k": 70}},
                {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                 "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
            ]
            shapes.append({"ty": "gr", "it": output_items, "nm": "OutputIcon"})

        if not shapes:
            return None

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 4,
            "nm": f"{service.id}_icon",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [service.x, service.y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": shapes,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_group(self, group: Group, duration_frames: int) -> Dict:
        """Render a group container with icon in top-left corner"""
        cfg = self.config
        stroke_color = cfg.colors['cloud_stroke'] + [1]

        # Group box position (top-left corner)
        box_left = group.x - group.width / 2
        box_top = group.y - group.height / 2

        shapes = [
            # Dashed border rectangle (no fill)
            {
                "ty": "gr",
                "it": [
                    {
                        "ty": "rc",
                        "s": {"a": 0, "k": [group.width, group.height]},
                        "p": {"a": 0, "k": [0, 0]},
                        "r": {"a": 0, "k": 8}
                    },
                    {
                        "ty": "st",
                        "c": {"a": 0, "k": stroke_color},
                        "o": {"a": 0, "k": 60},
                        "w": {"a": 0, "k": 2},
                        "d": [
                            {"n": "d", "nm": "dash", "v": {"a": 0, "k": 8}},
                            {"n": "g", "nm": "gap", "v": {"a": 0, "k": 5}}
                        ]
                    },
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "Border"
            }
        ]

        # Add cloud icon in top-left if icon is 'cloud'
        if group.icon == 'cloud':
            icon_x = -group.width/2 + 25
            icon_y = -group.height/2 + 20
            # Simple cloud shape
            shapes.append({
                "ty": "gr",
                "it": [
                    # Cloud body (ellipses)
                    {"ty": "el", "s": {"a": 0, "k": [24, 16]}, "p": {"a": 0, "k": [icon_x, icon_y]}},
                    {"ty": "el", "s": {"a": 0, "k": [16, 14]}, "p": {"a": 0, "k": [icon_x - 10, icon_y + 2]}},
                    {"ty": "el", "s": {"a": 0, "k": [14, 12]}, "p": {"a": 0, "k": [icon_x + 10, icon_y + 2]}},
                    {"ty": "fl", "c": {"a": 0, "k": stroke_color}, "o": {"a": 0, "k": 80}},
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "CloudIcon"
            })

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 4,
            "nm": f"Group {group.id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [group.x, group.y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": shapes,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_layer(self, arch_layer: Layer, duration_frames: int) -> Dict:
        """Render a layer label box (left side of layered diagram)"""
        cfg = self.config

        # Determine layer color based on icon/label
        layer_color = cfg.colors.get('layer_process', cfg.colors['server'])
        if arch_layer.icon:
            if 'input' in arch_layer.icon.lower():
                layer_color = cfg.colors['layer_input']
            elif 'process' in arch_layer.icon.lower():
                layer_color = cfg.colors['layer_process']
            elif 'action' in arch_layer.icon.lower():
                layer_color = cfg.colors['layer_action']
            elif 'output' in arch_layer.icon.lower():
                layer_color = cfg.colors['layer_output']

        fill_color = layer_color + [1]

        shapes = [
            {
                "ty": "gr",
                "it": [
                    {
                        "ty": "rc",
                        "s": {"a": 0, "k": [arch_layer.width, arch_layer.height]},
                        "p": {"a": 0, "k": [0, 0]},
                        "r": {"a": 0, "k": 8}
                    },
                    {"ty": "fl", "c": {"a": 0, "k": fill_color}, "o": {"a": 0, "k": 100}},
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                     "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "LayerBox"
            }
        ]

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 4,
            "nm": f"Layer {arch_layer.id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [arch_layer.x, arch_layer.y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": shapes,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_layer_label(self, arch_layer: Layer, duration_frames: int) -> Dict:
        """Render layer label text"""
        text_color = self.config.colors['text']

        # Split label into two lines for better fit
        label_text = arch_layer.label if arch_layer.label else ""
        if " " in label_text:
            words = label_text.split()
            if len(words) == 2:
                label_text = words[0] + "\n" + words[1]

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 5,
            "nm": f"LayerLabel {arch_layer.id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [arch_layer.x, arch_layer.y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "t": {
                "d": {
                    "k": [{
                        "s": {
                            "sz": [90, 60],
                            "ps": [-45, -20],
                            "s": 11,
                            "f": "Arial",
                            "t": label_text,
                            "ca": 0,
                            "j": 2,  # Center align
                            "tr": 0,
                            "lh": 14,
                            "ls": 0,
                            "fc": text_color
                        },
                        "t": 0
                    }]
                },
                "p": {},
                "m": {"g": 1, "a": {"a": 0, "k": [0, 0]}},
                "a": []
            },
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_arrow(self, edge: Edge, diagram: ArchitectureDiagram, duration_frames: int) -> Optional[Dict]:
        """Render animated arrow edge"""
        source = diagram.get_node(edge.source_id)
        target = diagram.get_node(edge.target_id)

        if not source or not target:
            return None

        # Calculate start/end points based on direction ports
        start = self._get_port_position(source, edge.source_dir)
        end = self._get_port_position(target, edge.target_dir)

        # Arrow color
        arrow_color = self.config.colors['arrow'] + [1]

        # Calculate arrowhead
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx**2 + dy**2) ** 0.5

        if length > 0:
            nx, ny = dx/length, dy/length
        else:
            nx, ny = 1, 0

        # Shorten for arrowhead
        arrow_end = [end[0] - nx*15, end[1] - ny*15]

        # Arrowhead points
        perp_x, perp_y = -ny, nx
        head_size = 10
        head1 = [end[0] - nx*18 + perp_x*head_size, end[1] - ny*18 + perp_y*head_size]
        head2 = [end[0] - nx*18 - perp_x*head_size, end[1] - ny*18 - perp_y*head_size]

        # Dash animation
        dash_size = 8
        gap_size = 4
        pattern_length = dash_size + gap_size

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 4,
            "nm": f"Arrow {edge.source_id}-{edge.target_id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [0, 0, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": [
                # Arrow line
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": False,
                                    "v": [start, arrow_end],
                                    "i": [[0, 0], [0, 0]],
                                    "o": [[0, 0], [0, 0]]
                                }
                            }
                        },
                        {
                            "ty": "st",
                            "c": {"a": 0, "k": arrow_color},
                            "o": {"a": 0, "k": 100},
                            "w": {"a": 0, "k": 3},
                            "lc": 2,
                            "lj": 2,
                            "d": [
                                {"n": "d", "nm": "dash", "v": {"a": 0, "k": dash_size}},
                                {"n": "g", "nm": "gap", "v": {"a": 0, "k": gap_size}},
                                {
                                    "n": "o",
                                    "nm": "offset",
                                    "v": {
                                        "a": 1,
                                        "k": [
                                            {
                                                "t": 0,
                                                "s": [0],
                                                "i": {"x": [0.167], "y": [0.167]},
                                                "o": {"x": [0.167], "y": [0.167]}
                                            },
                                            {
                                                "t": duration_frames - 1,
                                                "s": [-pattern_length * 10]
                                            }
                                        ]
                                    }
                                }
                            ]
                        },
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                         "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Line"
                },
                # Arrowhead
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": True,
                                    "v": [end, head1, head2],
                                    "i": [[0, 0], [0, 0], [0, 0]],
                                    "o": [[0, 0], [0, 0], [0, 0]]
                                }
                            }
                        },
                        {"ty": "fl", "c": {"a": 0, "k": arrow_color}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]},
                         "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Head"
                }
            ],
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _get_port_position(self, node, direction: Direction) -> List[float]:
        """Get connection port position on node edge"""
        offset = 5
        if direction == Direction.LEFT:
            return [node.x - node.width/2 - offset, node.y]
        elif direction == Direction.RIGHT:
            return [node.x + node.width/2 + offset, node.y]
        elif direction == Direction.TOP:
            return [node.x, node.y - node.height/2 - offset]
        elif direction == Direction.BOTTOM:
            return [node.x, node.y + node.height/2 + offset]
        return [node.x, node.y]

    def _render_label(self, service: Service, duration_frames: int) -> Dict:
        """Render service label"""
        text_color = self.config.colors['text']

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 5,
            "nm": f"Label {service.id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [service.x, service.y + service.height/2 + 20, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "t": {
                "d": {
                    "k": [{
                        "s": {
                            "sz": [150, 30],
                            "ps": [-75, -10],
                            "s": 13,
                            "f": "Arial",
                            "t": service.label,
                            "ca": 0,
                            "j": 2,
                            "tr": 0,
                            "lh": 16,
                            "ls": 0,
                            "fc": text_color
                        },
                        "t": 0
                    }]
                },
                "p": {},
                "m": {"g": 1, "a": {"a": 0, "k": [0, 0]}},
                "a": []
            },
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_group_label(self, group: Group, duration_frames: int) -> Dict:
        """Render group label next to icon in top-left"""
        text_color = self.config.colors['cloud_stroke']

        # Position label next to cloud icon (top-left)
        label_x = group.x - group.width/2 + 55  # After cloud icon
        label_y = group.y - group.height/2 + 22

        layer = {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 5,
            "nm": f"Label {group.id}",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [label_x, label_y, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "t": {
                "d": {
                    "k": [{
                        "s": {
                            "sz": [200, 30],
                            "ps": [0, -10],
                            "s": 16,
                            "f": "Arial",
                            "t": group.label,
                            "ca": 0,
                            "j": 0,  # Left align
                            "tr": 0,
                            "lh": 20,
                            "ls": 0,
                            "fc": text_color
                        },
                        "t": 0
                    }]
                },
                "p": {},
                "m": {"g": 1, "a": {"a": 0, "k": [0, 0]}},
                "a": []
            },
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

        self.layer_idx += 1
        return layer

    def _render_background(self, duration_frames: int) -> Dict:
        """Render background layer"""
        cfg = self.config

        return {
            "ddd": 0,
            "ind": self.layer_idx,
            "ty": 1,
            "nm": "Background",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [cfg.width/2, cfg.height/2, 0]},
                "a": {"a": 0, "k": [cfg.width/2, cfg.height/2, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "sw": cfg.width,
            "sh": cfg.height,
            "sc": cfg.background_color,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }


def render_to_lottie(diagram: ArchitectureDiagram, config: Optional[LottieConfig] = None) -> Dict:
    """Convenience function to render diagram to Lottie"""
    renderer = LottieRenderer(config)
    return renderer.render(diagram)


if __name__ == '__main__':
    from architecture_parser import ArchitectureParser
    from architecture_layout import ArchitectureLayout

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

    # Parse
    parser = ArchitectureParser()
    diagram = parser.parse(test_input)

    # Layout
    layout = ArchitectureLayout()
    layout.layout(diagram)

    # Render to Lottie
    lottie = render_to_lottie(diagram)

    # Save
    with open('test_output.json', 'w') as f:
        json.dump(lottie, f, indent=2)

    print("Generated test_output.json")
