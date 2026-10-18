import os
import sys
import requests
import time
from typing import List, Dict

if sys.platform == "win32" and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

HEADERS = {
    "User-Agent": "ShopLinxSniper/2.2 (platform:shopify-community; contact:partners@shoplinx.ai)",
    "Accept": "application/json"
}

# High-value Shopify Community categories
SHOPIFY_CATEGORIES = [
    {"slug": "shopify-apps", "name": "Shopify Apps"},
    {"slug": "shopify-discussion", "name": "Shopify Discussion"},
    {"slug": "technical-qa", "name": "Technical Q&A"},
    {"slug": "payments-shipping-fulfilment", "name": "Payments & Fulfillment"}
]

HIGH_INTENT_KEYWORDS = [
    "whatsapp", "interakt", "wati", "inventory", "stock", "oversell", "overselling",
    "abandoned cart", "cart recovery", "chatbot", "customer support", "automation",
    "alternative", "pricing", "crm", "sales", "app recommendation", "meta", "order",
    "orders", "checkout", "shipping", "sync", "store", "conversion", "leads", "broadcast", "scale"
]

def get_shopify_community_leads() -> List[Dict]:
    """
    Scans live Shopify Official Community discussions (community.shopify.com)
    using the official Discourse JSON endpoints.
    Returns high-buyer-intent Shopify merchant threads.
    """
    verified_leads = []
    seen = set()

    for cat in SHOPIFY_CATEGORIES:
        slug = cat["slug"]
        cat_name = cat["name"]
        url = f"https://community.shopify.com/c/{slug}.json"

        try:
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                data = res.json()
                topics = data.get("topic_list", {}).get("topics", [])

                for topic in topics:
                    title = topic.get("title", "")
                    topic_id = topic.get("id")
                    topic_slug = topic.get("slug")

                    if not title or not topic_id or not topic_slug:
                        continue

                    full_url = f"https://community.shopify.com/t/{topic_slug}/{topic_id}"
                    if full_url in seen:
                        continue

                    title_lower = title.lower()
                    if any(k in title_lower for k in HIGH_INTENT_KEYWORDS):
                        seen.add(full_url)
                        verified_leads.append({
                            "platform": "Shopify Community",
                            "subreddit": f"Community / {cat_name}",
                            "title": title,
                            "url": full_url,
                            "intent_tier": "Tier 1 (Verified Merchant)",
                            "intent_score": 98,
                            "snippet": f"Shopify Merchant Discussion in {cat_name}: {title}"
                        })
            time.sleep(1.0)
        except Exception as e:
            print(f"[WARN] Error scanning Shopify Community {slug}: {e}")

    print(f"[SHOPIFY COMMUNITY SCANNER] Found {len(verified_leads)} live high-intent merchant threads.")
    return verified_leads

if __name__ == "__main__":
    leads = get_shopify_community_leads()
    for l in leads[:3]:
        print(f"[{l['subreddit']}] {l['title']}")
        print(f"URL: {l['url']}\n")
