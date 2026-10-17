import os
import sys
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

if sys.stdout is None:
    log_fp = open(os.path.join(LOG_DIR, "scheduler_output.log"), "a", encoding="utf-8", buffering=1)
    sys.stdout = log_fp
    sys.stderr = log_fp
elif sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

# Add scripts directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from serp_rank_scanner import get_real_verified_threads
from sniper_generator import generate_banproof_answer
import threading
from telegram_interactive_server import send_interactive_lead_card, start_bot_listener, send_tg_message, CHAT_ID

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "data", "logs")
LOG_FILE = os.path.join(LOG_DIR, "scheduler.log")
SEEN_THREADS_FILE = os.path.join(BASE_DIR, "data", "processed", "seen_threads.txt")

def log_event(msg: str):
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
    full_msg = f"[{timestamp}] {msg}"
    print(full_msg)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(full_msg + "\n")
    except Exception:
        pass

def load_seen_threads() -> set:
    if os.path.exists(SEEN_THREADS_FILE):
        with open(SEEN_THREADS_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    return set()

def save_seen_thread(url: str):
    os.makedirs(os.path.dirname(SEEN_THREADS_FILE), exist_ok=True)
    with open(SEEN_THREADS_FILE, "a", encoding="utf-8") as f:
        f.write(url + "\n")

def run_scheduled_scan():
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    log_event(f"Starting Scheduled AI Sniper Scan at {now_str}...")

    try:
        seen = load_seen_threads()
        all_leads = get_real_verified_threads()
        sent_count = 0

        for lead in all_leads:
            url = lead.get("url", "")
            if url in seen:
                continue

            success = send_interactive_lead_card(lead, initial_mode="zero_click")
            if success:
                save_seen_thread(url)
                seen.add(url)
                sent_count += 1
                log_event(f"[SUCCESS] Delivered lead to Telegram: {lead.get('title')[:40]}...")

            if sent_count >= 3:
                break

        if sent_count == 0:
            log_event("No new unread leads for this slot.")
        else:
            log_event(f"Successfully delivered {sent_count} fresh leads to Telegram!")
    except Exception as e:
        log_event(f"[SCAN ERROR] Exception occurred during scan: {e}")

def start_scheduler():
    print("=" * 65)
    print("  ⏰ SHOPLINX AI SNIPER AUTOMATED 24/7 DAEMON ACTIVE")
    print("=" * 65)
    print("Scheduled Daily Slots:")
    print("  • Morning Slot : 09:30 AM (Morning Business Prime Time)")
    print("  • Afternoon Slot: 02:30 PM (Mid-Day E-commerce Updates)")
    print("  • Evening Slot : 06:30 PM (Evening Discussions & US Peak Hours)")
    print("-" * 65)

    # 1. Start background Telegram Listener thread for buttons and commands (/status, /scan)
    listener_thread = threading.Thread(target=start_bot_listener, daemon=True)
    listener_thread.start()
    log_event("Interactive Telegram Listener thread launched.")

    # 2. Schedule times
    schedule.every().day.at("09:30").do(run_scheduled_scan)
    schedule.every().day.at("14:30").do(run_scheduled_scan)
    schedule.every().day.at("18:30").do(run_scheduled_scan)

    # 3. Notify user on Telegram that daemon is awake
    startup_msg = (
        "🟢 <b>ShopLinx AI Sniper 24/7 System Online!</b>\n\n"
        "✅ Automated scans scheduled at: <b>09:30 AM | 02:30 PM | 06:30 PM</b>\n"
        "💡 You can send <b>/status</b> to verify bot uptime, or <b>/scan</b> to get fresh leads right now!"
    )
    send_tg_message(CHAT_ID, startup_msg)
    log_event("Startup Telegram notification dispatched.")

    log_event("Scheduler is running in background. Waiting for trigger times...")
    while True:
        try:
            schedule.run_pending()
        except Exception as e:
            log_event(f"[SCHEDULER LOOP ERROR] {e}")
        time.sleep(30)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--now", action="store_true", help="Run a scan immediately")
    args = parser.parse_args()

    if args.now:
        run_scheduled_scan()
    else:
        start_scheduler()

