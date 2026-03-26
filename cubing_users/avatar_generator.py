"""
avatar_generator.py
Génère des avatars SVG pour les cubeurs à partir des constantes
couleur / adjectif (forme) / héros (animal).
"""

import math
import random
from typing import Callable


# ──────────────────────────────────────────────
# Palette de couleurs
# ──────────────────────────────────────────────

COLORS: dict[str, dict[str, str]] = {
    "Rouge":  {"main": "#E24B4A", "light": "#FCEBEB"},
    "Bleu":   {"main": "#378ADD", "light": "#E6F1FB"},
    "Vert":   {"main": "#639922", "light": "#EAF3DE"},
    "Jaune":  {"main": "#EF9F27", "light": "#FAEEDA"},
    "Orange": {"main": "#D85A30", "light": "#FAECE7"},
    "Blanc":  {"main": "#888780", "light": "#F1EFE8"},
}

# Teintes fixes pour les détails des animaux
_DK = "#160e06"       # sombre (pupilles, contours)
_WH = "rgba(255,255,255,0.72)"  # blanc semi-transparent


# ──────────────────────────────────────────────
# Helpers géométriques
# ──────────────────────────────────────────────

def _f(n: float) -> str:
    return f"{n:.1f}"


def _poly(n: int, r: float = 52, cx: float = 60, cy: float = 60,
          a0: float | None = None) -> str:
    """Polygone régulier à n côtés."""
    if a0 is None:
        a0 = -math.pi / 2
    pts = []
    for i in range(n):
        a = a0 + 2 * math.pi * i / n
        pts.append(f"{_f(cx + r * math.cos(a))},{_f(cy + r * math.sin(a))}")
    return "M" + "L".join(pts) + "Z"


def _star(n: int, ro: float = 52, ri: float = 24,
          a0: float | None = None) -> str:
    """Étoile à n branches."""
    if a0 is None:
        a0 = -math.pi / 2
    pts = []
    for i in range(n * 2):
        a = a0 + math.pi * i / n
        r = ri if i % 2 else ro
        pts.append(f"{_f(60 + r * math.cos(a))},{_f(60 + r * math.sin(a))}")
    return "M" + "L".join(pts) + "Z"


# ──────────────────────────────────────────────
# 12 formes de cadre (adjectifs)
# ──────────────────────────────────────────────

FRAMES: dict[str, str] = {
    "Rapide":   "M62,8 L40,62 L60,62 L44,112 L54,112 L80,58 L62,58 L72,8 Z",
    "Turbo":    "M60,8 A52,52 0 1,1 60,112 A52,52 0 1,1 60,8 Z",
    "Génial":   _star(5, 52, 22),
    "Brillant": _poly(4, 52, 60, 60, 0),
    "Habile":   _poly(6, 52),
    "Malin":    _poly(5, 52),
    "Super":    "M14,12 L106,12 L106,72 Q106,108 60,118 Q14,108 14,72 Z",
    "Doué":     "M22,8 L98,8 Q112,8 112,22 L112,98 Q112,112 98,112 L22,112 Q8,112 8,98 L8,22 Q8,8 22,8 Z",
    "Véloce":   _poly(3, 52),
    "Ultime":   _star(8, 52, 26),
    "Rusé":     _poly(8, 52),
    "Adroit":   _star(6, 52, 26),
}


# ──────────────────────────────────────────────
# 12 animaux (héros) — fonctions de dessin SVG
# ──────────────────────────────────────────────

