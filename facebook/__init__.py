USERS = {
    "1363580823709423": "Mihai Enache",
    "1490475977629987": "Floris Kint",
    "895885400435547": "Ramona Comanescu",
    "10207488066788000": "Ondrej Bohdal"
}


def get_user_friends(user_id):
    # TODO: query Graph API
    return [x for x in USERS.keys() if x != user_id]


def get_user_name(user_id):
    if user_id not in USERS:
        return None
    return USERS[user_id]
