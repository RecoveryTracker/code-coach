"""
The same LeetCode patterns, written in Rust.

Mirrors `problems.py` problem for problem, so switching language keeps your
place in the curriculum. The algorithms are identical; what changes is the
idiom — `HashMap` and `HashSet`, `Vec<i32>` for a list, `usize` for an index,
and an explicit `as i32` where the answer has to come back as one.

The signatures are LeetCode's own Rust signatures — `nums: Vec<i32>` taken by
value, `s: String` rather than `&str` — because the muscle memory should match
what the site actually hands you.

Every solution here is compiled and run against real cases by
tests/test_rust_solutions.py. Nothing in this file is a solution that has only
been read.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Pattern
from code_coach.leetcode.rust_common import COLLECTIONS, HASH_MAP, _p

# ── 1. Hash maps ────────────────────────────────────────────

_HASH_MAP = Pattern(
    id="lc-hashmap",
    name="Hash Maps",
    order=1,
    blurb="Trade memory for speed: remember what you've seen in a map or set.",
    tell="You'd otherwise need a nested loop to ask 'have I seen this before?'",
    preamble=(COLLECTIONS,),
    problems=(
        _p(
            1, "Two Sum", "Easy",
            "Store each number's index as you pass it, then look up the complement.",
            "O(n) time, O(n) space",
            """
            pub fn two_sum(nums: Vec<i32>, target: i32) -> Vec<i32> {
                let mut seen: HashMap<i32, i32> = HashMap::new();
                for (i, n) in nums.iter().enumerate() {
                    let need = target - n;
                    if let Some(&j) = seen.get(&need) {
                        return vec![j, i as i32];
                    }
                    seen.insert(*n, i as i32);
                }
                vec![]
            }
            """,
        ),
        _p(
            217, "Contains Duplicate", "Easy",
            "A set answers 'seen already?' in constant time.",
            "O(n) time, O(n) space",
            """
            pub fn contains_duplicate(nums: Vec<i32>) -> bool {
                let mut seen: HashSet<i32> = HashSet::new();
                for n in nums {
                    if seen.contains(&n) {
                        return true;
                    }
                    seen.insert(n);
                }
                false
            }
            """,
        ),
        _p(
            242, "Valid Anagram", "Easy",
            "Count letters up for one word, down for the other.",
            "O(n) time, O(1) space (26 letters)",
            """
            pub fn is_anagram(s: String, t: String) -> bool {
                if s.len() != t.len() {
                    return false;
                }
                let mut counts: HashMap<char, i32> = HashMap::new();
                for ch in s.chars() {
                    *counts.entry(ch).or_insert(0) += 1;
                }
                for ch in t.chars() {
                    let count = counts.entry(ch).or_insert(0);
                    if *count == 0 {
                        return false;
                    }
                    *count -= 1;
                }
                true
            }
            """,
        ),
        _p(
            49, "Group Anagrams", "Medium",
            "Sorted letters make a key that all anagrams share.",
            "O(n k log k) time, O(n k) space",
            """
            pub fn group_anagrams(strs: Vec<String>) -> Vec<Vec<String>> {
                let mut groups: HashMap<String, Vec<String>> = HashMap::new();
                for word in strs {
                    let mut letters: Vec<char> = word.chars().collect();
                    letters.sort();
                    let key: String = letters.into_iter().collect();
                    groups.entry(key).or_insert_with(Vec::new).push(word);
                }
                groups.into_values().collect()
            }
            """,
        ),
        _p(
            454, "4Sum II", "Medium",
            "Count every sum from the first two lists, then look up its negation "
            "from the other two.",
            "O(n^2) time, O(n^2) space",
            """
            pub fn four_sum_count(
                a: Vec<i32>,
                b: Vec<i32>,
                c: Vec<i32>,
                d: Vec<i32>,
            ) -> i32 {
                let mut pairs: HashMap<i32, i32> = HashMap::new();
                for x in &a {
                    for y in &b {
                        *pairs.entry(x + y).or_insert(0) += 1;
                    }
                }
                let mut found = 0;
                for z in &c {
                    for w in &d {
                        found += pairs.get(&-(z + w)).copied().unwrap_or(0);
                    }
                }
                found
            }
            """,
        ),
        _p(
            560, "Subarray Sum Equals K", "Medium",
            "Remember every running total you've seen; the gap between two of "
            "them is a subarray.",
            "O(n) time, O(n) space",
            """
            pub fn subarray_sum(nums: Vec<i32>, k: i32) -> i32 {
                let mut seen: HashMap<i32, i32> = HashMap::new();
                seen.insert(0, 1);
                let mut running = 0;
                let mut found = 0;
                for n in nums {
                    running += n;
                    found += seen.get(&(running - k)).copied().unwrap_or(0);
                    *seen.entry(running).or_insert(0) += 1;
                }
                found
            }
            """,
        ),
        _p(
            128, "Longest Consecutive Sequence", "Medium",
            "Only start counting from a number with no left neighbour - each run "
            "is walked once.",
            "O(n) time, O(n) space",
            """
            pub fn longest_consecutive(nums: Vec<i32>) -> i32 {
                let pool: HashSet<i32> = nums.into_iter().collect();
                let mut best = 0;
                for &n in &pool {
                    if pool.contains(&(n - 1)) {
                        continue;
                    }
                    let mut length = 1;
                    while pool.contains(&(n + length)) {
                        length += 1;
                    }
                    if length > best {
                        best = length;
                    }
                }
                best
            }
            """,
        ),
        _p(
            36, "Valid Sudoku", "Medium",
            "Three sets per cell: its row, its column, and its box at "
            "(r / 3, c / 3).",
            "O(1) time, O(1) space",
            """
            pub fn is_valid_sudoku(board: Vec<Vec<char>>) -> bool {
                let mut rows: Vec<HashSet<char>> = vec![HashSet::new(); 9];
                let mut cols: Vec<HashSet<char>> = vec![HashSet::new(); 9];
                let mut boxes: Vec<HashSet<char>> = vec![HashSet::new(); 9];
                for r in 0..9 {
                    for c in 0..9 {
                        let value = board[r][c];
                        if value == '.' {
                            continue;
                        }
                        let b = (r / 3) * 3 + c / 3;
                        if !rows[r].insert(value) {
                            return false;
                        }
                        if !cols[c].insert(value) {
                            return false;
                        }
                        if !boxes[b].insert(value) {
                            return false;
                        }
                    }
                }
                true
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
    problems=(
        _p(
            125, "Valid Palindrome", "Easy",
            "Skip non-letters from both ends and compare inward.",
            "O(n) time, O(1) space",
            """
            pub fn is_palindrome(s: String) -> bool {
                let chars: Vec<char> = s.chars().collect();
                let mut left = 0;
                let mut right = chars.len().saturating_sub(1);
                while left < right {
                    while left < right && !chars[left].is_alphanumeric() {
                        left += 1;
                    }
                    while left < right && !chars[right].is_alphanumeric() {
                        right -= 1;
                    }
                    if chars[left].to_ascii_lowercase()
                        != chars[right].to_ascii_lowercase()
                    {
                        return false;
                    }
                    left += 1;
                    right -= 1;
                }
                true
            }
            """,
        ),
        _p(
            167, "Two Sum II (sorted)", "Medium",
            "Too big? Move right in. Too small? Move left out.",
            "O(n) time, O(1) space",
            """
            pub fn two_sum_sorted(numbers: Vec<i32>, target: i32) -> Vec<i32> {
                let mut left = 0;
                let mut right = numbers.len() - 1;
                while left < right {
                    let total = numbers[left] + numbers[right];
                    if total == target {
                        return vec![left as i32 + 1, right as i32 + 1];
                    }
                    if total < target {
                        left += 1;
                    } else {
                        right -= 1;
                    }
                }
                vec![]
            }
            """,
        ),
        _p(
            11, "Container With Most Water", "Medium",
            "Always move the shorter wall - the taller one can't help you.",
            "O(n) time, O(1) space",
            """
            pub fn max_area(height: Vec<i32>) -> i32 {
                let mut left = 0;
                let mut right = height.len() - 1;
                let mut best = 0;
                while left < right {
                    let width = (right - left) as i32;
                    let area = width * height[left].min(height[right]);
                    if area > best {
                        best = area;
                    }
                    if height[left] < height[right] {
                        left += 1;
                    } else {
                        right -= 1;
                    }
                }
                best
            }
            """,
        ),
        _p(
            15, "3Sum", "Medium",
            "Sort, fix one number, then two-pointer the rest for its negative.",
            "O(n^2) time, O(1) extra space",
            """
            pub fn three_sum(nums: Vec<i32>) -> Vec<Vec<i32>> {
                let mut nums = nums;
                nums.sort();
                let mut result = Vec::new();
                for i in 0..nums.len().saturating_sub(2) {
                    if i > 0 && nums[i] == nums[i - 1] {
                        continue;
                    }
                    let mut left = i + 1;
                    let mut right = nums.len() - 1;
                    while left < right {
                        let total = nums[i] + nums[left] + nums[right];
                        if total < 0 {
                            left += 1;
                        } else if total > 0 {
                            right -= 1;
                        } else {
                            result.push(vec![nums[i], nums[left], nums[right]]);
                            left += 1;
                            while left < right && nums[left] == nums[left - 1] {
                                left += 1;
                            }
                        }
                    }
                }
                result
            }
            """,
        ),
        _p(
            26, "Remove Duplicates from Sorted Array", "Easy",
            "One pointer writes, the other reads - the writer only moves on a "
            "new value.",
            "O(n) time, O(1) space",
            """
            pub fn remove_duplicates(nums: &mut Vec<i32>) -> i32 {
                if nums.is_empty() {
                    return 0;
                }
                let mut write = 1;
                for read in 1..nums.len() {
                    if nums[read] != nums[write - 1] {
                        nums[write] = nums[read];
                        write += 1;
                    }
                }
                write as i32
            }
            """,
        ),
        _p(
            283, "Move Zeroes", "Easy",
            "Same read/write pair: write every non-zero forward, then fill the tail.",
            "O(n) time, O(1) space",
            """
            pub fn move_zeroes(nums: &mut Vec<i32>) {
                let mut write = 0;
                for read in 0..nums.len() {
                    if nums[read] != 0 {
                        nums[write] = nums[read];
                        write += 1;
                    }
                }
                for i in write..nums.len() {
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
            pub fn trap(height: Vec<i32>) -> i32 {
                if height.is_empty() {
                    return 0;
                }
                let mut left = 0;
                let mut right = height.len() - 1;
                let mut left_max = height[left];
                let mut right_max = height[right];
                let mut water = 0;
                while left < right {
                    if left_max < right_max {
                        left += 1;
                        left_max = left_max.max(height[left]);
                        water += left_max - height[left];
                    } else {
                        right -= 1;
                        right_max = right_max.max(height[right]);
                        water += right_max - height[right];
                    }
                }
                water
            }
            """,
        ),
        _p(
            977, "Squares of a Sorted Array", "Easy",
            "The biggest square is at one end or the other, so fill the answer "
            "backwards.",
            "O(n) time, O(n) space",
            """
            pub fn sorted_squares(nums: Vec<i32>) -> Vec<i32> {
                let mut out = vec![0; nums.len()];
                let mut left = 0;
                let mut right = nums.len() - 1;
                for slot in (0..nums.len()).rev() {
                    if nums[left].abs() > nums[right].abs() {
                        out[slot] = nums[left] * nums[left];
                        left += 1;
                    } else {
                        out[slot] = nums[right] * nums[right];
                        if right > 0 {
                            right -= 1;
                        }
                    }
                }
                out
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
    preamble=(HASH_MAP,),
    problems=(
        _p(
            121, "Best Time to Buy and Sell Stock", "Easy",
            "Track the cheapest price so far; every day ask what selling today pays.",
            "O(n) time, O(1) space",
            """
            pub fn max_profit(prices: Vec<i32>) -> i32 {
                let mut best = 0;
                let mut cheapest = i32::MAX;
                for price in prices {
                    cheapest = cheapest.min(price);
                    best = best.max(price - cheapest);
                }
                best
            }
            """,
        ),
        _p(
            3, "Longest Substring Without Repeating Characters", "Medium",
            "On a repeat, jump the window start past the previous copy.",
            "O(n) time, O(min(n, alphabet)) space",
            """
            pub fn length_of_longest_substring(s: String) -> i32 {
                let mut last_seen: HashMap<char, usize> = HashMap::new();
                let mut start = 0;
                let mut best = 0;
                for (i, ch) in s.chars().enumerate() {
                    if let Some(&prev) = last_seen.get(&ch) {
                        if prev >= start {
                            start = prev + 1;
                        }
                    }
                    last_seen.insert(ch, i);
                    best = best.max((i - start + 1) as i32);
                }
                best
            }
            """,
        ),
        _p(
            209, "Minimum Size Subarray Sum", "Medium",
            "Grow right always; shrink left while the window still qualifies.",
            "O(n) time, O(1) space",
            """
            pub fn min_sub_array_len(target: i32, nums: Vec<i32>) -> i32 {
                let mut left = 0;
                let mut total = 0;
                let mut best = nums.len() + 1;
                for right in 0..nums.len() {
                    total += nums[right];
                    while total >= target {
                        best = best.min(right - left + 1);
                        total -= nums[left];
                        left += 1;
                    }
                }
                if best <= nums.len() {
                    best as i32
                } else {
                    0
                }
            }
            """,
        ),
        _p(
            424, "Longest Repeating Character Replacement", "Medium",
            "A window is legal when (size - most common letter) <= k.",
            "O(n) time, O(1) space",
            """
            pub fn character_replacement(s: String, k: i32) -> i32 {
                let chars: Vec<char> = s.chars().collect();
                let mut counts: HashMap<char, i32> = HashMap::new();
                let mut left = 0;
                let mut most_common = 0;
                let mut best = 0;
                for right in 0..chars.len() {
                    let count = counts.entry(chars[right]).or_insert(0);
                    *count += 1;
                    most_common = most_common.max(*count);
                    while (right - left + 1) as i32 - most_common > k {
                        *counts.entry(chars[left]).or_insert(0) -= 1;
                        left += 1;
                    }
                    best = best.max((right - left + 1) as i32);
                }
                best
            }
            """,
        ),
        _p(
            643, "Maximum Average Subarray I", "Easy",
            "The window never changes size, so each step adds one number and "
            "drops one.",
            "O(n) time, O(1) space",
            """
            pub fn find_max_average(nums: Vec<i32>, k: i32) -> f64 {
                let k = k as usize;
                let mut window: i32 = nums[..k].iter().sum();
                let mut best = window;
                for i in k..nums.len() {
                    window += nums[i] - nums[i - k];
                    if window > best {
                        best = window;
                    }
                }
                best as f64 / k as f64
            }
            """,
        ),
        _p(
            567, "Permutation in String", "Medium",
            "A fixed window whose letter counts match is a permutation - no "
            "sorting needed.",
            "O(n) time, O(1) space",
            """
            pub fn check_inclusion(pattern: String, text: String) -> bool {
                if pattern.len() > text.len() {
                    return false;
                }
                let pattern: Vec<char> = pattern.chars().collect();
                let text: Vec<char> = text.chars().collect();
                let mut need: HashMap<char, i32> = HashMap::new();
                for &ch in &pattern {
                    *need.entry(ch).or_insert(0) += 1;
                }
                let mut window: HashMap<char, i32> = HashMap::new();
                for i in 0..text.len() {
                    *window.entry(text[i]).or_insert(0) += 1;
                    if i >= pattern.len() {
                        let out = text[i - pattern.len()];
                        let count = window.entry(out).or_insert(0);
                        *count -= 1;
                        if *count == 0 {
                            window.remove(&out);
                        }
                    }
                    if window == need {
                        return true;
                    }
                }
                false
            }
            """,
        ),
        _p(
            1004, "Max Consecutive Ones III", "Medium",
            "Grow while at most k zeros are inside; shrink from the left when a "
            "k+1th appears.",
            "O(n) time, O(1) space",
            """
            pub fn longest_ones(nums: Vec<i32>, k: i32) -> i32 {
                let mut left = 0;
                let mut zeros = 0;
                let mut best = 0;
                for right in 0..nums.len() {
                    if nums[right] == 0 {
                        zeros += 1;
                    }
                    while zeros > k {
                        if nums[left] == 0 {
                            zeros -= 1;
                        }
                        left += 1;
                    }
                    if (right - left + 1) as i32 > best {
                        best = (right - left + 1) as i32;
                    }
                }
                best
            }
            """,
        ),
        _p(
            76, "Minimum Window Substring", "Hard",
            "Count how many required letters are satisfied; shrink only while all "
            "of them are.",
            "O(n) time, O(1) space",
            """
            pub fn min_window(text: String, pattern: String) -> String {
                if pattern.is_empty() || text.is_empty() {
                    return String::new();
                }
                let text: Vec<char> = text.chars().collect();
                let mut need: HashMap<char, i32> = HashMap::new();
                for ch in pattern.chars() {
                    *need.entry(ch).or_insert(0) += 1;
                }
                let mut missing = need.len() as i32;
                let mut window: HashMap<char, i32> = HashMap::new();
                let mut best = String::new();
                let mut left = 0;
                for right in 0..text.len() {
                    let ch = text[right];
                    *window.entry(ch).or_insert(0) += 1;
                    if need.contains_key(&ch) && window[&ch] == need[&ch] {
                        missing -= 1;
                    }
                    while missing == 0 {
                        if best.is_empty() || right - left + 1 < best.chars().count() {
                            best = text[left..=right].iter().collect();
                        }
                        let out = text[left];
                        *window.entry(out).or_insert(0) -= 1;
                        if need.contains_key(&out) && window[&out] < need[&out] {
                            missing += 1;
                        }
                        left += 1;
                    }
                }
                best
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
    problems=(
        _p(
            20, "Valid Parentheses", "Easy",
            "Push openers; every closer must match the most recent opener.",
            "O(n) time, O(n) space",
            """
            pub fn is_valid(s: String) -> bool {
                let mut stack: Vec<char> = Vec::new();
                for ch in s.chars() {
                    match ch {
                        '(' | '[' | '{' => stack.push(ch),
                        ')' => {
                            if stack.pop() != Some('(') {
                                return false;
                            }
                        }
                        ']' => {
                            if stack.pop() != Some('[') {
                                return false;
                            }
                        }
                        '}' => {
                            if stack.pop() != Some('{') {
                                return false;
                            }
                        }
                        _ => {}
                    }
                }
                stack.is_empty()
            }
            """,
        ),
        _p(
            155, "Min Stack", "Medium",
            "Keep a parallel stack of 'the minimum as of this push'.",
            "O(1) per operation, O(n) space",
            """
            pub struct MinStack {
                stack: Vec<i32>,
                mins: Vec<i32>,
            }

            impl MinStack {
                pub fn new() -> Self {
                    MinStack {
                        stack: Vec::new(),
                        mins: Vec::new(),
                    }
                }

                pub fn push(&mut self, val: i32) {
                    self.stack.push(val);
                    if self.mins.is_empty() || val <= *self.mins.last().unwrap() {
                        self.mins.push(val);
                    }
                }

                pub fn pop(&mut self) {
                    if let Some(val) = self.stack.pop() {
                        if self.mins.last() == Some(&val) {
                            self.mins.pop();
                        }
                    }
                }

                pub fn top(&self) -> i32 {
                    *self.stack.last().unwrap()
                }

                pub fn get_min(&self) -> i32 {
                    *self.mins.last().unwrap()
                }
            }
            """,
        ),
        _p(
            150, "Evaluate Reverse Polish Notation", "Medium",
            "Numbers go on the stack; an operator pops two and pushes the result.",
            "O(n) time, O(n) space",
            """
            pub fn eval_rpn(tokens: Vec<String>) -> i32 {
                let mut stack: Vec<i32> = Vec::new();
                for token in tokens {
                    match token.as_str() {
                        "+" => {
                            let b = stack.pop().unwrap();
                            let a = stack.pop().unwrap();
                            stack.push(a + b);
                        }
                        "*" => {
                            let b = stack.pop().unwrap();
                            let a = stack.pop().unwrap();
                            stack.push(a * b);
                        }
                        "-" => {
                            let b = stack.pop().unwrap();
                            let a = stack.pop().unwrap();
                            stack.push(a - b);
                        }
                        "/" => {
                            let b = stack.pop().unwrap();
                            let a = stack.pop().unwrap();
                            stack.push(a / b);
                        }
                        _ => stack.push(token.parse().unwrap()),
                    }
                }
                stack[0]
            }
            """,
        ),
        _p(
            739, "Daily Temperatures", "Medium",
            "Monotonic stack of indexes still waiting for a warmer day.",
            "O(n) time, O(n) space",
            """
            pub fn daily_temperatures(temperatures: Vec<i32>) -> Vec<i32> {
                let mut answer = vec![0; temperatures.len()];
                let mut stack: Vec<usize> = Vec::new();
                for i in 0..temperatures.len() {
                    while let Some(&prev) = stack.last() {
                        if temperatures[prev] < temperatures[i] {
                            stack.pop();
                            answer[prev] = (i - prev) as i32;
                        } else {
                            break;
                        }
                    }
                    stack.push(i);
                }
                answer
            }
            """,
        ),
        _p(
            682, "Baseball Game", "Easy",
            "Every operation only ever looks at the top of the stack, which is "
            "the whole idea.",
            "O(n) time, O(n) space",
            """
            pub fn cal_points(operations: Vec<String>) -> i32 {
                let mut stack: Vec<i32> = Vec::new();
                for op in operations {
                    match op.as_str() {
                        "C" => {
                            stack.pop();
                        }
                        "D" => {
                            let last = *stack.last().unwrap();
                            stack.push(last * 2);
                        }
                        "+" => {
                            let a = stack[stack.len() - 1];
                            let b = stack[stack.len() - 2];
                            stack.push(a + b);
                        }
                        _ => stack.push(op.parse().unwrap()),
                    }
                }
                stack.iter().sum()
            }
            """,
        ),
        _p(
            71, "Simplify Path", "Medium",
            "A '..' pops the directory before it, which is exactly what a stack "
            "is for.",
            "O(n) time, O(n) space",
            """
            pub fn simplify_path(path: String) -> String {
                let mut stack: Vec<&str> = Vec::new();
                for part in path.split('/') {
                    if part.is_empty() || part == "." {
                        continue;
                    }
                    if part == ".." {
                        stack.pop();
                    } else {
                        stack.push(part);
                    }
                }
                format!("/{}", stack.join("/"))
            }
            """,
        ),
        _p(
            84, "Largest Rectangle in Histogram", "Hard",
            "Keep bars increasing; a shorter one closes off every taller bar "
            "behind it.",
            "O(n) time, O(n) space",
            """
            pub fn largest_rectangle_area(heights: Vec<i32>) -> i32 {
                let mut stack: Vec<(usize, i32)> = Vec::new();
                let mut best = 0;
                let mut bars = heights;
                bars.push(0);
                for i in 0..bars.len() {
                    let height = bars[i];
                    let mut start = i;
                    while let Some(&(left, tall)) = stack.last() {
                        if tall > height {
                            stack.pop();
                            if tall * (i - left) as i32 > best {
                                best = tall * (i - left) as i32;
                            }
                            start = left;
                        } else {
                            break;
                        }
                    }
                    stack.push((start, height));
                }
                best
            }
            """,
        ),
        _p(
            394, "Decode String", "Medium",
            "Push the work in progress when a bracket opens, finish it when one "
            "closes.",
            "O(n) time, O(n) space",
            """
            pub fn decode_string(encoded: String) -> String {
                let mut stack: Vec<(String, usize)> = Vec::new();
                let mut current = String::new();
                let mut count = 0;
                for ch in encoded.chars() {
                    if ch.is_ascii_digit() {
                        count = count * 10 + ch.to_digit(10).unwrap() as usize;
                    } else if ch == '[' {
                        stack.push((current.clone(), count));
                        current = String::new();
                        count = 0;
                    } else if ch == ']' {
                        let (before, times) = stack.pop().unwrap();
                        current = format!("{}{}", before, current.repeat(times));
                    } else {
                        current.push(ch);
                    }
                }
                current
            }
            """,
        ),
    ),
)


# The remaining nine patterns are still being written. Until every pattern is
# here this bank is deliberately NOT registered in `patterns_for_language`:
# a partial bank would let `has_own_bank` say yes and then serve Python for
# whatever is missing, which is the exact failure that was just fixed.
PARTIAL: tuple[Pattern, ...] = (
    _HASH_MAP,
    _TWO_POINTERS,
    _SLIDING_WINDOW,
    _STACK,
)
