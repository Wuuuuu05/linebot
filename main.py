import os
import requsets
import json
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# Line bot credentials from environment variables
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))

def create_rich_menu():
    url = "https://api.line.me/v2/bot/richmenu"

    payload = json.dumps({
        "size": {
            "width": 2500,
            "height": 1686
        },
        "selected": False,
        "name": "Nice rich menu",
        "chatBarText": "Tap to open",
        "areas": [
            {
                "bounds": {
                    "x": 0,
                    "y": 0,
                    "width": 2500,
                    "height": 1686
                },
                "action": {
                    "type": "postback",
                    "data": "action=buy&itemid=123"
                }
            }
        ]
    })
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    rich_menu_id = response.json().get('richMenuId')
    if rich_menu_id:
        print(f"Rich menu created: {rich_menu_id}")
        set_rich_menu_image(rich_menu_id)
        set_default_rich_menu(rich_menu_id)
    else:
        print(f"Failed to create rich menu: {response.text}")

def set_rich_menu_image(rich_menu_id):
    url = f"https://api.line.me/v2/bot/richmenu/{rich_menu_id}/content"
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'image/png'
    }
    with open('wp12341807.jpg', 'rb') as f:
        response = requests.request("POST", url, headers=headers, data=f)
    if response.status_code == 200:
        print("Rich menu image set successfully")
    else:
        print(f"Failed to set rich menu image: {response.text}")

def set_default_rich_menu(rich_menu_id):
    url = f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}"
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    response = requests.request("POST", url, headers=headers)
    if response.status_code == 200:
        print("Default rich menu set successfully")
    else:
        print(f"Failed to set default rich menu: {response.text}")
        
if __name__ == "__main__":
    create_rich_menu()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
