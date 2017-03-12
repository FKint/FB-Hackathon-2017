# interaction with MongoDB
import mongo

data_model = mongo.Model()


def register_user(user_id):
    data_model.register_user(user_id)


# Dummy methods - to be deleted
def get_active_friends(user_id):
    friends = [
        {"user_id": "f1", "display_name": "Friend 1"},
        {"user_id": "f2", "display_name": "Friend 2"},
        {"user_id": "f3", "display_name": "Friend 3"},
    ]

    return friends


def select_poll(user_id, poll_name):
    return data_model.select_poll(user_id, poll_name)


def create_poll(user_id, poll_name):
    return data_model.create_poll(user_id, poll_name)


def is_admin_of_poll(user_id, poll_name):
    return data_model.is_admin_of_poll(user_id, poll_name)


def get_selected_poll(user_id):
    return data_model.get_selected_poll(user_id)


def get_polls_for_user(user_id):
    return data_model.get_polls_for_user(user_id)


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


def get_poll_participants(user_id, poll_id):
    return data_model.get_poll_participants(user_id, poll_id)


def suggest_song(user_id, poll, song_id):
    return None

user_state = dict()

def set_user_state(poll, user, state):
    if poll not in user_state:
        user_state[poll] = dict()
        
    user_state[poll][user] = state
   
def get_user_state(poll, user):
    return user_state[poll][user]

