# main/views/cubiecurieux/two_look_pll_v2.py
"""
2-Look PLL — Cubie-Curieux (v2)
Version pilotée par CubeState, même architecture que two_look_oll_v2.py :
  - Diagramme de reconnaissance SVG statique (généré par
    `generate_recognition_svgs`, ou retouché manuellement pour les cas PLL
    où les vraies couleurs sont conservées -- voir note ci-dessous)
  - Algorithme affiché en icônes de mouvement, pas de TwistyPlayer

Note couleurs : contrairement à OLL (strictement blanc/gris), les
diagrammes PLL gardent les vraies couleurs sur les flancs -- c'est ce qui
révèle si une pièce est bien placée ou non. Ce choix a été fait à la main
(fichiers SVG retouchés directement) plutôt que dans le générateur, donc
`generate_recognition_svgs.py` n'a pas besoin d'être modifié pour ça.

Fichier temporaire pendant la transition, comme two_look_oll_v2.py :
coexiste avec two_look_pll.py sur une URL séparée jusqu'à validation
complète.
"""

from django.shortcuts import render
from django.urls import reverse
from django.templatetags.static import static
from cube.models import CubeState

# ── Métadonnées des groupes (analogue à F2L_CATEGORIES / OLL_CATEGORY_META) ──
PLL_CATEGORY_META = {
    'coins': {
        'name': 'Permutation des Coins',
        'icon': 'bi-triangle-fill',
        'description': "Place les coins à leur bonne position avant de t'occuper des arêtes.",
        'badge_slug': 'cubie-curieux-2lpll-corners',
        'badge_name': 'Coins en Place',
    },
    'aretes-adjacentes': {
        'name': 'Arêtes Adjacentes',
        'icon': 'bi-arrow-left-right',
        'description': "Les coins sont bons — permute maintenant 3 arêtes voisines.",
        'badge_slug': 'cubie-curieux-2lpll-adjacent',
        'badge_name': 'Arêtes Adjacentes',
    },
    'aretes-opposees': {
        'name': 'Arêtes Opposées',
        'icon': 'bi-arrows-collapse',
        'description': "Les deux derniers cas : arêtes échangées deux par deux.",
        'badge_slug': 'cubie-curieux-2lpll-opposite',
        'badge_name': 'Arêtes Opposées',
    },
}

CATEGORY_ORDER = ['coins', 'aretes-adjacentes', 'aretes-opposees']


def _is_badge_earned(request, badge_slug):
    cuber = getattr(request, 'cuber', None)
    if not cuber:
        return False

    from badges.models import CuberBadge

    return CuberBadge.objects.filter(
        cuber=cuber, badge__slug=badge_slug, quiz_complete=True
    ).exists()


def two_look_pll_view(request):
    cases = CubeState.objects.filter(
        method='cubiecurieux', stickering='PLL'
    ).order_by('category', 'step_number')

    by_category = {}
    for case in cases:
        by_category.setdefault(case.category, []).append(case)

    groups = []
    for cat_slug in CATEGORY_ORDER:
        meta = PLL_CATEGORY_META[cat_slug]
        cat_cases = by_category.get(cat_slug, [])

        case_contexts = []
        for case in cat_cases:
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
        'page_title': '2-Look PLL — Cubie-Curieux',
        'page_description': "Termine ton cube en permutant coins puis arêtes — seulement 6 algorithmes.",
        'groups': groups,
        'total_algorithms': cases.count(),
        'breadcrumbs': [
            {'name': 'Méthodes', 'url': reverse('main:home'), 'icon': 'book'},
            {'name': 'Cubie-Curieux', 'url': reverse('main:method_cubiecurieux'), 'icon': 'star-fill'},
            {'name': '2-Look PLL', 'icon': 'arrow-repeat'},
        ],
    }
    return render(request, 'main/methods/cubiecurieux/two_look_pll.html', context)