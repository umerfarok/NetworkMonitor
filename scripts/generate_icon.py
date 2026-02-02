#!/usr/bin/env python
"""
Generate application icons for NetworkMonitor
Creates proper ICO and ICNS files for Windows and macOS
"""
from PIL import Image, ImageDraw
import os
import sys

def create_icon():
    """Create application icon with network signal bars design"""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        margin = max(1, size // 10)
        
        # Draw blue background
        for y in range(margin, size - margin):
            for x in range(margin, size - margin):
                # Gradient from top-left to bottom-right
                t = (x + y) / (2 * size)
                r = int(33 + t * 20)
                g = int(150 - t * 50)
                b = int(243 - t * 60)
                img.putpixel((x, y), (r, g, b, 255))
        
        # Draw three network bars (signal icon)
        bar_width = max(2, size // 10)
        bar_heights = [0.35, 0.55, 0.75]
        
        center_x = size // 2
        bottom_y = size - margin - max(2, size // 8)
        
        for i, height_ratio in enumerate(bar_heights):
            bar_height = int((size - 2 * margin) * height_ratio)
            x_offset = (i - 1) * (bar_width * 2)
            x = center_x + x_offset - bar_width // 2
            y = bottom_y - bar_height
            
            # Draw white bar
            for bx in range(x, min(x + bar_width, size - margin)):
                for by in range(max(y, margin), bottom_y):
                    if margin <= bx < size - margin and margin <= by < size - margin:
                        img.putpixel((bx, by), (255, 255, 255, 255))
        
        images.append(img)
    
    # Get assets directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(os.path.dirname(script_dir), 'assets')
    
    if not os.path.exists(assets_dir):
        assets_dir = os.path.join(script_dir, 'assets')
    if not os.path.exists(assets_dir):
        assets_dir = 'assets'
    
    os.makedirs(assets_dir, exist_ok=True)
    
    # Save as ICO
    ico_path = os.path.join(assets_dir, 'icon.ico')
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"Created {ico_path}")
    print(f"Size: {os.path.getsize(ico_path)} bytes")
    
    return ico_path

if __name__ == '__main__':
    create_icon()
