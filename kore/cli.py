#!/usr/bin/env python3
"""
Architecture Diagram CLI

Usage:
    python cli.py <input.md> [output.json] [--preview]
    python cli.py architecture1.md architecture1.json --preview

Parses Mermaid architecture syntax, auto-layouts, and generates Lottie JSON.
"""

import argparse
import json
import os
import sys
from pathlib import Path

from architecture_parser import ArchitectureParser
from architecture_layout import ArchitectureLayout, LayoutConfig
from architecture_lottie import LottieRenderer, LottieConfig, render_to_lottie


def create_preview_html(lottie_path: str, output_path: str):
    """Create HTML preview file for Lottie animation"""
    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Architecture Diagram Preview</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        body {{
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            background: #1a1a1a;
        }}
        #lottie-container {{
            width: 800px;
            height: 600px;
            background: #2B2B2B;
            border-radius: 10px;
            border: 2px solid #4ECDC4;
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
            path: '{os.path.basename(lottie_path)}'
        }});
    </script>
</body>
</html>'''

    with open(output_path, 'w') as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(
        description='Convert Mermaid architecture diagrams to Lottie JSON'
    )
    parser.add_argument(
        'input',
        help='Input file (.md with mermaid architecture syntax)'
    )
    parser.add_argument(
        'output',
        nargs='?',
        help='Output Lottie JSON file (default: <input>.json)'
    )
    parser.add_argument(
        '--preview',
        action='store_true',
        help='Generate HTML preview file'
    )
    parser.add_argument(
        '--width',
        type=int,
        default=800,
        help='Canvas width (default: 800)'
    )
    parser.add_argument(
        '--height',
        type=int,
        default=600,
        help='Canvas height (default: 600)'
    )
    parser.add_argument(
        '--fps',
        type=int,
        default=60,
        help='Frames per second (default: 60)'
    )
    parser.add_argument(
        '--duration',
        type=float,
        default=2.0,
        help='Animation duration in seconds (default: 2.0)'
    )

    args = parser.parse_args()

    # Resolve paths
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_suffix('.json')

    print(f"Parsing: {input_path}")

    # Parse diagram
    arch_parser = ArchitectureParser()
    try:
        diagram = arch_parser.parse_file(str(input_path))
    except Exception as e:
        print(f"Error parsing diagram: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"  Groups: {len(diagram.groups)}")
    print(f"  Services: {len(diagram.services)}")
    print(f"  Edges: {len(diagram.edges)}")

    # Layout
    print("Calculating layout...")
    layout_config = LayoutConfig()
    layout = ArchitectureLayout(layout_config)
    layout.layout(diagram)

    # Render to Lottie
    print("Generating Lottie JSON...")
    lottie_config = LottieConfig(
        width=args.width,
        height=args.height,
        fps=args.fps,
        duration_seconds=args.duration
    )
    lottie = render_to_lottie(diagram, lottie_config)

    # Save
    with open(output_path, 'w') as f:
        json.dump(lottie, f, indent=2)
    print(f"Saved: {output_path}")

    # Generate preview if requested
    if args.preview:
        preview_path = output_path.with_name(f"preview-{output_path.stem}.html")
        create_preview_html(str(output_path), str(preview_path))
        print(f"Preview: {preview_path}")
        print(f"\nRun: python3 -m http.server 8080")
        print(f"Open: http://localhost:8080/{preview_path.name}")


if __name__ == '__main__':
    main()
