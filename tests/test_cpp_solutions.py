"""Every C++ solution is compiled and run against real cases.

The source compiled is the exact string the student is asked to type — read
out of the bank rather than a copy kept beside it, because a copy is how a
solution stops being the one that was verified.

It goes through the app's own runner, not a hand-rolled compile. That
distinction has already mattered once: the Rust bank was checked by hand with
a different language edition than the runner used, and a solution that passed
by hand failed for the student.

One compile per pattern: the preamble, all eight solutions, and a block of
assertions in a single program.
"""

from __future__ import annotations

import unittest

from code_coach.engine import msvc_available, run_code
from code_coach.leetcode.problems_cpp import PATTERNS

import shutil

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_CPP = any(shutil.which(c) for c in ("g++", "clang++")) or msvc_available()

CHECKS = {
    "lc-hashmap": """
        vector<int> a = {2, 7, 11, 15};
        check(twoSum(a, 9) == vector<int>({0, 1}), "twoSum basic");
        vector<int> b = {3, 2, 4};
        check(twoSum(b, 6) == vector<int>({1, 2}), "twoSum not-first");
        vector<int> c = {1, 2};
        check(twoSum(c, 99).empty(), "twoSum no answer");
        vector<int> dup = {1, 2, 3, 1};
        check(containsDuplicate(dup), "containsDuplicate yes");
        vector<int> uniq = {1, 2, 3};
        check(!containsDuplicate(uniq), "containsDuplicate no");
        check(isAnagram("anagram", "nagaram"), "isAnagram yes");
        check(!isAnagram("rat", "car"), "isAnagram no");
        check(!isAnagram("a", "ab"), "isAnagram length");
        vector<string> words = {"eat", "tea", "tan", "ate", "nat", "bat"};
        auto groups = groupAnagrams(words);
        check(groups.size() == 3, "groupAnagrams count");
        vector<int> p = {1, 2}, q = {-2, -1}, r = {-1, 2}, s = {0, 2};
        check(fourSumCount(p, q, r, s) == 2, "fourSumCount");
        vector<int> ones = {1, 1, 1};
        check(subarraySum(ones, 2) == 2, "subarraySum ones");
        vector<int> onetwothree = {1, 2, 3};
        check(subarraySum(onetwothree, 3) == 2, "subarraySum mixed");
        vector<int> scattered = {100, 4, 200, 1, 3, 2};
        check(longestConsecutive(scattered) == 4, "longestConsecutive");
        vector<int> none = {};
        check(longestConsecutive(none) == 0, "longestConsecutive empty");
        vector<vector<char>> board(9, vector<char>(9, '.'));
        check(isValidSudoku(board), "sudoku empty is valid");
        board[0][0] = '5';
        board[0][1] = '5';
        check(!isValidSudoku(board), "sudoku row clash");
        board[0][1] = '.';
        board[1][0] = '5';
        check(!isValidSudoku(board), "sudoku column clash");
        board[1][0] = '.';
        board[1][1] = '5';
        check(!isValidSudoku(board), "sudoku box clash");
    """,
    "lc-two-pointers": """
        check(isPalindrome("A man, a plan, a canal: Panama"), "palindrome yes");
        check(!isPalindrome("race a car"), "palindrome no");
        check(isPalindrome(""), "palindrome empty");
        vector<int> sorted = {2, 7, 11, 15};
        check(twoSumSorted(sorted, 9) == vector<int>({1, 2}), "twoSumSorted");
        vector<int> walls = {1, 8, 6, 2, 5, 4, 8, 3, 7};
        check(maxArea(walls) == 49, "maxArea");
        vector<int> three = {-1, 0, 1, 2, -1, -4};
        auto triples = threeSum(three);
        check(triples.size() == 2, "threeSum count");
        vector<int> zeros = {0, 0};
        check(threeSum(zeros).empty(), "threeSum too short");
        vector<int> dupes = {1, 1, 2, 2, 3};
        check(removeDuplicates(dupes) == 3, "removeDuplicates count");
        check(dupes[0] == 1 && dupes[1] == 2 && dupes[2] == 3,
              "removeDuplicates prefix");
        vector<int> zeroed = {0, 1, 0, 3, 12};
        moveZeroes(zeroed);
        check(zeroed == vector<int>({1, 3, 12, 0, 0}), "moveZeroes");
        vector<int> relief = {0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1};
        check(trap(relief) == 6, "trap");
        vector<int> flat = {};
        check(trap(flat) == 0, "trap empty");
        vector<int> negatives = {-4, -1, 0, 3, 10};
        check(sortedSquares(negatives) == vector<int>({0, 1, 9, 16, 100}),
              "sortedSquares");
    """,
    "lc-sliding-window": """
        vector<int> prices = {7, 1, 5, 3, 6, 4};
        check(maxProfit(prices) == 5, "maxProfit");
        vector<int> falling = {7, 6, 4, 3, 1};
        check(maxProfit(falling) == 0, "maxProfit never up");
        check(lengthOfLongestSubstring("abcabcbb") == 3, "longest substring");
        check(lengthOfLongestSubstring("bbbbb") == 1, "longest all same");
        check(lengthOfLongestSubstring("pwwkew") == 3, "longest wraparound");
        check(lengthOfLongestSubstring("") == 0, "longest empty");
        vector<int> nums = {2, 3, 1, 2, 4, 3};
        check(minSubArrayLen(7, nums) == 2, "minSubArrayLen");
        vector<int> small = {1, 1, 1};
        check(minSubArrayLen(11, small) == 0, "minSubArrayLen impossible");
        check(characterReplacement("ABAB", 2) == 4, "characterReplacement");
        check(characterReplacement("AABABBA", 1) == 4, "characterReplacement 2");
        vector<int> avg = {1, 12, -5, -6, 50, 3};
        check(findMaxAverage(avg, 4) > 12.749 && findMaxAverage(avg, 4) < 12.751,
              "findMaxAverage");
        check(checkInclusion("ab", "eidbaooo"), "checkInclusion yes");
        check(!checkInclusion("ab", "eidboaoo"), "checkInclusion no");
        check(!checkInclusion("abcd", "ab"), "checkInclusion too long");
        vector<int> ones = {1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0};
        check(longestOnes(ones, 2) == 6, "longestOnes");
        check(minWindow("ADOBECODEBANC", "ABC") == "BANC", "minWindow");
        check(minWindow("a", "aa") == "", "minWindow impossible");
    """,
    "lc-stack": """
        check(isValid("()[]{}"), "brackets valid");
        check(!isValid("([)]"), "brackets interleaved");
        check(!isValid("("), "brackets unclosed");
        check(!isValid(")"), "brackets unopened");
        MinStack ms;
        ms.push(-2);
        ms.push(0);
        ms.push(-3);
        check(ms.getMin() == -3, "MinStack min");
        ms.pop();
        check(ms.top() == 0, "MinStack top");
        check(ms.getMin() == -2, "MinStack min after pop");
        vector<string> rpn = {"2", "1", "+", "3", "*"};
        check(evalRPN(rpn) == 9, "evalRPN");
        vector<string> divide = {"4", "13", "5", "/", "+"};
        check(evalRPN(divide) == 6, "evalRPN divide");
        vector<string> minus = {"7", "2", "-"};
        check(evalRPN(minus) == 5, "evalRPN order matters");
        vector<int> temps = {73, 74, 75, 71, 69, 72, 76, 73};
        check(dailyTemperatures(temps) ==
                  vector<int>({1, 1, 4, 2, 1, 1, 0, 0}),
              "dailyTemperatures");
        vector<string> ops = {"5", "2", "C", "D", "+"};
        check(calPoints(ops) == 30, "calPoints");
        check(simplifyPath("/home//foo/") == "/home/foo", "simplifyPath");
        check(simplifyPath("/../") == "/", "simplifyPath above root");
        check(simplifyPath("/a/./b/../../c/") == "/c", "simplifyPath dots");
        vector<int> bars = {2, 1, 5, 6, 2, 3};
        check(largestRectangleArea(bars) == 10, "largestRectangleArea");
        check(decodeString("3[a]2[bc]") == "aaabcbc", "decodeString");
        check(decodeString("3[a2[c]]") == "accaccacc", "decodeString nested");
        check(decodeString("10[a]") == "aaaaaaaaaa", "decodeString two digits");
    """,
    "lc-linked-list": """
        check(flatten(reverseList(build({1, 2, 3}))) == vector<int>({3, 2, 1}),
              "reverseList");
        check(flatten(reverseList(build({}))).empty(), "reverseList empty");
        check(flatten(mergeTwoLists(build({1, 2, 4}), build({1, 3, 4}))) ==
                  vector<int>({1, 1, 2, 3, 4, 4}),
              "mergeTwoLists");
        check(flatten(mergeTwoLists(build({}), build({0}))) == vector<int>({0}),
              "mergeTwoLists one empty");
        ListNode* looped = build({1, 2, 3});
        check(!hasCycle(looped), "hasCycle no");
        looped->next->next->next = looped->next;
        check(hasCycle(looped), "hasCycle yes");
        check(!hasCycle(nullptr), "hasCycle empty");
        check(flatten(removeNthFromEnd(build({1, 2, 3, 4, 5}), 2)) ==
                  vector<int>({1, 2, 3, 5}),
              "removeNthFromEnd");
        check(flatten(removeNthFromEnd(build({1}), 1)).empty(),
              "removeNthFromEnd only node");
        check(flatten(removeNthFromEnd(build({1, 2}), 2)) == vector<int>({2}),
              "removeNthFromEnd head");
        check(flatten(middleNode(build({1, 2, 3, 4, 5}))) ==
                  vector<int>({3, 4, 5}),
              "middleNode odd");
        check(flatten(middleNode(build({1, 2, 3, 4, 5, 6}))) ==
                  vector<int>({4, 5, 6}),
              "middleNode even takes the second");
        check(flatten(deleteDuplicates(build({1, 1, 2, 3, 3}))) ==
                  vector<int>({1, 2, 3}),
              "deleteDuplicates");
        check(flatten(deleteDuplicates(build({1, 1, 1}))) == vector<int>({1}),
              "deleteDuplicates run of three");
        check(isPalindromeList(build({1, 2, 2, 1})), "palindrome even");
        check(isPalindromeList(build({1, 2, 1})), "palindrome odd");
        check(!isPalindromeList(build({1, 2})), "palindrome no");
        check(isPalindromeList(build({})), "palindrome empty");
        check(flatten(addTwoNumbers(build({2, 4, 3}), build({5, 6, 4}))) ==
                  vector<int>({7, 0, 8}),
              "addTwoNumbers");
        check(flatten(addTwoNumbers(build({5}), build({5}))) ==
                  vector<int>({0, 1}),
              "addTwoNumbers final carry");
    """,
    "lc-binary-search": """
        vector<int> sorted = {-1, 0, 3, 5, 9, 12};
        check(search(sorted, 9) == 4, "search found");
        check(search(sorted, 2) == -1, "search missing");
        vector<int> empty = {};
        check(search(empty, 1) == -1, "search empty");
        vector<int> four = {1, 3, 5, 6};
        check(searchInsert(four, 5) == 2, "searchInsert found");
        check(searchInsert(four, 7) == 4, "searchInsert past end");
        check(searchInsert(four, 0) == 0, "searchInsert front");
        vector<int> rotated = {3, 4, 5, 1, 2};
        check(findMin(rotated) == 1, "findMin rotated");
        vector<int> plain = {11, 13, 15, 17};
        check(findMin(plain) == 11, "findMin unrotated");
        vector<int> spun = {4, 5, 6, 7, 0, 1, 2};
        check(searchRotated(spun, 0) == 4, "searchRotated found");
        check(searchRotated(spun, 3) == -1, "searchRotated missing");
        vector<int> one = {1};
        check(searchRotated(one, 1) == 0, "searchRotated single");
        vector<int> piles = {3, 6, 7, 11};
        check(minEatingSpeed(piles, 8) == 4, "minEatingSpeed");
        vector<int> bigger = {30, 11, 23, 4, 20};
        check(minEatingSpeed(bigger, 5) == 30, "minEatingSpeed tight");
        check(firstBadVersion(5, badFrom4) == 4, "firstBadVersion");
        check(firstBadVersion(1, badFrom1) == 1, "firstBadVersion single");
        vector<int> repeated = {5, 7, 7, 8, 8, 10};
        check(searchRange(repeated, 8) == vector<int>({3, 4}), "searchRange");
        check(searchRange(repeated, 6) == vector<int>({-1, -1}),
              "searchRange missing");
        vector<vector<int>> matrix = {
            {1, 3, 5, 7}, {10, 11, 16, 20}, {23, 30, 34, 60}};
        check(searchMatrix(matrix, 3), "searchMatrix found");
        check(!searchMatrix(matrix, 13), "searchMatrix missing");
        vector<vector<int>> noRows = {};
        check(!searchMatrix(noRows, 1), "searchMatrix empty");
    """,
    "lc-tree-dfs": """
        check(maxDepth(build({n(3), n(9), n(20)})) == 2, "maxDepth");
        check(maxDepth(nullptr) == 0, "maxDepth empty");
        check(vals(invertTree(build({n(1), n(2), n(3)}))) ==
                  vector<int>({1, 3, 2}),
              "invertTree");
        check(hasPathSum(build({n(5), n(4), n(8), n(11)}), 20), "hasPathSum");
        check(!hasPathSum(build({n(1), n(2), n(3)}), 5), "hasPathSum no");
        check(!hasPathSum(nullptr, 0), "hasPathSum empty");
        check(diameterOfBinaryTree(build({n(1), n(2), n(3), n(4), n(5)})) == 3,
              "diameter");
        check(diameterOfBinaryTree(build({n(1), n(2)})) == 1, "diameter small");
        check(isValidBST(build({n(2), n(1), n(3)})), "bst valid");
        check(!isValidBST(build({n(5), n(1), n(4), n(3), n(6)})), "bst invalid");
        check(!isValidBST(build({n(5), n(4), n(6), gap(), gap(), n(3), n(7)})),
              "bst deep violation");
        check(isValidBST(build({n(INT_MIN)})), "bst INT_MIN");
        check(isSameTree(build({n(1), n(2), n(3)}), build({n(1), n(2), n(3)})),
              "sameTree yes");
        check(!isSameTree(build({n(1), n(2)}), build({n(1), gap(), n(2)})),
              "sameTree shape");
        check(isSymmetric(build({n(1), n(2), n(2), n(3), n(4), n(4), n(3)})),
              "symmetric yes");
        check(!isSymmetric(build({n(1), n(2), n(2), gap(), n(3), gap(), n(3)})),
              "symmetric no");
        TreeNode* tree = build({n(3), n(5), n(1), n(6), n(2), n(0), n(8)});
        TreeNode* five = tree->left;
        TreeNode* oneNode = tree->right;
        TreeNode* two = tree->left->right;
        check(lowestCommonAncestor(tree, five, oneNode) == tree, "lca root");
        check(lowestCommonAncestor(tree, five, two) == five, "lca own ancestor");
    """,
    "lc-tree-bfs": """
        TreeNode* tree = build({n(3), n(9), n(20), gap(), gap(), n(15), n(7)});
        vector<vector<int>> expected = {{3}, {9, 20}, {15, 7}};
        check(levelOrder(tree) == expected, "levelOrder");
        check(levelOrder(nullptr).empty(), "levelOrder empty");
        check(rightSideView(build({n(1), n(2), n(3), gap(), n(5)})) ==
                  vector<int>({1, 3, 5}),
              "rightSideView");
        vector<vector<int>> zig = {{3}, {20, 9}, {15, 7}};
        check(zigzagLevelOrder(tree) == zig, "zigzag");
        check(minDepth(tree) == 2, "minDepth");
        check(minDepth(build({n(2), gap(), n(3)})) == 2, "minDepth one-sided");
        check(minDepth(nullptr) == 0, "minDepth empty");
        vector<double> avgs = averageOfLevels(tree);
        check(avgs[0] > 2.99 && avgs[0] < 3.01, "averages row 1");
        check(avgs[1] > 14.49 && avgs[1] < 14.51, "averages row 2");
        check(largestValues(build({n(1), n(3), n(2), n(5), n(3), gap(), n(9)})) ==
                  vector<int>({1, 3, 9}),
              "largestValues");
        check(largestValues(build({n(-1), n(-2), n(-3)})) ==
                  vector<int>({-1, -2}),
              "largestValues all negative");
        check(maxLevelSum(build({n(1), n(7), n(0), n(7), n(-8)})) == 2,
              "maxLevelSum");
        check(maxLevelSum(build({n(1)})) == 1, "maxLevelSum single");
        check(widthOfBinaryTree(
                  build({n(1), n(3), n(2), n(5), n(3), gap(), n(9)})) == 4,
              "width");
        check(widthOfBinaryTree(build({n(1), n(3), n(2), n(5)})) == 2,
              "width narrow");
        check(widthOfBinaryTree(nullptr) == 0, "width empty");
    """,
    "lc-graph": """
        vector<vector<int>> image = {{1, 1, 1}, {1, 1, 0}, {1, 0, 1}};
        vector<vector<int>> filled = {{2, 2, 2}, {2, 2, 0}, {2, 0, 1}};
        check(floodFill(image, 1, 1, 2) == filled, "floodFill");
        vector<vector<int>> same = {{0, 0}, {0, 0}};
        vector<vector<int>> unchanged = {{0, 0}, {0, 0}};
        check(floodFill(same, 0, 0, 0) == unchanged, "floodFill same colour");
        vector<vector<char>> land = gridOf({"11000", "11000", "00100", "00011"});
        check(numIslands(land) == 3, "numIslands");
        vector<vector<char>> sea = gridOf({"000"});
        check(numIslands(sea) == 0, "numIslands none");
        vector<vector<int>> oranges = {{2, 1, 1}, {1, 1, 0}, {0, 1, 1}};
        check(orangesRotting(oranges) == 4, "orangesRotting");
        vector<vector<int>> stranded = {{2, 1, 1}, {0, 1, 1}, {1, 0, 1}};
        check(orangesRotting(stranded) == -1, "orangesRotting unreachable");
        vector<vector<int>> alreadyDone = {{0, 2}};
        check(orangesRotting(alreadyDone) == 0, "orangesRotting nothing fresh");
        Node* a = new Node(1);
        Node* b = new Node(2);
        a->neighbors.push_back(b);
        b->neighbors.push_back(a);
        Node* cloned = cloneGraph(a);
        check(cloned->val == 1, "cloneGraph value");
        check(cloned != a, "cloneGraph is a copy");
        check(cloned->neighbors.size() == 1, "cloneGraph edge count");
        check(cloned->neighbors[0]->val == 2, "cloneGraph neighbour");
        check(cloned->neighbors[0]->neighbors[0] == cloned,
              "cloneGraph cycle points back at the copy");
        check(cloneGraph(nullptr) == nullptr, "cloneGraph null");
        vector<vector<int>> islands = {{1, 1, 0}, {1, 0, 0}, {0, 0, 1}};
        check(maxAreaOfIsland(islands) == 3, "maxAreaOfIsland");
        vector<vector<int>> water = {{0, 0}};
        check(maxAreaOfIsland(water) == 0, "maxAreaOfIsland none");
        vector<vector<int>> joined = {{1, 1, 0}, {1, 1, 0}, {0, 0, 1}};
        check(findCircleNum(joined) == 2, "findCircleNum");
        vector<vector<int>> apart = {{1, 0, 0}, {0, 1, 0}, {0, 0, 1}};
        check(findCircleNum(apart) == 3, "findCircleNum separate");
        vector<vector<int>> mat = {{0, 0, 0}, {0, 1, 0}, {1, 1, 1}};
        vector<vector<int>> distances = {{0, 0, 0}, {0, 1, 0}, {1, 2, 1}};
        check(updateMatrix(mat) == distances, "updateMatrix");
        vector<vector<int>> heights = {
            {1, 2, 2, 3, 5}, {3, 2, 3, 4, 4}, {2, 4, 5, 3, 1},
            {6, 7, 1, 4, 5}, {5, 1, 1, 2, 4}};
        auto flows = pacificAtlantic(heights);
        check(flows.size() == 7, "pacificAtlantic count");
    """,
    "lc-backtracking": """
        vector<int> three = {1, 2, 3};
        check(subsets(three).size() == 8, "subsets count");
        vector<int> dupes = {1, 2, 2};
        auto withDup = subsetsWithDup(dupes);
        check(withDup.size() == 6, "subsetsWithDup count");
        vector<int> perm = {1, 2, 3};
        check(permute(perm).size() == 6, "permute count");
        vector<int> candidates = {2, 3, 6, 7};
        auto sums = combinationSum(candidates, 7);
        check(sums.size() == 2, "combinationSum count");
        vector<vector<char>> board = gridOf({"ABCE", "SFCS", "ADEE"});
        check(exist(board, "ABCCED"), "wordSearch found");
        check(!exist(board, "ABCB"), "wordSearch reuses a cell");
        check(combine(4, 2).size() == 6, "combine count");
        check(letterCombinations("23").size() == 9, "letterCombinations");
        check(letterCombinations("").empty(), "letterCombinations empty");
        check(partition("aab").size() == 2, "partition count");
    """,
    "lc-heap": """
        vector<int> nums = {3, 2, 1, 5, 6, 4};
        check(findKthLargest(nums, 2) == 5, "findKthLargest");
        vector<int> single = {1};
        check(findKthLargest(single, 1) == 1, "findKthLargest single");
        vector<int> repeated = {1, 1, 1, 2, 2, 3};
        auto top = topKFrequent(repeated, 2);
        sort(top.begin(), top.end());
        check(top == vector<int>({1, 2}), "topKFrequent");
        vector<vector<int>> points = {{1, 3}, {-2, 2}};
        auto closest = kClosest(points, 1);
        check(closest.size() == 1 && closest[0] == vector<int>({-2, 2}),
              "kClosest");
        vector<int> stones = {2, 7, 4, 1, 8, 1};
        check(lastStoneWeight(stones) == 1, "lastStoneWeight");
        vector<int> lone = {1};
        check(lastStoneWeight(lone) == 1, "lastStoneWeight one");
        vector<int> pair2 = {2, 2};
        check(lastStoneWeight(pair2) == 0, "lastStoneWeight cancel");
        vector<string> words = {"i", "love", "leetcode", "i", "love", "coding"};
        check(topKFrequentWords(words, 2) == vector<string>({"i", "love"}),
              "topKFrequentWords");
        vector<string> tied = {"b", "a", "c", "a", "b"};
        check(topKFrequentWords(tied, 2) == vector<string>({"a", "b"}),
              "topKFrequentWords alphabetical tie-break");
        string sorted = frequencySort("tree");
        check(sorted == "eert" || sorted == "eetr", "frequencySort");
        check(frequencySort("cccaaa").size() == 6, "frequencySort length");
        vector<vector<int>> matrix = {{1, 5, 9}, {10, 11, 13}, {12, 13, 15}};
        check(kthSmallest(matrix, 8) == 13, "kthSmallest");
        vector<vector<int>> tiny = {{-5}};
        check(kthSmallest(tiny, 1) == -5, "kthSmallest single");
        string spread = reorganizeString("aab");
        check(spread.size() == 3, "reorganizeString length");
        bool adjacent = false;
        for (size_t i = 1; i < spread.size(); i++) {
            if (spread[i] == spread[i - 1]) {
                adjacent = true;
            }
        }
        check(!adjacent, "reorganizeString has no neighbours alike");
        check(reorganizeString("aaab") == "", "reorganizeString impossible");
    """,
    "lc-topological": """
        vector<vector<int>> one = {{1, 0}};
        check(canFinish(2, one), "canFinish");
        vector<vector<int>> cycle = {{1, 0}, {0, 1}};
        check(!canFinish(2, cycle), "canFinish cycle");
        check(findOrder(2, one) == vector<int>({0, 1}), "findOrder");
        check(findOrder(2, cycle).empty(), "findOrder cycle");
        vector<vector<int>> star = {{1, 0}, {1, 2}, {1, 3}};
        check(findMinHeightTrees(4, star) == vector<int>({1}), "minHeightTrees");
        vector<vector<int>> none = {};
        check(findMinHeightTrees(1, none) == vector<int>({0}),
              "minHeightTrees single");
        vector<vector<int>> graph = {{1, 2}, {2, 3}, {5}, {0}, {5}, {}, {}};
        check(eventualSafeNodes(graph) == vector<int>({2, 4, 5, 6}), "safeNodes");
        vector<vector<int>> chain = {{0, 1}, {1, 2}};
        vector<vector<int>> queries = {{0, 2}, {2, 0}};
        vector<bool> expected = {true, false};
        check(checkIfPrerequisite(3, chain, queries) == expected,
              "checkIfPrerequisite transitive");
        vector<string> recipes = {"bread"};
        vector<vector<string>> ingredients = {{"yeast", "flour"}};
        vector<string> supplies = {"yeast", "flour", "corn"};
        check(findAllRecipes(recipes, ingredients, supplies) ==
                  vector<string>({"bread"}),
              "findAllRecipes");
        vector<string> two = {"bread", "sandwich"};
        vector<vector<string>> needs = {{"yeast", "flour"}, {"bread", "meat"}};
        vector<string> have = {"yeast", "flour", "meat"};
        check(findAllRecipes(two, needs, have) ==
                  vector<string>({"bread", "sandwich"}),
              "findAllRecipes chained");
        vector<vector<int>> parallel = {{1, 3}, {2, 3}};
        check(minimumSemesters(3, parallel) == 2, "minimumSemesters");
        vector<vector<int>> looped = {{1, 2}, {2, 3}, {3, 1}};
        check(minimumSemesters(3, looped) == -1, "minimumSemesters cycle");
        vector<string> alien = {"wrt", "wrf", "er", "ett", "rftt"};
        check(alienOrder(alien).size() == 5, "alienOrder");
        vector<string> prefix = {"abc", "ab"};
        check(alienOrder(prefix) == "", "alienOrder impossible prefix");
    """,
    "lc-dp": """
        check(climbStairs(2) == 2, "climbStairs 2");
        check(climbStairs(3) == 3, "climbStairs 3");
        check(climbStairs(1) == 1, "climbStairs 1");
        vector<int> houses = {1, 2, 3, 1};
        check(rob(houses) == 4, "rob");
        vector<int> more = {2, 7, 9, 3, 1};
        check(rob(more) == 12, "rob longer");
        vector<int> coins = {1, 3, 4};
        check(coinChange(coins, 6) == 2, "coinChange beats greedy");
        vector<int> two = {2};
        check(coinChange(two, 3) == -1, "coinChange impossible");
        vector<int> penny = {1};
        check(coinChange(penny, 0) == 0, "coinChange zero");
        vector<int> rising = {10, 9, 2, 5, 3, 7, 101, 18};
        check(lengthOfLIS(rising) == 4, "lengthOfLIS");
        vector<int> flat = {7, 7, 7};
        check(lengthOfLIS(flat) == 1, "lengthOfLIS strict");
        vector<int> cost = {10, 15, 20};
        check(minCostClimbingStairs(cost) == 15, "minCost");
        vector<int> longer = {1, 100, 1, 1, 1, 100, 1, 1, 100, 1};
        check(minCostClimbingStairs(longer) == 6, "minCost longer");
        check(longestCommonSubsequence("abcde", "ace") == 3, "lcs");
        check(longestCommonSubsequence("abc", "def") == 0, "lcs none");
        vector<string> dict = {"leet", "code"};
        check(wordBreak("leetcode", dict), "wordBreak");
        vector<string> tricky = {"cats", "dog", "sand", "and", "cat"};
        check(!wordBreak("catsandog", tricky), "wordBreak no");
        vector<int> products = {2, 3, -2, 4};
        check(maxProduct(products) == 6, "maxProduct");
        vector<int> zeroed = {-2, 0, -1};
        check(maxProduct(zeroed) == 0, "maxProduct zero");
        vector<int> negatives = {-2, 3, -4};
        check(maxProduct(negatives) == 24, "maxProduct two negatives");
    """,
}

