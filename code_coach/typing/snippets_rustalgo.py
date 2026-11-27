"""Rust for algorithms: the shapes interview problems are built from.

The same moves as the Python, JavaScript and Dart sets, written the way Rust
writes them: `usize` indexes that must not underflow (`checked_sub`,
`saturating_sub`), `HashMap` counting through `entry().or_insert(0)`, `insert`
on a `HashSet` answering whether the value was new, a `Vec` as a stack whose
`pop` hands back an `Option`, `VecDeque` for breadth-first search,
`vec![0; n + 1]` DP tables, iterator chains, and `sort_by_key` with
`Reverse` for descending order.

The blocks are whole programs with a `main`, and the tests run every one
through rustc and hold what it prints to an answer worked out by hand. None
of them prints a HashMap or HashSet directly: their order is random.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

RUSTALGO_LINES: tuple[Passage, ...] = (
    # two pointers and windows
    _s("let (mut lo, mut hi) = (0, nums.len() - 1);", "two pointers; an empty slice would underflow"),
    _s("while lo < hi && nums[lo] + nums[hi] != target {", "closing in on a pair"),
    _s("nums.swap(lo, hi);", "swap two slots in place"),
    _s("run_sum += values[i] - values[i - k];", "slide: add the new end, drop the old"),
    _s("best = best.max(end - start + 1);", "the widest window so far"),
    _s("let mut last_seen: HashMap<char, usize> = HashMap::with_capacity(26);", "letter to its latest position"),
    _s("if let Some(&at) = last_seen.get(&ch) { start = start.max(at + 1); }", "a repeat inside the window"),
    _s("for (end, ch) in text.chars().enumerate() {", "the window's right edge, with its index"),
    # binary search
    _s("let mid = lo + (hi - lo) / 2;", "the midpoint, safe from overflow"),
    _s("if sorted[mid] == target { return Some(mid); }", "found it"),
    _s("if sorted[mid] < target { lo = mid + 1; } else { hi = mid; }", "half-open: hi is never the answer"),
    _s("match sorted.binary_search(&target) {", "the library's search; it returns a Result"),
    _s("Err(spot) => sorted.insert(spot, target),", "Err holds where the value belongs"),
    _s("let spot = sorted.partition_point(|&x| x < target);", "the first slot that is not less"),
    # maps, sets, counting
    _s("let mut counts: HashMap<char, usize> = HashMap::new();", "letter to how many times"),
    _s("*counts.entry(ch).or_insert(0) += 1;", "counting with entry"),
    _s("let mut seen = HashSet::new();", "a set that infers its type from use"),
    _s("if !seen.insert(n) { return true; }", "insert returns false if it was there"),
    _s("let want = target - nums[i];", "the partner this number needs"),
    _s("if let Some(&j) = index.get(&want) { return vec![j, i]; }", "the pair, once both are seen"),
    _s("index.insert(nums[i], i);", "remember where this value lives"),
    _s("let best = counts.iter().max_by_key(|&(_, &n)| n);", "the most common, or None when empty"),
    _s("groups.entry(key).or_default().push(word);", "make the group if missing, then add"),
    _s("let mut keys: Vec<_> = counts.keys().copied().collect();", "keys in a Vec, ready to sort"),
    # stacks and queues
    _s("let mut stack: Vec<usize> = Vec::with_capacity(n);", "a Vec used as a stack"),
    _s("while let Some(&top) = stack.last() {", "peek at the top until it is empty"),
    _s("let Some(open) = stack.pop() else { return false; };", "pop gives an Option; none means unmatched"),
    _s("while stack.last().map_or(false, |&t| temps[t] < temp) {", "a monotonic stack"),
    _s("let mut queue = VecDeque::from([start]);", "a double-ended queue with the start in it"),
    _s("while let Some(cur) = queue.pop_front() {", "the oldest in the queue"),
    _s("if visited.insert(next) { queue.push_back(next); }", "only the new nodes join the queue"),
    _s("for &next in graph[cur].iter() {", "every neighbour of the node"),
    _s("dist[next] = dist[node] + 1;", "one further than the node it came from"),
    # recursion and memo
    _s("fn climb(n: u64, memo: &mut HashMap<u64, u64>) -> u64 {", "a recursive function with a cache"),
    _s("if let Some(&known) = memo.get(&n) { return known; }", "already worked out"),
    _s("memo.insert(n, ways);", "keep the answer for next time"),
    # dynamic programming
    _s("let mut dp = vec![0; n + 1];", "one slot per subproblem"),
    _s("dp[i] = dp[i - 1].max(dp[i - 2] + houses[i - 1]);", "take it or skip it"),
    _s("let mut table = vec![vec![0; cols]; rows];", "a grid; each row is its own copy"),
    _s("let mut ways = vec![0u64; amount + 1];", "unsigned counts for the ways"),
    _s("for total in coin..=amount {", "every amount this coin helps"),
    _s("ways[amount] += ways[amount - coin];", "the ways of making change"),
    # prefix sums and iterator chains
    _s("let mut prefix = vec![0];", "the empty prefix comes first"),
    _s("prefix.push(prefix[prefix.len() - 1] + x);", "a running total"),
    _s("let squares = nums.iter().map(|&x| x * x).sum::<i32>();", "map then add, with a turbofish"),
    _s("let product = nums.iter().fold(1, |acc, &x| acc * x);", "multiplying with fold"),
    _s("for (i, &x) in nums.iter().enumerate() {", "index and value together"),
    _s("let dot: i32 = a.iter().zip(&b).map(|(x, y)| x * y).sum();", "pairs from two slices"),
    _s("let rises = temps.windows(2).filter(|w| w[1] > w[0]).count();", "each neighbouring pair"),
    _s("let sums: Vec<i32> = nums.chunks(3).map(|c| c.iter().sum()).collect();", "totals of groups of three"),
    # sorting
    _s("nums.sort_unstable();", "fast in-place sort; ties may reorder"),
    _s("people.sort_by_key(|p| p.age);", "sort by one field"),
    _s("nums.sort_by(|a, b| b.cmp(a));", "largest first"),
    _s("words.sort_by_key(|w| Reverse(w.len()));", "longest first, with cmp::Reverse"),
    _s("intervals.sort_by(|a, b| a.0.cmp(&b.0));", "by start, before merging"),
    _s("heap.push(Reverse((dist, node)));", "Reverse turns the max-heap into a min-heap"),
    # strings
    _s("let reversed = text.chars().rev().collect::<String>();", "a string, backwards"),
    _s("let slot = (ch as u8 - b'a') as usize;", "a to 0, b to 1 and so on"),
    _s("let shifted = ((ch as u8 - b'a' + shift) % 26 + b'a') as char;", "a Caesar shift"),
    _s("let cleaned: String = text.chars().filter(|c| c.is_alphanumeric()).collect();", "letters and digits only"),
    # bits
    _s("let ones = n.count_ones();", "how many bits are set"),
    _s("if n > 0 && n & (n - 1) == 0 { return true; }", "exactly one bit set: a power of two"),
    _s("n &= n - 1;", "clears the lowest set bit"),
    _s("let single = nums.iter().fold(0, |a, &b| a ^ b);", "pairs cancel out"),
    _s("if n & 1 == 1 { odd += 1; }", "the lowest bit says odd"),
    # usize underflow, grids and match
    _s("let prev = i.checked_sub(1);", "None instead of a panic at zero"),
    _s("let left = col.saturating_sub(1);", "stops at zero"),
    _s("let Some(up) = row.checked_sub(1) else { continue; };", "skip the top edge"),
    _s("const DIRS: [(i32, i32); 4] = [(1, 0), (-1, 0), (0, 1), (0, -1)];", "the four neighbours"),
    _s("let (nr, nc) = (r as i32 + dr, c as i32 + dc);", "signed, so a step off the edge can go below zero"),
    _s("if nr < 0 || nc < 0 || nr >= rows as i32 || nc >= cols as i32 { continue; }", "off the edge of the grid"),
    _s("match (n % 3, n % 5) {", "match on a pair of remainders"),
    _s("(0, 0) => String::from(\"fizzbuzz\"),", "an arm for both"),
    _s("let top = scores.iter().copied().max().unwrap_or(0);", "the biggest, or zero when empty"),
)


# -- Blocks ---------------------------------------------------

def _b(code: str, note: str) -> Passage:
    return Passage(code, f"Rust · {note}")


RUSTALGO_BLOCKS: tuple[Passage, ...] = (
    _b("""use std::collections::HashMap;

