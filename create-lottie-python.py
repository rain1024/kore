#!/usr/bin/env python3
"""
Create Lottie animations programmatically with Python
Uses the python-lottie library: pip install lottie

Documentation: https://pypi.org/project/lottie/
"""

import json

# Method 1: Create Lottie JSON manually (no external dependencies)
def create_arrow_lottie_manual():
    """Create a simple animated arrow using raw Lottie JSON structure"""

    lottie_data = {
        "v": "5.7.4",  # Lottie version
        "fr": 60,      # Frame rate
        "ip": 0,       # In point (start frame)
        "op": 60,      # Out point (end frame) - 1 second at 60fps
        "w": 500,      # Width
        "h": 500,      # Height
        "nm": "Arrow Animation",  # Name
        "ddd": 0,      # 3D disabled
        "assets": [],  # No external assets
        "layers": [
            {
                "ddd": 0,
                "ind": 1,
                "ty": 4,  # Shape layer
                "nm": "Arrow",
                "sr": 1,
                "ks": {  # Transform properties
                    "o": {"a": 0, "k": 100},  # Opacity
                    "r": {"a": 0, "k": 0},    # Rotation
                    "p": {  # Position with animation
                        "a": 1,  # Animated
                        "k": [
                            {
                                "i": {"x": 0.667, "y": 1},
                                "o": {"x": 0.333, "y": 0},
                                "t": 0,
                                "s": [150, 250, 0]  # Start position
                            },
                            {
                                "t": 60,
                                "s": [350, 250, 0]  # End position
                            }
                        ]
                    },
                    "a": {"a": 0, "k": [0, 0, 0]},  # Anchor point
                    "s": {"a": 0, "k": [100, 100, 100]}  # Scale
                },
                "ao": 0,
                "shapes": [
                    {
                        "ty": "gr",  # Group
                        "it": [
                            {
                                "ty": "sh",  # Shape path
                                "nm": "Arrow Path",
                                "ks": {
                                    "a": 0,
                                    "k": {
                                        "i": [[0, 0], [0, 0], [0, 0]],  # In tangents
                                        "o": [[0, 0], [0, 0], [0, 0]],  # Out tangents
                                        "v": [[-30, -30], [30, 0], [-30, 30]],  # Vertices (arrow shape)
                                        "c": False  # Not closed
                                    }
                                }
                            },
                            {
                                "ty": "st",  # Stroke
                                "c": {"a": 0, "k": [0.2, 0.6, 1, 1]},  # Blue color
                                "o": {"a": 0, "k": 100},  # Opacity
                                "w": {"a": 0, "k": 8},   # Stroke width
                                "lc": 2,  # Line cap (round)
                                "lj": 2,  # Line join (round)
                                "nm": "Stroke"
                            },
                            {
                                "ty": "tr",  # Transform
                                "p": {"a": 0, "k": [0, 0]},
                                "a": {"a": 0, "k": [0, 0]},
                                "s": {"a": 0, "k": [100, 100]},
                                "r": {"a": 0, "k": 0},
                                "o": {"a": 0, "k": 100}
                            }
                        ],
                        "nm": "Arrow Group"
                    }
                ],
                "ip": 0,
                "op": 60,
                "st": 0
            }
        ]
    }

    return lottie_data


