#!/usr/bin/env python3
"""
export_cube_state.py
--------------------
Export CubeState records from your Django database as transparent PNGs,
with optional arrow overlays for tutorial annotations.

SETUP
-----
Place this script anywhere inside your Django project (e.g. next to manage.py)
or pass --django-settings explicitly.

Usage examples:
  # Single slug
  python export_cube_state.py f2l-05

  # Multiple slugs
  python export_cube_state.py f2l-05 f2l-06 f2l-07

  # Whole category
  python export_cube_state.py --method cfop --category corner-in-slot

  # Whole method
  python export_cube_state.py --method cfop

  # With arrows from a JSON file
  python export_cube_state.py f2l-05 --arrows arrows.json

  # With inline arrows (JSON string)
  python export_cube_state.py f2l-05 --arrows '[{"x1":180,"y1":230,"x2":290,"y2":140,"color":"#cc2200","width":5}]'

  # Custom size and output dir
  python export_cube_state.py f2l-05 --size 512 --output ./my_pngs

  # Only the three visible faces (U, F, R / U, F, L) — no ghosted back layers
  python export_cube_state.py f2l-05 --no-hidden

  # Combine with other options
  python export_cube_state.py --method cfop --no-hidden --size 400

ARROW JSON FORMAT
-----------------
A JSON array of arrow objects. Each arrow:
  {
    "x1": 180,        required  start x  (SVG coords, viewBox 0 0 500 360)
    "y1": 230,        required  start y
    "x2": 290,        required  end x
    "y2": 140,        required  end y
    "color": "#cc2200",  optional  default #cc2200
    "width": 5,          optional  stroke width, default 4
    "tip": 8             optional  arrowhead size, default 7
  }

You can also save arrows as a .json file and pass its path to --arrows.
The same arrows are applied to all exported images in that run.
If you need per-slug arrows, export slugs one at a time with different --arrows.

COORDINATE REFERENCE
--------------------
The SVG canvas is 500 × 360.  Approximate face centres:
  Right-hand:  U ≈ (250, 75)   F ≈ (210, 210)   R ≈ (330, 185)
  Left-hand:   U ≈ (250, 75)   F ≈ (290, 210)   L ≈ (175, 185)
Hidden faces (B, D, and the side opposite the orientation) are rendered
in grey with a dashed border, matching the HTML template.
"""

import argparse
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

# ── Try to bootstrap Django ────────────────────────────────────────────────────
def setup_django(settings_module: str):
    try:
        import django
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings_module)
        django.setup()
    except Exception as e:
        print(f"[error] Could not initialise Django: {e}")
        print("        Make sure you run this from your project root,")
        print("        or pass --django-settings myproject.settings")
        sys.exit(1)

# ── Colour map ─────────────────────────────────────────────────────────────────
STICKER_COLORS = {
    "W": "#FFFFFF",
    "Y": "#FFFF00",
    "R": "#FF0000",
    "O": "#FF8000",
    "B": "#0000ff",
    "G": "#00cc00",
    "X": "#CCCCCC",   # unknown / hidden

}

HIDDEN_FILL         = "#EFEFEF"   # very light grey fill
HIDDEN_STROKE       = "#DDDDDD"
HIDDEN_STROKE_WIDTH = .20

