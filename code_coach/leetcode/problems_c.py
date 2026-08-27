"""
The same LeetCode patterns, written in C.

Mirrors `problems.py` problem for problem, so switching language keeps your
place in the curriculum. The algorithm is identical; what changes is
everything the standard library used to do for you.

The signatures are LeetCode's own. An array arrives as a pointer and a length,
and leaves as something you malloc with its length written through
`returnSize`. That bookkeeping IS the C exercise, so it is not smoothed over —
but the hash map is shared from `c_common`, because writing the same chained
table eight times teaches nothing except that C is tiring.

Every solution is compiled and run against real cases by
tests/test_c_solutions.py.
"""

from __future__ import annotations

from code_coach.leetcode.c_common import (
    COPY_STRING,
    CTYPE,
    INT_MAP,
    LIMITS,
    STDBOOL,
    STDLIB,
    STRING_H,
    _p,
)
from code_coach.leetcode.problems import Pattern

# ── 1. Hash maps ────────────────────────────────────────────

_HASH_MAP = Pattern(
    id="lc-hashmap",
    name="Hash Maps",
    order=1,
    blurb="Trade memory for speed: remember what you've seen in a map or set.",
    tell="You'd otherwise need a nested loop to ask 'have I seen this before?'",
    preamble=(STDLIB, STRING_H, STDBOOL, COPY_STRING, INT_MAP),
    problems=(
        _p(
            1, "Two Sum", "Easy",
            "Store each number's index as you pass it, then look up the "
            "complement. The answer is malloc'd and its length written back.",
            "O(n) time, O(n) space",
            """
            int *twoSum(int *nums, int numsSize, int target, int *returnSize) {
                IntMap *seen = mapNew();
                for (int i = 0; i < numsSize; i++) {
                    int found;
                    if (mapGet(seen, target - nums[i], &found)) {
                        int *out = malloc(2 * sizeof(int));
                        out[0] = found;
                        out[1] = i;
                        *returnSize = 2;
                        mapFree(seen);
                        return out;
                    }
                    mapPut(seen, nums[i], i);
                }
                mapFree(seen);
                *returnSize = 0;
                return NULL;
            }
            """,
        ),
        _p(
            217, "Contains Duplicate", "Easy",
            "A map used only for its keys is a set.",
            "O(n) time, O(n) space",
            """
            bool containsDuplicate(int *nums, int numsSize) {
                IntMap *seen = mapNew();
                for (int i = 0; i < numsSize; i++) {
                    int ignored;
                    if (mapGet(seen, nums[i], &ignored)) {
                        mapFree(seen);
                        return true;
                    }
                    mapPut(seen, nums[i], 1);
                }
                mapFree(seen);
                return false;
            }
            """,
        ),
        _p(
            242, "Valid Anagram", "Easy",
            "Only 26 letters, so a plain array beats a hash map - no hashing, "
            "no allocation, and the index is the letter.",
            "O(n) time, O(1) space",
            """
            bool isAnagram(char *s, char *t) {
                if (strlen(s) != strlen(t)) {
                    return false;
                }
                int counts[26] = {0};
                for (int i = 0; s[i]; i++) {
                    counts[s[i] - 'a']++;
                }
                for (int i = 0; t[i]; i++) {
                    if (counts[t[i] - 'a'] == 0) {
                        return false;
                    }
                    counts[t[i] - 'a']--;
                }
                return true;
            }
            """,
        ),
        _p(
            49, "Group Anagrams", "Medium",
            "Sorted letters make a key all anagrams share. With no map from "
            "string to list, compare each word against the group heads.",
            "O(n k log k) time, O(n k) space",
            """
            static int byLetter(const void *a, const void *b) {
                return *(const char *)a - *(const char *)b;
            }

            char ***groupAnagrams(char **strs, int strsSize, int *returnSize,
                                  int **columnSizes) {
                char **keys = malloc(strsSize * sizeof(char *));
                char ***groups = malloc(strsSize * sizeof(char **));
                int *sizes = malloc(strsSize * sizeof(int));
                int total = 0;
                for (int i = 0; i < strsSize; i++) {
                    char *key = copyString(strs[i]);
                    qsort(key, strlen(key), sizeof(char), byLetter);
                    int at = -1;
                    for (int g = 0; g < total; g++) {
                        if (strcmp(keys[g], key) == 0) {
                            at = g;
                            break;
                        }
                    }
                    if (at < 0) {
                        at = total++;
                        keys[at] = key;
                        groups[at] = malloc(strsSize * sizeof(char *));
                        sizes[at] = 0;
                    } else {
                        free(key);
                    }
                    groups[at][sizes[at]++] = strs[i];
                }
                for (int g = 0; g < total; g++) {
                    free(keys[g]);
                }
                free(keys);
                *returnSize = total;
                *columnSizes = sizes;
                return groups;
            }
            """,
        ),
        _p(
            454, "4Sum II", "Medium",
            "Count every sum from the first two lists, then look up its negation "
            "from the other two.",
            "O(n^2) time, O(n^2) space",
            """
            int fourSumCount(int *a, int aSize, int *b, int bSize, int *c,
                             int cSize, int *d, int dSize) {
                IntMap *pairs = mapNew();
                for (int i = 0; i < aSize; i++) {
                    for (int j = 0; j < bSize; j++) {
                        mapBump(pairs, a[i] + b[j], 1);
                    }
                }
                int found = 0;
                for (int i = 0; i < cSize; i++) {
                    for (int j = 0; j < dSize; j++) {
                        found += mapCount(pairs, -(c[i] + d[j]));
                    }
                }
                mapFree(pairs);
                return found;
            }
            """,
        ),
        _p(
            560, "Subarray Sum Equals K", "Medium",
            "Remember every running total you've seen; the gap between two of "
            "them is a subarray.",
            "O(n) time, O(n) space",
            """
            int subarraySum(int *nums, int numsSize, int k) {
                IntMap *seen = mapNew();
                mapPut(seen, 0, 1);
                int running = 0;
                int found = 0;
                for (int i = 0; i < numsSize; i++) {
                    running += nums[i];
                    found += mapCount(seen, running - k);
                    mapBump(seen, running, 1);
                }
                mapFree(seen);
                return found;
            }
            """,
        ),
        _p(
            128, "Longest Consecutive Sequence", "Medium",
            "Only start counting from a number with no left neighbour - each run "
            "is walked once.",
            "O(n) time, O(n) space",
            """
            int longestConsecutive(int *nums, int numsSize) {
                IntMap *pool = mapNew();
                for (int i = 0; i < numsSize; i++) {
                    mapPut(pool, nums[i], 1);
                }
                int best = 0;
                for (int i = 0; i < numsSize; i++) {
                    int ignored;
                    if (mapGet(pool, nums[i] - 1, &ignored)) {
                        continue;
                    }
                    int length = 1;
                    while (mapGet(pool, nums[i] + length, &ignored)) {
                        length++;
                    }
                    if (length > best) {
                        best = length;
                    }
                }
                mapFree(pool);
                return best;
            }
            """,
        ),
        _p(
            36, "Valid Sudoku", "Medium",
            "Nine digits and nine groups, so three flat arrays of bools do the "
            "whole job - no hashing needed at all.",
            "O(1) time, O(1) space",
            """
            bool isValidSudoku(char **board, int boardSize, int *boardColSize) {
                bool rows[9][9] = {{false}};
                bool cols[9][9] = {{false}};
                bool boxes[9][9] = {{false}};
                for (int r = 0; r < 9; r++) {
                    for (int c = 0; c < 9; c++) {
                        char value = board[r][c];
                        if (value == '.') {
                            continue;
                        }
                        int digit = value - '1';
                        int b = (r / 3) * 3 + c / 3;
                        if (rows[r][digit] || cols[c][digit] ||
                            boxes[b][digit]) {
                            return false;
                        }
                        rows[r][digit] = true;
                        cols[c][digit] = true;
                        boxes[b][digit] = true;
                    }
                }
                return true;
            }
            """,
        ),
    ),
)


