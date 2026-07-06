# badges/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from .models import Badge, CuberBadge


@require_POST
def confirm_badge(request, slug):
    """
    Confirmation honnête du cubeur pour un écusson à auto-validation
    (honor system — ex: "J'ai fini ma marguerite!").

    Ne fonctionne QUE si le badge n'exige ni auto-track ni validation
    leader — sinon retourne une erreur, pour empêcher de contourner un
    écusson qui a besoin d'une vraie vérification.
    """
    if request.cuber is None:
        return JsonResponse(
            {'ok': False, 'auth_required': True},
            status=200,
        )

    badge = get_object_or_404(Badge, slug=slug, active=True)

    if badge.requires_auto_track or badge.requires_leader_validation:
        return JsonResponse(
            {'ok': False, 'error': "Cet écusson nécessite une autre forme de validation."},
            status=400,
        )

    cuberbadge, _ = CuberBadge.objects.get_or_create(
        cuber=request.cuber, badge=badge
    )
    cuberbadge.complete_self_check()

    return JsonResponse({
        'ok': True,
        'status': cuberbadge.status,
        'badge_name': badge.name,
        'badge_icon': badge.icon,
    })