# ── Polygon data (from _cube_svg_RL.html) ─────────────────────────────────────
# Each face is a 3×3 list of point strings.
POLYGONS = {
    "right": {
        "U": [
            ["209.148,42.905 258.265,47.594 231.732,71.5 180.808,65.951",
             "258.265,47.594 307.382,52.284 282.655,77.048 231.732,71.5",
             "307.382,52.284 356.499,56.973 333.578,82.597 282.655,77.048"],
            ["180.808,65.951 231.732,71.5 205.198,95.405 152.469,88.998",
             "231.732,71.5 282.655,77.048 257.928,101.813 205.198,95.405",
             "282.655,77.048 333.578,82.597 310.657,108.22 257.928,101.813"],
            ["152.469,88.998 205.198,95.405 178.665,119.311 124.129,112.044",
             "205.198,95.405 257.928,101.813 233.2,126.577 178.665,119.311",
             "257.928,101.813 310.657,108.22 287.736,133.844 233.2,126.577"],
        ],
        "F": [
            ["124.100,112.000 178.633,119.267 184.856,173.878 131.433,165.233",
             "178.633,119.267 233.167,126.533 238.278,182.522 184.856,173.878",
             "233.167,126.533 287.700,133.800 291.700,191.167 238.278,182.522"],
            ["131.433,165.233 184.856,173.878 191.078,228.489 138.767,218.467",
             "184.856,173.878 238.278,182.522 243.389,238.511 191.078,228.489",
             "238.278,182.522 291.700,191.167 295.700,248.533 243.389,238.511"],
            ["138.767,218.467 191.078,228.489 197.300,283.100 146.100,271.700",
             "191.078,228.489 243.389,238.511 248.500,294.500 197.300,283.100",
             "243.389,238.511 295.700,248.533 299.700,305.900 248.500,294.500"],
        ],
        "R": [
            ["287.7,133.8 310.633,108.167 313.456,164.644 291.700,191.167",
             "310.633,108.167 333.567,82.533 335.211,138.122 313.456,164.644",
             "333.567,82.533 356.5,56.9 356.967,111.600 335.211,138.122"],
            ["291.700,191.167 313.456,164.644 316.278,221.122 295.700,248.533",
             "313.456,164.644 335.211,138.122 336.856,193.711 316.278,221.122",
             "335.211,138.122 356.967,111.600 357.433,166.300 336.856,193.711"],
            ["295.700,248.533 316.278,221.122 319.100,277.600 299.700,305.900",
             "316.278,221.122 336.856,193.711 338.500,249.300 319.100,277.600",
             "336.856,193.711 357.433,166.300 357.900,221.000 338.500,249.300"],
        ],
        # Hidden faces
        "B": [
            ["331.9,37.85 371.1,41.05 371.1,85.05 331.9,81.05",
             "282.9,32.95 322.1,36.95 322.1,80.15 282.9,76.95",
             "233.9,28 273.1,32 273.1,76 233.9,72"],

            ["332,92 371.2,96 372,140 332.8,136",
             "278.729,82.269 327.847,86.96 328.315,141.634 279.197,136.945",
             "229.61,77.581 278.729,82.269 279.197,136.945 230.079,132.256"],



            ["230.079,132.256 279.197,136.945 279.666,191.62 230.549,186.932",
             "279.197,136.945 328.315,141.634 328.783,196.311 279.666,191.62",
             "332.9,147 372.1,151 372.1,195 332.9,191"],
        ],
        "L": [
            ["153.3,47.75 176.5,29.35 178.9,69.35 157.3,88.55",
             "125.35,70.85 147.75,52.45 151.75,93.25 130.15,112.45",
             "97.45,94.85 119.85,75.65 124.65,117.25 103.05,137.25"],
            ["155.468,96.591 182.485,72.27 185.821,121.635 160.136,147.247",
             "128.45,120.912 155.468,96.591 160.136,147.247 134.452,172.856",
             "104.35,147.75 125.95,127.75 130.75,169.35 109.95,190.15"],
            ["160.136,147.247 185.821,121.635 189.158,171 164.805,197.9",
             "134.452,172.856 160.136,147.247 164.805,197.9 140.453,224.8",
             "111.3,200.65 132.1,179.85 136.9,221.45 117.7,243.05"],
        ],
        "D": [
            ["178.2,270.95 219,279.75 203.8,302.95 163,293.35",
             "229.25,282 270.85,290.8 254.85,314 214.05,305.2",
             "281.1,292.95 321.9,300.95 305.9,324.95 265.1,316.15"],
            ["194.9,239.1 246.545,249.389 226.922,278.244 175.5,267.4",
             "246.545,249.389 298.189,259.678 278.344,289.09 226.922,278.244",
             "301.1,263 341.9,271 325.9,295 285.1,287"],
            ["214.3,210.8 266.167,220.533 246.545,249.389 194.9,239.1",
             "266.167,220.533 318.033,230.27 298.189,259.678 246.545,249.389",
             "321.1,233.9 361.9,241.9 345.9,265.1 305.1,257.1"],
        ],
    },
    "left": {
        "U": [
            ["143.501,56.973 192.618,52.284 217.345,77.048 166.422,82.597",
             "192.618,52.284 241.735,47.594 268.268,71.5 217.345,77.048",
             "241.735,47.594 290.852,42.905 319.192,65.951 268.268,71.5"],
            ["166.422,82.597 217.345,77.048 242.072,101.813 189.343,108.22",
             "217.345,77.048 268.268,71.5 294.802,95.405 242.072,101.813",
             "268.268,71.5 319.192,65.951 347.531,88.998 294.802,95.405"],
            ["189.343,108.22 242.072,101.813 266.8,126.577 212.264,133.844",
             "242.072,101.813 294.802,95.405 321.335,119.311 266.8,126.577",
             "294.802,95.405 347.531,88.998 375.871,112.044 321.335,119.311"],
        ],
        "F": [
            ["212.3,133.800 266.833,126.533 261.722,182.522 208.3,191.167",
             "266.833,126.533 321.367,119.267 315.144,173.878 261.722,182.522",
             "321.367,119.267 375.9,112.000 368.567,165.233 315.144,173.878"],
            ["208.3,191.167 261.722,182.522 256.611,238.511 204.3,248.533",
             "261.722,182.522 315.144,173.878 308.922,228.489 256.611,238.511",
             "315.144,173.878 368.567,165.233 361.233,218.467 308.922,228.489"],
            ["204.3,248.533 256.611,238.511 251.5,294.500 200.3,305.900",
             "256.611,238.511 308.922,228.489 302.7,283.100 251.5,294.500",
             "308.922,228.489 361.233,218.467 353.9,271.700 302.7,283.100"],
        ],
        "L": [
            ["143.5,56.9 166.433,82.533 164.789,138.122 143.033,111.600",
             "166.433,82.533 189.367,108.167 186.544,164.644 164.789,138.122",
             "189.367,108.167 212.3,133.8 208.3,191.167 186.544,164.644"],
            ["143.033,111.600 164.789,138.122 163.144,193.711 142.567,166.300",
             "164.789,138.122 186.544,164.644 183.722,221.122 163.144,193.711",
             "186.544,164.644 208.3,191.167 204.3,248.533 183.722,221.122"],
            ["142.567,166.300 163.144,193.711 161.5,249.300 142.1,221.000",
             "163.144,193.711 183.722,221.122 180.9,277.600 161.5,249.300",
             "183.722,221.122 204.3,248.533 200.3,305.900 180.9,277.600"],
        ],
        # Hidden faces
        "R": [
            ["320.852,22.905 349.201,45.94 344.532,96.591 317.515,72.27",
             "349.201,45.94 377.551,68.968 371.55,120.912 344.532,96.591",
             "377.551,68.968 405.9,92 398.567,145.233 371.55,120.912"],
            ["317.515,72.27 344.532,96.591 339.864,147.247 314.179,121.635",
             "344.532,96.591 371.55,120.912 365.548,172.856 339.864,147.247",
             "371.55,120.912 398.567,145.233 391.233,198.467 365.548,172.856"],
            ["314.179,121.635 339.864,147.247 335.195,197.9 310.842,171",
             "339.864,147.247 365.548,172.856 359.547,224.8 335.195,197.9",
             "365.548,172.856 391.233,198.467 383.9,251.7 359.547,224.8"],
        ],
        "B": [
            ["123.501,36.973 172.621,32.28 172.153,86.96 123.034,91.649",
             "172.621,32.28 221.74,27.594 221.271,82.269 172.153,86.96",
             "221.74,27.594 270.86,22.905 270.39,77.581 221.271,82.269"],
            ["123.034,91.649 172.153,86.96 171.685,141.634 122.567,146.324",
             "172.153,86.96 221.271,82.269 220.803,136.945 171.685,141.634",
             "221.271,82.269 270.39,77.581 269.921,132.256 220.803,136.945"],
            ["122.567,146.324 171.685,141.634 171.217,196.311 122.1,201",
             "171.685,141.634 220.803,136.945 220.334,191.62 171.217,196.311",
             "220.803,136.945 269.921,132.256 269.451,186.932 220.334,191.62"],
        ],
        "D": [
            ["170.233,299.933 221.656,289.09 241.5,318.5 190.3,329.9",
             "221.656,289.09 273.078,278.244 292.7,307.1 241.5,318.5",
             "273.078,278.244 324.5,267.4 343.9,295.7 292.7,307.1"],
            ["150.167,269.967 201.811,259.678 221.656,289.09 170.233,299.933",
             "201.811,259.678 253.455,249.389 273.078,278.244 221.656,289.09",
             "253.455,249.389 305.1,239.1 324.5,267.4 273.078,278.244"],
            ["130.1,240 181.967,230.27 201.811,259.678 150.167,269.967",
             "181.967,230.27 233.833,220.533 253.455,249.389 201.811,259.678",
             "233.833,220.533 285.7,210.8 305.1,239.1 253.455,249.389"],
        ],
    },
}

