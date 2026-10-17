import os
import sys
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

# Ensure utf-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from sniper_scanner import search_reddit_opportunities
from sniper_generator import generate_banproof_answer
from telegram_sniper_bot import send_telegram_alert

load_dotenv()

def run_growth_sniper(max_leads=5, mode="zero_click"):
    print("=" * 70)
    print("   SHOPLINX PRO MAX AI GROWTH SNIPER ENGINE (2026)")
    print("=" * 70)
    print(f"Target Brand: ShopLinx (https://www.shoplinx.ai/)")
    print(f"Anti-Ban Mode: {mode.upper()}")
    print("-" * 70)

    # 1. Scan Reddit & Target Communities
    leads = search_reddit_opportunities(limit_per_sub=25)
    if not leads:
        print("[INFO] No new high-intent leads found right now. Check back later.")
        return []

    processed_leads = []
    
    # 2. Process Top Leads
    for idx, lead in enumerate(leads[:max_leads], 1):
        answer = generate_banproof_answer(lead, mode=mode)
        lead["generated_answer"] = answer
        lead["processed_at"] = datetime.now().isoformat()
        processed_leads.append(lead)

        print(f"\n[{idx}] [TARGET] {lead['intent_tier']} (Score: {lead['intent_score']}/100)")
        print(f"    Subreddit : {lead['subreddit']}")
        print(f"    Title     : {lead['title']}")
        print(f"    URL       : {lead['url']}")
        print(f"    --- Anti-Ban Ready Answer ---")
        preview = lead['generated_answer'][:180].replace('\n', ' ')
        print(f"    {preview}...")

        # 3. Send Telegram Alert if configured
        send_telegram_alert(lead, answer, mode=mode)

    # 4. Save results to data/processed/
    os.makedirs("data/processed", exist_ok=True)
    json_path = "data/processed/sniper_leads.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(processed_leads, f, indent=2, ensure_ascii=False)

    csv_path = "data/processed/sniper_leads.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Platform", "Subreddit", "Intent Tier", "Score", "Title", "URL", "Generated Answer"])
        for l in processed_leads:
            writer.writerow([
                l["platform"],
                l["subreddit"],
                l["intent_tier"],
                l["intent_score"],
                l["title"],
                l["url"],
                l["generated_answer"]
            ])

    print("\n" + "=" * 70)
    print(f"[SUCCESS] Successfully processed {len(processed_leads)} high-intent leads!")
    print(f"Saved to: {json_path} and {csv_path}")
    print("=" * 70)

    return processed_leads

if __name__ == "__main__":
    run_growth_sniper(max_leads=5, mode="zero_click")
