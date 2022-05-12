from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('get/', views.SpAuth.get_token, name='get'),
    path('features/', views.features, name='features'),
    path('redirect/', views.SpAuth.auth, name='redirect'),
    path('playlists/', views.playlist_output, name='output'),
    path('playlist/', views.playlist, name='playlist'),
]