# Draw order: hidden faces first (back-to-front), visible faces on top
DRAW_ORDER = {
    "right": [
        ("B",  True,  False),  # (face, is_hidden, dashed_border)
        ("L",  True,  False),
        ("D",  True,  False),
        ("U",  False, False),
        ("F",  False, False),
        ("R",  False, False),
    ],
    "left": [
        ("R",  True,  False),
        ("D",  True,  False),
        ("B",  True,  True),
        ("U",  False, False),
        ("L",  False, False),
        ("F",  False, False),
    ],
}

SVG_NS = "http://www.w3.org/2000/svg"


# ── Colour resolution ──────────────────────────────────────────────────────────
def resolve_color(code: str, highlight_set: set, face: str, r: int, c: int) -> str:
    """
    Returns the fill hex for a sticker.
    Highlighted stickers get a yellow tint overlay (rendered as a separate polygon).
    """
    key = f"{face}-{r}-{c}"
    base = STICKER_COLORS.get(code.upper(), STICKER_COLORS["X"])
    return base
 
 
def is_highlighted(highlight_data, face: str, r: int, c: int) -> bool:
    if not highlight_data:
        return False
    stickers = highlight_data.get("stickers", [])
    return f"{face}-{r}-{c}" in stickers or [face, r, c] in stickers
 
 
