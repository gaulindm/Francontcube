"""
main/views/puzzles/puzzle_big_cubes.py
Views for the 4x4 and 5x5 — Reduction method.
Uses CubeState (same as all 3x3 views).
"""

from django.shortcuts import render
from django.http import Http404
from cube.models import CubeState
import json


# ── Step metadata ─────────────────────────────────────────────────────────

STEPS_4X4 = [
    {
        'slug':  'w_y_centers',
        'name':  'Étape 1 — Centres Jaune et Blanc',
        'desc':  'Assembler les deux premiers centres de façon intuitive.',
        'icon':  'bi-circle',
        'tip':   'Commence par le jaune en bas — aucune contrainte pour le premier centre!',
    },
    {
        'slug':  'other_centers',
        'name':  'Étape 2 — Les Quatre Autres Centres',
        'desc':  'Assembler les 4 centres latéraux avec les techniques de remplacement.',
        'icon':  'bi-circle-fill',
        'tip':   'Garde toujours jaune en bas et blanc en haut pendant cette étape.',
    },
    {
        'slug':  'edges',
        'name':  'Étape 3 — Arêtes',
        'desc':  "Regrouper les 12 paires d'arêtes (edge pairing).",
        'icon':  'bi-arrows-collapse',
        'tip':   'Garde toujours une arête libre pour le wing flip.',
    },
    {
        'slug':  'bottom_cross',
        'name':  'Étape 4 — Croix du Bas',
        'desc':  'Former la croix jaune sur la face du bas.',
        'icon':  'bi-plus-circle',
        'tip':   'Le cube se comporte maintenant comme un 3×3 — plus de wide moves!',
    },
    {
        'slug':  'bottom_corners',
        'name':  'Étape 5 — Coins du Bas',
        'desc':  'Placer et orienter les 4 coins jaunes pour compléter la face du bas.',
        'icon':  'bi-grid',
        'tip':   "Le sexy move R U R' U' répété suffit pour tous les coins!",
    },
    {
        'slug':  'middle_edges',
        'name':  'Étape 6 — Arêtes du Milieu',
        'desc':  'Insérer les 4 arêtes de la couche du milieu (F2L).',
        'icon':  'bi-distribute-horizontal',
        'tip':   'Tourne le cube entier (y) si le slot cible est à gauche ou derrière.',
    },
    {
        'slug':  'top_cross',
        'name':  'Étape 7 — Croix du Haut',
        'desc':  'Former la croix blanche sur la face du haut.',
        'icon':  'bi-plus-circle-fill',
        'tip':   "Identifie ton cas (point, L ou I) avant d'exécuter l'algorithme.",
    },
    {
        'slug':  'top_face',
        'name':  'Étape 8 — Face du Haut',
        'desc':  'Orienter les 4 coins blancs pour compléter la face du haut.',
        'icon':  'bi-grid-fill',
        'tip':   'Ne tourne jamais le cube pendant cette étape — seulement U entre les coins!',
    },
    {
        'slug':  'pll_corners',
        'name':  'Étape 9 — PLL Coins',
        'desc':  'Permuter les 4 coins de la dernière couche à leur bonne position.',
        'icon':  'bi-arrow-repeat',
        'tip':   "Un seul algorithme suffit — répète-le jusqu'à ce que tous les coins soient placés.",
    },
    {
        'slug':  'pll_edges',
        'name':  'Étape 10 — PLL Arêtes',
        'desc':  'Permuter les 4 arêtes de la dernière couche pour finir le cube.',
        'icon':  'bi-shuffle',
        'tip':   "Deux arêtes impossibles à placer? Tu as une parité PLL — consulte la page Parité.",
    },
]

# ── 5×5 steps — mirrors the 4×4 structure exactly ─────────────────────────
#
# Key differences vs 4×4 called out in each tip:
#   • Centers  : Each face has a 3×3 centre (9 stickers) instead of 2×2 (4 stickers).
#                Build column by column (or cross-then-fill) instead of pair-by-pair.
#   • Edges    : Each edge group has 3 wing pieces (triplets) instead of 2 pairs.
#                The free-slot trick and flip technique work the same way.
#   • Parity   : The 5×5 is an odd cube — OLL parity CANNOT occur after reduction.
#                Only PLL parity is possible (one pair of edges swapped).
#   • 3×3 phase: Steps 4–10 are identical in concept to the 4×4.

