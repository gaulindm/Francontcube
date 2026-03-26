"""
populate_4x4_centers.py
=======================
Script pour peupler les cas de la section "Centres" du 4x4.

Usage:
    python manage.py shell < populate_4x4_centers.py

Organisation: 3 techniques — Déplacer, Préserver, Échanger
Orientation:  Blanc dessus, vert devant (défaut WCA)
Visualisation: cubing.js twisty-player (puzzle="4x4x4")

Note sur le setup:
    Le champ 'setup' est laissé vide intentionnellement.
    get_setup_alg() calcule automatiquement l'inverse de l'algorithme,
    ce qui place le cube dans l'état de départ correct pour chaque cas.
"""

from cube.models import PuzzleCase

# ── Constantes ─────────────────────────────────────────────────────────────

PUZZLE_TYPE = '4x4'
METHOD      = 'reduction'
CATEGORY    = 'centers'

# Caméra — latitude plus haute pour bien voir le dessus (centres du haut)
CAM_TOP  = {'camera_latitude': 35.0, 'camera_longitude': -25.0}
CAM_SIDE = {'camera_latitude': 22.0, 'camera_longitude': -25.0}

# ── Données ────────────────────────────────────────────────────────────────

CASES = [

    # ══════════════════════════════════════════════════════════════
    # TECHNIQUE 1 — DÉPLACER
    # Amener un centre blanc isolé vers la face du dessus.
    # Pas de contraintes encore — aucun centre n'est résolu.
    # ══════════════════════════════════════════════════════════════
    {
        'step_number': 1,
        'name':        "Déplacer — Centre avant vers le dessus",
        'slug':        '4x4-centers-01',
        'algorithm':   "Rw U Rw'",
        'setup':       '',
        'description': (
            "Un centre blanc est sur la face avant (verte). "
            "Rw fait monter la tranche intérieure droite, "
            "U la repositionne, Rw' remet la tranche en place."
        ),
        'tip':         "Mémorise ce mouvement — c'est la base de presque tout le reste.",
        'difficulty':  'facile',
        **CAM_TOP,
    },
    {
        'step_number': 2,
        'name':        "Déplacer — Centre à droite vers le dessus",
        'slug':        '4x4-centers-02',
        'algorithm':   "Uw' Rw U Rw' Uw",
        'setup':       '',
        'description': (
            "Un centre blanc est sur la face droite. "
            "Uw' amène la tranche U en position, "
            "puis le même Rw U Rw' de base insère le centre, "
            "et Uw remet la couche en place."
        ),
        'tip':         "Remarque : Uw' … Uw encadre le mouvement de base comme des parenthèses.",
        'difficulty':  'facile',
        **CAM_TOP,
    },
    {
        'step_number': 3,
        'name':        "Déplacer — Centre en bas vers le dessus",
        'slug':        '4x4-centers-03',
        'algorithm':   'Rw2',
        'setup':       '',
        'description': (
            "Un centre blanc est directement en dessous. "
            "Un seul Rw2 (double tranche droite) "
            "le fait passer directement au dessus."
        ),
        'tip':         "Le cas le plus simple — un seul mouvement suffit!",
        'difficulty':  'facile',
        **CAM_SIDE,
    },

    # ══════════════════════════════════════════════════════════════
    # TECHNIQUE 2 — PRÉSERVER
    # Construire les centres latéraux sans défaire le dessus (blanc)
    # et le dessous (jaune) déjà résolus.
    # ══════════════════════════════════════════════════════════════
    {
        'step_number': 4,
        'name':        "Préserver — Insérer un latéral sans casser le dessus",
        'slug':        '4x4-centers-04',
        'algorithm':   "Uw Rw U Rw' Uw'",
        'setup':       '',
        'description': (
            "Le centre blanc (dessus) et jaune (dessous) sont résolus. "
            "Uw décale temporairement la tranche U pour protéger le centre blanc, "
            "Rw U Rw' insère le centre latéral, "
            "puis Uw' remet tout en place."
        ),
        'tip':         "La règle : chaque Uw doit être annulé par un Uw' pour ne rien casser.",
        'difficulty':  'moyen',
        **CAM_SIDE,
    },
    {
        'step_number': 5,
        'name':        "Préserver — Insérer par le bas",
        'slug':        '4x4-centers-05',
        'algorithm':   "Dw' Rw U Rw' Dw",
        'setup':       '',
        'description': (
            "Alternative utile quand la tranche U est déjà occupée. "
            "Dw' décale la tranche du bas pour libérer de l'espace, "
            "le mouvement de base insère le centre, "
            "Dw remet la tranche du bas en place."
        ),
        'tip':         "Utilise cette variante quand Uw perturberait un centre déjà placé.",
        'difficulty':  'moyen',
        **CAM_SIDE,
    },
    {
        'step_number': 6,
        'name':        "Préserver — Construire une paire avant d\u2019insérer",
        'slug':        '4x4-centers-06',
        'algorithm':   "Rw U2 Rw'",
        'setup':       '',
        'description': (
            "Deux centres de même couleur sont alignés verticalement sur la face avant. "
            "Rw U2 Rw' les insère ensemble en une seule fois "
            "— plus efficace que d\u2019insérer un centre à la fois."
        ),
        'tip':         "Cherche toujours à aligner deux centres avant d\u2019insérer — ça économise des mouvements.",
        'difficulty':  'moyen',
        **CAM_SIDE,
    },

    # ══════════════════════════════════════════════════════════════
    # TECHNIQUE 3 — ÉCHANGER
    # Les 5 premiers centres sont résolus mais les deux derniers
    # sont inversés — impossible à corriger autrement.
    # ══════════════════════════════════════════════════════════════
    {
        'step_number': 7,
        'name':        "Échanger — Deux centres opposés inversés",
        'slug':        '4x4-centers-07',
        'algorithm':   "Rw2 B2 Rw2 Uw2 Rw2 B2 Rw2",
        'setup':       '',
        'description': (
            "Les centres de deux faces opposées sont inversés "
            "et ne peuvent pas être corrigés autrement. "
            "Cet algorithme échange les deux centres sans toucher aux autres faces."
        ),
        'tip':         "Mémorise-le bien — il arrive souvent quand on arrive aux derniers centres!",
        'difficulty':  'difficile',
        **CAM_SIDE,
    },
    {
        'step_number': 8,
        'name':        "Échanger — Derniers deux centres latéraux",
        'slug':        '4x4-centers-08',
        'algorithm':   "Rw U2 Rw' Uw2 Rw U2 Rw'",
        'setup':       '',
        'description': (
            "Variante d\u2019échange pour les deux derniers centres latéraux. "
            "Plus court que le précédent, utilisé quand les faces haut/bas sont déjà résolues "
            "et que l\u2019on ne veut pas les perturber."
        ),
        'tip':         "Remarque la symétrie : Rw U2 Rw' se répète deux fois avec Uw2 au milieu.",
        'difficulty':  'difficile',
        **CAM_SIDE,
    },
]