# ── SVG polygon helpers ────────────────────────────────────────────────────────
def poly_el(points: str, fill: str, stroke: str, stroke_width: float,
            dashed: bool = False, opacity: float = 1.0) -> str:
    dash = ' stroke-dasharray="4,3"' if dashed else ""
    op   = f' opacity="{opacity}"' if opacity < 1.0 else ""
    return (
        f'<polygon points="{points}" '
        f'fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{stroke_width}" stroke-linejoin="round"'
        f'{dash}{op}/>'
    )
 
 
# ── Arrow helpers ──────────────────────────────────────────────────────────────
def arrow_marker_id(color: str) -> str:
    return "ah" + color.lstrip("#")
 
 
def arrow_defs(arrows: list) -> str:
    seen = {}
    for a in arrows:
        color = a.get("color", "#cc2200")
        tip   = a.get("tip", 7)
        seen[color] = tip
    parts = []
    for color, tip in seen.items():
        mid = arrow_marker_id(color)
        parts.append(
            f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="{tip}" markerHeight="{tip}" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/>'
            f'</marker>'
        )
    return "<defs>" + "".join(parts) + "</defs>" if parts else ""
 
 
def arrow_el(a: dict) -> str:
    color = a.get("color", "#cc2200")
    width = a.get("width", 4)
    mid   = arrow_marker_id(color)
    return (
        f'<line x1="{a["x1"]:.1f}" y1="{a["y1"]:.1f}" '
        f'x2="{a["x2"]:.1f}" y2="{a["y2"]:.1f}" '
        f'stroke="{color}" stroke-width="{width}" stroke-linecap="round" '
        f'marker-end="url(#{mid})"/>'
    )
 
 