def _renard(c: str) -> str:
    return f"""
<circle cx="60" cy="70" r="30" fill="{c}"/>
<polygon points="28,54 42,14 56,54" fill="{c}"/>
<polygon points="92,54 78,14 64,54" fill="{c}"/>
<polygon points="32,52 42,20 52,52" fill="{_WH}"/>
<polygon points="88,52 78,20 68,52" fill="{_WH}"/>
<ellipse cx="60" cy="84" rx="16" ry="11" fill="{_WH}"/>
<circle cx="48" cy="65" r="6" fill="{_DK}"/>
<circle cx="72" cy="65" r="6" fill="{_DK}"/>
<circle cx="50" cy="63" r="2" fill="white"/>
<circle cx="74" cy="63" r="2" fill="white"/>
<ellipse cx="60" cy="78" rx="4" ry="3" fill="{_DK}"/>
"""


def _hibou(c: str) -> str:
    return f"""
<ellipse cx="60" cy="78" rx="28" ry="30" fill="{c}"/>
<circle cx="60" cy="46" r="26" fill="{c}"/>
<polygon points="38,28 33,6 50,28" fill="{c}"/>
<polygon points="82,28 87,6 70,28" fill="{c}"/>
<circle cx="46" cy="46" r="14" fill="{_WH}"/>
<circle cx="74" cy="46" r="14" fill="{_WH}"/>
<circle cx="46" cy="46" r="8" fill="{_DK}"/>
<circle cx="74" cy="46" r="8" fill="{_DK}"/>
<circle cx="48" cy="44" r="2.5" fill="white"/>
<circle cx="76" cy="44" r="2.5" fill="white"/>
<polygon points="60,56 54,66 66,66" fill="{_DK}" opacity=".5"/>
<path d="M38,80 Q50,70 60,80 Q70,70 82,80" fill="none" stroke="{_DK}" stroke-width="1.5" opacity=".25"/>
"""


def _lion(c: str) -> str:
    return f"""
<circle cx="60" cy="68" r="40" fill="{c}" opacity=".42"/>
<circle cx="60" cy="64" r="26" fill="{c}"/>
<circle cx="40" cy="30" r="10" fill="{c}"/>
<circle cx="80" cy="30" r="10" fill="{c}"/>
<circle cx="40" cy="30" r="5" fill="{_WH}"/>
<circle cx="80" cy="30" r="5" fill="{_WH}"/>
<ellipse cx="60" cy="76" rx="14" ry="9" fill="{_WH}"/>
<circle cx="50" cy="60" r="6" fill="{_DK}"/>
<circle cx="70" cy="60" r="6" fill="{_DK}"/>
<circle cx="52" cy="58" r="2" fill="white"/>
<circle cx="72" cy="58" r="2" fill="white"/>
<ellipse cx="60" cy="71" rx="5" ry="3.5" fill="{_DK}"/>
<path d="M50,80 Q60,87 70,80" fill="none" stroke="{_DK}" stroke-width="2" stroke-linecap="round"/>
"""


def _pieuvre(c: str) -> str:
    return f"""
<path d="M38,58 Q22,72 28,94" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<path d="M46,64 Q32,80 38,106" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<path d="M54,67 Q48,88 54,112" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<path d="M66,67 Q72,88 66,112" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<path d="M74,64 Q88,80 82,106" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<path d="M82,58 Q98,72 92,94" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
<ellipse cx="60" cy="40" rx="30" ry="26" fill="{c}"/>
<circle cx="47" cy="36" r="10" fill="{_WH}"/>
<circle cx="73" cy="36" r="10" fill="{_WH}"/>
<circle cx="47" cy="36" r="6" fill="{_DK}"/>
<circle cx="73" cy="36" r="6" fill="{_DK}"/>
<circle cx="49" cy="34" r="2" fill="white"/>
<circle cx="75" cy="34" r="2" fill="white"/>
"""


