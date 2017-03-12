import os

from flask import Flask, request

import chatbot
import model
from logs import log

app = Flask(__name__)
edi = chatbot.Edi()


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "not ok", 404


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log("RECEIVED DATA: ")
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                recipient_id = messaging_event["recipient"][
                    "id"]  # the recipient's ID, which should be your page's facebook ID
                model.register_user(sender_id)
                if messaging_event.get("message"):  # someone sent us a message

                    message_text = None
                    try:
                        message_text = messaging_event["message"]["text"]  # the message's text
                    except:
                        message_text = "hello"

                    edi.handle_message(sender_id, message_text)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    postback = messaging_event["postback"]
                    edi.handle_postback(sender_id, postback)

    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