# ── Bounding box helper ───────────────────────────────────────────────────────
def tight_viewbox(polys_map: dict, padding: float = 4.0,
                  faces: set | None = None) -> tuple[float,float,float,float]:
    """Return (x, y, width, height) tightly wrapping all polygon points.

    ``faces`` – if given, only consider polygons for those face keys.
    """
    all_x, all_y = [], []
    for face_key, face_data in polys_map.items():
        if faces is not None and face_key not in faces:
            continue
        for row in face_data:
            for pts in row:
                for pair in pts.split():
                    px, py = pair.split(",")
                    all_x.append(float(px))
                    all_y.append(float(py))
    x = min(all_x) - padding
    y = min(all_y) - padding
    w = max(all_x) - min(all_x) + padding * 2
    h = max(all_y) - min(all_y) + padding * 2
    return x, y, w, h
 
 
# ── Main SVG builder ──────────────────────────────────────────────────────────
def build_svg(cube_data: dict, highlight_data: dict | None,
              orientation: str, arrows: list,
              no_hidden: bool = False) -> str:
    """Build an SVG string for a cube state.

    Parameters
    ----------
    no_hidden:
        When True, the three hidden/back layers (L, D, B for the right-hand
        orientation; R, D, B for the left-hand orientation) are omitted
        entirely.  The viewBox is tightened to the visible faces only.
    """
    ori = orientation if orientation in ("right", "left") else "right"
    order = DRAW_ORDER[ori]
    polys_map = POLYGONS[ori]
 
    # json_state["cube"] keyed by face letter (U L F R B D)
    face_colors = cube_data  # already the inner cube dict

    # Determine which faces to include in the viewBox / draw pass
    visible_faces: set | None = None
    if no_hidden:
        visible_faces = {face for face, hidden, _ in order if not hidden}

    vx, vy, vw, vh = tight_viewbox(polys_map, faces=visible_faces)
    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' "
             f"width='{vw:.1f}' height='{vh:.1f}' "
             f"viewBox='{vx:.1f} {vy:.1f} {vw:.1f} {vh:.1f}'>"]
 
    # Arrow defs
    if arrows:
        parts.append(arrow_defs(arrows))
 
    for face, hidden, dashed in order:
        # Skip the hidden layers when --no-hidden is requested
        if no_hidden and hidden:
            continue
        face_grid = face_colors.get(face, [])
        for r in range(3):
            row = face_grid[r] if r < len(face_grid) else []
            for c in range(3):
                pts = polys_map[face][r][c]
                code = row[c] if c < len(row) else "X"
                fill = resolve_color(code, set(), face, r, c)
                if hidden:
                    # Use actual sticker color but ghosted — muted stroke, reduced opacity
                    parts.append(poly_el(pts, fill, HIDDEN_STROKE,
                                         HIDDEN_STROKE_WIDTH, dashed=dashed,
                                         opacity=1))
                else:
                    parts.append(poly_el(pts, fill, "#111111", 2.0))
                    # Highlight overlay
                    if is_highlighted(highlight_data, face, r, c):
                        parts.append(poly_el(pts, "#FFFF00", "#FFD500",
                                              2.0, opacity=0.45))
 
    # Arrows on top
    for a in arrows:
        parts.append(arrow_el(a))
 
    parts.append("</svg>")
    return "\n".join(parts)
 
 
# ── PNG export ────────────────────────────────────────────────────────────────
def svg_to_png(svg_str: str, out_path: str, size: int):
    try:
        import cairosvg
    except ImportError:
        print("[error] cairosvg not installed.  Run:  pip install cairosvg")
        sys.exit(1)
 
    # Parse actual SVG dimensions so the output matches the tight viewBox
    import re as _re
    m = _re.search(r"width='([\d.]+)'.*?height='([\d.]+)'", svg_str)
    if m:
        svg_w, svg_h = float(m.group(1)), float(m.group(2))
    else:
        svg_w, svg_h = 500.0, 360.0
    scale  = size / max(svg_w, svg_h)
    out_w  = round(svg_w * scale)
    out_h  = round(svg_h * scale)
 
    cairosvg.svg2png(
        bytestring=svg_str.encode("utf-8"),
        write_to=out_path,
        output_width=out_w,
        output_height=out_h,
        background_color="transparent",
    )
 
 
