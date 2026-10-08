def reconcile(payment: str, invoices: list[str]) -> str:
    pass

def parse_payment(payment):
    payment_id, amount, memo = (payment.split(",", 2) + ["", ""])[:3]    # the memo may contain commas