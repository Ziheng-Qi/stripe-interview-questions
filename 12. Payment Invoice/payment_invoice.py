"""
12. Payment / invoice reconciliation — match by the memo's invoice ID, then by exact amount,
then within a forgiveness range. Prompt: "12. Payment Invoice.md"; the fuller spec (output wording,
"(forgiven X)", exact match beats tolerance) is from your PDF.   Run: python3 payment_invoice.py

Input (the interview's string format):
  payment  = "payment_id,amount,memo"            memo looks like "Paying off: invoice_id" (may be empty)
  invoices = ["invoice_id,due_date,amount", ...]  amounts in minor units (cents)
Output:
  "<payment_id> paid <amount> amount for invoice <invoice_id> on date <due_date>"
  + " (forgiven <difference>)" when Part 3's tolerance was needed
  "<payment_id> has no matching invoice" when nothing matches
"""
MEMO_PREFIX = "paying off:"


def parse_payment(raw):
    payment_id, amount, memo = (raw.split(",", 2) + ["", ""])[:3]    # the memo may contain commas
    memo = memo.strip()
    invoice_id = memo[len(MEMO_PREFIX):].strip() if memo.lower().startswith(MEMO_PREFIX) else ""
    return payment_id.strip(), int(amount), invoice_id


def parse_invoice(raw):
    invoice_id, due_date, amount = (part.strip() for part in raw.split(","))
    return {"id": invoice_id, "due_date": due_date, "amount": int(amount)}


def describe(payment_id, amount, invoice, forgiven=0):
    line = f"{payment_id} paid {amount} amount for invoice {invoice['id']} on date {invoice['due_date']}"
    return line + (f" (forgiven {forgiven})" if forgiven else "")


def earliest(candidates):
    """Earliest due date; YYYY-MM-DD strings sort correctly as plain strings."""
    return min(candidates, key=lambda inv: inv["due_date"]) if candidates else None


def reconcile(payment_raw, invoice_raws, forgiveness=0):
    payment_id, amount, memo_invoice_id = parse_payment(payment_raw)
    invoices = [parse_invoice(r) for r in invoice_raws]

    # Part 1: the memo names the invoice. Amount mismatches are ignored.
    # IDs are compared case-insensitively (the 地里 example has "invoiceX" vs "invoicex") — ask.
    if memo_invoice_id:
        for inv in invoices:
            if inv["id"].lower() == memo_invoice_id.lower():
                return describe(payment_id, amount, inv)
        # Unknown ID: we fall back to amount matching. Ask whether they'd rather report no match.

    # Part 2: same amount, earliest due date.
    # exact = earliest([inv for inv in invoices if inv["amount"] == amount])
    result = []
    for inv in invoices:
        if inv['amount'] == amount:
            result.append(inv)
    exact = min(result, key = lambda inv: inv['due_date']) if result else None

    if exact:
        return describe(payment_id, amount, exact)

    # Part 3: within +- forgiveness, earliest due date. Only reached when there is no exact match.
    close = earliest([inv for inv in invoices if abs(inv["amount"] - amount) <= forgiveness])
    if close:
        return describe(payment_id, amount, close, forgiven=abs(close["amount"] - amount))
    return f"{payment_id} has no matching invoice"


# ---------------- tests ----------------
def test_part1():
    invoices = ["invoice-id-1,2022-01-01,100", "invoice-id-2,2022-01-30,300"]
    assert reconcile("p_100,300,Paying off: invoice-id-1", invoices) == \
        "p_100 paid 300 amount for invoice invoice-id-1 on date 2022-01-01"      # amount mismatch ignored
    assert reconcile("paymentx,600,Paying off: invoiceX",
                     ["invoicea,2024-03-22,100", "invoiceb,2024-02-05,400", "invoicex,2025-05-20,1000"]) == \
        "paymentx paid 600 amount for invoice invoicex on date 2025-05-20"
    assert reconcile("p_9,1,Paying off: nope", invoices) == "p_9 has no matching invoice"


def test_part2():
    invoices = ["invoice-id-1,2022-01-01,100", "invoice-id-2,2022-01-15,300", "invoice-id-3,2022-02-01,300"]
    assert reconcile("p_200,300,", invoices) == "p_200 paid 300 amount for invoice invoice-id-2 on date 2022-01-15"
    assert reconcile("p_201,300", invoices) == "p_201 paid 300 amount for invoice invoice-id-2 on date 2022-01-15"
    assert reconcile("p_202,999,", invoices) == "p_202 has no matching invoice"


def test_part3():
    assert reconcile("p_300,300,", ["invoice-id-10,2022-01-01,100", "invoice-id-11,2022-01-05,295"],
                     forgiveness=5) == \
        "p_300 paid 300 amount for invoice invoice-id-11 on date 2022-01-05 (forgiven 5)"
    assert reconcile("p_301,300,", ["a,2022-01-03,300", "b,2022-01-01,299"], forgiveness=2) == \
        "p_301 paid 300 amount for invoice a on date 2022-01-03"                 # exact match beats tolerance
    assert reconcile("p_302,300,", ["a,2022-01-03,310"], forgiveness=5) == "p_302 has no matching invoice"


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    print("all tests passed")
