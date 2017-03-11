# interaction with MongoDB



# Dummy methods - to be deleted
def get_active_friends(user_id):
    friends = ["Friend 1", "Friend 2", "Friend 3"]

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


def invite_friend(user_id, active_poll, friend):
    if friend not in get_active_friends(user_id):
        return "That's an imaginary friend?"
    return None
