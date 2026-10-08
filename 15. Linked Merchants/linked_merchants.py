"""
15. Linked Merchants / New Matching Contacts — weighted field matching + graph reachability.
Prompt: see "15. Linked Merchants.md".   Run: python3 linked_merchants.py
"""
import csv
import io
from collections import deque

EPS = 1e-9   # 0.7 + 0.1 == 0.7999999999999999 in floating point


def parse_records(csv_text):
    """CSV with a header row -> list of dicts, input order kept, values stripped."""
    reader = csv.DictReader(io.StringIO(csv_text.strip()))
    return [{key.strip(): (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader]


def normalize(value):
    return (value or "").strip().lower()


# ---------------- Part 1: direct matches ----------------
def match_score(a, b, weights):
    """Sum of the weights of the fields where both records have the same non-empty value."""
    score = 0.0
    for field, weight in weights.items():
        va, vb = normalize(a.get(field)), normalize(b.get(field))
        if va and va == vb:                 # two empty values are NOT a match
            score += weight
    return score


def is_match(a, b, weights, threshold):
    return match_score(a, b, weights) + EPS >= threshold


def direct_matches(records, weights, threshold, target_id):
    by_id = {r["id"]: r for r in records}
    target = by_id[target_id]
    return [r["id"] for r in records
            if r["id"] != target_id and is_match(target, r, weights, threshold)]


# ---------------- Part 2 / Part 3: follow the links ----------------
def build_graph(records, weights, threshold):
    """Adjacency list. Pairwise comparison: O(n^2 * fields) — fine for interview-sized input."""
    graph = {r["id"]: [] for r in records}
    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            if is_match(records[i], records[j], weights, threshold):
                graph[records[i]["id"]].append(records[j]["id"])
                graph[records[j]["id"]].append(records[i]["id"])
    return graph


def linked_records(records, weights, threshold, target_id, max_hops=None):
    """
    BFS from the target.
      max_hops=1    -> Part 1 (direct matches)
      max_hops=2    -> Part 2 (one extra hop)
      max_hops=None -> Part 3 (the whole connected component)
    Result is in input order and excludes the target itself.
    """
    graph = build_graph(records, weights, threshold)
    if target_id not in graph:
        raise KeyError(f"unknown id {target_id}")
    dist = {target_id: 0}
    queue = deque([target_id])
    while queue:
        cur = queue.popleft()
        if max_hops is not None and dist[cur] == max_hops:
            continue
        for nxt in graph[cur]:
            if nxt not in dist:
                dist[nxt] = dist[cur] + 1
                queue.append(nxt)
    return [r["id"] for r in records if r["id"] in dist and r["id"] != target_id]


# ---------------- Extra: group everyone (union-find) ----------------
def all_groups(records, weights, threshold):
    parent = {r["id"]: r["id"] for r in records}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path halving
            x = parent[x]
        return x

    for i in range(len(records)):
        for j in range(i + 1, len(records)):
            if is_match(records[i], records[j], weights, threshold):
                parent[find(records[j]["id"])] = find(records[i]["id"])
    groups = {}
    for r in records:
        groups.setdefault(find(r["id"]), []).append(r["id"])
    return list(groups.values())


# ---------------- tests ----------------
SAMPLE = """
id,name,email,company
1,Alice,alice@x.com,Stripe
2,Alicia,alice@x.com,Stripe
3,Alice,al@y.com,Google
4,Bob,bob@z.com,Stripe
5,Alicia,ali@w.com,Stripe
6,Al,ali@w.com,Square
"""
WEIGHTS = {"name": 0.2, "email": 0.5, "company": 0.3}
THRESHOLD = 0.5


def test_score():
    r = parse_records(SAMPLE)
    assert abs(match_score(r[0], r[1], WEIGHTS) - 0.8) < 1e-9     # email + company
    assert abs(match_score(r[0], r[2], WEIGHTS) - 0.2) < 1e-9     # name only
    assert match_score({"email": ""}, {"email": ""}, {"email": 1.0}) == 0
    assert match_score({"name": " ALICE "}, {"name": "alice"}, {"name": 1.0}) == 1.0


def test_parts():
    r = parse_records(SAMPLE)
    assert direct_matches(r, WEIGHTS, THRESHOLD, "1") == ["2"]
    assert linked_records(r, WEIGHTS, THRESHOLD, "1", max_hops=1) == ["2"]
    assert linked_records(r, WEIGHTS, THRESHOLD, "1", max_hops=2) == ["2", "5"]
    assert linked_records(r, WEIGHTS, THRESHOLD, "1") == ["2", "5", "6"]
    assert linked_records(r, WEIGHTS, THRESHOLD, "4") == []
    assert all_groups(r, WEIGHTS, THRESHOLD) == [["1", "2", "5", "6"], ["3"], ["4"]]


def test_float_threshold():
    weights = {"name": 0.7, "email": 0.1, "company": 0.2}
    a = {"id": "a", "name": "x", "email": "e", "company": "c1"}
    b = {"id": "b", "name": "x", "email": "e", "company": "c2"}
    assert (0.7 + 0.1 >= 0.8) is False            # the trap
    assert is_match(a, b, weights, 0.8)            # EPS fixes it


if __name__ == "__main__":
    test_score()
    test_parts()
    test_float_threshold()
    print("all tests passed")
