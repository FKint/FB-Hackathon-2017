# interaction with MongoDB
import mongo

data_model = mongo.Model()


def register_user(user_id):
    return data_model.register_user(user_id)


# Dummy methods - to be deleted
def get_active_friends(user_id):
    return data_model.get_active_friends(user_id)


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
    return data_model.invite_friend(user_id, poll_name, friend)


def get_ranking(user_id, poll_name):
    return data_model.get_ranking(user_id, poll_name)


def update_user_vote(user_id, poll_id, song_id, score):
    return data_model.update_user_vote(user_id, poll_id, song_id, score)


def get_poll_participants(user_id, poll_id):
    return data_model.get_poll_participants(user_id, poll_id)


def suggest_song(user_id, poll, song_id):
    return data_model.suggest_song(user_id, poll, song_id)


user_state = dict()


def set_user_state(poll, user, state):
    if poll not in user_state:
        user_state[poll] = dict()

    user_state[poll][user] = state


def get_user_state(poll, user):
    if poll not in user_state:
        return "voting"
    if user not in user_state[poll]:
        return "voting"
    return user_state[poll][user]


def get_song_option(user_id, poll_id):
    return data_model.get_song_option(user_id, poll_id)
