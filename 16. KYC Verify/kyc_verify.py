"""
16. KYC business verification — 2026 version of folder #13 "Col Verify".
Prompt: see "16. KYC Verify.md".   Run: python3 kyc_verify.py
"""
import csv
import io
import re

LENGTH_MIN, LENGTH_MAX = 5, 32
FORBIDDEN = ("loan", "cash advance")
SUFFIXES = ("llc", "inc")


def parse_csv(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [{key.strip(): (value or "") for key, value in row.items() if key is not None}
            for row in reader]


def is_blank(value):
    return value is None or value.strip() == ""


def words(text):
    """'North Star, Inc.' -> ['north', 'star', 'inc']"""
    return re.findall(r"[a-z0-9]+", (text or "").lower())


# ---- every check returns None when it passes, otherwise a short reason ----
def check_required(row, required_fields):
    missing = [f for f in required_fields if is_blank(row.get(f))]
    return f"missing {', '.join(missing)}" if missing else None


def check_length(row, field):
    n = len(row.get(field) or "")                    # original value: spaces count
    return None if LENGTH_MIN <= n <= LENGTH_MAX else f"{field} length {n}"


def contains_phrase(text_words, phrase):
    """Whole-word match: 'cash advance' hits 'Cash  Advance!', 'loan' does not hit 'Sloane'."""
    target = words(phrase)
    if not target:
        return False
    k = len(target)
    return any(text_words[i:i + k] == target for i in range(len(text_words) - k + 1))


def check_forbidden(row, phrases):
    description = words(row.get("description"))
    hits = [p for p in phrases if contains_phrase(description, p)]
    return f"forbidden {', '.join(hits)}" if hits else None


def check_name_overlap(row, suffixes):
    name = words(row.get("business_name"))
    while name and name[-1] in suffixes:             # strip suffixes only at the END
        name.pop()
    if not name:
        return "no name words left"
    nickname = set(words(row.get("nickname")))
    hit = sum(1 for w in name if w in nickname)
    return None if 2 * hit >= len(name) else f"name overlap {hit}/{len(name)}"


# ---------------- Parts 1-3 (+ guessed Part 4: show the first failing reason) ----------------
def build_checks(part, required, phrases, suffixes):
    suffix_set = set(suffixes)
    checks = [lambda row: check_required(row, required)]                   # Part 1
    if part >= 2:
        checks.append(lambda row: check_length(row, "nickname"))           # Part 2
        checks.append(lambda row: check_forbidden(row, phrases))
    if part >= 3:
        checks.append(lambda row: check_name_overlap(row, suffix_set))     # Part 3
    return checks


def verify(csv_text, part=3, phrases=FORBIDDEN, suffixes=SUFFIXES, show_reason=False):
    rows = parse_csv(csv_text)
    if not rows:
        return []
    required = [col for col in rows[0] if col != "business_name"]
    checks = build_checks(part, required, phrases, suffixes)
    out = []
    for row in rows:
        name = row.get("business_name") or ""
        if is_blank(name):                           # no business name -> no output line at all
            continue
        reasons = [r for r in (check(row) for check in checks) if r]
        line = ("VERIFIED: " if not reasons else "NOT VERIFIED: ") + name.strip()
        if show_reason and reasons:
            line += f" ({reasons[0]})"
        out.append(line)
    return out


# ---------------- tests ----------------
SAMPLE = """
business_name,url,nickname,description
Acme Labs LLC,acme.com,Acme Labs,Developer tools
,ghost.com,Ghost,Nothing here
North Star Inc.,northstar.io,North,Payment tools
Bright Oak LLC,brightoak.com,Bright Oak,Payday loan services
Red Pine LLC,redpine.com,Green Leaf,Garden supplies
Blue Sky LLC,,Blue Sky,Travel booking
Tiny Studio,tiny.io,Tiny,Design tools
"""


def test_part1():
    assert verify(SAMPLE, part=1) == [
        "VERIFIED: Acme Labs LLC",
        "VERIFIED: North Star Inc.",
        "VERIFIED: Bright Oak LLC",
        "VERIFIED: Red Pine LLC",
        "NOT VERIFIED: Blue Sky LLC",
        "VERIFIED: Tiny Studio",
    ]


def test_part2():
    assert verify(SAMPLE, part=2) == [
        "VERIFIED: Acme Labs LLC",
        "VERIFIED: North Star Inc.",
        "NOT VERIFIED: Bright Oak LLC",      # "loan" in the description
        "VERIFIED: Red Pine LLC",
        "NOT VERIFIED: Blue Sky LLC",
        "NOT VERIFIED: Tiny Studio",         # nickname "Tiny" has 4 characters
    ]


def test_part3():
    assert verify(SAMPLE, part=3) == [
        "VERIFIED: Acme Labs LLC",           # acme, labs both in the nickname
        "VERIFIED: North Star Inc.",         # 1 of 2 words = exactly half
        "NOT VERIFIED: Bright Oak LLC",
        "NOT VERIFIED: Red Pine LLC",        # 0 of 2 words
        "NOT VERIFIED: Blue Sky LLC",
        "NOT VERIFIED: Tiny Studio",
    ]


def test_reasons():
    out = verify(SAMPLE, part=3, show_reason=True)
    assert out[2] == "NOT VERIFIED: Bright Oak LLC (forbidden loan)"
    assert out[3] == "NOT VERIFIED: Red Pine LLC (name overlap 0/2)"
    assert out[4] == "NOT VERIFIED: Blue Sky LLC (missing url)"
    assert out[5] == "NOT VERIFIED: Tiny Studio (nickname length 4)"


def test_helpers():
    assert contains_phrase(words("Sloane Square shop"), "loan") is False
    assert contains_phrase(words("Fast CASH  advance!"), "cash advance") is True
    assert check_name_overlap({"business_name": "Inc Labs", "nickname": "Labs"}, {"inc"}) is None   # leading 'inc' stays
    assert check_name_overlap({"business_name": "Acme LLC Inc", "nickname": "Acme"}, {"llc", "inc"}) is None
    assert check_length({"nickname": " " * 5}, "nickname") is None    # spaces count toward the length
    assert verify("business_name,url\n") == []


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_reasons()
    test_helpers()
    print("\n".join(verify(SAMPLE, part=3, show_reason=True)))
    print("all tests passed")
