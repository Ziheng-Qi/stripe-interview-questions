"""
1. Backtracking + Pruning

Key idea
    •	Convert transactions into a list balance_list of net balances (positive = should receive, negative = should pay).
    •	Define dfs(cur) to settle person cur’s balance, then recursively settle cur+1, cur+2, ….
    •	For balance_list[cur] ≠ 0, try pairing it with any later person nxt who has an opposite‐sign balance:
        1.	“Transfer” balance_list[cur] to balance_list[nxt] (i.e. balance_list[nxt] += balance_list[cur]).
        2.	Recurse with dfs(cur+1) and add 1 transaction.
        3.	Undo the change (backtrack).
    •	Keep track of the minimum transactions over all such choices.
    •	Pruning tricks:
    •	Skip any cur whose balance is already zero.
    •	Only pair if balance[cur] * balance[nxt] < 0 (opposite signs).
    •	Early exit if you reach the theoretical minimum (e.g. 1) at any level.

    dfs(cur):
        while cur < n and balance[cur] == 0:
            cur += 1
        if cur == n:
            return 0

        ans = ∞
        for nxt in range(cur+1, n):
            if balance[cur] * balance[nxt] < 0:
                balance[nxt] += balance[cur]
                ans = min(ans, 1 + dfs(cur+1))
                balance[nxt] -= balance[cur]
        return ans

    •	Time: worst‐case O(n!), but heavy pruning allows around n\le12.
    •	Space: O(n) recursion depth.

2. Bitmask DP + Memoization

Key idea
    •	Still build balance_list of length n (nonzero balances).
    •	Observe: any group of m people whose balances sum to zero can settle themselves in m-1 transactions.
    •	So if we can partition all n people into k disjoint zero-sum groups, total transactions = n - k.
    •	Define a DP on subsets: let dfs(mask) = maximum number of zero-sum groups that can be formed from people in mask (a bitmask of size n).
    •	To compute dfs(mask):
        1.	Enumerate removing one person i from mask, and take the max of dfs(mask ^ (1<<i)).
        2.	Compute the sum of balances in mask; if it’s zero, add 1 (the entire mask can be one more group).
    •	Cache results in memo[mask] to avoid recomputation.

    memo[0] = 0

    def dfs(mask):
        if memo[mask] ≠ -1:
            return memo[mask]

        s = 0
        max_groups = 0
        for i in bits_set_in(mask):
            s += balance_list[i]
            max_groups = max(max_groups, dfs(mask without i))

        memo[mask] = max_groups + (1 if s == 0 else 0)
        return memo[mask]

    full_mask = (1<<n) - 1
    max_zero_groups = dfs(full_mask)
    return n - max_zero_groups

    •	Time: O(n \times 2^n)
        •	Space: O(2^n) for memo.
"""