STEPS_5X5 = [
    {
        'slug':  'w_y_centers',
        'name':  'Étape 1 — Centres Jaune et Blanc',
        'desc':  'Assembler les deux premiers centres (3×3) de façon intuitive.',
        'icon':  'bi-circle',
        'tip':   (
            'Chaque centre du 5×5 contient 9 stickers (3×3). '
            'Commence par le jaune en bas — tu peux bouger librement sans casser quoi que ce soit!'
        ),
    },
    {
        'slug':  'other_centers',
        'name':  'Étape 2 — Les Quatre Autres Centres',
        'desc':  'Assembler les 4 centres latéraux en les construisant colonne par colonne.',
        'icon':  'bi-circle-fill',
        'tip':   (
            'Garde jaune en bas et blanc en haut. '
            'Construis chaque centre en 3 colonnes verticales — '
            'utilise des wide moves (Rw, Uw) pour insérer sans casser les centres terminés.'
        ),
    },
    {
        'slug':  'edges',
        'name':  'Étape 3 — Arêtes',
        'desc':  "Regrouper les 12 triplets d'arêtes (3 wing pieces par arête).",
        'icon':  'bi-arrows-collapse',
        'tip':   (
            'Chaque arête du 5×5 a 3 pièces (contre 2 pour le 4×4). '
            'Assemble les 8 premières arêtes librement, puis utilise le slot libre '
            'pour les 4 dernières. Le flip de l\'arête fonctionne exactement comme sur le 4×4!'
        ),
    },
    {
        'slug':  'bottom_cross',
        'name':  'Étape 4 — Croix du Bas',
        'desc':  'Former la croix jaune sur la face du bas.',
        'icon':  'bi-plus-circle',
        'tip':   (
            'Le cube se comporte maintenant comme un 3×3 — '
            'plus de wide moves ni de Rw/Uw! '
            'Même technique que sur le 4×4.'
        ),
    },
    {
        'slug':  'bottom_corners',
        'name':  'Étape 5 — Coins du Bas',
        'desc':  'Placer et orienter les 4 coins jaunes pour compléter la face du bas.',
        'icon':  'bi-grid',
        'tip':   "Le sexy move R U R' U' répété suffit pour tous les coins — identique au 4×4!",
    },
    {
        'slug':  'middle_edges',
        'name':  'Étape 6 — Arêtes du Milieu',
        'desc':  'Insérer les 4 arêtes de la couche du milieu (F2L).',
        'icon':  'bi-distribute-horizontal',
        'tip':   'Tourne le cube entier (y) si le slot cible est à gauche ou derrière — identique au 4×4.',
    },
    {
        'slug':  'top_cross',
        'name':  'Étape 7 — Croix du Haut',
        'desc':  'Former la croix blanche sur la face du haut.',
        'icon':  'bi-plus-circle-fill',
        'tip':   "Identifie ton cas (point, L ou I) avant d'exécuter l'algorithme — identique au 4×4.",
    },
    {
        'slug':  'top_face',
        'name':  'Étape 8 — Face du Haut',
        'desc':  'Orienter les 4 coins blancs pour compléter la face du haut.',
        'icon':  'bi-grid-fill',
        'tip':   'Ne tourne jamais le cube pendant cette étape — seulement U entre les coins!',
    },
    {
        'slug':  'pll_corners',
        'name':  'Étape 9 — PLL Coins',
        'desc':  'Permuter les 4 coins de la dernière couche à leur bonne position.',
        'icon':  'bi-arrow-repeat',
        'tip':   "Un seul algorithme suffit — répète-le jusqu'à ce que tous les coins soient placés.",
    },
    {
        'slug':  'pll_edges',
        'name':  'Étape 10 — PLL Arêtes',
        'desc':  'Permuter les 4 arêtes de la dernière couche pour finir le cube.',
        'icon':  'bi-shuffle',
        'tip':   (
            'Deux arêtes impossibles à placer? Tu as une parité PLL — consulte la page Parité. '
            '(Sur le 5×5 il n\'y a PAS de parité OLL — seulement PLL!)'
        ),
    },
]


