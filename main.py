import os
import requests
from flask import Flask, request

app = Flask(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DIFY_KEY = os.getenv("DIFY_KEY", "").strip()
DIFY_URL = os.getenv("DIFY_URL", "https://api.dify.ai/v1/chat-messages").strip()
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "").strip()

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

@app.route("/", methods=["GET"])
def home():
    return "Bot is Live", 200

@app.route("/", methods=["POST"])
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return "ok", 200
    if "message" not in data:
        return "ok", 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = message.get("text", "")

    if not text:
        return "ok", 200

    if CHANNEL_USERNAME:
        try:
            check_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
            check_res = requests.get(check_url, params={"chat_id": CHANNEL_USERNAME, "user_id": user_id}, timeout=10).json()
            status = check_res.get("result", {}).get("status", "")
            if status in ["left", "kicked"]:
                send_message(chat_id, f"عشان تستخدم البوت لازم تشترك أول في القناة: {CHANNEL_USERNAME}")
                return "ok", 200
        except Exception as e:
            print(f"Channel check error: {e}")

    try:
        headers = {
            "Authorization": f"Bearer {DIFY_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": {},
            "query": text,
            "user": str(user_id),
            "response_mode": "blocking"
        }
        r = requests.post(DIFY_URL, headers=headers, json=payload, timeout=60)

        if r.status_code == 200:
            answer = r.json().get("answer", "ما وصلني رد من المعلم")
        else:
            print(f"Dify Error {r.status_code}: {r.text}")
            answer = f"خطأ من Dify: {r.status_code}\n{r.text[:500]}"

        send_message(chat_id, answer)

    except Exception as e:
        print(f"Main error: {e}")
        send_message(chat_id, f"حصل خطأ داخلي: {e}")

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
