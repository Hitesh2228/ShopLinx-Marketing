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

def scan_platform(platform_name: str, lead_fetcher_func, max_leads: int = 3):
    now_str = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    log_event(f"Starting Scheduled AI Sniper Scan for [{platform_name}] at {now_str}...")

    try:
        seen = load_seen_threads()
        all_leads = lead_fetcher_func()
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
                log_event(f"[SUCCESS] Delivered {platform_name} lead to Telegram: {lead.get('title')[:40]}...")

            if sent_count >= max_leads:
                break

        if sent_count == 0:
            log_event(f"No new unread leads for {platform_name} in this slot.")
            status_msg = (
                f"ℹ️ <b>ShopLinx AI Sniper: {platform_name} Scan Completed</b>\n\n"
                f"✅ Scanned active discussions on {platform_name}.\n"
                f"📌 All current matching buyer-intent discussions have already been delivered to your chat.\n\n"
                f"⏰ Next scheduled scan in pipeline."
            )
            send_tg_message(CHAT_ID, status_msg)
        else:
            log_event(f"Successfully delivered {sent_count} fresh {platform_name} leads to Telegram!")
    except Exception as e:
        log_event(f"[SCAN ERROR] Exception in {platform_name} scan: {e}")

def run_shopify_scan():
    from shopify_community_scanner import get_shopify_community_leads
    scan_platform("Shopify Community", get_shopify_community_leads, max_leads=3)

def run_reddit_scan():
    from serp_rank_scanner import get_real_verified_threads
    scan_platform("Reddit", get_real_verified_threads, max_leads=3)

def run_youtube_scan():
    from youtube_video_scanner import get_youtube_video_leads
    scan_platform("YouTube", get_youtube_video_leads, max_leads=3)

def run_all_scans():
    run_shopify_scan()
    time.sleep(2)
    run_reddit_scan()
    time.sleep(2)
    run_youtube_scan()

def start_scheduler():
    print("=" * 65)
    print("  ⏰ SHOPLINX AI SNIPER MULTI-PLATFORM 24/7 DAEMON ACTIVE")
    print("=" * 65)
    print("Scheduled Daily Platform Slots:")
    print("  • 09:30 AM IST : 🛍️ Shopify Official Community (Morning Merchant Peak)")
    print("  • 02:30 PM IST : 🔴 Reddit Live Discussions (Mid-Day E-commerce)")
    print("  • 06:30 PM IST : 📺 YouTube Competitor & Video Radar (Evening Prime)")
    print("-" * 65)

    # 1. Start background Telegram Listener thread for buttons and commands (/status, /scan)
    listener_thread = threading.Thread(target=start_bot_listener, daemon=True)
    listener_thread.start()
    log_event("Interactive Telegram Listener thread launched.")

    # 2. Schedule times per platform
    schedule.every().day.at("09:30").do(run_shopify_scan)
    schedule.every().day.at("14:30").do(run_reddit_scan)
    schedule.every().day.at("18:30").do(run_youtube_scan)

    # 3. Notify user on Telegram that daemon is awake
    startup_msg = (
        "🟢 <b>ShopLinx AI Sniper Multi-Platform 24/7 Online!</b>\n\n"
        "📅 <b>Dedicated Platform Timings:</b>\n"
        "• 🌅 <b>09:30 AM IST:</b> 🛍️ Shopify Official Community\n"
        "• ☀️ <b>02:30 PM IST:</b> 🔴 Reddit E-commerce Radar\n"
        "• 🌆 <b>06:30 PM IST:</b> 📺 YouTube Competitor & Video Radar\n\n"
        "💡 Send <b>/status</b> or <b>/scan</b> anytime from your phone!"
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
    parser.add_argument("--platform", choices=["shopify", "reddit", "youtube", "all"], default="all", help="Target platform to scan")
    args = parser.parse_args()

    if args.now:
        if args.platform == "shopify":
            run_shopify_scan()
        elif args.platform == "reddit":
            run_reddit_scan()
        elif args.platform == "youtube":
            run_youtube_scan()
        else:
            run_all_scans()
    else:
        start_scheduler()

