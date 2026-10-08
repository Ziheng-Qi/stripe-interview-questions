"""
18. Transaction Balancer — split a list of transactions into consecutive zero-sum groups.
Prompt: see "18. Transaction Balancer.md".   Run: python3 transaction_balancer.py
"""
from decimal import Decimal


def zero_sum_groups(transactions, value=lambda t: t):
    """
    Single pass, O(n) time:
      running balance == 0 -> close the group and keep it
      running balance <  0 -> the group is invalid: drop it, restart after this transaction
    A trailing group that never gets back to 0 is dropped.
    `value` maps an item to a number, so the money follow-up can reuse this function.
    """
    groups, current, balance = [], [], 0
    for t in transactions:
        current.append(t)
        balance += value(t)
        if balance < 0:
            current, balance = [], 0
        elif balance == 0:
            groups.append(current)
            current = []
    return groups


# ---------- Follow-up 1: dollars and cents ----------
def to_cents(amount):
    """'12.34' -> 1234. Parse money from the string as Decimal, then work in integer cents."""
    cents = Decimal(amount) * 100
    if cents != cents.to_integral_value():
        raise ValueError(f"more than 2 decimal places: {amount}")
    return int(cents)


def zero_sum_groups_money(amounts):
    """amounts are strings like '10.10'; returns the original strings, grouped."""
    return zero_sum_groups(amounts, value=to_cents)


# ---------- Follow-up 2: real-time stream ----------
class StreamingBalancer:
    """Keeps only the open group; returns a group the moment it closes, else None."""

    def __init__(self, value=lambda t: t):
        self.value = value
        self.current, self.balance = [], 0

    def add(self, t):
        self.current.append(t)
        self.balance += self.value(t)
        if self.balance < 0:
            self.current, self.balance = [], 0
        elif self.balance == 0:
            done, self.current = self.current, []
            return done
        return None


# ---------------- tests ----------------
def test_examples():
    assert zero_sum_groups([2, -2, 3, -1, -2, 4, -4]) == [[2, -2], [3, -1, -2], [4, -4]]
    assert zero_sum_groups([3, -4, 2, 1, -3]) == [[2, 1, -3]]


def test_edges():
    assert zero_sum_groups([]) == []
    assert zero_sum_groups([5, -1]) == []                  # never gets back to 0
    assert zero_sum_groups([-3, 3]) == []                  # negative at once; [3] never closes
    assert zero_sum_groups([1, -1, 1, -1]) == [[1, -1], [1, -1]]   # closes at the FIRST zero
    assert zero_sum_groups([0]) == [[0]]                   # ask the interviewer about this one


def test_money():
    assert zero_sum_groups([0.1, 0.2, -0.3]) == []         # float trap: 0.1 + 0.2 - 0.3 != 0
    assert zero_sum_groups_money(["0.1", "0.2", "-0.3"]) == [["0.1", "0.2", "-0.3"]]
    assert zero_sum_groups_money(["10.10", "-5.05", "-5.05"]) == [["10.10", "-5.05", "-5.05"]]
    try:
        to_cents("1.005")
    except ValueError:
        pass
    else:
        raise AssertionError("sub-cent amounts should be rejected")


def test_streaming_matches_batch():
    import random
    rng = random.Random(0)
    for _ in range(500):
        txns = [rng.randint(-5, 5) for _ in range(rng.randint(0, 30))]
        stream, streamed = StreamingBalancer(), []
        for t in txns:
            group = stream.add(t)
            if group is not None:
                streamed.append(group)
        assert streamed == zero_sum_groups(txns), txns


if __name__ == "__main__":
    test_examples()
    test_edges()
    test_money()
    test_streaming_matches_batch()
    print("all tests passed")
