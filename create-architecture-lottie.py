#!/usr/bin/env python3
"""
Create Architecture Diagram Lottie Animation
- API cloud group containing: Database, 2 Storage disks, Server
- Animated arrows showing connections
"""

import json

# Load colors from colors.json (ByteByteGo Dark Theme)
with open('colors.json', 'r') as f:
    COLORS = json.load(f)

# SVG icon paths (external reference for proper rendering)
DATABASE_SVG_PATH = "icons/database/"
DATABASE_SVG_FILE = "database.svg"

def create_architecture_lottie():
    """Create architecture diagram with animated arrows"""

    width, height = 800, 600
    fps = 60
    duration_frames = 120  # 2 seconds

    # ByteByteGo Dark Theme Colors (normalized 0-1 for Lottie)
    BG_PRIMARY = COLORS['normalized']['background']['primary']  # [0.169, 0.169, 0.169]
    BG_SECONDARY = COLORS['normalized']['background']['secondary']  # [0.239, 0.239, 0.239]
    ACCENT_GREEN = COLORS['normalized']['accent']['green']  # [0.0, 0.851, 0.647]
    ACCENT_TEAL = COLORS['normalized']['accent']['teal']  # [0.306, 0.804, 0.769]
    ACCENT_CORAL = COLORS['normalized']['accent']['coral']  # [1.0, 0.420, 0.420]
    ACCENT_BLUE = COLORS['normalized']['accent']['blue']  # [0.365, 0.678, 0.886]
    ACCENT_ORANGE = COLORS['normalized']['accent']['orange']  # [0.902, 0.494, 0.133]
    ACCENT_PURPLE = COLORS['normalized']['accent']['purple']  # [0.851, 0.275, 0.937]
    ACCENT_YELLOW = COLORS['normalized']['accent']['yellow']  # [0.957, 0.816, 0.247]
    TEXT_PRIMARY = COLORS['normalized']['text']['primary']  # [1.0, 1.0, 1.0]
    TEXT_SECONDARY = COLORS['normalized']['text']['secondary']  # [0.690, 0.690, 0.690]

    # Mapped colors for architecture elements
    CLOUD_COLOR = BG_SECONDARY + [1]  # Background secondary with alpha
    CLOUD_STROKE = ACCENT_TEAL + [1]  # Teal border
    DB_COLOR = ACCENT_GREEN + [1]  # Green for database
    DISK_COLOR = ACCENT_PURPLE + [1]  # Purple for storage
    SERVER_COLOR = ACCENT_BLUE + [1]  # Blue for server
    ARROW_COLOR = ACCENT_CORAL + [1]  # Coral for arrows

    # Positions (centered layout)
    # Layout:
    #     disk1     disk2
    #       |         |
    #    server  --  db

    server_pos = [280, 350]
    db_pos = [520, 350]
    disk1_pos = [280, 180]
    disk2_pos = [520, 180]

    layers = []

    # Layer index counter
    layer_idx = 1

    # === ANIMATED ARROWS ===

    def create_animated_arrow(start, end, delay_frames, name, idx):
        """Create an arrow with smooth animated dash flow (seamless loop)"""

        # Calculate arrow direction
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = (dx**2 + dy**2) ** 0.5

        # Normalize
        if length > 0:
            nx, ny = dx/length, dy/length
        else:
            nx, ny = 1, 0

        # Shorten arrow slightly for arrowhead
        arrow_end = [end[0] - nx*15, end[1] - ny*15]

        # Arrowhead points
        perp_x, perp_y = -ny, nx  # Perpendicular
        head_size = 12
        head1 = [end[0] - nx*20 + perp_x*head_size, end[1] - ny*20 + perp_y*head_size]
        head2 = [end[0] - nx*20 - perp_x*head_size, end[1] - ny*20 - perp_y*head_size]

        # Dash pattern: 8px dash + 4px gap = 12px total
        # For seamless loop, animate offset by exactly one pattern (12px)
        dash_size = 8
        gap_size = 4
        pattern_length = dash_size + gap_size  # 12px

        return {
            "ddd": 0,
            "ind": idx,
            "ty": 4,
            "nm": name,
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
                            "c": {"a": 0, "k": ARROW_COLOR},
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
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
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
                        {
                            "ty": "fl",
                            "c": {"a": 0, "k": ARROW_COLOR},
                            "o": {"a": 0, "k": 100}
                        },
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Head"
                }
            ],
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

    # Arrow: db:L -- R:server (database left to server right)
    layers.append(create_animated_arrow(
        [db_pos[0] - 50, db_pos[1]],
        [server_pos[0] + 50, server_pos[1]],
        0, "Arrow DB-Server", layer_idx
    ))
    layer_idx += 1

    # Arrow: disk1:T -- B:server (disk1 bottom to server top)
    layers.append(create_animated_arrow(
        [disk1_pos[0], disk1_pos[1] + 40],
        [server_pos[0], server_pos[1] - 50],
        20, "Arrow Disk1-Server", layer_idx
    ))
    layer_idx += 1

    # Arrow: disk2:T -- B:db (disk2 bottom to db top)
    layers.append(create_animated_arrow(
        [disk2_pos[0], disk2_pos[1] + 40],
        [db_pos[0], db_pos[1] - 50],
        40, "Arrow Disk2-DB", layer_idx
    ))
    layer_idx += 1

    # === CLOUD GROUP (API) ===
    cloud_layer = {
        "ddd": 0,
        "ind": layer_idx,
        "ty": 4,
        "nm": "API Cloud",
        "sr": 1,
        "ks": {
            "o": {"a": 0, "k": 100},
            "r": {"a": 0, "k": 0},
            "p": {"a": 0, "k": [width/2, height/2, 0]},
            "a": {"a": 0, "k": [0, 0, 0]},
            "s": {"a": 0, "k": [100, 100, 100]}
        },
        "ao": 0,
        "shapes": [
            {
                "ty": "gr",
                "it": [
                    {
                        "ty": "rc",
                        "s": {"a": 0, "k": [500, 350]},
                        "p": {"a": 0, "k": [0, 20]},
                        "r": {"a": 0, "k": 30}
                    },
                    {
                        "ty": "fl",
                        "c": {"a": 0, "k": CLOUD_COLOR},
                        "o": {"a": 0, "k": 15}  # Very light fill
                    },
                    {
                        "ty": "st",
                        "c": {"a": 0, "k": CLOUD_STROKE},
                        "o": {"a": 0, "k": 100},
                        "w": {"a": 0, "k": 2},
                        "d": [
                            {"n": "d", "nm": "dash", "v": {"a": 0, "k": 10}},
                            {"n": "g", "nm": "gap", "v": {"a": 0, "k": 5}}
                        ]
                    },
                    {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                ],
                "nm": "Cloud Box"
            }
        ],
        "ip": 0,
        "op": duration_frames,
        "st": 0
    }
    layers.append(cloud_layer)
    layer_idx += 1

    # === DATABASE ICON (SVG image) ===
    # Uses icons/database/database.svg as image asset
    def create_database_image_layer(pos, name, idx, asset_id="database_svg"):
        icon_size = 80  # Display size
        return {
            "ddd": 0,
            "ind": idx,
            "ty": 2,  # Image layer
            "nm": name,
            "refId": asset_id,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [pos[0], pos[1], 0]},
                "a": {"a": 0, "k": [32, 32, 0]},  # Anchor at center (SVG is 64x64)
                "s": {"a": 0, "k": [icon_size / 64 * 100, icon_size / 64 * 100, 100]}  # Scale to icon_size
            },
            "ao": 0,
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

    layers.append(create_database_image_layer(db_pos, "Database", layer_idx))
    layer_idx += 1

    # === DISK/STORAGE ICON ===
    def create_disk_icon(pos, name, idx):
        return {
            "ddd": 0,
            "ind": idx,
            "ty": 4,
            "nm": name,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [pos[0], pos[1], 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": [
                # Disk body
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "rc",
                            "s": {"a": 0, "k": [60, 50]},
                            "p": {"a": 0, "k": [0, 0]},
                            "r": {"a": 0, "k": 8}
                        },
                        {"ty": "fl", "c": {"a": 0, "k": DISK_COLOR}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Body"
                },
                # Disk lines
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": False,
                                    "v": [[-20, -10], [20, -10]],
                                    "i": [[0, 0], [0, 0]],
                                    "o": [[0, 0], [0, 0]]
                                }
                            }
                        },
                        {"ty": "st", "c": {"a": 0, "k": BG_PRIMARY + [1]}, "o": {"a": 0, "k": 100}, "w": {"a": 0, "k": 2}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Line1"
                },
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": False,
                                    "v": [[-20, 0], [20, 0]],
                                    "i": [[0, 0], [0, 0]],
                                    "o": [[0, 0], [0, 0]]
                                }
                            }
                        },
                        {"ty": "st", "c": {"a": 0, "k": BG_PRIMARY + [1]}, "o": {"a": 0, "k": 100}, "w": {"a": 0, "k": 2}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Line2"
                },
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": False,
                                    "v": [[-20, 10], [20, 10]],
                                    "i": [[0, 0], [0, 0]],
                                    "o": [[0, 0], [0, 0]]
                                }
                            }
                        },
                        {"ty": "st", "c": {"a": 0, "k": BG_PRIMARY + [1]}, "o": {"a": 0, "k": 100}, "w": {"a": 0, "k": 2}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Line3"
                }
            ],
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

    layers.append(create_disk_icon(disk1_pos, "Storage 1", layer_idx))
    layer_idx += 1
    layers.append(create_disk_icon(disk2_pos, "Storage 2", layer_idx))
    layer_idx += 1

    # === SERVER ICON ===
    def create_server_icon(pos, name, idx):
        return {
            "ddd": 0,
            "ind": idx,
            "ty": 4,
            "nm": name,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [pos[0], pos[1], 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": [
                # Server body
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "rc",
                            "s": {"a": 0, "k": [70, 80]},
                            "p": {"a": 0, "k": [0, 0]},
                            "r": {"a": 0, "k": 5}
                        },
                        {"ty": "fl", "c": {"a": 0, "k": SERVER_COLOR}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Body"
                },
                # Server slots
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "rc",
                            "s": {"a": 0, "k": [50, 12]},
                            "p": {"a": 0, "k": [0, -25]},
                            "r": {"a": 0, "k": 2}
                        },
                        {"ty": "fl", "c": {"a": 0, "k": BG_SECONDARY + [1]}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Slot1"
                },
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "rc",
                            "s": {"a": 0, "k": [50, 12]},
                            "p": {"a": 0, "k": [0, -5]},
                            "r": {"a": 0, "k": 2}
                        },
                        {"ty": "fl", "c": {"a": 0, "k": BG_SECONDARY + [1]}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Slot2"
                },
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "rc",
                            "s": {"a": 0, "k": [50, 12]},
                            "p": {"a": 0, "k": [0, 15]},
                            "r": {"a": 0, "k": 2}
                        },
                        {"ty": "fl", "c": {"a": 0, "k": BG_SECONDARY + [1]}, "o": {"a": 0, "k": 100}},
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "Slot3"
                },
                # Blinking LED
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "el",
                            "s": {"a": 0, "k": [8, 8]},
                            "p": {"a": 0, "k": [25, 30]}
                        },
                        {
                            "ty": "fl",
                            "c": {"a": 0, "k": ACCENT_GREEN + [1]},
                            "o": {
                                "a": 1,
                                "k": [
                                    {"t": 0, "s": [100], "i": {"x": [0.5], "y": [1]}, "o": {"x": [0.5], "y": [0]}},
                                    {"t": 30, "s": [30], "i": {"x": [0.5], "y": [1]}, "o": {"x": [0.5], "y": [0]}},
                                    {"t": 60, "s": [100], "i": {"x": [0.5], "y": [1]}, "o": {"x": [0.5], "y": [0]}},
                                    {"t": 90, "s": [30], "i": {"x": [0.5], "y": [1]}, "o": {"x": [0.5], "y": [0]}},
                                    {"t": 120, "s": [100]}
                                ]
                            }
                        },
                        {"ty": "tr", "p": {"a": 0, "k": [0, 0]}, "a": {"a": 0, "k": [0, 0]}, "s": {"a": 0, "k": [100, 100]}, "r": {"a": 0, "k": 0}, "o": {"a": 0, "k": 100}}
                    ],
                    "nm": "LED"
                }
            ],
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

    layers.append(create_server_icon(server_pos, "Server", layer_idx))
    layer_idx += 1

    # === TEXT LABELS ===
    def create_text_layer(text, pos, font_size, color, idx, font="Arial"):
        """Create a proper Lottie text layer"""
        return {
            "ddd": 0,
            "ind": idx,
            "ty": 5,
            "nm": text,
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [pos[0], pos[1], 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "t": {
                "d": {
                    "k": [
                        {
                            "s": {
                                "sz": [200, 50],
                                "ps": [-100, -font_size/2],
                                "s": font_size,
                                "f": font,
                                "t": text,
                                "ca": 0,
                                "j": 2,
                                "tr": 0,
                                "lh": font_size * 1.2,
                                "ls": 0,
                                "fc": color
                            },
                            "t": 0
                        }
                    ]
                },
                "p": {},
                "m": {
                    "g": 1,
                    "a": {"a": 0, "k": [0, 0]}
                },
                "a": []
            },
            "ip": 0,
            "op": duration_frames,
            "st": 0
        }

    # Add text labels (ByteByteGo theme colors)
    layers.append(create_text_layer("API", [width/2, 90], 22, ACCENT_TEAL, layer_idx, "Arial"))
    layer_idx += 1
    layers.append(create_text_layer("Server", [server_pos[0], server_pos[1] + 60], 13, TEXT_PRIMARY, layer_idx))
    layer_idx += 1
    layers.append(create_text_layer("Database", [db_pos[0], db_pos[1] + 60], 13, TEXT_PRIMARY, layer_idx))
    layer_idx += 1
    layers.append(create_text_layer("Storage", [disk1_pos[0], disk1_pos[1] + 50], 11, TEXT_SECONDARY, layer_idx))
    layer_idx += 1
    layers.append(create_text_layer("Storage", [disk2_pos[0], disk2_pos[1] + 50], 11, TEXT_SECONDARY, layer_idx))
    layer_idx += 1

    # Add background layer (ByteByteGo primary background)
    bg_layer = {
        "ddd": 0,
        "ind": layer_idx,
        "ty": 1,  # Solid layer
        "nm": "Background",
        "sr": 1,
        "ks": {
            "o": {"a": 0, "k": 100},
            "r": {"a": 0, "k": 0},
            "p": {"a": 0, "k": [width/2, height/2, 0]},
            "a": {"a": 0, "k": [width/2, height/2, 0]},
            "s": {"a": 0, "k": [100, 100, 100]}
        },
        "ao": 0,
        "sw": width,
        "sh": height,
        "sc": COLORS['colors']['background']['primary'],  # #2B2B2B
        "ip": 0,
        "op": duration_frames,
        "st": 0
    }
    layers.append(bg_layer)
    layer_idx += 1

    # Create the final Lottie JSON
    lottie = {
        "v": "5.7.4",
        "fr": fps,
        "ip": 0,
        "op": duration_frames,
        "w": width,
        "h": height,
        "nm": "Architecture Diagram",
        "ddd": 0,
        "assets": [
            {
                "id": "database_svg",
                "w": 64,
                "h": 64,
                "u": DATABASE_SVG_PATH,  # Path to folder
                "p": DATABASE_SVG_FILE,   # Filename
                "e": 0  # External file (not embedded)
            }
        ],
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


if __name__ == "__main__":
    # Create the architecture Lottie
    lottie = create_architecture_lottie()

    # Save to file
    output_file = "architecture.json"
    with open(output_file, 'w') as f:
        json.dump(lottie, f, indent=2)

    print(f"Created: {output_file}")

    # Create HTML preview with ByteByteGo theme
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Architecture Diagram - Lottie Preview</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        body {{
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            background: {COLORS['colors']['background']['primary']};
            font-family: Arial, sans-serif;
        }}
        #lottie-container {{
            width: 800px;
            height: 600px;
            background: {COLORS['colors']['background']['primary']};
            border-radius: 10px;
            border: 2px solid {COLORS['colors']['border']['accent']};
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
    </style>
</head>
<body>
    <div id="lottie-container"></div>
    <script>
        lottie.loadAnimation({{
            container: document.getElementById('lottie-container'),
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: 'architecture.json'
        }});
    </script>
</body>
</html>'''

    with open("preview-architecture.html", 'w') as f:
        f.write(html)

    print("Created: preview-architecture.html")
    print("\nRun 'python3 -m http.server 8080' and open http://localhost:8080/preview-architecture.html")