def _gecko(c: str) -> str:
    return f"""
<ellipse cx="60" cy="68" rx="14" ry="26" fill="{c}"/>
<ellipse cx="60" cy="38" rx="17" ry="15" fill="{c}"/>
<path d="M46,56 Q16,42 8,52 Q6,62 14,64 Q14,72 10,80" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M74,56 Q104,42 112,52 Q114,62 106,64 Q106,72 110,80" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M46,76 Q14,90 10,100 Q12,108 22,104 Q24,112 18,118" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M74,76 Q106,90 110,100 Q108,108 98,104 Q96,112 102,118" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M60,94 Q68,108 64,120" stroke="{c}" stroke-width="7" fill="none" stroke-linecap="round"/>
<circle cx="50" cy="34" r="8" fill="{_WH}"/>
<circle cx="70" cy="34" r="8" fill="{_WH}"/>
<circle cx="50" cy="34" r="5" fill="{_DK}"/>
<circle cx="70" cy="34" r="5" fill="{_DK}"/>
<circle cx="52" cy="32" r="1.5" fill="white"/>
<circle cx="72" cy="32" r="1.5" fill="white"/>
"""


def _guepard(c: str) -> str:
    return f"""
<ellipse cx="60" cy="68" rx="28" ry="32" fill="{c}"/>
<polygon points="30,40 37,10 50,40" fill="{c}"/>
<polygon points="90,40 83,10 70,40" fill="{c}"/>
<circle cx="38" cy="25" r="5" fill="{_WH}"/>
<circle cx="82" cy="25" r="5" fill="{_WH}"/>
<ellipse cx="60" cy="82" rx="13" ry="9" fill="{_WH}"/>
<ellipse cx="48" cy="58" rx="8" ry="7" fill="{_DK}"/>
<ellipse cx="72" cy="58" rx="8" ry="7" fill="{_DK}"/>
<circle cx="50" cy="56" r="2.5" fill="white"/>
<circle cx="74" cy="56" r="2.5" fill="white"/>
<path d="M46,68 Q43,78 45,90" fill="none" stroke="{_DK}" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>
<path d="M74,68 Q77,78 75,90" fill="none" stroke="{_DK}" stroke-width="2.5" stroke-linecap="round" opacity=".7"/>
<circle cx="60" cy="44" r="3" fill="{_DK}" opacity=".35"/>
<circle cx="49" cy="46" r="2.5" fill="{_DK}" opacity=".35"/>
<circle cx="71" cy="46" r="2.5" fill="{_DK}" opacity=".35"/>
<ellipse cx="60" cy="74" rx="5" ry="3.5" fill="{_DK}"/>
<path d="M53,80 Q60,87 67,80" fill="none" stroke="{_DK}" stroke-width="2" stroke-linecap="round"/>
"""


def _dragon(c: str) -> str:
    return f"""
<ellipse cx="60" cy="72" rx="30" ry="32" fill="{c}"/>
<polygon points="40,44 34,8 54,42" fill="{c}"/>
<polygon points="80,44 86,8 66,42" fill="{c}"/>
<polygon points="38,26 34,8 44,20" fill="{_DK}" opacity=".22"/>
<polygon points="82,26 86,8 76,20" fill="{_DK}" opacity=".22"/>
<path d="M40,54 Q50,44 60,46 Q70,44 80,54" fill="none" stroke="{_DK}" stroke-width="1.5" opacity=".3"/>
<ellipse cx="46" cy="63" rx="9" ry="8" fill="white" opacity=".6"/>
<ellipse cx="74" cy="63" rx="9" ry="8" fill="white" opacity=".6"/>
<ellipse cx="46" cy="63" rx="3.5" ry="7" fill="{_DK}"/>
<ellipse cx="74" cy="63" rx="3.5" ry="7" fill="{_DK}"/>
<ellipse cx="54" cy="80" rx="4" ry="2.5" fill="{_DK}" opacity=".6"/>
<ellipse cx="66" cy="80" rx="4" ry="2.5" fill="{_DK}" opacity=".6"/>
<path d="M44,90 Q60,100 76,90" fill="none" stroke="{_DK}" stroke-width="2.5" stroke-linecap="round"/>
<line x1="52" y1="91" x2="50" y2="99" stroke="white" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>
<line x1="60" y1="93" x2="60" y2="101" stroke="white" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>
<line x1="68" y1="91" x2="70" y2="99" stroke="white" stroke-width="2.5" stroke-linecap="round" opacity=".8"/>
"""


