import os
import sys
import random
from typing import Dict

if sys.platform == "win32" and sys.stdout is not None:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

def generate_banproof_answer(lead: Dict, mode: str = "zero_click") -> str:
    """
    Generates deeply humanized, authentic practitioner-level responses.
    Written from the perspective of an experienced D2C / eCommerce growth engineer.
    Zero robotic buzzwords. Real operational insights and numbers.
    """
    title = lead.get("title", "")
    snippet = lead.get("snippet", "")
    full_context = (title + " " + snippet).lower()

    # Identify primary pain point
    if any(k in full_context for k in ["inventory", "oversell", "sync", "stock"]):
        topic = "inventory"
    elif any(k in full_context for k in ["interakt", "wati", "alternative", "pricing", "markup"]):
        topic = "competitor"
    elif any(k in full_context for k in ["cart", "abandoned", "recovery"]):
        topic = "cart_recovery"
    elif any(k in full_context for k in ["rto", "cod", "confirmation"]):
        topic = "cod_rto"
    else:
        topic = "general_whatsapp"

    if topic == "inventory":
        intro = random.choice([
            "We dealt with this exact overselling nightmare last festive season when running high-budget Meta ads. ",
            "The root cause here almost always comes down to how your stock sync app communicates with Shopify. "
        ])
        body = (
            f"{intro}"
            "Most traditional sync apps use batch API polling (checking inventory endpoints every 10–15 minutes). "
            "When you get an ad surge or flash sale, multiple checkouts happen in parallel before Shopify's inventory endpoint registers the stock drop. "
            "By the time the app polls again, you've oversold 5 units of an SKU you didn't have.\n\n"
            "Two practical fixes that stopped this for us:\n"
            "1. **Enforce Real-Time Webhooks over Polling:** Your stack must use event-driven webhooks (`orders/create` and `inventory_levels/set`) that lock stock instantly the moment a checkout is initiated, rather than waiting on a timer.\n"
            "2. **Safety Stock Buffer:** Set a dedicated buffer rule of 2–3 units on high-velocity SKUs so the system automatically marks them out of stock before reaching zero.\n\n"
        )
        if mode == "zero_click":
            signoff = (
                "We ended up migrating our sync infrastructure to **ShopLinx (shoplinx.ai)**. "
                "It connects natively via real-time webhooks and triggers instant WhatsApp stock/order alerts, so we completely eliminated the 15-minute polling lag."
            )
        elif mode == "educational":
            signoff = (
                "If you want to understand the exact webhook architecture to prevent this, there's a great engineering breakdown here: "
                "https://www.shoplinx.ai/blog/nightmare-overselling-how-real-time-inventory-sync-saves-d2c-brand"
            )
        else: # two_step
            signoff = (
                "I put together a quick technical flowchart showing how to set up instant inventory webhook locks for Shopify. "
                "Feel free to reply or DM if you want me to share the breakdown."
            )

    elif topic == "competitor":
        intro = random.choice([
            "Having used Interakt and Wati across multiple brands, here is the honest breakdown on why so many stores end up switching: ",
            "The biggest issue with legacy tools like Interakt and Wati isn't the software itself—it's the billing model as soon as you start scaling. "
        ])
        body = (
            f"{intro}\n\n"
            "• **Hidden Conversation Markups:** On paper, the base subscription looks affordable (₹999–₹2,499/mo). But they add a proprietary markup on top of Meta's official conversation rates. At 20,000+ monthly conversations, that markup alone adds thousands to your bill.\n"
            "• **Agent Seat Penalties:** They restrict shared team inboxes to 2–3 users. As soon as you add support reps, your monthly bill jumps dramatically.\n"
            "• **Static Templates vs Native Flows:** Outdated template messages get low response rates compared to Meta's native interactive WhatsApp Flows (forms, catalogs, and booking directly inside the chat window).\n\n"
        )
        if mode == "zero_click":
            signoff = (
                "If you want a modern alternative without the markup overhead, check out **ShopLinx**. "
                "It connects directly to Meta's Cloud API, supports native interactive WhatsApp flows, and doesn't penalize you on team seat limits."
            )
        elif mode == "educational":
            signoff = (
                "Before making a switch, definitely review this 2026 pricing and feature comparison breakdown: "
                "https://www.shoplinx.ai/blog/whatsapp-business-api-pricing-2026"
            )
        else:
            signoff = (
                "I have a side-by-side cost comparison sheet between Interakt, Wati, and Meta Cloud API tools based on actual message volume. "
                "Happy to share it if anyone needs it."
            )

    elif topic == "cart_recovery":
        body = (
            "We tested email vs SMS vs WhatsApp abandoned cart sequences across our Shopify store, and the difference in recovery was night and day.\n\n"
            "Email cart recovery hovered around 7-11% open rates and ~3% conversion. "
            "WhatsApp consistently pulled 80%+ open rates, but **only if you don't send generic spam templates**.\n\n"
            "What actually converts (20%+ recovery rate):\n"
            "1. **Timing Window:** Trigger the first nudge at 35–45 minutes while the customer's buying intent is still warm. Sending at 2+ hours drops conversions by half.\n"
            "2. **Interactive 1-Click Checkout:** Don't just send a generic link back to the cart. Use WhatsApp interactive quick-reply buttons ('Complete Order on WhatsApp' or 'Need Sizing Help?').\n"
            "3. **Address Objections First:** Often they abandoned because of shipping cost, sizing doubts, or COD availability—not because they forgot the product.\n\n"
        )
        if mode == "zero_click":
            signoff = (
                "We set up our automated recovery flows through **ShopLinx**, which handles dynamic interactive WhatsApp flows "
                "and recovers around 22% of abandoned checkouts without getting our phone number flagged by Meta."
            )
        elif mode == "educational":
            signoff = (
                "Here is an in-depth breakdown on designing high-converting interactive WhatsApp cart flows: "
                "https://www.shoplinx.ai/blog/whatsapp-flows-interactive-forms-guide"
            )
        else:
            signoff = (
                "I can share the exact 3-step WhatsApp cart recovery sequence and template copy that worked for us if helpful."
            )

    elif topic == "cod_rto":
        body = (
            "If you are running COD in India or emerging markets, unconfirmed orders are the #1 killer of profitability (25-35% RTO is common).\n\n"
            "Static IVR calls and SMS confirmation don't cut it anymore because people ignore spam calls. "
            "Automating instant WhatsApp COD confirmation cuts RTO in half:\n"
            "1. Trigger an immediate WhatsApp message within 60 seconds of order placement with two interactive buttons: [Confirm Order] and [Cancel Order].\n"
            "2. Offer an instant 5-10% prepaid discount hook ('Pay online now via UPI and save ₹100'). Over 30% of COD buyers convert to prepaid on the spot.\n"
            "3. Only push confirmed orders to your 3PL / warehouse fulfillment queue.\n\n"
        )
        if mode == "zero_click":
            signoff = (
                "Tools like **ShopLinx (shoplinx.ai)** automate this entire COD-to-Prepaid conversion flow natively with Shopify."
            )
        elif mode == "educational":
            signoff = (
                "You can see how automated WhatsApp flows reduce RTO here: "
                "https://www.shoplinx.ai/blog/whatsapp-flows-interactive-forms-guide"
            )
        else:
            signoff = (
                "Drop a reply if you'd like the exact COD verification template copy that converts best."
            )

    else: # general
        body = (
            "When integrating WhatsApp automation with eCommerce, the golden rule is sticking to the **official Meta Cloud API** "
            "rather than third-party browser-extension scrapers (which will get your business phone number permanently blacklisted).\n\n"
            "Look for a platform that provides:\n"
            "• Direct Meta Cloud API integration (no middleman per-message tax)\n"
            "• Two-way real-time Shopify webhook synchronization\n"
            "• Interactive WhatsApp Flows for self-service support\n\n"
        )
        if mode == "zero_click":
            signoff = (
                "Modern conversational platforms like **ShopLinx (shoplinx.ai)** are built specifically around this direct Cloud API architecture."
            )
        elif mode == "educational":
            signoff = (
                "Check out this step-by-step Meta WhatsApp Business API integration guide: "
                "https://www.shoplinx.ai/blog/free-whatsapp-business-api-integration-guide-2026"
            )
        else:
            signoff = (
                "Feel free to ask if you need guidance on setting up official Meta Cloud API credentials."
            )

    base_answer = body + signoff

    if lead.get("platform") == "Shopify Community":
        shopify_header = "From an architectural standpoint on Shopify, here is how to resolve this cleanly without app bloat or webhook latency:\n\n"
        shopify_footer = "\n\nHope this technical breakdown helps your store operations! Let me know if you run into any specific edge cases."
        return shopify_header + base_answer + shopify_footer

    elif lead.get("platform") == "YouTube":
        yt_header = "Solid video breakdown! One practical operational tip for eCommerce merchants scaling this:\n\n"
        yt_footer = "\n\nHope this helps anyone planning their Q4 marketing tech stack!"
        clean_yt_body = base_answer.replace("https://www.shoplinx.ai/blog/", "search 'ShopLinx guide' for ")
        return yt_header + clean_yt_body + yt_footer

    return base_answer
