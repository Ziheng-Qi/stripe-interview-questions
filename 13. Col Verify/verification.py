def parse_csv(data: str) -> list[list[str]]:
    """
    Parses the CSV string into a list of rows (excluding header),
    each row is a list of strings.
    """
    lines = data.strip().split("\n")
    return [line.split(",") for line in lines[1:]]  # Skip header


def rule_non_empty(row: list[str], expected_len: int) -> bool:
    return len(row) == expected_len and all(cell.strip() != "" for cell in row)


def rule_col5_len(row):
    return len(row[4]) >= 5 and len(row[4]) <= 31


def rule_col2_no_keywords(row, keywords):
    col2_words_set = set(word.lower() for word in row[1].strip().split())
    # print(col2_words_set)
    keywords_set = set(k.lower() for k in keywords)
    for k in keywords:
        if keywords_set & col2_words_set:
            return False

    return True


def rule_col2_word_match(row):
    col2, col4, col5 = row[1], row[3], row[4]

    def tokenize(s: str) -> set[str]:
        ignore = {"llc", "inc"}
        return set(
            word.lower() for word in s.strip().split() if word.lower() not in ignore
        )

    w1 = tokenize(col2)
    if not w1:
        return False

    w4 = tokenize(col4)
    w5 = tokenize(col5)

    def match_rate(w_target: set[str]) -> float:
        return len(w1 & w_target) / len(w1)

    return match_rate(w4) >= 0.5 or match_rate(w5) >= 0.5


def validate_rows(data: str) -> list[str]:
    header = data.strip().split("\n")[0].split(",")
    expected_len = len(header)
    rows = parse_csv(data)
    results = []

    for row in rows:
        if not rule_non_empty(row, expected_len):
            results.append(f"NOT VERIFIED: {row[1]}")
            continue

        if not rule_col5_len(row):
            results.append(f"NOT VERIFIED: {row[1]}")
            continue

        if not rule_col2_no_keywords(row, ["company", "firm"]):
            results.append(f"NOT VERIFIED: {row[1]}")
            continue

        if not rule_col2_word_match(row):
            results.append(f"NOT VERIFIED: {row[1]}")
            continue

        # following rules：
        # if not rule_col5_length(row[4]): ...
        # if not rule_no_forbidden_words(row[1]): ...
        # if not rule_word_match(row[1], row[4], row[5]): ...

        results.append(f"VERIFIED: {row[1]}")

    for result in results:
        print(result)


def is_empty(string):
    rows = string.split("\n")
    n = len(rows) - 1
    m = len(rows[0].split(","))
    input_data = parse_csv(string)
    is_row_empty = [False] * n
    for i in range(n):
        curr_row = rows[i + 1].split(",")
        for j in range(m):
            if curr_row[j]:
                input_data[j][i] += curr_row[j]
            else:
                is_row_empty[i] = True

    # print col2
    for i in range(n):
        if not is_row_empty[i]:
            print("VERIFIED:", input_data[1][i])
        else:
            print("NOT VERIFIED:", input_data[1][i])


if __name__ == "__main__":

    data = "col1,col2,col3,col4,col5,col6\na,land water,c,d,land water LLC,f\na,Good Company,c,d,land water,f\na,b,c,d,e,f\n1,2,3,,5,6"
    validate_rows(data)

    # Edge Case 1: All rules pass ✅
    data1 = "col1,col2,col3,col4,col5,col6\na,hello world,c,d,hello world LLC,f"
    print("Edge 1:", validate_rows(data1))
    # Expected: ['VERIFIED: hello world']

    # Edge Case 2: Rule 1 - Empty field ❌
    data2 = "col1,col2,col3,col4,col5,col6\na,b,c,,e,f"
    print("Edge 2:", validate_rows(data2))
    # Expected: ['NOT VERIFIED: b']

    # Edge Case 3: Rule 2 - col5 too short ❌
    data3 = "col1,col2,col3,col4,col5,col6\na,b,c,d,x,f"
    print("Edge 3:", validate_rows(data3))
    # Expected: ['NOT VERIFIED: b']

    # Edge Case 4: Rule 2 - col5 too long ❌
    data4 = "col1,col2,col3,col4,col5,col6\na,b,c,d,xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx,f"
    print("Edge 4:", validate_rows(data4))
    # Expected: ['NOT VERIFIED: b']

    # Edge Case 5: Rule 3 - col2 contains forbidden word ❌
    data5 = "col1,col2,col3,col4,col5,col6\na,Best Company,c,d,Somewhere LLC,f"
    print("Edge 5:", validate_rows(data5))
    # Expected: ['NOT VERIFIED: Best Company']

    # Edge Case 6: Rule 4 - No word match ❌
    data6 = "col1,col2,col3,col4,col5,col6\na,sky blue ocean,c,d,green yellow pink,f"
    print("Edge 6:", validate_rows(data6))
    # Expected: ['NOT VERIFIED: sky blue ocean']

    # Edge Case 7: Rule 4 - Exactly 50% match ✅
    data7 = "col1,col2,col3,col4,col5,col6\na,apple banana,c,d,banana orange,f"
    print("Edge 7:", validate_rows(data7))
    # Expected: ['VERIFIED: apple banana']

    # Edge Case 8: Rule 3 borderline word ✅
    data8 = "col1,col2,col3,col4,col5,col6\na,Companyish Name,c,d,Companyish land,f"
    print("Edge 8:", validate_rows(data8))
    # Expected: ['VERIFIED: Companyish Name']

    # Edge Case 9: Rule 4 - Only LLC/Inc in col2 ❌
    data9 = "col1,col2,col3,col4,col5,col6\na,LLC Inc,c,d,something real,f"
    print("Edge 9:", validate_rows(data9))
    # Expected: ['NOT VERIFIED: LLC Inc']

    # Edge Case 10: Combo - Valid match of 2/3 words ✅
    data10 = "col1,col2,col3,col4,col5,col6\na,land water stone,c,d,land water LLC,f"
    print("Edge 10:", validate_rows(data10))
    # Expected: ['VERIFIED: land water stone']
