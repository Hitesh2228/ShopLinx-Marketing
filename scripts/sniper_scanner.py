import os
import sys
import time
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}

TARGET_SUBREDDITS = [
    "shopify",
    "ecommerce",
    "smallbusiness",
    "DTC",
    "SaaS",
    "entrepreneur"
]

BUYER_INTENT_KEYWORDS = [
    "whatsapp", "interakt", "wati", "inventory", "stock", "oversell", "overselling",
    "abandoned cart", "cart recovery", "chatbot", "customer support", "automation",
    "alternative", "pricing", "crm", "sales", "app recommendation"
]

def calculate_intent_score(title: str, text: str) -> int:
    score = 50
    content = (title + " " + text).lower()
    for kw in BUYER_INTENT_KEYWORDS:
        if kw in content:
            score += 10
    if "?" in title:
        score += 10
    if any(comp in content for comp in ["interakt", "wati", "respond.io"]):
        score += 30
    if any(inv in content for inv in ["inventory", "oversell", "stock sync"]):
        score += 25
    return min(score, 100)

def search_reddit_opportunities(limit_per_sub=25) -> List[Dict]:
    opportunities = []
    seen_urls = set()

    print("[SCANNER] Scanning live feeds across targeted subreddits...")

    for sub in TARGET_SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/new.rss"
        try:
            res = requests.get(url, headers=HEADERS, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                entries = root.findall("atom:entry", ns)
                
                for entry in entries:
                    title_elem = entry.find("atom:title", ns)
                    link_elem = entry.find("atom:link", ns)
                    content_elem = entry.find("atom:content", ns)

                    title = title_elem.text if title_elem is not None else ""
                    post_url = link_elem.attrib.get("href", "") if link_elem is not None else ""
                    body = content_elem.text if content_elem is not None else ""

                    if not post_url or post_url in seen_urls:
                        continue
                    seen_urls.add(post_url)

                    # Check for intent matches
                    full_text = (title + " " + body).lower()
                    if any(k in full_text for k in BUYER_INTENT_KEYWORDS):
                        score = calculate_intent_score(title, body)
                        tier = "Tier 1 (Ready to Buy)" if score >= 80 else "Tier 2 (High Interest)"
                        
                        opportunities.append({
                            "platform": "Reddit",
                            "subreddit": f"r/{sub}",
                            "title": title,
                            "url": post_url,
                            "intent_score": score,
                            "intent_tier": tier,
                            "snippet": (title[:200])
                        })
            time.sleep(1) # respectful delay between subreddits
        except Exception as e:
            print(f"[WARN] Failed scanning r/{sub}: {e}")

    opportunities.sort(key=lambda x: x["intent_score"], reverse=True)
    print(f"[SCANNER] Scan complete. Found {len(opportunities)} qualified high-intent opportunities.")
    return opportunities

if __name__ == "__main__":
    leads = search_reddit_opportunities()
    for l in leads[:5]:
        print(f"\n[{l['intent_tier']} - {l['intent_score']}/100] {l['subreddit']}")
        print(f"Title: {l['title']}")
        print(f"Link: {l['url']}")
