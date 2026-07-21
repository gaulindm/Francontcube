# cube/management/commands/load_cubiecurieux_2look.py
"""
Peuple les CubeState pour 2-Look OLL et 2-Look PLL (Cubie-Curieux).
Idempotent : rerun-able, met à jour les entrées existantes par slug.

Usage:
    python manage.py load_cubiecurieux_2look
"""

from django.core.management.base import BaseCommand
from cube.models import CubeState


# ── OLL : 4 catégories, 10 cas ──────────────────────────────────────────
OLL_CASES = [
    # -- croix (facile) --
    {
        'slug': 'cc-oll-point-croix', 'name': 'Point → Croix', 'category': 'croix',
        'step_number': 1, 'difficulty': 'facile',
        'algorithm': "F (R U R' U') F' f (R U R' U') f'",
        'description': 'Aucune arête blanche sur le dessus',
    },
    {
        'slug': 'cc-oll-ligne-croix', 'name': 'Ligne → Croix', 'category': 'croix',
        'step_number': 2, 'difficulty': 'facile',
        'algorithm': "F (R U R' U') F'",
        'description': 'Ligne horizontale blanche',
    },
    {
        'slug': 'cc-oll-forme-l-croix', 'name': 'Forme L → Croix', 'category': 'croix',
        'step_number': 3, 'difficulty': 'facile',
        'algorithm': "f (R U R' U') f'",
        'description': 'Forme L blanche à gauche',
    },
    # -- sune (moyen) --
    {
        'slug': 'cc-oll-sune', 'name': 'Sune', 'category': 'sune',
        'step_number': 1, 'difficulty': 'moyen',
        'algorithm': "R U R' U R U2 R'",
        'description': 'Motif poisson — phares à droite',
    },
    {
        'slug': 'cc-oll-anti-sune', 'name': 'Anti-Sune', 'category': 'sune',
        'step_number': 2, 'difficulty': 'moyen',
        'algorithm': "R U2 R' U' R U' R'",
        'description': 'Motif poisson — phares à gauche',
    },
    # -- hpi (moyen) --
    {
        'slug': 'cc-oll-h', 'name': 'Motif H', 'category': 'hpi',
        'step_number': 1, 'difficulty': 'moyen',
        'algorithm': "R U R' U R U' R' U R U2 R'",
        'description': 'Motif damier',
    },
    {
        'slug': 'cc-oll-pi', 'name': 'Motif Pi', 'category': 'hpi',
        'step_number': 2, 'difficulty': 'moyen',
        'algorithm': "R U2 R2 U' R2 U' R2 U2 R",
        'description': 'Deux phares devant',
    },
    # -- tul (difficile) --
    {
        'slug': 'cc-oll-t', 'name': 'Motif T', 'category': 'tul',
        'step_number': 1, 'difficulty': 'difficile',
        'algorithm': "r U R' U' r' F R F'",
        'description': 'Forme T devant',
    },
    {
        'slug': 'cc-oll-u', 'name': 'Motif U', 'category': 'tul',
        'step_number': 2, 'difficulty': 'difficile',
        'algorithm': "R2 D R' U2 R D' R' U2 R'",
        'description': 'Forme U face à vous',
    },
    {
        'slug': 'cc-oll-l', 'name': 'Motif L', 'category': 'tul',
        'step_number': 3, 'difficulty': 'difficile',
        'algorithm': "F R' F' r U R U' r'",
        'description': 'Forme L dans le coin',
    },
]

# ── PLL : 3 catégories, 6 cas (algorithmes vérifiés par simulation) ────
PLL_CASES = [
    # -- coins (moyen) — Aa/Ab, cycles de coins purs, verifie via pycuber --
    {
        'slug': 'cc-pll-aa', 'name': 'Aa-perm', 'category': 'coins',
        'step_number': 1, 'difficulty': 'moyen',
        'algorithm': "x R' U R' D2 R U' R' D2 R2 x'",
        'description': 'Aucun phare sur la couche du haut',
    },
    {
        'slug': 'cc-pll-ab', 'name': 'Ab-perm', 'category': 'coins',
        'step_number': 2, 'difficulty': 'moyen',
        'algorithm': "x R2 D2 R U R' D2 R U' R x'",
        'description': 'Phare sur le côté gauche',
    },
    # -- aretes-adjacentes (moyen) --
    {
        'slug': 'cc-pll-ua', 'name': 'Cycle vers la droite', 'category': 'aretes-adjacentes',
        'step_number': 1, 'difficulty': 'moyen',
        'algorithm': "R U' R U R U R U' R' U' R2",
        'description': '3 arêtes à tourner, sens antihoraire',
    },
    {
        'slug': 'cc-pll-ub', 'name': 'Cycle vers la gauche', 'category': 'aretes-adjacentes',
        'step_number': 2, 'difficulty': 'moyen',
        'algorithm': "L' U L' U' L' U' L' U L U L2",
        'description': '3 arêtes à tourner, sens horaire',
    },
    # -- aretes-opposees (difficile) --
    {
        'slug': 'cc-pll-h', 'name': 'H-perm', 'category': 'aretes-opposees',
        'step_number': 1, 'difficulty': 'difficile',
        'algorithm': "R2 U2 R U2 R2 U2 R2 U2 R U2 R2",
        'description': 'Les 4 arêtes opposées deux par deux',
    },
    {
        'slug': 'cc-pll-z', 'name': 'Z-perm', 'category': 'aretes-opposees',
        'step_number': 2, 'difficulty': 'difficile',
        'algorithm': "R U R' U R' U' R' U R U' R' U' R2 U R U2",
        'description': 'Arêtes adjacentes échangées en diagonale',
    },
]


class Command(BaseCommand):
    help = "Peuple les CubeState pour 2-Look OLL et 2-Look PLL (Cubie-Curieux)"

    def handle(self, *args, **options):
        self._load(OLL_CASES, stickering='OLL')
        self._load(PLL_CASES, stickering='PLL')

    def _load(self, cases, stickering):
        created_count, updated_count = 0, 0
        for case in cases:
            obj, created = CubeState.objects.update_or_create(
                slug=case['slug'],
                defaults={
                    'name': case['name'],
                    'json_state': {},  # non utilisé par ces pages (rendu via TwistyPlayer + data-alg)
                    'algorithm': case['algorithm'],
                    'description': case['description'],
                    'step_number': case['step_number'],
                    'method': 'cubiecurieux',
                    'category': case['category'],
                    'difficulty': case['difficulty'],
                    'stickering': stickering,
                    'camera_longitude': 30.0,
                    'camera_latitude': 25.0,
                    'hand_orientation': 'right',
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"[{stickering}] {created_count} créés, {updated_count} mis à jour."
        ))