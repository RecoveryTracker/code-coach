"""Every C solution is compiled and run against real cases.

C is the bank where this matters most. There is no type system catching a
wrong length, no container bounds-checking an index, and a solution that is
subtly wrong about who frees what still looks perfectly reasonable on the
page. Reading is not enough; these are executed.

The source compiled is the exact string the student is asked to type, read
out of the bank rather than a copy, and it goes through the app's own runner
so the flags are the ones the student's Run button uses.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import msvc_available, run_code
from code_coach.leetcode.problems_c import PATTERNS

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_C = any(shutil.which(c) for c in ("gcc", "clang")) or msvc_available()

CHECKS = {
    "lc-hashmap": """
        int nums[] = {2, 7, 11, 15};
        int size = 0;
        int *pair = twoSum(nums, 4, 9, &size);
        check(size == 2 && pair[0] == 0 && pair[1] == 1, "twoSum basic");
        free(pair);
        int later[] = {3, 2, 4};
        pair = twoSum(later, 3, 6, &size);
        check(size == 2 && pair[0] == 1 && pair[1] == 2, "twoSum not-first");
        free(pair);
        int none[] = {1, 2};
        pair = twoSum(none, 2, 99, &size);
        check(size == 0 && pair == NULL, "twoSum no answer");
        int dup[] = {1, 2, 3, 1};
        check(containsDuplicate(dup, 4), "containsDuplicate yes");
        int uniq[] = {1, 2, 3};
        check(!containsDuplicate(uniq, 3), "containsDuplicate no");
        check(isAnagram("anagram", "nagaram"), "isAnagram yes");
        check(!isAnagram("rat", "car"), "isAnagram no");
        check(!isAnagram("a", "ab"), "isAnagram length");
        char *words[] = {"eat", "tea", "tan", "ate", "nat", "bat"};
        int groupCount = 0;
        int *columns = NULL;
        char ***groups = groupAnagrams(words, 6, &groupCount, &columns);
        check(groupCount == 3, "groupAnagrams count");
        int biggest = 0;
        for (int i = 0; i < groupCount; i++) {
            if (columns[i] > biggest) {
                biggest = columns[i];
            }
        }
        check(biggest == 3, "groupAnagrams largest group");
        for (int i = 0; i < groupCount; i++) {
            free(groups[i]);
        }
        free(groups);
        free(columns);
        int a[] = {1, 2}, b[] = {-2, -1}, c[] = {-1, 2}, d[] = {0, 2};
        check(fourSumCount(a, 2, b, 2, c, 2, d, 2) == 2, "fourSumCount");
        int ones[] = {1, 1, 1};
        check(subarraySum(ones, 3, 2) == 2, "subarraySum ones");
        int upto[] = {1, 2, 3};
        check(subarraySum(upto, 3, 3) == 2, "subarraySum mixed");
        int scattered[] = {100, 4, 200, 1, 3, 2};
        check(longestConsecutive(scattered, 6) == 4, "longestConsecutive");
        check(longestConsecutive(NULL, 0) == 0, "longestConsecutive empty");
        char *rows[9];
        char blank[9][10];
        for (int r = 0; r < 9; r++) {
            for (int col = 0; col < 9; col++) {
                blank[r][col] = '.';
            }
            blank[r][9] = '\\0';
            rows[r] = blank[r];
        }
        int widths[9];
        for (int r = 0; r < 9; r++) {
            widths[r] = 9;
        }
        check(isValidSudoku(rows, 9, widths), "sudoku empty is valid");
        blank[0][0] = '5';
        blank[0][1] = '5';
        check(!isValidSudoku(rows, 9, widths), "sudoku row clash");
        blank[0][1] = '.';
        blank[1][0] = '5';
        check(!isValidSudoku(rows, 9, widths), "sudoku column clash");
        blank[1][0] = '.';
        blank[1][1] = '5';
        check(!isValidSudoku(rows, 9, widths), "sudoku box clash");
    """,
    "lc-two-pointers": """
        check(isPalindrome("A man, a plan, a canal: Panama"), "palindrome yes");
        check(!isPalindrome("race a car"), "palindrome no");
        check(isPalindrome(""), "palindrome empty");
        int sorted[] = {2, 7, 11, 15};
        int size = 0;
        int *pair = twoSumSorted(sorted, 4, 9, &size);
        check(size == 2 && pair[0] == 1 && pair[1] == 2, "twoSumSorted");
        free(pair);
        int walls[] = {1, 8, 6, 2, 5, 4, 8, 3, 7};
        check(maxArea(walls, 9) == 49, "maxArea");
        int three[] = {-1, 0, 1, 2, -1, -4};
        int tripleCount = 0;
        int *widths = NULL;
        int **triples = threeSum(three, 6, &tripleCount, &widths);
        check(tripleCount == 2, "threeSum count");
        check(widths[0] == 3, "threeSum triple width");
        for (int i = 0; i < tripleCount; i++) {
            free(triples[i]);
        }
        free(triples);
        free(widths);
        int zeros[] = {0, 0};
        triples = threeSum(zeros, 2, &tripleCount, &widths);
        check(tripleCount == 0, "threeSum too short");
        free(triples);
        free(widths);
        int dupes[] = {1, 1, 2, 2, 3};
        check(removeDuplicates(dupes, 5) == 3, "removeDuplicates count");
        check(dupes[0] == 1 && dupes[1] == 2 && dupes[2] == 3,
              "removeDuplicates prefix");
        int zeroed[] = {0, 1, 0, 3, 12};
        moveZeroes(zeroed, 5);
        check(zeroed[0] == 1 && zeroed[1] == 3 && zeroed[2] == 12 &&
                  zeroed[3] == 0 && zeroed[4] == 0,
              "moveZeroes");
        int relief[] = {0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1};
        check(trap(relief, 12) == 6, "trap");
        check(trap(NULL, 0) == 0, "trap empty");
        int negatives[] = {-4, -1, 0, 3, 10};
        int *squares = sortedSquares(negatives, 5, &size);
        check(size == 5 && squares[0] == 0 && squares[1] == 1 &&
                  squares[2] == 9 && squares[3] == 16 && squares[4] == 100,
              "sortedSquares");
        free(squares);
    """,
    "lc-sliding-window": """
        int prices[] = {7, 1, 5, 3, 6, 4};
        check(maxProfit(prices, 6) == 5, "maxProfit");
        int falling[] = {7, 6, 4, 3, 1};
        check(maxProfit(falling, 5) == 0, "maxProfit never up");
        check(lengthOfLongestSubstring("abcabcbb") == 3, "longest substring");
        check(lengthOfLongestSubstring("bbbbb") == 1, "longest all same");
        check(lengthOfLongestSubstring("pwwkew") == 3, "longest wraparound");
        check(lengthOfLongestSubstring("") == 0, "longest empty");
        int nums[] = {2, 3, 1, 2, 4, 3};
        check(minSubArrayLen(7, nums, 6) == 2, "minSubArrayLen");
        int small[] = {1, 1, 1};
        check(minSubArrayLen(11, small, 3) == 0, "minSubArrayLen impossible");
        check(characterReplacement("ABAB", 2) == 4, "characterReplacement");
        check(characterReplacement("AABABBA", 1) == 4, "characterReplacement 2");
        int avg[] = {1, 12, -5, -6, 50, 3};
        double got = findMaxAverage(avg, 6, 4);
        check(got > 12.749 && got < 12.751, "findMaxAverage");
        check(checkInclusion("ab", "eidbaooo"), "checkInclusion yes");
        check(!checkInclusion("ab", "eidboaoo"), "checkInclusion no");
        check(!checkInclusion("abcd", "ab"), "checkInclusion too long");
        int ones[] = {1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0};
        check(longestOnes(ones, 11, 2) == 6, "longestOnes");
        char *window = minWindow("ADOBECODEBANC", "ABC");
        check(strcmp(window, "BANC") == 0, "minWindow");
        free(window);
        window = minWindow("a", "aa");
        check(strcmp(window, "") == 0, "minWindow impossible");
        free(window);
    """,
    "lc-stack": """
        check(isValid("()[]{}"), "brackets valid");
        check(!isValid("([)]"), "brackets interleaved");
        check(!isValid("("), "brackets unclosed");
        check(!isValid(")"), "brackets unopened");
        MinStack *ms = minStackCreate();
        minStackPush(ms, -2);
        minStackPush(ms, 0);
        minStackPush(ms, -3);
        check(minStackGetMin(ms) == -3, "MinStack min");
        minStackPop(ms);
        check(minStackTop(ms) == 0, "MinStack top");
        check(minStackGetMin(ms) == -2, "MinStack min after pop");
        minStackFree(ms);
        char *rpn[] = {"2", "1", "+", "3", "*"};
        check(evalRPN(rpn, 5) == 9, "evalRPN");
        char *divide[] = {"4", "13", "5", "/", "+"};
        check(evalRPN(divide, 5) == 6, "evalRPN divide");
        char *minus[] = {"7", "2", "-"};
        check(evalRPN(minus, 3) == 5, "evalRPN order matters");
        char *negative[] = {"-3", "2", "*"};
        check(evalRPN(negative, 3) == -6, "evalRPN negative literal");
        int temps[] = {73, 74, 75, 71, 69, 72, 76, 73};
        int size = 0;
        int *waits = dailyTemperatures(temps, 8, &size);
        int expected[] = {1, 1, 4, 2, 1, 1, 0, 0};
        bool same = size == 8;
        for (int i = 0; i < 8 && same; i++) {
            same = waits[i] == expected[i];
        }
        check(same, "dailyTemperatures");
        free(waits);
        char *ops[] = {"5", "2", "C", "D", "+"};
        check(calPoints(ops, 5) == 30, "calPoints");
        char *simple = simplifyPath("/home//foo/");
        check(strcmp(simple, "/home/foo") == 0, "simplifyPath");
        free(simple);
        simple = simplifyPath("/../");
        check(strcmp(simple, "/") == 0, "simplifyPath above root");
        free(simple);
        simple = simplifyPath("/a/./b/../../c/");
        check(strcmp(simple, "/c") == 0, "simplifyPath dots");
        free(simple);
        int bars[] = {2, 1, 5, 6, 2, 3};
        check(largestRectangleArea(bars, 6) == 10, "largestRectangleArea");
        char *decoded = decodeString("3[a]2[bc]");
        check(strcmp(decoded, "aaabcbc") == 0, "decodeString");
        free(decoded);
        decoded = decodeString("3[a2[c]]");
        check(strcmp(decoded, "accaccacc") == 0, "decodeString nested");
        free(decoded);
        decoded = decodeString("10[a]");
        check(strcmp(decoded, "aaaaaaaaaa") == 0, "decodeString two digits");
        free(decoded);
    """,
    "lc-linked-list": """
        int one[] = {1, 2, 3};
        check(sameList(reverseList(build(one, 3)), (int[]){3, 2, 1}, 3),
              "reverseList");
        check(reverseList(build(NULL, 0)) == NULL, "reverseList empty");
        check(sameList(mergeTwoLists(build((int[]){1, 2, 4}, 3),
                                     build((int[]){1, 3, 4}, 3)),
                       (int[]){1, 1, 2, 3, 4, 4}, 6),
              "mergeTwoLists");
        check(sameList(mergeTwoLists(build(NULL, 0), build((int[]){0}, 1)),
                       (int[]){0}, 1),
              "mergeTwoLists one empty");
        struct ListNode *looped = build((int[]){1, 2, 3}, 3);
        check(!hasCycle(looped), "hasCycle no");
        looped->next->next->next = looped->next;
        check(hasCycle(looped), "hasCycle yes");
        check(!hasCycle(NULL), "hasCycle empty");
        check(sameList(removeNthFromEnd(build((int[]){1, 2, 3, 4, 5}, 5), 2),
                       (int[]){1, 2, 3, 5}, 4),
              "removeNthFromEnd");
        check(removeNthFromEnd(build((int[]){1}, 1), 1) == NULL,
              "removeNthFromEnd only node");
        check(sameList(removeNthFromEnd(build((int[]){1, 2}, 2), 2),
                       (int[]){2}, 1),
              "removeNthFromEnd head");
        check(sameList(middleNode(build((int[]){1, 2, 3, 4, 5}, 5)),
                       (int[]){3, 4, 5}, 3),
              "middleNode odd");
        check(sameList(middleNode(build((int[]){1, 2, 3, 4, 5, 6}, 6)),
                       (int[]){4, 5, 6}, 3),
              "middleNode even takes the second");
        check(sameList(deleteDuplicates(build((int[]){1, 1, 2, 3, 3}, 5)),
                       (int[]){1, 2, 3}, 3),
              "deleteDuplicates");
        check(sameList(deleteDuplicates(build((int[]){1, 1, 1}, 3)),
                       (int[]){1}, 1),
              "deleteDuplicates run of three");
        check(isPalindromeList(build((int[]){1, 2, 2, 1}, 4)), "palindrome even");
        check(isPalindromeList(build((int[]){1, 2, 1}, 3)), "palindrome odd");
        check(!isPalindromeList(build((int[]){1, 2}, 2)), "palindrome no");
        check(isPalindromeList(build(NULL, 0)), "palindrome empty");
        check(sameList(addTwoNumbers(build((int[]){2, 4, 3}, 3),
                                     build((int[]){5, 6, 4}, 3)),
                       (int[]){7, 0, 8}, 3),
              "addTwoNumbers");
        check(sameList(addTwoNumbers(build((int[]){5}, 1), build((int[]){5}, 1)),
                       (int[]){0, 1}, 2),
              "addTwoNumbers final carry");
    """,
    "lc-binary-search": """
        int sorted[] = {-1, 0, 3, 5, 9, 12};
        check(search(sorted, 6, 9) == 4, "search found");
        check(search(sorted, 6, 2) == -1, "search missing");
        check(search(NULL, 0, 1) == -1, "search empty");
        int four[] = {1, 3, 5, 6};
        check(searchInsert(four, 4, 5) == 2, "searchInsert found");
        check(searchInsert(four, 4, 7) == 4, "searchInsert past end");
        check(searchInsert(four, 4, 0) == 0, "searchInsert front");
        int rotated[] = {3, 4, 5, 1, 2};
        check(findMin(rotated, 5) == 1, "findMin rotated");
        int plain[] = {11, 13, 15, 17};
        check(findMin(plain, 4) == 11, "findMin unrotated");
        int spun[] = {4, 5, 6, 7, 0, 1, 2};
        check(searchRotated(spun, 7, 0) == 4, "searchRotated found");
        check(searchRotated(spun, 7, 3) == -1, "searchRotated missing");
        int single[] = {1};
        check(searchRotated(single, 1, 1) == 0, "searchRotated single");
        int piles[] = {3, 6, 7, 11};
        check(minEatingSpeed(piles, 4, 8) == 4, "minEatingSpeed");
        int bigger[] = {30, 11, 23, 4, 20};
        check(minEatingSpeed(bigger, 5, 5) == 30, "minEatingSpeed tight");
        check(firstBadVersion(5, badFrom4) == 4, "firstBadVersion");
        check(firstBadVersion(1, badFrom1) == 1, "firstBadVersion single");
        int repeated[] = {5, 7, 7, 8, 8, 10};
        int size = 0;
        int *range = searchRange(repeated, 6, 8, &size);
        check(size == 2 && range[0] == 3 && range[1] == 4, "searchRange");
        free(range);
        range = searchRange(repeated, 6, 6, &size);
        check(range[0] == -1 && range[1] == -1, "searchRange missing");
        free(range);
        int row0[] = {1, 3, 5, 7};
        int row1[] = {10, 11, 16, 20};
        int row2[] = {23, 30, 34, 60};
        int *matrix[] = {row0, row1, row2};
        int widths[] = {4, 4, 4};
        check(searchMatrix(matrix, 3, widths, 3), "searchMatrix found");
        check(!searchMatrix(matrix, 3, widths, 13), "searchMatrix missing");
        check(!searchMatrix(NULL, 0, widths, 1), "searchMatrix empty");
    """,
    "lc-tree-dfs": """
        check(maxDepth(build((int[]){3, 9, 20}, (bool[]){1, 1, 1}, 3)) == 2,
              "maxDepth");
        check(maxDepth(NULL) == 0, "maxDepth empty");
        struct TreeNode *inverted =
            invertTree(build((int[]){1, 2, 3}, (bool[]){1, 1, 1}, 3));
        check(inverted->left->val == 3 && inverted->right->val == 2,
              "invertTree");
        check(hasPathSum(build((int[]){5, 4, 8, 11}, (bool[]){1, 1, 1, 1}, 4), 20),
              "hasPathSum");
        check(!hasPathSum(build((int[]){1, 2, 3}, (bool[]){1, 1, 1}, 3), 5),
              "hasPathSum no");
        check(!hasPathSum(NULL, 0), "hasPathSum empty");
        check(diameterOfBinaryTree(
                  build((int[]){1, 2, 3, 4, 5}, (bool[]){1, 1, 1, 1, 1}, 5)) == 3,
              "diameter");
        check(diameterOfBinaryTree(build((int[]){1, 2}, (bool[]){1, 1}, 2)) == 1,
              "diameter small");
        check(isValidBST(build((int[]){2, 1, 3}, (bool[]){1, 1, 1}, 3)),
              "bst valid");
        check(!isValidBST(
                  build((int[]){5, 1, 4, 3, 6}, (bool[]){1, 1, 1, 1, 1}, 5)),
              "bst invalid");
        check(!isValidBST(build((int[]){5, 4, 6, 0, 0, 3, 7},
                                (bool[]){1, 1, 1, 0, 0, 1, 1}, 7)),
              "bst deep violation");
        check(isValidBST(build((int[]){INT_MIN}, (bool[]){1}, 1)),
              "bst INT_MIN");
        check(isSameTree(build((int[]){1, 2, 3}, (bool[]){1, 1, 1}, 3),
                         build((int[]){1, 2, 3}, (bool[]){1, 1, 1}, 3)),
              "sameTree yes");
        check(!isSameTree(build((int[]){1, 2}, (bool[]){1, 1}, 2),
                          build((int[]){1, 0, 2}, (bool[]){1, 0, 1}, 3)),
              "sameTree shape");
        check(isSymmetric(build((int[]){1, 2, 2, 3, 4, 4, 3},
                                (bool[]){1, 1, 1, 1, 1, 1, 1}, 7)),
              "symmetric yes");
        check(!isSymmetric(build((int[]){1, 2, 2, 0, 3, 0, 3},
                                 (bool[]){1, 1, 1, 0, 1, 0, 1}, 7)),
              "symmetric no");
        struct TreeNode *tree = build((int[]){3, 5, 1, 6, 2, 0, 8},
                                      (bool[]){1, 1, 1, 1, 1, 1, 1}, 7);
        check(lowestCommonAncestor(tree, tree->left, tree->right) == tree,
              "lca root");
        check(lowestCommonAncestor(tree, tree->left, tree->left->right) ==
                  tree->left,
              "lca own ancestor");
    """,
    "lc-tree-bfs": """
        struct TreeNode *tree = build((int[]){3, 9, 20, 0, 0, 15, 7},
                                      (bool[]){1, 1, 1, 0, 0, 1, 1}, 7);
        int rows = 0;
        int *widths = NULL;
        int **levels = levelOrder(tree, &rows, &widths);
        check(rows == 3 && widths[0] == 1 && widths[1] == 2 && widths[2] == 2,
              "levelOrder shape");
        check(levels[1][0] == 9 && levels[1][1] == 20, "levelOrder values");
        freeLevels(levels, widths, rows);
        levels = levelOrder(NULL, &rows, &widths);
        check(rows == 0 && levels == NULL, "levelOrder empty");
        int size = 0;
        int *view = rightSideView(
            build((int[]){1, 2, 3, 0, 5}, (bool[]){1, 1, 1, 0, 1}, 5), &size);
        check(size == 3 && view[0] == 1 && view[1] == 3 && view[2] == 5,
              "rightSideView");
        free(view);
        levels = zigzagLevelOrder(tree, &rows, &widths);
        check(rows == 3 && levels[1][0] == 20 && levels[1][1] == 9, "zigzag");
        freeLevels(levels, widths, rows);
        check(minDepth(tree) == 2, "minDepth");
        check(minDepth(build((int[]){2, 0, 3}, (bool[]){1, 0, 1}, 3)) == 2,
              "minDepth one-sided");
        check(minDepth(NULL) == 0, "minDepth empty");
        double *avgs = averageOfLevels(tree, &size);
        check(size == 3 && avgs[0] > 2.99 && avgs[0] < 3.01, "averages row 1");
        check(avgs[1] > 14.49 && avgs[1] < 14.51, "averages row 2");
        free(avgs);
        int *largest = largestValues(
            build((int[]){1, 3, 2, 5, 3, 0, 9}, (bool[]){1, 1, 1, 1, 1, 0, 1}, 7),
            &size);
        check(size == 3 && largest[0] == 1 && largest[1] == 3 && largest[2] == 9,
              "largestValues");
        free(largest);
        largest = largestValues(
            build((int[]){-1, -2, -3}, (bool[]){1, 1, 1}, 3), &size);
        check(size == 2 && largest[0] == -1 && largest[1] == -2,
              "largestValues all negative");
        free(largest);
        check(maxLevelSum(build((int[]){1, 7, 0, 7, -8},
                                (bool[]){1, 1, 1, 1, 1}, 5)) == 2,
              "maxLevelSum");
        check(maxLevelSum(build((int[]){1}, (bool[]){1}, 1)) == 1,
              "maxLevelSum single");
        check(widthOfBinaryTree(build((int[]){1, 3, 2, 5, 3, 0, 9},
                                      (bool[]){1, 1, 1, 1, 1, 0, 1}, 7)) == 4,
              "width");
        check(widthOfBinaryTree(
                  build((int[]){1, 3, 2, 5}, (bool[]){1, 1, 1, 1}, 4)) == 2,
              "width narrow");
        check(widthOfBinaryTree(NULL) == 0, "width empty");
    """,
    "lc-graph": """
        int im0[] = {1, 1, 1};
        int im1[] = {1, 1, 0};
        int im2[] = {1, 0, 1};
        int *image[] = {im0, im1, im2};
        int widths3[] = {3, 3, 3};
        int rows = 0;
        int *outWidths = NULL;
        int **filled = floodFill(image, 3, widths3, 1, 1, 2, &rows, &outWidths);
        check(rows == 3 && filled[0][0] == 2 && filled[1][2] == 0 &&
                  filled[2][2] == 1,
              "floodFill");
        int same0[] = {0, 0};
        int same1[] = {0, 0};
        int *same[] = {same0, same1};
        int widths2[] = {2, 2};
        floodFill(same, 2, widths2, 0, 0, 0, &rows, &outWidths);
        check(same[0][0] == 0, "floodFill same colour");
        char g0[] = "11000";
        char g1[] = "11000";
        char g2[] = "00100";
        char g3[] = "00011";
        char *grid[] = {g0, g1, g2, g3};
        int widths5[] = {5, 5, 5, 5};
        check(numIslands(grid, 4, widths5) == 3, "numIslands");
        char sea0[] = "000";
        char *sea[] = {sea0};
        check(numIslands(sea, 1, widths3) == 0, "numIslands none");
        int o0[] = {2, 1, 1};
        int o1[] = {1, 1, 0};
        int o2[] = {0, 1, 1};
        int *oranges[] = {o0, o1, o2};
        check(orangesRotting(oranges, 3, widths3) == 4, "orangesRotting");
        int s0[] = {2, 1, 1};
        int s1[] = {0, 1, 1};
        int s2[] = {1, 0, 1};
        int *stranded[] = {s0, s1, s2};
        check(orangesRotting(stranded, 3, widths3) == -1,
              "orangesRotting unreachable");
        struct GraphNode a;
        struct GraphNode b;
        struct GraphNode *aNeighbors[1];
        struct GraphNode *bNeighbors[1];
        a.val = 1;
        a.numNeighbors = 1;
        a.neighbors = aNeighbors;
        b.val = 2;
        b.numNeighbors = 1;
        b.neighbors = bNeighbors;
        aNeighbors[0] = &b;
        bNeighbors[0] = &a;
        struct GraphNode *cloned = cloneGraph(&a);
        check(cloned->val == 1, "cloneGraph value");
        check(cloned != &a, "cloneGraph is a copy");
        check(cloned->neighbors[0]->val == 2, "cloneGraph neighbour");
        check(cloned->neighbors[0]->neighbors[0] == cloned,
              "cloneGraph cycle points back at the copy");
        check(cloneGraph(NULL) == NULL, "cloneGraph null");
        int i0[] = {1, 1, 0};
        int i1[] = {1, 0, 0};
        int i2[] = {0, 0, 1};
        int *islands[] = {i0, i1, i2};
        check(maxAreaOfIsland(islands, 3, widths3) == 3, "maxAreaOfIsland");
        int c0[] = {1, 1, 0};
        int c1[] = {1, 1, 0};
        int c2[] = {0, 0, 1};
        int *joined[] = {c0, c1, c2};
        check(findCircleNum(joined, 3, widths3) == 2, "findCircleNum");
        int a0[] = {1, 0, 0};
        int a1[] = {0, 1, 0};
        int a2[] = {0, 0, 1};
        int *apart[] = {a0, a1, a2};
        check(findCircleNum(apart, 3, widths3) == 3, "findCircleNum separate");
        int m0[] = {0, 0, 0};
        int m1[] = {0, 1, 0};
        int m2[] = {1, 1, 1};
        int *mat[] = {m0, m1, m2};
        int **distances = updateMatrix(mat, 3, widths3, &rows, &outWidths);
        check(rows == 3 && distances[1][1] == 1 && distances[2][1] == 2,
              "updateMatrix");
        freeLevels(distances, outWidths, rows);
        int h0[] = {1, 2, 2, 3, 5};
        int h1[] = {3, 2, 3, 4, 4};
        int h2[] = {2, 4, 5, 3, 1};
        int h3[] = {6, 7, 1, 4, 5};
        int h4[] = {5, 1, 1, 2, 4};
        int *heights[] = {h0, h1, h2, h3, h4};
        int widths5b[] = {5, 5, 5, 5, 5};
        int **flows = pacificAtlantic(heights, 5, widths5b, &rows, &outWidths);
        check(rows == 7, "pacificAtlantic count");
        freeLevels(flows, outWidths, rows);
    """,
    "lc-backtracking": """
        int three[] = {1, 2, 3};
        int rows = 0;
        int *widths = NULL;
        int **out = subsets(three, 3, &rows, &widths);
        check(rows == 8, "subsets count");
        freeLevels(out, widths, rows);
        int dupes[] = {1, 2, 2};
        out = subsetsWithDup(dupes, 3, &rows, &widths);
        check(rows == 6, "subsetsWithDup count");
        freeLevels(out, widths, rows);
        int perm[] = {1, 2, 3};
        out = permute(perm, 3, &rows, &widths);
        check(rows == 6, "permute count");
        check(widths[0] == 3, "permute width");
        freeLevels(out, widths, rows);
        int candidates[] = {2, 3, 6, 7};
        out = combinationSum(candidates, 4, 7, &rows, &widths);
        check(rows == 2, "combinationSum count");
        freeLevels(out, widths, rows);
        char b0[] = "ABCE";
        char b1[] = "SFCS";
        char b2[] = "ADEE";
        char *board[] = {b0, b1, b2};
        int widths4[] = {4, 4, 4};
        check(exist(board, 3, widths4, "ABCCED"), "wordSearch found");
        check(!exist(board, 3, widths4, "ABCB"), "wordSearch reuses a cell");
        out = combine(4, 2, &rows, &widths);
        check(rows == 6, "combine count");
        freeLevels(out, widths, rows);
        int found = 0;
        char **letters = letterCombinations("23", &found);
        check(found == 9, "letterCombinations");
        bool sawAd = false;
        for (int i = 0; i < found; i++) {
            if (strcmp(letters[i], "ad") == 0) {
                sawAd = true;
            }
            free(letters[i]);
        }
        check(sawAd, "letterCombinations contains ad");
        free(letters);
        letters = letterCombinations("", &found);
        check(found == 0, "letterCombinations empty");
        char ***cuts = partition("aab", &rows, &widths);
        check(rows == 2, "partition count");
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < widths[i]; j++) {
                free(cuts[i][j]);
            }
            free(cuts[i]);
        }
        free(cuts);
        free(widths);
    """,
    "lc-heap": """
        int nums[] = {3, 2, 1, 5, 6, 4};
        check(findKthLargest(nums, 6, 2) == 5, "findKthLargest");
        int single[] = {1};
        check(findKthLargest(single, 1, 1) == 1, "findKthLargest single");
        int repeated[] = {1, 1, 1, 2, 2, 3};
        int size = 0;
        int *top = topKFrequent(repeated, 6, 2, &size);
        check(size == 2, "topKFrequent count");
        bool sawOne = false;
        bool sawTwo = false;
        for (int i = 0; i < size; i++) {
            if (top[i] == 1) {
                sawOne = true;
            }
            if (top[i] == 2) {
                sawTwo = true;
            }
        }
        check(sawOne && sawTwo, "topKFrequent values");
        free(top);
        int p0[] = {1, 3};
        int p1[] = {-2, 2};
        int *points[] = {p0, p1};
        int widths2[] = {2, 2};
        int rows = 0;
        int *outWidths = NULL;
        int **closest = kClosest(points, 2, widths2, 1, &rows, &outWidths);
        check(rows == 1 && closest[0][0] == -2 && closest[0][1] == 2,
              "kClosest");
        freeLevels(closest, outWidths, rows);
        int stones[] = {2, 7, 4, 1, 8, 1};
        check(lastStoneWeight(stones, 6) == 1, "lastStoneWeight");
        int lone[] = {1};
        check(lastStoneWeight(lone, 1) == 1, "lastStoneWeight one");
        int pairOff[] = {2, 2};
        check(lastStoneWeight(pairOff, 2) == 0, "lastStoneWeight cancel");
        char *words[] = {"i", "love", "leetcode", "i", "love", "coding"};
        char **best = topKFrequentWords(words, 6, 2, &size);
        check(size == 2 && strcmp(best[0], "i") == 0 &&
                  strcmp(best[1], "love") == 0,
              "topKFrequentWords");
        free(best);
        char *tied[] = {"b", "a", "c", "a", "b"};
        best = topKFrequentWords(tied, 5, 2, &size);
        check(strcmp(best[0], "a") == 0 && strcmp(best[1], "b") == 0,
              "topKFrequentWords alphabetical tie-break");
        free(best);
        char *sorted = frequencySort("tree");
        check(strcmp(sorted, "eert") == 0 || strcmp(sorted, "eetr") == 0,
              "frequencySort");
        free(sorted);
        sorted = frequencySort("cccaaa");
        check(strlen(sorted) == 6, "frequencySort length");
        free(sorted);
        int k0[] = {1, 5, 9};
        int k1[] = {10, 11, 13};
        int k2[] = {12, 13, 15};
        int *matrix[] = {k0, k1, k2};
        int widths3[] = {3, 3, 3};
        check(kthSmallest(matrix, 3, widths3, 8) == 13, "kthSmallest");
        int tiny0[] = {-5};
        int *tiny[] = {tiny0};
        int widths1[] = {1};
        check(kthSmallest(tiny, 1, widths1, 1) == -5, "kthSmallest single");
        char *spread = reorganizeString("aab");
        check(strlen(spread) == 3, "reorganizeString length");
        bool adjacent = false;
        for (size_t i = 1; i < strlen(spread); i++) {
            if (spread[i] == spread[i - 1]) {
                adjacent = true;
            }
        }
        check(!adjacent, "reorganizeString has no neighbours alike");
        free(spread);
        spread = reorganizeString("aaab");
        check(strlen(spread) == 0, "reorganizeString impossible");
        free(spread);
    """,
    "lc-topological": """
        int e0[] = {1, 0};
        int *one[] = {e0};
        int widths2[] = {2};
        check(canFinish(2, one, 1, widths2), "canFinish");
        int c0[] = {1, 0};
        int c1[] = {0, 1};
        int *cycle[] = {c0, c1};
        int widths2b[] = {2, 2};
        check(!canFinish(2, cycle, 2, widths2b), "canFinish cycle");
        int size = 0;
        int *order = findOrder(2, one, 1, widths2, &size);
        check(size == 2 && order[0] == 0 && order[1] == 1, "findOrder");
        free(order);
        order = findOrder(2, cycle, 2, widths2b, &size);
        check(size == 0, "findOrder cycle");
        free(order);
        int s0[] = {1, 0};
        int s1[] = {1, 2};
        int s2[] = {1, 3};
        int *star[] = {s0, s1, s2};
        int widths2c[] = {2, 2, 2};
        int *centres = findMinHeightTrees(4, star, 3, widths2c, &size);
        check(size == 1 && centres[0] == 1, "minHeightTrees");
        free(centres);
        centres = findMinHeightTrees(1, NULL, 0, NULL, &size);
        check(size == 1 && centres[0] == 0, "minHeightTrees single");
        free(centres);
        int g0[] = {1, 2};
        int g1[] = {2, 3};
        int g2[] = {5};
        int g3[] = {0};
        int g4[] = {5};
        int *graph[] = {g0, g1, g2, g3, g4, NULL, NULL};
        int graphWidths[] = {2, 2, 1, 1, 1, 0, 0};
        int *safe = eventualSafeNodes(graph, 7, graphWidths, &size);
        check(size == 4 && safe[0] == 2 && safe[1] == 4 && safe[2] == 5 &&
                  safe[3] == 6,
              "safeNodes");
        free(safe);
        int p0[] = {0, 1};
        int p1[] = {1, 2};
        int *chain[] = {p0, p1};
        int q0[] = {0, 2};
        int q1[] = {2, 0};
        int *queries[] = {q0, q1};
        bool *answers = checkIfPrerequisite(3, chain, 2, widths2b, queries, 2,
                                            widths2b, &size);
        check(size == 2 && answers[0] && !answers[1],
              "checkIfPrerequisite transitive");
        free(answers);
        char *recipes[] = {"bread"};
        char *breadNeeds[] = {"yeast", "flour"};
        char **ingredients[] = {breadNeeds};
        int needWidths[] = {2};
        char *supplies[] = {"yeast", "flour", "corn"};
        char **made = findAllRecipes(recipes, 1, ingredients, 1, needWidths,
                                     supplies, 3, &size);
        check(size == 1 && strcmp(made[0], "bread") == 0, "findAllRecipes");
        free(made);
        char *two[] = {"bread", "sandwich"};
        char *sandwichNeeds[] = {"bread", "meat"};
        char **needs[] = {breadNeeds, sandwichNeeds};
        int needWidths2[] = {2, 2};
        char *have[] = {"yeast", "flour", "meat"};
        made = findAllRecipes(two, 2, needs, 2, needWidths2, have, 3, &size);
        check(size == 2 && strcmp(made[1], "sandwich") == 0,
              "findAllRecipes chained");
        free(made);
        int r0[] = {1, 3};
        int r1[] = {2, 3};
        int *parallel[] = {r0, r1};
        check(minimumSemesters(3, parallel, 2, widths2b) == 2,
              "minimumSemesters");
        int l0[] = {1, 2};
        int l1[] = {2, 3};
        int l2[] = {3, 1};
        int *looped[] = {l0, l1, l2};
        check(minimumSemesters(3, looped, 3, widths2c) == -1,
              "minimumSemesters cycle");
        char *alien[] = {"wrt", "wrf", "er", "ett", "rftt"};
        char *letters = alienOrder(alien, 5);
        check(strlen(letters) == 5, "alienOrder");
        free(letters);
        char *prefix[] = {"abc", "ab"};
        letters = alienOrder(prefix, 2);
        check(strlen(letters) == 0, "alienOrder impossible prefix");
        free(letters);
    """,
    "lc-dp": """
        check(climbStairs(2) == 2, "climbStairs 2");
        check(climbStairs(3) == 3, "climbStairs 3");
        check(climbStairs(1) == 1, "climbStairs 1");
        int houses[] = {1, 2, 3, 1};
        check(rob(houses, 4) == 4, "rob");
        int more[] = {2, 7, 9, 3, 1};
        check(rob(more, 5) == 12, "rob longer");
        int coins[] = {1, 3, 4};
        check(coinChange(coins, 3, 6) == 2, "coinChange beats greedy");
        int two[] = {2};
        check(coinChange(two, 1, 3) == -1, "coinChange impossible");
        int penny[] = {1};
        check(coinChange(penny, 1, 0) == 0, "coinChange zero");
        int rising[] = {10, 9, 2, 5, 3, 7, 101, 18};
        check(lengthOfLIS(rising, 8) == 4, "lengthOfLIS");
        int flat[] = {7, 7, 7};
        check(lengthOfLIS(flat, 3) == 1, "lengthOfLIS strict");
        int cost[] = {10, 15, 20};
        check(minCostClimbingStairs(cost, 3) == 15, "minCost");
        int longer[] = {1, 100, 1, 1, 1, 100, 1, 1, 100, 1};
        check(minCostClimbingStairs(longer, 10) == 6, "minCost longer");
        check(longestCommonSubsequence("abcde", "ace") == 3, "lcs");
        check(longestCommonSubsequence("abc", "def") == 0, "lcs none");
        char *dict[] = {"leet", "code"};
        check(wordBreak("leetcode", dict, 2), "wordBreak");
        char *tricky[] = {"cats", "dog", "sand", "and", "cat"};
        check(!wordBreak("catsandog", tricky, 5), "wordBreak no");
        int products[] = {2, 3, -2, 4};
        check(maxProduct(products, 4) == 6, "maxProduct");
        int zeroed[] = {-2, 0, -1};
        check(maxProduct(zeroed, 3) == 0, "maxProduct zero");
        int negatives[] = {-2, 3, -4};
        check(maxProduct(negatives, 3) == 24, "maxProduct two negatives");
    """,
}

LIST_HELPERS = """
static struct ListNode *build(int *values, int count) {
    struct ListNode head;
    head.next = NULL;
    struct ListNode *tail = &head;
    for (int i = 0; i < count; i++) {
        tail->next = malloc(sizeof(struct ListNode));
        tail->next->val = values[i];
        tail->next->next = NULL;
        tail = tail->next;
    }
    return head.next;
}

