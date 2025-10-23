#!/usr/bin/env python3
"""
MHwPlistSplitter
by MalikHw47
Github: MalikHw
YouTube: @MalikHw47

A tool to split PNG sprite sheets based on plist files.
"""

import os
import sys
import plistlib
import argparse
from pathlib import Path
from tkinter import Tk, filedialog
from PIL import Image


def show_help():
    """Display help information."""
    help_text = """
MHwPlistSplitter - PNG Sprite Sheet Splitter
by MalikHw47
Github: https://github.com/MalikHw
YouTube: @MalikHw47

Usage:
    python mhw_plist_splitter.py

This tool will:
1. Prompt you to select a plist file
2. Prompt you to select a PNG file
3. Split the PNG based on the plist data
4. Save sprites to: %USERPROFILE%\\Documents\\MHwPlistSplitter\\[original-plist-filename]\\
"""
    print(help_text)


def pick_file(title, filetypes):
    """Open a file picker dialog."""
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path


def parse_plist(plist_path):
    """Parse plist file and extract frame information."""
    with open(plist_path, 'rb') as f:
        plist_data = plistlib.load(f)
    
    # Handle different plist formats
    if 'frames' in plist_data:
        return plist_data['frames']
    elif 'metadata' in plist_data and 'frames' in plist_data['metadata']:
        return plist_data['metadata']['frames']
    else:
        raise ValueError("Unsupported plist format")


def parse_rect_string(rect_str):
    """Parse rectangle string from plist (e.g., '{{x,y},{w,h}}')."""
    # Remove braces and split
    rect_str = rect_str.strip('{}')
    parts = rect_str.split('},{')
    
    if len(parts) == 2:
        x, y = map(float, parts[0].strip('{}').split(','))
        w, h = map(float, parts[1].strip('{}').split(','))
        return int(x), int(y), int(w), int(h)
    else:
        raise ValueError(f"Cannot parse rect string: {rect_str}")


def split_sprites(plist_path, png_path):
    """Split PNG based on plist data."""
    # Get output directory
    plist_name = Path(plist_path).stem
    user_docs = Path.home() / "Documents"
    output_dir = user_docs / "MHwPlistSplitter" / plist_name
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Reading plist: {plist_path}")
    print(f"Reading PNG: {png_path}")
    print(f"Output directory: {output_dir}")
    
    # Parse plist
    frames = parse_plist(plist_path)
    
    # Open PNG
    img = Image.open(png_path)
    
    # Split sprites
    count = 0
    for sprite_name, sprite_data in frames.items():
        try:
            # Handle different plist formats
            if isinstance(sprite_data, dict):
                if 'frame' in sprite_data:
                    frame_str = sprite_data['frame']
                elif 'textureRect' in sprite_data:
                    frame_str = sprite_data['textureRect']
                else:
                    print(f"Skipping {sprite_name}: no frame data found")
                    continue
            else:
                frame_str = sprite_data
            
            # Parse frame rectangle
            x, y, w, h = parse_rect_string(frame_str)
            
            # Extract sprite
            sprite = img.crop((x, y, x + w, y + h))
            
            # Save sprite
            sprite_filename = Path(sprite_name).stem + ".png"
            sprite_path = output_dir / sprite_filename
            sprite.save(sprite_path)
            
            count += 1
            print(f"Saved: {sprite_filename}")
            
        except Exception as e:
            print(f"Error processing {sprite_name}: {e}")
    
    print(f"\nDone! Split {count} sprites to: {output_dir}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help', '-h', action='store_true', help='Show help')
    args = parser.parse_args()
    
    if args.help:
        show_help()
        return
    
    print("MHwPlistSplitter by MalikHw47")
    print("-" * 40)
    
    # Pick plist file
    print("\n1. Select a plist file...")
    plist_path = pick_file(
        "Select plist file",
        [("Plist files", "*.plist"), ("All files", "*.*")]
    )
    
    if not plist_path:
        print("No plist file selected. Exiting.")
        return
    
    # Pick PNG file
    print("\n2. Select a PNG file...")
    png_path = pick_file(
        "Select PNG file",
        [("PNG files", "*.png"), ("All files", "*.*")]
    )
    
    if not png_path:
        print("No PNG file selected. Exiting.")
        return
    
    # Split sprites
    print("\n3. Splitting sprites...")
    try:
        split_sprites(plist_path, png_path)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()