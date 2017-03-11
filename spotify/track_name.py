import re

import spotipy


def get_track_from_message(message):
    """
    Given a message, decided whether is a lin, song id or song name
    and returns its spotify id
    Sample usages:

    get_track_from_message("5T6KMs50XcY81tLhGKHQSB")
    get_track_from_message("https://play.spotify.com/track/5T6KMs50XcY81tLhGKHQSB")
    get_track_from_message("Shakira")
    """
    # TODO: check if extracted id matches a song
    # TODO: ignore parameters ?XX
    if "spotify.com" in message:
        return message.split("/")[-1]
    pattern = re.compile("^([A-Z0-9]*[0-9]+[A-Z0-9]*)$")
    if pattern.match(message.upper()):
        return message
    else:
        spotify = spotipy.Spotify()
        results = spotify.search(q='track:' + message, type='track')
        items = results['tracks']['items']
        if len(items) > 0:
            track = items[0]
            return track['id']
        else:
            return None
