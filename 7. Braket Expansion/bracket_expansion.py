"""
7. Bracket expansion — "/2022/{jan,feb,march}/report" -> one string per option.
Prompt: see "7. Braket Expansion.md". Part 3 is LeetCode 1087 (several brace groups, no nesting).
Run: python3 bracket_expansion.py
"""
from itertools import product


def tokenize(s):
    """
    'a{b,c}d' -> [['a'], ['b', 'c'], ['d']]; returns None for an invalid expression:
    '}' before any '{', '{' never closed, nested braces, or a group with fewer than two
    non-empty tokens ('{mid}', '{}', '{a,}').
    """
    parts, literal, i = [], [], 0
    while i < len(s):
        ch = s[i]
        if ch == "}":
            return None
        if ch == "{":
            close = s.find("}", i + 1)
            if close == -1 or "{" in s[i + 1:close]:
                return None
            options = s[i + 1:close].split(",")
            if len(options) < 2 or any(opt == "" for opt in options):
                return None
            if literal:
                parts.append(["".join(literal)])
                literal = []
            parts.append(options)
            i = close + 1
            continue
        literal.append(ch)
        i += 1
    if literal:
        parts.append(["".join(literal)])
    return parts


def expand(s, sort=False):
    """Parts 1-3. Invalid input comes back unchanged (Part 2). sort=True gives LC 1087's lexicographic order."""
    parts = tokenize(s)
    if parts is None:
        return [s]
    words = ["".join(combo) for combo in product(*parts)]
    return sorted(words) if sort else words


# ---------------- tests ----------------
def test_part1():
    assert expand("/2022/{jan,feb,march}/report") == [
        "/2022/jan/report", "/2022/feb/report", "/2022/march/report"]
    assert expand("{a,b}") == ["a", "b"]
    assert expand("no braces") == ["no braces"]


def test_part2_invalid_returns_input():
    for s in ["pre{mid}suf", "pre{}suf", "pre{a,b", "pre}a,b{", "x}{a,b}", "a{b,{c,d}}", "a{b,}c"]:
        assert expand(s) == [s], s


def test_part3_multiple_groups():
    assert expand("{a,b}c{d,e}f") == ["acdf", "acef", "bcdf", "bcef"]          # LC 1087 example
    assert expand("{b,a}x{d,c}", sort=True) == ["axc", "axd", "bxc", "bxd"]
    assert expand("{a,b}{a,b}") == ["aa", "ab", "ba", "bb"]
    assert expand("") == [""]


if __name__ == "__main__":
    test_part1()
    test_part2_invalid_returns_input()
    test_part3_multiple_groups()
    print("all tests passed")
