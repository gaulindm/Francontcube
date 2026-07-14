# main/views/cubiecurieux/two_look_oll.py
"""
2-Look OLL — Cubie-Curieux
10 algorithmes répartis en 4 groupes, chacun avec son écusson.
"""

from django.shortcuts import render
from django.urls import reverse
from cube.models import CubeState

TWO_LOOK_OLL_GROUPS = [
    {
        'slug': 'croix',
        'name': 'Croix Blanche',
        'icon': 'bi-plus-lg',
        'description': "Orienter les arêtes pour former une croix blanche sur le dessus.",
        'badge_slug': 'cubie-curieux-2loll-edges',
        'badge_name': 'Croix Blanche',
        'cases': [
            {'name': 'Point → Croix', 'algorithm': "F R U R' U' F' f R U R' U' f'",
            'recognition': 'Aucune arête blanche sur le dessus',
            'trigger_groups': [1, 4, 1, 1, 4, 1]},  # F RUR'U' F' f RUR'U' f'
            {'name': 'Ligne → Croix', 'algorithm': "F R U R' U' F'",
            'recognition': 'Ligne horizontale blanche',
            'trigger_groups': [1, 4, 1]},           # F RUR'U' F'
            {'name': 'Forme L → Croix', 'algorithm': "f R U R' U' f'",
            'recognition': 'Forme L blanche à gauche',
            'trigger_groups': [1, 4, 1]},           # f RUR'U' f'
        ],
    },
    {
        'slug': 'sune',
        'name': 'Sune & Anti-Sune',
        'icon': 'bi-star-fill',
        'description': "Les deux algorithmes fondamentaux — à maîtriser en premier.",
        'badge_slug': 'cubie-curieux-oll-sune',
        'badge_name': 'Sune & Anti-Sune',
        'cases': [
            {'name': 'Sune', 'algorithm': "R U R' U R U2 R'",
             'recognition': 'Motif poisson — phares à droite'},
            {'name': 'Anti-Sune', 'algorithm': "R U2 R' U' R U' R'",
             'recognition': 'Motif poisson — phares à gauche',
             'left_hand_tip': "L' U' L U' L' U2 L"},
        ],
    },
    {
        'slug': 'hpi',
        'name': 'H & Pi',
        'icon': 'bi-grid-3x3',
        'description': "Deux cas obtenus par double application de Sune.",
        'badge_slug': 'cubie-curieux-oll-hpi',
        'badge_name': 'H & Pi',
        'cases': [
            {'name': 'Motif H', 'algorithm': "R U R' U R U' R' U R U2 R'",
             'recognition': 'Motif damier'},
            {'name': 'Motif Pi', 'algorithm': "R U2 R2 U' R2 U' R2 U2 R",
             'recognition': 'Deux phares devant'},
        ],
    },
    {
        'slug': 'tul',
        'name': 'T, U & L',
        'icon': 'bi-shuffle',
        'description': "Les trois derniers cas pour compléter la face blanche.",
        'badge_slug': 'cubie-curieux-oll-tul',
        'badge_name': 'T, U & L',
        'cases': [
            {'name': 'Motif T', 'algorithm': "r U R' U' r' F R F'",
             'recognition': 'Forme T devant'},
            {'name': 'Motif U', 'algorithm': "R2 D R' U2 R D' R' U2 R'",
             'recognition': 'Forme U face à vous'},
            {'name': 'Motif L', 'algorithm': "F R' F' r U R U' r'",
             'recognition': 'Forme L dans le coin'},
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

def group_display(algorithm, groups):
    """
    Formate un algorithme pour l'affichage en collant certains groupes de moves.
    groups = liste d'entiers indiquant combien de moves coller ensemble à chaque groupe.
    La somme de groups doit égaler le nombre de moves dans l'algorithme.

    Exemple : group_display("F R U R' U' F'", [1, 4, 1])
              → "F RUR'U' F'"
    """
    moves = algorithm.split()
    assert sum(groups) == len(moves), (
        f"group_display: {sum(groups)} moves attendus dans groups, "
        f"{len(moves)} trouvés dans '{algorithm}'"
    )
    parts = []
    i = 0
    for g in groups:
        parts.append(''.join(moves[i:i + g]))
        i += g
    return ' '.join(parts)


def two_look_oll_view(request):
    groups = []
    for group in TWO_LOOK_OLL_GROUPS:
        cases = []
        for case in group['cases']:
            display = case['algorithm']
            if 'trigger_groups' in case:
                display = group_display(case['algorithm'], case['trigger_groups'])
            cases.append({
                **case,
                'setup_alg': CubeState.invert_alg(case['algorithm']),
                'display_algorithm': display,
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
        'page_title': '2-Look OLL — Cubie-Curieux',
        'page_description': "Maîtrise l'orientation de la dernière couche en seulement 10 algorithmes.",
        'groups': groups,
        'total_algorithms': 10,
        'breadcrumbs': [
            {'name': 'Méthodes', 'url': reverse('main:home'), 'icon': 'book'},
            {'name': 'Cubie-Curieux', 'url': reverse('main:method_cubiecurieux'), 'icon': 'star-fill'},
            {'name': '2-Look OLL', 'icon': 'brightness-high'},
        ],
    }
    return render(request, 'main/methods/cubiecurieux/two_look_oll.html', context)