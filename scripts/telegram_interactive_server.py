import os
import sys
import time
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

if sys.platform == "win32" and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "8833342791:AAGeaCdVhyw7QihwOblzQZJWPsimegbK2xU"
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID") or "714475086"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

from sniper_generator import generate_banproof_answer

# In-memory lead cache for interactive callbacks
LEAD_CACHE = {}

def send_interactive_lead_card(lead: dict, initial_mode: str = "zero_click"):
    """
    Sends an interactive Telegram card with:
    [ ✅ Approve & Auto-Post ]
    [ 🔄 Regenerate Answer ] [ ❌ Skip ]
    [ 🔗 Open Thread ]
    """
    lead_id = str(abs(hash(lead["url"])) % 1000000)
    lead["current_mode"] = initial_mode
    answer = generate_banproof_answer(lead, mode=initial_mode)
    lead["current_answer"] = answer
    LEAD_CACHE[lead_id] = lead

    strategy_desc = (
        "Zero-Click Brand Search (100% Safe)" if initial_mode == "zero_click"
        else "Educational Guide Deep-Link" if initial_mode == "educational"
        else "2-Step Conversational Request"
    )

    text = (
        f"🎯 <b>SHOPLINX AI SNIPER: GOOGLE-RANKED LEAD</b>\n\n"
        f"📍 <b>Platform:</b> {lead.get('platform')} ({lead.get('subreddit')})\n"
        f"🔥 <b>Buyer Intent:</b> {lead.get('intent_tier')} (Score: {lead.get('intent_score')}/100)\n"
        f"📌 <b>Thread:</b> {lead.get('title')}\n\n"
        f"🛡️ <b>Anti-Ban Strategy:</b> {strategy_desc}\n\n"
        f"💡 <b>READY-TO-POST ANSWER:</b>\n"
        f"<code>{answer}</code>"
    )

    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve & Auto-Post", "callback_data": f"post:{lead_id}"}
            ],
            [
                {"text": "🔄 Regenerate", "callback_data": f"regen:{lead_id}"},
                {"text": "❌ Skip", "callback_data": f"skip:{lead_id}"}
            ],
            [
                {"text": "🔗 Open Reddit Thread", "url": lead.get("url")}
            ]
        ]
    }

    res = requests.post(
        f"{API_URL}/sendMessage",
        json={
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": keyboard
        },
        timeout=10
    )
    return res.status_code == 200