# ── 2. Two pointers ─────────────────────────────────────────

_TWO_POINTERS = Pattern(
    id="lc-two-pointers",
    name="Two Pointers",
    order=2,
    blurb="Walk two indexes toward each other (or together) instead of nesting loops.",
    tell="The input is sorted, or you care about pairs from opposite ends.",
    preamble=(STDLIB, STRING_H, STDBOOL, CTYPE),
    problems=(
        _p(
            125, "Valid Palindrome", "Easy",
            "Skip non-letters from both ends and compare inward.",
            "O(n) time, O(1) space",
            """
            bool isPalindrome(char *s) {
                int left = 0;
                int right = (int)strlen(s) - 1;
                while (left < right) {
                    while (left < right && !isalnum((unsigned char)s[left])) {
                        left++;
                    }
                    while (left < right && !isalnum((unsigned char)s[right])) {
                        right--;
                    }
                    if (tolower((unsigned char)s[left]) !=
                        tolower((unsigned char)s[right])) {
                        return false;
                    }
                    left++;
                    right--;
                }
                return true;
            }
            """,
        ),
        _p(
            167, "Two Sum II (sorted)", "Medium",
            "Too big? Move right in. Too small? Move left out.",
            "O(n) time, O(1) space",
            """
            int *twoSumSorted(int *numbers, int numbersSize, int target,
                              int *returnSize) {
                int left = 0;
                int right = numbersSize - 1;
                while (left < right) {
                    int total = numbers[left] + numbers[right];
                    if (total == target) {
                        int *out = malloc(2 * sizeof(int));
                        out[0] = left + 1;
                        out[1] = right + 1;
                        *returnSize = 2;
                        return out;
                    }
                    if (total < target) {
                        left++;
                    } else {
                        right--;
                    }
                }
                *returnSize = 0;
                return NULL;
            }
            """,
        ),
        _p(
            11, "Container With Most Water", "Medium",
            "Always move the shorter wall - the taller one can't help you.",
            "O(n) time, O(1) space",
            """
            int maxArea(int *height, int heightSize) {
                int left = 0;
                int right = heightSize - 1;
                int best = 0;
                while (left < right) {
                    int shorter = height[left] < height[right] ? height[left]
                                                               : height[right];
                    int area = (right - left) * shorter;
                    if (area > best) {
                        best = area;
                    }
                    if (height[left] < height[right]) {
                        left++;
                    } else {
                        right--;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            15, "3Sum", "Medium",
            "Sort, fix one number, then two-pointer the rest for its negative. "
            "The answer is an array of arrays, so both sizes travel back.",
            "O(n^2) time, O(1) extra space",
            """
            static int ascending(const void *a, const void *b) {
                int x = *(const int *)a;
                int y = *(const int *)b;
                return (x > y) - (x < y);
            }

            int **threeSum(int *nums, int numsSize, int *returnSize,
                           int **columnSizes) {
                qsort(nums, numsSize, sizeof(int), ascending);
                int capacity = 16;
                int **result = malloc(capacity * sizeof(int *));
                int total = 0;
                for (int i = 0; i + 2 < numsSize; i++) {
                    if (i > 0 && nums[i] == nums[i - 1]) {
                        continue;
                    }
                    int left = i + 1;
                    int right = numsSize - 1;
                    while (left < right) {
                        int sum = nums[i] + nums[left] + nums[right];
                        if (sum < 0) {
                            left++;
                        } else if (sum > 0) {
                            right--;
                        } else {
                            if (total == capacity) {
                                capacity *= 2;
                                result = realloc(result,
                                                 capacity * sizeof(int *));
                            }
                            int *triple = malloc(3 * sizeof(int));
                            triple[0] = nums[i];
                            triple[1] = nums[left];
                            triple[2] = nums[right];
                            result[total++] = triple;
                            left++;
                            while (left < right && nums[left] == nums[left - 1]) {
                                left++;
                            }
                        }
                    }
                }
                int *sizes = malloc(total * sizeof(int));
                for (int i = 0; i < total; i++) {
                    sizes[i] = 3;
                }
                *returnSize = total;
                *columnSizes = sizes;
                return result;
            }
            """,
        ),
        _p(
            26, "Remove Duplicates from Sorted Array", "Easy",
            "One pointer writes, the other reads - the writer only moves on a "
            "new value.",
            "O(n) time, O(1) space",
            """
            int removeDuplicates(int *nums, int numsSize) {
                if (numsSize == 0) {
                    return 0;
                }
                int write = 1;
                for (int read = 1; read < numsSize; read++) {
                    if (nums[read] != nums[write - 1]) {
                        nums[write] = nums[read];
                        write++;
                    }
                }
                return write;
            }
            """,
        ),
        _p(
            283, "Move Zeroes", "Easy",
            "Same read/write pair: write every non-zero forward, then fill the tail.",
            "O(n) time, O(1) space",
            """
            void moveZeroes(int *nums, int numsSize) {
                int write = 0;
                for (int read = 0; read < numsSize; read++) {
                    if (nums[read] != 0) {
                        nums[write] = nums[read];
                        write++;
                    }
                }
                while (write < numsSize) {
                    nums[write] = 0;
                    write++;
                }
            }
            """,
        ),
        _p(
            42, "Trapping Rain Water", "Hard",
            "Water over a column is the smaller of the two tallest walls beside "
            "it, minus the column.",
            "O(n) time, O(1) space",
            """
            int trap(int *height, int heightSize) {
                if (heightSize == 0) {
                    return 0;
                }
                int left = 0;
                int right = heightSize - 1;
                int leftMax = height[left];
                int rightMax = height[right];
                int water = 0;
                while (left < right) {
                    if (leftMax < rightMax) {
                        left++;
                        if (height[left] > leftMax) {
                            leftMax = height[left];
                        }
                        water += leftMax - height[left];
                    } else {
                        right--;
                        if (height[right] > rightMax) {
                            rightMax = height[right];
                        }
                        water += rightMax - height[right];
                    }
                }
                return water;
            }
            """,
        ),
        _p(
            977, "Squares of a Sorted Array", "Easy",
            "The biggest square is at one end or the other, so fill the answer "
            "backwards.",
            "O(n) time, O(n) space",
            """
            int *sortedSquares(int *nums, int numsSize, int *returnSize) {
                int *out = malloc(numsSize * sizeof(int));
                int left = 0;
                int right = numsSize - 1;
                for (int slot = numsSize - 1; slot >= 0; slot--) {
                    if (abs(nums[left]) > abs(nums[right])) {
                        out[slot] = nums[left] * nums[left];
                        left++;
                    } else {
                        out[slot] = nums[right] * nums[right];
                        right--;
                    }
                }
                *returnSize = numsSize;
                return out;
            }
            """,
        ),
    ),
)


# ── 3. Sliding window ───────────────────────────────────────

_SLIDING_WINDOW = Pattern(
    id="lc-sliding-window",
    name="Sliding Window",
    order=3,
    blurb="One pass, two edges: grow the window, then shrink it while it still qualifies.",
    tell="You want the best or shortest run of adjacent items.",
    preamble=(STDLIB, STRING_H, STDBOOL, LIMITS, COPY_STRING),
    problems=(
        _p(
            121, "Best Time to Buy and Sell Stock", "Easy",
            "Track the cheapest price so far; every day ask what selling today pays.",
            "O(n) time, O(1) space",
            """
            int maxProfit(int *prices, int pricesSize) {
                int best = 0;
                int cheapest = INT_MAX;
                for (int i = 0; i < pricesSize; i++) {
                    if (prices[i] < cheapest) {
                        cheapest = prices[i];
                    }
                    if (prices[i] - cheapest > best) {
                        best = prices[i] - cheapest;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            3, "Longest Substring Without Repeating Characters", "Medium",
            "On a repeat, jump the window start past the previous copy. 128 "
            "slots covers ASCII, so no hash map is needed.",
            "O(n) time, O(1) space",
            """
            int lengthOfLongestSubstring(char *s) {
                int lastSeen[128];
                for (int i = 0; i < 128; i++) {
                    lastSeen[i] = -1;
                }
                int start = 0;
                int best = 0;
                for (int i = 0; s[i]; i++) {
                    int previous = lastSeen[(unsigned char)s[i]];
                    if (previous >= start) {
                        start = previous + 1;
                    }
                    lastSeen[(unsigned char)s[i]] = i;
                    if (i - start + 1 > best) {
                        best = i - start + 1;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            209, "Minimum Size Subarray Sum", "Medium",
            "Grow right always; shrink left while the window still qualifies.",
            "O(n) time, O(1) space",
            """
            int minSubArrayLen(int target, int *nums, int numsSize) {
                int left = 0;
                int total = 0;
                int best = numsSize + 1;
                for (int right = 0; right < numsSize; right++) {
                    total += nums[right];
                    while (total >= target) {
                        if (right - left + 1 < best) {
                            best = right - left + 1;
                        }
                        total -= nums[left];
                        left++;
                    }
                }
                return best <= numsSize ? best : 0;
            }
            """,
        ),
        _p(
            424, "Longest Repeating Character Replacement", "Medium",
            "A window is legal when (size - most common letter) <= k.",
            "O(n) time, O(1) space",
            """
            int characterReplacement(char *s, int k) {
                int counts[26] = {0};
                int left = 0;
                int mostCommon = 0;
                int best = 0;
                for (int right = 0; s[right]; right++) {
                    counts[s[right] - 'A']++;
                    if (counts[s[right] - 'A'] > mostCommon) {
                        mostCommon = counts[s[right] - 'A'];
                    }
                    while ((right - left + 1) - mostCommon > k) {
                        counts[s[left] - 'A']--;
                        left++;
                    }
                    if (right - left + 1 > best) {
                        best = right - left + 1;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            643, "Maximum Average Subarray I", "Easy",
            "The window never changes size, so each step adds one number and "
            "drops one.",
            "O(n) time, O(1) space",
            """
            double findMaxAverage(int *nums, int numsSize, int k) {
                int window = 0;
                for (int i = 0; i < k; i++) {
                    window += nums[i];
                }
                int best = window;
                for (int i = k; i < numsSize; i++) {
                    window += nums[i] - nums[i - k];
                    if (window > best) {
                        best = window;
                    }
                }
                return (double)best / k;
            }
            """,
        ),
        _p(
            567, "Permutation in String", "Medium",
            "A fixed window whose letter counts match is a permutation - and "
            "with 26 letters, memcmp answers that in one call.",
            "O(n) time, O(1) space",
            """
            bool checkInclusion(char *pattern, char *text) {
                int patternLength = (int)strlen(pattern);
                int textLength = (int)strlen(text);
                if (patternLength > textLength) {
                    return false;
                }
                int need[26] = {0};
                int window[26] = {0};
                for (int i = 0; i < patternLength; i++) {
                    need[pattern[i] - 'a']++;
                }
                for (int i = 0; i < textLength; i++) {
                    window[text[i] - 'a']++;
                    if (i >= patternLength) {
                        window[text[i - patternLength] - 'a']--;
                    }
                    if (memcmp(need, window, sizeof(need)) == 0) {
                        return true;
                    }
                }
                return false;
            }
            """,
        ),
        _p(
            1004, "Max Consecutive Ones III", "Medium",
            "Grow while at most k zeros are inside; shrink from the left when a "
            "k+1th appears.",
            "O(n) time, O(1) space",
            """
            int longestOnes(int *nums, int numsSize, int k) {
                int left = 0;
                int zeros = 0;
                int best = 0;
                for (int right = 0; right < numsSize; right++) {
                    if (nums[right] == 0) {
                        zeros++;
                    }
                    while (zeros > k) {
                        if (nums[left] == 0) {
                            zeros--;
                        }
                        left++;
                    }
                    if (right - left + 1 > best) {
                        best = right - left + 1;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            76, "Minimum Window Substring", "Hard",
            "Count how many required letters are satisfied; shrink only while all "
            "of them are. The answer is a fresh string, so it is malloc'd.",
            "O(n) time, O(1) space",
            """
            char *minWindow(char *text, char *pattern) {
                int textLength = (int)strlen(text);
                int patternLength = (int)strlen(pattern);
                if (patternLength == 0 || textLength == 0) {
                    return copyString("");
                }
                int need[128] = {0};
                int window[128] = {0};
                int missing = 0;
                for (int i = 0; i < patternLength; i++) {
                    if (need[(unsigned char)pattern[i]]++ == 0) {
                        missing++;
                    }
                }
                int bestStart = 0;
                int bestLength = 0;
                int left = 0;
                for (int right = 0; right < textLength; right++) {
                    unsigned char ch = (unsigned char)text[right];
                    window[ch]++;
                    if (need[ch] && window[ch] == need[ch]) {
                        missing--;
                    }
                    while (missing == 0) {
                        if (bestLength == 0 || right - left + 1 < bestLength) {
                            bestStart = left;
                            bestLength = right - left + 1;
                        }
                        unsigned char out = (unsigned char)text[left];
                        window[out]--;
                        if (need[out] && window[out] < need[out]) {
                            missing++;
                        }
                        left++;
                    }
                }
                char *answer = malloc(bestLength + 1);
                memcpy(answer, text + bestStart, bestLength);
                answer[bestLength] = '\\0';
                return answer;
            }
            """,
        ),
    ),
)


# ── 4. Stacks ───────────────────────────────────────────────

_STACK = Pattern(
    id="lc-stack",
    name="Stacks",
    order=4,
    blurb="Last in, first out: the right shape whenever the most recent thing matters.",
    tell="You need to match, undo, or look back at the nearest previous item.",
    preamble=(STDLIB, STRING_H, STDBOOL, CTYPE, COPY_STRING),
    problems=(
        _p(
            20, "Valid Parentheses", "Easy",
            "Push openers; every closer must match the most recent opener. The "
            "stack can never outgrow the input, so one malloc does it.",
            "O(n) time, O(n) space",
            """
            bool isValid(char *s) {
                int length = (int)strlen(s);
                char *stack = malloc(length + 1);
                int top = 0;
                bool ok = true;
                for (int i = 0; i < length; i++) {
                    char ch = s[i];
                    if (ch == '(' || ch == '[' || ch == '{') {
                        stack[top++] = ch;
                    } else {
                        char want = ch == ')' ? '(' : (ch == ']' ? '[' : '{');
                        if (top == 0 || stack[--top] != want) {
                            ok = false;
                            break;
                        }
                    }
                }
                if (top != 0) {
                    ok = false;
                }
                free(stack);
                return ok;
            }
            """,
        ),
        _p(
            155, "Min Stack", "Medium",
            "Keep a parallel stack of 'the minimum as of this push'. In C the "
            "object is a struct you allocate and free yourself.",
            "O(1) per operation, O(n) space",
            """
            #define MIN_STACK_CAP 10000

            typedef struct {
                int *values;
                int *mins;
                int size;
                int minSize;
            } MinStack;

            MinStack *minStackCreate(void) {
                MinStack *stack = malloc(sizeof(MinStack));
                stack->values = malloc(MIN_STACK_CAP * sizeof(int));
                stack->mins = malloc(MIN_STACK_CAP * sizeof(int));
                stack->size = 0;
                stack->minSize = 0;
                return stack;
            }

            void minStackPush(MinStack *stack, int val) {
                stack->values[stack->size++] = val;
                if (stack->minSize == 0 ||
                    val <= stack->mins[stack->minSize - 1]) {
                    stack->mins[stack->minSize++] = val;
                }
            }

            void minStackPop(MinStack *stack) {
                int val = stack->values[--stack->size];
                if (stack->minSize > 0 &&
                    val == stack->mins[stack->minSize - 1]) {
                    stack->minSize--;
                }
            }

            int minStackTop(MinStack *stack) {
                return stack->values[stack->size - 1];
            }

            int minStackGetMin(MinStack *stack) {
                return stack->mins[stack->minSize - 1];
            }

            void minStackFree(MinStack *stack) {
                free(stack->values);
                free(stack->mins);
                free(stack);
            }
            """,
        ),
        _p(
            150, "Evaluate Reverse Polish Notation", "Medium",
            "Numbers go on the stack; an operator pops two and pushes the result.",
            "O(n) time, O(n) space",
            """
            int evalRPN(char **tokens, int tokensSize) {
                int *stack = malloc(tokensSize * sizeof(int));
                int top = 0;
                for (int i = 0; i < tokensSize; i++) {
                    char *token = tokens[i];
                    bool isOperator = token[1] == '\\0' &&
                                      strchr("+-*/", token[0]) != NULL;
                    if (isOperator) {
                        int b = stack[--top];
                        int a = stack[--top];
                        switch (token[0]) {
                            case '+': stack[top++] = a + b; break;
                            case '-': stack[top++] = a - b; break;
                            case '*': stack[top++] = a * b; break;
                            default: stack[top++] = a / b; break;
                        }
                    } else {
                        stack[top++] = atoi(token);
                    }
                }
                int answer = stack[0];
                free(stack);
                return answer;
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Monotonic stack of indexes still waiting for a warmer day.",
            "O(n) time, O(n) space",
            """
            int *dailyTemperatures(int *temperatures, int temperaturesSize,
                                   int *returnSize) {
                int *answer = calloc(temperaturesSize, sizeof(int));
                int *stack = malloc(temperaturesSize * sizeof(int));
                int top = 0;
                for (int i = 0; i < temperaturesSize; i++) {
                    while (top > 0 &&
                           temperatures[stack[top - 1]] < temperatures[i]) {
                        int prev = stack[--top];
                        answer[prev] = i - prev;
                    }
                    stack[top++] = i;
                }
                free(stack);
                *returnSize = temperaturesSize;
                return answer;
            }
            """,
        ),
        _p(
            682, "Baseball Game", "Easy",
            "Every operation only ever looks at the top of the stack, which is "
            "the whole idea.",
            "O(n) time, O(n) space",
            """
            int calPoints(char **operations, int operationsSize) {
                int *stack = malloc(operationsSize * sizeof(int));
                int top = 0;
                for (int i = 0; i < operationsSize; i++) {
                    char *op = operations[i];
                    if (strcmp(op, "C") == 0) {
                        top--;
                    } else if (strcmp(op, "D") == 0) {
                        stack[top] = stack[top - 1] * 2;
                        top++;
                    } else if (strcmp(op, "+") == 0) {
                        stack[top] = stack[top - 1] + stack[top - 2];
                        top++;
                    } else {
                        stack[top++] = atoi(op);
                    }
                }
                int total = 0;
                for (int i = 0; i < top; i++) {
                    total += stack[i];
                }
                free(stack);
                return total;
            }
            """,
        ),
        _p(
            71, "Simplify Path", "Medium",
            "A '..' pops the directory before it. Remember where each name sits "
            "rather than copying it, and build the answer in one pass.",
            "O(n) time, O(n) space",
            """
            char *simplifyPath(char *path) {
                int length = (int)strlen(path);
                int *starts = malloc((length + 1) * sizeof(int));
                int *lengths = malloc((length + 1) * sizeof(int));
                int top = 0;
                int i = 0;
                while (i <= length) {
                    if (i == length || path[i] == '/') {
                        i++;
                        continue;
                    }
                    int from = i;
                    while (i < length && path[i] != '/') {
                        i++;
                    }
                    int size = i - from;
                    bool dot = size == 1 && path[from] == '.';
                    bool up = size == 2 && path[from] == '.' &&
                              path[from + 1] == '.';
                    if (up) {
                        if (top > 0) {
                            top--;
                        }
                    } else if (!dot) {
                        starts[top] = from;
                        lengths[top] = size;
                        top++;
                    }
                }
                char *out = malloc(length + 2);
                int at = 0;
                for (int part = 0; part < top; part++) {
                    out[at++] = '/';
                    memcpy(out + at, path + starts[part], lengths[part]);
                    at += lengths[part];
                }
                if (at == 0) {
                    out[at++] = '/';
                }
                out[at] = '\\0';
                free(starts);
                free(lengths);
                return out;
            }
            """,
        ),
        _p(
            84, "Largest Rectangle in Histogram", "Hard",
            "Keep bars increasing; a shorter one closes off every taller bar "
            "behind it. A sentinel zero at the end settles the rest.",
            "O(n) time, O(n) space",
            """
            int largestRectangleArea(int *heights, int heightsSize) {
                int *starts = malloc((heightsSize + 1) * sizeof(int));
                int *talls = malloc((heightsSize + 1) * sizeof(int));
                int top = 0;
                int best = 0;
                for (int i = 0; i <= heightsSize; i++) {
                    int height = i == heightsSize ? 0 : heights[i];
                    int start = i;
                    while (top > 0 && talls[top - 1] > height) {
                        top--;
                        int area = talls[top] * (i - starts[top]);
                        if (area > best) {
                            best = area;
                        }
                        start = starts[top];
                    }
                    starts[top] = start;
                    talls[top] = height;
                    top++;
                }
                free(starts);
                free(talls);
                return best;
            }
            """,
        ),
        _p(
            394, "Decode String", "Medium",
            "Push the work in progress when a bracket opens, finish it when one "
            "closes. A length-tracking builder keeps the appending linear.",
            "O(n) time, O(n) space",
            """
            typedef struct {
                char *text;
                size_t length;
                size_t capacity;
            } Builder;

            static Builder builderNew(void) {
                Builder b;
                b.capacity = 16;
                b.length = 0;
                b.text = malloc(b.capacity);
                b.text[0] = '\\0';
                return b;
            }

            static void builderAppend(Builder *b, const char *text,
                                      size_t size) {
                while (b->length + size + 1 > b->capacity) {
                    b->capacity *= 2;
                    b->text = realloc(b->text, b->capacity);
                }
                memcpy(b->text + b->length, text, size);
                b->length += size;
                b->text[b->length] = '\\0';
            }

            char *decodeString(char *encoded) {
                int length = (int)strlen(encoded);
                Builder current = builderNew();
                Builder *saved = malloc((length + 1) * sizeof(Builder));
                int *counts = malloc((length + 1) * sizeof(int));
                int depth = 0;
                int count = 0;
                for (int i = 0; i < length; i++) {
                    char ch = encoded[i];
                    if (isdigit((unsigned char)ch)) {
                        count = count * 10 + (ch - '0');
                    } else if (ch == '[') {
                        saved[depth] = current;
                        counts[depth] = count;
                        depth++;
                        current = builderNew();
                        count = 0;
                    } else if (ch == ']') {
                        depth--;
                        Builder before = saved[depth];
                        int times = counts[depth];
                        for (int t = 0; t < times; t++) {
                            builderAppend(&before, current.text,
                                          current.length);
                        }
                        free(current.text);
                        current = before;
                    } else {
                        builderAppend(&current, &ch, 1);
                    }
                }
                free(saved);
                free(counts);
                return current.text;
            }
            """,
        ),
    ),
)


# Patterns 5 to 8 live in problems_c2, 9 to 13 in problems_c3, to keep each
# file a readable length; PATTERNS below stitches them together.
from code_coach.leetcode.problems_c2 import (  # noqa: E402
    _BINARY_SEARCH,
    _LINKED_LIST,
    _TREE_BFS,
    _TREE_DFS,
)
from code_coach.leetcode.problems_c3 import (  # noqa: E402
    _DP,
    _GRAPH,
    _HEAP,
    _SUBSETS,
    _TOPOLOGICAL,
)

PATTERNS: tuple[Pattern, ...] = (
    _HASH_MAP,
    _TWO_POINTERS,
    _SLIDING_WINDOW,
    _STACK,
    _LINKED_LIST,
    _BINARY_SEARCH,
    _TREE_DFS,
    _TREE_BFS,
    _GRAPH,
    _SUBSETS,
    _HEAP,
    _TOPOLOGICAL,
    _DP,
)
