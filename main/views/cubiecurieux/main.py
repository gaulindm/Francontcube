"""
Beginner method overview page.
"""

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState
import json



def method_cubiecurieux(request):
    """
    Main overview page for the Cubie Curieux method.
    """
    breadcrumbs = [
        {'name': 'Méthodes', 'url': reverse('main:home'), 'icon': 'book'},
        {'name': 'Cubie Curieux', 'url': '', 'icon': 'star-fill'},  # Page actuelle, URL vide
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
            "name": "À propos",
            "desc": "Présentation de la méthode débutant pour résoudre le Rubik's Cube",
            "icon": "bi-info-circle",
            "url": reverse('main:cubiecurieux_about'),
            "available": True,
            "step_number": None,
        },
        {
            "name": "Étape 1 : La croix jaune",
            "desc": "Aligner les arêtes jaunes avec les centres pour former la croix.",
            "icon": "bi-plus-circle",
            "url": reverse('main:cubiecurieux_bottom_cross'),
            "available": True,
            "step_number": 1,
            "cube_state": get_cube_state('bottom-cross-goal')

        },
        {
            "name": "Étape 2 : Les coins inférieurs",
            "desc": "Placer les coins inférieurs jaunes pour compléter la première couche.",
            "icon": "bi-box",
            "url": reverse('main:cubiecurieux_bottom_corners'),
            "available": True,
            "step_number": 2,
            "cube_state": get_cube_state('bottom-corners-goal')

        },
        {
            "name": "Étape 3 : Les bords du milieu",
            "desc": "Placer les arêtes du milieu pour compléter les deux premières rangées du bas.",
            "icon": "bi-arrows-expand",
            "url": reverse('main:cubiecurieux_second_layer'),
            "available": True,
            "step_number": 3,
            "cube_state": get_cube_state('second-layer-goal')

        },
        {
            "name": "Étape 4 : 2-Look OLL",
            "desc": "Orienter la face du dessus en 10 algorithmes — croix blanche, puis Sune, H, Pi, T, U, L.",
            "icon": "bi-brightness-high",
            "url": reverse('main:cubiecurieux_two_look_oll'),
            "available": True,
            "step_number": 4,
            "cube_state": get_cube_state('top-face-goal')

        },
        {
            "name": "Étape 5 : 2-Look PLL",
            "desc": "Permuter les coins puis les arêtes de la dernière couche pour terminer le cube.",
            "icon": "bi-check-circle",
            "url": reverse('main:cubiecurieux_two_look_pll'),
            "available": True,
            "step_number": 5,
            "icon": "bi-arrow-repeat",

        },
    ]

    context = {
        "steps": steps,
        "breadcrumbs": breadcrumbs,
        "method_name": "Truc Cubie Curieux",
        "method_description": "Une méthode efficace en 5 étapes pour résoudre le Rubik's Cube 3x3",
        "total_steps": 5,
        "difficulty": "Débutant",
        "estimated_time": "3-4 heures d'apprentissage",
    }

    return render(request, "main/methods/cubiecurieux/index.html", context)