LIST_HELPERS = """
static ListNode* build(vector<int> values) {
    ListNode head;
    ListNode* tail = &head;
    for (int v : values) {
        tail->next = new ListNode(v);
        tail = tail->next;
    }
    return head.next;
}

static vector<int> flatten(ListNode* head) {
    vector<int> out;
    while (head) {
        out.push_back(head->val);
        head = head->next;
    }
    return out;
}
"""

# Built from a level-order list where a gap is a missing child, the way
# LeetCode prints its trees, so a check reads like the problem statement.
TREE_HELPERS = """
#include <queue>
#include <optional>
static optional<int> n(int value) { return value; }
static optional<int> gap() { return nullopt; }

static TreeNode* build(vector<optional<int>> values) {
    if (values.empty() || !values[0].has_value()) {
        return nullptr;
    }
    TreeNode* root = new TreeNode(values[0].value());
    queue<TreeNode*> pending;
    pending.push(root);
    size_t i = 1;
    while (i < values.size()) {
        TreeNode* parent = pending.front();
        pending.pop();
        if (i < values.size()) {
            if (values[i].has_value()) {
                parent->left = new TreeNode(values[i].value());
                pending.push(parent->left);
            }
            i++;
        }
        if (i < values.size()) {
            if (values[i].has_value()) {
                parent->right = new TreeNode(values[i].value());
                pending.push(parent->right);
            }
            i++;
        }
    }
    return root;
}
"""

