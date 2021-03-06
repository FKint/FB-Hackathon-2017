import os
import random

from pymongo import MongoClient

import facebook
import spotify.track_name
from logs import log

"""
[new user] Introduce to users
How to make a poll
How to show friends on APP
Show POLLS this user can vote in
[friends] Show active friends on APP
[create poll <name>] Make a new POLL
Introduce how POLL works
How to invite friends to POLL
How to suggest songs (or import from Spotify)
How to see current standings
Automatically selects poll <name>
[shol all polls] Show all polls.
[show poll] Which poll is currently selected?
[select poll <name>] Select poll <name>
[invite <friend_name>] Invite friends to POLL
Send invitation to that friend
[]Accept invitation
[suggest <spotify_id>] Suggest song in POLL (id/url/name + song)
Alert about songs to be voted about
How to see which songs are available?
How to vote about a song
[show ranking] Provide ranking for most popular songs
Import songs from Spotify
[show option] Selects a random song suggested by one of the users, for which this user has not voted yet.
[button for rating] Votes
"""


class Model:
    def __init__(self):
        """Collection of polls will look like this:
        {
        "poll_name": poll_name,
        "admin_id" admin_id,
        "participants": [user_id_1, user_id_2, user_id_3, user_id_4]
        "songs": [{"artist": "ad", "name": "a2", "uri": "fg@sf"},
                  {"artist": "ad2", "name": "a22", "uri": "fg@s2f"}}],
        "participant_states": {"user12": "waiting", "user324": "waiting"}
        }

        Collection of selected polls will look like this:
        {
        "user_id": user_id,
        "selected_poll": poll_name
        }

        Collection of users of our app will be (user ids there):
        {
        "app_users": [1,2,4,5,6]
        }
        for now it will be only an array - it is better for now

        Collection of friends will be:
        {
        "user_id": user_id,
        "friends": [1,2,4,5,34]
        }

        want to choose the person by their name - so we need to assume
        that people have different names in the set so that we can assign
        them the ids.

        Collection of names and ids will be (simplification for now):
        {
        "user_id": user_id,
        "name": name
        }
        """
        MONGODB_URI = os.environ['MONGODB_URI']
        self.db = MongoClient(MONGODB_URI).heroku_6lqmlg1q
        self.polls = self.db.polls  # this gives the collection of polls (+creates it)
        self.user_data = self.db.user_data
        # in the worst case just hardcode the app user ids here
        # self.app_users = self.db.users
        # self.app_users = []
        # self.friends = self.db.friends
        # self.names = self.db.names

    def register_user(self, user_id):
        user_data = self.user_data.find_one({"user_id": user_id})
        if user_data is None:
            self.user_data.insert_one({
                "user_id": user_id,
                "name": facebook.get_user_name(user_id),
                "selected_poll_name": None,
            })

    def create_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)"""
        if self.polls.find_one({"poll_name": poll_name}):
            return "Error - the poll name is already used."
        poll = {"poll_name": poll_name,
                "admin_id": user_id,
                "participants": [user_id],
                "songs": [],
                "participant_states": {}
                }
        self.polls.insert_one(poll)

    def is_admin_of_poll(self, user_id, poll_name):
        """Returns either True or False based on if the user with given
        user_id is an admin of the poll_name
        """
        poll_doc = self.polls.find_one({"poll_name": poll_name})
        if poll_doc is not None:
            if poll_doc["admin_id"] == user_id:
                return True
            else:
                return False
        else:
            return "Error - the poll does not exist."

    def select_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)
        we can have one selected poll per user - or change it?
        """
        # check if the poll exists
        if self.polls.find_one({"poll_name": poll_name}) is None:
            return "Error - the poll does not exist."
        sel_pol_doc = self.user_data.find_one({"user_id": user_id})
        # if the user already has something selected, change the poll name
        if sel_pol_doc:
            self.user_data.update({"_id": sel_pol_doc['_id']}, {"$set": {
                "selected_poll_name": poll_name
            }})
        else:
            self.user_data.insert_one({"user_id": user_id,
                                       "selected_poll_name": poll_name})

    def get_selected_poll(self, user_id):
        """(returns None or the name of the selected poll for that user)"""
        sel_pol_doc = self.user_data.find_one({"user_id": user_id})
        if sel_pol_doc is not None:
            return sel_pol_doc["selected_poll_name"]
        return None

    def get_polls_for_user(self, user_id):
        """returning a list of strings (the poll names where this user is
         active in, both as admin and as participant)
        """
        poll_names = set([])
        for poll in self.polls.find():
            if user_id in poll["participants"]:
                poll_names.add(poll["poll_name"])
        return list(poll_names)

    def invite_friend(self, user_id, poll_name, friend_name):
        """returning an error message if user_id is not the admin of poll_name,
        friend is not an active user of our application our friend
        is not a FB friend of user_id
        friend is given as a name --> convert it to id
        using database
        """
        log("Trying to invite friend: {}".format(friend_name))
        poll = self.polls.find_one({"poll_name": poll_name, "admin_id": user_id})
        if poll is None:
            return "Error - Poll does not exist or is not owned by user."
        user = self.user_data.find_one({"user_id": user_id})
        if user is None:
            return "Error - No user record found"
        user_friends = facebook.get_user_friends(user_id)
        official_friend_name = None
        for friend_id in user_friends:
            actual_friend_name = facebook.get_user_name(friend_id)
            if friend_name in actual_friend_name:
                official_friend_name = actual_friend_name
        if official_friend_name is None:
            return "Error - No valid friend found"
        log("Found friend with name {}".format(official_friend_name))
        friend = self.user_data.find_one({"name": official_friend_name})
        if friend is None:
            return "Friend is not using the bot!"

        # update the field of participants for the poll
        self.polls.update_one({
            "poll_name": poll_name
        }, {
            "$addToSet": {
                "participants": friend['user_id']
            }
        })
        return None

    def get_ranking(self, user_id, poll):
        """ returning a list of dicts, each representing one song:
        {artist: <str>, uri: <str>, name: <str>} sorted by descending popularity.
        Can return a string with the error message if the user is not a participant
        of the poll or the poll does not exist.
        """
        ranking = []
        poll = self.polls.find_one({"poll_name": poll})
        if not poll:
            return "Error - either poll or user_id does not exist."
        # scores will be just the sums of values given by the users as scores
        songs = sorted(poll["songs"], key=lambda x: sum(x["votes"].values()), reverse=True)
        answ = []
        for song in songs:
            answ.append({"artist": song["artist"], "uri": song["uri"] if "uri" in song else "", "title": song["title"],
                         "song_id": song["song_id"], "score": sum(song["votes"].values())})
        return answ

    def get_active_friends(self, person_id):
        """This method returns the friends using the application
        of a given person. We store all friends of a person on Facebook.
        We need an intersection of the friends of person_id and app_users.
        """
        user = self.user_data.find_one({"user_id": person_id})
        facebook_friends = facebook.get_user_friends(person_id)
        active_friends = []
        for friend in facebook_friends:
            friend_data = self.user_data.find_one({"user_id": friend})
            if friend_data is not None:
                active_friends.append({"user_id": friend, "display_name": friend_data['name']})
        return active_friends

    def suggest_song(self, user_id, poll_id, song_id):
        """adds the song to poll as a suggestion from user user_id. Returns
           None on success or a string with an
           error message when something goes wrong.
        """
        poll = self.polls.find_one({"poll_name": poll_id})
        if poll is None:
            return "Error - No such poll found"
        log("Finding song {} in {}".format(song_id, poll['songs']))
        if song_id in map(lambda x: x['song_id'], poll['songs']):
            return "Error - Song already in the poll"
        artist, title, uri = spotify.track_name.get_metadata(song_id)
        self.polls.update({
            "poll_name": poll_id
        }, {
            "$push": {
                "songs": {
                    "song_id": song_id,
                    "title": title,
                    "artist": artist,
                    "uri": uri,
                    "votes": dict(),
                    "suggested_by": user_id
                }
            }
        })
        return None

    def get_poll_participants(self, user_id, poll):
        """returns a list of
           {user_id: <string>, display_name: <string>} values
            (similar to get_active_friends) representing all users participating
             in the poll
           (only returned when user_id is a member of that poll as well). Returns
           the list upon success or <string> when an error occurred.
        """
        poll = self.polls.find_one({"poll_name": poll})  # , "participants": user_id})
        if poll is None:
            return "Error - poll does not exist"
        participants = poll["participants"]
        if user_id in participants:
            people_list = []
            for e in participants:
                people_list.append({"user_id": e, "display_name": self.user_data.find_one({"user_id": e})["name"]})
            return people_list
        return "Error - user is not a member of poll."

    def set_user_state(self, poll_id, user_id, state):
        """updates the state of the user with user_id
        within the poll with poll_id to state
        """
        """-> Store whether a user has interacted since the last notification
         was sent to them (code keeping this in memory is already present
         in model/__init__.py, but this data should be stored in the
          database instead of in RAM)
        """
        poll_participant_states = self.polls.find_one({"poll_name": poll_id})["participant_states"]
        poll_participant_states[user_id] = state
        self.polls.update({
            "poll_name": poll_id
        }, {
            "$set": {
                "participant_states": poll_participant_states
            }
        })

    def get_user_state(self, poll_id, user_id):
        """returns the state of the user with user_id
        within the poll with poll_id
        default state voting
        """
        try:
            return self.polls.find_one({"poll_name": poll_id})["participant_states"][user_id]
        except:
            return "Error - either poll_id or user_id is wrong"

    def get_song_option(self, user_id, poll_id):
        """returns the ID of a song that the user still has to vote for
        in poll (or None if no such song exists).
        """
        poll = self.polls.find_one({"poll_name": poll_id})
        log("Songs for poll {}".format(poll_id))
        log(poll["songs"])
        good_song_ids = []
        for song in poll["songs"]:
            if user_id not in song['votes'] and song['suggested_by'] != user_id:
                good_song_ids.append(song["song_id"])
        if len(good_song_ids) == 0:
            return None
        ind = random.randrange(0, len(good_song_ids))
        return good_song_ids[ind]

    def update_user_vote(self, user_id, poll_id, song_id, score):
        """sets the vote for user_id in poll_id for song_id to score
         (needs to be 0 or 1, user needs to be participant of the poll,
         shouldn't have added the song themself)
         return None upon success, return error string upon failure
        """
        poll = self.polls.find_one({"poll_name": poll_id})
        # check if the user is participant in the poll
        if user_id not in poll["participants"]:
            return "Error - the user is not a participant in the poll."
        log("Finding song {} in {}".format(song_id, poll['songs']))
        for song in poll["songs"]:
            if song["song_id"] == song_id:
                # check if they have not added the song themselves
                if user_id == song["suggested_by"]:
                    return "Error - the song was added by this user."
                song["votes"][user_id] = score
                self.polls.update_one({
                    "poll_name": poll_id
                }, {"$set": {
                    "songs": poll["songs"]
                }})
                return
