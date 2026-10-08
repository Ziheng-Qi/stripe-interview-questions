"""
5. Shipping Cost 2 — order + per-country shipping table:
   flat per-unit cost -> quantity tiers -> fixed / incremental tiers.
Prompt: see "5. Shipping Cost 2.md" (CA laptop's second tier is 1000, per the poster's correction).
Run: python3 shipping_cost_2.py
"""


def tier_units(quantity, tier):
    """How many of the units 1..quantity fall inside [minQuantity, maxQuantity] (None = no cap)."""
    low = max(tier["minQuantity"], 1)
    high = quantity if tier["maxQuantity"] is None else min(quantity, tier["maxQuantity"])
    return max(0, high - low + 1)


def item_cost(quantity, pricing):
    if "cost" in pricing:                            # Part 1: one flat per-unit cost
        return quantity * pricing["cost"]
    total = 0
    for tier in pricing["costs"]:                    # Parts 2-3: quantity tiers
        units = tier_units(quantity, tier)
        if units == 0:
            continue
        if tier.get("type", "incremental") == "fixed":
            total += tier["cost"]                    # Part 3: one price for the whole tier
        else:
            total += units * tier["cost"]            # Part 2: per-unit price inside the tier
    return total


def calculate_shipping_cost(order, shipping_cost):
    table = {entry["product"]: entry for entry in shipping_cost[order["country"]]}
    items = order.get("items") or order.get("products") or []    # both spellings show up in posts
    total = 0
    for item in items:
        if item["product"] not in table:
            raise ValueError(f"no shipping cost for {item['product']} in {order['country']}")
        total += item_cost(item["quantity"], table[item["product"]])
    return total


# ---------------- tests ----------------
ORDER_US = {"country": "US", "items": [{"product": "mouse", "quantity": 20}, {"product": "laptop", "quantity": 5}]}
ORDER_CA = {"country": "CA", "items": [{"product": "mouse", "quantity": 20}, {"product": "laptop", "quantity": 5}]}


def tiers(*rows):
    """(min, max, cost[, type]) tuples -> tier dicts."""
    out = []
    for r in rows:
        tier = {"minQuantity": r[0], "maxQuantity": r[1], "cost": r[2]}
        if len(r) > 3:
            tier["type"] = r[3]
        out.append(tier)
    return out


COST_1 = {"US": [{"product": "mouse", "cost": 550}, {"product": "laptop", "cost": 1000}],
          "CA": [{"product": "mouse", "cost": 750}, {"product": "laptop", "cost": 1100}]}
COST_2 = {"US": [{"product": "mouse", "costs": tiers((0, None, 550))},
                 {"product": "laptop", "costs": tiers((0, 2, 1000), (3, None, 900))}],
          "CA": [{"product": "mouse", "costs": tiers((0, None, 750))},
                 {"product": "laptop", "costs": tiers((0, 2, 1100), (3, None, 1000))}]}
COST_3 = {"US": [{"product": "mouse", "costs": tiers((0, None, 550, "incremental"))},
                 {"product": "laptop", "costs": tiers((0, 2, 1000, "fixed"), (3, None, 900, "incremental"))}],
          "CA": [{"product": "mouse", "costs": tiers((0, None, 750, "incremental"))},
                 {"product": "laptop", "costs": tiers((0, 2, 1100, "fixed"), (3, None, 1000, "incremental"))}]}


def test_parts():
    assert calculate_shipping_cost(ORDER_US, COST_1) == 16000
    assert calculate_shipping_cost(ORDER_CA, COST_1) == 20500
    assert calculate_shipping_cost(ORDER_US, COST_2) == 15700     # 20*550 + 2*1000 + 3*900
    assert calculate_shipping_cost(ORDER_CA, COST_2) == 20200
    assert calculate_shipping_cost(ORDER_US, COST_3) == 14700     # 20*550 + 1000 + 3*900
    assert calculate_shipping_cost(ORDER_CA, COST_3) == 19100


def test_edges():
    laptop = {"costs": tiers((0, 2, 1000, "fixed"), (3, None, 900))}
    assert [item_cost(q, laptop) for q in (0, 1, 2, 3)] == [0, 1000, 1000, 1900]   # fixed tier charged once
    assert item_cost(5, {"costs": tiers((0, None, 300, "fixed"))}) == 300          # fixed with no upper bound
    assert calculate_shipping_cost({"country": "US", "products": [{"product": "mouse", "quantity": 2}]},
                                   COST_1) == 1100


if __name__ == "__main__":
    test_parts()
    test_edges()
    print("all tests passed")
