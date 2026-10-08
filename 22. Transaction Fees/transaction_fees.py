"""
22. Transaction fees — calculate_fees(transaction_csv). Your classmate's actual question.
Prompt: see "22. Transaction Fees.md".   Run: python3 transaction_fees.py

Parts 2 and 3 follow the screenshots exactly. Part 1's numbers were not in the screenshots
(only its intro was): every constant marked UNCONFIRMED is a placeholder to replace.
"""
import csv
import io
from collections import defaultdict
from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal

OUTPUT_HEADER = "id,transaction_type,payment_provider,fee"     # UNCONFIRMED output format
FIXED_FEE = Decimal(30)                                         # Part 2: "The fixed fee remains 30"

# ---------- Part 1 constants: UNCONFIRMED (taken from a programhelp write-up of this question) ----------
PART1_PAYMENT_RATE = Decimal("2.1")   # % — the single variable rate every payment used in Part 1
DISPUTE_FEE = Decimal(1500)           # "the dispute fee remains the same" — the real value is unknown
DISPUTE_WON_PAYS = {"card"}           # programhelp: a WON dispute still pays the fee if the provider is card
# payment_failed / payment_pending / refund_completed pay nothing.

# ---------- Part 2 table (from the screenshot) ----------
PART2_TABLE = [
    # provider   countries            variable rate %
    ("card",   ("ie",),             "2.1"),
    ("card",   ("de", "fr", "at"),  "2.3"),
    ("klarna", ("ie",),             "2.4"),
    ("klarna", ("de", "fr", "at"),  "2.5"),
]

# ---------- Part 3 table (from the screenshot) ----------
PART3_TABLE = [
    # provider   countries            normal %  threshold  after-threshold %
    ("card",   ("ie",),             "2.1",    10000,     "2.0"),
    ("card",   ("de", "fr", "at"),  "2.3",    10000,     "2.1"),
    ("klarna", ("ie",),             "2.4",    10000,     "2.3"),
    ("klarna", ("de", "fr", "at"),  "2.5",    10000,     "2.1"),
]


def expand(table):
    """Rows with country groups -> {(provider, country): [remaining columns]}."""
    return {(row[0], country): list(row[2:]) for row in table for country in row[1]}


PART2_RATES = {key: Decimal(rate) for key, (rate,) in expand(PART2_TABLE).items()}
PART3_TIERS = {key: (Decimal(normal), threshold, Decimal(after))
               for key, (normal, threshold, after) in expand(PART3_TABLE).items()}


