"""
20. Email notification scheduler — immediate / daily / weekly digests + unsubscribe.
Prompt: see "20. Email Digest.md".   Run: python3 email_digest.py
Source is a single unverified doc: treat the exact rules as a guess and confirm them in the interview.
"""
from collections import defaultdict

DAY = 24 * 60 * 60
PERIOD = {"daily": DAY, "weekly": 7 * DAY}
FREQUENCIES = {"immediate", "daily", "weekly"}


# ---------------- Part 1: parse subscriptions ----------------
def parse_subscriptions(text):
    """'user_id,topic,frequency' lines -> {user: {topic: frequency}}. Header / bad lines are skipped."""
    subs = {}
    for line in text.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != 3 or parts[2] not in FREQUENCIES:
            continue
        user, topic, freq = parts
        subs.setdefault(user, {})[topic] = freq       # a later line overrides the frequency
    return subs


def format_subscriptions(subs):
    return [f"{user}: " + ", ".join(f"{topic} ({freq})" for topic, freq in topics.items())
            for user, topics in subs.items()]


# ---------------- Parts 2-4: process the event stream ----------------
class Notifier:
    def __init__(self, subs):
        self.subscribers = defaultdict(dict)          # topic -> {user: frequency}
        for user, topics in subs.items():
            for topic, freq in topics.items():
                self.subscribers[topic][user] = freq
        self.pending = {}                             # (user, freq, period_no) -> [(ts, topic, content)]
        self.sent = []

    @staticmethod
    def _period_end(key):
        _, freq, period_no = key
        return (period_no + 1) * PERIOD[freq]

    def _flush_until(self, now):
        """Part 3: send every digest whose period has ended by `now`."""
        ready = sorted((key for key in self.pending if self._period_end(key) <= now),
                       key=lambda key: (self._period_end(key), key[0], key[1]))
        for key in ready:
            items = self.pending.pop(key)
            if items:                                 # can be empty after an unsubscribe
                body = "; ".join(f"{topic}: {content}" for _, topic, content in items)
                self.sent.append(f"{self._period_end(key)} -> {key[0]} [{key[1]} digest] {body}")

    def publish(self, ts, topic, content):
        self._flush_until(ts)
        for user, freq in self.subscribers.get(topic, {}).items():
            if freq == "immediate":                   # Part 2
                self.sent.append(f"{ts} -> {user} [immediate] {topic}: {content}")
            else:                                     # Part 3
                key = (user, freq, ts // PERIOD[freq])
                self.pending.setdefault(key, []).append((ts, topic, content))

    def unsubscribe(self, ts, user, topic):           # Part 4
        self._flush_until(ts)
        self.subscribers.get(topic, {}).pop(user, None)
        for key, items in self.pending.items():
            if key[0] == user:
                items[:] = [item for item in items if item[1] != topic]

    def finish(self):
        self._flush_until(float("inf"))
        return self.sent


def run(subscriptions_text, events):
    """
    events: ("publish", ts, topic, content) or ("unsubscribe", ts, user, topic).
    Processed in timestamp order; ties keep input order.
    """
    notifier = Notifier(parse_subscriptions(subscriptions_text))
    for event in sorted(events, key=lambda e: e[1]):
        kind = event[0]
        if kind == "publish":
            _, ts, topic, content = event
            notifier.publish(ts, topic, content)
        elif kind == "unsubscribe":
            _, ts, user, topic = event
            notifier.unsubscribe(ts, user, topic)
        else:
            raise ValueError(f"unknown event {event!r}")
    return notifier.finish()


# ---------------- tests ----------------
SUBS = """
user_id,topic,frequency
alice,payments,immediate
alice,fraud,daily
bob,payments,daily
bob,fraud,weekly
carol,payouts,hourly
"""


def test_part1():
    assert format_subscriptions(parse_subscriptions(SUBS)) == [
        "alice: payments (immediate), fraud (daily)",
        "bob: payments (daily), fraud (weekly)",       # carol's 'hourly' is not a valid frequency
    ]


def test_parts_2_to_4():
    events = [
        ("publish", 100, "payments", "p1"),
        ("publish", 200, "fraud", "f1"),
        ("unsubscribe", 300, "alice", "fraud"),       # alice's pending fraud digest must be dropped
        ("publish", 400, "fraud", "f2"),
        ("publish", DAY + 50, "payments", "p2"),
    ]
    assert run(SUBS, events) == [
        "100 -> alice [immediate] payments: p1",
        "86400 -> bob [daily digest] payments: p1",
        "86450 -> alice [immediate] payments: p2",
        "172800 -> bob [daily digest] payments: p2",
        "604800 -> bob [weekly digest] fraud: f1; fraud: f2",
    ]


def test_order_and_day_boundary():
    events = [("publish", DAY, "payments", "next-day"), ("publish", DAY - 1, "payments", "same-day")]
    assert run("bob,payments,daily", events) == [
        "86400 -> bob [daily digest] payments: same-day",
        "172800 -> bob [daily digest] payments: next-day",
    ]


if __name__ == "__main__":
    test_part1()
    test_parts_2_to_4()
    test_order_and_day_boundary()
    print("all tests passed")
