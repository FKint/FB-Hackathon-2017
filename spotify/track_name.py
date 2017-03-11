import re
import urllib
import spotipy


def get_track_from_message(message):
    """
    Return spotify id of possible track in message.
    """
    sp = spotipy.Spotify()
    # look for string containing track and an id
    if "spotify.com" in message:
        pattern = re.search("track/(\w+)\W*",message)
        if pattern:
            res=pattern.group(1)
            if sp.tracks([res])['tracks']!=[None]:
                return res
                
    # look for track with artist name or song name
    results = sp.search(q='track:' + message, type='track')
    items = results['tracks']['items']
    if len(items) > 0:
        track = items[0]
        return track['id']
    return None
   

#get_track_from_message("https://open.spotify.com/truck/6qnaCx4wQQBqFd9XdQyWjC?context=spotify%3Aalbum%3A51q9Mkz5BVwTRYsMlLASVZ")
#get_track_from_message("Shakira - Hips")