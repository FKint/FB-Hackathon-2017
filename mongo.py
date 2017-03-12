from pymongo import MongoClient
import os
import datetime
import json
# use the below in Heroku with relevant user, pass and mongoprovider
# heroku create
# heroku config:set MONGODB_URI=mongodb://user:pass@mongoprovider.com:27409/rest

# create signatures for the methods for getting data
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
        "songs": [{"artist": "ad", "name": "a2", "uri": "fg@sf", "score":0},
                  {"artist": "ad2", "name": "a22", "uri": "fg@s2f", "score":0}}]
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
        MONGODB_URI = "mongodb://heroku_f0s5338v:kurrih7o6a72idgjr2bf3c7g6d@ds129030.mlab.com:29030/heroku_f0s5338v"
        # MONGODB_URI = "mongodb://user:pass@mongoprovider.com:27409/rest"
        client = MongoClient(MONGODB_URI)
        self.db = client['polls'] # this gives the database
        self.polls = self.db.polls # this gives the collection of polls (+creates it)
        self.selected_polls = self.db.selected_polls
        # in the worst case just hardcode the app user ids here
        self.app_users = self.db.users
        self.app_users = []
        self.friends = self.db.friends
        self.names = self.db.names

    def create_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)"""
        if self.polls.find_one({"poll_name": poll_name}):
            return "Error - the poll name is already used."
        poll = {"poll_name": poll_name,
                "admin_id": user_id,
                "participants": [],
                "songs": []
               }
        self.polls.insert_one(post)

    def is_admin_of_poll(self, user_id, poll_name):
        """Returns either True or False based on if the user with given
        user_id is an admin of the poll_name
        """
        poll_doc = self.polls.find_one({"poll_name": poll_name})
        if poll_doc:
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
        if not self.polls.find_one({"poll_name": poll_name}):
            return "Error - the poll does not exist."
        sel_pol_doc = self.selected_polls.find_one({"user_id": user_id})
        # if the user already has something selected, change the poll name
        if sel_pol_doc:
            sel_pol_doc["poll_name"] = poll_name
        else:
            self.selected_polls.insert_one({"user_id": user_id,
                                            "selected_poll": poll_name})

    def get_selected_poll(self, user_id):
        """(returns None or the name of the selected poll for that user)"""
        sel_pol_doc = self.selected_polls.find_one({"user_id": user_id})
        if sel_pol_doc:
            return sel_pol_doc["selected_poll"]

    def get_polls_for_user(self, sender_id):
        """returning a list of strings (the poll names where this user is
         active in, both as admin and as participant)
        """
        poll_names = set([])
        for poll in self.polls.find({"admin_id": sender_id}):
            poll_names.add(poll["poll_name"])

        for poll in self.polls.find():
            if sender_id in poll["participants"]:
                poll_names.add(poll["poll_name"])
        return list(poll_names)

        # get all the polls where the user is admin

    def invite_friend(self, user_id, poll_name, friend_name):
        """returning an error message if user_id is not the admin of poll_name,
        friend is not an active user of our application our friend
        is not a FB friend of user_id
        friend is given as a name --> convert it to id
        using database
        """
        friend = self.names.find_one({"name": friend_name})["user_id"]
        if self.selected_polls.find_one({"poll_name": poll_name, "admin_id": user_id}):
            if friend in self.app_users:
                if friend in self.friends.find_one({"user_id": user_id})["friends"]:
                    # update the field of participants for the poll
                    participants = self.polls.find_one({"poll_name": poll_name})["participants"]
                    participants.append(friend)
                    # now update the list of participants in the collection of polls for the given poll
                    self.polls.update_one({"poll_name": poll_name}, {'$set': {'participants': participants}})
        return "Error - not admin, not user or not friend."

    def get_ranking(self, user_id, poll):
        """ returning a list of dicts, each representing one song:
        {artist: <str>, uri: <str>, name: <str>} sorted by descending popularity.
        Can return a string with the error message if the user is not a participant
        of the poll or the poll does not exist.
        """
        ranking = []
        poll = self.polls.find_one({"poll_name": poll, "admin_id": user_id})
        if not poll:
            return "Error - either poll or user_id does not exist."
        songs = sorted(poll["songs"], key=lambda x: x["score"], reverse=True)
        answ = []
        for song in songs:
            answ.append({"artist": song["artist"], "uri": song["uri"], "name": song["name"]})

    def get_active_friends(self, person_id):
        """This method returns the friends using the application
        of a given person. We store all friends of a person on Facebook.
        We need an intersection of the friends of person_id and app_users.
        """
        active_friends = []
        app_users_set = set(app_users)
        friends = self.friends.find_one({"user_id": person_id})["friends"]
        for friend in friends:
            if friend in self.app_users_set:
                active_friends.append(friend)
        return active_friends

    def suggest_song(self, user_id, poll, song_id):
        """adds the song to poll as a suggestion from user user_id. Returns
           None on success or a string with an
           error message when something goes wrong.
        """
        {
        "poll_name": poll_name,
        "admin_id" admin_id,
        "participants": [user_id_1, user_id_2, user_id_3, user_id_4]
        "songs": [{"artist": "ad", "name": "a2", "uri": "fg@sf", "score":0},
                  {"artist": "ad2", "name": "a22", "uri": "fg@s2f", "score":0}}]
        }
        poll = self.polls.find_one({"poll_name": poll, "admin_id": user_id})
        return None

    def get_poll_participants(self, user_id, poll):
        """returns a list of
           {user_id: <string>, display_name: <string>} values
            (similar to get_active_friends) representing all users participating
             in the poll
           (only returned when user_id is a member of that poll as well). Returns
           the list upon success or <string> when an error occurred.
        """
        participants = self.polls.find_one({"poll_name": poll})["participants"]
        if user_id in participants:
            people_list = []
            for e in  participants:
                people_list.append({"user_id": e, "display_name": self.names.find_one({"user_id": e})["name"]})
            return people_list
        return "Error - poll does not exist or the user is not a member of poll."
