# badges/urls.py
from django.urls import path
from . import views

app_name = 'badges'

urlpatterns = [
    path('confirm/<slug:slug>/', views.confirm_badge, name='confirm_badge'),
]