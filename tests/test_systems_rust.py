"""Every Rust systems implementation is compiled and run.

These lean on `unsafe`, so the compiler is not the whole safety net the way
it usually is in Rust. A `MyBox` that forgets its Drop leaks silently, an
`Rc` whose count is wrong double-frees, and a `SpinLock` whose `unsafe impl
Sync` is a lie is a data race the borrow checker was explicitly told not to
look at. So they are executed, under threads where threads are the point.

The source compiled is the exact string the student is asked to type.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import run_code
from code_coach.systems.problems_rust import PATTERNS

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_RUSTC = shutil.which("rustc") is not None

CHECKS = {
    "sys-memory": """
        // MyBox derefs, mutates, and frees.
        {
            let mut boxed = MyBox::new(7);
            check(*boxed == 7, "MyBox reads through");
            *boxed = 9;
            check(*boxed == 9, "MyBox writes through");
            check(MyBox::new(String::from("hi")).len() == 2,
                  "deref coercion reaches the inner methods");
            let taken = MyBox::new(41).into_inner();
            check(taken == 41, "into_inner hands the value back");
        }
        // And the Drop really runs.
        {
            reset_drops();
            {
                let _held = MyBox::new(Noisy::new("box"));
                check(drop_count() == 0, "nothing dropped yet");
            }
            check(drop_count() == 1, "MyBox dropped what it owned");
        }
        // MyRc shares one count and frees once.
        {
            reset_drops();
            {
                let first = MyRc::new(Noisy::new("shared"));
                check(first.strong_count() == 1, "one owner");
                {
                    let second = first.clone();
                    check(first.strong_count() == 2, "clone bumps the count");
                    check(second.strong_count() == 2, "both see it");
                }
                check(first.strong_count() == 1, "the clone going away drops it");
                check(drop_count() == 0, "still alive while one holds it");
            }
            check(drop_count() == 1, "and freed exactly once");
        }
        // The borrow flag is what RefCell is checking.
        {
            let flag = BorrowFlag::new();
            check(flag.try_read(), "a first reader gets in");
            check(flag.try_read(), "and so does a second");
            check(flag.readers() == 2, "two readers counted");
            check(!flag.try_write(), "a writer cannot join readers");
            flag.release_read();
            flag.release_read();
            check(flag.try_write(), "and can once they leave");
            check(!flag.try_read(), "a reader cannot join a writer");
            check(!flag.try_write(), "nor can a second writer");
            flag.release_write();
            check(flag.try_read(), "and readers return afterwards");
        }
        // ScopeGuard runs on drop unless dismissed.
        {
            let ran = Cell::new(0);
            {
                let _g = ScopeGuard::new(|| ran.set(ran.get() + 1));
            }
            check(ran.get() == 1, "ScopeGuard ran on the way out");
            {
                let mut g = ScopeGuard::new(|| ran.set(ran.get() + 1));
                g.dismiss();
            }
            check(ran.get() == 1, "a dismissed guard does not run");
        }
        // An index arena sidesteps the borrow checker.
        {
            let mut arena: Arena<i32> = Arena::new();
            check(arena.is_empty(), "a fresh arena is empty");
            let first = arena.add(10);
            let second = arena.add(20);
            check(arena.len() == 2, "two items in");
            check(arena.get(first) == Some(&10), "the first is there");
            check(arena.get(second) == Some(&20), "and the second");
            check(first != second, "ids are distinct");
            if let Some(slot) = arena.get_mut(first) {
                *slot = 99;
            }
            check(arena.get(first) == Some(&99), "and they can be edited");
        }
        // SmallVec spills to the heap as a variant change.
        {
            let mut v: SmallVec<i32> = SmallVec::new();
            v.push(1);
            v.push(2);
            check(v.len() == 2, "SmallVec counts");
            check(!v.on_heap(), "and stays inline while it fits");
            v.push(3);
            v.push(4);
            check(!v.on_heap(), "still inline at capacity");
            v.push(5);
            check(v.on_heap(), "and spills when it outgrows");
            check(v.len() == 5, "keeping everything");
        }
        // Drop order: fields in declaration order, locals in reverse.
        {
            let log = Recorder { order: RefCell::new(Vec::new()) };
            {
                let _pair = Pair {
                    first: Noisy2::new("first", &log),
                    second: Noisy2::new("second", &log),
                };
            }
            check(log.order.borrow().as_slice() == ["first", "second"],
                  "struct fields drop in declaration order");
            let log2 = Recorder { order: RefCell::new(Vec::new()) };
            {
                let _a = Noisy2::new("a", &log2);
                let _b = Noisy2::new("b", &log2);
            }
            check(log2.order.borrow().as_slice() == ["b", "a"],
                  "locals drop in reverse");
        }
        // mem::take moves out without cloning.
        {
            let mut buffer = Buffer::new(vec![1, 2, 3]);
            check(buffer.len() == 3, "three in");
            let taken = buffer.drain();
            check(taken == vec![1, 2, 3], "everything came out");
            check(buffer.len() == 0, "and the buffer is empty");
            let mut second = Buffer::new(vec![9]);
            let old = second.swap_in(vec![7, 8]);
            check(old == vec![9], "replace hands back the old one");
            check(second.len() == 2, "and installs the new one");
        }
    """,
    "sys-lockfree": """
        // Atomicity is not ordering: both totals are exact.
        {
            let counter = Arc::new(Counter::new());
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&counter);
                workers.push(thread::spawn(move || {
                    for _ in 0..5000 {
                        mine.bump_relaxed();
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(counter.get() == 20000, "relaxed increments lose nothing");

            let ordered = Arc::new(Counter::new());
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&ordered);
                workers.push(thread::spawn(move || {
                    for _ in 0..5000 {
                        mine.bump_ordered();
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(ordered.get() == 20000, "seq_cst increments lose nothing");
        }
        // The CAS loop settles on the real maximum.
        {
            let best = Arc::new(AtomicMax::new());
            let mut workers = Vec::new();
            for i in 1..=4 {
                let mine = Arc::clone(&best);
                workers.push(thread::spawn(move || {
                    for n in 1..=1000 {
                        mine.offer(n * i);
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(best.get() == 4000, "CAS loop finds the true maximum");
        }
        // SpinLock excludes. Read, yield, write, or the race never shows.
        {
            let lock = Arc::new(SpinLock::new(0i64));
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&lock);
                workers.push(thread::spawn(move || {
                    for _ in 0..200 {
                        mine.with(|value| {
                            let seen = *value;
                            thread::yield_now();
                            *value = seen + 1;
                        });
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(lock.with(|value| *value) == 800, "SpinLock excludes");
        }
        // Treiber stack conserves every push.
        {
            let stack: Arc<TreiberStack<i32>> = Arc::new(TreiberStack::new());
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&stack);
                workers.push(thread::spawn(move || {
                    for _ in 0..500 {
                        mine.push(1);
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            let mut total = 0;
            while let Some(value) = stack.pop() {
                total += value;
            }
            check(total == 2000, "Treiber stack kept every push");
            check(stack.pop().is_none(), "and is empty afterwards");
        }
        // SPSC: everything across, in order, nothing duplicated.
        {
            let queue: Arc<SpscQueue<usize>> = Arc::new(SpscQueue::new(64));
            let total = 20000usize;
            let consumer = {
                let mine = Arc::clone(&queue);
                thread::spawn(move || {
                    let mut got = Vec::with_capacity(total);
                    while got.len() < total {
                        if let Some(value) = mine.pop() {
                            got.push(value);
                        }
                    }
                    got
                })
            };
            for i in 0..total {
                while !queue.push(i) {}
            }
            let got = consumer.join().unwrap();
            check(got.len() == total, "SPSC moved everything");
            let ordered = got.iter().enumerate().all(|(i, v)| *v == i);
            check(ordered, "SPSC kept the order and duplicated nothing");
            check(queue.pop().is_none(), "an empty queue pops nothing");
        }
        // Acquire/release publishes the payload with the flag.
        {
            for _ in 0..200 {
                let box_ = Arc::new(Mailbox::new());
                let reader = {
                    let mine = Arc::clone(&box_);
                    thread::spawn(move || loop {
                        if let Some(pair) = mine.collect() {
                            return pair;
                        }
                    })
                };
                box_.publish(11, 22);
                let seen = reader.join().unwrap();
                check(seen == (11, 22), "the flag published the payload");
            }
        }
        // Once runs exactly once, however many ask.
        {
            let once = Arc::new(Once::new());
            let ran = Arc::new(Counter::new());
            let mut workers = Vec::new();
            for _ in 0..8 {
                let mine = Arc::clone(&once);
                let count = Arc::clone(&ran);
                workers.push(thread::spawn(move || {
                    mine.call(|| count.bump_ordered());
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(ran.get() == 1, "Once ran exactly once");
            check(once.finished(), "and says so afterwards");
        }
        // Exactly one releaser is told it was last.
        {
            let refs = Arc::new(AtomicRefCount::new());
            check(refs.count() == 1, "starts at one");
            for _ in 0..7 {
                refs.acquire();
            }
            check(refs.count() == 8, "acquires add up");
            let claimed = Arc::new(Counter::new());
            let mut workers = Vec::new();
            for _ in 0..8 {
                let mine = Arc::clone(&refs);
                let count = Arc::clone(&claimed);
                workers.push(thread::spawn(move || {
                    if mine.release() {
                        count.bump_ordered();
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(claimed.get() == 1, "exactly one releaser was last");
            check(refs.count() == 0, "and the count reached zero");
        }
    """,
}

# A type whose Drop is observable is the only honest way to ask whether a
# smart pointer actually freed anything.
HELPERS = """
use std::sync::atomic::AtomicUsize as DropCounter;
use std::sync::atomic::Ordering as DropOrdering;

static DROPS: DropCounter = DropCounter::new(0);

fn reset_drops() {
    DROPS.store(0, DropOrdering::SeqCst);
}

fn drop_count() -> usize {
    DROPS.load(DropOrdering::SeqCst)
}

struct Noisy {
    _name: &'static str,
}

impl Noisy {
    fn new(name: &'static str) -> Self {
        Noisy { _name: name }
    }
}

impl Drop for Noisy {
    fn drop(&mut self) {
        DROPS.fetch_add(1, DropOrdering::SeqCst);
    }
}

static mut FAILURES: usize = 0;

fn check(ok: bool, label: &str) {
    if !ok {
        println!("FAILED: {}", label);
        unsafe {
            FAILURES += 1;
        }
    }
}
"""

# The drop-order exercise defines its own noisy type against a Recorder, so
# the checks need one that matches that shape rather than the counter above.
EXTRA_HELPERS = {
    "sys-memory": """
pub struct Noisy2<'a> {
    name: &'static str,
    log: &'a Recorder,
}

impl<'a> Noisy2<'a> {
    fn new(name: &'static str, log: &'a Recorder) -> Self {
        Noisy2 { name, log }
    }
}

impl<'a> Drop for Noisy2<'a> {
    fn drop(&mut self) {
        self.log.order.borrow_mut().push(self.name);
    }
}

pub struct Pair<'a> {
    pub first: Noisy2<'a>,
    pub second: Noisy2<'a>,
}
""",
}

REPORT = """
    unsafe {
        if FAILURES > 0 {
            std::process::exit(1);
        }
    }
    println!("ok");
"""


@unittest.skipUnless(HAS_RUSTC, "needs rustc on PATH")
class RustSystemsTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.extend(
            p.code
            for p in pattern.problems
            # The bank's own Pair/Noisy for the drop-order exercise would
            # clash with the checks' versions, so the checks supply theirs.
            if not (pattern_id == "sys-memory" and p.number == 9107)
        )
        parts.append(BANK_DROP_ORDER if pattern_id == "sys-memory" else "")
        parts.append(HELPERS)
        if pattern_id in EXTRA_HELPERS:
            parts.append(EXTRA_HELPERS[pattern_id])
        parts.append("fn main() {\n" + CHECKS[pattern_id] + REPORT + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="rust")
        self.assertEqual(code, 0, (err or out)[:3000])
        self.assertEqual(out.strip(), "ok", out[:3000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


# The Recorder from the drop-order problem, without the Noisy/Pair the
# checks define themselves.
BANK_DROP_ORDER = """
pub struct Recorder {
    pub order: RefCell<Vec<&'static str>>,
}
"""


class ShapeTests(unittest.TestCase):
    def test_every_pattern_has_checks(self) -> None:
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_every_pattern_is_a_full_class(self) -> None:
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertEqual(len(pattern.problems), 8)

    def test_it_shares_class_ids_with_the_cpp_bank(self) -> None:
        """Same class, different language — so switching keeps your place."""
        from code_coach.systems.problems_cpp import PATTERNS as CPP

        cpp_ids = {p.id for p in CPP}
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertIn(pattern.id, cpp_ids)

    def test_the_curriculum_offers_only_what_rust_has(self) -> None:
        """The C++ bank is ahead; Rust must not be offered the difference."""
        from code_coach.curriculum.catalog import classes_for_language

        offered = {
            c.id for c in classes_for_language("rust") if c.id.startswith("sys-")
        }
        self.assertEqual(offered, {p.id for p in PATTERNS})


if __name__ == "__main__":
    unittest.main()
