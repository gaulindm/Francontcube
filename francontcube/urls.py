from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    # Apps (namespaced)
    path('main/', include(('main.urls', 'main'), namespace='main')),
    path('cuber/', include(('cubing_users.urls', 'cubing_users'), namespace='cubing_users')),
    path('cube_prep/', include(('cube_prep.urls', 'cube_prep'), namespace='cube_prep')),
    path('training/', include(('training.urls', 'training'), namespace='training')),
    path('cube/', include(('cube.urls', 'cube'), namespace='cube')),

    # Root URL → redirect to main home
    path('', lambda request: redirect('main:home')),
    
]