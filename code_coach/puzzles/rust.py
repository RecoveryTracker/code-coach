"""Rust answers for the two-part puzzles.

Run through kata/rust_harness.py, which writes each case into the program as
Rust literals, so each part's parameter and return types are derived from the
Dart types every puzzle already declares (`rust_types` below): List<String>
is a Vec<String>, int an i32, String a String. Owned values in, because a
case is built fresh for every call. tests/test_puzzles.py runs every one
against the puzzle's cases.
"""

from __future__ import annotations


def rust_type(dart: str) -> str:
    """A puzzle's Dart type as the Rust type its answers take."""
    dart = dart.strip()
    simple = {"int": "i32", "double": "f64", "num": "f64", "String": "String", "bool": "bool"}
    if dart in simple:
        return simple[dart]
    if dart.startswith("List<") and dart.endswith(">"):
        return f"Vec<{rust_type(dart[5:-1])}>"
    raise ValueError(f"no Rust type for {dart}")


#: Puzzle id -> (part one, part two). Function names are part_one and part_two.
RUST: dict[str, tuple[str, str]] = {
    "pz-night-shift": (
        """fn part_one(log: Vec<String>) -> i32 {
    let mut inside = 0;
    for line in &log {
        let (kind, count) = line.split_once(' ').unwrap();
        let n: i32 = count.parse().unwrap();
        inside += if kind == "IN" { n } else { -n };
    }
    inside
}""",
        """fn part_two(log: Vec<String>) -> i32 {
    let (mut inside, mut most) = (0, 0);
    for line in &log {
        let (kind, count) = line.split_once(' ').unwrap();
        let n: i32 = count.parse().unwrap();
        inside += if kind == "IN" { n } else { -n };
        most = most.max(inside);
    }
    most
}""",
    ),
    "pz-sorting-station": (
        """fn part_one(parcels: Vec<String>) -> i32 {
    parcels.iter().filter(|p| p[1..].parse::<i32>().unwrap() > 10).count() as i32
}""",
        """fn part_two(parcels: Vec<String>) -> String {
    let mut totals = std::collections::BTreeMap::new();
    for p in &parcels {
        *totals.entry(p[..1].to_string()).or_insert(0) += p[1..].parse::<i32>().unwrap();
    }
    let mut best = String::new();
    let mut most = i32::MIN;
    for (zone, total) in &totals {
        if *total > most {
            most = *total;
            best = zone.clone();
        }
    }
    best
}""",
    ),
    "pz-the-lift": (
        """fn part_one(moves: Vec<String>) -> i32 {
    let mut floor = 0;
    for m in &moves {
        let amount: i32 = m[1..].parse().unwrap();
        floor += if m.starts_with('U') { amount } else { -amount };
    }
    floor
}""",
        """fn part_two(moves: Vec<String>) -> i32 {
    let mut floor = 0;
    for (i, m) in moves.iter().enumerate() {
        let amount: i32 = m[1..].parse().unwrap();
        floor += if m.starts_with('U') { amount } else { -amount };
        if floor < 0 {
            return i as i32 + 1;
        }
    }
    0
}""",
    ),
    "pz-class-vote": (
        """fn part_one(votes: Vec<String>) -> i32 {
    let mut counts = std::collections::HashMap::new();
    for name in &votes {
        *counts.entry(name.as_str()).or_insert(0) += 1;
    }
    counts.values().copied().max().unwrap_or(0)
}""",
        """fn part_two(votes: Vec<String>) -> String {
    let mut counts = std::collections::HashMap::new();
    for name in &votes {
        *counts.entry(name.as_str()).or_insert(0) += 1;
    }
    let most = counts.values().copied().max().unwrap_or(0);
    let mut seen = std::collections::HashMap::new();
    for name in &votes {
        let n = seen.entry(name.as_str()).or_insert(0);
        *n += 1;
        if *n == most {
            return name.clone();
        }
    }
    String::new()
}""",
    ),
    "pz-password-rules": (
        """fn part_one(passwords: Vec<String>) -> i32 {
    passwords
        .iter()
        .filter(|p| p.chars().count() >= 8 && p.chars().any(|c| c.is_ascii_digit()))
        .count() as i32
}""",
        """fn three_in_a_row(p: &str) -> bool {
    let chars: Vec<char> = p.chars().collect();
    chars.windows(3).any(|w| w[0] == w[1] && w[1] == w[2])
}

fn part_two(passwords: Vec<String>) -> i32 {
    passwords
        .iter()
        .filter(|p| p.chars().count() >= 8 && p.chars().any(|c| c.is_ascii_digit()))
        .filter(|p| !three_in_a_row(p))
        .count() as i32
}""",
    ),
    "pz-garden-grid": (
        """fn part_one(grid: Vec<String>) -> i32 {
    grid.iter().map(|row| row.matches('#').count() as i32).sum()
}""",
        """fn part_two(grid: Vec<String>) -> i32 {
    let cells: Vec<Vec<char>> = grid.iter().map(|row| row.chars().collect()).collect();
    let is_plant = |r: i32, c: i32| -> bool {
        r >= 0 && (r as usize) < cells.len() && c >= 0
            && (c as usize) < cells[r as usize].len() && cells[r as usize][c as usize] == '#'
    };
    let mut count = 0;
    for r in 0..cells.len() as i32 {
        for c in 0..cells[r as usize].len() as i32 {
            if is_plant(r, c)
                && [(1, 0), (-1, 0), (0, 1), (0, -1)].iter().any(|(dr, dc)| is_plant(r + dr, c + dc))
            {
                count += 1;
            }
        }
    }
    count
}""",
    ),
    "pz-brackets": (
        """fn part_one(text: String) -> bool {
    let mut stack = Vec::new();
    for ch in text.chars() {
        match ch {
            '(' | '[' | '{' => stack.push(ch),
            ')' | ']' | '}' => {
                let want = match ch { ')' => '(', ']' => '[', _ => '{' };
                if stack.pop() != Some(want) {
                    return false;
                }
            }
            _ => {}
        }
    }
    stack.is_empty()
}""",
        """fn part_two(text: String) -> String {
    let mut stack = Vec::new();
    for ch in text.chars() {
        match ch {
            '(' | '[' | '{' => stack.push(ch),
            ')' | ']' | '}' => {
                let want = match ch { ')' => '(', ']' => '[', _ => '{' };
                if stack.pop() != Some(want) {
                    return ch.to_string();
                }
            }
            _ => {}
        }
    }
    String::new()
}""",
    ),
    "pz-seat-map": (
        """fn part_one(rows: Vec<String>) -> i32 {
    rows.iter().map(|row| row.matches('.').count() as i32).sum()
}""",
        """fn part_two(rows: Vec<String>) -> i32 {
    let mut total = 0;
    for row in &rows {
        let seats: Vec<char> = row.chars().collect();
        for i in 0..seats.len() {
            let left = if i > 0 { seats[i - 1] } else { '.' };
            let right = if i + 1 < seats.len() { seats[i + 1] } else { '.' };
            if seats[i] == '.' && left == '.' && right == '.' {
                total += 1;
            }
        }
    }
    total
}""",
    ),
    "pz-traffic-light": (
        """fn part_one(log: Vec<String>) -> i32 {
    log.iter().filter(|colour| colour.as_str() == "green").count() as i32
}""",
        """fn part_two(log: Vec<String>) -> i32 {
    let (mut best, mut run) = (0, 0);
    for i in 0..log.len() {
        run = if i > 0 && log[i - 1] == log[i] { run + 1 } else { 1 };
        best = best.max(run);
    }
    best
}""",
    ),
    "pz-last-bus": (
        """fn minutes(clock: &str) -> i32 {
    let (h, m) = clock.split_once(':').unwrap();
    h.parse::<i32>().unwrap() * 60 + m.parse::<i32>().unwrap()
}

fn part_one(departures: Vec<String>, now: String) -> i32 {
    let now = minutes(&now);
    departures.iter().map(|d| minutes(d) - now).filter(|wait| *wait >= 0).min().unwrap_or(-1)
}""",
        """fn minutes(clock: &str) -> i32 {
    let (h, m) = clock.split_once(':').unwrap();
    h.parse::<i32>().unwrap() * 60 + m.parse::<i32>().unwrap()
}

fn part_two(departures: Vec<String>, now: String) -> i32 {
    let now = minutes(&now);
    departures.iter().map(|d| (minutes(d) - now).rem_euclid(1440)).min().unwrap_or(-1)
}""",
    ),
    "pz-word-chain": (
        """fn part_one(words: Vec<String>) -> bool {
    words.windows(2).all(|w| w[0].chars().last() == w[1].chars().next())
}""",
        """fn part_two(words: Vec<String>) -> i32 {
    if words.is_empty() {
        return 0;
    }
    let (mut best, mut run) = (1, 1);
    for w in words.windows(2) {
        run = if w[0].chars().last() == w[1].chars().next() { run + 1 } else { 1 };
        best = best.max(run);
    }
    best
}""",
    ),
    "pz-meeting-rooms": (
        """fn part_one(meetings: Vec<String>) -> i32 {
    meetings
        .iter()
        .map(|slot| {
            let (start, end) = slot.split_once('-').unwrap();
            end.parse::<i32>().unwrap() - start.parse::<i32>().unwrap()
        })
        .sum()
}""",
        """fn part_two(meetings: Vec<String>) -> i32 {
    let slots: Vec<(i32, i32)> = meetings
        .iter()
        .map(|slot| {
            let (start, end) = slot.split_once('-').unwrap();
            (start.parse().unwrap(), end.parse().unwrap())
        })
        .collect();
    (0..24)
        .map(|hour| slots.iter().filter(|(s, e)| *s <= hour && hour < *e).count() as i32)
        .max()
        .unwrap_or(0)
}""",
    ),
    "pz-walking-robot": (
        """fn part_one(commands: String) -> i32 {
    let steps = [(0, 1), (1, 0), (0, -1), (-1, 0)];
    let (mut x, mut y, mut facing) = (0i32, 0i32, 0usize);
    for c in commands.chars() {
        match c {
            'R' => facing = (facing + 1) % 4,
            'L' => facing = (facing + 3) % 4,
            _ => {
                x += steps[facing].0;
                y += steps[facing].1;
            }
        }
    }
    x.abs() + y.abs()
}""",
        """fn part_two(commands: String) -> i32 {
    let steps = [(0, 1), (1, 0), (0, -1), (-1, 0)];
    let (mut x, mut y, mut facing) = (0i32, 0i32, 0usize);
    let mut seen = std::collections::HashSet::from([(0, 0)]);
    for c in commands.chars() {
        match c {
            'R' => facing = (facing + 1) % 4,
            'L' => facing = (facing + 3) % 4,
            _ => {
                x += steps[facing].0;
                y += steps[facing].1;
                if !seen.insert((x, y)) {
                    return x.abs() + y.abs();
                }
            }
        }
    }
    -1
}""",
    ),
    "pz-shopping-list": (
        """fn part_one(lines: Vec<String>) -> i32 {
    lines.iter().map(|line| line.split_once(" x").unwrap().1.parse::<i32>().unwrap()).sum()
}""",
        """fn part_two(lines: Vec<String>) -> Vec<String> {
    let mut totals = std::collections::BTreeMap::new();
    for line in &lines {
        let (name, count) = line.split_once(" x").unwrap();
        *totals.entry(name.to_string()).or_insert(0) += count.parse::<i32>().unwrap();
    }
    totals.iter().map(|(name, n)| format!("{} x{}", name, n)).collect()
}""",
    ),
    "pz-warming-up": (
        """fn part_one(readings: Vec<i32>) -> i32 {
    readings.windows(2).map(|w| w[1] - w[0]).fold(0, |best, rise| best.max(rise))
}""",
        """fn part_two(readings: Vec<i32>) -> i32 {
    let (mut best, mut run) = (0, 0);
    for i in 0..readings.len() {
        run = if i > 0 && readings[i - 1] < readings[i] { run + 1 } else { 1 };
        best = best.max(run);
    }
    best
}""",
    ),
    "pz-step-counter": (
        """fn part_one(days: Vec<i32>) -> i32 {
    days.iter().sum()
}""",
        """fn part_two(days: Vec<i32>) -> i32 {
    days.windows(2).filter(|w| w[1] > w[0]).count() as i32
}""",
    ),
    "pz-car-park": (
        """fn part_one(log: Vec<String>) -> i32 {
    log.iter().filter(|e| e.as_str() == "in").count() as i32
}""",
        """fn part_two(log: Vec<String>) -> i32 {
    let (mut now, mut best) = (0, 0);
    for e in &log {
        now += if e == "in" { 1 } else { -1 };
        best = best.max(now);
    }
    best
}""",
    ),
    "pz-temperatures": (
        """fn part_one(readings: Vec<i32>) -> i32 {
    *readings.iter().max().unwrap()
}""",
        """fn part_two(readings: Vec<i32>) -> i32 {
    readings.windows(2).map(|w| w[1] - w[0]).fold(0, |best, rise| best.max(rise))
}""",
    ),
    "pz-receipts": (
        """fn part_one(lines: Vec<String>) -> i32 {
    lines.iter().map(|line| line.split_once(':').unwrap().1.parse::<i32>().unwrap()).sum()
}""",
        """fn part_two(lines: Vec<String>) -> String {
    let (mut best_name, mut best) = (String::new(), -1);
    for line in &lines {
        let (name, price) = line.split_once(':').unwrap();
        let price: i32 = price.parse().unwrap();
        if price > best {
            best_name = name.to_string();
            best = price;
        }
    }
    best_name
}""",
    ),
    "pz-digit-string": (
        """fn part_one(text: String) -> i32 {
    text.chars().map(|ch| ch.to_digit(10).unwrap() as i32).sum()
}""",
        """fn part_two(text: String) -> i32 {
    let digits: Vec<char> = text.chars().collect();
    digits.windows(2).filter(|w| w[1] > w[0]).map(|w| w[1].to_digit(10).unwrap() as i32).sum()
}""",
    ),
    "pz-stock-room": (
        """fn part_one(log: Vec<String>) -> i32 {
    let mut total = 0;
    for line in &log {
        let parts: Vec<&str> = line.split(' ').collect();
        let n: i32 = parts[2].parse().unwrap();
        total += if parts[0] == "add" { n } else { -n };
    }
    total
}""",
        """fn part_two(log: Vec<String>) -> Vec<String> {
    let mut stock = std::collections::BTreeMap::new();
    for line in &log {
        let parts: Vec<&str> = line.split(' ').collect();
        let n: i32 = parts[2].parse().unwrap();
        *stock.entry(parts[1].to_string()).or_insert(0) += if parts[0] == "add" { n } else { -n };
    }
    stock.into_iter().filter(|(_, n)| *n > 0).map(|(name, _)| name).collect()
}""",
    ),
}
