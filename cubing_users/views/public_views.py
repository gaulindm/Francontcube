# cubing_users/views/public_views.py
from django.shortcuts import render

from ..models import Cuber, Group


# ==========================================
# VIEWS PUBLIQUES
# ==========================================

def home(request):
    """Page d'accueil du système cubing."""
    return render(request, 'cubing_users/home.html', {
        'total_cubers': Cuber.objects.count(),
        'total_groups': Group.objects.count(),
    })
