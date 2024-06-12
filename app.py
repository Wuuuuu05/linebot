from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

app = Flask(__name__)

# 設置您的Channel Secret和Channel Access Token
line_bot_api = LineBotApi('CHANNEL_ACCESS_TOKEN')
handler = WebhookHandler('CHANNEL_SECRET')

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if event.message.text == 'menu':
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text='這是圖文選單範例')
        )
        create_rich_menu()

def create_rich_menu():
    rich_menu_to_create = RichMenu(
        size=RichMenuSize(width=2500, height=1686),
        selected=False,
        name="Nice richmenu",
        chat_bar_text="Tap here",
        areas=[
            RichMenuArea(
                bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                action=MessageAction(label='Hello', text='Hello')
            ),
            RichMenuArea(
                bounds=RichMenuBounds(x=1251, y=0, width=1250, height=843),
                action=MessageAction(label='World', text='World')
            )
        ]
    )
    rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)

    with open("path_to_your_image.png", 'rb') as f:
        line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)

    line_bot_api.set_default_rich_menu(rich_menu_id)

if __name__ == "__main__":
    app.run()
