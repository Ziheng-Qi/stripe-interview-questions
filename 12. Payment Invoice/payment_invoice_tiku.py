"""
12. Invoice / Payment Reconciliation — the 地里 question bank's canonical version.
Frequency High, last asked 2026-09-29; phone screen / tech screen / onsite coding.

reconcile_payment(payment, invoices, forgiveness=0) -> str
  payment  = "payment-id, amount, memo"       the memo may itself contain commas
  invoice  = "invoice-id, due-date, amount"   amount in cents, due-date YYYY-MM-DD
  Priority: invoice id named in the memo  >  exact amount  >  fuzzy amount (only if forgiveness > 0)
  Ties at every tier: earliest due date (then input order).
  Match:    "Payment {payment-id} paid {amount} for invoice {invoice-id} due on {date}"
  No match: "Payment {payment-id} could not be matched to any invoice"

Tests live in test_reconcile.py (it tests my_solution.py if you write one, otherwise this file).
"""
MARKERS = ("paying for:", "paying off:")


def parse_payment(payment):
    """-> (payment_id, amount or None, memo). maxsplit=2 keeps commas inside the memo intact."""
    parts = [part.strip() for part in payment.split(",", 2)]
    payment_id = parts[0]
    try:
        amount = int(parts[1]) if len(parts) > 1 else None
    except ValueError:
        amount = None
    memo = parts[2] if len(parts) > 2 else ""
    return payment_id, amount, memo


def invoice_id_from_memo(memo):
    """Find the marker case-insensitively, but slice the id out of the ORIGINAL memo to keep its case."""
    lowered = memo.lower()
    for marker in MARKERS:
        pos = lowered.find(marker)
        if pos != -1:
            return memo[pos + len(marker):].strip()
    return None


def parse_invoices(invoices):
    """-> [(invoice_id, due_date, amount)]; malformed rows are skipped instead of crashing."""
    parsed = []
    for line in invoices:
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            continue
        invoice_id, due_date, amount = parts
        try:
            parsed.append((invoice_id, due_date, int(amount)))
        except ValueError:
            continue
    return parsed


def earliest(candidates):
    """YYYY-MM-DD sorts correctly as a plain string; min() keeps the first one on a tie."""
    return min(candidates, key=lambda inv: inv[1]) if candidates else None


def reconcile_payment(payment, invoices, forgiveness=0):
    payment_id, amount, memo = parse_payment(payment)
    no_match = f"Payment {payment_id} could not be matched to any invoice"
    if amount is None:                                     # malformed payment: don't throw
        return no_match
    rows = parse_invoices(invoices)
    wanted_id = invoice_id_from_memo(memo)

    tiers = [
        [inv for inv in rows if wanted_id and inv[0] == wanted_id],      # Part 1: id wins, amount ignored
        [inv for inv in rows if inv[2] == amount],                       # Part 2: exact amount
    ]
    if forgiveness > 0:                                                  # Part 3: fuzzy, range is inclusive
        tiers.append([inv for inv in rows if inv[2] != amount and abs(inv[2] - amount) <= forgiveness])

    for candidates in tiers:                               # strictly in priority order
        best = earliest(candidates)
        if best:
            invoice_id, due_date, _ = best
            return f"Payment {payment_id} paid {amount} for invoice {invoice_id} due on {due_date}"
    return no_match


if __name__ == "__main__":
    invoices = ["inv_1, 2024-03-01, 1000", "inv_2, 2024-01-15, 2500", "inv_3, 2024-02-01, 2500"]
    print(reconcile_payment("pmt_1, 9999, Paying off: inv_1", invoices))
    print(reconcile_payment("pmt_2, 2500, rent for January", invoices))
    print(reconcile_payment("pmt_3, 990, no id here", invoices, forgiveness=10))
    print(reconcile_payment("pmt_4, 1, nothing", invoices))
