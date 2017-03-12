import sys

import spotipy
import spotipy.util as util


def log(message):  # simple wrapper for logging to stdout on heroku
    print str(message)
    sys.stdout.flush()


class PlaylistHandler:
    '''
    Create a playlist and add tracks to it
    '''

    def __init__(self, username="floris.kint@gmail.com"):
        scope = 'playlist-modify-public'
        token = util.prompt_for_user_token(username, scope)
        self.sp = spotipy.Spotify(auth=token)
        self.user_id = None
        self.playlist_id = None
        if token:
            self.user_id = self.sp.current_user()['id']
            if self.user_id:
                playlist = self.sp.user_playlist_create(self.user_id, "Results")
                if playlist and playlist.get('id'):
                    self.playlist_id = playlist.get('id')
                    log("created playlist")

    def add_to_playlist(self, track_ids):
        if self.playlist_id:
            self.sp.user_playlist_add_tracks(self.user_id, self.playlist_id, track_ids)
            log("added song to playlist")

if __name__ == "__main__":
    ph = PlaylistHandler()
    track_url = ["0xBsZrUrsZcCCrpxryZDHc"]
    ph.add_to_playlist(track_url)