# ── Insertion ──────────────────────────────────────────────────────────────

created = 0
updated = 0

for data in CASES:
    obj, is_new = PuzzleCase.objects.update_or_create(
        slug=data['slug'],
        defaults={
            'puzzle_type':      PUZZLE_TYPE,
            'method':           METHOD,
            'category':         CATEGORY,
            'step_number':      data['step_number'],
            'name':             data['name'],
            'algorithm':        data['algorithm'],
            'setup':            data.get('setup', ''),
            'description':      data.get('description', ''),
            'tip':              data.get('tip', ''),
            'difficulty':       data.get('difficulty', 'moyen'),
            'stickering':       'full',
            'camera_latitude':  data.get('camera_latitude', 22.0),
            'camera_longitude': data.get('camera_longitude', -25.0),
        }
    )
    if is_new:
        created += 1
        print(f"  Créé  : {obj.name}")
    else:
        updated += 1
        print(f"  Mis à jour : {obj.name}")

print(f"\n{'─'*50}")
print(f"Centres 4x4 — {created} créés, {updated} mis à jour")
print(f"Total en BD : {PuzzleCase.objects.filter(puzzle_type='4x4', category='centers').count()} cas")
print(f"{'─'*50}")

# ── Vérification rapide ────────────────────────────────────────────────────

print("\nVérification des setups auto-calculés:")
for case in PuzzleCase.objects.filter(puzzle_type='4x4', category='centers').order_by('step_number'):
    setup = case.get_setup_alg()
    print(f"  #{case.step_number} {case.name[:40]:<40} setup: {setup}")