static bool sameList(struct ListNode *node, int *values, int count) {
    for (int i = 0; i < count; i++) {
        if (!node || node->val != values[i]) {
            return false;
        }
        node = node->next;
    }
    return node == NULL;
}
"""

BAD_VERSION = """
static bool badFrom4(int v) { return v >= 4; }
static bool badFrom1(int v) { return v >= 1; }
"""

# Built from a level-order list with a parallel present/absent array, since C
# has nothing like an optional. Reads the way LeetCode prints its trees.
TREE_HELPERS = """
static struct TreeNode *build(int *values, bool *present, int count) {
    if (count == 0 || !present[0]) {
        return NULL;
    }
    struct TreeNode **made = calloc(count, sizeof(struct TreeNode *));
    for (int i = 0; i < count; i++) {
        if (present[i]) {
            made[i] = malloc(sizeof(struct TreeNode));
            made[i]->val = values[i];
            made[i]->left = NULL;
            made[i]->right = NULL;
        }
    }
    struct TreeNode **queue = malloc(count * sizeof(struct TreeNode *));
    int head = 0;
    int tail = 0;
    queue[tail++] = made[0];
    int i = 1;
    while (i < count && head < tail) {
        struct TreeNode *parent = queue[head++];
        if (i < count) {
            if (present[i]) {
                parent->left = made[i];
                queue[tail++] = made[i];
            }
            i++;
        }
        if (i < count) {
            if (present[i]) {
                parent->right = made[i];
                queue[tail++] = made[i];
            }
            i++;
        }
    }
    struct TreeNode *root = made[0];
    free(queue);
    free(made);
    return root;
}
"""

FREE_LEVELS = """
static void freeLevels(int **levels, int *widths, int rows) {
    for (int i = 0; i < rows; i++) {
        free(levels[i]);
    }
    free(levels);
    free(widths);
}
"""

HELPERS_FOR = {
    "lc-linked-list": [LIST_HELPERS],
    "lc-binary-search": [BAD_VERSION],
    "lc-tree-dfs": [TREE_HELPERS],
    "lc-tree-bfs": [TREE_HELPERS, FREE_LEVELS],
    "lc-graph": [FREE_LEVELS],
    "lc-backtracking": [FREE_LEVELS],
    "lc-heap": [FREE_LEVELS],
}

# A tiny assert that names itself. A green run prints only the last line.
HARNESS = """
#include <stdio.h>
static int failures = 0;
static void check(bool ok, const char *label) {
    if (!ok) {
        printf("FAILED: %s\\n", label);
        failures++;
    }
}
"""

REPORT = """
    if (failures) {
        return 1;
    }
    printf("ok\\n");
    return 0;
