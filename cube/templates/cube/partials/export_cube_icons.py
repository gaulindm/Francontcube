#!/usr/bin/env python3
"""
export_cube_icons.py
--------------------
Reads cube-moves-sprite.svg, extracts every <symbol>, and exports each one
as a transparent-background PNG ready to use in Kdenlive.

Output dimensions are derived from each symbol's viewBox aspect ratio so the
PNG is always pixel-perfect with no letterboxing or wasted space.

Usage:
    python export_cube_icons.py [--color COLOR] [--size SIZE] [--output DIR]

Options:
    --color   Foreground color for icons (default: #1a1a1a  ≈ near-black)
    --size    Longest edge in pixels – the other dimension scales to match
              the viewBox aspect ratio (default: 256)
    --output  Output directory (default: ./cube_icons_png)
"""

import argparse
import os
import xml.etree.ElementTree as ET

import cairosvg

# ── Namespace helper ──────────────────────────────────────────────────────────
SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def extract_symbols(svg_path: str) -> dict[str, ET.Element]:
    """Return a dict of {symbol_id: Element} from the sprite file."""
    tree = ET.parse(svg_path)
    root = tree.getroot()
    symbols = {}
    for sym in root.iter(f"{{{SVG_NS}}}symbol"):
        sid = sym.get("id")
        if sid:
            symbols[sid] = sym
    return symbols


def symbol_to_standalone_svg(symbol: ET.Element, color: str) -> tuple[str, float, float]:
    """
    Wrap a <symbol> element's children in a standalone <svg> element,
    replacing 'currentColor' with the chosen color.

    Returns (svg_string, viewbox_width, viewbox_height).
    """
    viewbox = symbol.get("viewBox", "0 0 100 100")
    parts = viewbox.split()
    vb_w, vb_h = float(parts[2]), float(parts[3])

    # Serialise the inner content
    inner_parts = []
    for child in symbol:
        inner_parts.append(ET.tostring(child, encoding="unicode"))
    inner = "\n  ".join(inner_parts)

    svg_str = (
        f'<svg xmlns="{SVG_NS}" '
        f'viewBox="{viewbox}" '
        f'width="{vb_w}" height="{vb_h}">\n'
        f'  {inner}\n'
        f'</svg>'
    )

    # Replace currentColor with the real color value
    svg_str = svg_str.replace("currentColor", color)

    return svg_str, vb_w, vb_h


def export_all(svg_path: str, output_dir: str, color: str, size: int) -> None:
    os.makedirs(output_dir, exist_ok=True)

    symbols = extract_symbols(svg_path)
    if not symbols:
        print("No <symbol> elements found – check the SVG file path.")
        return

    print(f"Found {len(symbols)} symbols. Exporting to '{output_dir}' "
          f"(longest edge = {size}px, aspect ratio preserved) …\n")

    for sid, sym in symbols.items():
        svg_str, vb_w, vb_h = symbol_to_standalone_svg(sym, color)

        # Scale so the longest edge equals `size`; the other edge follows
        # the viewBox aspect ratio — no letterboxing, no wasted pixels.
        scale = size / max(vb_w, vb_h)
        out_w = round(vb_w * scale)
        out_h = round(vb_h * scale)

        filename = f"{sid}.png"
        out_path = os.path.join(output_dir, filename)

        cairosvg.svg2png(
            bytestring=svg_str.encode("utf-8"),
            write_to=out_path,
            output_width=out_w,
            output_height=out_h,
            background_color="transparent",
        )
        print(f"  ✓ {filename}  ({out_w}×{out_h}px)")

    print(f"\nDone! {len(symbols)} PNGs saved to '{output_dir}'.")


# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Export cube-move SVG symbols to individual PNGs."
    )
    parser.add_argument(
        "--input",
        default="cube-moves-sprite.svg",
        help="Path to the sprite SVG file",
    )
    parser.add_argument(
        "--color",
        default="#1a1a1a",
        help="Icon foreground color (default: #1a1a1a)",
    )
    parser.add_argument(
        "--size",
        type=int,
        default=256,
        help="Longest edge in pixels; other dimension scales with viewBox aspect ratio (default: 256)",
    )
    parser.add_argument(
        "--output",
        default="cube_icons_png",
        help="Output directory (default: ./cube_icons_png)",
    )
    args = parser.parse_args()

    export_all(
        svg_path=args.input,
        output_dir=args.output,
        color=args.color,
        size=args.size,
    )