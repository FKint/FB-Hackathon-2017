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

"""
What we will store:
1) Friends of a person for each person on Facebook. We will map them by their
user_id. Example:
We will have a collection of the following for each user of FB:

{
user_id: 123,
name: "name1",
friend_ids: [12, 23, 44, 35, 34]
}

2) People using the application

3) Collection of the polls:
{
poll_name: "poll1",
admin_id: 123
}

--> when creating a poll, return error if there is a poll with some given name

"""
class Poll:
    def __init__(self):
        """Collection of polls will look like this:
        {
        "poll_name": poll_name,
        "admin_id" admin_id,
        "participants": [user_id_1, user_id_2, user_id_3, user_id_4]
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

    def create_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)"""
        if self.polls.find_one({"poll_name": poll_name}):
            return "Error - the poll name is already used."
        poll = {"poll_name": poll_name,
                "admin_id": user_id,
                "participants": set([])
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

    def invite_friend(self, user_id, poll_name, friend):
        """returning an error message if user_id is not the admin of poll_name,
        friend is not an active user of our application our friend
        is not a FB friend of user_id
        friend is given as an id number
        """
        if self.selected_polls.find_one({"poll_name": poll_name,
                                         "admin_id": user_id}):
            if friend in self.app_users:
                if friend in self.friends.find_one({"user_id": user_id})["friends"]:
                    # update the field of participants for the poll
                    participants = self.polls.find_one({"poll_name": poll_name})["participants"]
                    participants.append(friend)
                    # now update the list of participants in the collection of polls for the given poll
                    self.polls.update_one({"poll_name": poll_name}, {'$set': {'participants': participants}})
        return "Error - not admin, not user or not friend."

    def get_ranking(user_id, poll):
    """ returning a list of dicts, each representing one song:
    {artist: <str>, url: <str>, name: <str>} sorted by descending popularity.
    Can return a string with the error message if the user is not a participant
    of the poll or the poll does not exist.
    """

def get_active_friends(person_id):
    """This method returns the friends using the application
    of a given person. We store all friends of a person on Facebook.
    We need an intersection of the

    Collection of

    {person_id: 123,
     name: "name1",
     friend_ids: [1234, 1235, 1236]
    }
    """
    for
    return json.dumps(friends)

"""

"""
def get_most_popular_songs():

    return None


def initialize():
    MONGODB_URI = os.environ.get('MONGO_URL')
    if not MONGODB_URI:
        MONGODB_URI = "mongodb://localhost:27017/rest";

    #  MONGO_URL=mongodb://user:pass@mongoprovider.com:27409/rest

    client = MongoClient(MONGODB_URI) # this should direct to Heroku
    db = client['songs-database'] # the database with that name should be created in Heroku
    # or use db = client.get_default_database()
    # collection = db['songs-collection']

    # if we get a new vote from some user
    # it should be in json format

    post = {song: "abc1",
            user: "user1",
            vote: 1,
            last_session: datetime.datetime.now()}

    posts = db.posts

    posts.insert_one(post)

# posts.find_one() # for finding a post
