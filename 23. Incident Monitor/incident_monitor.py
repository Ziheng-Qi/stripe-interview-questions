"""
23. Incident Monitor — trigger / resolve per-(merchant, error code) alerts over a 30-second window.
地里 question bank: OA / tech screen / phone screen, frequency Medium, last asked 2026-09-07.
Prompt: see "23. Incident Monitor.md".   Run: python3 incident_monitor.py
"""
from collections import defaultdict, deque
from itertools import groupby

MIN_FAILURES = 5
# Keep logs with ts >= T - LOOKBACK. 30 reproduces the Part 3 example; the written definition
# [T-29, T] means 29. Ask which one — only this constant changes.
LOOKBACK = 30


def parse(log):
    ts, merchant, code, count = log.split(",")
    return int(ts), merchant.strip(), int(code), int(count)


class MerchantWindow:
    """Rolling per-status counts for one merchant. Logs sit in a FIFO, so eviction exactly undoes insertion."""

    def __init__(self):
        self.logs = deque()
        self.counts = defaultdict(int)

    def add(self, ts, code, count):
        self.logs.append((ts, code, count))
        self.counts[code] += count

    def evict(self, now, lookback):
        while self.logs and self.logs[0][0] < now - lookback:
            _, code, count = self.logs.popleft()
            self.counts[code] -= count
            if self.counts[code] == 0:
                del self.counts[code]


def should_alert(window, code, part):
    failures = window.counts.get(code, 0)
    if failures < MIN_FAILURES:                    # Part 1: at least 5 failures with this code
        return False
    if part == 1:
        return True
    successes = window.counts.get(200, 0)
    return failures * 100 > successes              # Part 2: strictly more than 1% (integers, no floats)


def detect_incidents(logs, part=3, lookback=LOOKBACK):
    windows = defaultdict(MerchantWindow)
    active = set()                                 # (merchant_id, error_code) pairs with an open alert
    events = []
    records = [parse(line) for line in logs if line.strip()]
    for ts, same_second in groupby(records, key=lambda r: r[0]):     # input is sorted by timestamp
        touched = set()
        for _, merchant, code, count in same_second:                 # apply every log of this second first
            windows[merchant].add(ts, code, count)
            touched.add(merchant)
        for merchant in touched:                   # only a merchant's own traffic re-evaluates its alerts
            window = windows[merchant]
            window.evict(ts, lookback)
            codes = {c for c in window.counts if c >= 400} | {c for m, c in active if m == merchant}
            for code in codes:
                key = (merchant, code)
                firing = should_alert(window, code, part)
                if firing and key not in active:
                    active.add(key)
                    events.append((ts, merchant, code, "TRIGGER"))
                elif not firing and key in active and part >= 3:     # Part 3: resolution
                    active.remove(key)
                    events.append((ts, merchant, code, "RESOLVE"))
    events.sort()                                  # timestamp, merchant, code, then RESOLVE < TRIGGER
    return [f"{ts},{event},{merchant},{code}" for ts, merchant, code, event in events]


# ---------------- tests: the three examples from the prompt, then edge cases ----------------
def test_part1():
    logs = ["10,merchant1,500,2", "10,merchant2,500,1", "15,merchant1,500,2",
            "20,merchant1,500,1", "20,merchant2,500,4"]
    assert detect_incidents(logs, part=1) == ["20,TRIGGER,merchant1,500", "20,TRIGGER,merchant2,500"]


def test_part2():
    logs = ["10,merchant1,200,600", "12,merchant1,500,6", "15,merchant2,200,599", "16,merchant2,500,6"]
    # merchant1: 6 is exactly 1% of 600 -> no; merchant2: 6 > 1% of 599 -> yes
    assert detect_incidents(logs, part=2) == ["16,TRIGGER,merchant2,500"]


def test_part3():
    logs = ["10,merchant1,500,6", "16,merchant2,500,6", "45,merchant1,200,1", "46,merchant2,200,1"]
    assert detect_incidents(logs) == [
        "10,TRIGGER,merchant1,500", "16,TRIGGER,merchant2,500", "45,RESOLVE,merchant1,500"]
    # with the written window [T-29, T], the log at 16 is gone by 46, so merchant2 resolves too
    assert detect_incidents(logs, lookback=29) == [
        "10,TRIGGER,merchant1,500", "16,TRIGGER,merchant2,500",
        "45,RESOLVE,merchant1,500", "46,RESOLVE,merchant2,500"]
    assert detect_incidents(logs, part=2) == ["10,TRIGGER,merchant1,500", "16,TRIGGER,merchant2,500"]


def test_no_duplicate_and_retrigger():
    logs = ["0,m1,500,5", "1,m1,500,5", "40,m1,200,1", "41,m1,500,5"]
    assert detect_incidents(logs) == ["0,TRIGGER,m1,500", "40,RESOLVE,m1,500", "41,TRIGGER,m1,500"]


def test_codes_are_separate_and_gaps_change_nothing():
    logs = ["0,m1,404,5", "0,m1,500,5", "100,m2,200,1"]     # m2's traffic never resolves m1's alerts
    assert detect_incidents(logs) == ["0,TRIGGER,m1,404", "0,TRIGGER,m1,500"]


def test_success_volume_leaving_the_window():
    logs = ["0,m1,200,1000", "5,m1,500,5", "31,m1,500,1"]   # at 31 the 1000 successes have expired
    assert detect_incidents(logs) == ["31,TRIGGER,m1,500"]


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_no_duplicate_and_retrigger()
    test_codes_are_separate_and_gaps_change_nothing()
    test_success_volume_leaving_the_window()
    print("all tests passed")
