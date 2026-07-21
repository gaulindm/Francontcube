# main/views/cubiecurieux/two_look_oll_v2.py
"""
2-Look OLL — Cubie-Curieux (v2)
Version pilotée par CubeState : les 10 algorithmes viennent de la base de
données (chargés via `load_cubiecurieux_2look`), pas d'un dict Python.

Nouveautés vs. two_look_oll.py :
  - Diagramme de reconnaissance SVG (généré par `generate_recognition_svgs`,
    basé sur une vraie simulation du cube -- jamais désynchronisé de
    l'algorithme réel)
  - Algorithme affiché en icônes de mouvement (comme sur les pages
    d'entraînement) plutôt qu'en texte brut

Fichier temporaire pendant la transition : coexiste avec two_look_oll.py
sur une URL séparée jusqu'à validation complète, puis bascule + suppression
de l'ancien fichier.
"""

from django.shortcuts import render
from django.urls import reverse
from django.templatetags.static import static
from cube.models import CubeState

# ── Métadonnées des groupes (analogue à F2L_CATEGORIES) ─────────────────
OLL_CATEGORY_META = {
    'croix': {
        'name': 'Croix Blanche',
        'icon': 'bi-plus-lg',
        'description': "Orienter les arêtes pour former une croix blanche sur le dessus.",
        'badge_slug': 'cubie-curieux-2loll-edges',
        'badge_name': 'Croix Blanche',
    },
    'sune': {
        'name': 'Sune & Anti-Sune',
        'icon': 'bi-star-fill',
        'description': "Les deux algorithmes fondamentaux — à maîtriser en premier.",
        'badge_slug': 'cubie-curieux-oll-sune',
        'badge_name': 'Sune & Anti-Sune',
    },
    'hpi': {
        'name': 'H & Pi',
        'icon': 'bi-grid-3x3',
        'description': "Deux cas obtenus par double application de Sune.",
        'badge_slug': 'cubie-curieux-oll-hpi',
        'badge_name': 'H & Pi',
    },
    'tul': {
        'name': 'T, U & L',
        'icon': 'bi-shuffle',
        'description': "Les trois derniers cas pour compléter la face blanche.",
        'badge_slug': 'cubie-curieux-oll-tul',
        'badge_name': 'T, U & L',
    },
}

# Alternates main gauche -- pas encore un champ CubeState dédié, donc gardé
# ici en attendant (candidat pour un futur champ `left_hand_algorithm`).
LEFT_HAND_OVERRIDES = {
    'cc-oll-anti-sune': "L' U' L U' L' U2 L",
}

CATEGORY_ORDER = ['croix', 'sune', 'hpi', 'tul']


def _is_badge_earned(request, badge_slug):
    cuber = getattr(request, 'cuber', None)
    if not cuber:
        return False

    from badges.models import CuberBadge

    return CuberBadge.objects.filter(
        cuber=cuber, badge__slug=badge_slug, quiz_complete=True
    ).exists()


def two_look_oll_view(request):
    cases = CubeState.objects.filter(
        method='cubiecurieux', stickering='OLL'
    ).order_by('category', 'step_number')

    by_category = {}
    for case in cases:
        by_category.setdefault(case.category, []).append(case)

    groups = []
    for cat_slug in CATEGORY_ORDER:
        meta = OLL_CATEGORY_META[cat_slug]
        cat_cases = by_category.get(cat_slug, [])

        case_contexts = []
        for case in cat_cases:
            left_hand_alg = LEFT_HAND_OVERRIDES.get(case.slug)
            case_contexts.append({
                'slug': case.slug,
                'name': case.name,
                'algorithm': case.algorithm,
                'setup_alg': case.get_setup_alg(),
                'recognition': case.description,
                'algorithm_svg': case.get_algorithm_svg(),
                'recognition_svg_url': static(f'cube/recognition/{case.slug}.svg'),
                'stickering': case.stickering,
                'camera_longitude': case.camera_longitude,
                'camera_latitude': case.camera_latitude,
                'left_hand_tip': left_hand_alg,
                'left_hand_tip_svg': (
                    CubeState.render_algorithm_svg(left_hand_alg) if left_hand_alg else None
                ),
            })

        groups.append({
            'slug': cat_slug,
            'name': meta['name'],
            'icon': meta['icon'],
            'description': meta['description'],
            'cases': case_contexts,
            'badge': {
                'slug': meta['badge_slug'],
                'name': meta['badge_name'],
                'earned': _is_badge_earned(request, meta['badge_slug']),
            },
        })

    context = {
        'page_title': '2-Look OLL — Cubie-Curieux',
        'page_description': "Maîtrise l'orientation de la dernière couche en seulement 10 algorithmes.",
        'groups': groups,
        'total_algorithms': cases.count(),
        'breadcrumbs': [
            {'name': 'Méthodes', 'url': reverse('main:home'), 'icon': 'book'},
            {'name': 'Cubie-Curieux', 'url': reverse('main:method_cubiecurieux'), 'icon': 'star-fill'},
            {'name': '2-Look OLL', 'icon': 'brightness-high'},
        ],
    }
    return render(request, 'main/methods/cubiecurieux/two_look_oll.html', context)