"""
16. Business Account Data Verification (KYC) — the 地里 question bank version, 5 steps.
Frequency Medium, last asked 2026-10-04, stage: OA / tech screen / phone screen.
Prompt: see "16. KYC Verify.md".   Run: python3 validate_businesses.py
"""
import csv
import io

NUM_COLUMNS = 6           # col1 id, col2 legal name, col3 url, col4 short desc, col5 full desc, col6 products
LENGTH_MIN, LENGTH_MAX = 5, 31
BLOCKED_TERMS = ("ONLINE STORE", "ECOMMERCE", "RETAIL", "SHOP", "GENERAL MERCHANDISE")
IGNORED_WORDS = {"llc", "inc"}

# Part 5 error codes, in the order the checks run
ERROR_MISSING_FIELDS = "ERROR_MISSING_FIELDS"
ERROR_INVALID_LENGTH = "ERROR_INVALID_LENGTH"
ERROR_GENERIC_NAME = "ERROR_GENERIC_NAME"
ERROR_NAME_MISMATCH = "ERROR_NAME_MISMATCH"


def parse_rows(csv_data):
    """Skip the header and blank lines; strip every field."""
    rows = list(csv.reader(io.StringIO(csv_data.strip())))
    return [[field.strip() for field in row] for row in rows[1:] if row]


def words(text):
    """
    Whitespace split, lower-case, drop LLC / Inc.
    Trailing '.' / ',' are stripped so "Inc." also counts as Inc — the prompt only says
    "split by whitespace", so mention this to the interviewer.
    """
    out = []
    for word in text.lower().split():
        word = word.strip(".,")
        if word and word not in IGNORED_WORDS:
            out.append(word)
    return out


# ---- each check returns an error code, or None when it passes ----
def check_missing_fields(fields):                                    # Part 1
    return ERROR_MISSING_FIELDS if len(fields) != NUM_COLUMNS or not all(fields) else None


def check_length(fields):                                            # Part 2: col5, stripped
    return None if LENGTH_MIN <= len(fields[4]) <= LENGTH_MAX else ERROR_INVALID_LENGTH


def check_blocked_terms(fields):                                     # Part 3: col5 only
    full_description = fields[4].upper()
    # substring match, like the reference: "WORKSHOP" counts as "SHOP" — ask the interviewer
    return ERROR_GENERIC_NAME if any(term in full_description for term in BLOCKED_TERMS) else None


def check_name_match(fields):                                        # Part 4
    name = set(words(fields[1]))
    if not name:                                                     # e.g. the name was just "LLC"
        return ERROR_NAME_MISMATCH
    described = set(words(fields[3])) | set(words(fields[4]))       # col4 OR col5
    return None if 2 * len(name & described) >= len(name) else ERROR_NAME_MISMATCH


CHECKS = [check_missing_fields, check_length, check_blocked_terms, check_name_match]


def validate_businesses(csv_data, part=5):
    """Part k runs the first k checks (Part 5 = all four, but prints the error code)."""
    checks = CHECKS[:min(part, len(CHECKS))]
    lines = []
    for fields in parse_rows(csv_data):
        name = fields[1] if len(fields) > 1 else ""
        # the generator is lazy: we stop at the first failing check, so later checks never
        # see a row with missing columns
        error = next((code for code in (check(fields) for check in checks) if code), None)
        if error is None:
            status = "VERIFIED"
        else:
            status = error if part >= 5 else "NOT VERIFIED"
        lines.append(f"{status}: {name}".rstrip())    # empty name -> "NOT VERIFIED:" (ask about the trailing space)
    return "\n".join(lines)


# ---------------- tests: the five examples from the prompt ----------------
def test_part1():
    csv_data = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,,,Artisan coffee roasters
