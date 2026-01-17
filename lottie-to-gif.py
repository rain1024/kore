#!/usr/bin/env python3
"""
Convert Lottie JSON to GIF using Python

Requirements:
    pip install lottie cairosvg pillow
"""

import json
import io
import os
from PIL import Image

def lottie_to_gif_with_library(input_file, output_file, width=400, height=400, fps=30):
    """Convert Lottie to GIF using python-lottie library"""
    try:
        from lottie import parsers, exporters

        # Load the animation
        animation = parsers.tgs.parse_tgs(input_file)

        # Export to GIF
        with open(output_file, 'wb') as f:
            exporters.gif.export_gif(animation, f, width, height, fps)

        print(f"Saved: {output_file}")
        return True
    except ImportError:
        print("python-lottie not installed or missing dependencies")
        return False


def lottie_to_gif_manual(input_file, output_file, width=400, height=400, fps=30):
    """Convert Lottie to GIF by rendering SVG frames"""
    try:
        import cairosvg
        from lottie import parsers
        from lottie.exporters import svg

        # Load animation
        if input_file.endswith('.json'):
            with open(input_file, 'r') as f:
                from lottie import Animation
                animation = Animation.load(json.load(f))
        else:
            animation = parsers.tgs.parse_tgs(input_file)

        # Calculate frames
        total_frames = int(animation.out_point - animation.in_point)
        frame_duration = int(1000 / fps)  # milliseconds per frame

        frames = []

        print(f"Rendering {total_frames} frames...")

        for i in range(0, total_frames, max(1, total_frames // (fps * 2))):
            frame = animation.in_point + i

            # Render to SVG
            svg_str = io.StringIO()
            svg.export_svg(animation, svg_str, frame)
            svg_data = svg_str.getvalue()

            # Convert SVG to PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_data.encode(),
                output_width=width,
                output_height=height
            )

            # Open as PIL Image
            img = Image.open(io.BytesIO(png_data))
            frames.append(img.convert('RGBA'))

            print(f"  Frame {i + 1}/{total_frames}", end='\r')

        print(f"\nSaving GIF with {len(frames)} frames...")

        # Save as GIF
        if frames:
            frames[0].save(
                output_file,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=0,
                optimize=True
            )
            print(f"Saved: {output_file}")
            return True

        return False

    except Exception as e:
        print(f"Error: {e}")
        return False


def lottie_to_gif_simple(input_file, output_file, width=400, height=400, fps=30):
    """
    Simple method: Render Lottie frames to PNG then combine to GIF
    Uses basic SVG rendering without python-lottie exporters
    """
    try:
        import cairosvg

        # Load Lottie JSON
        with open(input_file, 'r') as f:
            lottie_data = json.load(f)

        frame_rate = lottie_data.get('fr', 60)
        in_point = lottie_data.get('ip', 0)
        out_point = lottie_data.get('op', 60)
        lottie_width = lottie_data.get('w', 500)
        lottie_height = lottie_data.get('h', 500)

        total_frames = int(out_point - in_point)
        duration_seconds = total_frames / frame_rate
        output_frames = int(duration_seconds * fps)

        print(f"Animation: {total_frames} frames at {frame_rate}fps = {duration_seconds:.2f}s")
        print(f"Output: {output_frames} frames at {fps}fps")

        frames = []

        for i in range(output_frames):
            # Calculate current time
            t = i / output_frames
            frame_num = in_point + t * (out_point - in_point)

            # Render frame to SVG
            svg_content = render_lottie_frame_to_svg(lottie_data, frame_num, lottie_width, lottie_height)

            # Convert SVG to PNG
            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode(),
                output_width=width,
                output_height=height
            )

            # Open as PIL Image
            img = Image.open(io.BytesIO(png_data))
            frames.append(img.convert('RGBA'))

            print(f"  Rendering frame {i + 1}/{output_frames}", end='\r')

        print(f"\nSaving to {output_file}...")

        # Check output format
        ext = os.path.splitext(output_file)[1].lower()

        if ext in ['.webm', '.mp4', '.mov']:
            # Use imageio for video formats
            import imageio.v3 as iio

            # Convert RGBA to RGB for video
            rgb_frames = []
            for frame in frames:
                rgb = Image.new('RGB', frame.size, (255, 255, 255))
                rgb.paste(frame, mask=frame.split()[3] if frame.mode == 'RGBA' else None)
                rgb_frames.append(rgb)

            # Convert to numpy arrays
            import numpy as np
            numpy_frames = [np.array(frame) for frame in rgb_frames]

            # Write video
            iio.imwrite(
                output_file,
                numpy_frames,
                fps=fps,
                codec='libvpx-vp9' if ext == '.webm' else 'libx264'
            )
        else:
            # Save as GIF (GIF uses centiseconds, so round to nearest 10ms)
            frame_duration = round(1000 / fps / 10) * 10
            if frame_duration < 20:
                frame_duration = 20  # Many viewers enforce 20ms minimum

            print(f"Frame duration: {frame_duration}ms")

            frames[0].save(
                output_file,
                save_all=True,
                append_images=frames[1:],
                duration=frame_duration,
                loop=0,
                disposal=2  # Clear frame before drawing next
            )

        print(f"Saved: {output_file} ({os.path.getsize(output_file) / 1024:.1f} KB)")
        return True

    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install cairosvg pillow")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def cubic_bezier(t, p0, p1, p2, p3):
    """Calculate cubic bezier value at t"""
    mt = 1 - t
    return mt*mt*mt*p0 + 3*mt*mt*t*p1 + 3*mt*t*t*p2 + t*t*t*p3


