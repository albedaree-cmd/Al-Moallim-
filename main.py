import requests
from flask import Flask, request
import os
app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL")
DIFY_KEY = os.environ.get("DIFY_KEY")
DIFY_URL = os.environ.get("DIFY_URL")
def is_joined(user_id):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember?chat_id={CHANNEL}&user_id={user_id}"
    try:
        status = requests.get(url).json()['result']['status']
        return status not in ['left', 'kicked']
    except:
        return False
@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    data = request.json
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        user_id = data['message']['from']['id']
        text = data['message'].get('text', '')
        if not is_joined(user_id):
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": f"لازم تشترك في قناتنا أول {CHANNEL} عشان تستخدم البوت 📚", "reply_markup": {"inline_keyboard": [[{"text": "اشترك هنا ✅", "url": f"https://t.me/{CHANNEL.replace('@','')}"}]]}})
            return "ok"
        res = requests.post(DIFY_URL, headers={"Authorization": f"Bearer {DIFY_KEY}"}, json={"inputs": {}, "query": text, "response_mode": "blocking", "user": str(user_id)})
        answer = res.json().get('answer', 'حصلت مشكلة')
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": answer})
    return "ok"
@app.route("/")
def home():
    return "Bot is running"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
