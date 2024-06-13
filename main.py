import os
import requests
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

    body = json.dumps({
        'size': {'width': 2500, 'height': 1686},   # 設定尺寸
        'selected': 'true',                        # 預設是否顯示
        'name': 'Richmenu demo',                   # 選單名稱
        'chatBarText': 'Richmenu demo',            # 選單在 LINE 顯示的標題
        'areas':[                                  # 選單內容
            {
              'bounds': {'x': 341, 'y': 75, 'width': 560, 'height': 340}, # 選單位置與大小
              'action': {'type': 'message', 'text': '電器'}                # 點擊後傳送文字
            },
            {
              'bounds': {'x': 1434, 'y': 229, 'width': 930, 'height': 340},
              'action': {'type': 'message', 'text': '運動用品'}
            },
            {
              'bounds': {'x': 122, 'y': 641, 'width':560, 'height': 340},
              'action': {'type': 'message', 'text': '客服'}
            },
            {
              'bounds': {'x': 1012, 'y': 645, 'width': 560, 'height': 340},
              'action': {'type': 'message', 'text': '餐廳'}
            },
            {
              'bounds': {'x': 1813, 'y': 677, 'width': 560, 'height': 340},
              'action': {'type': 'message', 'text': '鞋子'}
            },
            {
              'bounds': {'x': 423, 'y': 1203, 'width': 560, 'height': 340},
              'action': {'type': 'message', 'text': '美食'}
            },
            {
              'bounds': {'x': 1581, 'y': 1133, 'width': 560, 'height': 340},
              'action': {'type': 'message', 'text': '衣服'}
            }
        ]
    })
    
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=body.encode('utf-8'))
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
    with open('line-rich-menu-demo.jpg', 'rb') as f:
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
