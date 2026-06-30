"""
Apprenti Cubi method overview page.

Displays the list of all steps in the method with their descriptions.
"""

from django.shortcuts import render
from cube.models import CubeState
import json


def method_cubienewbie(request):
    """
    Main overview page for Apprenti Cubi method.
    
    Shows all 11 items (3 intro + 7 solving steps + 1 final) with descriptions,
    icons, cube states, and availability status.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': '/francontcube/', 'icon': 'book'},
        {'name': 'Cubie Newbie', 'url': '', 'icon': 'star-fill'},
    ]
    
    # Helper function to get cube state safely
    def get_cube_state(slug):
        try:
            state = CubeState.objects.get(slug=slug)
            # json_state is already a dict (JSONField), just return it as JSON string
            return json.dumps(state.json_state)
        except CubeState.DoesNotExist:
            return None
    
    steps = [
        {
            "name": "1 — A propos",
            "desc": "Au sujet de la méthode présenté pour les nouveaux cubeurs",
            "icon": "bi-cube",
            "url": "/main/methods/cubienewbie/about/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "2 — Le cube",
            "desc": "Comprendre les pièces, la structure et le fonctionnement.",
            "url": "/main/methods/cubienewbie/cube/",
            "youtube_id": "mxdhT0ZWzB8",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "3 — La notation",
            "desc": "Apprendre comment lire les mouvements (R, L, U, F…).",
            "icon": "bi-pencil",
            "url": "/main/methods/cubienewbie/notation/",
            "available": True,
            "cube_state": None  # No cube for intro
        },
        {
            "name": "4 — Mission 1: La marguerite",
            "desc": "Premier objectif : construire la marguerite autour du centre blanc.",
            "icon": "bi-flower3",
            "url": "/main/methods/cubienewbie/daisy/",
            "youtube_id": "ijyADdRXc7Y",
            "available": True,
            "cube_state": get_cube_state('marguerite-goal')
        },
        {
            "name": "5 — Mission 2 : La croix jaune parfaite",
            "desc": "Aligner les arêtes jaunes avec les centres pour former la croix.",
                        "url": "/main/methods/cubienewbie/bottom-cross/",
            "youtube_id": "OQ8ck1LWObk",
            "available": True,
            "cube_state": get_cube_state('bottom-cross-goal')
        },
        {
            "name": "6 — Mission 3 : Les coins magiques",
            "desc": "Placer les coins inférieurs jaunes pour compléter la première couche.",
            "url": "/main/methods/cubienewbie/bottom-corners/",
            "youtube_id": "1xNxfuMvrW8",
            "available": True,
            "cube_state": get_cube_state('bottom-corners-goal')
        },
        {
            "name": "7 — Mission 4 : Les arêtes voyageuses",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": "/main/methods/cubienewbie/second-layer/",
            "youtube_id": "vaHJ3Qb4ufI",
            "available": True,
            "cube_state": get_cube_state('second-layer-goal')
        },
        {
            "name": "8 — Mission 5 : La vraie croix blanche",
            "desc": "Former la croix blanche sur la face supérieure.",
            "icon": "bi-plus-circle",
            "url": "/main/methods/cubienewbie/top-cross/",
            "youtube_id": "eOU6A2fAEaI",
            "available": True,
            "cube_state": get_cube_state('top-cross-goal')
        },
        {
            "name": "9 — Mission 6 : La chasse au poisson",
            "desc": "La chasse au poisson.",
            "icon": "bi-brightness-high",
            "url": "/main/methods/cubienewbie/top-face/",
            "youtube_id": "lgHNc8m3jgM",
            "available": True,
            "cube_state": get_cube_state('top-face-goal')
        },
        {
            "name": "10 — Mission 7 : Les phares",
            "desc": "Placer les coins à leur bon emplacement.",
            "icon": "bi-arrow-repeat",
            "url": "/main/methods/cubienewbie/corner-permutation/",
            "youtube_id": "vVgyCC-MniQ",
            "available": True,
            "cube_state": get_cube_state('corner-perm-goal')
        },
        {
            "name": "11 — Mission 8 : L'alignement final",    
            "desc": "La permutation des arêtes de la couche superieur pour finir le cube.",
            "icon": "bi-check-circle",
            "url": "/main/methods/cubienewbie/edge-permutation/",
            "youtube_id": "zTiAbeoY4o4",
            "available": True,
            "cube_state": get_cube_state('edge-perm-goal-needsu')  # Final solved cube
        },
    ]

    return render(request, "main/methods/cubienewbie/index.html", {
        "steps": steps,
        "breadcrumbs": breadcrumbs
    })