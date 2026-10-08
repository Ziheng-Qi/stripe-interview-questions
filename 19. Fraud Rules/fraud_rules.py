"""
19. Fraud rules validation (4-part phone screen reported on LeetCode Discuss).
Prompt: see "19. Fraud Rules.md".   Run: python3 fraud_rules.py
Field names, thresholds and error codes are reconstructions — the interviewer will give the real ones.
"""
import csv
import io
from datetime import datetime
from decimal import Decimal, InvalidOperation

FIELDS = ["transaction_id", "user_id", "amount", "payment_method", "country", "timestamp"]

# error codes, highest priority first (Part 4)
E_INVALID = "E01_INVALID_FIELD"
E_BLOCKED = "E02_BLOCKED_METHOD"
E_AMOUNT = "E03_AMOUNT_OUT_OF_RANGE"
E_BEHAVIOR = "E04_BEHAVIOR_MISMATCH"
PRIORITY = [E_INVALID, E_BLOCKED, E_AMOUNT, E_BEHAVIOR]

CONFIG = {
    "amount_range": (Decimal("1.00"), Decimal("10000.00")),
    "blocked_methods": {"prepaid_card", "crypto"},
    "profiles": {   # user history for Part 3
        "u1": {"countries": {"US", "CA"}, "hours": (8, 22),
               "amount_range": (Decimal("10"), Decimal("100"))},
        "u2": {"countries": {"US"}, "hours": (9, 18),
               "amount_range": (Decimal("20"), Decimal("200"))},
    },
}


def parse(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [{key.strip(): (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader]


def in_hours(hour, start, end):
    """Inclusive hour range that may wrap past midnight, e.g. (22, 2)."""
    return start <= hour <= end if start <= end else (hour >= start or hour <= end)


def behavior_ok(country, hour, amount, profile):
    """Part 3: at least 50% of the behavior attributes must match the user's history."""
    checks = [
        country in profile["countries"],
        in_hours(hour, *profile["hours"]),
        profile["amount_range"][0] <= amount <= profile["amount_range"][1],
    ]
    return 2 * sum(checks) >= len(checks)            # integer math, no float ratio


def find_issues(txn, part, cfg=CONFIG):
    """Every issue code for one transaction, sorted by priority."""
    if any(not txn.get(field) for field in FIELDS):                    # Part 1
        return [E_INVALID]
    try:
        amount = Decimal(txn["amount"])
        hour = datetime.fromisoformat(txn["timestamp"]).hour
    except (InvalidOperation, ValueError):
        return [E_INVALID]
    if not amount.is_finite():                                          # "NaN" / "Infinity"
        return [E_INVALID]

    issues = []
    if part >= 2:                                                       # Part 2
        if txn["payment_method"].lower() in cfg["blocked_methods"]:
            issues.append(E_BLOCKED)
        low, high = cfg["amount_range"]
        if not low <= amount <= high:
            issues.append(E_AMOUNT)
    if part >= 3:                                                       # Part 3
        profile = cfg["profiles"].get(txn["user_id"])
        if profile and not behavior_ok(txn["country"], hour, amount, profile):
            issues.append(E_BEHAVIOR)
    return sorted(issues, key=PRIORITY.index)


def align(rows):
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    return ["  ".join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows]


def report(csv_text, part, cfg=CONFIG):
    rows = []
    for txn in parse(csv_text):
        issues = find_issues(txn, part, cfg)
        if part >= 4:                                                   # Part 4: up to two codes
            result = " ".join(issues[:2]) if issues else "OK"
        elif E_INVALID in issues:
            result = "INVALID"
        else:
            result = "SUSPICIOUS" if issues else "OK"
        rows.append([txn.get("transaction_id") or "?", txn.get("user_id") or "?", result])
    if part >= 4:
        return align([["TXN", "USER", "RESULT"]] + rows)
    return [f"{txn_id} {result}" for txn_id, _, result in rows]      # Parts 1-3: "<id> <status>"


# ---------------- tests ----------------
SAMPLE = """
transaction_id,user_id,amount,payment_method,country,timestamp
t1,u1,25.00,card,US,2024-05-01T10:15:00
t2,u1,,card,US,2024-05-01T11:00:00
t3,u2,50000.00,card,US,2024-05-01T12:00:00
t4,u2,30.00,prepaid_card,US,2024-05-01T12:30:00
t5,u1,40.00,card,BR,2024-05-01T03:00:00
t6,u3,15.00,card,FR,2024-05-01T09:00:00
t7,u2,20000.00,crypto,RU,2024-05-01T02:00:00
"""


def test_part1():
    assert report(SAMPLE, 1) == ["t1 OK", "t2 INVALID", "t3 OK", "t4 OK", "t5 OK", "t6 OK", "t7 OK"]


def test_part2():
    assert report(SAMPLE, 2) == ["t1 OK", "t2 INVALID", "t3 SUSPICIOUS", "t4 SUSPICIOUS",
                                 "t5 OK", "t6 OK", "t7 SUSPICIOUS"]


def test_part3():
    assert report(SAMPLE, 3) == ["t1 OK", "t2 INVALID", "t3 SUSPICIOUS", "t4 SUSPICIOUS",
                                 "t5 SUSPICIOUS", "t6 OK", "t7 SUSPICIOUS"]


def test_part4():
    assert report(SAMPLE, 4) == [
        "TXN  USER  RESULT",
        "t1   u1    OK",
        "t2   u1    E01_INVALID_FIELD",
        "t3   u2    E03_AMOUNT_OUT_OF_RANGE",
        "t4   u2    E02_BLOCKED_METHOD",
        "t5   u1    E04_BEHAVIOR_MISMATCH",
        "t6   u3    OK",
        "t7   u2    E02_BLOCKED_METHOD E03_AMOUNT_OUT_OF_RANGE",
    ]


def test_helpers():
    assert in_hours(23, 22, 2) and in_hours(1, 22, 2) and not in_hours(12, 22, 2)
    header = "transaction_id,user_id,amount,payment_method,country,timestamp\n"
    assert report(header + "x1,u1,abc,card,US,2024-05-01T10:00:00", 4)[1].endswith("E01_INVALID_FIELD")
    assert report(header + "x2,u1,NaN,card,US,2024-05-01T10:00:00", 4)[1].endswith("E01_INVALID_FIELD")


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_part4()
    test_helpers()
    print("\n".join(report(SAMPLE, 4)))
    print("all tests passed")
