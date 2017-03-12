import re

import spotipy


def check_track_with_url(message):
    """
    Return spotify id of possible track in message.
    """

    sp = spotipy.Spotify()
    # look for string containing track and an id
    if "spotify.com" in message:
        pattern = re.search("track/(\w+)\W*", message)
        if pattern:
            res=pattern.group(1)
            return sp.track(res)['id']

    return None


def check_track_with_keywords(message):
    """ look for track with artist name or song name
    Returns url
    """

    sp = spotipy.Spotify()
    results = sp.search(q='track:' + message, type='track')
    for r in results['tracks']['items']:
        return r['external_urls']['spotify']
    return None



def id_to_url(id):
    """
    Returns track url from id
    """
    sp = spotipy.Spotify()
    track = sp.track(id)
    if track:
       return track['external_urls']['spotify']
    return None

def get_metadata(id):
    """
    Returns metadata given track id
    """
    sp = spotipy.Spotify()
    track = sp.track(id)
    if track:
        artist = track['artists'][0]['name']
        uri = track['uri']
        name = track['name']
    return artist, name, uri


#print check_track_with_url("https://open.spotify.com/track/3ZFTkvIE7kyPt6Nu3PEa7V")
#print check_track_with_keywords("Eminem - Space bound ")
#print get_metadata("7BHPGtpuuWWsvE7cCaMuEU")
#print id_to_url("spotify:track:7BHPGtpuuWWsvE7cCaMuEU")