def post_to_reddit(post_url: str, comment_text: str) -> tuple[bool, str]:
    """
    Uses Reddit official API (PRAW) to post comments if credentials are set.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    username = os.getenv("REDDIT_USERNAME")
    password = os.getenv("REDDIT_PASSWORD")
    user_agent = os.getenv("REDDIT_USER_AGENT", "ShopLinxGrowthBot:v1.0")

    if not all([client_id, client_secret, username, password]):
        return False, "Reddit credentials missing in .env (Add REDDIT_CLIENT_ID, USERNAME, PASSWORD)"

    try:
        import praw
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            user_agent=user_agent
        )
        submission = reddit.submission(url=post_url)
        comment = submission.reply(comment_text)
        return True, f"Comment posted live! ID: {comment.id}"
    except Exception as e:
        return False, str(e)

def handle_callback_query(callback: dict):
    cb_id = callback.get("id")
    data = callback.get("data", "")
    msg = callback.get("message", {})
    msg_id = msg.get("message_id")
    chat_id = msg.get("chat", {}).get("id")

    if ":" not in data:
        return

    action, lead_id = data.split(":", 1)
    lead = LEAD_CACHE.get(lead_id)

    if action == "skip":
        requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "❌ Lead Skipped"})
        requests.post(f"{API_URL}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": msg_id,
            "text": f"❌ <i>Lead Skipped by User ({lead.get('title', '') if lead else ''})</i>",
            "parse_mode": "HTML"
        })

    elif action == "regen":
        if not lead:
            requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "Lead expired."})
            return
        
        # Cycle modes: zero_click -> educational -> two_step -> zero_click
        modes = ["zero_click", "educational", "two_step"]
        curr = lead.get("current_mode", "zero_click")
        next_mode = modes[(modes.index(curr) + 1) % len(modes)]
        lead["current_mode"] = next_mode
        new_answer = generate_banproof_answer(lead, mode=next_mode)
        lead["current_answer"] = new_answer

        strategy_desc = (
            "Zero-Click Brand Search (100% Safe)" if next_mode == "zero_click"
            else "Educational Guide Deep-Link" if next_mode == "educational"
            else "2-Step Conversational Request"
        )

        text = (
            f"🎯 <b>SHOPLINX AI SNIPER: GOOGLE-RANKED LEAD</b>\n\n"
            f"📍 <b>Platform:</b> {lead.get('platform')} ({lead.get('subreddit')})\n"
            f"🔥 <b>Buyer Intent:</b> {lead.get('intent_tier')} (Score: {lead.get('intent_score')}/100)\n"
            f"📌 <b>Thread:</b> {lead.get('title')}\n\n"
            f"🛡️ <b>Anti-Ban Strategy:</b> {strategy_desc} [REGENERATED]\n\n"
            f"💡 <b>READY-TO-POST ANSWER:</b>\n"
            f"<code>{new_answer}</code>"
        )

        keyboard = {
            "inline_keyboard": [
                [{"text": "✅ Approve & Auto-Post", "callback_data": f"post:{lead_id}"}],
                [{"text": "🔄 Regenerate", "callback_data": f"regen:{lead_id}"}, {"text": "❌ Skip", "callback_data": f"skip:{lead_id}"}],
                [{"text": "🔗 Open Reddit Thread", "url": lead.get("url")}]
            ]
        }

        requests.post(f"{API_URL}/editMessageText", json={
            "chat_id": chat_id,
            "message_id": msg_id,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
            "reply_markup": keyboard
        })
        requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": f"Regenerated in {next_mode} mode!"})

    elif action == "post":
        if not lead:
            requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "Lead expired."})
            return

        success, msg_resp = post_to_reddit(lead.get("url"), lead.get("current_answer"))
        if success:
            requests.post(f"{API_URL}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "✅ Successfully posted to Reddit!", "show_alert": True})
            requests.post(f"{API_URL}/editMessageText", json={
                "chat_id": chat_id,
                "message_id": msg_id,
                "text": f"✅ <b>POSTED TO REDDIT!</b>\n\nThread: {lead.get('title')}\nResult: {msg_resp}",
                "parse_mode": "HTML"
            })
        else:
            requests.post(f"{API_URL}/answerCallbackQuery", json={
                "callback_query_id": cb_id,
                "text": f"⚠️ Notice: {msg_resp[:180]}",
                "show_alert": True
            })

def send_tg_message(chat_id: str, text: str):
    try:
        requests.post(
            f"{API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": True
            },
            timeout=10
        )
    except Exception as e:
        print(f"[TG ERROR] Failed to send message: {e}")

def handle_message(msg: dict):
    chat_id = msg.get("chat", {}).get("id")
    text = (msg.get("text") or "").strip().lower()
    if not text:
        return

    if text in ["/start", "/help"]:
        reply = (
            "🎯 <b>ShopLinx AI Sniper Bot 24/7 Active!</b>\n\n"
            "Commands:\n"
            "👉 <b>/status</b> - Bot health, uptime & next scheduled slots\n"
            "👉 <b>/scan</b> - Trigger an instant live Reddit/Google scan\n"
            "👉 <b>/help</b> - Show command guide\n\n"
            "⏰ Auto-schedule slots: 09:30 AM | 02:30 PM | 06:30 PM"
        )
        send_tg_message(chat_id, reply)

    elif text == "/status":
        now_str = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        reply = (
            f"🟢 <b>Bot Status: 100% ONLINE & RUNNING 24/7</b>\n\n"
            f"🕒 Current Time: {now_str}\n"
            f"⚙️ Mode: Automated Background Daemon\n"
            f"⏰ Scheduled Daily Slots: 9:30 AM | 2:30 PM | 6:30 PM\n\n"
            f"💡 <i>Tip: Send <b>/scan</b> to get fresh leads right now!</i>"
        )
        send_tg_message(chat_id, reply)

    elif text == "/scan":
        send_tg_message(chat_id, "🔍 <i>Initiating live Reddit scan now... Please wait 10-15 seconds for results.</i>")
        try:
            from auto_scheduler import run_scheduled_scan
            run_scheduled_scan()
        except Exception as e:
            send_tg_message(chat_id, f"⚠️ Scan failed: {e}")

def start_bot_listener():
    """
    Polls Telegram for button clicks and user messages.
    """
    offset = 0
    print("[BOT SERVER] Telegram Interactive Button & Command Listener started...")
    while True:
        try:
            res = requests.get(f"{API_URL}/getUpdates?offset={offset}&timeout=5", timeout=10)
            if res.status_code == 200:
                data = res.json()
                for update in data.get("result", []):
                    offset = update.get("update_id") + 1
                    if "callback_query" in update:
                        handle_callback_query(update["callback_query"])
                    elif "message" in update:
                        handle_message(update["message"])
            time.sleep(1)
        except Exception as e:
            time.sleep(2)


if __name__ == "__main__":
    from serp_rank_scanner import get_google_ranked_threads
    threads = get_google_ranked_threads()
    print(f"Sending {len(threads)} Google-Ranked leads with interactive buttons...")
    for t in threads:
        send_interactive_lead_card(t)
    print("All interactive cards sent! Now listening for button taps...")
    start_bot_listener()