BIZ003,,,,,
BIZ004,Tech Solutions,techsol.io,Tech,TECH SOLUTIONS,Software consulting"""
    assert validate_businesses(csv_data, part=1) == "\n".join([
        "VERIFIED: Pawsome Pets Inc.",
        "NOT VERIFIED: Bean Bliss Coffee",
        "NOT VERIFIED:",
        "VERIFIED: Tech Solutions",
    ])


def test_part2():
    csv_data = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,Bean,Bean,Artisan coffee roasters
BIZ003,Oakridge Furniture,oakridge.com,Oak,OAKRIDGE CUSTOM WOODWORKING AND FURNITURE EMPORIUM,Custom furniture
BIZ004,Tech Solutions,techsol.io,Tech,ITCS,Software consulting"""
    assert validate_businesses(csv_data, part=2) == "\n".join([
        "VERIFIED: Pawsome Pets Inc.",
        "NOT VERIFIED: Bean Bliss Coffee",       # length 4
        "NOT VERIFIED: Oakridge Furniture",      # length 50
        "NOT VERIFIED: Tech Solutions",          # length 4
    ])


def test_part3():
    csv_data = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Global Goods Market,globalgoods.com,Global,ONLINE STORE,Various products
BIZ003,Northwest Tech,nwtech.com,NW Tech,NORTHWEST INNOVATION TECH,Technology solutions
BIZ004,Sweet Dreams,sweetdreams.com,Sweet,SWEET DREAMS CREAMERY,Ice cream shop"""
    assert validate_businesses(csv_data, part=3) == "\n".join([
        "VERIFIED: Pawsome Pets Inc.",
        "NOT VERIFIED: Global Goods Market",
        "VERIFIED: Northwest Tech",
        "VERIFIED: Sweet Dreams",                # "shop" is only in col6
    ])


def test_part4():
    csv_data = """col1,col2,col3,col4,col5,col6
BIZ001,land water,landwater.com,land,land water LLC,Environmental services
BIZ002,Acme Global Trading,acme.com,Acme,XYZ ENTERPRISES,Import export services
BIZ003,Maple Ridge Bakery,maplebakery.com,Maple,MAPLE RIDGE BAKERY LLC,Artisan baked goods
BIZ004,Innovation Labs Inc,innovlabs.com,Labs,INNOVATION RESEARCH,R&D services"""
    assert validate_businesses(csv_data, part=4) == "\n".join([
        "VERIFIED: land water",
        "NOT VERIFIED: Acme Global Trading",     # 1 of 3 words
        "VERIFIED: Maple Ridge Bakery",
        "VERIFIED: Innovation Labs Inc",         # 2 words once Inc is dropped
    ])


def test_part5():
    csv_data = """col1,col2,col3,col4,col5,col6
BIZ001,Pawsome Pets Inc.,pawsomepets.com,Pawsome,PAWSOME PETS INC,Premium pet supplies
BIZ002,Bean Bliss Coffee,beanbliss.com,,,Artisan coffee roasters
BIZ003,Short Name,short.com,Short,SHRT,Products
BIZ004,Generic Store,generic.com,Store,RETAIL,Various items
BIZ005,Mismatched Corp,mismatch.com,Wrong,DIFFERENT BUSINESS,Services"""
    assert validate_businesses(csv_data) == "\n".join([
        "VERIFIED: Pawsome Pets Inc.",
        "ERROR_MISSING_FIELDS: Bean Bliss Coffee",
        "ERROR_INVALID_LENGTH: Short Name",
        "ERROR_GENERIC_NAME: Generic Store",
        "ERROR_NAME_MISMATCH: Mismatched Corp",
    ])


def test_edges():
    header = "col1,col2,col3,col4,col5,col6\n"
    assert validate_businesses(header + "B1,Short Row,x.com") == "ERROR_MISSING_FIELDS: Short Row"
    assert validate_businesses(header + "B1,Acme,x.com,  ,ACME TOOLS,Tools") == "ERROR_MISSING_FIELDS: Acme"
    assert validate_businesses(header + "B1,Acme,x.com,Acme,ACME WORKSHOP,Tools") == "ERROR_GENERIC_NAME: Acme"
    assert validate_businesses(header + "B1,LLC,x.com,Acme,ACME TOOLS,Tools") == "ERROR_NAME_MISMATCH: LLC"
    assert validate_businesses(header + "\n\nB1,Acme,x.com,Acme,ACME TOOLS,Tools\n") == "VERIFIED: Acme"
    assert validate_businesses(header) == ""


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_part4()
    test_part5()
    test_edges()
    print("all tests passed")
