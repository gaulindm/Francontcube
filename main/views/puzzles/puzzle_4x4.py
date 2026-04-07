"""
main/views/puzzles/puzzle_4x4.py

Everything specific to the 4×4 (Rubik's Revenge) — Reduction method.
Templates live in:  main/templates/main/puzzles/4x4/
"""

from .puzzle_base import get_cube_state, puzzle_home, puzzle_step, puzzle_reference


# ── Step metadata ─────────────────────────────────────────────────────────

STEPS = [
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


# ── Reference pages ───────────────────────────────────────────────────────

REFERENCE_PAGES = {
    'parity': {
        'slug': 'parity',
        'name': 'Référence — Parité',
        'desc': 'Algorithmes de correction pour la parité OLL et PLL du 4×4.',
    },
}


# ── Config ────────────────────────────────────────────────────────────────

CONFIG = {
    'puzzle_type': '4x4',
    'name':        "4×4 — Rubik's Revenge",
    'steps':       STEPS,
    'home_url':    'main:4x4_home',
    'step_url':    'main:4x4_step',
    'ref_url':     'main:4x4_ref',
}


# ── Named states ──────────────────────────────────────────────────────────

def _named_states(slug):
    """Return context variables (CubeState JSON) for a given step or reference slug."""

    # ── Étape 1 : Centres Jaune et Blanc ─────────────────────────────────
    if slug == 'w_y_centers':
        return {
            'state_yellow_start':   get_cube_state('4x4-wy-centers-yellow-start'),
            'state_yellow_done':    get_cube_state('4x4-wy-centers-yellow-done'),
            'state_white_progress': get_cube_state('4x4-wy-centers-white-progress'),
        }

    # ── Étape 2 : Les Quatre Autres Centres ──────────────────────────────
    if slug == 'other_centers':
        return {
            'state_goal':         get_cube_state('4x4-centers-goal'),
            'state_remplacement': get_cube_state('4x4-centers-remplacement'),
            'state_last_two':     get_cube_state('4x4-centers-last-two'),
        }

    # ── Étape 3 : Arêtes ─────────────────────────────────────────────────
    if slug == 'edges':
        return {
            'state_pairing_from_top':    get_cube_state('4x4-edge-pairing-from-top'),
            'state_pairing_from_bottom': get_cube_state('4x4-edge-pairing-from-bottom'),
            'state_flip':                get_cube_state('4x4-edge-flip'),
            'state_last_two':            get_cube_state('4x4-last-two-edges'),
        }

    # ── Référence : Parité ────────────────────────────────────────────────
    if slug == 'parity':
        return {
            'state_oll_parity': get_cube_state('4x4-parity-oll'),
            'state_pll_parity': get_cube_state('4x4-parity-pll'),
        }

    # ── Étape 4 : Croix du Bas ───────────────────────────────────────────
    if slug == 'bottom_cross':
        return {
            'state_cross_goal':      get_cube_state('4x4-bottom-cross-goal'),
            'state_cross_intuitive': get_cube_state('4x4-bottom-cross-intuitive'),
            'state_cross_flip':      get_cube_state('4x4-bottom-cross-flip'),
            'state_cross_direct':    get_cube_state('4x4-bottom-cross-direct'),
        }

    # ── Étape 5 : Coins du Bas ───────────────────────────────────────────
    if slug == 'bottom_corners':
        return {
            'state_corners_goal':         get_cube_state('4x4-bottom-corners-goal'),
            'state_corners_setup':        get_cube_state('4x4-bottom-corners-setup'),
            'state_corners_wrong_orient': get_cube_state('4x4-bottom-corners-wrong-orient'),
        }

    # ── Étape 6 : Arêtes du Milieu ───────────────────────────────────────
    if slug == 'middle_edges':
        return {
            'state_mid_goal':  get_cube_state('4x4-middle-edges-goal'),
            'state_mid_right': get_cube_state('4x4-middle-edges-right'),
            'state_mid_left':  get_cube_state('4x4-middle-edges-left'),
            'state_mid_wrong': get_cube_state('4x4-middle-edges-wrong'),
        }

    # ── Étape 7 : Croix du Haut ──────────────────────────────────────────
    if slug == 'top_cross':
        return {
            'state_top_cross_goal': get_cube_state('4x4-top-cross-goal'),
            'state_top_cross_0':    get_cube_state('4x4-top-cross-0'),
            'state_top_cross_l':    get_cube_state('4x4-top-cross-l'),
            'state_top_cross_i':    get_cube_state('4x4-top-cross-i'),
            'state_top_cross_done': get_cube_state('4x4-top-cross-done'),
            'state_top_cross_alg':  get_cube_state('4x4-top-cross-alg'),
        }

    # ── Étape 8 : Face du Haut ───────────────────────────────────────────
    if slug == 'top_face':
        return {
            'state_top_face_goal':  get_cube_state('4x4-top-face-goal'),
            'state_top_face_setup': get_cube_state('4x4-top-face-setup'),
            'state_corner_correct': get_cube_state('4x4-top-face-corner-correct'),
            'state_corner_twist1':  get_cube_state('4x4-top-face-corner-twist1'),
            'state_corner_twist2':  get_cube_state('4x4-top-face-corner-twist2'),
        }

    # ── Étape 9 : PLL Coins ──────────────────────────────────────────────
    if slug == 'pll_corners':
        return {
            'state_pll_corners_goal':          get_cube_state('4x4-pll-corners-goal'),
            'state_pll_corners_no_headlights': get_cube_state('4x4-pll-corners-no-headlights'),
            'state_pll_corners_one_headlight': get_cube_state('4x4-pll-corners-one-headlight'),
        }

    # ── Étape 10 : PLL Arêtes ────────────────────────────────────────────
    if slug == 'pll_edges':
        return {
            'state_pll_edges_goal':    get_cube_state('4x4-pll-edges-goal'),
            'state_pll_3_edges_right': get_cube_state('4x4-pll-3-edges-right'),
            'state_pll_3_edges_left':  get_cube_state('4x4-pll-3-edges-left'),
            'state_pll_edges_opp':     get_cube_state('4x4-pll-edges-opp'),
        }

    return {}


# ── Public views ──────────────────────────────────────────────────────────

def puzzle_4x4_home(request):
    return puzzle_home(request, CONFIG)

def puzzle_4x4_step(request, step):
    return puzzle_step(request, CONFIG, step, _named_states)

def puzzle_4x4_ref(request, ref):
    return puzzle_reference(request, CONFIG, REFERENCE_PAGES, ref, _named_states)
