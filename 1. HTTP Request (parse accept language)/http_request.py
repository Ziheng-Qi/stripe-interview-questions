import unittest


def parse_accept_language(header, supported_languages):
    """
    Parses the Accept-Language header and returns the list of supported languages
    in the order of client's preference.
    """
    # throw errors
    if not header or len(header) == 0:
        return "header is not valid"
    if not supported_languages or len(supported_languages) == 0:
        return "supported_languages is not valid"

    preferred = [lang.strip() for lang in header.split(",")]
    matched = [lang for lang in preferred if lang in supported_languages]
    return matched


def parse_accept_language_v2(header, supported_languages):
    """
    Extended Accept-Language parser to support generic tags like 'en' matching 'en-US', 'en-GB', etc.
    """
    if not header or len(header.strip()) == 0:
        return "header is not valid"
    if not supported_languages or len(supported_languages) == 0:
        return "supported_languages is not valid"

    preferred = [lang.strip() for lang in header.split(",")]
    matched = []  # list, guarantees the order and priorities
    seen = set()  # avoid adding duplicates

    for lang in preferred:
        # exact match
        if lang in supported_languages:
            if lang not in seen:
                matched.append(lang)
                seen.add(lang)
        else:
            # fuzzy match, like 'fr' matches all 'fr-*'
            for s_lang in supported_languages:
                if s_lang.startswith(lang + "-") and s_lang not in seen:
                    matched.append(s_lang)
                    seen.add(s_lang)

    return matched


from collections import OrderedDict


def parse_accept_language_ordered(header, supported_languages):
    """
    Accept-Language parser with support for:
    - exact match
    - generic match ('en' -> 'en-US', etc.)
    - wildcard '*'
    - correct preference order and demotion logic
    """
    if not header or len(header.strip()) == 0:
        return "header is not valid"
    if not supported_languages or len(supported_languages) == 0:
        return "supported_languages is not valid"

    preferred = [lang.strip() for lang in header.split(",")]

    # I used an OrderedDict to preserve insertion order
    # and allow efficient promotion/demotion of entries.
    # When a generic tag like fr matches multiple variants
    # including fr-FR, and fr-FR appears later in the header,
    # I demote it by moving it to the end. This reflects the true client preference:
    # specific entries override generic ones, even if matched earlier.
    matched = OrderedDict()

    for lang in preferred:
        if lang == "*":
            for s_lang in supported_languages:
                if s_lang not in matched:
                    matched[s_lang] = True
        elif lang in supported_languages:
            # Demote exact match if already added by generic (re-insert at end)
            if lang in matched:
                matched.move_to_end(lang)
            else:
                matched[lang] = True
        else:
            # generic fallback
            for s_lang in supported_languages:
                if s_lang.startswith(lang + "-"):
                    if s_lang in matched:
                        # Demote if it's matched again specifically later
                        matched.move_to_end(s_lang)
                    else:
                        matched[s_lang] = True

    return list(matched.keys())


import re
from collections import defaultdict


def parse_accept_language_qfactor(header, supported_languages):
    if not header or len(header.strip()) == 0:
        return "header is not valid"
    if not supported_languages or len(supported_languages) == 0:
        return "supported_languages is not valid"

    entries = []
    for item in header.split(","):
        parts = item.strip().split(";")
        lang = parts[0].strip()
        q = 1.0
        if len(parts) == 2 and parts[1].strip().startswith("q="):
            try:
                q = float(parts[1].strip()[2:])
            except ValueError:
                pass
        entries.append((lang, q))

    matched = {}  # lang -> (q, order)
    excluded = set()  # languages to ignore entirely
    added = set()
    order = 0

    for lang, q in entries:
        order += 1
        if q == 0:
            # Block listed
            if lang == "*":
                excluded.update(supported_languages)
            elif lang in supported_languages:
                excluded.add(lang)
            else:
                for s_lang in supported_languages:
                    if s_lang.startswith(lang + "-"):
                        excluded.add(s_lang)
            continue  # skip further logic for this item

        # Wildcard match
        if lang == "*":
            for s_lang in supported_languages:
                if s_lang not in excluded and s_lang not in added:
                    matched[s_lang] = (q, order)
                    added.add(s_lang)

        # Exact match
        elif lang in supported_languages:
            if lang not in excluded and lang not in added:
                matched[lang] = (q, order)
                added.add(lang)

        # Generic match
        else:
            for s_lang in supported_languages:
                if (
                    s_lang.startswith(lang + "-")
                    and s_lang not in excluded
                    and s_lang not in added
                ):
                    matched[s_lang] = (q, order)
                    added.add(s_lang)

    sorted_result = sorted(matched.items(), key=lambda x: (-x[1][0], x[1][1]))
    return [lang for lang, _ in sorted_result]


