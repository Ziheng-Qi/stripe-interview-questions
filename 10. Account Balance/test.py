import unittest
from account_balance import Solution  # 假设你的解在 solution.py 里


class TestMinTransfers(unittest.TestCase):
    def setUp(self):
        self.sol = Solution()

    def test_empty(self):
        self.assertEqual(self.sol.minTransfers([]), 0)

    def test_self_cancel(self):
        tx = [[0, 1, 10], [1, 2, 10], [2, 0, 10]]
        self.assertEqual(self.sol.minTransfers(tx), 0)

    def test_single(self):
        self.assertEqual(self.sol.minTransfers([[0, 1, 5]]), 1)

    def test_two_independent_pairs(self):
        tx = [[0, 1, 5], [2, 3, 5]]
        self.assertEqual(self.sol.minTransfers(tx), 2)

    def test_chain_debt(self):
        tx = [[0, 1, 10], [1, 2, 5]]
        # balances = [+10,+5,−15] -> 2 transfers
        self.assertEqual(self.sol.minTransfers(tx), 2)

    def test_middle_zero(self):
        tx = [[0, 1, 5], [1, 2, 5]]
        # balances = [+5,0,−5] -> direct 2->0
        self.assertEqual(self.sol.minTransfers(tx), 1)

    def test_mixed_small(self):
        # 4 people, random debts
        tx = [[0, 1, 7], [2, 3, 4], [1, 2, 3], [3, 0, 2]]
        # net = [7-2, 7-3, 3-4, 4-2] = [5,4,-1,2]
        # one optimal: 2->1:1, 2->0:4, 3->0:2, 共 3 笔
        self.assertEqual(self.sol.minTransfers(tx), 3)


if __name__ == "__main__":
    unittest.main()
