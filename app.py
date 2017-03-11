import json
import os
import sys

import requests
from flask import Flask, request, render_template

import chatbot

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

    return render_template('pig.html'), 200


@app.route('/', methods=['POST'])
def webhook():
    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = None
                    try:
                        message_text = messaging_event["message"]["text"]  # the message's text
                    except:
                        message_text = "hello"

                    answer = edi.handle_message(message_text)

                    send_message(sender_id, answer)

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


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


def log(message):  # simple wrapper for logging to stdout on heroku
    print
    str(message)
    sys.stdout.flush()


###########################
# web interface starts here
@app.route('/pig')
def signUp():
    return render_template('pig.html')


@app.route('/ajaxcalc', methods=['POST', 'GET'])
def ajaxcalc():
    if request.method == 'POST':
        print
        "hello"
        # pig1 and pig2 are sent from the ajax script
        input1 = request.form['pig1']
        # print input1
        # input2=int(request.form['pig2'])
        result = edi.handle_message(input1)
        return json.dumps({"result": result})
    else:
        return "error"


if __name__ == '__main__':
    app.run(debug=True)