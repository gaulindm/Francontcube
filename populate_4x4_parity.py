"""
populate_4x4_parity.py
Script pour peupler les cas de parité du 4x4.

Usage: dans le shell Django:
    exec(open('populate_4x4_parity.py').read())
"""

from cube.models import PuzzleCase

PUZZLE   = '4x4'
METHOD   = 'reduction'
CATEGORY = 'parity'

CASES = [

    # ── OLL Parity ────────────────────────────────────────────────────────
    {
        'step_number': 1,
        'name':        '4x4 OLL Parity — arête retournée',
        'algorithm':   "Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 Rw' U2 Rw U2 Rw' U2 Rw'",
        'setup':       "Rw U2 Rw U2 Rw' U2 Rw' U2 Lw' U2 Rw U2 Rw' U2 Rw U2 Rw x' U2 Rw'",
        'description': "Une arête de la dernière couche est retournée sur elle-même. "
                       "Ce cas est impossible sur un 3×3 — c'est la signature de la parité du 4×4. "
                       "L'algorithme retourne l'arête sans perturber le reste du cube.",
        'tip':         "Repère l'arête mal orientée AVANT de commencer ton OLL. "
                       "Applique cet algo, puis reprends ton OLL normalement.",
        'difficulty':  'difficile',
        'camera_longitude': -25.0,
        'camera_latitude':  35.0,
    },

    # ── PLL Parity ────────────────────────────────────────────────────────
    {
        'step_number': 2,
        'name':        '4x4 PLL Parity — deux arêtes échangées',
        'algorithm':   "2R2 U2 2R2 Uw2 2R2 Uw2",
        'setup':       "Uw2 2R2 Uw2 2R2 U2 2R2",
        'description': "Deux arêtes adjacentes de la dernière couche sont échangées. "
                       "Ce cas arrive après avoir résolu l'OLL — deux pièces semblent "
                       "impossible à permuter avec les PLL normaux du 3×3.",
        'tip':         "Si tu n'arrives pas à finir ton PLL, c'est probablement ce cas. "
                       "Applique l'algo, puis refais ton PLL normalement.",
        'difficulty':  'difficile',
        'camera_longitude': -25.0,
        'camera_latitude':  35.0,
    },
    {
        'step_number': 3,
        'name':        '4x4 PLL Parity — deux coins échangés',
        'algorithm':   "Rw2 F2 U2 Rw2 U2 F2 Rw2",
        'setup':       "Rw2 F2 U2 Rw2 U2 F2 Rw2",
        'description': "Deux coins de la dernière couche sont échangés. "
                       "Variante moins fréquente de la parité PLL.",
        'tip':         "Cet algo est self-inverse — applique-le deux fois et tu reviens au début.",
        'difficulty':  'difficile',
        'camera_longitude': -25.0,
        'camera_latitude':  35.0,
    },
]

# ── Exécution ─────────────────────────────────────────────────────────────

created = 0
updated = 0

for data in CASES:
    obj, was_created = PuzzleCase.objects.update_or_create(
        puzzle_type=PUZZLE,
        method=METHOD,
        category=CATEGORY,
        step_number=data['step_number'],
        defaults={
            'name':             data['name'],
            'algorithm':        data['algorithm'],
            'setup':            data.get('setup', ''),
            'description':      data.get('description', ''),
            'tip':              data.get('tip', ''),
            'difficulty':       data.get('difficulty', 'difficile'),
            'camera_longitude': data.get('camera_longitude', -25.0),
            'camera_latitude':  data.get('camera_latitude', 35.0),
        }
    )
    if was_created:
        created += 1
        print(f"  ✅ Créé  : {obj}")
    else:
        updated += 1
        print(f"  🔄 Màj   : {obj}")

print(f"\nTerminé — {created} créés, {updated} mis à jour.")
print(f"Total : {PuzzleCase.objects.filter(puzzle_type=PUZZLE, method=METHOD, category=CATEGORY).count()} cas")