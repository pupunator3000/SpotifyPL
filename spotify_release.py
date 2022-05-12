import spotipy
import re
from time import strftime
from datetime import date


class SpotifyRelease(spotipy.Spotify):

    def __init__(self, token):
        self.spotify_session = spotipy.Spotify(auth=token)

    def get_playlists(self):
        """Get user playlists"""
        results = self.spotify_session.current_user_playlists()
        views_out = {}
        plids = {}
        for idx, item in enumerate(results['items']):
            name = item['name']
            total = item['tracks']
            plids[idx+1] = item['id']
            views_out[item['id']] = str(name)+' - '+str(total['total'])+' tracks total'
        return views_out, plids

    def already_exists_check(self, pl_id):
        """Check if playlist with name '...new releases' already exists, if there is none - create one

        Keyword argument:
        pl_id -- id of selected playlist
        """
        playlists = self.spotify_session.current_user_playlists()
        pl_name = self.spotify_session.playlist(pl_id)['name']
        for playlist in playlists['items']:
            print('\nChecking if playlist', playlist['name'], '==', pl_name+' new releases')
            print(playlist['name'] == pl_name+' new releases\n')
            if playlist['name'] == pl_name+' new releases':
                print('Playlist with id', playlist['id'], 'already exists\n')
                return playlist['id']
        print('Creating new playlist...\n')
        return self.spotify_session.user_playlist_create(self.spotify_session.me()['id'], pl_name + ' new releases', public=False,
                                                         description='New releases based on playlist ' + pl_name)['id']

    def get_playlist_artists(self, pl_id):
        """Get artists from playlist, and store each inside dict

        Keyword argument:
        pl_id -- id of selected playlist
        """
        print('\nPlaylist "', self.spotify_session.playlist(pl_id)['name'], '" has been selected\nSearching for new releases...\n')
        results = self.spotify_session.playlist(pl_id)['tracks']
        artist_dict = {}
        if results['next']:
            while results['next']:
                for item in (results['items']):
                    artist_dict[item['track']['artists'][0]['id']] = [item['track']['artists'][0]['name']]
                results = self.spotify_session.next(results)
        if results['next'] is None:
            for item in (results['items']):
                artist_dict[item['track']['artists'][0]['id']] = [item['track']['artists'][0]['name']]
        return artist_dict

    def playlist_search(self, pl_id):
        """Search for new releases of each artist which was released within a week

        Keyword argument:
        pl_id -- id of selected playlist
        """
        print('\nPlaylist "', self.spotify_session.playlist(pl_id)['name'], '" has been selected\nSearching for new releases...\n')
        results = self.spotify_session.playlist(pl_id)['tracks']
        artist_dict = {}
        if results['next']:
            while results['next']:
                for item in (results['items']):
                    artist_dict[item['track']['artists'][0]['id']] = [item['track']['artists'][0]['name']]
                results = self.spotify_session.next(results)
        if results['next'] is None:
            for item in (results['items']):
                artist_dict[item['track']['artists'][0]['id']] = [item['track']['artists'][0]['name']]
        album_info = set()
        for artist_id in artist_dict:
            album_data = self.spotify_session.artist_albums(artist_id, None, None, 20, 0)
            album_pre_info = {}
            for item in album_data['items']:
                album_id = item['id']
                album_available_markets = item['available_markets']
                album_release_date = item['release_date']
                current_date = date(int((strftime('%Y'))), int(strftime('%m')), int(strftime('%d')))
                convert_album_release_date = re.split(r'-', album_release_date)
                if item['album_group'] == 'appears_on':
                    break
                else:
                    if len(convert_album_release_date) > 1:
                        release_date = date(int(convert_album_release_date[0]), int(convert_album_release_date[1]),
                                            int(convert_album_release_date[2]))
                        day_diff = (current_date - release_date).days
                        if day_diff >= 7:
                            continue
                        else:
                            if len(album_pre_info) > 0:
                                if album_release_date in album_pre_info:
                                    if len(album_pre_info[album_release_date][1]) > len(album_available_markets):
                                        print('Seems like album id', album_pre_info[album_release_date][0], '(',
                                              item['name'], 'by', item['artists'][0]['name'], ')', 'is similar to id',
                                              album_id, ' but second one available in more countries')
                                        print('Founded ', item['artists'][0]['name'] + "'s",
                                              '"' + item['name'] + '"', 'released at', item['release_date'])
                                        album_info.add(album_id)
                                        break
                                    else:
                                        print('Seems like album id', album_pre_info[album_release_date][0], '(',
                                              item['name'], 'by', item['artists'][0]['name'], ')', 'is similar to id',
                                              album_id, ' but first one available in more countries')
                                        album_info.add(album_pre_info[album_release_date][0])
                                        print('Founded ', item['artists'][0]['name'] + "'s",
                                              '"' + item['name'] + '"', 'released at', item['release_date'])
                                        break
                                else:
                                    album_info.add(album_id)
                                    print('Founded ', item['artists'][0]['name'] + "'s",
                                          '"' + item['name'] + '"', 'released at', item['release_date'])
                                    album_pre_info[album_release_date] = [album_id, album_available_markets]
                            else:
                                album_info.add(album_id)
                                print('Founded ', item['artists'][0]['name']+"'s",
                                      '"'+item['name']+'"', 'released at', item['release_date'])
                                album_pre_info[album_release_date] = [album_id, album_available_markets]
                    else:
                        continue
        html_out = []
        counter_albums = 0
        counter_songs = 0
        plid_for_adding = self.already_exists_check(pl_id)
        html_out.append('Adding to playlist with id ' + plid_for_adding)
        print('Adding to playlist with id ', plid_for_adding, '\n')
        for track in self.spotify_session.playlist(plid_for_adding)['tracks']['items']:
            if track['track']['album']['id'] in album_info:
                album_info.discard(track['track']['album']['id'])
                print('Track', track['track']['album']['artists'][0]['name'], track['track']['name'], ' already exists!'
                                                                                                      ' Skipping...')
        for album_id in album_info:
            counter_albums += 1
            album_tracks = self.spotify_session.album(album_id)
            print('\nFor artist ', '"'+album_tracks['artists'][0]['name']+'"', ' added:')
            html_out.append('')
            html_out.append('For artist '+'"'+album_tracks['artists'][0]['name']+'" added')
            for idx, item in enumerate(album_tracks['tracks']['items']):
                track_id = [item['id']]
                self.spotify_session.user_playlist_add_tracks(self.spotify_session.me()['id'], plid_for_adding, track_id)
                print(idx + 1, ': ', item['name'], 'from album', album_tracks['name'])
                html_out.append(str(idx + 1)+ ': ' + item['name'] + 'from album'+ album_tracks['name'])
                counter_songs += 1
        print("\nAdded: ", counter_albums, 'new albums. Total', counter_songs, 'songs')
        html_out.append("Added: " + str(counter_albums) + ' new albums. Total ' + str(counter_songs) + ' songs')
        return html_out