def bezier_easing(t, x1, y1, x2, y2, iterations=10):
    """Apply bezier easing curve to progress t"""
    # Newton-Raphson to find t for given x
    guess = t
    for _ in range(iterations):
        x = cubic_bezier(guess, 0, x1, x2, 1)
        if abs(x - t) < 0.0001:
            break
        # Derivative
        dx = 3*(1-guess)**2*(x1-0) + 6*(1-guess)*guess*(x2-x1) + 3*guess**2*(1-x2)
        if abs(dx) < 0.0001:
            break
        guess -= (x - t) / dx
        guess = max(0, min(1, guess))

    return cubic_bezier(guess, 0, y1, y2, 1)


def interpolate_value(keyframes, frame):
    """Interpolate animated value at given frame with bezier easing"""
    if not isinstance(keyframes, list):
        return keyframes

    # Find surrounding keyframes
    prev_kf = None
    next_kf = None

    for kf in keyframes:
        if isinstance(kf, dict) and 't' in kf:
            if kf['t'] <= frame:
                prev_kf = kf
            elif next_kf is None:
                next_kf = kf
                break

    if prev_kf is None:
        return keyframes[0].get('s', [0, 0]) if isinstance(keyframes[0], dict) else keyframes[0]

    if next_kf is None:
        return prev_kf.get('s', prev_kf.get('e', [0, 0]))

    t1, t2 = prev_kf['t'], next_kf['t']
    if t2 == t1:
        return prev_kf.get('s', [0, 0])

    # Linear progress
    linear_progress = (frame - t1) / (t2 - t1)

    # Apply bezier easing if available
    out_ease = prev_kf.get('o', {})
    in_ease = prev_kf.get('i', {})

    # Get easing values (can be single value or array per dimension)
    ox = out_ease.get('x', 0.333)
    oy = out_ease.get('y', 0.333)
    ix = in_ease.get('x', 0.667)
    iy = in_ease.get('y', 0.667)

    # Normalize to single values if arrays
    if isinstance(ox, list): ox = ox[0] if ox else 0.333
    if isinstance(oy, list): oy = oy[0] if oy else 0.333
    if isinstance(ix, list): ix = ix[0] if ix else 0.667
    if isinstance(iy, list): iy = iy[0] if iy else 0.667

    # Apply bezier easing
    progress = bezier_easing(linear_progress, ox, oy, ix, iy)

    start = prev_kf.get('s', [0, 0])
    end = next_kf.get('s', prev_kf.get('e', start))

    if isinstance(start, list) and isinstance(end, list):
        return [s + (e - s) * progress for s, e in zip(start, end)]
    elif isinstance(start, (int, float)) and isinstance(end, (int, float)):
        return start + (end - start) * progress

    return start


def get_animated_value(prop, frame):
    """Get value of animated property at frame"""
    if not isinstance(prop, dict):
        return prop

    if prop.get('a', 0) == 0:
        # Not animated
        return prop.get('k', 0)

    # Animated
    keyframes = prop.get('k', [])
    return interpolate_value(keyframes, frame)


def render_lottie_frame_to_svg(lottie_data, frame, width, height):
    """Render a single Lottie frame to SVG"""
    svg_elements = []

    # Process layers (reverse order for proper stacking)
    layers = lottie_data.get('layers', [])

    for layer in reversed(layers):
        layer_svg = render_layer(layer, frame)
        if layer_svg:
            svg_elements.append(layer_svg)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="{width}" height="{height}" fill="white"/>
  {''.join(svg_elements)}
