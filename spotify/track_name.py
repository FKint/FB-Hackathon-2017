import re
import urllib
import spotipy


def get_track_from_message(message):
    if "spotify.com" in message:
        pattern = re.search("track/(\w+)\W*",message)
        if pattern:
            sp = spotipy.Spotify()
            res=pattern.group(1)
            if sp.tracks([res])['tracks']!=[None]:
                return res
    return None
   

#get_track_from_message("https://open.spotify.com/truck/6qnaCx4wQQBqFd9XdQyWjC?context=spotify%3Aalbum%3A51q9Mkz5BVwTRYsMlLASVZ")