# Tree DFS has no level walk of its own, so it needs one to check against.
TREE_VALS = """
static vector<int> vals(TreeNode* root) {
    vector<int> out;
    queue<TreeNode*> pending;
    if (root) {
        pending.push(root);
    }
    while (!pending.empty()) {
        TreeNode* node = pending.front();
        pending.pop();
        out.push_back(node->val);
        if (node->left) {
            pending.push(node->left);
        }
        if (node->right) {
            pending.push(node->right);
        }
    }
    return out;
}
"""

GRID = """
static vector<vector<char>> gridOf(vector<string> rows) {
    vector<vector<char>> out;
    for (const string& row : rows) {
        out.push_back(vector<char>(row.begin(), row.end()));
    }
    return out;
}
"""

# firstBadVersion takes a plain function pointer, so the checks need real
# functions rather than lambdas with captures.
BAD_VERSION = """
static bool badFrom4(int v) { return v >= 4; }
static bool badFrom1(int v) { return v >= 1; }
"""

HELPERS_FOR = {
    "lc-linked-list": [LIST_HELPERS],
    "lc-binary-search": [BAD_VERSION],
    "lc-tree-dfs": [TREE_HELPERS, TREE_VALS],
    "lc-tree-bfs": [TREE_HELPERS],
    "lc-graph": ["#include <string>", GRID],
    "lc-backtracking": [GRID],
}

