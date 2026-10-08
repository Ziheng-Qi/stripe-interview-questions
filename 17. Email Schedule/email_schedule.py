"""
17. Email schedule — three reported variants of "expand a schedule into emails".
Prompt: see "17. Email Schedule.md".   Run: python3 email_schedule.py
"""
from collections import defaultdict
from datetime import date, timedelta


# ================= Variant A: send_schedule map, query at `now` =================
def send_time(user, key):
    """'start' / 'end' are fixed events; any other key is minutes relative to start ('-15', '60')."""
    if key == "start":
        return user["start"]
    if key == "end":
        return user["end"]
    try:
        return user["start"] + int(key)
    except ValueError:
        raise ValueError(f"unknown schedule key {key!r}") from None


def emails_due(users, send_schedule, now):
    """(user, email) pairs to send at `now`; users in input order, schedule in map order."""
    return [(user["name"], email)
            for user in users
            for key, email in send_schedule.items()
            if send_time(user, key) == now]


def full_timeline(users, send_schedule):
    """Likely follow-up: every email for every user, sorted by time (ties: user order, then schedule order)."""
    events = []
    for ui, user in enumerate(users):
        for ki, (key, email) in enumerate(send_schedule.items()):
            events.append((send_time(user, key), ui, ki, user["name"], email))
    events.sort()
    return [f"{t}: {email} -> {name}" for t, _, _, name, email in events]


# ================= Variant B: invoice reminder subject lines, sorted =================
def invoice_reminder_subjects(invoices, schedule, due_in_days=30):
    """
    schedule entries: {"offset": days relative to the invoice date, or "due", "subject": str}.
    Returns every reminder for every invoice, sorted by send date.
    """
    emails = []
    for ii, inv in enumerate(invoices):
        issued = date.fromisoformat(inv["invoice_date"])
        due = issued + timedelta(days=due_in_days)
        for si, rule in enumerate(schedule):
            send = due if rule["offset"] == "due" else issued + timedelta(days=rule["offset"])
            subject = f"[{rule['subject']}] Invoice {inv['invoice_id']} for {inv['customer']}"
            emails.append((send, ii, si, subject))
    emails.sort()
    return [f"{send.isoformat()} {subject}" for send, _, _, subject in emails]


# ================= Variant C: account notification rules for one day =================
def notifications_for_day(current_day, accounts, rules):
    """
    Triggers: on_create (created_day == today), days_before_expiration
    (expires_day - today == offset_days), after_expiration (today > expires_day).
    Output "<account_id> <rule_name> <template>": accounts in input order, rules in
    configuration order. Rules are bucketed once, so each account costs O(#matches)
    instead of O(#rules) — this matters at 200k accounts x 200k rules.
    """
    on_create, after_expiration = [], []
    before_expiration = defaultdict(list)            # offset_days -> [rule index]
    for idx, rule in enumerate(rules):
        trigger = rule["trigger"]
        if trigger == "on_create":
            on_create.append(idx)
        elif trigger == "after_expiration":
            after_expiration.append(idx)
        elif trigger == "days_before_expiration":
            before_expiration[rule["offset_days"]].append(idx)
        else:
            raise ValueError(f"unknown trigger {trigger!r}")

    out = []
    for acc in accounts:
        matched = []
        if acc["created_day"] == current_day:
            matched += on_create
        matched += before_expiration.get(acc["expires_day"] - current_day, [])
        if current_day > acc["expires_day"]:
            matched += after_expiration
        for idx in sorted(matched):                  # back to configuration order
            rule = rules[idx]
            out.append(f"{acc['account_id']} {rule['name']} {rule['template']}")
    return out


# ---------------- tests ----------------
USERS = [{"name": "A", "start": 100, "end": 400}, {"name": "B", "start": 115, "end": 300}]
SCHEDULE = {"start": "Welcome", "-15": "Starting soon", "60": "How is it going?", "end": "Goodbye"}


def test_variant_a():
    assert emails_due(USERS, SCHEDULE, 100) == [("A", "Welcome"), ("B", "Starting soon")]
    assert emails_due(USERS, SCHEDULE, 175) == [("B", "How is it going?")]
    assert emails_due(USERS, SCHEDULE, 300) == [("B", "Goodbye")]
    assert emails_due(USERS, SCHEDULE, 1) == []
    # a brand-new numeric key works without touching the code
    assert emails_due(USERS, {**SCHEDULE, "+200": "Halfway"}, 315) == [("B", "Halfway")]
    assert full_timeline(USERS, SCHEDULE) == [
        "85: Starting soon -> A",
        "100: Welcome -> A",
        "100: Starting soon -> B",
        "115: Welcome -> B",
        "160: How is it going? -> A",
        "175: How is it going? -> B",
        "300: Goodbye -> B",
        "400: Goodbye -> A",
    ]
    try:
        emails_due(USERS, {"midnight": "x"}, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("an unknown key should raise")


def test_variant_b():
    invoices = [
        {"invoice_id": "inv_1", "customer": "acme", "invoice_date": "2024-03-15"},
        {"invoice_id": "inv_2", "customer": "globex", "invoice_date": "2024-03-08"},
    ]
    schedule = [
        {"offset": -10, "subject": "Upcoming invoice"},
        {"offset": 0, "subject": "New invoice"},
        {"offset": 20, "subject": "Payment reminder"},
        {"offset": "due", "subject": "Invoice due"},
    ]
    assert invoice_reminder_subjects(invoices, schedule) == [
        "2024-02-27 [Upcoming invoice] Invoice inv_2 for globex",     # crosses into February (leap year)
        "2024-03-05 [Upcoming invoice] Invoice inv_1 for acme",
        "2024-03-08 [New invoice] Invoice inv_2 for globex",
        "2024-03-15 [New invoice] Invoice inv_1 for acme",
        "2024-03-28 [Payment reminder] Invoice inv_2 for globex",
        "2024-04-04 [Payment reminder] Invoice inv_1 for acme",
        "2024-04-07 [Invoice due] Invoice inv_2 for globex",
        "2024-04-14 [Invoice due] Invoice inv_1 for acme",
    ]


def test_variant_c():
    accounts = [
        {"account_id": "a1", "created_day": 10, "expires_day": 40},
        {"account_id": "a2", "created_day": 1, "expires_day": 17},
        {"account_id": "a3", "created_day": 2, "expires_day": 8},
    ]
    rules = [
        {"name": "welcome", "trigger": "on_create", "template": "Welcome aboard"},
        {"name": "warn7", "trigger": "days_before_expiration", "offset_days": 7,
         "template": "Expires in 7 days"},
        {"name": "warn30", "trigger": "days_before_expiration", "offset_days": 30,
         "template": "Expires in 30 days"},
        {"name": "expired", "trigger": "after_expiration", "template": "Your account expired"},
    ]
    assert notifications_for_day(10, accounts, rules) == [
        "a1 welcome Welcome aboard",
        "a1 warn30 Expires in 30 days",
        "a2 warn7 Expires in 7 days",
        "a3 expired Your account expired",
    ]
    assert notifications_for_day(9, accounts, rules) == ["a3 expired Your account expired"]


if __name__ == "__main__":
    test_variant_a()
    test_variant_b()
    test_variant_c()
    print("all tests passed")