def _serpent(c: str) -> str:
    return f"""
<path d="M84,28 Q100,46 84,62 Q68,78 80,96 Q90,108 78,116" fill="none" stroke="{c}" stroke-width="11" stroke-linecap="round"/>
<path d="M84,28 Q68,12 48,22 Q28,32 34,54 Q40,74 60,80 Q80,86 78,104" fill="none" stroke="{c}" stroke-width="11" stroke-linecap="round"/>
<ellipse cx="84" cy="24" rx="14" ry="11" fill="{c}"/>
<circle cx="90" cy="20" r="4.5" fill="{_DK}"/>
<circle cx="91.5" cy="18.5" r="1.5" fill="white"/>
<path d="M98,28 L108,23 M108,23 L112,19 M108,23 L112,27" fill="none" stroke="{_DK}" stroke-width="1.5" stroke-linecap="round"/>
"""


def _raton(c: str) -> str:
    return f"""
<circle cx="60" cy="64" r="32" fill="{c}"/>
<circle cx="36" cy="34" r="14" fill="{c}"/>
<circle cx="84" cy="34" r="14" fill="{c}"/>
<circle cx="36" cy="34" r="7" fill="{_DK}" opacity=".28"/>
<circle cx="84" cy="34" r="7" fill="{_DK}" opacity=".28"/>
<ellipse cx="46" cy="60" rx="13" ry="10" fill="{_DK}" opacity=".65"/>
<ellipse cx="74" cy="60" rx="13" ry="10" fill="{_DK}" opacity=".65"/>
<rect x="54" y="54" width="12" height="6" fill="{_DK}" opacity=".65" rx="1"/>
<ellipse cx="46" cy="60" rx="7" ry="6" fill="white" opacity=".82"/>
<ellipse cx="74" cy="60" rx="7" ry="6" fill="white" opacity=".82"/>
<circle cx="46" cy="60" r="4" fill="{_DK}"/>
<circle cx="74" cy="60" r="4" fill="{_DK}"/>
<circle cx="48" cy="58" r="1.5" fill="white"/>
<circle cx="76" cy="58" r="1.5" fill="white"/>
<ellipse cx="60" cy="76" rx="14" ry="10" fill="{_WH}"/>
<ellipse cx="60" cy="72" rx="5" ry="4" fill="{_DK}"/>
<path d="M54,80 Q60,86 66,80" fill="none" stroke="{_DK}" stroke-width="2" stroke-linecap="round"/>
"""


def _cameleon(c: str) -> str:
    return f"""
<ellipse cx="58" cy="74" rx="30" ry="22" fill="{c}"/>
<ellipse cx="26" cy="60" rx="20" ry="17" fill="{c}"/>
<polygon points="26,43 12,28 40,28" fill="{c}"/>
<polygon points="26,43 18,26 34,26" fill="{c}" opacity=".65"/>
<circle cx="14" cy="56" r="12" fill="{_WH}"/>
<circle cx="14" cy="56" r="7" fill="{_DK}"/>
<circle cx="16" cy="54" r="2.5" fill="white"/>
<path d="M6,66 L36,62" stroke="{_DK}" stroke-width="2" stroke-linecap="round" opacity=".4"/>
<path d="M40,88 Q32,100 28,102" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M58,92 Q50,106 46,108" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M74,86 Q82,98 88,98" stroke="{c}" stroke-width="5" fill="none" stroke-linecap="round"/>
<path d="M88,74 Q108,70 112,52 Q114,36 102,32 Q90,28 88,42 Q86,52 96,52" fill="none" stroke="{c}" stroke-width="8" stroke-linecap="round"/>
"""


