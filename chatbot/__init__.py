class Edi(object):
    def __init__(self):
        pass

    def handle_message(self, sender_id, message_text):
        action = self.get_action(message_text)

        if action == Edi.ACTION_CREATE_POLL:
            anser = self.create_poll(sender_id, message_text)
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
        return None

    def introduce_bot(self):
        # How to create a poll, list of all polls, show friends
        pass

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