# ---------------- parsing / formatting ----------------
def parse_transactions(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    txns = []
    for row in reader:
        # strip the keys too: Part 3's sample header is "...,payment_provider, status" (note the space)
        t = {key.strip(): (value or "").strip() for key, value in row.items() if key is not None}
        t["amount"] = int(t["amount"])
        for field in ("buyer_country", "payment_provider", "transaction_type", "status"):
            t[field] = t[field].lower()
        txns.append(t)
    return txns


def format_fee(fee, rounding=None):
    """rounding=None keeps the exact value (87.5); ROUND_FLOOR / ROUND_HALF_UP give whole minor units."""
    if rounding is not None:
        fee = fee.quantize(Decimal(1), rounding=rounding)
    return format(fee.normalize(), "f")


def format_output(txns, fees, rounding=None):
    return [OUTPUT_HEADER] + [
        f"{t['id']},{t['transaction_type']},{t['payment_provider']},{format_fee(fee, rounding)}"
        for t, fee in zip(txns, fees)]


# ---------------- pieces shared by every part ----------------
def is_charged_payment(t):
    return t["transaction_type"] == "payment" and t["status"] == "payment_completed"


def payment_fee(amount, rate_pct):
    """fixed + variable, exact. With floats, 3400 * 0.024 is 81.60000000000001."""
    return Decimal(amount) * rate_pct / 100 + FIXED_FEE


def other_fee(t):
    """Disputes, refunds and payments that didn't complete. Identical in every part."""
    if t["transaction_type"] == "dispute":
        if t["status"] == "dispute_lost":
            return DISPUTE_FEE
        if t["status"] == "dispute_won" and t["payment_provider"] in DISPUTE_WON_PAYS:
            return DISPUTE_FEE
    return Decimal(0)


# ---------------- Part 1: one variable rate for every payment ----------------
def fee_part1(t):
    return payment_fee(t["amount"], PART1_PAYMENT_RATE) if is_charged_payment(t) else other_fee(t)


def calculate_fees(transaction_csv, rounding=None):
    txns = parse_transactions(transaction_csv)
    return format_output(txns, [fee_part1(t) for t in txns], rounding)


# ---------------- Part 2: variable rate by (payment_provider, buyer_country) ----------------
def part2_rate(t):
    # combinations missing from the table fall back to Part 1's rate — ask the interviewer
    return PART2_RATES.get((t["payment_provider"], t["buyer_country"]), PART1_PAYMENT_RATE)


def fee_part2(t):
    return payment_fee(t["amount"], part2_rate(t)) if is_charged_payment(t) else other_fee(t)


def calculate_fees_by_country(transaction_csv, rounding=None):
    txns = parse_transactions(transaction_csv)
    return format_output(txns, [fee_part2(t) for t in txns], rounding)


# ---------------- Part 3: lower rate once a merchant's volume passes the threshold ----------------
class TieredFees:
    """
    Volume is tracked per (merchant_id, payment_provider, buyer_country), across all dates,
    in input order. A payment's rate depends on the volume BEFORE it ("the future transactions
    will carry a less fee"). inclusive=False: that earlier volume must be > threshold (the literal
    "surpasses"); inclusive=True: >= threshold.
    """

    def __init__(self, inclusive=False):
        self.inclusive = inclusive
        self.volume = defaultdict(int)

    def fee(self, t):
        if not is_charged_payment(t):
            return other_fee(t)                       # failed / pending payments add no volume
        tier = PART3_TIERS.get((t["payment_provider"], t["buyer_country"]))
        if tier is None:
            return fee_part2(t)                       # no tier for this provider / country
        normal, threshold, after = tier
        key = (t["merchant_id"], t["payment_provider"], t["buyer_country"])
        before = self.volume[key]
        passed = before >= threshold if self.inclusive else before > threshold
        self.volume[key] += t["amount"]
        return payment_fee(t["amount"], after if passed else normal)


def calculate_fees_tiered(transaction_csv, rounding=None, inclusive=False):
    txns = parse_transactions(transaction_csv)
    tiers = TieredFees(inclusive)
    return format_output(txns, [tiers.fee(t) for t in txns], rounding)


# ---------------- tests ----------------
HEADER = "id,reference,amount,currency,date,merchant_id,buyer_country,transaction_type,payment_provider,status"

PART2_SAMPLE = HEADER + """
py_1,1,1000,eur,2024-12-24,acct_1,ie,payment,card,payment_completed
py_2,2,2500,eur,2024-12-24,acct_1,de,payment,card,payment_completed
py_3,3,3400,eur,2024-12-25,acct_1,ie,payment,klarna,payment_completed
py_4,3,3400,eur,2024-12-25,acct_1,fr,payment,klarna,payment_completed
"""

# copied as shown in the screenshot, including the space before "status"
PART3_SAMPLE = """
id,reference,amount,currency,date,merchant_id,buyer_country,transaction_type,payment_provider, status
py_1,1,10000,eur,2024-12-24,acct_1,ie,payment,card,payment_completed
py_2,2,2500,eur,2024-12-24,acct_1,ie,payment,card,payment_completed
py_3,3,10000,eur,2024-12-24,acct_1,de,payment,card,payment_completed
py_4,4,2500,eur,2024-12-24,acct_1,de,payment,card,payment_completed
py_9,9,5000,eur,2024-12-24,acct_2,ie,payment,card,payment_completed
"""


def fees_only(lines):
    return [line.rsplit(",", 1)[1] for line in lines[1:]]


def test_part1_placeholders():
    csv_text = HEADER + """
t1,1,1000,usd,2024-12-24,acct_1,us,payment,card,payment_completed
t2,2,1000,usd,2024-12-24,acct_1,us,payment,card,payment_failed
t3,3,1000,usd,2024-12-24,acct_1,us,refund,card,refund_completed
t4,4,1000,usd,2024-12-24,acct_1,us,dispute,card,dispute_lost
t5,5,1000,usd,2024-12-24,acct_1,us,dispute,card,dispute_won
t6,6,1000,usd,2024-12-24,acct_1,us,dispute,klarna,dispute_won
"""
    assert fees_only(calculate_fees(csv_text)) == ["51", "0", "0", "1500", "1500", "0"]


def test_part2_sample():
    assert calculate_fees_by_country(PART2_SAMPLE) == [
        "id,transaction_type,payment_provider,fee",
        "py_1,payment,card,51",           # 1000 * 2.1% + 30
        "py_2,payment,card,87.5",         # 2500 * 2.3% + 30
        "py_3,payment,klarna,111.6",      # 3400 * 2.4% + 30
        "py_4,payment,klarna,115",        # 3400 * 2.5% + 30
    ]
    assert fees_only(calculate_fees_by_country(PART2_SAMPLE, rounding=ROUND_FLOOR)) == ["51", "87", "111", "115"]
    assert fees_only(calculate_fees_by_country(PART2_SAMPLE, rounding=ROUND_HALF_UP)) == ["51", "88", "112", "115"]


def test_part3_sample():
    # py_1 is exactly 10000. Has the threshold been "surpassed" after it? Ask.
    assert fees_only(calculate_fees_tiered(PART3_SAMPLE)) == ["240", "82.5", "260", "87.5", "135"]
    assert fees_only(calculate_fees_tiered(PART3_SAMPLE, inclusive=True)) == ["240", "80", "260", "82.5", "135"]


def test_part3_rules():
    csv_text = HEADER + """
a,1,6000,eur,2024-12-24,m1,ie,payment,card,payment_completed
b,2,5000,eur,2024-12-25,m1,ie,payment,card,payment_completed
c,3,100,eur,2024-12-26,m1,ie,payment,card,payment_completed
d,4,100,eur,2024-12-26,m1,de,payment,card,payment_completed
e,5,100,eur,2024-12-26,m2,ie,payment,card,payment_completed
f,6,20000,eur,2024-12-26,m3,ie,payment,card,payment_failed
g,7,100,eur,2024-12-26,m3,ie,payment,card,payment_completed
h,8,100,usd,2024-12-26,m1,us,payment,card,payment_completed
"""
    assert fees_only(calculate_fees_tiered(csv_text)) == [
        "156",    # a: earlier volume 0      -> 2.1%: 126 + 30
        "135",    # b: earlier volume 6000   -> 2.1% (b itself pushes the total past 10000)
        "32",     # c: earlier volume 11000  -> 2.0%: 2 + 30
        "32.3",   # d: same merchant, other country -> its own counter, 2.3%
        "32.1",   # e: other merchant -> its own counter, 2.1%
        "0",      # f: failed -> no fee and no volume
        "32.1",   # g: m3's volume is still 0
        "32.1",   # h: card / US has no tier -> Part 1's rate
    ]


def test_float_trap():
    assert 3400 * 0.024 + 30 != 111.6                    # float: 111.60000000000001
    assert payment_fee(3400, Decimal("2.4")) == Decimal("111.6")


if __name__ == "__main__":
    test_part1_placeholders()
    test_part2_sample()
    test_part3_sample()
    test_part3_rules()
    test_float_trap()
    print("\n".join(calculate_fees_tiered(PART3_SAMPLE)))
    print("all tests passed")