PUZZLE_CONFIGS = {
    '4x4': {
        'name':        "4×4 — Rubik's Revenge",
        'method':      'reduction-4x4',
        'steps':       STEPS_4X4,
        'home_url':    'main:4x4_home',
        'step_url':    'main:4x4_step',
        'ref_url':     'main:4x4_ref',
    },
    '5x5': {
        'name':        '5×5 — Professor',
        'method':      'reduction-5x5',
        'steps':       STEPS_5X5,
        'home_url':    'main:5x5_home',
        'step_url':    'main:5x5_step',
        'ref_url':     'main:5x5_ref',       # PLL-parity reference page
    },
}

# ── Reference pages (not sequential steps) ───────────────────────────────
# These are standalone pages linked from within other steps.
# They do not appear in the home step list and have no prev/next navigation.

REFERENCE_PAGES_4X4 = {
    'parity': {
        'slug': 'parity',
        'name': 'Référence — Parité',
        'desc': 'Algorithmes de correction pour la parité OLL et PLL du 4×4.',
    },
}

# The 5×5 is an odd cube: OLL parity cannot occur after reduction.
# Only PLL parity (one pair of adjacent or opposite edges swapped) is possible.
REFERENCE_PAGES_5X5 = {
    'parity': {
        'slug': 'parity',
        'name': 'Référence — Parité PLL',
        'desc': (
            'Algorithme de correction pour la parité PLL du 5×5. '
            'Contrairement au 4×4, la parité OLL n\'existe PAS sur le 5×5.'
        ),
    },
}


# ── Helpers ───────────────────────────────────────────────────────────────

def _get_config(puzzle_type):
    config = PUZZLE_CONFIGS.get(puzzle_type)
    if not config:
        raise Http404(f"Puzzle inconnu : {puzzle_type}")
    return config


def _get_step_info(config, step_slug):
    steps     = config['steps']
    step_info = next((s for s in steps if s['slug'] == step_slug), None)
    if not step_info:
        raise Http404(f"Étape inconnue : {step_slug}")
    idx       = [s['slug'] for s in steps].index(step_slug)
    prev_step = steps[idx - 1] if idx > 0 else None
    next_step = steps[idx + 1] if idx < len(steps) - 1 else None
    return step_info, prev_step, next_step


def get_cube_state(slug):
    """Fetch a CubeState json_state by slug. Returns JSON string or None."""
    try:
        state = CubeState.objects.get(slug=slug)
        return json.dumps(state.json_state)
    except CubeState.DoesNotExist:
        return None


# ── Named states per step ─────────────────────────────────────────────────