def _perroquet(c: str) -> str:
    return f"""
<ellipse cx="60" cy="80" rx="24" ry="28" fill="{c}"/>
<circle cx="60" cy="46" r="24" fill="{c}"/>
<path d="M48,22 Q52,5 60,3 Q68,5 72,22" fill="{c}"/>
<line x1="52" y1="22" x2="50" y2="5" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<line x1="60" y1="22" x2="60" y2="4" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<line x1="68" y1="22" x2="70" y2="5" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<circle cx="44" cy="44" r="9" fill="{_WH}"/>
<circle cx="76" cy="44" r="9" fill="{_WH}"/>
<circle cx="44" cy="44" r="5.5" fill="{_DK}"/>
<circle cx="76" cy="44" r="5.5" fill="{_DK}"/>
<circle cx="46" cy="42" r="1.8" fill="white"/>
<circle cx="78" cy="42" r="1.8" fill="white"/>
<path d="M50,56 Q56,60 60,64 Q64,60 70,56 Q70,68 60,72 Q50,68 50,56 Z" fill="{_DK}" opacity=".72"/>
"""


def _araignee(c: str) -> str:
    return f"""
<line x1="60" y1="8" x2="60" y2="112" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<line x1="8" y1="60" x2="112" y2="60" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<line x1="18" y1="18" x2="102" y2="102" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<line x1="102" y1="18" x2="18" y2="102" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<circle cx="60" cy="60" r="18" fill="none" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<circle cx="60" cy="60" r="34" fill="none" stroke="{c}" stroke-width="0.6" opacity=".2"/>
<path d="M32,50 L8,34" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M28,60 L4,54" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M28,70 L4,76" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M32,80 L8,96" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M88,50 L112,34" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M92,60 L116,54" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M92,70 L116,76" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<path d="M88,80 L112,96" stroke="{c}" stroke-width="5" stroke-linecap="round"/>
<circle cx="60" cy="68" r="20" fill="{c}"/>
<circle cx="60" cy="46" r="14" fill="{c}"/>
<circle cx="52" cy="42" r="3.5" fill="{_DK}"/>
<circle cx="60" cy="40" r="3.5" fill="{_DK}"/>
<circle cx="68" cy="42" r="3.5" fill="{_DK}"/>
<circle cx="54" cy="49" r="2.5" fill="{_DK}"/>
<circle cx="66" cy="49" r="2.5" fill="{_DK}"/>
<circle cx="53" cy="41" r="1.2" fill="white"/>
<circle cx="61" cy="39" r="1.2" fill="white"/>
<circle cx="69" cy="41" r="1.2" fill="white"/>
"""


# Mapping héros → fonction de dessin
ANIMALS: dict[str, Callable[[str], str]] = {
    "Solveur":   _renard,
    "Maître":    _hibou,
    "Champion":  _lion,
    "Cubeur":    _pieuvre,
    "Ninja":     _gecko,
    "Pro":       _guepard,
    "Légende":   _dragon,
    "Twisteur":  _serpent,
    "Magicien":  _raton,
    "Tourneur":  _cameleon,
    "Mélangeur": _perroquet,
    "Démêleur":  _araignee,
}


# ──────────────────────────────────────────────
# Fonction principale
# ──────────────────────────────────────────────

