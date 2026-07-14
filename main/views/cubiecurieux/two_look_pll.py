# main/views/cubiecurieux/two_look_pll.py
"""
2-Look PLL — Cubie-Curieux
6 algorithmes répartis en 3 groupes (coins d'abord, arêtes ensuite),
chacun avec son écusson.
"""

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState

TWO_LOOK_PLL_GROUPS = [
{
        'slug': 'coins',
        'name': 'Permutation des Coins',
        'icon': 'bi-triangle-fill',
        'description': "Place les coins à leur bonne position avant de t'occuper des arêtes.",
        'badge_slug': 'cubie-curieux-2lpll-corners',
        'badge_name': 'Coins en Place',
        'cases': [
            {
                'name': 'Y-perm',
                'algorithm': "F R U' R' U' R U R' F' R U R' U' R' F R F'",
                'recognition': "Aucun phare sur la couche du haut",
            },
            {
                'name': 'T-perm',
                'algorithm': "R U R' U' R' F R2 U' R' U' R U R' F'",
                'recognition': "Phare sur le côté gauche",
            },
        ],
    },
    {
        'slug': 'aretes-adjacentes',
        'name': 'Arêtes Adjacentes',
        'icon': 'bi-arrow-left-right',
        'description': "Les coins sont bons — permute maintenant 3 arêtes voisines.",
        'badge_slug': 'cubie-curieux-2lpll-adjacent',
        'badge_name': 'Arêtes Adjacentes',
        'cases': [
            {
                'name': 'Cycle vers la droite',
                'algorithm': "R U' R U R U R U' R' U' R2",
                'recognition': "3 arêtes à tourner, sens antihoraire",
            },
            {
                'name': 'Cycle vers la gauche',
                'algorithm': "L' U L' U' L' U' L' U L U L2",
                'recognition': "3 arêtes à tourner, sens horaire",
                
            },
        ],
    },
    {
        'slug': 'aretes-opposees',
        'name': 'Arêtes Opposées',
        'icon': 'bi-arrows-collapse',
        'description': "Les deux derniers cas : arêtes échangées deux par deux.",
        'badge_slug': 'cubie-curieux-2lpll-opposite',
        'badge_name': 'Arêtes Opposées',
        'cases': [
            {
                'name': 'H-perm',
                'algorithm': "R2 U2 R U2 R2 U2 R2 U2 R U2 R2",
                'recognition': "Les 4 arêtes opposées deux par deux",
            },
            {
                'name': 'Z-perm',
                'algorithm': "R U R' U R' U' R' U R U' R' U' R2 U R U2",
                'recognition': "Arêtes adjacentes échangées en diagonale",
            },
        ],
    },
]


def _is_badge_earned(request, badge_slug):
    """
    Un écusson est considéré "obtenu" sur cette page si le cubeur a complété
    le quiz honor-system (quiz_complete) — pas besoin de validation leader
    pour l'affichage ici.
    """
    cuber = getattr(request, 'cuber', None)
    if not cuber:
        return False

    from badges.models import CuberBadge

    return CuberBadge.objects.filter(
        cuber=cuber, badge__slug=badge_slug, quiz_complete=True
    ).exists()


def two_look_pll_view(request):
    groups = []
    for group in TWO_LOOK_PLL_GROUPS:
        cases = []
        for case in group['cases']:
            cases.append({
                **case,
                'setup_alg': CubeState.invert_alg(case['algorithm']),
                'display_algorithm': case['algorithm'],
            })

        groups.append({
            'slug': group['slug'],
            'name': group['name'],
            'icon': group['icon'],
            'description': group['description'],
            'cases': cases,
            'badge': {
                'slug': group['badge_slug'],
                'name': group['badge_name'],
                'earned': _is_badge_earned(request, group['badge_slug']),
            },
        })

    context = {
        'page_title': '2-Look PLL — Cubie-Curieux',
        'page_description': "Termine ton cube en permutant coins puis arêtes — seulement 6 algorithmes.",
        'groups': groups,
        'total_algorithms': 6,
        'breadcrumbs': [
            {'name': 'Méthodes', 'url': reverse('main:home'), 'icon': 'book'},
            {'name': 'Cubie-Curieux', 'url': reverse('main:method_cubiecurieux'), 'icon': 'star-fill'},
            {'name': '2-Look PLL', 'icon': 'arrow-repeat'},
        ],
    }
    return render(request, 'main/methods/cubiecurieux/two_look_pll.html', context)