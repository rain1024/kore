#!/usr/bin/env python3
"""
Kore CLI

Usage:
    kore                           # Interactive mode
    kore <file.kore>               # Run file
    kore -e "animate CAT.go; show" # Inline command
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from kore_parser import KoreParser
from mindmap_renderer import save_mindmap_svg, render_mindmap_svg

# IPC file for CLI <-> GUI communication
IPC_FILE = Path(tempfile.gettempdir()) / "kore_ipc.json"

# Resources directory (relative to this file)
RESOURCES_DIR = Path(__file__).parent / "resources"
GUI_DIR = Path(__file__).parent / "gui"


def send_to_gui(command: dict):
    """Send command to GUI via IPC file"""
    IPC_FILE.write_text(json.dumps(command))


def show_gui(animation: str = None):
    """Launch the Electron GUI app with optional animation"""
    gui_path = GUI_DIR
    if not gui_path.exists():
        print("Error: GUI not found. Run 'npm install' in kore/gui first.", file=sys.stderr)
        sys.exit(1)

    # Check if node_modules exists
    if not (gui_path / "node_modules").exists():
        print("Installing GUI dependencies...")
        subprocess.run(["npm", "install"], cwd=gui_path, check=True)

    # Launch electron with animation and cwd arguments
    cmd = ["npm", "start", "--"]
    if animation:
        cmd.append(animation)
    # Pass current working directory
    cmd.append(f"--cwd={os.getcwd()}")

    subprocess.Popen(
        cmd,
        cwd=gui_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def mindmap_to_json(node) -> dict:
    """Convert MindmapNode to JSON-serializable dict"""
    return {
        "text": node.text,
        "children": [mindmap_to_json(c) for c in node.children]
    }


def show_mindmap_gui(svg_path: str, mindmap_data: dict = None):
    """Launch the Electron GUI app with mindmap SVG"""
    gui_path = GUI_DIR
    if not gui_path.exists():
        print("Error: GUI not found. Run 'npm install' in kore/gui first.", file=sys.stderr)
        sys.exit(1)

    # Check if node_modules exists
    if not (gui_path / "node_modules").exists():
        print("Installing GUI dependencies...")
        subprocess.run(["npm", "install"], cwd=gui_path, check=True)

    # Save mindmap data as JSON for GUI to modify
    if mindmap_data:
        json_path = Path(tempfile.gettempdir()) / "kore_mindmap.json"
        json_path.write_text(json.dumps(mindmap_data))

    # Launch electron with mindmap SVG path
    cmd = ["npm", "start", "--", f"--mindmap={svg_path}", f"--cwd={os.getcwd()}"]

    subprocess.Popen(
        cmd,
        cwd=gui_path,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def run_repl():
    """Interactive REPL mode"""
    print("Kore interactive mode. Type 'help' for commands, 'quit' to exit.")

    kore_parser = KoreParser()
    gui_running = False
    current_animation = None

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not line:
            continue

        # Built-in commands
        if line == "quit" or line == "exit":
            send_to_gui({"cmd": "quit"})
            break

        if line == "help":
            print("""Commands:
  animate <NAME>.<action>  - Load animation (e.g., animate CAT.go)
  show                     - Open GUI window
  play                     - Play animation
  pause                    - Pause animation
  stop                     - Stop and reset animation
  speed <value>            - Set speed (e.g., speed 2)
  loop <on|off>            - Toggle loop
  quit                     - Exit""")
            continue

        # Parse as kore command
        if line.startswith("animate "):
            try:
                program = kore_parser.parse(line)
                if program.animations:
                    a = program.animations[0]
                    current_animation = f"{a.target.lower()}.{a.action}"
                    # Check if animation exists
                    if load_animation(a.target, a.action):
                        print(f"Loaded: {a.target}.{a.action}")
                        if gui_running:
                            send_to_gui({"cmd": "animate", "name": current_animation})
                    else:
                        print(f"Error: Animation not found: {a.target}.{a.action}")
            except Exception as e:
                print(f"Error: {e}")
            continue

        if line == "show":
            show_gui(current_animation)
            gui_running = True
            continue

        if line == "play":
            send_to_gui({"cmd": "play"})
            continue

        if line == "pause":
            send_to_gui({"cmd": "pause"})
            continue

        if line == "stop":
            send_to_gui({"cmd": "stop"})
            continue

        if line.startswith("speed "):
            try:
                speed = float(line.split()[1])
                send_to_gui({"cmd": "speed", "value": speed})
                print(f"Speed: {speed}x")
            except:
                print("Usage: speed <number>")
            continue

        if line.startswith("loop "):
            val = line.split()[1].lower()
            send_to_gui({"cmd": "loop", "value": val == "on"})
            print(f"Loop: {val}")
            continue

        print(f"Unknown command: {line}. Type 'help' for commands.")


def load_animation(target: str, action: str) -> dict | None:
    """Load animation JSON from resources/{target}.{action}.json"""
    # Try lowercase
    anim_file = RESOURCES_DIR / f"{target.lower()}.{action}.json"
    if anim_file.exists():
        return json.loads(anim_file.read_text())
    return None


def save_gif(lottie_data: dict, output_path: str, width=400, height=400, fps=30):
    """Save Lottie JSON to GIF using Playwright"""
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import io
    import os

    frame_rate = lottie_data.get('fr', 30)
    in_point = lottie_data.get('ip', 0)
    out_point = lottie_data.get('op', 60)
    lottie_width = lottie_data.get('w', 200)
    lottie_height = lottie_data.get('h', 200)

    total_frames = int(out_point - in_point)
    duration_ms = (total_frames / frame_rate) * 1000

    # Create HTML with lottie-web
    html = f'''<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; }}
        body {{ background: black; }}
        #lottie {{ width: {lottie_width}px; height: {lottie_height}px; }}
    </style>
</head>
<body>
    <div id="lottie"></div>
    <script>
        const animData = {json.dumps(lottie_data)};
        const anim = lottie.loadAnimation({{
            container: document.getElementById('lottie'),
            renderer: 'svg',
            loop: false,
            autoplay: false,
            animationData: animData
        }});
        window.anim = anim;
        window.totalFrames = anim.totalFrames;
    </script>
</body>
</html>'''

    # Write temp HTML
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
        f.write(html)
        temp_html = f.name

    frames = []
    output_frames = max(1, int((duration_ms / 1000) * fps))

    print(f"Rendering {output_frames} frames...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': lottie_width, 'height': lottie_height})
            page.goto(f'file://{temp_html}')
            page.wait_for_function('window.anim && window.anim.isLoaded')

            for i in range(output_frames):
                frame_num = (i / max(1, output_frames - 1)) * total_frames if output_frames > 1 else 0
                page.evaluate(f'window.anim.goToAndStop({frame_num}, true)')

                screenshot = page.locator('#lottie').screenshot()
                img = Image.open(io.BytesIO(screenshot))
                frames.append(img.convert('RGBA'))
                print(f"  Frame {i + 1}/{output_frames}", end='\r')

            browser.close()

        print()

        if frames:
            frame_duration = max(20, round(1000 / fps / 10) * 10)
            frames[0].save(
                output_path,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=0,
                disposal=2
            )
            print(f"Saved: {output_path} ({os.path.getsize(output_path) / 1024:.1f} KB)")

    finally:
        Path(temp_html).unlink(missing_ok=True)


def generate_mindmap(topic: str) -> str:
    """Use Claude CLI to generate a mindmap for the given topic"""
    prompt = f"""Generate a mindmap for the topic: "{topic}"

