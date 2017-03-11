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
        "admin_id" admin_id
        }
        """
        MONGODB_URI = "mongodb://heroku_f0s5338v:kurrih7o6a72idgjr2bf3c7g6d@ds129030.mlab.com:29030/heroku_f0s5338v"
        # MONGODB_URI = "mongodb://user:pass@mongoprovider.com:27409/rest"
        client = MongoClient(MONGODB_URI)
        self.db = client['polls'] # this gives the database
        self.polls = db.polls # this gives the collection of polls (creates it)

    def create_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)"""
        if self.polls.find_one({"poll_name": poll_name}):
            return "Error - the poll name is already used."
        poll = {"poll_name": poll_name,
                "admin_id": user_id
               }
        self.polls.insert_one(post)

    def is_admin_of_poll(self, user_id, poll_name):
        """Returns either True or False based on if the user with given
        user_id is an admin of the poll_name
        """
        if self.polls.find_one({"poll_name": poll_name})
        return True

    def select_poll(self, user_id, poll_name):
        """(returns an error message or None if succeeds)"""
        return None



    def get_selected_poll(self, user_id):
        """(returns None or the name of the selected poll for that user)"""
        return None

    def get_polls_for_user(self, sender_id):
        """returning a list of strings (the poll names where this user is
         active in, both as admin and as participant)
        """

def invite_friend(user_id, poll_name, friend):
    """returning an error message if user_id is not the admin of poll_name,
    friend is not an active user of our application our friend
    is not a FB friend of user_id
    """
    return None

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
