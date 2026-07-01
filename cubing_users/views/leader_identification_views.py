# cubing_users/views/leader_identification_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ..models import Cuber, Group, GroupMembership
from ..decorators import leader_required


# ==========================================
# VIEWS LEADER — GESTION DES IDENTIFIANTS
# ==========================================


@leader_required
def leader_set_identification(request, group_id, cuber_id):
    """
    Le leader corrige les 2 premières lettres du prénom et du nom d'un élève.
    Ex: "TO" + "SM" → affiche "TOSM" dans la liste du groupe.
    """
    group  = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    membership = get_object_or_404(
        GroupMembership, cuber__cuber_id=cuber_id, group=group, status='active'
    )

    if request.method == 'POST':
        membership.first_name_prefix = request.POST.get('first_name_prefix', '').strip()
        membership.last_name_prefix  = request.POST.get('last_name_prefix', '').strip()
        membership.save()  # save() normalise les préfixes en majuscules automatiquement

        messages.success(
            request,
            f"Identification mise à jour → {membership.display_name}"
        )
        return redirect('cubing_users:group_roster', group_id=group_id)

    return render(request, 'cubing_users/set_identification.html', {
        'group': group,
        'membership': membership,
    })



@leader_required
def leader_reset_color_code(request, group_id, cuber_id):
    """
    Le leader réinitialise le code couleur d'un élève qui l'a oublié.

    Flux :
      GET  → formulaire de confirmation (affiche display_name du cubeur)
      POST → définit le nouveau code, affiche la valeur en clair UNE SEULE FOIS
             → le leader la note et la remet à l'élève en mains propres

    Sécurité : seul un leader du groupe peut faire cette action.
    Le code en clair n'est JAMAIS stocké — uniquement son hash SHA-256.
    """
    group  = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    cuber = get_object_or_404(Cuber, cuber_id=cuber_id)

    membership = get_object_or_404(
        GroupMembership, cuber=cuber, group=group, status='active'
    )

    # Seulement rempli après un POST réussi — affiché une seule fois dans le template
    new_code_plain = None

    if request.method == 'POST':
        new_code = request.POST.get('new_color_code', '').strip()

        if not new_code:
            messages.error(request, "Le nouveau code couleur ne peut pas être vide.")
        else:
            cuber.set_color_code(new_code)
            cuber.save()
            new_code_plain = new_code  # ← affiché une fois dans le template, puis perdu
            messages.success(
                request,
                f"Code couleur réinitialisé pour {membership.display_name} "
                f"({cuber.display_name}). Note-le maintenant — il ne sera plus affiché!"
            )

    return render(request, 'cubing_users/reset_color_code.html', {
        'group': group,
        'cuber': cuber,
        'membership': membership,
        'new_code_plain': new_code_plain,
    })
