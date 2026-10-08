def parse_conversion_rates(rates_str):
    if not rates_str:
        return "Error: empty input string"

    rate_map = {}
    for entry in rates_str.split(","):
        parts = entry.split(":")
        if len(parts) != 3:
            return f"Error: malformed entry '{entry}'"

        from_curr, to_curr, rate_str = parts
        try:
            rate = float(rate_str)
        except ValueError:
            return f"Error: invalid rate value '{rate_str}' in '{entry}'"

        if rate <= 0:
            return f"Error: non-positive rate '{rate}' in '{entry}'"

        if from_curr not in rate_map:
            rate_map[from_curr] = []
        rate_map[from_curr].append((to_curr, rate))
    return rate_map


def get_direct_conversion_rate(rates_str, from_currency, to_currency):
    parsed = parse_conversion_rates(rates_str)
    if isinstance(parsed, str):  # error message
        return parsed

    for to_curr, rate in parsed.get(from_currency, []):
        if to_curr == to_currency:
            return rate

    return "Error: direct conversion not found"


def get_single_hop_conversion_rate(rates_str, from_currency, to_currency):
    parsed = parse_conversion_rates(rates_str)
    if isinstance(parsed, str):
        return parsed

    rates = []

    # 1. Direct conversion
    for to_curr, rate in parsed.get(from_currency, []):
        if to_curr == to_currency:
            rates.append(rate)

    # 2. One-hop conversion
    for mid_curr, rate1 in parsed.get(from_currency, []):
        for to_curr2, rate2 in parsed.get(mid_curr, []):
            if to_curr2 == to_currency:
                rates.append(rate1 * rate2)

    return sorted(rates) if rates else "Error: no single-hop conversion found"


def get_best_conversion_rate(rates_str, from_currency, to_currency):
    parsed = parse_conversion_rates(rates_str)
    if isinstance(parsed, str):
        return parsed

    visited = set()
    max_rate = [0.0]

    def dfs(curr, acc):
        if curr == to_currency:
            max_rate[0] = max(max_rate[0], acc)
            return
        visited.add(curr)
        for neighbor, rate in parsed.get(curr, []):
            if neighbor not in visited:
                dfs(neighbor, acc * rate)
        visited.remove(curr)

    dfs(from_currency, 1.0)

    return max_rate[0] if max_rate[0] > 0 else "Error: no conversion path found"


