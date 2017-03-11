import re
import urllib
import spotipy


def get_track_from_message(message):
    if "spotify.com" in message:
        pattern = re.search("track/(\w+)\W*",message)
        if pattern.group(1):
            sp = spotipy.Spotify()
            res=pattern.group(1)
            if sp.tracks([res])['tracks']!=[None]:
                print "yep"
                print res
            return res
    return None
   


#get_track_from_message("https://open.spotify.com/track/6qnaCx4wQQBqFd9XdQyWjC?context=spotify%3Aalbum%3A51q9Mkz5BVwTRYsMlLASVZ")