# ── DB fetch ──────────────────────────────────────────────────────────────────
def fetch_states(slugs=None, method=None, category=None):
    from cube.models import CubeState   # import after django.setup()
    qs = CubeState.objects.all()
    if slugs:
        qs = qs.filter(slug__in=slugs)
    if method:
        qs = qs.filter(method=method)
    if category:
        qs = qs.filter(category=category)
    return list(qs.order_by("method", "category", "step_number"))
 
 
# ── Arrow loading ─────────────────────────────────────────────────────────────
def load_arrows(arrow_arg: str | None) -> list:
    if not arrow_arg:
        return []
    # Could be a file path or an inline JSON string
    if os.path.isfile(arrow_arg):
        with open(arrow_arg) as f:
            data = json.load(f)
    else:
        try:
            data = json.loads(arrow_arg)
        except json.JSONDecodeError as e:
            print(f"[error] Could not parse --arrows value: {e}")
            sys.exit(1)
 
    required = {"x1", "y1", "x2", "y2"}
    for i, a in enumerate(data):
        missing = required - a.keys()
        if missing:
            print(f"[error] Arrow #{i} is missing fields: {missing}")
            sys.exit(1)
    return data
 
 
# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Export CubeState PNGs with optional arrow overlays.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("slugs", nargs="*",
                        help="One or more CubeState slugs to export")
    parser.add_argument("--method",   help="Filter by method (e.g. cfop)")
    parser.add_argument("--category", help="Filter by category (e.g. corner-in-slot)")
    parser.add_argument("--arrows",
                        help="Path to arrows JSON file or inline JSON array string")
    parser.add_argument("--size", type=int, default=500,
                        help="Output width in pixels (height scales to 72%% of width). Default: 500")
    parser.add_argument("--output", default="cube_state_png",
                        help="Output directory. Default: ./cube_state_png")
    parser.add_argument("--django-settings",
                        default="francontcube.settings",
                        help="Django settings module. Default: francontcube.settings")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be exported without writing files")
    parser.add_argument("--no-hidden", action="store_true",
                        help="Omit the three hidden/back layers (L, D, B for right-hand; "
                             "R, D, B for left-hand orientation). The output canvas is "
                             "tightened to the three visible faces only.")
    args = parser.parse_args()
 
    if not args.slugs and not args.method and not args.category:
        parser.error("Provide at least one slug, --method, or --category.")
 
    setup_django(args.django_settings)
 
    states = fetch_states(
        slugs=args.slugs or None,
        method=args.method,
        category=args.category,
    )
 
    if not states:
        print("[warn] No CubeState records matched your query.")
        return
 
    arrows = load_arrows(args.arrows)
    os.makedirs(args.output, exist_ok=True)
 
    print(f"Exporting {len(states)} cube state(s) → '{args.output}' "
          f"at {args.size}px wide …")
    if arrows:
        print(f"  Arrow overlay: {len(arrows)} arrow(s)")
    if args.no_hidden:
        print("  Hidden layers (L/D/B) will be omitted")
    print()
 
    for cs in states:
        raw = cs.json_state
        # Support both {"cube": {...}} and raw {face: [[...]]} formats
        if isinstance(raw, dict) and "cube" in raw:
            cube_data      = raw["cube"]
            highlight_data = raw.get("highlight") or cs.json_highlight
        else:
            cube_data      = raw
            highlight_data = cs.json_highlight
 
        filename = f"{cs.slug}.png"
        out_path = os.path.join(args.output, filename)
 
        if args.dry_run:
            hidden_tag = " no-hidden" if args.no_hidden else ""
            print(f"  [dry-run] {filename}  (ori={cs.hand_orientation}{hidden_tag})")
            continue
 
        svg_str = build_svg(
            cube_data=cube_data,
            highlight_data=highlight_data,
            orientation=cs.hand_orientation,
            arrows=arrows,
            no_hidden=args.no_hidden,
        )
        svg_to_png(svg_str, out_path, args.size)
        print(f"  ✓ {filename}  (ori={cs.hand_orientation})")
 
    if not args.dry_run:
        print(f"\nDone! {len(states)} PNG(s) saved to '{args.output}'.")
 
 
if __name__ == "__main__":
    main()