</svg>'''

    return svg


def render_layer(layer, frame):
    """Render a layer to SVG elements"""
    layer_type = layer.get('ty', 0)

    # Check if layer is visible at this frame
    ip = layer.get('ip', 0)
    op = layer.get('op', 9999)
    if frame < ip or frame >= op:
        return ''

    # Get transform
    ks = layer.get('ks', {})

    position = get_animated_value(ks.get('p', {'k': [0, 0]}), frame)
    scale = get_animated_value(ks.get('s', {'k': [100, 100, 100]}), frame)
    rotation = get_animated_value(ks.get('r', {'k': 0}), frame)
    opacity = get_animated_value(ks.get('o', {'k': 100}), frame)

    if isinstance(position, list) and len(position) >= 2:
        tx, ty = position[0], position[1]
    else:
        tx, ty = 0, 0

    if isinstance(scale, list) and len(scale) >= 2:
        sx, sy = scale[0] / 100, scale[1] / 100
    else:
        sx, sy = 1, 1

    transform = f'translate({tx}, {ty}) scale({sx}, {sy}) rotate({rotation})'

    elements = []

    # Shape layer
    if layer_type == 4:
        shapes = layer.get('shapes', [])
        for shape in shapes:
            shape_svg = render_shape(shape, frame)
            if shape_svg:
                elements.append(shape_svg)

    if elements:
        return f'<g transform="{transform}" opacity="{opacity/100}">{"".join(elements)}</g>'

    return ''


def render_shape(shape, frame):
    """Render a shape to SVG"""
    shape_type = shape.get('ty', '')

    if shape_type == 'gr':  # Group
        items = shape.get('it', [])
        elements = []
        fill_color = None
        stroke_color = None
        stroke_width = 0

        # First pass: collect fill and stroke styles
        for item in items:
            item_type = item.get('ty', '')

            if item_type == 'fl':  # Fill
                color = get_animated_value(item.get('c', {'k': [0, 0, 0, 1]}), frame)
                if isinstance(color, list) and len(color) >= 3:
                    r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
                    fill_color = f'rgb({r},{g},{b})'

            elif item_type == 'st':  # Stroke
                color = get_animated_value(item.get('c', {'k': [0, 0, 0, 1]}), frame)
                if isinstance(color, list) and len(color) >= 3:
                    r, g, b = int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)
                    stroke_color = f'rgb({r},{g},{b})'
                stroke_width = get_animated_value(item.get('w', {'k': 1}), frame)

        # Second pass: render shapes with collected styles
        for item in items:
            item_type = item.get('ty', '')

            if item_type == 'el':  # Ellipse
                size = get_animated_value(item.get('s', {'k': [100, 100]}), frame)
                pos = get_animated_value(item.get('p', {'k': [0, 0]}), frame)
                if isinstance(size, list) and isinstance(pos, list):
                    rx, ry = size[0] / 2, size[1] / 2
                    cx, cy = pos[0], pos[1]
                    style = []
                    if fill_color:
                        style.append(f'fill="{fill_color}"')
                    else:
                        style.append('fill="none"')
                    if stroke_color:
                        style.append(f'stroke="{stroke_color}" stroke-width="{stroke_width}"')
                    elements.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" {" ".join(style)}/>')

            elif item_type == 'rc':  # Rectangle
                size = get_animated_value(item.get('s', {'k': [100, 100]}), frame)
                pos = get_animated_value(item.get('p', {'k': [0, 0]}), frame)
                if isinstance(size, list) and isinstance(pos, list):
                    w, h = size[0], size[1]
                    x, y = pos[0] - w/2, pos[1] - h/2
                    style = []
                    if fill_color:
                        style.append(f'fill="{fill_color}"')
                    else:
                        style.append('fill="none"')
                    if stroke_color:
                        style.append(f'stroke="{stroke_color}" stroke-width="{stroke_width}"')
                    elements.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" {" ".join(style)}/>')

            elif item_type == 'sh':  # Path
                path_data = get_animated_value(item.get('ks', {'k': {}}), frame)
                if isinstance(path_data, dict):
                    vertices = path_data.get('v', [])
                    if vertices:
                        d = f'M {vertices[0][0]} {vertices[0][1]}'
                        for v in vertices[1:]:
                            d += f' L {v[0]} {v[1]}'
                        if path_data.get('c', False):
                            d += ' Z'
                        style = []
                        if fill_color:
                            style.append(f'fill="{fill_color}"')
                        else:
                            style.append('fill="none"')
                        if stroke_color:
                            style.append(f'stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linecap="round" stroke-linejoin="round"')
                        elements.append(f'<path d="{d}" {" ".join(style)}/>')

        return ''.join(elements)

    return ''


if __name__ == "__main__":
    import sys

    # Default files
    input_file = "bouncing-circle.json"
    output_file = "bouncing-circle.gif"

    # Parse command line args
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]

    print(f"Converting {input_file} to {output_file}...")
    print()

    # Determine fps based on output format
    ext = os.path.splitext(output_file)[1].lower()
    fps = 60 if ext in ['.webm', '.mp4', '.mov'] else 50  # 50fps for GIF (20ms frames)

    success = lottie_to_gif_simple(input_file, output_file, width=400, height=400, fps=fps)

    if success:
        print(f"\nDone! Open {output_file} to view the animation.")
    else:
        print("\nFailed to convert. Make sure you have the required dependencies:")
        print("  pip install cairosvg pillow")
