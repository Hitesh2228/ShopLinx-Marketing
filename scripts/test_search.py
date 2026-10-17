from duckduckgo_search import DDGS

ddgs = DDGS()
results = list(ddgs.text("interakt alternative whatsapp reddit", max_results=5))
print(f"Found {len(results)} results:")
for r in results:
    print("Title:", r.get("title"))
    print("URL:", r.get("href"))
    print("Body:", r.get("body")[:120])
    print("-" * 40)