# A tiny assert that names itself. A green run prints nothing but the final
# line, so a failure is the only thing you have to read.
HARNESS = """
#include <iostream>
static int failures = 0;
static void check(bool ok, const char* label) {
    if (!ok) {
        std::cout << "FAILED: " << label << "\\n";
        failures++;
    }
}
"""

REPORT = """
    if (failures) {
        return 1;
    }
    std::cout << "ok\\n";
    return 0;
"""


@unittest.skipUnless(HAS_CPP, "needs g++, clang++, or an MSVC install")
class CppSolutionTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.append(HARNESS)
        parts.extend(HELPERS_FOR.get(pattern_id, []))
        parts.extend(p.code for p in pattern.problems)
        parts.append("int main() {\n" + CHECKS[pattern_id] + REPORT + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="cpp")
        self.assertEqual(code, 0, (err or out)[:2000])
        self.assertEqual(out.strip(), "ok", out[:2000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class CoverageTests(unittest.TestCase):
    """These run with or without a compiler."""

    def test_every_pattern_present_has_checks(self) -> None:
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_every_pattern_mirrors_the_python_bank(self) -> None:
        from code_coach.leetcode.problems import PATTERNS_BY_ID as PY

        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                theirs = [p.number for p in PY[pattern.id].problems]
                self.assertEqual([p.number for p in pattern.problems], theirs)
                titles = [p.title for p in PY[pattern.id].problems]
                self.assertEqual([p.title for p in pattern.problems], titles)

    def test_it_covers_every_problem(self) -> None:
        from code_coach.leetcode.problems import all_problems

        theirs = sorted(p.number for p in all_problems())
        mine = sorted(p.number for pat in PATTERNS for p in pat.problems)
        self.assertEqual(mine, theirs)


if __name__ == "__main__":
    unittest.main()