def _get_named_states(puzzle_type, slug):
    """Return named CubeState json_states for a given step or reference page."""

    # ══════════════════════════════════════════════════════════════════════
    # 4×4 STATES
    # ══════════════════════════════════════════════════════════════════════

    # ── Étape 1: Centres Jaune et Blanc ────────────────────────────────
    if puzzle_type == '4x4' and slug == 'w_y_centers':
        return {
            'state_yellow_start':   get_cube_state('4x4-wy-centers-yellow-start'),
            'state_yellow_done':    get_cube_state('4x4-wy-centers-yellow-done'),
            'state_white_progress': get_cube_state('4x4-wy-centers-white-progress'),
        }

    # ── Étape 2: Les Quatre Autres Centres ─────────────────────────────
    if puzzle_type == '4x4' and slug == 'other_centers':
        return {
            'state_goal':         get_cube_state('4x4-centers-goal'),
            'state_remplacement': get_cube_state('4x4-centers-remplacement'),
            'state_last_two':     get_cube_state('4x4-centers-last-two'),
        }

    # ── Étape 3 : Arêtes ─────────────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'edges':
        return {
            'state_pairing_from_top':    get_cube_state('4x4-edge-pairing-from-top'),
            'state_pairing_from_bottom': get_cube_state('4x4-edge-pairing-from-bottom'),
            'state_flip':                get_cube_state('4x4-edge-flip'),
            'state_last_two':            get_cube_state('4x4-last-two-edges'),
        }

    # ── Référence : Parité ────────────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'parity':
        return {
            'state_oll_parity': get_cube_state('4x4-parity-oll'),
            'state_pll_parity': get_cube_state('4x4-parity-pll'),
        }

    # ── Étape 4 : Croix du Bas ───────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'bottom_cross':
        return {
            'state_cross_goal':      get_cube_state('4x4-bottom-cross-goal'),
            'state_cross_intuitive': get_cube_state('4x4-bottom-cross-intuitive'),
            'state_cross_flip':      get_cube_state('4x4-bottom-cross-flip'),
            'state_cross_direct':    get_cube_state('4x4-bottom-cross-direct'),
        }

    # ── Étape 5 : Coins du Bas ───────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'bottom_corners':
        return {
            'state_corners_goal':         get_cube_state('4x4-bottom-corners-goal'),
            'state_corners_setup':        get_cube_state('4x4-bottom-corners-setup'),
            'state_corners_wrong_orient': get_cube_state('4x4-bottom-corners-wrong-orient'),
        }

    # ── Étape 6 : Arêtes du Milieu ───────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'middle_edges':
        return {
            'state_mid_goal':  get_cube_state('4x4-middle-edges-goal'),
            'state_mid_right': get_cube_state('4x4-middle-edges-right'),
            'state_mid_left':  get_cube_state('4x4-middle-edges-left'),
            'state_mid_wrong': get_cube_state('4x4-middle-edges-wrong'),
        }

    # ── Étape 7 : Croix du Haut ──────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'top_cross':
        return {
            'state_top_cross_goal': get_cube_state('4x4-top-cross-goal'),
            'state_top_cross_0':    get_cube_state('4x4-top-cross-0'),
            'state_top_cross_l':    get_cube_state('4x4-top-cross-l'),
            'state_top_cross_i':    get_cube_state('4x4-top-cross-i'),
            'state_top_cross_done': get_cube_state('4x4-top-cross-done'),
            'state_top_cross_alg':  get_cube_state('4x4-top-cross-alg'),
        }

    # ── Étape 8 : Face du Haut ───────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'top_face':
        return {
            'state_top_face_goal':  get_cube_state('4x4-top-face-goal'),
            'state_top_face_setup': get_cube_state('4x4-top-face-setup'),
            'state_corner_correct': get_cube_state('4x4-top-face-corner-correct'),
            'state_corner_twist1':  get_cube_state('4x4-top-face-corner-twist1'),
            'state_corner_twist2':  get_cube_state('4x4-top-face-corner-twist2'),
        }

    # ── Étape 9 : PLL Coins ──────────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'pll_corners':
        return {
            'state_pll_corners_goal':          get_cube_state('4x4-pll-corners-goal'),
            'state_pll_corners_no_headlights': get_cube_state('4x4-pll-corners-no-headlights'),
            'state_pll_corners_one_headlight': get_cube_state('4x4-pll-corners-one-headlight'),
        }

    # ── Étape 10 : PLL Arêtes ─────────────────────────────────────────────
    if puzzle_type == '4x4' and slug == 'pll_edges':
        return {
            'state_pll_edges_goal':      get_cube_state('4x4-pll-edges-goal'),
            'state_pll_3_edges_right':   get_cube_state('4x4-pll-3-edges-right'),
            'state_pll_3_edges_left':    get_cube_state('4x4-pll-3-edges-left'),
            'state_pll_edges_opp':       get_cube_state('4x4-pll-edges-opp'),
        }

    # ══════════════════════════════════════════════════════════════════════
    # 5×5 STATES
    # Slugs follow the convention: '5x5-<step>-<description>'
    # Add CubeState DB entries with these slugs as you build each template.
    # ══════════════════════════════════════════════════════════════════════

    # ── Étape 1 : Centres Jaune et Blanc ─────────────────────────────────
    # Each centre is 3×3 (9 stickers). Show: column-by-column build strategy.
    if puzzle_type == '5x5' and slug == 'w_y_centers':
        return {
            'state_yellow_start':    get_cube_state('5x5-wy-centers-yellow-start'),
            'state_yellow_col1':     get_cube_state('5x5-wy-centers-yellow-col1'),
            'state_yellow_done':     get_cube_state('5x5-wy-centers-yellow-done'),
            'state_white_progress':  get_cube_state('5x5-wy-centers-white-progress'),
        }

    # ── Étape 2 : Les Quatre Autres Centres ──────────────────────────────
    # Show: inserting a column with Rw, replacing without breaking done centres.
    if puzzle_type == '5x5' and slug == 'other_centers':
        return {
            'state_goal':          get_cube_state('5x5-centers-goal'),
            'state_col_insert':    get_cube_state('5x5-centers-col-insert'),
            'state_remplacement':  get_cube_state('5x5-centers-remplacement'),
            'state_last_two':      get_cube_state('5x5-centers-last-two'),
        }

    # ── Étape 3 : Arêtes ─────────────────────────────────────────────────
    # Each edge has 3 wing pieces. Show: triplet build, flip, last-two trick.
    if puzzle_type == '5x5' and slug == 'edges':
        return {
            'state_pairing_start':       get_cube_state('5x5-edge-pairing-start'),
            'state_pairing_from_top':    get_cube_state('5x5-edge-pairing-from-top'),
            'state_pairing_from_bottom': get_cube_state('5x5-edge-pairing-from-bottom'),
            'state_flip':                get_cube_state('5x5-edge-flip'),
            'state_last_two':            get_cube_state('5x5-last-two-edges'),
        }

    # ── Référence : Parité PLL ────────────────────────────────────────────
    # The 5×5 is an odd cube: OLL parity CANNOT occur. Only PLL parity.
    if puzzle_type == '5x5' and slug == 'parity':
        return {
            'state_pll_parity': get_cube_state('5x5-parity-pll'),
        }

    # ── Étape 4 : Croix du Bas ───────────────────────────────────────────
    # Identical technique to 4×4 — reuse same visual explanations.
    if puzzle_type == '5x5' and slug == 'bottom_cross':
        return {
            'state_cross_goal':      get_cube_state('5x5-bottom-cross-goal'),
            'state_cross_intuitive': get_cube_state('5x5-bottom-cross-intuitive'),
            'state_cross_flip':      get_cube_state('5x5-bottom-cross-flip'),
            'state_cross_direct':    get_cube_state('5x5-bottom-cross-direct'),
        }

    # ── Étape 5 : Coins du Bas ───────────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'bottom_corners':
        return {
            'state_corners_goal':         get_cube_state('5x5-bottom-corners-goal'),
            'state_corners_setup':        get_cube_state('5x5-bottom-corners-setup'),
            'state_corners_wrong_orient': get_cube_state('5x5-bottom-corners-wrong-orient'),
        }

    # ── Étape 6 : Arêtes du Milieu ───────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'middle_edges':
        return {
            'state_mid_goal':  get_cube_state('5x5-middle-edges-goal'),
            'state_mid_right': get_cube_state('5x5-middle-edges-right'),
            'state_mid_left':  get_cube_state('5x5-middle-edges-left'),
            'state_mid_wrong': get_cube_state('5x5-middle-edges-wrong'),
        }

    # ── Étape 7 : Croix du Haut ──────────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'top_cross':
        return {
            'state_top_cross_goal': get_cube_state('5x5-top-cross-goal'),
            'state_top_cross_0':    get_cube_state('5x5-top-cross-0'),
            'state_top_cross_l':    get_cube_state('5x5-top-cross-l'),
            'state_top_cross_i':    get_cube_state('5x5-top-cross-i'),
            'state_top_cross_done': get_cube_state('5x5-top-cross-done'),
            'state_top_cross_alg':  get_cube_state('5x5-top-cross-alg'),
        }

    # ── Étape 8 : Face du Haut ───────────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'top_face':
        return {
            'state_top_face_goal':  get_cube_state('5x5-top-face-goal'),
            'state_top_face_setup': get_cube_state('5x5-top-face-setup'),
            'state_corner_correct': get_cube_state('5x5-top-face-corner-correct'),
            'state_corner_twist1':  get_cube_state('5x5-top-face-corner-twist1'),
            'state_corner_twist2':  get_cube_state('5x5-top-face-corner-twist2'),
        }

    # ── Étape 9 : PLL Coins ──────────────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'pll_corners':
        return {
            'state_pll_corners_goal':          get_cube_state('5x5-pll-corners-goal'),
            'state_pll_corners_no_headlights': get_cube_state('5x5-pll-corners-no-headlights'),
            'state_pll_corners_one_headlight': get_cube_state('5x5-pll-corners-one-headlight'),
        }

    # ── Étape 10 : PLL Arêtes ────────────────────────────────────────────
    if puzzle_type == '5x5' and slug == 'pll_edges':
        return {
            'state_pll_edges_goal':    get_cube_state('5x5-pll-edges-goal'),
            'state_pll_3_edges_right': get_cube_state('5x5-pll-3-edges-right'),
            'state_pll_3_edges_left':  get_cube_state('5x5-pll-3-edges-left'),
            'state_pll_edges_opp':     get_cube_state('5x5-pll-edges-opp'),
        }

    return {}


