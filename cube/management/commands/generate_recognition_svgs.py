# cube/management/commands/generate_recognition_svgs.py
"""
Génère les diagrammes SVG de reconnaissance (vue du dessus + flancs) pour
chaque CubeState de Cubie-Curieux (2-Look OLL et PLL), à partir du template
francontcube_recognition_template.svg.

La simulation (pycuber, dépendance dev-only — jamais dans requirements.txt
de production) est la source de vérité : la couleur de chaque sticker et
les flèches de permutation sont calculées directement depuis l'algorithme,
jamais saisies à la main — donc jamais désynchronisées si un algorithme
est corrigé plus tard.

Usage:
    python manage.py generate_recognition_svgs
    python manage.py generate_recognition_svgs --slug cc-pll-aa   # un seul cas

Prérequis (dev uniquement) :
    pip install pycuber
    Copier francontcube_recognition_template.svg dans
    cube/static/cube/francontcube_recognition_template.svg
"""

import os
import re
import pycuber as pc
from django.conf import settings
from django.core.management.base import BaseCommand
from cube.models import CubeState

TEMPLATE_PATH = os.path.join(
    settings.BASE_DIR, 'cube', 'static', 'cube', 'francontcube_recognition_template.svg'
)
OUTPUT_DIR = os.path.join(settings.BASE_DIR, 'cube', 'static', 'cube', 'recognition')

# ── Schéma de couleurs réel de FrancontCube : U = BLANC ──────────────────
FACE_TO_COLOUR = {'U': 'white', 'D': 'yellow', 'F': 'green', 'B': 'blue', 'R': 'red', 'L': 'orange'}
PYCUBER_ORIGIN = {'yellow': 'U', 'white': 'D', 'green': 'F', 'blue': 'B', 'orange': 'R', 'red': 'L'}
PYCUBER_TO_DANIEL = {pyc: FACE_TO_COLOUR[face] for pyc, face in PYCUBER_ORIGIN.items()}

# Points d'ancrage des flèches, dans la grille 3x3 de la face U uniquement
ANCHORS = {
    'LUB': (176, 120), 'RUB': (352, 120), 'LUF': (176, 296), 'RUF': (352, 296),
    'UB': (264, 120), 'LU': (176, 208), 'RU': (352, 208), 'UF': (264, 296),
}


def sticker_colours(cube):
    """
    Lecture directe des facelets (pas de tracking d'identité ici).
    Indexation vérifiée empiriquement :
      - U : rangée0=arrière, rangée2=avant, col0=gauche, col2=droite
      - F, L : correspondance directe avec le template
      - R, B : colonnes INVERSÉES par rapport au template (piège classique
        des conventions pycuber/cubing.js — vérifié par simulation, pas deviné)
    """
    u = cube.get_face('U')
    f = cube.get_face('F')[0]
    l = cube.get_face('L')[0]
    r = list(reversed(cube.get_face('R')[0]))
    b = list(reversed(cube.get_face('B')[0]))

    def c(sq):
        return PYCUBER_TO_DANIEL[str(sq.colour)]

    return {
        'u00': c(u[0][0]), 'u01': c(u[0][1]), 'u02': c(u[0][2]),
        'u10': c(u[1][0]), 'u11': c(u[1][1]), 'u12': c(u[1][2]),
        'u20': c(u[2][0]), 'u21': c(u[2][1]), 'u22': c(u[2][2]),
        'f0': c(f[0]), 'f1': c(f[1]), 'f2': c(f[2]),
        'l0': c(l[0]), 'l1': c(l[1]), 'l2': c(l[2]),
        'r0': c(r[0]), 'r1': c(r[1]), 'r2': c(r[2]),
        'b0': c(b[0]), 'b1': c(b[1]), 'b2': c(b[2]),
    }


