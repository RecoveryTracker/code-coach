"""
The same LeetCode patterns, written in C++.

Mirrors `problems.py` problem for problem, so switching language keeps your
place in the curriculum. The algorithms are identical; what changes is the
idiom — `unordered_map` and `unordered_set`, `vector<int>` for a list,
`size_t` where an index is compared against `.size()`, and a `&` on a
parameter to avoid copying a container you only mean to read.

The signatures are LeetCode's own: containers by value, `string` rather than
`const char*`, raw `ListNode*` and `TreeNode*`. Free functions rather than a
`Solution` class, which is how the other language banks here are written.

Every solution is compiled and run against real cases by
tests/test_cpp_solutions.py. Nothing here is a solution that has only been
read.
"""

from __future__ import annotations

from code_coach.leetcode.cpp_common import (
    ALGORITHM,
    CLIMITS,
    MAPS,
    STRING,
    USING,
    VECTOR,
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
    preamble=(VECTOR, STRING, MAPS, ALGORITHM, USING),
    problems=(
        _p(
            1, "Two Sum", "Easy",
            "Store each number's index as you pass it, then look up the complement.",
            "O(n) time, O(n) space",
            """
            vector<int> twoSum(vector<int>& nums, int target) {
                unordered_map<int, int> seen;
                for (int i = 0; i < (int)nums.size(); i++) {
                    int need = target - nums[i];
                    if (seen.count(need)) {
                        return {seen[need], i};
                    }
                    seen[nums[i]] = i;
                }
                return {};
            }
            """,
        ),
        _p(
            217, "Contains Duplicate", "Easy",
            "A set answers 'seen already?' in constant time.",
            "O(n) time, O(n) space",
            """
            bool containsDuplicate(vector<int>& nums) {
                unordered_set<int> seen;
                for (int n : nums) {
                    if (seen.count(n)) {
                        return true;
                    }
                    seen.insert(n);
                }
                return false;
            }
            """,
        ),
        _p(
            242, "Valid Anagram", "Easy",
            "Count letters up for one word, down for the other.",
            "O(n) time, O(1) space (26 letters)",
            """
            bool isAnagram(string s, string t) {
                if (s.size() != t.size()) {
                    return false;
                }
                unordered_map<char, int> counts;
                for (char ch : s) {
                    counts[ch]++;
                }
                for (char ch : t) {
                    if (counts[ch] == 0) {
                        return false;
                    }
                    counts[ch]--;
                }
                return true;
            }
            """,
        ),
        _p(
            49, "Group Anagrams", "Medium",
            "Sorted letters make a key that all anagrams share.",
            "O(n k log k) time, O(n k) space",
            """
            vector<vector<string>> groupAnagrams(vector<string>& strs) {
                unordered_map<string, vector<string>> groups;
                for (const string& word : strs) {
                    string key = word;
                    sort(key.begin(), key.end());
                    groups[key].push_back(word);
                }
                vector<vector<string>> out;
                for (auto& [key, group] : groups) {
                    out.push_back(group);
                }
                return out;
            }
            """,
        ),
        _p(
            454, "4Sum II", "Medium",
            "Count every sum from the first two lists, then look up its negation "
            "from the other two.",
            "O(n^2) time, O(n^2) space",
            """
            int fourSumCount(vector<int>& a, vector<int>& b, vector<int>& c,
                             vector<int>& d) {
                unordered_map<int, int> pairs;
                for (int x : a) {
                    for (int y : b) {
                        pairs[x + y]++;
                    }
                }
                int found = 0;
                for (int z : c) {
                    for (int w : d) {
                        auto it = pairs.find(-(z + w));
                        if (it != pairs.end()) {
                            found += it->second;
                        }
                    }
                }
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
            int subarraySum(vector<int>& nums, int k) {
                unordered_map<int, int> seen;
                seen[0] = 1;
                int running = 0;
                int found = 0;
                for (int n : nums) {
                    running += n;
                    auto it = seen.find(running - k);
                    if (it != seen.end()) {
                        found += it->second;
                    }
                    seen[running]++;
                }
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
            int longestConsecutive(vector<int>& nums) {
                unordered_set<int> pool(nums.begin(), nums.end());
                int best = 0;
                for (int n : pool) {
                    if (pool.count(n - 1)) {
                        continue;
                    }
                    int length = 1;
                    while (pool.count(n + length)) {
                        length++;
                    }
                    if (length > best) {
                        best = length;
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            36, "Valid Sudoku", "Medium",
            "Three sets per cell: its row, its column, and its box at "
            "(r / 3, c / 3).",
            "O(1) time, O(1) space",
            """
            bool isValidSudoku(vector<vector<char>>& board) {
                vector<unordered_set<char>> rows(9), cols(9), boxes(9);
                for (int r = 0; r < 9; r++) {
                    for (int c = 0; c < 9; c++) {
                        char value = board[r][c];
                        if (value == '.') {
                            continue;
                        }
                        int b = (r / 3) * 3 + c / 3;
                        if (!rows[r].insert(value).second) {
                            return false;
                        }
                        if (!cols[c].insert(value).second) {
                            return false;
                        }
                        if (!boxes[b].insert(value).second) {
                            return false;
                        }
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
    preamble=(VECTOR, STRING, ALGORITHM, USING),
    problems=(
        _p(
            125, "Valid Palindrome", "Easy",
            "Skip non-letters from both ends and compare inward.",
            "O(n) time, O(1) space",
            """
            bool isPalindrome(string s) {
                int left = 0;
                int right = (int)s.size() - 1;
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
            vector<int> twoSumSorted(vector<int>& numbers, int target) {
                int left = 0;
                int right = (int)numbers.size() - 1;
                while (left < right) {
                    int total = numbers[left] + numbers[right];
                    if (total == target) {
                        return {left + 1, right + 1};
                    }
                    if (total < target) {
                        left++;
                    } else {
                        right--;
                    }
                }
                return {};
            }
            """,
        ),
        _p(
            11, "Container With Most Water", "Medium",
            "Always move the shorter wall - the taller one can't help you.",
            "O(n) time, O(1) space",
            """
            int maxArea(vector<int>& height) {
                int left = 0;
                int right = (int)height.size() - 1;
                int best = 0;
                while (left < right) {
                    int width = right - left;
                    int area = width * min(height[left], height[right]);
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
            "Sort, fix one number, then two-pointer the rest for its negative.",
            "O(n^2) time, O(1) extra space",
            """
            vector<vector<int>> threeSum(vector<int>& nums) {
                sort(nums.begin(), nums.end());
                vector<vector<int>> result;
                for (int i = 0; i + 2 < (int)nums.size(); i++) {
                    if (i > 0 && nums[i] == nums[i - 1]) {
                        continue;
                    }
                    int left = i + 1;
                    int right = (int)nums.size() - 1;
                    while (left < right) {
                        int total = nums[i] + nums[left] + nums[right];
                        if (total < 0) {
                            left++;
                        } else if (total > 0) {
                            right--;
                        } else {
                            result.push_back({nums[i], nums[left], nums[right]});
                            left++;
                            while (left < right && nums[left] == nums[left - 1]) {
                                left++;
                            }
                        }
                    }
                }
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
            int removeDuplicates(vector<int>& nums) {
                if (nums.empty()) {
                    return 0;
                }
                int write = 1;
                for (int read = 1; read < (int)nums.size(); read++) {
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
            void moveZeroes(vector<int>& nums) {
                int write = 0;
                for (int read = 0; read < (int)nums.size(); read++) {
                    if (nums[read] != 0) {
                        nums[write] = nums[read];
                        write++;
                    }
                }
                for (int i = write; i < (int)nums.size(); i++) {
                    nums[i] = 0;
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
            int trap(vector<int>& height) {
                if (height.empty()) {
                    return 0;
                }
                int left = 0;
                int right = (int)height.size() - 1;
                int leftMax = height[left];
                int rightMax = height[right];
                int water = 0;
                while (left < right) {
                    if (leftMax < rightMax) {
                        left++;
                        leftMax = max(leftMax, height[left]);
                        water += leftMax - height[left];
                    } else {
                        right--;
                        rightMax = max(rightMax, height[right]);
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
            vector<int> sortedSquares(vector<int>& nums) {
                vector<int> out(nums.size());
                int left = 0;
                int right = (int)nums.size() - 1;
                for (int slot = (int)nums.size() - 1; slot >= 0; slot--) {
                    if (abs(nums[left]) > abs(nums[right])) {
                        out[slot] = nums[left] * nums[left];
                        left++;
                    } else {
                        out[slot] = nums[right] * nums[right];
                        right--;
                    }
                }
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
    preamble=(VECTOR, STRING, MAPS, ALGORITHM, CLIMITS, USING),
    problems=(
        _p(
            121, "Best Time to Buy and Sell Stock", "Easy",
            "Track the cheapest price so far; every day ask what selling today pays.",
            "O(n) time, O(1) space",
            """
            int maxProfit(vector<int>& prices) {
                int best = 0;
                int cheapest = INT_MAX;
                for (int price : prices) {
                    cheapest = min(cheapest, price);
                    best = max(best, price - cheapest);
                }
                return best;
            }
            """,
        ),
        _p(
            3, "Longest Substring Without Repeating Characters", "Medium",
            "On a repeat, jump the window start past the previous copy.",
            "O(n) time, O(min(n, alphabet)) space",
            """
            int lengthOfLongestSubstring(string s) {
                unordered_map<char, int> lastSeen;
                int start = 0;
                int best = 0;
                for (int i = 0; i < (int)s.size(); i++) {
                    auto it = lastSeen.find(s[i]);
                    if (it != lastSeen.end() && it->second >= start) {
                        start = it->second + 1;
                    }
                    lastSeen[s[i]] = i;
                    best = max(best, i - start + 1);
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
            int minSubArrayLen(int target, vector<int>& nums) {
                int left = 0;
                int total = 0;
                int best = (int)nums.size() + 1;
                for (int right = 0; right < (int)nums.size(); right++) {
                    total += nums[right];
                    while (total >= target) {
                        best = min(best, right - left + 1);
                        total -= nums[left];
                        left++;
                    }
                }
                return best <= (int)nums.size() ? best : 0;
            }
            """,
        ),
        _p(
            424, "Longest Repeating Character Replacement", "Medium",
            "A window is legal when (size - most common letter) <= k.",
            "O(n) time, O(1) space",
            """
            int characterReplacement(string s, int k) {
                unordered_map<char, int> counts;
                int left = 0;
                int mostCommon = 0;
                int best = 0;
                for (int right = 0; right < (int)s.size(); right++) {
                    counts[s[right]]++;
                    mostCommon = max(mostCommon, counts[s[right]]);
                    while ((right - left + 1) - mostCommon > k) {
                        counts[s[left]]--;
                        left++;
                    }
                    best = max(best, right - left + 1);
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
            double findMaxAverage(vector<int>& nums, int k) {
                int window = 0;
                for (int i = 0; i < k; i++) {
                    window += nums[i];
                }
                int best = window;
                for (int i = k; i < (int)nums.size(); i++) {
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
            "A fixed window whose letter counts match is a permutation - no "
            "sorting needed.",
            "O(n) time, O(1) space",
            """
            bool checkInclusion(string pattern, string text) {
                if (pattern.size() > text.size()) {
                    return false;
                }
                vector<int> need(26, 0), window(26, 0);
                for (char ch : pattern) {
                    need[ch - 'a']++;
                }
                for (int i = 0; i < (int)text.size(); i++) {
                    window[text[i] - 'a']++;
                    if (i >= (int)pattern.size()) {
                        window[text[i - pattern.size()] - 'a']--;
                    }
                    if (window == need) {
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
            int longestOnes(vector<int>& nums, int k) {
                int left = 0;
                int zeros = 0;
                int best = 0;
                for (int right = 0; right < (int)nums.size(); right++) {
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
            "of them are.",
            "O(n) time, O(1) space",
            """
            string minWindow(string text, string pattern) {
                if (pattern.empty() || text.empty()) {
                    return "";
                }
                unordered_map<char, int> need;
                for (char ch : pattern) {
                    need[ch]++;
                }
                int missing = (int)need.size();
                unordered_map<char, int> window;
                string best = "";
                int left = 0;
                for (int right = 0; right < (int)text.size(); right++) {
                    char ch = text[right];
                    window[ch]++;
                    if (need.count(ch) && window[ch] == need[ch]) {
                        missing--;
                    }
                    while (missing == 0) {
                        if (best.empty() || right - left + 1 < (int)best.size()) {
                            best = text.substr(left, right - left + 1);
                        }
                        char out = text[left];
                        window[out]--;
                        if (need.count(out) && window[out] < need[out]) {
                            missing++;
                        }
                        left++;
                    }
                }
                return best;
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
    preamble=(VECTOR, STRING, MAPS, ALGORITHM, USING),
    problems=(
        _p(
            20, "Valid Parentheses", "Easy",
            "Push openers; every closer must match the most recent opener.",
            "O(n) time, O(n) space",
            """
            bool isValid(string s) {
                unordered_map<char, char> pairs = {
                    {')', '('}, {']', '['}, {'}', '{'}
                };
                vector<char> stack;
                for (char ch : s) {
                    if (pairs.count(ch)) {
                        if (stack.empty() || stack.back() != pairs[ch]) {
                            return false;
                        }
                        stack.pop_back();
                    } else {
                        stack.push_back(ch);
                    }
                }
                return stack.empty();
            }
            """,
        ),
        _p(
            155, "Min Stack", "Medium",
            "Keep a parallel stack of 'the minimum as of this push'.",
            "O(1) per operation, O(n) space",
            """
            class MinStack {
            public:
                void push(int val) {
                    values.push_back(val);
                    if (mins.empty() || val <= mins.back()) {
                        mins.push_back(val);
                    }
                }

                void pop() {
                    int val = values.back();
                    values.pop_back();
                    if (!mins.empty() && val == mins.back()) {
                        mins.pop_back();
                    }
                }

                int top() { return values.back(); }

                int getMin() { return mins.back(); }

            private:
                vector<int> values;
                vector<int> mins;
            };
            """,
        ),
        _p(
            150, "Evaluate Reverse Polish Notation", "Medium",
            "Numbers go on the stack; an operator pops two and pushes the result.",
            "O(n) time, O(n) space",
            """
            int evalRPN(vector<string>& tokens) {
                vector<int> stack;
                for (const string& token : tokens) {
                    if (token == "+" || token == "-" || token == "*" ||
                        token == "/") {
                        int b = stack.back();
                        stack.pop_back();
                        int a = stack.back();
                        stack.pop_back();
                        if (token == "+") {
                            stack.push_back(a + b);
                        } else if (token == "-") {
                            stack.push_back(a - b);
                        } else if (token == "*") {
                            stack.push_back(a * b);
                        } else {
                            stack.push_back(a / b);
                        }
                    } else {
                        stack.push_back(stoi(token));
                    }
                }
                return stack[0];
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Monotonic stack of indexes still waiting for a warmer day.",
            "O(n) time, O(n) space",
            """
            vector<int> dailyTemperatures(vector<int>& temperatures) {
                vector<int> answer(temperatures.size(), 0);
                vector<int> stack;
                for (int i = 0; i < (int)temperatures.size(); i++) {
                    while (!stack.empty() &&
                           temperatures[stack.back()] < temperatures[i]) {
                        int prev = stack.back();
                        stack.pop_back();
                        answer[prev] = i - prev;
                    }
                    stack.push_back(i);
                }
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
            int calPoints(vector<string>& operations) {
                vector<int> stack;
                for (const string& op : operations) {
                    if (op == "C") {
                        stack.pop_back();
                    } else if (op == "D") {
                        stack.push_back(stack.back() * 2);
                    } else if (op == "+") {
                        int a = stack[stack.size() - 1];
                        int b = stack[stack.size() - 2];
                        stack.push_back(a + b);
                    } else {
                        stack.push_back(stoi(op));
                    }
                }
                int total = 0;
                for (int score : stack) {
                    total += score;
                }
                return total;
            }
            """,
        ),
        _p(
            71, "Simplify Path", "Medium",
            "A '..' pops the directory before it, which is exactly what a stack "
            "is for.",
            "O(n) time, O(n) space",
            """
            string simplifyPath(string path) {
                vector<string> stack;
                string part;
                for (size_t i = 0; i <= path.size(); i++) {
                    if (i == path.size() || path[i] == '/') {
                        if (part == "..") {
                            if (!stack.empty()) {
                                stack.pop_back();
                            }
                        } else if (!part.empty() && part != ".") {
                            stack.push_back(part);
                        }
                        part.clear();
                    } else {
                        part += path[i];
                    }
                }
                string out;
                for (const string& name : stack) {
                    out += "/" + name;
                }
                return out.empty() ? "/" : out;
            }
            """,
        ),
        _p(
            84, "Largest Rectangle in Histogram", "Hard",
            "Keep bars increasing; a shorter one closes off every taller bar "
            "behind it.",
            "O(n) time, O(n) space",
            """
            int largestRectangleArea(vector<int>& heights) {
                vector<pair<int, int>> stack;
                int best = 0;
                vector<int> bars = heights;
                bars.push_back(0);
                for (int i = 0; i < (int)bars.size(); i++) {
                    int start = i;
                    while (!stack.empty() && stack.back().second > bars[i]) {
                        int left = stack.back().first;
                        int tall = stack.back().second;
                        stack.pop_back();
                        if (tall * (i - left) > best) {
                            best = tall * (i - left);
                        }
                        start = left;
                    }
                    stack.push_back({start, bars[i]});
                }
                return best;
            }
            """,
        ),
        _p(
            394, "Decode String", "Medium",
            "Push the work in progress when a bracket opens, finish it when one "
            "closes.",
            "O(n) time, O(n) space",
            """
            string decodeString(string encoded) {
                vector<pair<string, int>> stack;
                string current;
                int count = 0;
                for (char ch : encoded) {
                    if (isdigit((unsigned char)ch)) {
                        count = count * 10 + (ch - '0');
                    } else if (ch == '[') {
                        stack.push_back({current, count});
                        current.clear();
                        count = 0;
                    } else if (ch == ']') {
                        auto [before, times] = stack.back();
                        stack.pop_back();
                        string repeated;
                        for (int i = 0; i < times; i++) {
                            repeated += current;
                        }
                        current = before + repeated;
                    } else {
                        current += ch;
                    }
                }
                return current;
            }
            """,
        ),
    ),
)


# The rest of the patterns live in problems_cpp2 to keep each file a readable
# length; PATTERNS below stitches them together.
from code_coach.leetcode.problems_cpp2 import (  # noqa: E402
    _BINARY_SEARCH,
    _DP,
    _GRAPH,
    _HEAP,
    _LINKED_LIST,
    _SUBSETS,
    _TOPOLOGICAL,
    _TREE_BFS,
    _TREE_DFS,
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