def generate_avatar(
    color: str,
    adjective: str,
    hero: str,
    size: int = 200,
) -> str:
    """
    Génère un avatar SVG complet.

    Paramètres
    ----------
    color     : clé de COLORS  — ex. "Rouge"
    adjective : clé de FRAMES  — ex. "Rapide"
    hero      : clé de ANIMALS — ex. "Solveur"
    size      : dimension en pixels du SVG final

    Retourne
    --------
    Chaîne SVG complète, prête à écrire dans un fichier ou à
    injecter directement dans un template HTML Django.
    """
    if color not in COLORS:
        raise ValueError(f"Couleur inconnue: {color!r}. Choix: {list(COLORS)}")
    if adjective not in FRAMES:
        raise ValueError(f"Adjectif inconnu: {adjective!r}. Choix: {list(FRAMES)}")
    if hero not in ANIMALS:
        raise ValueError(f"Héros inconnu: {hero!r}. Choix: {list(ANIMALS)}")

    clip_id = f"clip_{color[:2]}_{adjective[:3]}_{hero[:3]}"
    palette = COLORS[color]
    frame_path = FRAMES[adjective]
    animal_svg = ANIMALS[hero](palette["main"])

    return f"""<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}">
  <defs>
    <clipPath id="{clip_id}">
      <path d="{frame_path}"/>
    </clipPath>
  </defs>
  <!-- Fond coloré clippé dans la forme -->
  <rect x="0" y="0" width="120" height="120" fill="{palette['light']}" clip-path="url(#{clip_id})"/>
  <!-- Animal clipé dans la même forme -->
  <g clip-path="url(#{clip_id})">
    {animal_svg}
  </g>
  <!-- Bordure de la forme -->
  <path d="{frame_path}" fill="none" stroke="{palette['main']}" stroke-width="5.5"/>
</svg>"""


def random_avatar(size: int = 200) -> tuple[str, str, str, str]:
    """
    Génère un avatar aléatoire.

    Retourne
    --------
    (svg_string, color, adjective, hero)
    """
    color = random.choice(list(COLORS))
    adjective = random.choice(list(FRAMES))
    hero = random.choice(list(ANIMALS))
    svg = generate_avatar(color, adjective, hero, size)
    return svg, color, adjective, hero


# ──────────────────────────────────────────────
# Intégration Django — CubingUser model
# ──────────────────────────────────────────────
#
# Dans cubing_users/models.py :
#
#   from .avatar_generator import generate_avatar
#
#   class CubingUser(AbstractUser):
#       color     = models.CharField(max_length=16, choices=[(k,k) for k in COLORS])
#       adjective = models.CharField(max_length=32, choices=[(k,k) for k in FRAMES])
#       hero      = models.CharField(max_length=32, choices=[(k,k) for k in ANIMALS])
#
#       @property
#       def avatar_svg(self) -> str:
#           return generate_avatar(self.color, self.adjective, self.hero)
#
#       @property
#       def avatar_name(self) -> str:
#           return f"{self.adjective} {self.hero} {self.color}"
#
#
# Dans un template Django :
#   {{ user.avatar_svg|safe }}
#
# Pour assigner aléatoirement à la création :
#   import random
#   user.color     = random.choice(list(COLORS))
#   user.adjective = random.choice(list(FRAMES))
#   user.hero      = random.choice(list(ANIMALS))


# ──────────────────────────────────────────────
# Script de test — génère un fichier SVG local
# ──────────────────────────────────────────────

if __name__ == "__main__":
    # Test d'un avatar spécifique
    svg = generate_avatar("Bleu", "Ultime", "Légende", size=400)
    with open("test_avatar.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print("✅ test_avatar.svg généré — Ultime Légende Bleu")

    # Test aléatoire
    svg2, col, adj, hero = random_avatar(400)
    with open("test_avatar_random.svg", "w", encoding="utf-8") as f:
        f.write(svg2)
    print(f"✅ test_avatar_random.svg généré — {adj} {hero} {col}")

    # Vérification de toutes les combinaisons (144 = 6×12×12... / 12 formes × 12 animaux)
    errors = []
    for c in COLORS:
        for a in FRAMES:
            for h in ANIMALS:
                try:
                    generate_avatar(c, a, h)
                except Exception as e:
                    errors.append(f"{c}/{a}/{h}: {e}")
    if errors:
        print(f"❌ {len(errors)} erreurs:")
        for e in errors:
            print(f"  {e}")
    else:
        combos = len(COLORS) * len(FRAMES) * len(ANIMALS)
        print(f"✅ {combos} combinaisons générées sans erreur")