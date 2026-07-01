# cubing_users/views/__init__.py
"""
Point d'entrée du package views.

Toutes les vues sont ré-exportées ici pour que le reste du projet
(urls.py, etc.) puisse continuer à faire:
    from cubing_users import views
    views.cuber_login
    views.leader_dashboard
    ...
sans rien changer ailleurs dans le code.
"""

from .public_views import home

from .cuber_views import (
    cuber_register,
    cuber_login,
    cuber_logout,
    cuber_dashboard,
    join_group,
    my_groups,
    group_leaderboard,
)

from .leader_views import (
    leader_register,
    leader_login,
    leader_logout,
    leader_dashboard,
    create_group,
    group_detail,
    group_roster,
    student_progress,
    group_statistics,
    print_login_cards,
)

from .leader_identification_views import (
    leader_set_identification,
    leader_reset_color_code,
)

__all__ = [
    # Public
    'home',

    # Cubeurs (Étudiants)
    'cuber_register',
    'cuber_login',
    'cuber_logout',
    'cuber_dashboard',
    'join_group',
    'my_groups',
    'group_leaderboard',

    # Leaders (Enseignants/Coachs)
    'leader_register',
    'leader_login',
    'leader_logout',
    'leader_dashboard',
    'create_group',
    'group_detail',
    'group_roster',
    'student_progress',
    'group_statistics',
    'print_login_cards',

    # Leaders — Gestion des identifiants
    'leader_set_identification',
    'leader_reset_color_code',
]
