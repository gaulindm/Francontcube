# cubing_users/views/leader_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from ..models import Cuber, Group, GroupMembership
from ..forms import LeaderRegistrationForm, LeaderLoginForm, GroupCreationForm
from ..decorators import leader_required


# ==========================================
# VIEWS LEADERS (Enseignants/Coachs)
# ==========================================

def leader_register(request):
    """
    Formulaire de demande de compte Leader.
    Crée une LeaderRequest en attente — pas de compte actif tant que non approuvée.
    """
    if request.method == 'POST':
        form = LeaderRegistrationForm(request.POST)
        if form.is_valid():
            leader_request = form.save()
            return render(request, 'cubing_users/leader_register.html', {
                'form': form,
                'request_submitted': True,
                'submitted_name': f"{leader_request.first_name} {leader_request.last_name}",
            })
    else:
        form = LeaderRegistrationForm()

    return render(request, 'cubing_users/leader_register.html', {'form': form})


def leader_login(request):
    """Connexion d'un leader existant."""
    if request.method == 'POST':
        form = LeaderLoginForm(request.POST)
        if form.is_valid():
            email    = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # DEBUG
            User = get_user_model()
            try:
                u = User.objects.get(username=email)
                print(f"User trouvé: {u}")
                print(f"is_active: {u.is_active}")
                print(f"password hash début: {u.password[:30]}")
                print(f"check_password: {u.check_password(password)}")
                print(f"has leader_profile: {hasattr(u, 'leader_profile')}")
            except User.DoesNotExist:
                print(f"❌ Aucun User avec username={email!r}")

            user = authenticate(request, username=email, password=password)
            print(f"authenticate() retourne: {user}")

            if user and hasattr(user, 'leader_profile'):
                login(request, user)
                messages.success(request, f"Bon retour {user.get_full_name()}!")
                return redirect('cubing_users:leader_dashboard')
            else:
                messages.error(request, "Adresse courriel ou mot de passe incorrect.")
    else:
        form = LeaderLoginForm()

    return render(request, 'cubing_users/leader_login.html', {'form': form})



@leader_required
def leader_logout(request):
    """Déconnexion d'un leader."""
    logout(request)
    messages.info(request, "Déconnexion réussie. À bientôt!")
    return redirect('cubing_users:leader_login')


@leader_required
def leader_dashboard(request):
    """Dashboard principal du leader."""
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



@leader_required
def create_group(request):
    """Créer un nouveau groupe."""
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



@leader_required
def group_detail(request, group_id):
    """Détails d'un groupe (pour le leader)."""
    group  = get_object_or_404(Group, group_id=group_id)
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


@leader_required
def group_roster(request, group_id):
    """
    Liste complète des membres d'un groupe.
    Chaque ligne affiche display_name (préfixe TOSM ou identité cubeur)
    pour que le leader puisse identifier chaque élève rapidement.
    """
    group  = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber').order_by(
        'first_name_prefix', 'last_name_prefix',
        'cuber__animal', 'cuber__cube_color'
    )

    return render(request, 'cubing_users/group_roster.html', {
        'group': group,
        'memberships': memberships,
    })



@leader_required
def student_progress(request, group_id, cuber_id):
    """Détails du progrès d'un étudiant spécifique."""
    group  = get_object_or_404(Group, group_id=group_id)
    cuber  = get_object_or_404(Cuber, cuber_id=cuber_id)
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



@leader_required
def group_statistics(request, group_id):
    """Statistiques globales du groupe."""
    group  = get_object_or_404(Group, group_id=group_id)
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



@leader_required
def print_login_cards(request, group_id):
    """
    Page pour imprimer les cartes de connexion des membres.
    Affiche display_name à côté de l'identité cubeur pour que le leader
    puisse distribuer les bonnes cartes aux bons élèves.
    Format: "TOSM → Hibou Courageux (foulard bleu)"
    """
    group  = get_object_or_404(Group, group_id=group_id)
    leader = request.user.leader_profile

    if leader not in group.leaders.all():
        messages.error(request, "Tu n'as pas accès à ce groupe.")
        return redirect('cubing_users:leader_dashboard')

    memberships = GroupMembership.objects.filter(
        group=group, status='active'
    ).select_related('cuber').order_by(
        'first_name_prefix', 'last_name_prefix', 'cuber__animal'
    )

    # color_codes sont hashés — non récupérables.
    # Si un élève a perdu son code, utiliser leader_reset_color_code.

    return render(request, 'cubing_users/print_login_cards.html', {
        'group': group,
        'memberships': memberships,
    })