if __name__ == "__main__":
    print("Part 1")
    # Test 1: basic conversion
    print(
        get_direct_conversion_rate("AUD:USD:0.7,AUD:JPY:100,USD:CAD:1.2", "AUD", "USD")
    )
    # Expected: 0.7

    # Test 2: direct conversion not found
    print(
        get_direct_conversion_rate("AUD:USD:0.7,AUD:JPY:100,USD:CAD:1.2", "AUD", "CAD")
    )
    # Expected: Error: direct conversion not found

    # Test 3: empty string
    print(get_direct_conversion_rate("", "AUD", "USD"))
    # Expected: Error: empty input string

    # Test 4: invalid rate format
    print(get_direct_conversion_rate("AUD:USD:abc", "AUD", "USD"))
    # Expected: Error: invalid rate value 'abc' in 'AUD:USD:abc'

    # Test 5: malformed entry
    print(get_direct_conversion_rate("AUD:USD:0.7,AUDJPY100", "AUD", "JPY"))
    # Expected: Error: malformed entry 'AUDJPY100'

    # Test 6: case sensitive currency mismatch
    print(get_direct_conversion_rate("aud:usd:0.7", "AUD", "USD"))
    # Expected: Error: direct conversion not found

    print("Part 2")
    # Test 1: direct only
    print(get_single_hop_conversion_rate("AUD:USD:0.7,USD:CAD:1.2", "AUD", "USD"))
    # Expected: [0.7]

    # Test 2: direct and one-hop (AUD->USD->CAD)
    print(
        get_single_hop_conversion_rate(
            "AUD:CAD:0.75,AUD:USD:0.7,USD:CAD:1.2", "AUD", "CAD"
        )
    )
    # Expected: [0.75, 0.84]

    # Test 3: multiple one-hop paths (AUD->EUR->CAD, AUD->USD->CAD)
    print(
        get_single_hop_conversion_rate(
            "AUD:USD:0.7,AUD:EUR:0.6,USD:CAD:1.2,EUR:CAD:1.5", "AUD", "CAD"
        )
    )
    # Expected: [0.84, 0.9]

    # Test 4: no direct or one-hop path
    print(get_single_hop_conversion_rate("AUD:JPY:100,USD:CAD:1.2", "AUD", "CAD"))
    # Expected: Error: no single-hop conversion found

    # Test 5: empty input
    print(get_single_hop_conversion_rate("", "AUD", "USD"))
    # Expected: Error: empty input string

    # Test 6: malformed entry
    print(get_single_hop_conversion_rate("AUD:USD:0.7,AUDJPY100", "AUD", "CAD"))
    # Expected: Error: malformed entry 'AUDJPY100'

    # Test 7: invalid rate
    print(get_single_hop_conversion_rate("AUD:USD:abc", "AUD", "USD"))
    # Expected: Error: invalid rate value 'abc' in 'AUD:USD:abc'

    # Test 8: case-sensitive mismatch
    print(get_single_hop_conversion_rate("aud:usd:0.7,usd:cad:1.2", "AUD", "CAD"))
    # Expected: Error: no single-hop conversion found

    print("Part 3")
    # Test 1: direct only
    print(get_best_conversion_rate("AUD:USD:0.7", "AUD", "USD"))
    # Expected: 0.7

    # Test 2: two paths, pick better one (AUD->EUR->CAD is better than AUD->USD->CAD)
    print(
        round(
            get_best_conversion_rate(
                "AUD:USD:0.7,AUD:EUR:0.6,USD:CAD:1.2,EUR:CAD:1.5", "AUD", "CAD"
            ),
            2,
        )
    )
    # Expected: 0.9
    # I noticed that floating-point operations like 0.6 * 1.5
    # may result in values like 0.8999999 due to precision issues.
    # Would you like me to round the result for readability,
    # or should I keep the raw float value to preserve accuracy?

    # Test 3: longer path, more hops
    print(get_best_conversion_rate("A:B:2,B:C:2,C:D:2,A:D:5", "A", "D"))
    # Expected: 8.0 (via A→B→C→D)

    # Test 4: cycle present but not used
    print(get_best_conversion_rate("A:B:2,B:C:2,C:A:0.5,C:D:3", "A", "D"))
    # Expected: 12.0 (A→B→C→D)

    # Test 5: empty input
    print(get_best_conversion_rate("", "AUD", "USD"))
    # Expected: Error: empty input string

    # Test 6: malformed input
    print(get_best_conversion_rate("AUD:USD:0.7,AUDUSD1", "AUD", "USD"))
    # Expected: Error: malformed entry 'AUDUSD1'

    # Test 7: invalid rate
    print(get_best_conversion_rate("AUD:USD:abc", "AUD", "USD"))
    # Expected: Error: invalid rate value 'abc' in 'AUD:USD:abc'

    # Test 8: unreachable target
    print(get_best_conversion_rate("AUD:USD:0.7", "AUD", "CAD"))
    # Expected: Error: no conversion path found

    # Test 9: case-sensitive failure
    print(get_best_conversion_rate("aud:usd:0.7,usd:cad:1.2", "AUD", "CAD"))
    # Expected: Error: no conversion path found

    # Test 10: zero rate
    print(get_best_conversion_rate("AUD:USD:0", "AUD", "USD"))
    # Expected: Error: non-positive rate '0.0' in 'AUD:USD:0'

    # Test 11: negative rate
    print(get_best_conversion_rate("AUD:USD:-1.2", "AUD", "USD"))
    # Expected: Error: non-positive rate '-1.2' in 'AUD:USD:-1.2'

    print("Part 4")
