"""
populate_4x4_cases.py
=====================
Populates PuzzleCase objects for the 4×4 Reduction tutorial.

Usage:
    python manage.py shell < populate_4x4_cases.py

Only covers the cases needed for the home page and centers step for now.
Add edges/parity/3x3-phase cases as you build those templates.
"""

from cube.models import PuzzleCase

# ── Helper ────────────────────────────────────────────────────────────────

def upsert(data):
    """Create or update a PuzzleCase by (puzzle_type, method, category, step_number)."""
    obj, created = PuzzleCase.objects.update_or_create(
        puzzle_type  = data['puzzle_type'],
        method       = data['method'],
        category     = data['category'],
        step_number  = data['step_number'],
        defaults     = {k: v for k, v in data.items()
                        if k not in ('puzzle_type', 'method', 'category', 'step_number')},
    )
    action = 'Created' if created else 'Updated'
    print(f"  {action}: [{obj.puzzle_type}] {obj.name}")
    return obj


# ── 4×4 — Centers (Étape 1) ───────────────────────────────────────────────
# The goal is to assemble the 6 centres (2×2 block per face).
# Each case represents a key concept or technique.

CENTERS_CASES = [
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'centers',
        'step_number': 1,
        'name':        '4x4 Centers — Blanc et Jaune',
        'slug':        '4x4-centers-01-white-yellow',
        'algorithm':   '',   # Intuitive — no fixed algorithm
        'setup':       '',
        'description': (
            "Commencez toujours par les centres blanc (bas) et jaune (haut). "
            "Ce sont les plus faciles car vous n'avez pas encore de contraintes. "
            "Placez le cube avec le blanc en bas et assemblez les 4 pièces centrales blanches."
        ),
        'tip':         'Si vous placez bien blanc/jaune dès le départ, les 4 autres centres se contraignent automatiquement.',
        'difficulty':  'facile',
        'stickering':  'centers-only',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'centers',
        'step_number': 2,
        'name':        '4x4 Centers — Les 4 Centres Latéraux',
        'slug':        '4x4-centers-02-lateral',
        'algorithm':   '',   # Intuitive
        'setup':       '',
        'description': (
            "Une fois blanc et jaune placés, résolvez les 4 centres latéraux "
            "(rouge, orange, vert, bleu). Faites attention à leur position relative — "
            "rouge doit être en face d'orange, vert en face de bleu."
        ),
        'tip':         "Tenez blanc en bas pendant toute cette étape pour ne pas perdre vos repères.",
        'difficulty':  'facile',
        'stickering':  'centers-only',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'centers',
        'step_number': 3,
        'name':        '4x4 Centers — Technique du Remplacement',
        'slug':        '4x4-centers-03-replacement',
        'algorithm':   'Rw U Rw\' U\' Rw U\' Rw\'',
        'setup':       '',
        'description': (
            "Quand un centre est presque complet mais qu'il manque une pièce "
            "et que la bonne pièce est déjà sur une autre face, utilisez cette "
            "technique pour l'insérer sans défaire ce qui est déjà fait."
        ),
        'tip':         "Ce mouvement déplace une pièce centrale de la face U vers la face R sans toucher les coins.",
        'difficulty':  'moyen',
        'stickering':  'centers-only',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'centers',
        'step_number': 4,
        'name':        '4x4 Centers — Deux Derniers Centres',
        'slug':        '4x4-centers-04-last-two',
        'algorithm':   'Rw U2 Rw\'',
        'setup':       '',
        'description': (
            "Les deux derniers centres sont souvent les plus délicats car "
            "chaque mouvement affecte l'autre. Utilisez les mouvements Rw "
            "(tranche droite large) pour cycler des pièces entre les deux faces "
            "sans toucher les centres déjà complétés."
        ),
        'tip':         "Rw tourne les deux couches droites ensemble — c'est différent du R normal du 3×3.",
        'difficulty':  'moyen',
        'stickering':  'centers-only',
    },
]

# ── 4×4 — Edges (Étape 2) ─────────────────────────────────────────────────
# The goal is to pair all 12 edge pairs (wings).

