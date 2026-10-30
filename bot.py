import os
import requests
from py_clob_client.client import ClobClient
from py_clob_client.clob_types import MarketOrderArgs, OrderType
from py_clob_client.order_builder.constants import BUY

HOST = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"
PRIVATE_KEY = os.environ.get("POLY_PRIVATE_KEY")
FUNDER = os.environ.get("POLY_FUNDER", "")
CHAIN_ID = 137

# Keywords that flag a market as "awards" related
AWARD_KEYWORDS = [
    "award", "oscar", "emmy", "grammy", "golden globe",
    "esports award", "game award", "mvp", "best player",
    "best actor", "best director", "ballon d'or", "hall of fame",
]

DRY_RUN = os.environ.get("DRY_RUN", "true").lower() == "true"


def find_award_markets():
    """Pull active events from Gamma API and filter to awards markets."""
    resp = requests.get(
        f"{GAMMA_API}/events",
        params={"closed": "false", "limit": 100},
        timeout=30,
    )
    resp.raise_for_status()
    events = resp.json()

    markets = []
    for event in events:
        title = (event.get("title") or "").lower()
        if not any(kw in title for kw in AWARD_KEYWORDS):
            continue
        for m in event.get("markets", []):
            if m.get("closed"):
                continue
            token_ids = m.get("clobTokenIds") or []
            prices = m.get("outcomePrices") or []
            if not token_ids:
                continue
            markets.append({
                "event": event.get("title"),
                "question": m.get("question"),
                "yes_token": token_ids[0],
                "no_token": token_ids[1] if len(token_ids) > 1 else None,
                "yes_price": prices[0] if prices else "?",
                "no_price": prices[1] if len(prices) > 1 else "?",
            })
    return markets


def place_bet(token_id, amount_usd):
    """Market FOK buy order. Test with $1 first."""
    client = ClobClient(
        HOST,
        key=PRIVATE_KEY,
        chain_id=CHAIN_ID,
        signature_type=1 if FUNDER else 0,
        funder=FUNDER or None,
    )
    client.set_api_creds(client.create_or_derive_api_creds())

    order = MarketOrderArgs(
        token_id=token_id,
        amount=amount_usd,
        side=BUY,
        order_type=OrderType.FOK,
    )
    signed = client.create_market_order(order)
    return client.post_order(signed, OrderType.FOK)


def main():
    print(f"=== polybot254 start | DRY_RUN={DRY_RUN} ===")
    markets = find_award_markets()
    print(f"Found {len(markets)} active awards markets\n")

    for m in markets:
        print(f"- {m['question']}")
        print(f"    yes={m['yes_price']}  no={m['no_price']}")

    if not markets:
        return

    # --- Optional: uncomment to place a $1 test order on the first market ---
    # target = markets[0]
    # if DRY_RUN:
    #     print(f"\n[DRY RUN] would buy $1 of YES on: {target['question']}")
    # else:
    #     result = place_bet(target["yes_token"], 1.0)
    #     print(f"\nOrder result: {result}")


if __name__ == "__main__":
    main()