def build_identity_index(cube):
    """
    home identity ('RUF', 'UF', ...) -> position actuelle, retrouvée par
    signature de couleurs (constante peu importe où la pièce se déplace).
    """
    solved = pc.Cube()
    home_by_sig = {}
    for piece in solved.children:
        if type(piece).__name__ in ('Corner', 'Edge'):
            sig = frozenset(str(x) for x in piece.facings.values())
            home_by_sig[sig] = piece.location

    current_home_to_loc = {}
    for piece in cube.children:
        if type(piece).__name__ in ('Corner', 'Edge'):
            sig = frozenset(str(x) for x in piece.facings.values())
            home = home_by_sig[sig]
            current_home_to_loc[home] = piece.location
    return current_home_to_loc


def render_svg(algorithm, kind):
    """kind: 'oll' ou 'pll'. Les flèches ne sont générées que pour 'pll'."""
    setup = CubeState.invert_alg(algorithm)
    cube = pc.Cube()
    if setup.strip():
        cube(pc.Formula(setup))

    colours = sticker_colours(cube)
    svg = open(TEMPLATE_PATH).read()

    for sid, colour in colours.items():
        if sid.startswith('u'):
            # Face U : blanc si correct, gris neutre sinon (abstrait, comme
            # les diagrammes OLL classiques -- la couleur réelle n'a pas
            # d'importance tant que la pièce n'est pas orientée)
            css_class = 'white' if colour == 'white' else 'neutral'
        else:
            # Flancs (f/l/r/b) : toujours la vraie couleur -- c'est ce qui
            # révèle les "phares" (OLL) et les pièces mal placées (PLL)
            css_class = colour
        svg = re.sub(
            rf'(id="{sid}"[^>]*class=")sticker [a-z]+(")',
            rf'\1sticker {css_class}\2',
            svg,
        )

    arrows_svg = ''
    if kind == 'pll':
        idx = build_identity_index(cube)
        paths = []
        for home, current in idx.items():
            if home not in ANCHORS or current == home:
                continue
            x1, y1 = ANCHORS[current]
            x2, y2 = ANCHORS[home]
            # Courbe quadratique qui s'arque vers l'extérieur du centre,
            # pour rester lisible même quand plusieurs flèches se croisent
            cx, cy = 264, 208
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            bow = 0.35
            ctrl_x = mx + (mx - cx) * bow
            ctrl_y = my + (my - cy) * bow
            paths.append(
                f'<path d="M {x1} {y1} Q {ctrl_x} {ctrl_y} {x2} {y2}" '
                f'fill="none" stroke="#1a1a1a" stroke-width="5" '
                f'marker-end="url(#arrowhead)" opacity="0.85"/>'
            )
        if paths:
            arrows_svg = (
                '<defs><marker id="arrowhead" markerWidth="10" markerHeight="10" '
                'refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#1a1a1a"/></marker></defs>'
                + ''.join(paths)
            )

    return svg.replace('</svg>', arrows_svg + '</svg>')


class Command(BaseCommand):
    help = "Génère les SVG de reconnaissance pour les CubeState Cubie-Curieux (OLL/PLL)"

    def add_arguments(self, parser):
        parser.add_argument('--slug', type=str, default=None, help="Ne générer qu'un seul cas")

    def handle(self, *args, **options):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        qs = CubeState.objects.filter(method='cubiecurieux', stickering__in=['OLL', 'PLL'])
        if options['slug']:
            qs = qs.filter(slug=options['slug'])

        if not qs.exists():
            self.stdout.write(self.style.WARNING(
                "Aucun CubeState trouvé (method='cubiecurieux', stickering in OLL/PLL). "
                "As-tu lancé load_cubiecurieux_2look d'abord ?"
            ))
            return

        for case in qs:
            kind = 'oll' if case.stickering == 'OLL' else 'pll'
            svg = render_svg(case.algorithm, kind)
            out_path = os.path.join(OUTPUT_DIR, f'{case.slug}.svg')
            with open(out_path, 'w') as fh:
                fh.write(svg)
            self.stdout.write(self.style.SUCCESS(f'{case.slug}.svg  ({kind})'))

        self.stdout.write(self.style.SUCCESS(f"\n{qs.count()} SVG générés dans {OUTPUT_DIR}"))