fn two_sum(nums: &[i32], target: i32) -> Option<(usize, usize)> {
    let mut seen: HashMap<i32, usize> = HashMap::new();
    for (i, &n) in nums.iter().enumerate() {
        if let Some(&j) = seen.get(&(target - n)) {
            return Some((j, i));
        }
        seen.insert(n, i);
    }
    None
}

fn main() {
    println!("{:?} {:?}", two_sum(&[2, 7, 11, 15], 9), two_sum(&[1, 2], 7));
}""",
       "two sum with a map"),
    _b("""fn search(sorted: &[i32], target: i32) -> i32 {
    let (mut lo, mut hi) = (0i32, sorted.len() as i32 - 1);
    while lo <= hi {
        let mid = lo + (hi - lo) / 2;
        if sorted[mid as usize] == target { return mid; }
        if sorted[mid as usize] < target { lo = mid + 1; } else { hi = mid - 1; }
    }
    -1
}

fn main() {
    println!("{} {}", search(&[1, 3, 5, 7, 9], 1), search(&[2, 4], 3));
}""",
       "binary search"),
    _b("""fn valid(text: &str) -> bool {
    let mut stack: Vec<char> = Vec::new();
    for ch in text.chars() {
        match ch {
            '(' => stack.push(')'),
            '[' => stack.push(']'),
            '{' => stack.push('}'),
            _ if stack.pop() != Some(ch) => return false,
            _ => {}
        }
    }
    stack.is_empty()
}