Output ONLY the mindmap in Kore syntax format (no explanations, no markdown code blocks):
- First line: mindmap TOPIC
- Children indented with 2 spaces
- Grandchildren indented with 4 spaces
- Keep it concise: 3-5 main branches, 2-3 items per branch
- Use short, clear labels (2-4 words max)

Example format:
mindmap Python
  Data Types
    Numbers
    Strings
    Lists
  Control Flow
    If/Else
    Loops
  Functions
    Arguments
    Return Values

Now generate for: {topic}"""

    try:
        result = subprocess.run(
            ["claude", "-p", prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            # Clean up: remove markdown code blocks if present
            if output.startswith("```"):
                lines = output.split("\n")
                output = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
            return output
        else:
            print(f"Error: Claude CLI failed: {result.stderr}", file=sys.stderr)
            return None
    except FileNotFoundError:
        print("Error: 'claude' CLI not found. Install Claude Code first.", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("Error: Claude CLI timed out", file=sys.stderr)
        return None


def main():
    # Handle 'kore show' command directly (before argparse)
    if len(sys.argv) >= 2 and sys.argv[1] == "show":
        show_gui()
        print("Kore GUI launched.")
        return

    # Handle 'kore generate <topic>' command
    # Usage: kore generate <topic> [-o file.kore] [--show]
    if len(sys.argv) >= 3 and sys.argv[1] == "generate":
        # Parse generate arguments
        args_list = sys.argv[2:]
        output_file = None
        show_result = False
        topic_parts = []

        i = 0
        while i < len(args_list):
            if args_list[i] == "-o" and i + 1 < len(args_list):
                output_file = args_list[i + 1]
                i += 2
            elif args_list[i] == "--show":
                show_result = True
                i += 1
            else:
                topic_parts.append(args_list[i])
                i += 1

        topic = " ".join(topic_parts)
        if not topic:
            print("Usage: kore generate <topic> [-o file.kore] [--show]", file=sys.stderr)
            sys.exit(1)

        print(f"Generating mindmap for: {topic}...")
        result = generate_mindmap(topic)
        if result:
            if output_file:
                Path(output_file).write_text(result + "\n\nshow\n")
                print(f"Saved to: {output_file}")
            else:
                print(result)

            if show_result:
                # Parse and show the generated mindmap
                kore_parser = KoreParser()
                program = kore_parser.parse(result)
                if program.mindmaps:
                    temp_svg = Path(tempfile.gettempdir()) / "kore_mindmap.svg"
                    save_mindmap_svg(program.mindmaps[0], str(temp_svg))
                    mindmap_data = mindmap_to_json(program.mindmaps[0].root)
                    show_mindmap_gui(str(temp_svg), mindmap_data)
                    print("GUI launched.")
        return

    parser = argparse.ArgumentParser(
        description="Kore - Transform thinking into illustrations and animations"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input .kore file, 'show' to open GUI, or inline command (if -e is used)"
    )
    parser.add_argument(
        "-e", "--exec",
        dest="inline",
        metavar="CMD",
        help="Execute inline command (e.g., 'animate CAT.go; save cat.gif')"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)"
    )
    parser.add_argument(
        "--ast",
        action="store_true",
        help="Print AST instead of rendering"
    )

    args = parser.parse_args()

    # Determine source: inline command or file
    kore_parser = KoreParser()

    if args.inline:
        # Inline command: replace semicolons with newlines
        source = args.inline.replace(";", "\n")
        try:
            program = kore_parser.parse(source)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.input:
        # Check if input looks like an inline command (no file extension or doesn't exist)
        input_path = Path(args.input)
        if input_path.exists():
            # File input
            try:
                program = kore_parser.parse_file(str(input_path))
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        elif args.input.startswith("animate ") or args.input.startswith("object ") or args.input.startswith("save "):
            # Looks like inline command
            source = args.input.replace(";", "\n")
            try:
                program = kore_parser.parse(source)
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"Error: File not found: {input_path}", file=sys.stderr)
            sys.exit(1)
    else:
        # No arguments - run interactive mode
        run_repl()
        return

    # Output AST
    if args.ast:
        print("Objects:")
        for obj in program.objects:
            print(f"  {obj.name}")
            for k, v in obj.properties.items():
                print(f"    {k}: {v}")
        print("\nAnimations:")
        for anim in program.animations:
            print(f"  {anim.target}.{anim.action}")
        print("\nMindmaps:")
        for mm in program.mindmaps:
            def print_node(node, indent=0):
                print("  " * indent + f"  {node.text}")
                for child in node.children:
                    print_node(child, indent + 1)
            if mm.root:
                print_node(mm.root)
        print("\nSaves:")
        for save in program.saves:
            print(f"  {save.filename}")
        return

    # Render (placeholder - will generate Lottie JSON later)
    output = {
        "objects": [
            {"name": o.name, "properties": o.properties}
            for o in program.objects
        ],
        "animations": [
            {"target": a.target, "action": a.action}
            for a in program.animations
        ],
        "saves": [s.filename for s in program.saves]
    }

    result = json.dumps(output, indent=2, ensure_ascii=False)

    # Load animations from resources
    loaded_animations = []
    for anim in program.animations:
        lottie = load_animation(anim.target, anim.action)
        if lottie:
            loaded_animations.append(lottie)
            print(f"Loaded: {anim.target}.{anim.action}")
        else:
            print(f"Warning: Animation not found: {anim.target}.{anim.action}", file=sys.stderr)

    # Handle save commands
    for save in program.saves:
        filename = save.filename

        # SVG output for mindmaps
        if filename.endswith('.svg') and program.mindmaps:
            save_mindmap_svg(program.mindmaps[0], filename)
            continue

        # GIF output for animations
        if loaded_animations:
            save_gif(loaded_animations[0], filename)
        else:
            print(f"Error: No animations to save", file=sys.stderr)

    if args.output:
        Path(args.output).write_text(result)
        print(f"Saved: {args.output}")
    elif not program.saves and not program.shows:
        print(result)

    # Handle show commands
    if program.shows:
        if program.mindmaps:
            # Show mindmap in Electron GUI
            temp_svg = Path(tempfile.gettempdir()) / "kore_mindmap.svg"
            save_mindmap_svg(program.mindmaps[0], str(temp_svg))
            mindmap_data = mindmap_to_json(program.mindmaps[0].root)
            show_mindmap_gui(str(temp_svg), mindmap_data)
        elif program.animations:
            # Pass first animation to GUI
            a = program.animations[0]
            anim_name = f"{a.target.lower()}.{a.action}"
            show_gui(anim_name)
        else:
            print("Nothing to show", file=sys.stderr)


if __name__ == "__main__":
    main()
