import re
import urllib
import spotipy


def check_track_with_url(message):
    """
    Return spotify id of possible track in message.
    """

    sp = spotipy.Spotify()
    # look for string containing track and an id
    if "spotify.com" in message:
        pattern = re.search("track/(\w+)\W*",message)
        if pattern:
            res=pattern.group(1)
            return sp.track(res)['uri']
    return None

def search_for_name_and_artist(w1,w2):
    sp = spotipy.Spotify()
    results = sp.search(q='artist:' + w1, type='artist')
    items = results['artists']['items']
    ptential=None
    for artist in items:
        if artist["name"] == w1:
            tracks = sp.artist_top_tracks(artist["uri"])
            for track in tracks['tracks'][:20]:
                a=re.sub("\W+", "", w2).lower()
                b=re.sub("\W+", "", track['name']).lower()          
                potential=track['external_urls']['spotify']
                if a in b or b in a:
                    return potential
    return potential

def check_track_with_keywords(message):               
    """ look for track with artist name or song name
    Returns url
    """

    ww = message.split('-')
    
    if len(ww) !=2:
        return None

    w1 = ww[0].strip()
    w2 = ww[1].strip()

    x = search_for_name_and_artist(w1,w2)
    if x:   
        return x

    #do the same thing for artist and name in opposite order

    return search_for_name_and_artist(w2,w1)


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
    return (artist,name,uri)

#print check_track_with_url("https://open.spotify.com/track/3ZFTkvIE7kyPt6Nu3PEa7V")
#print check_track_with_keywords("Frank Sinatra - Fly me to the moon ")
#print get_metadata("3ZFTkvIE7kyPt6Nu3PEa7V")