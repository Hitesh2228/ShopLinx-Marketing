import requests
from bs4 import BeautifulSoup
import urllib.parse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

queries = [
    'site:reddit.com "interakt" alternative',
    'site:reddit.com "wati" alternative',
    'site:reddit.com best whatsapp api shopify',
    'site:reddit.com shopify inventory sync overselling'
]

print("=== TESTING GOOGLE/SERP RANKED REDDIT THREADS ===")
for q in queries:
    url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(q)}"
    r = requests.post("https://html.duckduckgo.com/html/", headers=headers, data={"q": q}, timeout=10)
    print(f"\nQuery: {q} | Status: {r.status_code}")
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        results = soup.find_all("div", class_="result__body")
        for res in results[:2]:
            title_tag = res.find("a", class_="result__snippet") or res.find("a", class_="result__url")
            link_tag = res.find("a", class_="result__url")
            title = res.find("h2", class_="result__title")
            raw_url = link_tag.get("href", "") if link_tag else ""
            if "uddg=" in raw_url:
                actual_url = urllib.parse.unquote(raw_url.split("uddg=")[1].split("&")[0])
            else:
                actual_url = raw_url
            t_text = title.text.strip() if title else "No title"
            print(f"  * Title: {t_text}")
            print(f"    URL: {actual_url}")
