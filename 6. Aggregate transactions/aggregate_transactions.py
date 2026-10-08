"""
6. Aggregate transactions — Brazil receivables: aggregate per (merchant, card type, payout date),
then apply financing contracts. Prompt: see "6. Aggregate transactions.md".
Run: python3 aggregate_transactions.py
"""
import csv
import io


def parse_rows(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [{key.strip(): (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader]


def receivable_key(row):
    return row["merchant_id"], row["card_type"], row["payout_date"]


# ---------------- Part 1: register_receivables ----------------
def register_receivables(transactions_csv):
    """{(merchant_id, card_type, payout_date): total amount}, in first-seen order."""
    totals = {}
    for row in parse_rows(transactions_csv):
        key = receivable_key(row)
        totals[key] = totals.get(key, 0) + int(row["amount"])
    return totals


def format_receivables(totals):
    # careful: the output column order is NOT the input order (payout_date / card_type swap)
    lines = ["merchant_id,card_type,payout_date,amount"]
    lines += [f"{merchant},{card},{day},{amount}" for (merchant, card, day), amount in totals.items()]
    return lines


# ---------------- Parts 2-4: update_receivables ----------------
def contract_amount(contract, receivable_amount, part):
    if part >= 4 and contract.get("type", "fixed") == "percentage":
        return receivable_amount * int(contract["amount"]) // 100      # Part 4: % of the receivable
    return int(contract["amount"])


def update_receivables(registered, contracts_csv, part=2):
    """
    Part 2: a contract replaces the whole matching merchant receivable.
    Part 3: a contract may take only part of it; the merchant keeps the rest (0 stays as 0).
    Part 4: a contract amount is either fixed or a percentage of the receivable.
    Output: contracts in input order, then what is left for the merchants.
    """
    remaining = dict(registered)
    lines = ["id,card_type,payout_date,amount"]
    for contract in parse_rows(contracts_csv):
        key = receivable_key(contract)
        if key not in registered:
            raise ValueError(f"{contract['contract_id']}: no receivable for {key}")
        amount = contract_amount(contract, registered[key], part)
        lines.append(f"{contract['contract_id']},{key[1]},{key[2]},{amount}")
        if part == 2:
            remaining.pop(key, None)
        else:
            remaining[key] = max(0, remaining[key] - amount)
    lines += [f"{merchant},{card},{day},{amount}" for (merchant, card, day), amount in remaining.items()]
    return lines


# ---------------- tests ----------------
TXN_1 = """
customer_id,merchant_id,payout_date,card_type,amount
cust1,merchantA,2021-12-30,Visa,150
cust2,merchantA,2021-12-30,Visa,200
cust3,merchantB,2021-12-31,MasterCard,300
cust4,merchantA,2021-12-30,Visa,50
"""
TXN_2 = """
customer_id,merchant_id,payout_date,card_type,amount
cust1,merchantA,2021-12-29,MasterCard,50
cust2,merchantA,2021-12-29,Visa,150
cust3,merchantB,2021-12-31,Visa,300
cust4,merchantB,2021-12-29,MasterCard,200
"""
TXN_3 = """
customer_id,merchant_id,payout_date,card_type,amount
cust1,merchantA,2022-01-05,Visa,300
cust2,merchantA,2022-01-05,Visa,200
cust3,merchantB,2022-01-06,MasterCard,1000
"""
TXN_4 = """
customer_id,merchant_id,payout_date,card_type,amount
cust1,merchantA,2022-01-07,Visa,500
cust2,merchantA,2022-01-07,Visa,250
cust3,merchantB,2022-01-08,MasterCard,1250
cust4,merchantC,2022-01-09,Visa,1500
"""


def test_part1():
    assert format_receivables(register_receivables(TXN_1)) == [
        "merchant_id,card_type,payout_date,amount",
        "merchantA,Visa,2021-12-30,400",
        "merchantB,MasterCard,2021-12-31,300",
    ]
    assert format_receivables(register_receivables(TXN_2)) == [
        "merchant_id,card_type,payout_date,amount",
        "merchantA,MasterCard,2021-12-29,50",
        "merchantA,Visa,2021-12-29,150",
        "merchantB,Visa,2021-12-31,300",
        "merchantB,MasterCard,2021-12-29,200",
    ]


def test_part2():
    contracts = "contract_id,merchant_id,payout_date,card_type,amount\ncontract1,merchantA,2022-01-05,Visa,500"
    assert update_receivables(register_receivables(TXN_3), contracts) == [
        "id,card_type,payout_date,amount",
        "contract1,Visa,2022-01-05,500",
        "merchantB,MasterCard,2022-01-06,1000",
    ]
    contracts = ("contract_id,merchant_id,payout_date,card_type,amount\n"
                 "contract1,merchantA,2022-01-07,Visa,750\n"
                 "contract2,merchantC,2022-01-09,Visa,1500")
    assert update_receivables(register_receivables(TXN_4), contracts) == [
        "id,card_type,payout_date,amount",
        "contract1,Visa,2022-01-07,750",
        "contract2,Visa,2022-01-09,1500",
        "merchantB,MasterCard,2022-01-08,1250",
    ]


def test_part3():
    txns = "customer_id,merchant_id,payout_date,card_type,amount\ncust1,merchantA,2022-01-07,Visa,500"
    contracts = "contract_id,merchant_id,payout_date,card_type,amount\ncontract1,merchantA,2022-01-07,Visa,200"
    assert update_receivables(register_receivables(txns), contracts, part=3) == [
        "id,card_type,payout_date,amount",
        "contract1,Visa,2022-01-07,200",
        "merchantA,Visa,2022-01-07,300",
    ]
    contracts = "contract_id,merchant_id,payout_date,card_type,amount\ncontract1,merchantA,2022-01-05,Visa,500"
    assert update_receivables(register_receivables(TXN_3), contracts, part=3) == [
        "id,card_type,payout_date,amount",
        "contract1,Visa,2022-01-05,500",
        "merchantA,Visa,2022-01-05,0",                 # fully sold: the row stays, at 0
        "merchantB,MasterCard,2022-01-06,1000",
    ]


def test_part4():
    contracts = ("contract_id,merchant_id,payout_date,card_type,amount,type\n"
                 "contract1,merchantA,2022-01-07,Visa,200,fixed\n"
                 "contract2,merchantB,2022-01-08,MasterCard,50,percentage")
    assert update_receivables(register_receivables(TXN_4), contracts, part=4) == [
        "id,card_type,payout_date,amount",
        "contract1,Visa,2022-01-07,200",
        "contract2,MasterCard,2022-01-08,625",         # 50% of 1250
        "merchantA,Visa,2022-01-07,550",
        "merchantB,MasterCard,2022-01-08,625",
        "merchantC,Visa,2022-01-09,1500",
    ]


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_part4()
    print("all tests passed")