EDGES_CASES = [
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'edges',
        'step_number': 1,
        'name':        '4x4 Edges — Concept des Wings',
        'slug':        '4x4-edges-01-concept',
        'algorithm':   '',
        'setup':       '',
        'description': (
            "Chaque arête du 4×4 est formée de 2 pièces identiques appelées "
            "\"wings\". Il faut apparier les deux wings de la même arête pour "
            "reconstituer une arête complète, comme sur le 3×3."
        ),
        'tip':         'Vous avez 12 arêtes à compléter — commencez par les 8 premières librement, les 4 dernières demandent plus de soin.',
        'difficulty':  'facile',
        'stickering':  'ELS',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'edges',
        'step_number': 2,
        'name':        '4x4 Edges — Appariement Standard',
        'slug':        '4x4-edges-02-pairing',
        'algorithm':   'Uw R U\' R\' Uw\'',
        'setup':       '',
        'description': (
            "La technique de base pour apparier deux wings : placez un wing "
            "sur la face U et l'autre sur la face F, alignez-les, puis utilisez "
            "ce mouvement pour les réunir sans casser les arêtes déjà appariées."
        ),
        'tip':         "Uw tourne les deux couches supérieures — gardez toujours une arête \"sacrifiée\" disponible pour le flip.",
        'difficulty':  'moyen',
        'stickering':  'ELS',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'edges',
        'step_number': 3,
        'name':        '4x4 Edges — Wing Flip (Dernières Arêtes)',
        'slug':        '4x4-edges-03-flip',
        'algorithm':   'Uw R U R\' F R\' F\' R Uw\'',
        'setup':       '',
        'description': (
            "Pour les 4 dernières arêtes, il n'y a plus d'arête libre à sacrifier. "
            "Cet algorithme permet de retourner un wing sans défaire les arêtes "
            "déjà complétées — c'est la technique clé de cette étape."
        ),
        'tip':         "Si deux wings semblent \"retournés\" par rapport à l'autre, c'est exactement ce cas.",
        'difficulty':  'difficile',
        'stickering':  'ELS',
    },
]

# ── 4×4 — Parity (Étape 3) ────────────────────────────────────────────────
# Two parity cases specific to the 4×4.

PARITY_CASES = [
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'parity',
        'step_number': 1,
        'name':        '4x4 Parité — OLL Parity',
        'slug':        '4x4-parity-01-oll',
        'algorithm':   "Rw U2 x Rw U2 Rw U2 Rw' U2 Lw U2 Rw' U2 Rw U2 Rw' U2 Rw'",
        'setup':       '',
        'description': (
            "La parité OLL se produit quand une seule arête est retournée sur "
            "la dernière couche — un état impossible sur un 3×3. "
            "Cet algorithme corrige ce cas. Il est long mais il n'y a pas de raccourci."
        ),
        'tip':         "Repérez ce cas quand vous voyez une seule arête \"retournée\" lors de votre OLL habituel.",
        'difficulty':  'difficile',
        'stickering':  'full',
    },
    {
        'puzzle_type': '4x4',
        'method':      'reduction',
        'category':    'parity',
        'step_number': 2,
        'name':        '4x4 Parité — PLL Parity',
        'slug':        '4x4-parity-02-pll',
        'algorithm':   "Rw2 B2 U2 Lw U2 Rw' U2 Rw U2 F2 Rw F2 Lw' B2 Rw2",
        'setup':       '',
        'description': (
            "La parité PLL se produit quand deux arêtes adjacentes ou opposées "
            "semblent swappées — encore un état impossible sur le 3×3. "
            "Cet algorithme remet tout en ordre."
        ),
        'tip':         "Repérez ce cas quand votre PLL habituel ne fonctionne pas et que deux arêtes semblent échangées.",
        'difficulty':  'difficile',
        'stickering':  'full',
    },
]

# ── Run ───────────────────────────────────────────────────────────────────

print("\n=== 4×4 Centers ===")
for data in CENTERS_CASES:
    upsert(data)

print("\n=== 4×4 Edges ===")
for data in EDGES_CASES:
    upsert(data)

print("\n=== 4×4 Parity ===")
for data in PARITY_CASES:
    upsert(data)

print("\n✅ Done! Run: python manage.py shell < populate_4x4_cases.py")