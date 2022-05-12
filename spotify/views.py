from django.shortcuts import render, redirect
from spotify_release import SpotifyRelease
from spotipy.oauth2 import SpotifyPKCE
from .forms import NameForm
import os

scope = "playlist-read-private, user-library-read, playlist-modify-private"


class SpAuth:
    auth_sp = SpotifyPKCE(scope=scope)

    def auth(self):
        link = SpAuth.auth_sp.get_authorize_url()
        print(link)
        print('something')
        return redirect(link)

    def get_token(self):
        token = SpAuth.auth_sp.get_access_token(self.GET.get('code'), check_cache=False)
        print(token)
        global sp
        sp = SpotifyRelease(token)
        print('Success')
        return redirect('/playlists')

def playlist(request):
    playlist = request.GET.get('id')
    result_info = sp.playlist_search(playlist)
    return render(request, 'artists.html', {'result_info': result_info})


def playlist_output(request):
    pl_function = sp.get_playlists()
    playlist_out = pl_function[0]
    playlist_id = pl_function[1]
    print(playlist_id[1])
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            pl_number = form.cleaned_data['user_playlists']
            result_info = sp.playlist_search(playlist_id[int(pl_number)])
            return render(request, 'artists.html', {'result_info': result_info})
    else:
        form = NameForm()
    return render(request, 'user_playlists.html', {'playlists': playlist_out, 'form': form})


def main_page(request):
    return render(request, 'mainpage.html')


def features(request):
    return render(request, 'features.html')