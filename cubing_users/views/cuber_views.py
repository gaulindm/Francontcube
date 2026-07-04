# cubing_users/views/cuber_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone

from ..models import Group, GroupMembership
from ..forms import CuberRegistrationForm, CuberLoginForm, JoinGroupForm
from ..decorators import cuber_required
from ..authentication import CuberAuthenticationBackend

from badges.models import Badge, CuberBadge

# Ordre d'affichage des familles d'écussons sur le tableau de bord.
# Les brevets sont gérés séparément (case à trophées, pas dans cette liste).
BADGE_FAMILY_ORDER = [
    ('cubie-newbie', '🌱 Cubie-Newbie'),
    ('curieux', '🔷 Cubie-Curieux'),
    ('f2l', '🟩 F2L'),
    ('oll', '☀️ OLL'),
    ('pll', '🔁 PLL'),
    ('avance', '🚀 Avancé'),
    ('meta', '🏅 Méta'),
]


# ==========================================
# VIEWS CUBEURS (Étudiants)
# ==========================================

def cuber_register(request):
    """Inscription d'un nouveau cubeur — wizard 3 étapes géré côté template."""
    if request.method == 'POST':
        form = CuberRegistrationForm(request.POST)
        if form.is_valid():
            cuber = form.save()
            request.session['cuber_id'] = str(cuber.cuber_id)
            messages.success(
                request,
                f"Bienvenue {cuber.display_name}! 🎉"
            )
            return redirect('cubing_users:join_group')
    else:
        form = CuberRegistrationForm()

    return render(request, 'cubing_users/cuber_register.html', {'form': form})


def cuber_login(request):
    """Connexion d'un cubeur existant."""
    if request.method == 'POST':

        # ── DEBUG (retirer une fois le login confirmé) ──────────────────
        print("=== cuber_login POST ===")
        print(f"  animal:       {request.POST.get('animal')!r}")
        print(f"  cube_color:   {request.POST.get('cube_color')!r}")
        print(f"  quality_1:    {request.POST.get('quality_1')!r}")
        print(f"  quality_2:    {request.POST.get('quality_2')!r}")
        print(f"  color_code_1: {request.POST.get('color_code_1')!r}")
        print(f"  color_code_6: {request.POST.get('color_code_6')!r}")
        # ────────────────────────────────────────────────────────────────

        form = CuberLoginForm(request.POST)

        if not form.is_valid():
            # ── DEBUG ────────────────────────────────────────────────────
            print(f"  form invalide: {form.errors}")
            # ────────────────────────────────────────────────────────────
            messages.error(request, "Formulaire invalide. Vérifie tous les champs.")
        else:
            animal     = form.cleaned_data['animal']
            cube_color = form.cleaned_data['cube_color']
            quality_1  = form.cleaned_data['quality_1']
            quality_2  = form.cleaned_data['quality_2']
            color_code = form.get_color_code()

            # ── DEBUG ────────────────────────────────────────────────────
            print(f"  color_code assemblé: {color_code}")
            print(f"  color_code joint:    {','.join(color_code)!r}")
            # ────────────────────────────────────────────────────────────

            backend = CuberAuthenticationBackend()
            cuber = backend.authenticate(
                request,
                animal=animal,
                cube_color=cube_color,
                quality_1=quality_1,
                quality_2=quality_2,
                color_code=','.join(color_code)
            )

            # ── DEBUG ────────────────────────────────────────────────────
            print(f"  cuber trouvé: {cuber}")
            # ────────────────────────────────────────────────────────────

            if cuber:
                request.session['cuber_id'] = str(cuber.cuber_id)
                cuber.last_active_date = timezone.now()
                cuber.save()

                # ── DEBUG ────────────────────────────────────────────────
                print(f"  session cuber_id: {request.session['cuber_id']}")
                # ────────────────────────────────────────────────────────

                messages.success(
                    request,
                    f"Bon retour {cuber.display_name}! 🎯"
                )
                return redirect('cubing_users:cuber_dashboard')
            else:
                messages.error(
                    request,
                    "Identité ou code couleur incorrect. Vérifie et réessaie!"
                )
    else:
        form = CuberLoginForm()

    return render(request, 'cubing_users/cuber_login.html', {'form': form})


