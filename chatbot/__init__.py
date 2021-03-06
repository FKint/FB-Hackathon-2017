import json
import os

import requests

import model
import spotify.track_name
import spotify.user_playlist
from logs import log


def send_message(recipient_id, message_text, buttons=None):
    log("SENDING DATA to {recipient}:".format(recipient=recipient_id))

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
                    "text": message_text,
                    "buttons": buttons,
                }
            }
        }

    data = json.dumps(data)

    log(data)

    r = requests.post("https://graph.facebook.com/v2.8/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log("ERROR SENDING TO FB!")
        log(r.status_code)
        log(r.text)


class Edi(object):
    def __init__(self):
        pass

    def write_no_poll_selected(self, sender_id):
        send_message(
            sender_id,
            "You haven't selected a poll. Try 'show all polls' and 'select poll <poll>' to select a poll.",
            buttons=[self.get_polls_list_button(sender_id)] + list(self.get_poll_select_buttons(sender_id))
        )

    def handle_message(self, sender_id, message_text):
        log("PROCESSING MESSAGE FROM {}".format(sender_id))
        log(message_text)
        action = self.get_action(message_text)
        log("ACTION: {}".format(action))
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
        elif action == Edi.ACTION_SHOW_POLL_PARTICIPANTS:
            self.show_poll_participants(sender_id, message_text)
        elif action == Edi.ACTION_SUGGEST_SONG:
            self.suggest_song(sender_id, message_text)
        elif action == Edi.ACTION_EXPORT_LIST:
            self.export_list(sender_id, message_text)
        # TODO: add other cases
        elif spotify.track_name.check_track_with_url(message_text) is not None:
            log("Recognizes spotify URL")
            self.suggest_song(sender_id, message_text)
        else:
            send_message(sender_id, "I don't know what you mean. Send me 'help' if you want some help.")

    def handle_postback(self, sender_id, postback):
        payload = postback["payload"]
        payload = json.loads(payload)

        action = payload["action"]

        if action == "voting":

            poll_id = payload["poll_id"]
            song_id = payload["song_id"]
            score = payload["score"]
            model.set_user_state(poll_id, sender_id, "voted")
            if score != 0 and score != 1:
                send_message(sender_id, "I am sorry, please click a button")
            else:
                error = model.update_user_vote(sender_id, poll_id, song_id, score)

                if error is None:
                    send_message(sender_id, "Thanks, your vote has been recorded!",
                                 buttons=[self.get_ranking_button(sender_id, poll_id)])
                else:
                    send_message(sender_id, "I am sorry, there was an error: " + error)
        elif action == "confirming":

            poll_id = payload["poll_id"]
            song_id = payload["song_id"]
            score = payload["score"]
            if score == 1:
                self.suggest_song(sender_id, spotify.track_name.id_to_url(song_id), confirmed=True)
        elif action == Edi.ACTION_SHOW_ACTIVE_FRIENDS:
            self.show_active_friends(sender_id, "")
        elif action == Edi.ACTION_SHOW_POLLS_LIST:
            self.show_polls_list(sender_id, "")
        elif action == Edi.ACTION_SHOW_POLL_PARTICIPANTS:
            self.show_poll_participants(sender_id, "")
        elif action == Edi.ACTION_SHOW_RANKING:
            self.show_ranking(sender_id, "")
        elif action == Edi.ACTION_INVITE_FRIEND:
            user_id = payload["user_name"] if "user_name" in payload else ""
            self.invite_friend(sender_id, "invite {}".format(user_id))
        elif action == Edi.ACTION_SELECT_POLL:
            poll_name = payload["poll_name"]
            self.select_poll(sender_id, "select poll {}".format(poll_name))
        elif action == Edi.ACTION_SHOW_POLL:
            self.show_poll(sender_id, "")
        elif action == Edi.ACTION_SHOW_SONG_OPTION:
            self.show_song_option(sender_id, "")
        else:
            send_message(sender_id, "Undefined action")

    ACTION_INTRODUCE_BOT = "ACTION_INTRODUCE_BOT"
    ACTION_SHOW_ACTIVE_FRIENDS = "ACTION_SHOW_ACTIVE_FRIENDS"
    ACTION_CREATE_POLL = "ACTION_CREATE_POLL"
    ACTION_SHOW_POLL = "ACTION_SHOW_POLL"
    ACTION_SHOW_POLLS_LIST = "ACTION_SHOW_POLLS_LIST"
    ACTION_SHOW_POLL_PARTICIPANTS = "SHOW_POLL_PARTICIPANTS"
    ACTION_SELECT_POLL = "ACTION_SELECT_POLL"
    ACTION_INVITE_FRIEND = "ACTION_INVITE_FRIEND"
    ACTION_SUGGEST_SONG = "ACTION_SUGGEST_SONG"
    ACTION_SHOW_RANKING = "ACTION_SHOW_RANKING"
    ACTION_SHOW_SONG_OPTION = "ACTION_SHOW_SONG_OPTION"
    ACTION_VOTE_SONG_OPTION = "ACTION_VOTE_SONG_OPTION"
    ACTION_EXPORT_LIST = "ACTION_EXPORT_LIST"

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
        "show ranking": ACTION_SHOW_RANKING,
        "show participants": ACTION_SHOW_POLL_PARTICIPANTS,
        "suggest": ACTION_SUGGEST_SONG,
        "export": ACTION_EXPORT_LIST
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

    def get_polls_list_button(self, user_id):
        return {
            "type": "postback",
            "title": "Show all polls",
            "payload": json.dumps({
                "action": Edi.ACTION_SHOW_POLLS_LIST
            })
        }

    def introduce_bot(self, sender_id, message_text):
        # How to create a poll, list of all polls, show friends
        send_message(sender_id, "Hello, I'm Edi. I will help you vote on playlists with your friends using our polls.")
        send_message(sender_id,
                     "Send me 'create poll roadtrip' to create a new playlist called 'roadtrip'.")
        send_message(sender_id, "Send me 'show all polls' to see a list of all current polls. "
                                "Send me 'show active friends' to get a list of all your friends that use me.",
                     buttons=[self.get_polls_list_button(sender_id),
                              {
                                  "type": "postback",
                                  "title": "Show active friends",
                                  "payload": json.dumps({
                                      "action": Edi.ACTION_SHOW_ACTIVE_FRIENDS
                                  })
                              }])

    def show_active_friends(self, sender_id, message_text):
        # List of all Messenger contacts that can be invited
        activeFriends = model.get_active_friends(sender_id)

        messageContent = "The friends that can be invited are:\n"
        for friend in activeFriends:
            messageContent += friend['display_name'] + "\n"

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
            "I selected poll {} for you. {}".format(
                poll_name,
                "You're the ADMIN! " if model.is_admin_of_poll(sender_id, poll_name) else ""
            )
        )
        self.send_poll_help(sender_id, poll_name)

    def get_friend_invite_buttons(self, user_id, poll_name):
        all_friends = model.get_active_friends(user_id)
        friend_ids = set([x['user_id'] for x in all_friends]) - set(
            [x['user_id'] for x in model.get_poll_participants(user_id, poll_name)])

        return [
                   {
                       "type": "postback",
                       "title": "Invite {}".format(friend['display_name']),
                       "payload": json.dumps({
                           "user_name": friend['display_name'],
                           "score": 1,
                           "action": Edi.ACTION_INVITE_FRIEND
                       })
                   } for friend in all_friends if friend['user_id'] in friend_ids
                   ][:3]

    def get_ranking_button(self, user_id, poll_name):
        return {
            "type": "postback",
            "title": "Show ranking",
            "payload": json.dumps({
                "action": Edi.ACTION_SHOW_RANKING
            })
        }

    def send_poll_help(self, sender_id, poll_name):
        if model.is_admin_of_poll(sender_id, poll_name):
            log(model.get_active_friends(sender_id))
            log(model.get_poll_participants(sender_id, poll_name))

            send_message(
                sender_id,
                "You can invite friends to this poll by sending me 'invite <friend_name>'. "
                "Note that you can only invite friends which have talked to me before.",
                buttons=self.get_friend_invite_buttons(sender_id, poll_name)
            )
        send_message(
            sender_id,
            "You can show all participants in this poll by sending me 'show participants'. "
            "You can ask me to send a song that you can vote for by sending 'show song'. "
            "You can see the ranking by sending me 'show ranking'.",
            buttons=[
                {
                    "type": "postback",
                    "title": "Show participants",
                    "payload": json.dumps({
                        "action": Edi.ACTION_SHOW_POLL_PARTICIPANTS
                    })
                }, self.get_show_song_button(), self.get_ranking_button(sender_id, poll_name=poll_name),
            ]
        )
        send_message(
            sender_id,
            "You can suggest a new song for this poll by sending me 'suggest <song>', where "
            "song can be a Spotify song ID, URI or a search string."
        )

    def get_show_song_button(self):
        return {
            "type": "postback",
            "title": "Show song",
            "payload": json.dumps({
                "action": Edi.ACTION_SHOW_SONG_OPTION
            })
        }

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
            "You can see all polls by sending me 'show all polls'. "
            "You can select another poll by sending me 'select poll <poll>', where <poll> is the name of the poll. "
            "You can ask to vote for songs by sending 'show song'.",
            buttons=[
                        {
                            "type": "postback",
                            "title": "Show all polls",
                            "payload": json.dumps({
                                "action": Edi.ACTION_SHOW_POLLS_LIST
                            })
                        }] + self.get_poll_select_buttons(sender_id, exception=poll_name) + [
                        self.get_show_song_button()
                    ]
        )

    def get_poll_select_buttons(self, user_id, exception=None):
        return [{
                    "type": "postback",
                    "title": "Select poll {}".format(x),
                    "payload": json.dumps({
                        "action": Edi.ACTION_SELECT_POLL,
                        "poll_name": x
                    })
                } for x in model.get_polls_for_user(user_id) if exception != x][:3]

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
            "You can select another poll by sending me 'select poll <poll>', where <poll> is the name of the poll.\n"
            "If you send me 'create poll <poll>', I'll make you admin of one!",
            buttons=self.get_poll_select_buttons(sender_id)
        )

    def select_poll(self, sender_id, message_text):
        # <poll> selected
        parts = message_text.split()
        if len(parts) != 3:
            send_message(
                sender_id,
                "If you want me to select you a new poll, please send the following command: 'select poll <name>'"
                "where name should be a string without whitespace.",
                buttons=self.get_poll_select_buttons(sender_id))
            return

        poll_name = parts[-1]

        if model.select_poll(sender_id, poll_name) is None:
            send_message(sender_id,
                         "Poll successfully selected. If you send me 'show song', "
                         "I'll offer you a random song that you stil need to vote for! \n"
                         "You can suggest new songs with 'suggest <query>' or by sending a Spotify URL. \n"
                         "Send 'show ranking' to see the current standings.",
                         buttons=[
                             self.get_show_song_button(),
                             self.get_ranking_button(sender_id, poll_name)
                         ])
        else:
            send_message(sender_id, "Error occurred when trying to select the poll")

    def invite_friend(self, sender_id, message_text):
        # Confirm that <friend> has been added to <poll>
        active_poll = model.get_selected_poll(sender_id)
        if active_poll is None:
            self.write_no_poll_selected(sender_id)
            return
        parts = message_text.split()
        if len(parts) < 2:
            send_message(
                sender_id,
                "Please add your friend's name: 'invite <friend>'.",
                buttons=self.get_friend_invite_buttons(sender_id, active_poll)
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
            log(error)
            send_message(
                sender_id,
                "I couldn't add your friend, please check it's not an imaginary friend of yours ;)"
            )
            return
        send_message(
            sender_id,
            "I added your friend to the poll!"
        )

    def suggest_song(self, sender_id, message_text, confirmed=False):
        # Confirm that <song> has been added to <poll>
        # Show picture of the song
        if message_text.startswith("suggest "):
            message_text = message_text[len("suggest "):]

        poll = model.get_selected_poll(sender_id)
        if poll is None:
            self.write_no_poll_selected(sender_id)
            return
        # TODO: also check other forms of queries
        song_id = spotify.track_name.check_track_with_url_or_id(message_text)
        if song_id is None:
            # Try to find it based on keywords
            song_id = spotify.track_name.check_track_with_keywords(message_text)
            if song_id is None:
                send_message(
                    sender_id,
                    "I don't know that song, I haven't heard that name in Donkey's years! "
                    "Maybe try giving me its Spotify ID?"
                )
                return
            if not confirmed:
                artist, title, uri = spotify.track_name.get_metadata(song_id)
                log(title)
                log(artist)
                message = "Is {} by {} the suggestion you want to make?".format(title, artist)
                buttons = [
                    {
                        "type": "postback",
                        "title": "Yes",
                        "payload": json.dumps({
                            "song_id": song_id,
                            "poll_id": poll,
                            "score": 1,
                            "action": "confirming"
                        })
                    },
                    {
                        "type": "postback",
                        "title": "No",
                        "payload": json.dumps({
                            "song_id": song_id,
                            "poll_id": poll,
                            "score": 0,
                            "action": "confirming"
                        })
                    },
                ]

                send_message(
                    sender_id,
                    message,
                    buttons
                )
                return

        result = model.suggest_song(sender_id, poll, song_id)
        if result is not None:
            log(result)
            if "Song already in the poll" in result:
                send_message(
                    sender_id,
                    "Someone else has already suggested this song. Be creative!"
                )
                return
            else:
                send_message(
                    sender_id,
                    "I'm sorry, but I can't let you suggest that song. "
                    "Either something went wrong or it is just not my style :/"
                )
                return
        send_message(
            sender_id,
            "I suggested this song and I'll let the other participants in this poll know they can vote for it!"
        )
        # TODO: notify other participants
        poll_participants = model.get_poll_participants(sender_id, poll)
        if isinstance(poll_participants, list):
            for participant in poll_participants:
                if sender_id == participant['user_id']:
                    continue
                if model.get_user_state(poll, participant["user_id"]) is not "waiting":
                    if model.get_selected_poll(participant['user_id']) != poll:
                        send_message(
                            participant['user_id'],
                            "A new song has been added to poll {}. Use 'select poll {}' to vote for songs in that poll!"
                                .format(poll, poll),
                            buttons={
                                "type": "postback",
                                "title": "Select poll {}".format(poll),
                                "payload": json.dumps({
                                    "action": Edi.ACTION_SELECT_POLL,
                                    "poll_name": poll
                                })
                            }
                        )
                    else:
                        send_message(
                            participant['user_id'],
                            "A new song has been added to poll {}. Use 'show song' to get songs for which you can vote!"
                                .format(poll),
                            buttons=self.get_poll_select_buttons(sender_id, poll)[:2] + [
                                self.get_show_song_button()
                            ]
                        )
                        model.set_user_state(poll, participant["user_id"], "waiting")
        else:
            log(poll_participants)
            send_message(
                sender_id,
                "An error happened, sorry :/"
            )

    def show_ranking(self, sender_id, message_text):
        # Show top 10 songs
        # Later: paginator: next 10
        active_poll = model.get_selected_poll(sender_id)
        if active_poll is None:
            self.write_no_poll_selected(sender_id)
            return
        ranking = model.get_ranking(sender_id, active_poll)
        send_message(sender_id, "The current favourite songs are: ")
        index = 0
        for song in ranking:
            index += 1
            send_message(sender_id,
                         "Nb. {}: {} ({}) with {} votes".format(index, song['artist'] + " - " + song['title'],
                                                                spotify.track_name.id_to_url(song['song_id']),
                                                                song['score']))

    def show_song_option(self, sender_id, message_text):
        # Retrieve random song that user needs to vote for
        # Present with 0, 1 or cancel button.
        # No song available: suggest a song
        poll_id = model.get_selected_poll(sender_id)
        if poll_id is None:
            self.write_no_poll_selected(sender_id)
            return
        song_id = model.get_song_option(sender_id, poll_id)
        if song_id is None:
            send_message(
                sender_id,
                "I'm sorry, but I don't have any songs that you can vote on. Feel free to suggest some though!"
            )
            return
        artist, title, uri = spotify.track_name.get_metadata(song_id)
        url = spotify.track_name.id_to_url(song_id)

        message = "What do you think of {} by {}? Find it here {}.".format(title, artist, url)
        buttons = [
            {
                "type": "postback",
                "title": "Like",
                "payload": json.dumps({
                    "song_id": song_id,
                    "poll_id": poll_id,
                    "score": 1,
                    "action": "voting"
                })
            }, {
                "type": "postback",
                "title": "Dislike",
                "payload": json.dumps({
                    "song_id": song_id,
                    "poll_id": poll_id,
                    "score": 0,
                    "action": "voting"
                })
            },
        ]

        send_message(
            sender_id,
            message,
            buttons
        )

    def show_poll_participants(self, sender_id, message_text):
        poll_id = model.get_selected_poll(sender_id)

        message = "The participants in poll " + (poll_id if poll_id is not None else "NONE") + " are:\n"

        participants = model.get_poll_participants(sender_id, poll_id)
        if isinstance(participants, list):
            for participant in participants:
                message += participant["display_name"] + "\n"

            send_message(sender_id, message)
        else:
            log(participants)
            send_message(sender_id,
                         "An error happened, sorry: {}".format(participants))

    def export_list(self, sender_id, message_text):
        send_message(sender_id, "Unfortunately this functionality is not ready yet!")
        return
        poll = model.get_selected_poll(sender_id)
        if poll is None:
            self.write_no_poll_selected(sender_id)
            return
        ranking = model.get_ranking(sender_id, poll)
        handler = spotify.user_playlist.PlaylistHandler()
        result = handler.add_to_playlist([x['song_id'] for x in ranking])
        if result is None:
            send_message(sender_id, "Exported the playlist to your spotify account!")
            return
        send_message(
            sender_id,
            "An error occurred when I tried to export the playlist to your Spotify account. "
            "Please try again later?"
        )

    if __name__ == "__main__":
        e = Edi()
        e.handle_message(os.environ['USER_ID'], "query")
