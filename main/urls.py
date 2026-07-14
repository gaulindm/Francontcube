from django.urls import path

# Import organized views
from . import views

# CFOP specific imports (for clarity and organization)
from main.views.cfop.f2l import cfop, cfop_f2l_basic
from main.views.cfop.oll_pll import (
    cfop_oll_view,
    cfop_pll_view,
    oll_case_detail,
    pll_case_detail,
)
from main.views.cfop.two_look_oll import two_look_oll_view
from main.views.cfop.two_look_pll import two_look_pll_view
from main.views.cfop.beginner_to_f2l import beginner_to_f2l_bridge

# ⚠️ CORRECTION: Les vues d'introduction doivent être importées depuis leurs propres fichiers
# PAS depuis oll_pll.py
from main.views.cfop.f2l_intro import cfop_f2l_intro
from main.views.cfop.oll_intro import cfop_oll_intro
from main.views.cfop.pll_intro import cfop_pll_intro

# Other puzzles — each cube has its own view file
#from main.views.puzzles.home import puzzles_home
#from main.views.puzzles.puzzle_2x2 import (
#    puzzle_2x2_home,
#    puzzle_2x2_method,
#    puzzle_2x2_step,
#)
from main.views.puzzles.puzzle_4x4 import (
    puzzle_4x4_home,
    puzzle_4x4_step,
    puzzle_4x4_ref,
)
from main.views.puzzles.puzzle_5x5 import (
    puzzle_5x5_home,
    puzzle_5x5_step,
    puzzle_5x5_ref,
)

app_name = "main"

