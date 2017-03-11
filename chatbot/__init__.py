import json
import os

import requests

import model
from logs import log


def send_message(recipient_id, message_text, buttons=None):
    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }

    if buttons is not None:
        data["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Click me",
                    "buttons": buttons,
                }
            }
        }

    data = json.dumps(data)

    print "Data is " + data

    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


class Edi(object):
    def __init__(self):
        pass

    def handle_message(self, sender_id, message_text):
        print "handle message..."
        print "sender_id = " + sender_id
        print "message_text = " + message_text

        action = self.get_action(message_text)

        print "and action = " + (action if action is not None else "")
        if action == Edi.ACTION_INTRODUCE_BOT:
            self.introduce_bot(sender_id, message_text)
        elif action == Edi.ACTION_CREATE_POLL:
            self.create_poll(sender_id, message_text)
        elif action == Edi.ACTION_SHOW_ACTIVE_FRIENDS:
            self.show_active_friends(sender_id, message_text)
        elif action == Edi.ACTION_SELECT_POLL:
            self.select_poll(sender_id, message_text)
        elif action == Edi.ACTION_SHOW_POLL:
            self.show_poll(sender_id, message_text)
        elif action == Edi.ACTION_SHOW_POLLS_LIST:
            self.show_polls_list(sender_id, message_text)
        elif action == Edi.ACTION_INVITE_FRIEND:
            self.invite_friend(sender_id, message_text)
        elif action == Edi.ACTION_SHOW_SONG_OPTION:
            self.show_song_option(sender_id, message_text)
        elif action == Edi.ACTION_SHOW_RANKING:
            self.show_ranking(sender_id, message_text)
        # TODO: add other cases

        else:
            send_message(sender_id, "I don't know what you mean. Send me 'help' if you want some help.")

    def handle_postback(self, sender_id, postback):
        payload = postback["payload"]
        payload = json.loads(payload)

        poll_id = payload["poll_id"]
        song_id = payload["song_id"]
        score = payload["score"]
        action = payload["action"]

        if action == "voting":
            if score != 0 and score != 1:
                send_message(sender_id, "I am sorry, please click a button")
            else:
                error = model.update_user_vote(user_id, poll_id, song_id, score)

                if error is None:
                    send_message(sender_id, "Thanks, your vote has been recorded!")
                else:
                    send_message(sender_id, "I am sorry, there was an error: " + error)
        else:
            send_message(sender_id, "Undefined action")

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

    PREFIX_ACTIONS = {
        "help": ACTION_INTRODUCE_BOT,
        "info": ACTION_INTRODUCE_BOT,
        "hello": ACTION_INTRODUCE_BOT,
        "create poll": ACTION_CREATE_POLL,  # Only 1 prefix allowed for now
        "show active friends": ACTION_SHOW_ACTIVE_FRIENDS,
        "select poll": ACTION_SELECT_POLL,
        "show poll": ACTION_SHOW_POLL,
        "show song": ACTION_SHOW_SONG_OPTION,
        "invite": ACTION_INVITE_FRIEND,
        "show all polls": ACTION_SHOW_POLLS_LIST,
        "show ranking": ACTION_SHOW_RANKING
    }

    def get_action(self, message_text):
        """
        Return any of the above actions.
        :param message_text:
        :return:
        """
        message_text = message_text.lower()
        # TODO: if message_text contains spotify/song identifier -> return Edi.ACTION_SUGGEST_SONG
        for prefix in Edi.PREFIX_ACTIONS:
            if message_text.startswith(prefix):
                return Edi.PREFIX_ACTIONS[prefix]
        return None

    def introduce_bot(self, sender_id, message_text):
        # How to create a poll, list of all polls, show friends
        send_message(sender_id, "Hello, I'm Edi. I will help you vote on playlists with your friends using our polls.")
        send_message(sender_id,
                     "Send me 'create poll roadtrip' to create a new playlist called 'roadtrip'.")
        send_message(sender_id, "Send me 'show all polls' to see a list of all current polls.")
        send_message(sender_id, "Send me 'show active friends' to get a list of all your friends that use me.")

    def show_active_friends(self, sender_id, message_text):
        # List of all Messenger contacts that can be invited
        activeFriends = model.get_active_friends(sender_id)

        messageContent = "The friends that can be invited are:\n"
        for friend in activeFriends:
            messageContent += friend + "\n"

        send_message(sender_id, messageContent)

    def create_poll(self, sender_id, message_text):
        # Create + confirm
        parts = message_text.split()
        if len(parts) != 3:
            send_message(
                sender_id,
                "If you want me to create a new poll, please send the following command: 'create poll <name>'"
                "where name should be a string without whitespace.")
            return
        poll_name = parts[-1]
        # How to add songs, how to invite friends, how to see ranking
        error = model.create_poll(sender_id, poll_name)
        if error is not None:
            send_message(
                sender_id,
                "I was not able to create a new poll. The error message was {}.".format(error)
            )
            return
        send_message(
            sender_id,
            "I created a new poll for you with the name '{}'.".format(poll_name)
        )
        error = model.select_poll(
            sender_id,
            poll_name
        )
        if error is not None:
            send_message(
                sender_id,
                "I wanted to select this poll for you, but I failed. I'm so sorry to disappoint you :("
            )
            return
        send_message(
            sender_id,
            "I selected poll {} for you.".format(poll_name)
        )
        self.send_poll_help(sender_id, poll_name)

    def send_poll_help(self, sender_id, poll_name):
        if model.is_admin_of_poll(sender_id, poll_name):
            send_message(
                sender_id,
                "You can invite friends to this poll by sending me 'invite <friend_name>'. "
                "Note that you can only invite friends which have talked to me before."
            )
        send_message(
            sender_id,
            "You can show all participants in this poll by sending me 'show participants'."
        )
        send_message(
            sender_id,
            "You can suggest a new song for this poll by sending me 'suggest <song>', where "
            "song can be a Spotify song ID, URI or a string of the format 'Artist - Song'."
        )
        send_message(
            sender_id,
            "You can ask me to send a song that you can vote for by sending 'show option'."
        )
        send_message(
            sender_id,
            "You can see the ranking by sending me 'show ranking'."
        )

    def show_poll(self, sender_id, message_text):
        # Which is the currently active poll, how to switch polls, how to see all polls
        poll_name = model.get_selected_poll(sender_id)
        if poll_name is None:
            send_message(
                sender_id,
                "You haven't selected a poll yet."
            )
        else:
            send_message(
                sender_id,
                "You're currently working on poll {}.".format(poll_name)
            )
        send_message(
            sender_id,
            "You can see all polls by sending me 'show all polls'."
        )
        send_message(
            sender_id,
            "You can select another poll by sending me 'select poll <poll>', where <poll> is the name of the poll."
        )

    def show_polls_list(self, sender_id, message_text):
        polls = model.get_polls_for_user(sender_id)
        if len(polls) == 0:
            send_message(
                sender_id,
                "You are not participating in any poll."
            )
        else:
            send_message(
                sender_id,
                "You are active in the following polls: {}".format(", ".join(polls))
            )
        send_message(
            sender_id,
            "You can select another poll by sending me 'select poll <poll>', where <poll> is the name of the poll."
        )

    def select_poll(self, sender_id, message_text):
        # <poll> selected
        parts = message_text.split()
        if len(parts) != 3:
            send_message(
                sender_id,
                "If you want me to select you a new poll, please send the following command: 'select poll <name>'"
                "where name should be a string without whitespace.")
            return

        poll_name = parts[-1]

        if model.select_poll(sender_id, poll_name) is None:
            send_message(sender_id, "Poll successfully selected")
        else:
            send_message(sender_id, "Error occurred when trying to select the poll")

    def invite_friend(self, sender_id, message_text):
        # Confirm that <friend> has been added to <poll>
        active_poll = model.get_selected_poll(sender_id)
        if active_poll is None:
            send_message(
                sender_id,
                "You haven't selected a poll. Try 'show all polls' and 'select poll <poll>' to select a poll."
            )
            return
        parts = message_text.split()
        if len(parts) < 2:
            send_message(
                sender_id,
                "Please add your friend's name: 'invite <friend>'."
            )
            return
        friend = " ".join(parts[1:])
        if not model.is_admin_of_poll(sender_id, active_poll):
            send_message(
                sender_id,
                "I'm sorry, but I will only add participants if the admin asks me."
            )
            return
        error = model.invite_friend(sender_id, active_poll, friend)
        if error is not None:
            send_message(
                sender_id,
                "I couldn't add your friend, please check it's not an imaginary friend of yours ;)"
            )
            return
        send_message(
            sender_id,
            "I added your friend to the poll!"
        )

    def suggest_song(self, sender_id, message_text):
        # Confirm that <song> has been added to <poll>
        # Show picture of the song
        pass

    def show_ranking(self, sender_id, message_text):
        # Show top 10 songs
        # Later: paginator: next 10
        active_poll = model.get_selected_poll(sender_id)
        if active_poll is None:
            send_message(
                sender_id,
                "You haven't selected a poll. Try 'show all polls' and 'select poll <poll>' to select a poll."
            )
            return
        ranking = model.get_ranking(sender_id, active_poll)
        send_message(sender_id, "The current favourite songs are: ")
        index = 0
        for song in ranking:
            index += 1
            send_message(sender_id, "Nb. {}: {} ({})".format(index, song['artist'] + " - " + song['name'],
                                                             song['uri']))

    def show_song_option(self, sender_id, message_text):
        # Retrieve random song that user needs to vote for
        # Present with 0, 1 or cancel button.
        # No song available: suggest a song?

        message = "Please vote for this song"
        buttons = [
            {
                "type": "postback",
                "title": "Dislike",
                "payload": json.dumps({
                    "song_id": "<REDACTED>",
                    "poll_id": "<REDACTED>",
                    "score": 0
                })
            },
            {
                "type": "postback",
                "title": "Like",
                "payload": json.dumps({
                    "song_id": "<REDACTED>",
                    "poll_id": "<REDACTED>",
                    "score": 1
                })
            }
        ]

        send_message(
            sender_id,
            message,
            buttons
        )

    def vote_song_option(self, sender_id, message_text):
        # Apply vote
        # Confirm vote
        pass


if __name__ == "__main__":
    e = Edi()
    e.handle_message(os.environ['USER_ID'], "query")