class Test(unittest.TestCase):
    def test_case_1(self):
        result = parse_accept_language("en-US, fr-CA, fr-FR", ["fr-FR", "en-US"])
        self.assertEqual(result, ["en-US", "fr-FR"])

    def test_case_2(self):
        result = parse_accept_language("fr-CA, fr-FR", ["en-US", "fr-FR"])
        self.assertEqual(result, ["fr-FR"])

    def test_case_3(self):
        result = parse_accept_language("en-US", ["en-US", "fr-CA"])
        self.assertEqual(result, ["en-US"])

    def test_case_4_no_match(self):
        result = parse_accept_language("fr-CA, de-DE", ["en-US"])
        self.assertEqual(result, [])

    def test_case_5_extra_spaces(self):
        result = parse_accept_language(" en-US , fr-CA ", ["en-US", "fr-CA"])
        self.assertEqual(result, ["en-US", "fr-CA"])

    def test_case_6_empty_header(self):
        result = parse_accept_language("", ["en-US", "fr-CA"])
        self.assertEqual(result, "header is not valid")

    def test_case_7_empty_supported_list(self):
        result = parse_accept_language("en-US, fr-CA", [])
        self.assertEqual(result, "supported_languages is not valid")


if __name__ == "__main__":
    # unittest.main()

    print("part 1")
    # Test case 1
    print(parse_accept_language("en-US, fr-CA, fr-FR", ["fr-FR", "en-US"]))
    # Expected: ['en-US', 'fr-FR']

    # Test case 2
    print(parse_accept_language("fr-CA, fr-FR", ["en-US", "fr-FR"]))
    # Expected: ['fr-FR']

    # Test case 3
    print(parse_accept_language("en-US", ["en-US", "fr-CA"]))
    # Expected: ['en-US']

    # Test case 4: No match
    print(parse_accept_language("fr-CA, de-DE", ["en-US"]))
    # Expected: []

    # Test case 5: Extra spaces
    print(parse_accept_language(" en-US , fr-CA ", ["en-US", "fr-CA"]))
    # Expected: ['en-US', 'fr-CA']

    # Test case 6: Empty header
    print(parse_accept_language("", ["en-US", "fr-CA"]))
    # Expected: "header is not valid"

    # Test case 7: Empty supported_languages list
    print(parse_accept_language("en-US, fr-CA", []))
    # Expected: "supported_languages is not valid"

    print("part 2")
    # Test case 1: generic "en" matches all en-*
    print(parse_accept_language_v2("en", ["en-US", "fr-CA", "fr-FR"]))
    # Expected: ["en-US"]

    # Test case 2: generic "fr" matches all fr-*
    print(parse_accept_language_v2("fr", ["en-US", "fr-CA", "fr-FR"]))
    # Expected: ["fr-CA", "fr-FR"]

    # Test case 3: exact + fallback
    print(parse_accept_language_v2("fr-FR, fr", ["en-US", "fr-CA", "fr-FR"]))
    # Expected: ["fr-FR", "fr-CA"]

    # Test case 4: mix generic and specific
    print(parse_accept_language_v2("en-GB, en", ["en-US", "en-GB", "fr-FR"]))
    # Expected: ["en-GB", "en-US"]

    # Test case 5: duplication prevention
    print(parse_accept_language_v2("en, en-US", ["en-US", "en-GB"]))
    # Expected: ["en-US", "en-GB"]

    # Test case 6: nothing matches
    print(parse_accept_language_v2("de", ["en-US", "fr-CA"]))
    # Expected: []

    # Test case 7: empty header
    print(parse_accept_language_v2("", ["en-US"]))
    # Expected: "header is not valid"

    print("part 3")
    # Test 1: wildcard includes remaining supported languages
    print(parse_accept_language_ordered("en-US, *", ["en-US", "fr-CA", "fr-FR"]))
    # Expected: ['en-US', 'fr-CA', 'fr-FR']

    # Test 2: wildcard after exact and generic matches
    print(parse_accept_language_ordered("fr-FR, fr, *", ["en-US", "fr-CA", "fr-FR"]))
    # Expected: ['fr-FR', 'fr-CA', 'en-US']

    # Test 3: wildcard first
    print(parse_accept_language_ordered("*, en-US", ["en-US", "fr-FR"]))
    # Expected: ['fr-FR', 'en-US']

    # Test 4: generic then exact (demote exact)
    print(parse_accept_language_ordered("fr, fr-FR", ["fr-FR", "fr-BR", "fr-CA"]))
    # Expected: ['fr-BR', 'fr-CA', 'fr-FR']

    # Test 5: exact then generic (no demotion)
    print(parse_accept_language_ordered("fr-FR, fr", ["fr-FR", "fr-BR", "fr-CA"]))
    # Expected: ['fr-FR', 'fr-BR', 'fr-CA']

    # Test 6: wildcard only
    print(parse_accept_language_ordered("*", ["en-US", "fr-FR"]))
    # Expected: ['en-US', 'fr-FR']

    # Test 7: duplicate exact and wildcard
    print(parse_accept_language_ordered("en-US, *", ["en-US", "en-GB", "fr-FR"]))
    # Expected: ['en-US', 'en-GB', 'fr-FR']

    # Test 8: empty header
    print(parse_accept_language_ordered("", ["en-US"]))
    # Expected: "header is not valid"

    # Test 9: empty supported
    print(parse_accept_language_ordered("en-US, fr", []))
    # Expected: "supported_languages is not valid"

    print("part 4")
    # Test 1
    print(
        parse_accept_language_qfactor(
            "fr-FR;q=1, fr-CA;q=0, fr;q=0.5", ["fr-FR", "fr-CA", "fr-BG"]
        )
    )
    # Expected: ["fr-FR", "fr-BG"]

    # Test 2
    print(
        parse_accept_language_qfactor(
            "fr-FR;q=1, fr-CA;q=0, *;q=0.5", ["fr-FR", "fr-CA", "fr-BG", "en-US"]
        )
    )
    # Expected: ["fr-FR", "fr-BG", "en-US"]

    # Test 3
    print(
        parse_accept_language_qfactor(
            "fr-FR;q=1, fr-CA;q=0.8, *;q=0.5", ["fr-FR", "fr-CA", "fr-BG", "en-US"]
        )
    )
    # Expected: ["fr-FR", "fr-CA", "fr-BG", "en-US"]

    # Test 4: no q specified (defaults to 1)
    print(parse_accept_language_qfactor("fr-FR, fr", ["fr-FR", "fr-BR", "fr-CA"]))
    # Expected: ['fr-FR', 'fr-BR', 'fr-CA']

    # Test 5: wildcard has higher priority than later generic
    print(parse_accept_language_qfactor("*, fr;q=0.5", ["fr-FR", "en-US"]))
    # Expected: ['fr-FR', 'en-US']

    # Test 6: q=0 makes language ignored
    print(parse_accept_language_qfactor("en-US;q=0", ["en-US", "fr-FR"]))
    # Expected: []
    # Although many developers assume languages not listed in Accept-Language
    # are implicitly accepted,
    # the actual HTTP spec (RFC 9110) treats them as rejected
    # unless * is explicitly listed.
    # So I treat missing languages as q=0 unless *;q>0 is present,
    # in which case I apply the wildcard q-factor to the rest.

    # Test 7: invalid q factor fallback
    print(parse_accept_language_qfactor("fr-FR;q=xyz, fr", ["fr-FR", "fr-CA"]))
    # Expected: ['fr-FR', 'fr-CA'] (invalid q treated as 1.0)

    # Test 8: q=0.0 but appears in wildcard
    print(parse_accept_language_qfactor("fr-CA;q=0, *;q=0.5", ["fr-CA", "fr-FR"]))
    # Expected: ['fr-FR'] (fr-CA should be excluded)
