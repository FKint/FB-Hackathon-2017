import json
import os

import requests

from logs import log


def send_message(recipient_id, message_text):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


class Edi(object):
    def __init__(self):
        pass

    def handle_message(self, sender_id, message_text):
        action = self.get_action(message_text)
        if action == Edi.ACTION_INTRODUCE_BOT:
            answer = self.introduce_bot(sender_id, message_text)
        elif action == Edi.ACTION_CREATE_POLL:
            answer = self.create_poll(sender_id, message_text)
        # TODO: add other cases

        else:
            answer = "I don't know what you mean"
        return answer

    ACTION_INTRODUCE_BOT = "ACTION_INTRODUCE_BOT"
    ACTION_SHOW_ACTIVE_FRIENDS = "ACTION_SHOW_ACTIVE_FRIENDS"
    ACTION_CREATE_POLL = "ACTION_CREATE_POLL"
    ACTION_SHOW_POLL = "ACTION_SHOW_POLL"
    ACTION_SHOW_POLLS_LIST = "ACTION_SHOW_POLLS_LIST"
    ACTION_SELECT_POLL = "ACTION_SELECT_POLL"
    ACTION_INVITE_FRIEND = "ACTION_INVITE_FRIEND"
    ACTION_SUGGEST_SONG = "ACTION_SUGGEST_SONG"
    ACTION_SHOW_RANKING = "ACTION_SHOW_RANKING"
    ACTION_SHOW_SONG_OPTION = "ACTION_SHOW_SONG_OPTION"
    ACTION_VOTE_SONG_OPTION = "ACTION_VOTE_SONG_OPTION"

    def get_action(self, message_text):
        """
        Return any of the above actions.
        :param message_text:
        :return:
        """
        message_text = message_text.lower()
        prefix_actions = {
            "help": Edi.ACTION_INTRODUCE_BOT,
            "info": Edi.ACTION_INTRODUCE_BOT,
            "hello": Edi.ACTION_INTRODUCE_BOT,
            "create poll": Edi.ACTION_CREATE_POLL
        }
        for prefix in prefix_actions:
            if message_text.startswith(prefix):
                return prefix_actions[prefix]

        return None

    def introduce_bot(self, sender_id, message_text):
        # How to create a poll, list of all polls, show friends
        send_message(sender_id, "Hello, I'm Edi. I will help you vote on playlists with your friends using our polls.")
        send_message(sender_id,
                     "Send me 'create poll roadtrip' to create a new playlist called 'roadtrip'.")
        send_message(sender_id, "Send me 'show all polls' to see a list of all current polls.")
        send_message(sender_id, "Send me 'show friends' to get a list of all your friends that use me.")

    def show_active_friends(self, sender_id, message_text):
        # List of all Messenger contacts that can be invited
        pass

    def create_poll(self, sender_id, message_text):
        # Create + confirm
        poll_name = message_text.split()[-1]
        # How to add songs, how to invite friends, how to see ranking
        # Select this poll + notify
        pass

    def show_poll(self, sender_id, message_text):
        # Which is the currently active poll, how to switch polls, how to see all polls
        pass

    def select_poll(self, sender_id, message_text):
        # <poll> selected
        # How to invite friends (if admin)
        # How to suggest songs
        # How to vote for songs
        # How to see the ranking
        pass

    def invite_friend(self, sender_id, message_text):
        # Confirm that <friend> has been added to <poll>
        pass

    def suggest_song(self, sender_id, message_text):
        # Confirm that <song> has been added to <poll>
        # Show picture of the song
        pass

    def show_ranking(self, sender_id, message_text):
        # Show top 10 songs
        # Later: paginator: next 10
        pass

    def show_song_option(self, sender_id, message_text):
        # Retrieve random song that user needs to vote for
        # Present with 0, 1 or cancel button.
        # No song available: suggest a song?
        pass

    def vote_song_option(self, sender_id, message_text):
        # Apply vote
        # Confirm vote
        pass
