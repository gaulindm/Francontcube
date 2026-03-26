"""
populate_4x4_edges.py
Script pour peupler les cas d'arêtes du 4x4.

Usage:
    python manage.py shell < populate_4x4_edges.py
    
    ou dans le shell Django:
    exec(open('populate_4x4_edges.py').read())
"""

from cube.models import PuzzleCase

PUZZLE = '4x4'
METHOD = 'reduction'
CATEGORY = 'edges'

CASES = [

    # ── Groupe 1 : Arêtes libres (cas 1-4) ───────────────────────────────
    # Slot de travail libre — les plus simples

    {
        'step_number': 1,
        'name':        '4x4 Arête libre — côte à côte',
        'algorithm':   "Uw R U' R' Uw'",
        'setup':       "Uw R U R' Uw'",
        'description': "Les deux wings sont côte à côte dans la couche U. "
                       "Un simple Uw aligne, R U' R' insère, Uw' restaure.",
        'tip':         'Le move de base — maîtrise celui-là en premier.',
        'difficulty':  'facile',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },
    {
        'step_number': 2,
        'name':        '4x4 Arête libre — face à face',
        'algorithm':   "Uw R U R' Uw'",
        'setup':       "Uw R U' R' Uw'",
        'description': "Les deux wings sont face à face (miroir). "
                       "Même séquence mais avec U au lieu de U'.",
        'tip':         'Identique au cas 1 mais miroir — fais attention à la direction.',
        'difficulty':  'facile',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },
    {
        'step_number': 3,
        'name':        "4x4 Arête libre — wing dans la couche F",
        'algorithm':   "Rw U R' U' Rw'",
        'setup':       "Rw U' R U Rw'",
        'description': "Un wing est dans la couche F, l'autre en U. "
                       "Rw pour aligner, séquence standard, Rw' pour restaurer.",
        'tip':         'Pense à utiliser Rw comme un R large.',
        'difficulty':  'facile',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },
    {
        'step_number': 4,
        'name':        "4x4 Arête libre — wing dans la couche B",
        'algorithm':   "U Rw' U' R U Rw",
        'setup':       "Rw U' R' U Rw' U'",
        'description': "Un wing est dans la couche B. "
                       "Rotation U pour amener le wing en position, puis insertion.",
        'tip':         "Souvent, un simple U avant résout le cas en cas #3.",
        'difficulty':  'moyen',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },

    # ── Groupe 2 : Dernières arêtes (cas 5-8) ────────────────────────────
    # Plus d'arête libre — il faut en sortir une temporairement

    {
        'step_number': 5,
        'name':        "4x4 Dernière arête — insertion directe",
        'algorithm':   "Uw R U' R' Uw' U2 Uw R U' R' Uw'",
        'setup':       "Uw R U R' Uw' U2 Uw R U R' Uw'",
        'description': "Toutes les arêtes sont occupées. "
                       "Sortir une arête avec la première séquence, "
                       "repositionner avec U2, puis insérer la cible.",
        'tip':         "Choisis bien quelle arête sortir — prends celle qui est mal orientée.",
        'difficulty':  'moyen',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },
    {
        'step_number': 6,
        'name':        "4x4 Dernière arête — échange de slots",
        'algorithm':   "Rw2 B2 U2 Rw U2 Rw' U2 B2 Rw2",
        'setup':       "Rw2 B2 U2 Rw U2 Rw' U2 B2 Rw2",
        'description': "Deux arêtes doivent être échangées. "
                       "Algorithme pur qui échange deux paires d'arêtes.",
        'tip':         "Cet algo ne change rien d'autre — très propre.",
        'difficulty':  'moyen',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
    },

    # ── Groupe 3 : Wing flip (cas 9+) ────────────────────────────────────
    # Arête miroir — orientée dans le mauvais sens

    {
        'step_number': 9,
        'name':        "4x4 Wing flip — retourner une arête miroir",
        'algorithm':   "Rw2 B2 U2 Rw U2 Rw' U2 B2 Rw2 U2 Rw2",
        'setup':       "Rw2 U2 Rw2 B2 U2 Rw U2 Rw' U2 B2 Rw2",
        'description': "L'arête est bien placée mais orientée dans le mauvais sens (miroir). "
                       "Il n'existe pas d'algo court — on passe par un échange intermédiaire.",
        'tip':         "Évite ce cas dès le départ en vérifiant l'orientation avant d'insérer!",
        'difficulty':  'difficile',
        'camera_longitude': -25.0,
        'camera_latitude':  30.0,
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
            'name':              data['name'],
            'algorithm':         data['algorithm'],
            'setup':             data.get('setup', ''),
            'description':       data.get('description', ''),
            'tip':               data.get('tip', ''),
            'difficulty':        data.get('difficulty', 'moyen'),
            'camera_longitude':  data.get('camera_longitude', -25.0),
            'camera_latitude':   data.get('camera_latitude', 22.0),
        }
    )
    if was_created:
        created += 1
        print(f"  ✅ Créé  : {obj}")
    else:
        updated += 1
        print(f"  🔄 Màj   : {obj}")

print(f"\nTerminé — {created} créés, {updated} mis à jour.")
print(f"Total dans la BD : {PuzzleCase.objects.filter(puzzle_type=PUZZLE, method=METHOD, category=CATEGORY).count()} cas")