"""


@unittest.skipUnless(HAS_C, "needs gcc, clang, or an MSVC install")
class CSolutionTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.append(HARNESS)
        parts.extend(HELPERS_FOR.get(pattern_id, []))
        parts.extend(p.code for p in pattern.problems)
        parts.append("int main(void) {\n" + CHECKS[pattern_id] + REPORT + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="c")
        self.assertEqual(code, 0, (err or out)[:2500])
        self.assertEqual(out.strip(), "ok", out[:2500])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class CoverageTests(unittest.TestCase):
    def test_every_pattern_present_has_checks(self) -> None:
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_it_covers_every_problem(self) -> None:
        from code_coach.leetcode.problems import all_problems

        theirs = sorted(p.number for p in all_problems())
        mine = sorted(p.number for pat in PATTERNS for p in pat.problems)
        self.assertEqual(mine, theirs)

    def test_every_pattern_mirrors_the_python_bank(self) -> None:
        from code_coach.leetcode.problems import PATTERNS_BY_ID as PY

        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                theirs = [p.number for p in PY[pattern.id].problems]
                self.assertEqual([p.number for p in pattern.problems], theirs)
                titles = [p.title for p in PY[pattern.id].problems]
                self.assertEqual([p.title for p in pattern.problems], titles)


if __name__ == "__main__":
    unittest.main()
