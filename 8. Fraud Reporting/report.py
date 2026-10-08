"""
Stripe Fraudulent Transaction Detection

Overview:
Stripe accepts payments on behalf of merchants. These payments begin as Authorization Requests,
which represent an intent to transfer funds from an end user's credit card to a merchant.
Your task is to process a stream of authorization requests and fraud rules in multiple phases,
and produce a human-readable report that classifies each request as APPROVED or REJECTED.
Additionally, calculate the total amount lost to fraud.

---

Part 1: Basic Authorization Report

You are given a list of authorization requests in the following CSV format (one per line):

    timestamp_seconds,unique_id,amount,card_number,merchant

- `timestamp_seconds`: a positive integer (seconds)
- `unique_id`: a unique identifier for the request
- `amount`: a positive decimal number
- `card_number`: a 16-digit string
- `merchant`: a string (alphanumeric/underscore/period)

Assume all values are valid and contain no extra commas or whitespace.

Goal:
Print each request in **chronological order** (by `timestamp_seconds`), one per line, using this format:

    <timestamp> <unique_id> <amount> APPROVE

Example Input:
    5,R1,5.60,4242424242424242,bobs_burgers
    10,R2,500.00,4242111111111111,a_corp

Expected Output:
    5 R1 5.60 APPROVE
    10 R2 500.00 APPROVE

---

Part 2: Apply Fraud Rules

You are now given a second input: a list of fraud rules, in the following format:

    time,field,value

Each rule means:
  "From time `t` onward, any request with `<field> == value` is considered fraudulent."

Fields can be either `merchant` or `card_number`.

Rules apply **permanently** once active, but **not retroactively** to past requests.

Example Fraud Rules:
    1,merchant,bobs_burgers
    20,card_number,4242111111111111

Goal:
Update the report to mark requests as either APPROVE or REJECT based on all fraud rules
active at the time the request was made.

Expected Output:
    5 R1 5.60 REJECT      # merchant 'bobs_burgers' is fraud from time=1
    10 R2 500.00 APPROVE  # card_number becomes fraud only from time=20

---

Part 3: Calculate Fraud Loss

Some fraud is only discovered after the transaction has been approved.
If a request was APPROVED, and a fraud rule matching that request is introduced **after** its timestamp,
the transaction is now considered a fraud loss.

Goal:
Calculate the total amount lost to retroactive fraud.

Example:

Requests:
    5,R1,5.60,4242424242424242,bobs_burgers
    10,R2,500.00,4242111111111111,a_corp

Fraud Rules:
    20,card_number,4242111111111111
    30,merchant,bobs_burgers

Result:
    Total fraud loss: 505.60  # Both R1 and R2 are matched by future fraud rules

---

Deliverables:
- A function that produces the output report as described
- A separate function to compute the total fraud loss
- Sufficient test cases to validate correctness
"""


def parse_payments(requests):
    # parse requests
    payments = []
    for request in requests.split("\n"):
        # print(request)
        # print(request.split(","))
        timestamp_seconds, unique_id, amount, card_number, merchant = (
            request.strip().split(",")
        )
        payments.append(
            {
                "timestamp_seconds": timestamp_seconds,
                "unique_id": unique_id,
                "amount": amount,
                "card_number": card_number,
                "merchant": merchant,
            }
        )

    payments.sort(key=lambda x: int(x["timestamp_seconds"]))
    return payments


def validate_authorization_report(requests):
    payments = parse_payments(requests)
    # report payments
    for payment in payments:
        # print(payment)
        output = f"{payment['timestamp_seconds']} {payment['unique_id']} {payment['amount']}  APPROVE"
        print(output)


def parse_rules(requests_rules):
    rules = []
    for request in requests_rules.split("\n"):
        # print(request)
        # print(request.split(","))
        timestamp_seconds, field, value = request.strip().split(",")
        rules.append(
            {
                "timestamp_seconds": timestamp_seconds,
                "field": field,
                "value": value,
            }
        )

    rules.sort(key=lambda x: int(x["timestamp_seconds"]))
    return rules