fn main() { println!("{} {} {}", valid("{[()]}"), valid("(]"), valid("((")); }""",
       "matching brackets with a stack"),
    _b("""use std::collections::VecDeque;

fn main() {
    let graph = vec![vec![1, 2], vec![3], vec![3], vec![]];
    let mut dist = vec![usize::MAX; 4];
    let mut queue = VecDeque::from([0]);
    dist[0] = 0;
    while let Some(node) = queue.pop_front() {
        for &next in &graph[node] {
            if dist[next] == usize::MAX { dist[next] = dist[node] + 1; queue.push_back(next); }
        }
    }
    println!("{:?}", dist);
}""",
       "breadth-first search for distances"),
    _b("""use std::collections::HashMap;

fn climb(n: u64, memo: &mut HashMap<u64, u64>) -> u64 {
    if n <= 1 { return 1; }
    if let Some(&known) = memo.get(&n) { return known; }
    let ways = climb(n - 1, memo) + climb(n - 2, memo);
    memo.insert(n, ways);
    ways
}

fn main() {
    let mut memo = HashMap::new();
    let all: Vec<String> = (1..=7).map(|n| climb(n, &mut memo).to_string()).collect();
    println!("{}", all.join(" "));
}""",
       "climbing stairs with a memo"),
    _b("""fn rob(houses: &[i32]) -> i32 {
    let (mut take, mut skip) = (0i32, 0i32);
    for &money in houses {
        let new_take = skip + money;
        skip = skip.max(take);
        take = new_take;
    }
    take.max(skip)
}

fn main() {
    println!("{} {} {}", rob(&[2, 7, 9, 3, 1]), rob(&[5]), rob(&[]));
}""",
       "house robber in two variables"),
    _b("""fn merge(mut intervals: Vec<(i32, i32)>) -> Vec<(i32, i32)> {
    intervals.sort_unstable();
    let mut merged: Vec<(i32, i32)> = Vec::new();
    for (start, end) in intervals {
        match merged.last_mut() {
            Some(last) if start <= last.1 => last.1 = last.1.max(end),
            _ => merged.push((start, end)),
        }
    }
    merged
}

fn main() {
    println!("{:?}", merge(vec![(1, 3), (8, 10), (2, 6), (9, 12)]));
}""",
       "merging overlapping intervals"),
    _b("""fn coin_ways(coins: &[usize], amount: usize) -> u64 {
    let mut ways = vec![0u64; amount + 1];
    ways[0] = 1;
    for &coin in coins {
        for total in coin..=amount {
            ways[total] += ways[total - coin];
        }
    }
    ways[amount]
}

fn main() {
    println!("{} {}", coin_ways(&[1, 2, 5], 5), coin_ways(&[2], 3));
}""",
       "counting the ways to make change"),
    _b("""use std::collections::HashMap;

fn main() {
    let words = ["eat", "tea", "tan", "ate", "nat", "bat"];
    let mut groups: HashMap<String, Vec<&str>> = HashMap::new();
    for word in words {
        let mut letters: Vec<char> = word.chars().collect();
        letters.sort_unstable();
        groups.entry(letters.into_iter().collect()).or_default().push(word);
    }
    let mut sorted: Vec<Vec<&str>> = groups.into_values().collect();
    sorted.sort_by(|a, b| b.len().cmp(&a.len()).then(a[0].cmp(b[0])));
    println!("{:?}", sorted);
}""",
       "grouping anagrams by sorted letters"),
    _b("""use std::collections::HashMap;

