#!/usr/bin/env python3
"""
Capture Lottie animation from browser and convert to GIF
Uses playwright to render frames from lottie-web
"""

import asyncio
import os
import sys
from io import BytesIO
from PIL import Image


async def capture_lottie_to_gif(html_url, output_file, fps=60, duration_seconds=2, width=800, height=600, scale=2):
    """Capture Lottie animation from browser and save as GIF"""
    from playwright.async_api import async_playwright

    frames = []
    total_frames = int(fps * duration_seconds)
    frame_time_ms = 1000 / fps

    print(f"Capturing {total_frames} frames at {fps}fps...")

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={'width': width, 'height': height}, device_scale_factor=scale)

        await page.goto(html_url)
        await page.wait_for_timeout(500)  # Wait for animation to load

        # Get the lottie animation instance
        await page.evaluate('''() => {
            window.anim = lottie.getRegisteredAnimations()[0];
            window.anim.pause();
        }''')

        # Get total frames from animation
        anim_total_frames = await page.evaluate('() => window.anim.totalFrames')
        print(f"Animation has {anim_total_frames} frames")

        for i in range(total_frames):
            # Calculate which frame to show
            progress = i / total_frames
            frame_num = progress * anim_total_frames

            # Seek to frame
            await page.evaluate(f'() => window.anim.goToAndStop({frame_num}, true)')
            await page.wait_for_timeout(10)  # Small delay for rendering

            # Take screenshot
            screenshot = await page.screenshot()
            img = Image.open(BytesIO(screenshot))
            frames.append(img.convert('RGBA'))

            print(f"  Frame {i + 1}/{total_frames}", end='\r')

        await browser.close()

    print(f"\nSaving GIF with {len(frames)} frames...")

    # Convert to palette mode for GIF with high quality
    gif_frames = []
    for frame in frames:
        # Convert RGBA to RGB with ByteByteGo dark background
        rgb = Image.new('RGB', frame.size, (43, 43, 43))  # #2B2B2B
        rgb.paste(frame, mask=frame.split()[3] if frame.mode == 'RGBA' else None)
        # Use ADAPTIVE palette with max colors and FLOYDSTEINBERG dithering for quality
        gif_frames.append(rgb.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG))

    # Save as GIF (minimum 20ms per frame for compatibility)
    frame_duration = max(20, int(1000 / fps))
    print(f"Frame duration: {frame_duration}ms")

    gif_frames[0].save(
        output_file,
        save_all=True,
        append_images=gif_frames[1:],
        duration=frame_duration,
        loop=0
    )

    file_size = os.path.getsize(output_file) / 1024
    print(f"Saved: {output_file} ({file_size:.1f} KB)")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080/preview-architecture.html"
    output = sys.argv[2] if len(sys.argv) > 2 else "architecture.gif"
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else 60

    asyncio.run(capture_lottie_to_gif(url, output, fps=fps, duration_seconds=2))
