class Edi(object):
    def __init__(self):
        pass

    def handle_message(self, message_text):
        answer = "I don't know"
        print message_text
        if "hello" in message_text.lower():
            answer = "Hello to you too."
            return answer
        return answer
