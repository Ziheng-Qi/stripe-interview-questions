def parse_aid_string(s):
    aids = []
    i = 0

    while i < len(s):
        if s[i] == "0" and i == len(s) - 1:
            break
        if i + 2 > len(s):
            return "Invalid format: length prefix missing."

        try:
            length = int(s[i : i + 2])
        except ValueError:
            return "Invalid length prefix."

        i += 2
        if i + length > len(s):
            return "Invalid format: AID truncated."
        aids.append(s[i : i + length])
        i += length
    return aids


def filter_supported_aids(aid_str, supported_aids):
    parsed = parse_aid_string(aid_str)
    # print("parsed:", parsed)
    matched = [aid for aid in parsed if aid in supported_aids]
    return matched


def filter_applicable_aids(aid_str, supported_aids, supported_rids):
    parsed = parse_aid_string(aid_str)
    return [
        aid
        for aid in parsed
        if aid in supported_aids or any(aid.startswith(rid) for rid in supported_rids)
    ]


if __name__ == "__main__":
    print("Part 1")
    # Test 1: multiple AIDs
    print(parse_aid_string("18DS012345678987654310AI012345670"))
    # Expected: ['DS0123456789876543', 'AI01234567']

    # Test 2: one AID only
    print(parse_aid_string("08AIDTEST0"))
    # Expected: ['AIDTEST']

    # Test 3: empty list
    print(parse_aid_string("0"))
    # Expected: []

    # Test 4: incomplete final AID
    print(parse_aid_string("06ABC"))
    # Expected: Invalid format: AID truncated. []

    # Test 5: bad length prefix
    print(parse_aid_string("1AABCDEFG0"))
    # Expected: Invalid length prefix. []

    # Test 6: no ending 0, but valid data
    print(parse_aid_string("04TEST"))
    # Expected: ['TEST']

    print("part 2")
    # Test 1: some AIDs match
    # DS0123456789876543: length = 18
    # AI01234567: length = 10
    print(
        filter_supported_aids(
            "18DS012345678987654310AI012345670", ["DS0123456789876543"]
        )
    )
    # Expected: ['DS0123456789876543']

    # Test 2: all AIDs match (FIXED length prefix to 07 and 09)
    print(filter_supported_aids("07AIDTEST09FOOBARBAZ0", ["AIDTEST", "FOOBARBAZ"]))
    # Expected: ['AIDTEST', 'FOOBARBAZ']

    # Test 3: no match (FIXED length)
    print(filter_supported_aids("07AIDTEST09FOOBARBAZ0", ["UNSUPPORTED"]))
    # Expected: []

    # Test 4: partially match (FIXED both AIDs to have correct length)
    # 'HELLO123' = 8, 'WORLD456' = 8
    print(filter_supported_aids("08HELLO12308WORLD4560", ["WORLD456"]))
    # Expected: ['WORLD456']

    # Test 5: empty supported list
    print(filter_supported_aids("07AIDTEST0", []))
    # Expected: []

    # Test 6: empty input string
    print(filter_supported_aids("0", ["AIDTEST"]))
    # Expected: []

    print("part 3")
    # Test 1: AID in supported list
    # AID: "AI01234567" → length = 10
    print(filter_applicable_aids("10AI012345670", ["AI01234567"], []))
    # Expected: ['AI01234567']

    # Test 2: AID matches by RID only
    # AID: "AI12345678" → matches RID "AI1"
    print(filter_applicable_aids("10AI123456780", [], ["AI1"]))
    # Expected: ['AI12345678']

    # Test 3: AID matches both AID and RID list (should still be returned once)
    print(filter_applicable_aids("10AI123456780", ["AI12345678"], ["AI1"]))
    # Expected: ['AI12345678']

    # Test 4: No matches
    print(filter_applicable_aids("10ZZZ98765430", ["AIDTEST"], ["FOO"]))
    # Expected: []

    # Test 5: Mixed match — one by AID, one by RID, one not match
    # AID1: "AA11223344" (match RID "AA1")
    # AID2: "BB55667788" (match AID list)
    # AID3: "CC99887766" (no match)
    aid_input = "10AA1122334410BB5566778810CC998877660"
    supported_aids = ["BB55667788"]
    supported_rids = ["AA1"]
    print(filter_applicable_aids(aid_input, supported_aids, supported_rids))
    # Expected: ['AA11223344', 'BB55667788']
