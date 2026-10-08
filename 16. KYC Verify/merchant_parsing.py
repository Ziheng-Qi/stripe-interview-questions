"""
16b. Merchant info parsing — 2026-06 Backend Engineer tech screen (PracHub). Same family as KYC.
Only the three part descriptions are public; the "key:value" string format is a reconstruction.
Run: python3 merchant_parsing.py
"""
NULL_VALUES = {"", "null", "none"}
REQUIRED = ("id", "name", "country", "description")


# Part 1: "id:m1,name:Blue Bottle,country:US,description:Coffee shop" -> dict
def parse_merchant(raw):
    merchant = {}
    for pair in raw.split(","):
        key, sep, value = pair.partition(":")       # split on the FIRST ':' only ("9:30" survives)
        if sep:
            merchant[key.strip()] = value.strip()
    return merchant


# Part 2: drop merchants with an empty / null value (description included)
def is_complete(merchant, required=REQUIRED):
    return all(merchant.get(field, "").lower() not in NULL_VALUES for field in required)


def valid_merchants(raw_list):
    return [m for m in map(parse_merchant, raw_list) if is_complete(m)]


# Part 3: match descriptions against a predetermined list (case- and whitespace-insensitive)
def normalize(text):
    return " ".join(text.lower().split())


def match_descriptions(raw_list, known_descriptions):
    lookup = {normalize(d): d for d in known_descriptions}
    out = []
    for m in valid_merchants(raw_list):
        hit = lookup.get(normalize(m["description"]))
        out.append(f"{m['id']} MATCH {hit}" if hit else f"{m['id']} NO MATCH")
    return out


# ---------------- tests ----------------
RAW = [
    "id:m1,name:Blue Bottle,country:US,description:Coffee  Shop",
    "id:m2,name:,country:US,description:Bakery",                  # empty name
    "id:m3,name:Joe's,country:null,description:Pizza",            # null country
    "id:m4,name:Gadget Hub,country:CA,description:",              # empty description
    "id:m5,name:Crypto King,country:US,description:Crypto exchange",
    "id:m6,name:Time Co,country:US,description:Opens at 9:30",
]
KNOWN = ["coffee shop", "Bakery", "Book store"]


def test():
    assert parse_merchant(RAW[0]) == {"id": "m1", "name": "Blue Bottle", "country": "US",
                                      "description": "Coffee  Shop"}
    assert parse_merchant(RAW[5])["description"] == "Opens at 9:30"
    assert [m["id"] for m in valid_merchants(RAW)] == ["m1", "m5", "m6"]
    assert match_descriptions(RAW, KNOWN) == ["m1 MATCH coffee shop", "m5 NO MATCH", "m6 NO MATCH"]
    assert match_descriptions([], KNOWN) == []


if __name__ == "__main__":
    test()
    print("all tests passed")
