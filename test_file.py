import os

from chatbot import Edi

if __name__ == "__main__":
    e = Edi()
    query = "select poll wrong_poll"
    e.handle_message(os.environ["USER_ID"], query)
