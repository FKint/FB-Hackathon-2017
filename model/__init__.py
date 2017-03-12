# interaction with MongoDB



# Dummy methods - to be deleted
def get_active_friends(user_id):
    friends = [
        {"user_id": "f1", "display_name": "Friend 1"},
        {"user_id": "f2", "display_name": "Friend 2"},
        {"user_id": "f3", "display_name": "Friend 3"},
    ]

    return friends


def select_poll(user_id, poll_name):
    if poll_name != "wrong_poll":
        return None
    else:
        return "This should be an error"


def create_poll(user_id, poll_name):
    if "0" in poll_name:
        return "I don't like zeros, please don't put a zero in the name!"
    return None


def is_admin_of_poll(user_id, poll_name):
    if "anarchy" in poll_name:
        return False
    return True


def get_selected_poll(user_id):
    return "roadtrip"


def get_polls_for_user(user_id):
    return ["roadtrip", "house_party", "all_anarchy"]


def invite_friend(user_id, poll_name, friend):
    if friend not in get_active_friends(user_id):
        return "That's an imaginary friend?"
    return None


def get_ranking(user_id, poll_name):
    return [
        {"name": "Naive", "artist": "The Kooks", "uri": "spotify:track:7BHPGtpuuWWsvE7cCaMuEU"},
        {"name": "Roxanne", "artist": "The Police", "uri": "spotify:track:2NMgVh5qaPprKTEzFe3501"},
        {"name": "Like a stone", "artist": "Audioslave", "uri": "spotify:track:3YuaBvuZqcwN3CEAyyoaei"},
    ]


def update_user_vote(user_id, poll_id, song_id, score):
    if score == 1:
        return None
    else:
        return "ERROR - the score is 0"
