import os, requests
from flask import Flask, request
app = Flask(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN","").strip()
DIFY_KEY = os.getenv("DIFY_KEY","").strip()
DIFY_URL = os.getenv("DIFY_URL","").strip()
CHANNEL = os.getenv("CHANNEL_USERNAME","").strip()

@app.route("/", methods=["GET"])
def home(): return "Live", 200

@app.route("/", methods=["POST"])
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data or "message" not in data: return "ok", 200
    chat_id = data["message"]["chat"]["id"]
    user_id = data["message"]["from"]["id"]
    text = data["message"].get("text","")
    if not text: return "ok", 200
    try:
        r = requests.post(DIFY_URL, headers={"Authorization": f"Bearer {DIFY_KEY}","Content-Type":"application/json"}, json={"inputs":{},"query":text,"user":str(user_id),"response_mode":"blocking"}, timeout=60)
        print(f"STATUS {r.status_code} BODY {r.text[:1000]}")
        if not r.text:
            raise ValueError(f"Dify رجع فاضي - Status {r.status_code} - راجع DIFY_URL و Publish")
        j = r.json()
        ans = j.get("answer") or j.get("data",{}).get("outputs",{}).get("text") or str(j)[:1000]
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":chat_id,"text":ans})
    except Exception as e:
        print(f"ERROR {e}")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":chat_id,"text":f"خطأ: {e}"})
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
