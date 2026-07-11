"""
Francontcube views module.

This module organizes views into a clean directory structure:
- base.py: Reusable utilities and base classes
- home.py: Home page and legacy views
- mosaic/: Pages for preparing mosaic
- cubienewbie/: Apprenti Cubi method views (8 step views)
- cubiecurieux/: Cubie-Curieux method views
- cfop/: CFOP method views
- roux/: Roux method views (coming soon)
- puzzles/: Other puzzles (2x2, 4x4, 5x5)

All views are exported from this module for easy URL routing.
"""

# ============================================================
# HOME & LEGACY VIEWS
# ============================================================
from .home import (
    home,
    mosaic,
    method_cubiecurieux,
    method_f2l,
    method_roux,
    slides,
    pdfs,
    videos,
    ressources3par3,
    tutorial_step,
)

# ============================================================
# MOSAIC
# ============================================================
from .mosaic.main import mosaic
from .mosaic.about import about as about
from .mosaic.mosaic_steps import mosaic_steps as mosaic_steps


# ============================================================
# CUBIE NEWBIE METHOD
# ============================================================
from .cubienewbie.main import method_cubienewbie
from .cubienewbie.daisy import daisy as cubienewbie_daisy
from .cubienewbie.bottom_cross import bottom_cross as cubienewbie_bottom_cross
from .cubienewbie.bottom_corners import bottom_corners as cubienewbie_bottom_corners
from .cubienewbie.second_layer import second_layer as cubienewbie_second_layer
from .cubienewbie.top_cross import top_cross as cubienewbie_top_cross
from .cubienewbie.top_face import top_face as cubienewbie_top_face
from .cubienewbie.corner_permutation import corner_permutation as cubienewbie_corner_permutation
from .cubienewbie.edge_permutation import edge_permutation as cubienewbie_edge_permutation
from .cubienewbie.cube_intro import cube_intro as cubienewbie_cube_intro
from .cubienewbie.notation import notation as cubienewbie_notation
from .cubienewbie.about import about as cubienewbie_about

# ============================================================
# CUBIE CURIEUX METHOD
# ============================================================
from .cubiecurieux.main import method_cubiecurieux as cubiecurieux_method
from .cubiecurieux.bottom_cross import bottom_cross as cubiecurieux_bottom_cross
from .cubiecurieux.bottom_corners import bottom_corners as cubiecurieux_bottom_corners
from .cubiecurieux.second_layer import second_layer as cubiecurieux_second_layer
from .cubiecurieux.two_look_oll import two_look_oll_view as cubiecurieux_two_look_oll

from .cubiecurieux.top_cross import top_cross as cubiecurieux_top_cross
from .cubiecurieux.top_face import top_face as cubiecurieux_top_face
from .cubiecurieux.corner_permutation import corner_permutation as cubiecurieux_corner_permutation
from .cubiecurieux.edge_permutation import edge_permutation as cubiecurieux_edge_permutation
from .cubiecurieux.about import about as cubiecurieux_about

# ============================================================
# CFOP METHOD
# ============================================================
from .cfop.main import method_cfop
from .cfop.about import about as cfop_about
from .cfop.cross import cross as cfop_cross
from .cfop.f2l import cfop, cfop_f2l_basic

# CFOP Introduction Pages
from .cfop.f2l_intro import cfop_f2l_intro
from .cfop.oll_intro import cfop_oll_intro
from .cfop.pll_intro import cfop_pll_intro

from .cfop.beginner_to_f2l import beginner_to_f2l_bridge as cubiecurieux_to_f2l_bridge

# 2-Look OLL
from .cfop.two_look_oll import two_look_oll_view

# OLL & PLL - New system with categories and filtering
from .cfop.oll_pll import (
    cfop_oll_view,
    cfop_pll_view,
    oll_case_detail,
    pll_case_detail,
)

# ============================================================
# OTHER PUZZLES (2x2, 4x4, 5x5)
# ============================================================
from .puzzles.home import puzzles_home

#from .puzzles.puzzle_2x2 import (
#    puzzle_2x2_home,
#    puzzle_2x2_method,
#    puzzle_2x2_step,
#)

from .puzzles.puzzle_4x4 import (
    puzzle_4x4_home,
    puzzle_4x4_step,
    puzzle_4x4_ref,
)

from .puzzles.puzzle_5x5 import (
    puzzle_5x5_home,
    puzzle_5x5_step,
    puzzle_5x5_ref,
)

# ============================================================
# EXPORTS
# ============================================================
__all__ = [
    # Home & legacy
    'home',
    'method_cubiecurieux',
    'method_f2l',
    'method_roux',
    'slides',
    'pdfs',
    'videos',
    'ressources3par3',
    'tutorial_step',

    # Mosaic
    'mosaic',
    'about',
    'mosaic_steps',

    # Cubie Newbie
    'method_cubienewbie',
    'cubienewbie_about',
    'cubienewbie_cube_intro',
    'cubienewbie_notation',
    'cubienewbie_daisy',
    'cubienewbie_bottom_cross',
    'cubienewbie_bottom_corners',
    'cubienewbie_second_layer',
    'cubienewbie_top_cross',
    'cubienewbie_top_face',
    'cubienewbie_corner_permutation',
    'cubienewbie_edge_permutation',

    # Cubie Curieux Method
    'cubiecurieux_method',
    'cubiecurieux_about',
    'cubiecurieux_bottom_cross',
    'cubiecurieux_bottom_corners',
    'cubiecurieux_second_layer',
#    'cubiecurieux_top_cross',
#    'cubiecurieux_top_face',
    'cubiecurieux_two_look_oll',     

    'cubiecurieux_corner_permutation',
    'cubiecurieux_edge_permutation',

    # CFOP
    'method_cfop',
    'cfop_about',
    'cfop_cross',
    'cfop',
    'cfop_f2l_basic',

    # CFOP Introduction Pages
    'cfop_f2l_intro',
    'cfop_oll_intro',
    'cfop_pll_intro',
    'cubiecurieux_to_f2l_bridge',

    # OLL & PLL
    'cfop_oll_view',
    'cfop_pll_view',
    'oll_case_detail',
    'pll_case_detail',
    'cfop_two_look_oll_legacy',  

    # Other puzzles
    'puzzles_home',
    #'puzzle_2x2_home',
    #'puzzle_2x2_method',
    #'puzzle_2x2_step',
    'puzzle_4x4_home',
    'puzzle_4x4_step',
    'puzzle_4x4_ref',
    'puzzle_5x5_home',
    'puzzle_5x5_step',
    'puzzle_5x5_ref',
]