fn main() {
    let mut counts: HashMap<&str, i32> = HashMap::new();
    for word in "the cat and the hat and the bat".split(' ') {
        *counts.entry(word).or_insert(0) += 1;
    }
    let mut top: Vec<(&str, i32)> = counts.iter().map(|(&w, &n)| (w, n)).collect();
    top.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(b.0)));
    println!("{} {} {}", top[0].0, top[0].1, counts.len());
}""",
       "counting words with entry"),
    _b("""fn main() {
    let nums = [3, -1, 4, 1, 5, 9];
    let mut prefix = vec![0];
    for &x in &nums {
        prefix.push(prefix.last().unwrap() + x);
    }
    let range_sum = |i: usize, j: usize| prefix[j + 1] - prefix[i];
    println!("{:?} {} {}", prefix, range_sum(1, 3), range_sum(0, 5));
}""",
       "prefix sums and range queries"),
    _b("""fn longest(text: &str) -> usize {
    let mut last = [usize::MAX; 26];
    let (mut start, mut best) = (0usize, 0usize);
    for (end, b) in text.bytes().enumerate() {
        let slot = (b - b'a') as usize;
        if last[slot] != usize::MAX && last[slot] >= start { start = last[slot] + 1; }
        last[slot] = end;
        best = best.max(end - start + 1);
    }
    best
}

fn main() {
    println!("{} {} {}", longest("abcabcbb"), longest("bbbb"), longest("pwwkew"));
}""",
       "longest run of different letters"),
    _b("""fn main() {
    let nums = [12u32, 7, 8, 255, 0];
    let ones: Vec<u32> = nums.iter().map(|n| n.count_ones()).collect();
    let powers = nums.iter().filter(|&&n| n > 0 && n & (n - 1) == 0).count();
    let total = nums.iter().fold(0u32, |acc, &n| acc ^ n);
    println!("{:?} {} {}", ones, powers, total);
}""",
       "counting bits and xor"),
    _b("""fn main() {
    let (rows, cols) = (3, 4);
    let mut grid = vec![vec![1u32; cols]; rows];
    for r in 1..rows {
        for c in 1..cols {
            grid[r][c] = grid[r - 1][c] + grid[r][c - 1];
        }
    }
    println!("{} {:?}", grid[rows - 1][cols - 1], grid[1]);
}""",
       "paths through a grid"),
    _b("""use std::cmp::Reverse;

fn main() {
    let mut scores = vec![("ann", 90), ("bob", 72), ("cy", 90), ("di", 85)];
    scores.sort_by_key(|&(name, score)| (Reverse(score), name));
    let names: Vec<&str> = scores.iter().map(|&(name, _)| name).collect();
    println!("{}", names.join(","));
}""",
       "high score first with Reverse"),
    _b("""fn is_palindrome(text: &str) -> bool {
    let cleaned: Vec<char> = text.chars().filter(|c| c.is_alphanumeric()).collect();
    let (mut lo, mut hi) = (0, cleaned.len().saturating_sub(1));
    while lo < hi {
        if cleaned[lo].to_ascii_lowercase() != cleaned[hi].to_ascii_lowercase() { return false; }
        lo += 1;
        hi -= 1;
    }
    true
}

fn main() {
    println!("{} {} {}", is_palindrome("A man, a plan, a canal: Panama"), is_palindrome("abca"), is_palindrome(""));
}""",
       "palindrome with two pointers"),
)

#: What each block prints, by its note - worked out by hand before rustc was
#: asked, and held to the real run by tests/test_typing_rustalgo.py.
RUSTALGO_PRINTS: dict[str, str] = {
    "two sum with a map": "Some((0, 1)) None",
    "binary search": "0 -1",
    "matching brackets with a stack": "true false false",
    "breadth-first search for distances": "[0, 1, 1, 2]",
    "climbing stairs with a memo": "1 2 3 5 8 13 21",
    "house robber in two variables": "12 5 0",
    "merging overlapping intervals": "[(1, 6), (8, 12)]",
    "counting the ways to make change": "4 0",
    "grouping anagrams by sorted letters": '[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]',
    "counting words with entry": "the 3 5",
    "prefix sums and range queries": "[0, 3, 2, 6, 7, 12, 21] 4 21",
    "longest run of different letters": "3 1 3",
    "counting bits and xor": "[2, 3, 1, 8, 0] 1 252",
    "paths through a grid": "10 [1, 2, 3, 4]",
    "high score first with Reverse": "ann,cy,di,bob",
    "palindrome with two pointers": "true false true",
}
