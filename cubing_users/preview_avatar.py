"""
preview_avatars.py
Génère un fichier preview.html pour tester visuellement tous les avatars.
Aucun Django requis — juste Python standard.

Usage:
    python preview_avatars.py            # génère preview.html et l'ouvre
    python preview_avatars.py --no-open  # génère sans ouvrir le navigateur
"""

import argparse
import webbrowser
from pathlib import Path

from avatar_generator import ANIMALS, COLORS, FRAMES, generate_avatar


def build_html() -> str:
    color_tabs = "\n".join(
        f'<button class="tab" data-color="{c}" onclick="showColor(this)">'
        f'<span class="dot" style="background:{COLORS[c]["main"]}"></span>{c}</button>'
        for c in COLORS
    )

    sections = []
    for color in COLORS:
        rows = []
        for hero in ANIMALS:
            cells = []
            for adj in FRAMES:
                svg = generate_avatar(color, adj, hero, size=160)
                label = f"{adj}"
                cells.append(
                    f'<div class="cell" title="{adj} {hero} {color}">'
                    f"{svg}"
                    f'<div class="cell-label">{label}</div>'
                    f"</div>"
                )
            rows.append(
                f'<div class="animal-row">'
                f'<div class="animal-name">{hero}</div>'
                f'<div class="cells">{"".join(cells)}</div>'
                f"</div>"
            )
        sections.append(
            f'<div class="color-section" data-color="{color}" style="display:none">'
            f'<div class="grid-header">'
            + "".join(
                f'<div class="col-label">{adj}</div>' for adj in FRAMES
            )
            + f"</div>"
            f"{''.join(rows)}"
            f"</div>"
        )

    first_color = list(COLORS)[0]

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <title>Prévisualisation avatars cubeurs</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: system-ui, sans-serif;
      font-size: 13px;
      background: #f5f4f0;
      color: #222;
      padding: 24px;
    }}
    h1 {{
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 4px;
    }}
    .subtitle {{
      color: #666;
      margin-bottom: 20px;
      font-size: 13px;
    }}
    .tabs {{
      display: flex;
      gap: 6px;
      margin-bottom: 20px;
      flex-wrap: wrap;
    }}
    .tab {{
      display: flex;
      align-items: center;
      gap: 7px;
      padding: 6px 14px;
      border: 1.5px solid #ccc;
      border-radius: 20px;
      background: white;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: border-color .15s, background .15s;
    }}
    .tab:hover {{ background: #f0efeb; }}
    .tab.active {{ border-color: #333; background: #333; color: white; }}
    .tab.active .dot {{ outline: 2px solid white; }}
    .dot {{
      width: 12px; height: 12px;
      border-radius: 50%;
      flex-shrink: 0;
    }}
    .grid-header {{
      display: flex;
      margin-left: 110px;
      margin-bottom: 6px;
      gap: 4px;
    }}
    .col-label {{
      width: 168px;
      font-size: 11px;
      color: #888;
      text-align: center;
      font-weight: 500;
    }}
    .animal-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 4px;
    }}
    .animal-name {{
      width: 100px;
      font-size: 12px;
      font-weight: 600;
      text-align: right;
      color: #444;
      flex-shrink: 0;
    }}
    .cells {{
      display: flex;
      gap: 4px;
      flex-wrap: wrap;
    }}
    .cell {{
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: pointer;
      padding: 3px;
      border-radius: 6px;
      transition: background .12s;
    }}
    .cell:hover {{ background: rgba(0,0,0,.07); }}
    .cell-label {{
      font-size: 9px;
      color: #aaa;
      margin-top: 2px;
      text-align: center;
      max-width: 160px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .cell:hover .cell-label {{ color: #555; }}
    .stats {{
      margin-top: 24px;
      padding: 12px 16px;
      background: white;
      border-radius: 10px;
      border: 1px solid #e0dfd9;
      font-size: 12px;
      color: #666;
      display: inline-block;
    }}
    .stats strong {{ color: #222; }}
  </style>
</head>
<body>
  <h1>Prévisualisation des avatars cubeurs</h1>
  <p class="subtitle">
    {len(COLORS)} couleurs × {len(FRAMES)} formes × {len(ANIMALS)} animaux
    = <strong>{len(COLORS) * len(FRAMES) * len(ANIMALS)} combinaisons</strong>
  </p>

  <div class="tabs">
    {color_tabs}
  </div>

  {''.join(sections)}

  <div class="stats">
    Fichier source: <strong>avatar_generator.py</strong> —
    Relancer <code>python preview_avatars.py</code> après chaque modification.
  </div>

  <script>
    function showColor(btn) {{
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.color-section').forEach(s => s.style.display = 'none');
      btn.classList.add('active');
      const col = btn.dataset.color;
      document.querySelector('.color-section[data-color="' + col + '"]').style.display = 'block';
    }}

    // Afficher la première couleur au chargement
    const first = document.querySelector('.tab[data-color="{first_color}"]');
    if (first) showColor(first);

    // Clic sur un avatar → affiche le nom complet dans la console
    document.querySelectorAll('.cell').forEach(cell => {{
      cell.addEventListener('click', () => {{
        console.log('Avatar sélectionné:', cell.title);
        document.title = cell.title;
      }});
    }});
  </script>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description="Génère preview.html des avatars")
    parser.add_argument("--no-open", action="store_true", help="Ne pas ouvrir le navigateur")
    parser.add_argument("--output", default="preview.html", help="Fichier de sortie")
    args = parser.parse_args()

    print("Génération des avatars...", end=" ", flush=True)
    html = build_html()
    out = Path(args.output)
    out.write_text(html, encoding="utf-8")

    total = len(COLORS) * len(FRAMES) * len(ANIMALS)
    print(f"✅  {total} avatars → {out.resolve()}")

    if not args.no_open:
        webbrowser.open(out.resolve().as_uri())
        print("🌐 Navigateur ouvert")


if __name__ == "__main__":
    main()