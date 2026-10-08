"""
Tests for 12. Payment Invoice, reported part by part.
Practice: put your solution in my_solution.py (same folder) as reconcile_payment(...) or reconcile(...),
then run `python3 test_reconcile.py`. Without my_solution.py it tests the reference in payment_invoice_tiku.py.
"""
import traceback

try:
    import my_solution
    reconcile_payment = getattr(my_solution, "reconcile_payment", None) or my_solution.reconcile
    SOURCE = "my_solution.py"
except ImportError:
    from payment_invoice_tiku import reconcile_payment
    SOURCE = "payment_invoice_tiku.py (reference)"

INVOICES = [
    "inv_1, 2024-03-01, 1000",
    "inv_2, 2024-01-15, 2500",
    "inv_3, 2024-02-01, 2500",
    "inv_4, 2024-01-10, 980",
    "inv_5, 2024-01-05, 1020",
]
WITHOUT_INV_1 = INVOICES[1:]


def paid(pid, amount, inv, date):
    return f"Payment {pid} paid {amount} for invoice {inv} due on {date}"


def unmatched(pid):
    return f"Payment {pid} could not be matched to any invoice"


def check(args, expected):
    actual = reconcile_payment(*args)
    assert actual == expected, f"\n  input:    {args}\n  expected: {expected}\n  got:      {actual}"


def test_part1_id_match():
    check(("pmt_1, 9999, Paying off: inv_1", INVOICES), paid("pmt_1", 9999, "inv_1", "2024-03-01"))   # id wins over a wrong amount
    check(("pmt_2, 100, PAYING FOR: inv_3", INVOICES), paid("pmt_2", 100, "inv_3", "2024-02-01"))     # both markers, any case
    check(("pmt_3, 100, Hi team, thanks, paying for: inv_2", INVOICES),
          paid("pmt_3", 100, "inv_2", "2024-01-15"))                                                  # commas in the memo
    check(("pmt_4, 100, paying for: INV_1", INVOICES), unmatched("pmt_4"))                           # id keeps its case (ask)


def test_part2_amount_match():
    check(("pmt_5, 2500, rent", INVOICES), paid("pmt_5", 2500, "inv_2", "2024-01-15"))               # earliest of two 2500s
    check(("pmt_6, 2500, paying off: inv_99", INVOICES), paid("pmt_6", 2500, "inv_2", "2024-01-15")) # unknown id -> amount
    check(("pmt_7, 1, nothing", INVOICES), unmatched("pmt_7"))
    check(("pmt_8, 500, x", ["a, 2024-01-01, 500", "b, 2024-01-01, 500"]), paid("pmt_8", 500, "a", "2024-01-01"))


def test_part3_forgiveness():
    check(("pmt_9, 1000, x", INVOICES, 20), paid("pmt_9", 1000, "inv_1", "2024-03-01"))              # exact beats fuzzy
    check(("pmt_10, 1000, x", WITHOUT_INV_1, 20), paid("pmt_10", 1000, "inv_5", "2024-01-05"))       # boundary 20 counts
    check(("pmt_11, 1000, x", WITHOUT_INV_1, 19), unmatched("pmt_11"))
    check(("pmt_12, 1000, x", WITHOUT_INV_1, 0), unmatched("pmt_12"))                                # 0 -> no fuzzy tier
    check(("pmt_13, 1000, paying for: inv_3", WITHOUT_INV_1, 20), paid("pmt_13", 1000, "inv_3", "2024-02-01"))


def test_malformed_input():
    check(("pmt_14", INVOICES), unmatched("pmt_14"))                                                  # no amount
    check(("pmt_15, abc, paying for: inv_1", INVOICES), unmatched("pmt_15"))
    check(("pmt_16, 2500", INVOICES), paid("pmt_16", 2500, "inv_2", "2024-01-15"))                   # no memo
    check(("pmt_17, 2500, x", ["broken row"] + INVOICES), paid("pmt_17", 2500, "inv_2", "2024-01-15"))
    check(("pmt_18, 2500, x", []), unmatched("pmt_18"))


if __name__ == "__main__":
    print(f"testing {SOURCE}")
    for test in (test_part1_id_match, test_part2_amount_match, test_part3_forgiveness, test_malformed_input):
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as error:
            print(f"FAIL  {test.__name__}{error}")
        except Exception:
            print(f"ERROR {test.__name__}\n{traceback.format_exc(limit=2)}")
