#!/usr/bin/env python3
"""
webp2jpg.py - Batch convert .webp images to .jpg

By default it searches ~/Downloads and ~/Pictures (including subfolders),
converts every .webp it finds, and REPLACES the originals (each .webp is
deleted after its .jpg has been created successfully).

Examples:
    python3 webp2jpg.py                    # convert and replace everything
    python3 webp2jpg.py --dry-run          # just show what WOULD happen
    python3 webp2jpg.py --keep-originals   # convert but keep the .webp files
    python3 webp2jpg.py --quality 95       # higher quality JPGs
    python3 webp2jpg.py ~/Desktop          # search a different folder
"""

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("Pillow is not installed. On Fedora, run:")
    print("    sudo dnf install python3-pillow")
    sys.exit(1)


def find_webp_files(folders):
    """Yield every .webp file (any capitalisation) inside the given folders."""
    for folder in folders:
        if not folder.is_dir():
            print(f"Skipping missing folder: {folder}")
            continue
        for path in folder.rglob("*"):
            if path.is_file() and path.suffix.lower() == ".webp":
                yield path


def convert_to_jpg(src, quality):
    """Convert one file. Returns the path of the new JPG."""
    dest = src.with_suffix(".jpg")
    with Image.open(src) as img:
        # JPG has no transparency, so put transparent images on a white background
        has_alpha = img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        )
        if has_alpha:
            rgba = img.convert("RGBA")
            background = Image.new("RGB", rgba.size, (255, 255, 255))
            background.paste(rgba, mask=rgba.getchannel("A"))
            rgb = background
        else:
            rgb = img.convert("RGB")
        rgb.save(dest, "JPEG", quality=quality, optimize=True)
    return dest


def main():
    parser = argparse.ArgumentParser(description="Batch convert .webp images to .jpg")
    parser.add_argument(
        "folders",
        nargs="*",
        type=Path,
        help="Folders to search (default: ~/Downloads and ~/Pictures)",
    )
    parser.add_argument("--quality", type=int, default=90, help="JPG quality 1-100 (default 90)")
    parser.add_argument("--keep-originals", action="store_true", help="Keep the .webp files instead of replacing them")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be converted without changing anything")
    args = parser.parse_args()

    folders = [f.expanduser() for f in args.folders] or [
        Path.home() / "Downloads",
        Path.home() / "Pictures",
    ]

    converted = skipped = failed = 0

    for src in find_webp_files(folders):
        dest = src.with_suffix(".jpg")

        if dest.exists():
            print(f"[skip]    {src}  (a .jpg with that name already exists)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"[dry-run] {src}  ->  {dest.name}")
            converted += 1
            continue

        try:
            convert_to_jpg(src, args.quality)
            if not args.keep_originals:
                src.unlink()
            print(f"[done]    {src}  ->  {dest.name}")
            converted += 1
        except Exception as error:
            print(f"[failed]  {src}  ({error})")
            failed += 1

    verb = "would be converted" if args.dry_run else "converted"
    print(f"\nFinished: {converted} {verb}, {skipped} skipped, {failed} failed.")


if __name__ == "__main__":
    main()
