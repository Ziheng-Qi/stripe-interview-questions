import os


def compute_penalty(log, closing_time):
    customers = log.split(" ")
    n = len(customers)
    penalty = 0
    for i in range(n):
        if i < closing_time:
            if customers[i] == "N":
                penalty += 1
        else:
            if customers[i] == "Y":
                penalty += 1

    return penalty


def find_best_closing_time(log):
    customers = log.split(" ")
    n = len(customers)
    penalty = 0
    min_penalty, min_penalty_idx = 0, 0

    for i in range(n):
        if customers[i] == "Y":
            penalty -= 1
        else:
            penalty += 1

        if min_penalty > penalty:
            min_penalty = penalty
            min_penalty_idx = i + 1

    return min_penalty_idx


def get_best_closing_times(file):
    # it is the string "\n"
    logs = []
    lines = file.split("\\n")
    for line in lines:
        for s in line.split("BEGIN"):
            i = s.find("END")
            if i != -1:
                logs.append(s[:i].strip())

    best_closing_times = [find_best_closing_time(log) for log in logs]
    return best_closing_times


def get_best_closing_times_v2(filename):
    # it is the string "\n"
    logs = []
    with open(filename, "r") as file:
        for line in file:
            print(line)
            for s in line.split("BEGIN"):
                i = s.find("END")
                if i != -1:
                    logs.append(s[:i].strip())

    print(logs)

    best_closing_times = [find_best_closing_time(log) for log in logs]
    return best_closing_times


if __name__ == "__main__":
    print("Part 1:")
    # Simple test case 1: All Y, close at 0
    print("Case 1:", compute_penalty("Y Y N Y", 0))
    # Expected: 3 (missed 3 hours with Y)

    # Simple test case 2: One N during open, one Y after closing
    print("Case 2:", compute_penalty("N Y N Y", 2))
    # Expected: 2

    # Simple test case 3: Close at end, one N while open
    print("Case 3:", compute_penalty("Y Y N Y", 4))
    # Expected: 1

    # Edge Case 1: No log, close at 0
    print("Edge 1:", compute_penalty("", 0))
    # Expected: 0

    # Edge Case 2: Close immediately, all N
    print("Edge 2:", compute_penalty("N N N N", 0))
    # Expected: 0

    # Edge Case 3: Close fully open, all Y
    print("Edge 3:", compute_penalty("Y Y Y Y", 4))
    # Expected: 0

    # Edge Case 4: Close midway with alternating pattern
    print("Edge 4:", compute_penalty("Y N Y N", 2))
    # Expected: 2 (N during open + Y during close)

    print("Part 2:")
    # Case 1: "Y Y N N" → Best time is 2
    print("Case 1:", find_best_closing_time("Y Y N N"))
    # Expected: 2

    # Case 2: All Y → Best time is 4 (open full)
    print("Case 2:", find_best_closing_time("Y Y Y Y Y"))
    # Expected: 5

    # Case 3: All N → Best time is 0 (don’t open at all)
    print("Case 3:", find_best_closing_time("N N N N N"))
    # Expected: 0

    # Case 4: Mixed, ideal is closing at 4
    print("Case 4:", find_best_closing_time("N N Y Y"))
    # Expected: 0

    # Edge Case 1: Empty log
    print("Edge 1:", find_best_closing_time(""))
    # Expected: 0

    # Edge Case 2: One hour with Y
    print("Edge 2:", find_best_closing_time("Y"))
    # Expected: 1

    # Edge Case 3: One hour with N
    print("Edge 3:", find_best_closing_time("N"))
    # Expected: 0

    # Edge Case 4: Tie in penalty, return earliest closing time
    print("Edge 4:", find_best_closing_time("Y N Y"))
    # Expected: 1

    print("Part 3:")
    # Case 1: Simple two valid blocks
    log1 = "BEGIN Y Y N N END BEGIN Y Y Y Y Y END"
    print("Case 1:", get_best_closing_times(log1))
    # Expected: [2, 5]

    # Case 2: One valid block, one all N
    log2 = "BEGIN N N N N N END"
    print("Case 2:", get_best_closing_times(log2))
    # Expected: [0]

    # Case 3: One valid block, mixed
    log3 = "BEGIN N N Y Y END"
    print("Case 3:", get_best_closing_times(log3))
    # Expected: [0]

    # Case 4: Multiple valid logs, use different penalty behavior
    log4 = "BEGIN Y END BEGIN N END BEGIN Y N Y END"
    print("Case 4:", get_best_closing_times(log4))
    # Expected: [1, 0, 1]

    # Edge Case 1: Nested BEGINs are invalid
    log5 = "BEGIN BEGIN Y N Y END END"
    print("Edge 1:", get_best_closing_times(log5))
    # Expected: [] (no valid outer BEGIN-END)

    # Edge Case 2: Missing END
    log6 = "BEGIN Y N Y"
    print("Edge 2:", get_best_closing_times(log6))
    # Expected: []

    # Edge Case 3: Mixed trash content, should still find one valid
    log7 = "FOO BEGIN Y N Y END BAR BEGIN N END"
    print("Edge 3:", get_best_closing_times(log7))
    # Expected: [1, 0]

    print("Part 4:")
    base_dir = os.path.dirname(__file__)  # current dirname
    filepath = os.path.join(base_dir, "myfile.txt")
    print("Resolved path:", filepath)
    print("File Test Case:", get_best_closing_times_v2(filepath))
    # Final expected output:
    # [2, 5, 1, 0, 0]
