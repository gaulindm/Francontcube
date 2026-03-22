# cubing_users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import Cuber, Leader, Group, GroupMembership
from .forms import (
    CuberRegistrationForm, CuberLoginForm,
    LeaderRegistrationForm, LeaderLoginForm,
    GroupCreationForm, JoinGroupForm
)
from .decorators import cuber_required, leader_required
from .authentication import CuberAuthenticationBackend
from .constants import COLOR_EMOJIS


# ==========================================
# VIEWS CUBEURS (Étudiants)
# ==========================================

def cuber_register(request):
    """Inscription d'un nouveau cubeur"""
    if request.method == 'POST':
        form = CuberRegistrationForm(request.POST)
        if form.is_valid():
            cuber = form.save()

            request.session['cuber_id'] = str(cuber.cuber_id)

            messages.success(
                request,
                f"Bienvenue {cuber.color} {cuber.adjective} {cuber.superhero}! 🎉"
            )
            return redirect('cubing_users:join_group')
    else:
        form = CuberRegistrationForm()

    return render(request, 'cubing_users/cuber_register.html', {'form': form})


def cuber_login(request):
    """Connexion d'un cubeur existant"""
    if request.method == 'POST':

        # ── DEBUG (retirer une fois le login confirmé) ──────────────────
        print("=== cuber_login POST ===")
        print(f"  color:        {request.POST.get('color')!r}")
        print(f"  adjective:    {request.POST.get('adjective')!r}")
        print(f"  superhero:    {request.POST.get('superhero')!r}")
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
            color      = form.cleaned_data['color']
            adjective  = form.cleaned_data['adjective']
            superhero  = form.cleaned_data['superhero']
            color_code = form.get_color_code()

            # ── DEBUG ────────────────────────────────────────────────────
            print(f"  color_code assemblé: {color_code}")
            print(f"  color_code joint:    {','.join(color_code)!r}")
            # ────────────────────────────────────────────────────────────

            backend = CuberAuthenticationBackend()
            cuber = backend.authenticate(
                request,
                color=color,
                adjective=adjective,
                superhero=superhero,
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
                    f"Bon retour {cuber.color} {cuber.adjective} {cuber.superhero}! 🎯"
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
    """Déconnexion d'un cubeur"""
    cuber_name = f"{request.cuber.color} {request.cuber.adjective} {request.cuber.superhero}"
    if 'cuber_id' in request.session:
        del request.session['cuber_id']
    messages.info(request, f"À bientôt {cuber_name}! 👋")
    return redirect('cubing_users:cuber_login')


@cuber_required
def cuber_dashboard(request):
    """Dashboard principal du cubeur"""
    cuber = request.cuber

    memberships = GroupMembership.objects.filter(
        cuber=cuber,
        status='active'
    ).select_related('group')

    # TODO: Intégrer avec cube.models quand prêt
    f2l_stats = {
        'cases_completed': 0,
        'total_cases': 41,
        'average_time': 0,
        'recent_practice': []
    }

    return render(request, 'cubing_users/cuber_dashboard.html', {
        'cuber': cuber,
        'memberships': memberships,
        'f2l_stats': f2l_stats,
    })


@cuber_required
def join_group(request):
    """Rejoindre un groupe avec un code"""
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
    """Liste des groupes du cubeur"""
    memberships = GroupMembership.objects.filter(
        cuber=request.cuber,
        status='active'
    ).select_related('group').prefetch_related('group__leaders')

    return render(request, 'cubing_users/my_groups.html', {'memberships': memberships})


@cuber_required
def group_leaderboard(request, group_id):
    """Leaderboard d'un groupe spécifique"""
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


# ==========================================
# VIEWS LEADERS (Enseignants/Coachs)
# ==========================================

def leader_register(request):
    """Inscription d'un nouveau leader"""
    if request.method == 'POST':
        form = LeaderRegistrationForm(request.POST)
        if form.is_valid():
            leader = form.save()
            login(request, leader.user)
            messages.success(
                request,
                f"Bienvenue {leader.user.get_full_name()}! Ton compte leader est créé. 🎓"
            )
            return redirect('cubing_users:leader_dashboard')
    else:
        form = LeaderRegistrationForm()

    return render(request, 'cubing_users/leader_register.html', {'form': form})


def leader_login(request):
    """Connexion d'un leader existant"""
    if request.method == 'POST':
        form = LeaderLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user and hasattr(user, 'leader_profile'):
                login(request, user)
                messages.success(request, f"Bon retour {user.get_full_name()}!")
                return redirect('cubing_users:leader_dashboard')
            else:
                messages.error(request, "Adresse courriel ou mot de passe incorrect.")
    else:
        form = LeaderLoginForm()

    return render(request, 'cubing_users/leader_login.html', {'form': form})


@login_required
@leader_required
def leader_logout(request):
    """Déconnexion d'un leader"""
    logout(request)
    messages.info(request, "Déconnexion réussie. À bientôt!")
    return redirect('cubing_users:leader_login')


@login_required
@leader_required
def leader_dashboard(request):
    """Dashboard principal du leader"""
    leader = request.user.leader_profile

    groups = Group.objects.filter(leaders=leader).annotate(
        member_count=Count('groupmembership', filter=Q(groupmembership__status='active'))
    ).order_by('-created_date')

    total_students = GroupMembership.objects.filter(
        group__leaders=leader, status='active'
    ).values('cuber').distinct().count()

    return render(request, 'cubing_users/leader_dashboard.html', {
        'leader': leader,
        'groups': groups,
        'total_students': total_students,
    })


@login_required
@leader_required
def create_group(request):
    """Créer un nouveau groupe"""
    if request.method == 'POST':
        form = GroupCreationForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.leaders.add(request.user.leader_profile)
            messages.success(
                request,
                f"Groupe '{group.group_name}' créé avec succès! Code: {group.group_code}"
            )
            return redirect('cubing_users:group_detail', group_id=group.group_id)
    else:
        form = GroupCreationForm()

    return render(request, 'cubing_users/create_group.html', {'form': form})


@login_required
@leader_required
def group_detail(request, group_id):
    """Détails d'un groupe (pour le leader)"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber').order_by('joined_date')

    stats = {
        'total_members': memberships.count(),
        'active_this_week': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
        # TODO: Ajouter stats F2L réelles
    }

    return render(request, 'cubing_users/group_detail.html', {
        'group': group,
        'memberships': memberships,
        'stats': stats,
    })


@login_required
@leader_required
def group_roster(request, group_id):
    """
    Liste complète des membres d'un groupe.
    Chaque ligne affiche display_name (préfixe TOSM ou identité cubeur)
    pour que le leader puisse identifier chaque élève rapidement.
    """
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber').order_by('first_name_prefix', 'last_name_prefix', 'cuber__color', 'cuber__adjective')

    return render(request, 'cubing_users/group_roster.html', {
        'group': group,
        'memberships': memberships,
    })


@login_required
@leader_required
def student_progress(request, group_id, cuber_id):
    """Détails du progrès d'un étudiant spécifique"""
    group = get_object_or_404(Group, group_id=group_id)
    cuber = get_object_or_404(Cuber, cuber_id=cuber_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    membership = get_object_or_404(
        GroupMembership, cuber=cuber, group=group, status='active'
    )

    # TODO: Récupérer les vraies stats F2L depuis l'app cube
    progress_data = {
        'cases_completed': 0,
        'total_cases': 41,
        'average_time': 0,
        'recent_sessions': [],
        'best_times': [],
    }

    return render(request, 'cubing_users/student_progress.html', {
        'group': group,
        'cuber': cuber,
        'membership': membership,
        'progress_data': progress_data,
    })


@login_required
@leader_required
def group_statistics(request, group_id):
    """Statistiques globales du groupe"""
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber')

    stats = {
        'total_members': memberships.count(),
        'active_today': memberships.filter(
            cuber__last_active_date__date=timezone.now().date()
        ).count(),
        'active_this_week': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'active_this_month': memberships.filter(
            cuber__last_active_date__gte=timezone.now() - timedelta(days=30)
        ).count(),
        # TODO: Ajouter stats F2L réelles
        'avg_completion': 0,
        'avg_time': 0,
    }

    return render(request, 'cubing_users/group_statistics.html', {
        'group': group,
        'stats': stats,
        'memberships': memberships,
    })


@login_required
@leader_required
def print_login_cards(request, group_id):
    """
    Page pour imprimer les cartes de connexion des membres.
    Affiche display_name à côté de l'identité cubeur pour que le leader
    puisse distribuer les bonnes cartes aux bons élèves.
    Format: "TOSM → 🔴 Rouge Brave Spiderman"
    """
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber').order_by('first_name_prefix', 'last_name_prefix', 'cuber__color')

    # color_codes sont hashés — non récupérables.
    # Si un élève a perdu son code, utiliser leader_reset_color_code.

    return render(request, 'cubing_users/print_login_cards.html', {
        'group': group,
        'memberships': memberships,
        'color_emojis': COLOR_EMOJIS,
    })


# ==========================================
# VIEWS LEADER — GESTION DES IDENTIFIANTS
# ==========================================

@login_required
@leader_required
def leader_set_identification(request, group_id, cuber_id):
    """
    Le leader corrige les 2 premières lettres du prénom et du nom d'un élève.
    Ex: "TO" + "SM" → affiche "TOSM" dans la liste du groupe.
    """
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    membership = get_object_or_404(
        GroupMembership, cuber__cuber_id=cuber_id, group=group, status='active'
    )

    if request.method == 'POST':
        membership.first_name_prefix = request.POST.get('first_name_prefix', '').strip()
        membership.last_name_prefix = request.POST.get('last_name_prefix', '').strip()
        membership.save()  # save() normalizes prefixes to uppercase automatically

        messages.success(
            request,
            f"Identification mise à jour → {membership.display_name}"
        )
        return redirect('cubing_users:group_roster', group_id=group_id)

    return render(request, 'cubing_users/set_identification.html', {
        'group': group,
        'membership': membership,
    })


@login_required
@leader_required
def leader_reset_color_code(request, group_id, cuber_id):
    """
    Le leader réinitialise le code couleur d'un élève qui l'a oublié.

    Flux :
      GET  → formulaire de confirmation (affiche l'identité cubeur + display_name)
      POST → définit le nouveau code, affiche la valeur en clair UNE SEULE FOIS
             → le leader la note et la remet à l'élève en mains propres

    Sécurité : seul un leader du groupe peut faire cette action.
    Le code en clair n'est JAMAIS stocké — uniquement son hash SHA-256.
    """
    group = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    cuber = get_object_or_404(Cuber, cuber_id=cuber_id)

    # Confirm the cuber is actually an active member of this group
    membership = get_object_or_404(
        GroupMembership, cuber=cuber, group=group, status='active'
    )

    # Only populated after a successful POST — shown once in the template
    new_code_plain = None

    if request.method == 'POST':
        new_code = request.POST.get('new_color_code', '').strip()

        if not new_code:
            messages.error(request, "Le nouveau code couleur ne peut pas être vide.")
        else:
            cuber.set_color_code(new_code)
            cuber.save()
            new_code_plain = new_code  # ← shown once in template, then gone
            messages.success(
                request,
                f"Code couleur réinitialisé pour {membership.display_name} "
                f"({cuber}). Note-le maintenant — il ne sera plus affiché!"
            )

    return render(request, 'cubing_users/reset_color_code.html', {
        'group': group,
        'cuber': cuber,
        'membership': membership,
        'new_code_plain': new_code_plain,
    })


# ==========================================
# VIEWS PUBLIQUES
# ==========================================

def home(request):
    """Page d'accueil du système cubing"""
    return render(request, 'cubing_users/home.html', {
        'total_cubers': Cuber.objects.count(),
        'total_groups': Group.objects.count(),
    })