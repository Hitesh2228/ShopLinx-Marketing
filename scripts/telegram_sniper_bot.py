import os
import requests
from dotenv import load_dotenv
from typing import Dict

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(lead: Dict, answer: str, mode: str = "zero_click") -> bool:
    """
    Sends a beautifully formatted card to Telegram channel/user with action buttons.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[TELEGRAM] Token or Chat ID not configured. Skipping live alert.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    strategy_desc = (
        "Zero-Click Brand Search (100% Safe)" if mode == "zero_click"
        else "Educational Guide Deep-Link" if mode == "educational"
        else "2-Step Conversational Request"
    )

    message_text = (
        f"🎯 <b>SHOPLINX AI SNIPER: HIGH-INTENT LEAD</b>\n\n"
        f"📍 <b>Platform:</b> {lead.get('platform')} ({lead.get('subreddit')})\n"
        f"🔥 <b>Buyer Intent:</b> {lead.get('intent_tier')} (Score: {lead.get('intent_score')}/100)\n"
        f"📌 <b>Thread:</b> {lead.get('title')}\n"
        f"🔗 <b>Direct Link:</b> <a href='{lead.get('url')}'>Click Here to Open Thread</a>\n\n"
        f"🛡️ <b>Anti-Ban Strategy:</b> {strategy_desc}\n\n"
        f"💡 <b>READY-TO-POST EXPERT ANSWER:</b>\n"
        f"<code>{answer}</code>\n\n"
        f"<i>👉 Action: Tap the code block above to copy, then click the link to paste!</i>"
    )

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "🔗 Open Reddit Thread", "url": lead.get("url")},
                ]
            ]
        }
    }

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            print(f"[TELEGRAM] Successfully delivered alert for: {lead.get('title')[:30]}...")
            return True
        else:
            print(f"[TELEGRAM FAIL] Status: {res.status_code}, Response: {res.text}")
            return False
    except Exception as e:
        print(f"[TELEGRAM ERROR] {e}")
        return False

if __name__ == "__main__":
    print("Telegram module initialized.")
