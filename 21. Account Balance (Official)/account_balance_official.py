"""
21. Account Balance — Stripe's official prep-guide sample: move money so every account has >= 100.
Prompt: see "21. Account Balance (Official).md".   Run: python3 account_balance_official.py
"""
THRESHOLD = 100


def parse_balances(text):
    """'AU: 80' lines -> {'AU': 80}, input order kept."""
    balances = {}
    for line in text.strip().splitlines():
        if line.strip():
            name, amount = line.split(":")
            balances[name.strip()] = int(amount)
    return balances


def format_transfers(transfers):
    return [f"from: {src}, to: {dst}, amount: {amount}" for src, dst, amount in transfers]


def check_feasible(balances, threshold):
    if sum(balances.values()) < threshold * len(balances):
        raise ValueError("not enough total money for every account to reach the threshold")


# ---------------- Part 1: any working plan (not optimal) ----------------
def plan_transfers(balances, threshold=THRESHOLD):
    """Two pointers over donors (surplus) and receivers (deficit), both in input order."""
    check_feasible(balances, threshold)
    donors = [[acct, bal - threshold] for acct, bal in balances.items() if bal > threshold]
    transfers, d = [], 0
    for acct, bal in balances.items():
        need = threshold - bal
        while need > 0:
            donor = donors[d]
            amount = min(need, donor[1])
            transfers.append((donor[0], acct, amount))
            donor[1] -= amount
            need -= amount
            if donor[1] == 0:
                d += 1
    return transfers


# ---------------- Follow-up 1: verify before moving real money ----------------
def apply_and_verify(balances, transfers, threshold=THRESHOLD):
    """
    Simulate on a copy, then check every invariant. If anything fails, raise and execute nothing.
    Returns the balances after the transfers.
    """
    after = dict(balances)
    for src, dst, amount in transfers:
        if src not in after or dst not in after:
            raise ValueError(f"unknown account in transfer {src} -> {dst}")
        if amount <= 0:
            raise ValueError(f"non-positive transfer {src} -> {dst}: {amount}")
        after[src] -= amount
        after[dst] += amount
    if sum(after.values()) != sum(balances.values()):
        raise AssertionError("money was created or destroyed")
    below = [acct for acct, bal in after.items() if bal < threshold]
    if below:
        raise AssertionError(f"accounts still below {threshold}: {below}")
    return after


# ---------------- Follow-up 2: fewer moves (heuristic) ----------------
def plan_transfers_fewer_moves(balances, threshold=THRESHOLD):
    """
    The exact minimum is NP-hard ("each receiver gets exactly one transfer" is bin packing),
    so use a heuristic: biggest deficit first; if some donor can cover it alone, use the
    smallest such donor (best fit); otherwise drain the biggest donor and repeat.
    """
    check_feasible(balances, threshold)
    surplus = {acct: bal - threshold for acct, bal in balances.items() if bal > threshold}
    needs = sorted(((threshold - bal, acct) for acct, bal in balances.items() if bal < threshold),
                   reverse=True)
    transfers = []
    for need, acct in needs:
        while need > 0:
            covering = [donor for donor, s in surplus.items() if s >= need]
            donor = (min(covering, key=surplus.get) if covering
                     else max(surplus, key=surplus.get))
            amount = min(need, surplus[donor])
            transfers.append((donor, acct, amount))
            surplus[donor] -= amount
            need -= amount
            if surplus[donor] == 0:
                del surplus[donor]
    return transfers


# ---------------- tests ----------------
SAMPLE = """
AU: 80
US: 140
MX: 110
SG: 120
FR: 70
"""


def test_part1():
    balances = parse_balances(SAMPLE)
    plan = plan_transfers(balances)
    assert format_transfers(plan) == [          # identical to the official example output
        "from: US, to: AU, amount: 20",
        "from: US, to: FR, amount: 20",
        "from: MX, to: FR, amount: 10",
    ]
    after = apply_and_verify(balances, plan)
    assert all(bal >= 100 for bal in after.values())


def test_verify_rejects_bad_plans():
    balances = parse_balances(SAMPLE)
    bad_plans = [
        [("US", "AU", 10)],                       # AU and FR still below 100
        [("US", "XX", 20)],                       # unknown account
        [("US", "AU", -5)],                       # negative amount
        [("US", "AU", 20), ("US", "FR", 30)],     # the donor drops below 100
    ]
    for bad in bad_plans:
        try:
            apply_and_verify(balances, bad)
        except (ValueError, AssertionError):
            pass
        else:
            raise AssertionError(f"bad plan accepted: {bad}")


def test_fewer_moves():
    balances = parse_balances(SAMPLE)
    plan = plan_transfers_fewer_moves(balances)
    assert format_transfers(plan) == [          # matches the official minimum
        "from: US, to: FR, amount: 30",
        "from: SG, to: AU, amount: 20",
    ]
    apply_and_verify(balances, plan)


def test_edges():
    assert plan_transfers({"A": 100, "B": 150}) == []
    try:
        plan_transfers({"A": 50, "B": 120})
    except ValueError:
        pass
    else:
        raise AssertionError("should be impossible")


def test_random():
    import random
    rng = random.Random(7)
    for _ in range(500):
        n = rng.randint(1, 8)
        balances = {f"A{i}": rng.randint(0, 250) for i in range(n)}
        if sum(balances.values()) < 100 * n:
            continue
        for planner in (plan_transfers, plan_transfers_fewer_moves):
            apply_and_verify(balances, planner(balances))


if __name__ == "__main__":
    test_part1()
    test_verify_rejects_bad_plans()
    test_fewer_moves()
    test_edges()
    test_random()
    print("\n".join(format_transfers(plan_transfers(parse_balances(SAMPLE)))))
    print("all tests passed")
