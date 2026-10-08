"""
14. Task Tree — rebuild a task/subtask hierarchy from flat CSV records and print it as a text tree.
Prompt: see "14. Task Tree.md".   Run: python3 task_tree.py
"""
from collections import namedtuple

Task = namedtuple("Task", "task_id name timestamp parent_id line")

MIDDLE, LAST = "├─ ", "└─ "          # connector for a non-final / final child
PAD_MIDDLE, PAD_LAST = "│  ", "   "  # indentation under a non-final / final ancestor


# ---------------- Part 1: parse records -> roots + parent->children ----------------
def parse_records(text):
    """
    Returns (tasks, errors). tasks: task_id -> Task.
      Root:    timestamp,task,task_id,task_name
      Subtask: timestamp,subtask,parent_id,task_id,task_name
    Does NOT assume a parent's record comes before its children.
    """
    tasks, errors = {}, []
    for line_no, raw in enumerate(text.strip().splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        fields = [f.strip() for f in line.split(",")]
        kind = fields[1] if len(fields) > 1 else ""
        if kind == "task" and len(fields) == 4:
            ts, _, task_id, name = fields
            parent_id = None
        elif kind == "subtask" and len(fields) == 5:
            ts, _, parent_id, task_id, name = fields
        else:
            errors.append(f"line {line_no}: malformed record {line!r}")
            continue
        if not ts.isdigit():
            errors.append(f"line {line_no}: bad timestamp {ts!r}")
            continue
        if task_id in tasks:
            errors.append(f"line {line_no}: duplicate task_id {task_id}, ignored")
            continue
        tasks[task_id] = Task(task_id, name, int(ts), parent_id, line_no)
    return tasks, errors


def build_tree(tasks):
    """
    Returns (roots, children). Roots and every sibling list are ordered by
    (timestamp, input line). Timestamps are ints here: as strings "10" < "9".
    """
    children = {task_id: [] for task_id in tasks}
    roots = []
    for task in sorted(tasks.values(), key=lambda t: (t.timestamp, t.line)):
        if task.parent_id is None:
            roots.append(task.task_id)
        elif task.parent_id in tasks:
            children[task.parent_id].append(task.task_id)
    return roots, children


def parse_hierarchy(text):
    """Part 1 answer: (root ids, {task_id: [child ids]})."""
    tasks, _ = parse_records(text)
    return build_tree(tasks)


# ---------------- Part 2: render with ├─ / └─ ----------------
def render_subtree(tasks, children, root_id):
    """
    Lines for root_id and everything under it (root printed without a connector).
    Iterative DFS with an explicit stack: a very deep chain won't hit the recursion limit.
    """
    lines = [tasks[root_id].name]
    stack, seen = [], {root_id}

    def push_children(task_id, prefix):
        kids = children[task_id]
        for i in range(len(kids) - 1, -1, -1):            # push reversed -> pop in order
            stack.append((kids[i], prefix, i == len(kids) - 1))

    push_children(root_id, "")
    while stack:
        task_id, prefix, is_last = stack.pop()
        connector = LAST if is_last else MIDDLE
        if task_id in seen:                                 # only possible through a cycle
            lines.append(prefix + connector + tasks[task_id].name + " (cycle)")
            continue
        seen.add(task_id)
        lines.append(prefix + connector + tasks[task_id].name)
        push_children(task_id, prefix + (PAD_LAST if is_last else PAD_MIDDLE))
    return lines


def render(text):
    """Part 2 answer: every root tree, roots in timestamp order."""
    tasks, _ = parse_records(text)
    roots, children = build_tree(tasks)
    lines = []
    for root_id in roots:
        lines.extend(render_subtree(tasks, children, root_id))
    return "\n".join(lines)


# ---------------- Part 3: messy input -> also report problems ----------------
def find_problems(tasks):
    """Orphans (parent never appears) and cycles in the parent links."""
    problems = []
    for task in tasks.values():
        if task.parent_id is not None and task.parent_id not in tasks:
            problems.append(f"orphan: {task.task_id} (parent {task.parent_id} not found)")

    done = set()
    for start in tasks:
        path, index = [], {}
        cur = start
        while cur in tasks and cur not in done and cur not in index:
            index[cur] = len(path)
            path.append(cur)
            cur = tasks[cur].parent_id                    # None for a root -> loop ends
        if cur in index:                                  # walked back onto our own path
            cycle = path[index[cur]:] + [cur]
            problems.append("cycle: " + " -> ".join(cycle))
        done.update(path)
    return problems


def render_with_report(text):
    """Part 3 answer: (tree text, problems). Orphans / cycles are reported, not rendered."""
    tasks, problems = parse_records(text)
    problems += find_problems(tasks)
    roots, children = build_tree(tasks)
    lines = []
    for root_id in roots:
        lines.extend(render_subtree(tasks, children, root_id))
    return "\n".join(lines), problems


# ---------------- Part 4: render only one subtree ----------------
def render_from(text, task_id):
    tasks, _ = parse_records(text)
    _, children = build_tree(tasks)
    if task_id not in tasks:
        raise KeyError(f"unknown task_id {task_id}")
    return "\n".join(render_subtree(tasks, children, task_id))


# ---------------- tests ----------------
SAMPLE = """
3,subtask,T2,T4,Write spec
1,task,T1,Launch checkout
5,subtask,T1,T3,Build UI
2,subtask,T1,T2,Design API
4,task,T5,Fraud review
6,subtask,T5,T6,Check rules
7,subtask,T6,T7,Notify team
"""

MESSY = """
1,task,T1,Launch checkout
2,subtask,T1,T2,Design API
oops this line is broken
x,task,T9,Bad timestamp
3,subtask,T404,T3,Lost child
4,subtask,T5,T4,Loop A
5,subtask,T4,T5,Loop B
6,subtask,T1,T2,Duplicate id
"""


def test_part1():
    roots, children = parse_hierarchy(SAMPLE)
    assert roots == ["T1", "T5"]
    assert children["T1"] == ["T2", "T3"]            # T2 (ts=2) before T3 (ts=5)
    assert children["T2"] == ["T4"]                  # child's line came before its parent's
    assert children["T5"] == ["T6"] and children["T6"] == ["T7"]
    assert children["T3"] == [] and children["T4"] == []


def test_part2():
    expected = "\n".join([
        "Launch checkout",
        "├─ Design API",
        "│  └─ Write spec",
        "└─ Build UI",
        "Fraud review",
        "└─ Check rules",
        "   └─ Notify team",
    ])
    assert render(SAMPLE) == expected, "\n" + render(SAMPLE)
    assert render("") == ""
    assert render("1,task,A,Only root") == "Only root"
    # same timestamp -> input order
    assert render("1,task,R,Root\n2,subtask,R,B,b\n2,subtask,R,A,a") == "Root\n├─ b\n└─ a"
    # timestamps compare as numbers: 9 before 10
    assert render("1,task,R,Root\n10,subtask,R,X,ten\n9,subtask,R,Y,nine") == "Root\n├─ nine\n└─ ten"


def test_part3():
    tree, problems = render_with_report(MESSY)
    assert tree == "Launch checkout\n└─ Design API"
    assert "line 3: malformed record 'oops this line is broken'" in problems
    assert "line 4: bad timestamp 'x'" in problems
    assert "line 8: duplicate task_id T2, ignored" in problems
    assert "orphan: T3 (parent T404 not found)" in problems
    assert "cycle: T4 -> T5 -> T4" in problems
    assert len(problems) == 5, problems


def test_part4():
    assert render_from(SAMPLE, "T2") == "Design API\n└─ Write spec"
    assert render_from(SAMPLE, "T5") == "Fraud review\n└─ Check rules\n   └─ Notify team"
    assert render_from(MESSY, "T4") == "Loop A\n└─ Loop B\n   └─ Loop A (cycle)"


def test_deep_chain():
    lines = ["0,task,N0,n0"] + [f"{i},subtask,N{i - 1},N{i},n{i}" for i in range(1, 2001)]
    out = render("\n".join(lines)).splitlines()
    assert len(out) == 2001 and out[-1].endswith("└─ n2000")


if __name__ == "__main__":
    test_part1()
    test_part2()
    test_part3()
    test_part4()
    test_deep_chain()
    print(render(SAMPLE))
    print("all tests passed")