@cuber_required
def cuber_logout(request):
    """Déconnexion d'un cubeur."""
    cuber_name = request.cuber.display_name
    if 'cuber_id' in request.session:
        del request.session['cuber_id']
    messages.info(request, f"À bientôt {cuber_name}! 👋")
    return redirect('cubing_users:cuber_login')


@cuber_required
def cuber_dashboard(request):
    """Dashboard principal du cubeur — foulard, écussons, et groupes."""
    cuber = request.cuber

    memberships = GroupMembership.objects.filter(
        cuber=cuber,
        status='active'
    ).select_related('group')

    all_badges = Badge.objects.filter(active=True)
    cuber_progress = {
        cb.badge_id: cb
        for cb in CuberBadge.objects.filter(cuber=cuber).select_related('badge')
    }

    def badge_item(badge):
        cb = cuber_progress.get(badge.badge_id)
        return {'badge': badge, 'status': cb.status if cb else 'disponible'}

    brevets = [badge_item(b) for b in all_badges.filter(is_brevet=True)]

    badge_families = []
    for key, label in BADGE_FAMILY_ORDER:
        family_badges = [badge_item(b) for b in all_badges.filter(family=key)]
        if family_badges:
            badge_families.append({'key': key, 'label': label, 'badges': family_badges})

    badges_total_count = all_badges.exclude(is_brevet=True).count()
    badges_unlocked_count = sum(
        1 for fam in badge_families for item in fam['badges']
        if item['status'] == 'debloque'
    )

    return render(request, 'cubing_users/cuber_dashboard.html', {
        'cuber': cuber,
        'memberships': memberships,
        'brevets': brevets,
        'badge_families': badge_families,
        'badges_unlocked_count': badges_unlocked_count,
        'badges_total_count': badges_total_count,
    })


@cuber_required
def join_group(request):
    """Rejoindre un groupe avec un code."""
    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            group = form.get_group()
            cuber = request.cuber

            if GroupMembership.objects.filter(cuber=cuber, group=group).exists():
                messages.warning(request, f"Tu es déjà membre de {group.group_name}!")
                return redirect('cubing_users:cuber_dashboard')

            GroupMembership.objects.create(
                cuber=cuber,
                group=group,
                status='active',
                # Seed from what the student entered at registration.
                # The leader can always override via leader_set_identification.
                first_name_prefix=cuber.first_name_prefix,
                last_name_prefix=cuber.last_name_prefix,
            )
            messages.success(request, f"Bravo! Tu as rejoint {group.group_name}! 🎉")
            return redirect('cubing_users:cuber_dashboard')
    else:
        form = JoinGroupForm()

    return render(request, 'cubing_users/join_group.html', {'form': form})


@cuber_required
def my_groups(request):
    """Liste des groupes du cubeur."""
    memberships = GroupMembership.objects.filter(
        cuber=request.cuber,
        status='active'
    ).select_related('group').prefetch_related('group__leaders')

    return render(request, 'cubing_users/my_groups.html', {'memberships': memberships})


@cuber_required
def group_leaderboard(request, group_id):
    """Leaderboard d'un groupe spécifique."""
    group = get_object_or_404(Group, group_id=group_id)

    if not GroupMembership.objects.filter(cuber=request.cuber, group=group).exists():
        messages.error(request, "Tu n'es pas membre de ce groupe!")
        return redirect('cubing_users:cuber_dashboard')

    members = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber')

    # TODO: Ajouter les stats F2L réelles quand intégré avec cube app
    leaderboard_data = [
        {
            'cuber': m.cuber,
            'joined_date': m.joined_date,
            'avg_time': 0,
            'cases_completed': 0,
        }
        for m in members
    ]

    return render(request, 'cubing_users/group_leaderboard.html', {
        'group': group,
        'leaderboard_data': leaderboard_data,
        'is_member': True,
    })