# ── Views ─────────────────────────────────────────────────────────────────

def puzzle_big_home(request, puzzle_type):
    """Landing page for a big cube (4x4 or 5x5)."""
    config = _get_config(puzzle_type)
    return render(request, 'main/puzzles/big_cube/home.html', {
        'puzzle_type': puzzle_type,
        'name':        config['name'],
        'steps':       config['steps'],
        'home_url':    config['home_url'],
        'step_url':    config['step_url'],
        'ref_url':     config.get('ref_url'),
    })


def puzzle_big_step(request, puzzle_type, step):
    """One sequential step page for a big cube (4x4 or 5x5)."""
    config                          = _get_config(puzzle_type)
    step_info, prev_step, next_step = _get_step_info(config, step)

    context = {
        'puzzle_type': puzzle_type,
        'name':        config['name'],
        'step':        step_info,
        'prev_step':   prev_step,
        'next_step':   next_step,
        'home_url':    config['home_url'],
        'step_url':    config['step_url'],
        'ref_url':     config.get('ref_url'),
    }

    context.update(_get_named_states(puzzle_type, step))

    template = f'main/puzzles/big_cube/{step}.html'
    return render(request, template, context)


def puzzle_big_reference(request, puzzle_type, ref):
    """
    Standalone reference page — not a sequential step.
    No prev/next navigation. Linked from within other step pages.
    4×4: parity (OLL + PLL)
    5×5: parity (PLL only — OLL parity cannot occur on an odd cube)
    """
    config = _get_config(puzzle_type)

    reference_pages = {
        '4x4': REFERENCE_PAGES_4X4,
        '5x5': REFERENCE_PAGES_5X5,
    }.get(puzzle_type, {})

    ref_info = reference_pages.get(ref)
    if not ref_info:
        raise Http404(f"Page de référence inconnue : {ref}")

    context = {
        'puzzle_type': puzzle_type,
        'name':        config['name'],
        'ref':         ref_info,
        'home_url':    config['home_url'],
        'step_url':    config['step_url'],
        'ref_url':     config.get('ref_url'),
    }

    context.update(_get_named_states(puzzle_type, ref))

    template = f'main/puzzles/big_cube/{ref}.html'
    return render(request, template, context)


# ── Shortcuts ─────────────────────────────────────────────────────────────

def puzzle_4x4_home(request):
    return puzzle_big_home(request, '4x4')

def puzzle_4x4_step(request, step):
    return puzzle_big_step(request, '4x4', step)

def puzzle_4x4_ref(request, ref):
    return puzzle_big_reference(request, '4x4', ref)

def puzzle_5x5_home(request):
    return puzzle_big_home(request, '5x5')

def puzzle_5x5_step(request, step):
    return puzzle_big_step(request, '5x5', step)

def puzzle_5x5_ref(request, ref):
    return puzzle_big_reference(request, '5x5', ref)