def apply_fraud_rules(requests_payments, requests_rules):
    payments = parse_payments(requests_payments)
    rules = parse_rules(requests_rules)
    # report payments
    for payment in payments:
        # check rules
        is_approved = True
        for rule in rules:
            if rule["timestamp_seconds"] > payment["timestamp_seconds"]:
                break
            field = rule["field"]
            value = rule["value"]
            if value == payment[field]:
                is_approved = False
                break

        output = (
            f"{payment['timestamp_seconds']} {payment['unique_id']} {payment['amount']}"
        )
        if is_approved:
            output += " APPROVE"
        else:
            output += " REJECT"
        print(output)


def cal_total_fraud_loss(requests_payments, requests_rules):
    payments = parse_payments(requests_payments)
    rules = parse_rules(requests_rules)

    # report payments
    total_loss = 0
    for payment in payments:
        # check rules
        for rule in rules:
            if rule["timestamp_seconds"] > payment["timestamp_seconds"]:
                field = rule["field"]
                value = rule["value"]
                if value == payment[field]:
                    total_loss += float(payment["amount"])
                    break

    print("Total Fraud Loss: ", total_loss)


if __name__ == "__main__":
    print("*****Part 1*****")
    # Edge Case 1: Basic test with unordered timestamps ✅
    data1 = """5,R1,5.60,4242424242424242,bobs_burgers
    10,R2,500.00,4242111111111111,a_corp
    3,R3,12.00,4111111111111111,coffee_shop
    7,R4,100.00,4000000000000000,hardware_store"""

    print("Edge 1:", validate_authorization_report(data1))
    # Expected:
    # ['3 R3 12.00 APPROVE', '5 R1 5.60 APPROVE', '7 R4 100.00 APPROVE', '10 R2 500.00 APPROVE']

    # Edge Case 2: Only one row ✅
    data2 = """8,R8,42.00,4012888888881881,sushi_place"""
    print("Edge 2:", validate_authorization_report(data2))
    # Expected:
    # ['8 R8 42.00 APPROVE']

    # Edge Case 1: One merchant rule applies before request ❌
    data1 = """5,R1,5.60,4242,bobs_burgers
    10,R2,100.00,4242,a_corp"""

    rules1 = """1,merchant,bobs_burgers"""
    print("*****Part 2*****")
    print("Edge 1:", apply_fraud_rules(data1, rules1))
    cal_total_fraud_loss(data1, rules1)
    # Expected:
    # ['5 R1 5.60 REJECT', '10 R2 100.00 APPROVE']
    # Total Fraud Loss:  0

    # Edge Case 2: Rule comes after request ✅
    data2 = """5,R1,5.60,4242,bobs_burgers
    10,R2,100.00,4242,a_corp"""

    rules2 = """6,merchant,bobs_burgers"""

    print("Edge 2:", apply_fraud_rules(data2, rules2))
    cal_total_fraud_loss(data2, rules2)
    # Expected:
    # ['5 R1 5.60 APPROVE', '10 R2 100.00 APPROVE']
    # Total Fraud Loss:  5.6

    # Edge Case 3: Card number becomes fraud between two requests ✅
    data3 = """10,R1,10.00,1234,a
    20,R2,20.00,1234,a
    30,R3,30.00,1234,a"""

    rules3 = """25,card_number,1234"""

    print("Edge 3:", apply_fraud_rules(data3, rules3))
    cal_total_fraud_loss(data3, rules3)
    # Expected:
    # ['10 R1 10.00 APPROVE', '20 R2 20.00 APPROVE', '30 R3 30.00 REJECT']
    # Total Fraud Loss:  30.0

    # Edge Case 4: Multiple rules for same field ✅
    data4 = """10,X1,9.00,9999,safe_store
    15,X2,9.00,8888,safe_store
    20,X3,9.00,7777,fraud_store"""

    rules4 = """12,card_number,8888
    19,merchant,fraud_store"""

    print("Edge 4:", apply_fraud_rules(data4, rules4))
    cal_total_fraud_loss(data4, rules4)
    # Expected:
    # ['10 X1 9.00 APPROVE', '15 X2 9.00 REJECT', '20 X3 9.00 REJECT']
    # Total Fraud Loss:  0