def create_bouncing_circle_lottie():
    """Create a bouncing circle animation"""

    lottie_data = {
        "v": "5.7.4",
        "fr": 60,
        "ip": 0,
        "op": 120,  # 2 seconds
        "w": 400,
        "h": 400,
        "nm": "Bouncing Circle",
        "ddd": 0,
        "assets": [],
        "layers": [
            {
                "ddd": 0,
                "ind": 1,
                "ty": 4,
                "nm": "Circle",
                "sr": 1,
                "ks": {
                    "o": {"a": 0, "k": 100},
                    "r": {"a": 0, "k": 0},
                    "p": {
                        "a": 1,
                        "k": [
                            {
                                "i": {"x": 0.667, "y": 0.667},
                                "o": {"x": 0.333, "y": 0.333},
                                "t": 0,
                                "s": [200, 100, 0]
                            },
                            {
                                "i": {"x": 0.667, "y": 0.667},
                                "o": {"x": 0.333, "y": 0.333},
                                "t": 30,
                                "s": [200, 300, 0]
                            },
                            {
                                "i": {"x": 0.667, "y": 0.667},
                                "o": {"x": 0.333, "y": 0.333},
                                "t": 60,
                                "s": [200, 100, 0]
                            },
                            {
                                "i": {"x": 0.667, "y": 0.667},
                                "o": {"x": 0.333, "y": 0.333},
                                "t": 90,
                                "s": [200, 300, 0]
                            },
                            {
                                "t": 120,
                                "s": [200, 100, 0]
                            }
                        ]
                    },
                    "a": {"a": 0, "k": [0, 0, 0]},
                    "s": {
                        "a": 1,
                        "k": [
                            {
                                "i": {"x": [0.667], "y": [1]},
                                "o": {"x": [0.333], "y": [0]},
                                "t": 0,
                                "s": [100, 100, 100]
                            },
                            {
                                "i": {"x": [0.667], "y": [1]},
                                "o": {"x": [0.333], "y": [0]},
                                "t": 30,
                                "s": [120, 80, 100]  # Squash
                            },
                            {
                                "i": {"x": [0.667], "y": [1]},
                                "o": {"x": [0.333], "y": [0]},
                                "t": 60,
                                "s": [100, 100, 100]
                            },
                            {
                                "i": {"x": [0.667], "y": [1]},
                                "o": {"x": [0.333], "y": [0]},
                                "t": 90,
                                "s": [120, 80, 100]  # Squash
                            },
                            {
                                "t": 120,
                                "s": [100, 100, 100]
                            }
                        ]
                    }
                },
                "ao": 0,
                "shapes": [
                    {
                        "ty": "gr",
                        "it": [
                            {
                                "ty": "el",  # Ellipse
                                "s": {"a": 0, "k": [80, 80]},  # Size
                                "p": {"a": 0, "k": [0, 0]},    # Position
                                "nm": "Ellipse"
                            },
                            {
                                "ty": "fl",  # Fill
                                "c": {"a": 0, "k": [1, 0.4, 0.4, 1]},  # Red color
                                "o": {"a": 0, "k": 100},
                                "nm": "Fill"
                            },
                            {
                                "ty": "tr",
                                "p": {"a": 0, "k": [0, 0]},
                                "a": {"a": 0, "k": [0, 0]},
                                "s": {"a": 0, "k": [100, 100]},
                                "r": {"a": 0, "k": 0},
                                "o": {"a": 0, "k": 100}
                            }
                        ],
                        "nm": "Circle Group"
                    }
                ],
                "ip": 0,
                "op": 120,
                "st": 0
            }
        ]
    }

    return lottie_data


# Method 2: Using python-lottie library (pip install lottie)
def create_with_lottie_library():
    """Create animation using the python-lottie library"""
    try:
        from lottie import objects
        from lottie import Animation, Color
        from lottie.utils import animation as anim_utils

        # Create animation
        anim = Animation(60)  # 60 frames
        anim.width = 500
        anim.height = 500
        anim.frame_rate = 60
        anim.name = "Python Lottie Animation"

        # Create a shape layer
        layer = objects.ShapeLayer()
        anim.add_layer(layer)

        # Add a rectangle
        group = layer.add_shape(objects.Group())
        rect = group.add_shape(objects.Rect())
        rect.size.value = [100, 100]
        rect.position.value = [250, 250]

        # Add fill
        fill = group.add_shape(objects.Fill())
        fill.color.value = Color(0.2, 0.8, 0.4)  # Green

        # Animate position
        layer.transform.position.add_keyframe(0, [150, 250])
        layer.transform.position.add_keyframe(30, [350, 250])
        layer.transform.position.add_keyframe(60, [150, 250])

        return anim.to_dict()

    except ImportError:
        print("python-lottie not installed. Run: pip install lottie")
        return None


def save_lottie(data, filename):
    """Save Lottie data to a JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Saved: {filename}")


def create_html_preview(lottie_file, html_file):
    """Create an HTML file to preview the Lottie animation"""
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>Lottie Preview</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #1a1a2e;
        }}
        #lottie-container {{
            width: 500px;
            height: 500px;
            background: white;
            border-radius: 10px;
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
            path: '{lottie_file}'
        }});
    </script>
</body>
</html>'''

    with open(html_file, 'w') as f:
        f.write(html_content)
    print(f"Saved: {html_file}")


if __name__ == "__main__":
    # Create animations
    print("Creating Lottie animations with Python...\n")

    # Method 1: Manual JSON creation
    arrow_data = create_arrow_lottie_manual()
    save_lottie(arrow_data, "arrow-animation.json")

    bouncing_data = create_bouncing_circle_lottie()
    save_lottie(bouncing_data, "bouncing-circle.json")

    # Method 2: Using python-lottie library
    lib_data = create_with_lottie_library()
    if lib_data:
        save_lottie(lib_data, "lottie-library-animation.json")

    # Create HTML preview
    create_html_preview("arrow-animation.json", "preview-arrow.html")
    create_html_preview("bouncing-circle.json", "preview-bouncing.html")

    print("\nDone! Open the HTML files in a browser to preview animations.")
    print("\nTo install python-lottie: pip install lottie")