urlpatterns = [
    # ============================================================
    # HOME & LEGACY
    # ============================================================
    path("", views.home, name="home"),
    path("slides/", views.slides, name="slides"),
    path("pdfs/", views.pdfs, name="pdfs"),
    path("videos/", views.videos, name="videos"),
    path("ressources3par3/", views.ressources3par3, name="ressources3par3"),

    # ============================================================
    # MOSAIC
    # ============================================================
    path('mosaic/', views.mosaic, name='mosaic'),
    path('mosaic/about/', views.about, name='about'),
    path('mosaic/mosaic_steps/', views.mosaic_steps, name='mosiac_steps'),

    # ============================================================
    # CUBIE NEWBIE METHOD
    # ============================================================
    path('methods/cubienewbie/', views.method_cubienewbie, name='method_cubienewbie'),
    path('methods/cubienewbie/about/', views.cubienewbie_about, name='cubienewbie_about'),
    path('methods/cubienewbie/cube/', views.cubienewbie_cube_intro, name='cubienewbie_cube_intro'),
    path('methods/cubienewbie/notation/', views.cubienewbie_notation, name='cubienewbie_notation'),
    path('methods/cubienewbie/daisy/', views.cubienewbie_daisy, name='cubienewbie_daisy'),
    path('methods/cubienewbie/bottom-cross/', views.cubienewbie_bottom_cross, name='cubienewbie_bottom_cross'),
    path('methods/cubienewbie/bottom-corners/', views.cubienewbie_bottom_corners, name='cubienewbie_bottom_corners'),
    path('methods/cubienewbie/second-layer/', views.cubienewbie_second_layer, name='cubienewbie_second_layer'),
    path('methods/cubienewbie/top-cross/', views.cubienewbie_top_cross, name='cubienewbie_top_cross'),
    path('methods/cubienewbie/top-face/', views.cubienewbie_top_face, name='cubienewbie_top_face'),
    path('methods/cubienewbie/corner-permutation/', views.cubienewbie_corner_permutation, name='cubienewbie_corner_permutation'),
    path('methods/cubienewbie/edge-permutation/', views.cubienewbie_edge_permutation, name='cubienewbie_edge_permutation'),

    # ============================================================
    # CUBIE CURIEUX METHOD
    # ============================================================
    path('methods/cubiecurieux/', views.cubiecurieux_method, name='method_cubiecurieux'),
    path('methods/cubiecurieux/about/', views.cubiecurieux_about, name='cubiecurieux_about'),
    path('methods/cubiecurieux/bottom-cross/', views.cubiecurieux_bottom_cross, name='cubiecurieux_bottom_cross'),
    path('methods/cubiecurieux/bottom-corners/', views.cubiecurieux_bottom_corners, name='cubiecurieux_bottom_corners'),
    path('methods/cubiecurieux/second-layer/', views.cubiecurieux_second_layer, name='cubiecurieux_second_layer'),
    path('methods/cubiecurieux/2-look-oll/', views.cubiecurieux_two_look_oll, name='cubiecurieux_two_look_oll'),
    path('methods/cubiecurieux/2-look-pll/', views.cubiecurieux_two_look_pll, name='cubiecurieux_two_look_pll'),

    # ============================================================
    # CFOP METHOD
    # ============================================================
    path('methods/cfop/', views.method_cfop, name='method_cfop'),
    path('methods/cfop/about/', views.cfop_about, name='cfop_about'),
    path('methods/cfop/cross/', views.cfop_cross, name='cfop_cross'),
    path('methods/cfop/beginner-to-f2l/', beginner_to_f2l_bridge, name='beginner_to_f2l'),

    # ──────────────────────────────────────────────────────────
    # F2L Routes — most specific first
    # ──────────────────────────────────────────────────────────
    path('methods/cfop/f2l/introduction/', cfop_f2l_intro, name='cfop_f2l_intro'),
    path('methods/cfop/f2l/basic/', views.cfop_f2l_basic, name='cfop_f2l_basic'),
    path('methods/cfop/f2l/<str:category>/', cfop_f2l_basic, name='cfop_f2l_category'),

    # ──────────────────────────────────────────────────────────
    # OLL Routes — most specific first
    # ──────────────────────────────────────────────────────────
    path('methods/cfop/oll/2-look/', two_look_oll_view, name='two_look_oll'),
    path('methods/cfop/oll/introduction/', cfop_oll_intro, name='cfop_oll_intro'),
    path('methods/cfop/oll/case/<slug:slug>/', oll_case_detail, name='oll_case_detail'),
    path('methods/cfop/oll/<str:category>/', cfop_oll_view, name='cfop_oll_category'),
    path('methods/cfop/oll/', cfop_oll_view, name='cfop_oll'),

    # ──────────────────────────────────────────────────────────
    # PLL Routes — most specific first
    # ──────────────────────────────────────────────────────────
    path('methods/cfop/pll/2-look/', two_look_pll_view, name='two_look_pll'),
    path('methods/cfop/pll/introduction/', cfop_pll_intro, name='cfop_pll_intro'),
    path('methods/cfop/pll/case/<slug:slug>/', pll_case_detail, name='pll_case_detail'),
    path('methods/cfop/pll/<str:category>/', cfop_pll_view, name='cfop_pll_category'),
    path('methods/cfop/pll/', cfop_pll_view, name='cfop_pll'),

    # ============================================================
    # OTHER PUZZLES
    # ============================================================

    # ── Hub ────────────────────────────────────────────────────
    #path('puzzles/', puzzles_home, name='puzzles_home'),

    # ── 2×2 ────────────────────────────────────────────────────
#    path('puzzles/2x2/', puzzle_2x2_home, name='2x2_home'),
#    path('puzzles/2x2/<str:method>/<str:step>/', puzzle_2x2_step, name='2x2_step'),
#    path('puzzles/2x2/<str:method>/', puzzle_2x2_method, name='2x2_method'),

    # ── 4×4 — most specific first ──────────────────────────────
    path('puzzles/4x4/ref/<str:ref>/', puzzle_4x4_ref,  name='4x4_ref'),
    path('puzzles/4x4/<str:step>/',    puzzle_4x4_step, name='4x4_step'),
    path('puzzles/4x4/',               puzzle_4x4_home, name='4x4_home'),

    # ── 5×5 — most specific first ──────────────────────────────
    path('puzzles/5x5/ref/<str:ref>/', puzzle_5x5_ref,  name='5x5_ref'),
    path('puzzles/5x5/<str:step>/',    puzzle_5x5_step, name='5x5_step'),
    path('puzzles/5x5/',               puzzle_5x5_home, name='5x5_home'),

    # ============================================================
    # OTHER METHODS (legacy - to be migrated)
    # ============================================================
    path('methods/f2l/', views.method_f2l, name='method_f2l'),
    path('methods/roux/', views.method_roux, name='method_roux'),
]