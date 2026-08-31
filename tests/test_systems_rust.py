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
    "sys-concurrency": """
        // A guard that unlocks when it drops.
        {
            let lock = Arc::new(Lock::new(0i64));
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&lock);
                workers.push(thread::spawn(move || {
                    for _ in 0..200 {
                        let mut held = mine.lock();
                        let seen = *held;
                        thread::yield_now();
                        *held = seen + 1;
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(*lock.lock() == 800, "the guard really excluded");
        }
        // Semaphore counts permits and blocks when there are none.
        {
            let sem = Arc::new(Semaphore::new(2));
            check(sem.available() == 2, "starts with its permits");
            sem.acquire();
            sem.acquire();
            check(sem.available() == 0, "permits run out");
            let got = Arc::new(AtomicBool::new(false));
            let waiter = {
                let mine = Arc::clone(&sem);
                let flag = Arc::clone(&got);
                thread::spawn(move || {
                    mine.acquire();
                    flag.store(true, Ordering::SeqCst);
                    mine.release();
                })
            };
            thread::sleep(std::time::Duration::from_millis(20));
            check(!got.load(Ordering::SeqCst), "a waiter blocks");
            sem.release();
            waiter.join().unwrap();
            check(got.load(Ordering::SeqCst), "and proceeds once released");
        }
        // RwLock: readers share, writers exclude.
        {
            let lock = Arc::new(RwLock::new());
            let most = Arc::new(AtomicUsize::new(0));
            let mut workers = Vec::new();
            for _ in 0..4 {
                let mine = Arc::clone(&lock);
                let peak = Arc::clone(&most);
                workers.push(thread::spawn(move || {
                    mine.read();
                    let now = mine.readers_now();
                    peak.fetch_max(now, Ordering::SeqCst);
                    thread::sleep(std::time::Duration::from_millis(10));
                    mine.read_done();
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(most.load(Ordering::SeqCst) > 1, "readers really do share");
            check(lock.readers_now() == 0, "and all left again");
        }
        // Barrier: nobody passes early.
        {
            let barrier = Arc::new(Barrier::new(3));
            let before = Arc::new(AtomicUsize::new(0));
            let bad = Arc::new(AtomicUsize::new(0));
            let mut workers = Vec::new();
            for _ in 0..3 {
                let mine = Arc::clone(&barrier);
                let arrived = Arc::clone(&before);
                let early = Arc::clone(&bad);
                workers.push(thread::spawn(move || {
                    arrived.fetch_add(1, Ordering::SeqCst);
                    mine.wait();
                    if arrived.load(Ordering::SeqCst) != 3 {
                        early.fetch_add(1, Ordering::SeqCst);
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(bad.load(Ordering::SeqCst) == 0, "nobody passed early");
        }
        // Channel moves everything across, in order.
        {
            let channel: Arc<Channel<usize>> = Arc::new(Channel::new());
            let consumer = {
                let mine = Arc::clone(&channel);
                thread::spawn(move || {
                    let mut got = Vec::new();
                    for _ in 0..500 {
                        got.push(mine.recv());
                    }
                    got
                })
            };
            for i in 0..500 {
                channel.send(i);
            }
            let got = consumer.join().unwrap();
            check(got.len() == 500, "everything came across");
            check(got.iter().enumerate().all(|(i, v)| *v == i), "in order");
            check(channel.try_recv().is_none(), "and the channel is empty");
        }
        // Scoped threads borrow the stack rather than owning a copy.
        {
            let items: Vec<i64> = (1..=1000).collect();
            let expected: i64 = items.iter().sum();
            check(sum_in_parallel(&items, 4) == expected,
                  "the parallel sum agrees with the serial one");
            check(sum_in_parallel(&items, 1) == expected, "one worker too");
            check(sum_in_parallel(&items, 7) == expected,
                  "and a worker count that does not divide the work");
            check(sum_in_parallel(&[], 4) == 0, "an empty slice sums to zero");
        }
        // Lock ordering: transfers both ways round never deadlock.
        {
            let a = Arc::new(Account { id: 0, balance: Mutex::new(1000) });
            let b = Arc::new(Account { id: 1, balance: Mutex::new(1000) });
            let mut workers = Vec::new();
            for round in 0..4 {
                let first = Arc::clone(&a);
                let second = Arc::clone(&b);
                workers.push(thread::spawn(move || {
                    for _ in 0..200 {
                        if round % 2 == 0 {
                            transfer(&first, &second, 1);
                        } else {
                            transfer(&second, &first, 1);
                        }
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            let total = *a.balance.lock().unwrap() + *b.balance.lock().unwrap();
            check(total == 2000, "money is conserved");
            check(!transfer(&a, &b, 100_000), "and an overdraft is refused");
        }
        // The pool runs every job before it shuts down.
        {
            let done = Arc::new(AtomicUsize::new(0));
            {
                let pool = ThreadPool::new(3);
                for _ in 0..50 {
                    let mine = Arc::clone(&done);
                    pool.submit(move || {
                        mine.fetch_add(1, Ordering::SeqCst);
                    });
                }
            }
            check(done.load(Ordering::SeqCst) == 50,
                  "the pool finished its queue before dropping");
        }
    """,
    "sys-cache": """
        // Cache line arithmetic.
        {
            check(CACHE_LINE == 64, "the number worth knowing");
            // An ordinary local array has no guaranteed alignment, so two
            // bytes 63 apart may straddle a line. Aligning it is what makes
            // the claim about lines checkable at all.
            let block = AlignedBlock([0u8; 128]);
            check(same_cache_line(&block.0[0], &block.0[63]),
                  "bytes inside one line share it");
            check(!same_cache_line(&block.0[0], &block.0[64]),
                  "and the next starts a new one");
            check(lines_spanned(1) == 1, "one byte is one line");
            check(lines_spanned(64) == 1, "so is exactly a line");
            check(lines_spanned(65) == 2, "one more is two");
            check(lines_spanned(0) == 0, "nothing spans nothing");
        }
        // False sharing: same answer either way, different layout.
        {
            let shared = Arc::new(Shared::new());
            let mut workers = Vec::new();
            for which in 0..2 {
                let mine = Arc::clone(&shared);
                workers.push(thread::spawn(move || {
                    for _ in 0..20000 {
                        if which == 0 {
                            mine.a.fetch_add(1, Ordering::Relaxed);
                        } else {
                            mine.b.fetch_add(1, Ordering::Relaxed);
                        }
                    }
                }));
            }
            for worker in workers {
                worker.join().unwrap();
            }
            check(shared.a.load(Ordering::Relaxed) == 20000 &&
                  shared.b.load(Ordering::Relaxed) == 20000,
                  "the shared pair still counts correctly");
            // The layout is the point, and it is checkable without timing.
            check(mem::size_of::<Shared>() <= CACHE_LINE,
                  "an unpadded pair is small enough to share a line");
            check(mem::align_of::<Padded>() == CACHE_LINE,
                  "and padding puts each on its own");
            check(mem::size_of::<PaddedPair>() >= 2 * CACHE_LINE,
                  "which really does cost the bytes");
        }
        // Row vs column: identical answers, different walks.
        {
            let rows = 64;
            let cols = 64;
            let grid: Vec<i64> = (0..(rows * cols) as i64).map(|i| i % 7).collect();
            let by_row = sum_by_rows(&grid, rows, cols);
            let by_col = sum_by_columns(&grid, rows, cols);
            check(by_row == by_col, "both walks reach the same total");
            check(by_row > 0, "and it is a real total");
        }
        // Struct layout: Rust reorders, repr(C) does not.
        {
            check(size_of_reordered() <= size_of_as_written(),
                  "Rust's own layout is no bigger than the C one");
            check(per_cache_line(size_of_reordered()) >=
                  per_cache_line(size_of_as_written()),
                  "so at least as many fit in a line");
            check(per_cache_line(0) == 0, "and nothing divides by zero");
        }
        // AoS vs SoA: same total.
        {
            let mut aos = Vec::new();
            let mut soa = Particles::new();
            for i in 0..100 {
                aos.push(Particle { x: i as f64, y: 0.0, z: 0.0, mass: 2.0 });
                soa.add(i as f64, 0.0, 0.0, 2.0);
            }
            check(total_mass_aos(&aos) == 200.0, "array of structs sums");
            check(soa.total_mass() == 200.0, "struct of arrays agrees");
            check(mem::size_of::<Particle>() == 4 * mem::size_of::<f64>(),
                  "a particle is its four doubles");
        }
        // Pointer chasing vs contiguous: same sum.
        {
            let items: Vec<i64> = (0..500).collect();
            let links = build_links(&items);
            check(walk_links(&links) == walk_slice(&items),
                  "both walks reach the same total");
            check(walk_links(&None) == 0, "an empty list sums to nothing");
        }
        // Branchless agrees with branchy.
        {
            let items: Vec<i64> = (0..1000).map(|i| (i * 37) % 256).collect();
            let branchy = sum_over(&items, 128);
            check(branchy == sum_over_branchless(&items, 128),
                  "branchless agrees with branchy");
            check(branchy > 0, "and there was something to add");
            let mut sorted = items.clone();
            sorted.sort();
            check(sum_over(&sorted, 128) == branchy,
                  "sorting changes the speed, not the answer");
        }
        // Blocked transpose: same result as the plain one.
        {
            let n = 64;
            let src: Vec<i64> = (0..(n * n) as i64).collect();
            let mut plain = vec![0i64; n * n];
            let mut blocked = vec![0i64; n * n];
            transpose_naive(&src, &mut plain, n);
            transpose_blocked(&src, &mut blocked, n, 8);
            check(plain == blocked, "blocking does not change the answer");
            check(plain[n] == 1, "and the transpose is actually transposed");
            let mut odd = vec![0i64; n * n];
            transpose_blocked(&src, &mut odd, n, 7);
            check(plain == odd, "a block size that does not divide n is fine");
        }
    """,
    "sys-market": """
        // Fixed point is exact where an f64 is not.
        {
            let a = Price::from_f64(0.1);
            let b = Price::from_f64(0.2);
            check(a + b == Price::from_f64(0.3),
                  "0.1 + 0.2 is exactly 0.3 in ticks");
            check(0.1 + 0.2 != 0.3, "...which is more than an f64 manages");
            check(Price::from_f64(1.2345).0 == 12345, "scaling is exact");
            check(Price::from_f64(-1.5).0 == -15000, "negatives round away");
            check((Price::from_f64(1.0) - Price::from_f64(0.25)).to_f64() == 0.75,
                  "subtraction comes back right");
            check(Price(1) < Price(2), "prices order by ticks");
        }
        // A level is a total, not a list.
        {
            let mut level = Level::new(Price::from_f64(10.0), 100);
            check(level.quantity == 100 && level.orders == 1, "one order in");
            level.add(50);
            check(level.quantity == 150 && level.orders == 2, "two orders in");
            level.remove(150);
            check(level.is_empty(), "emptied");
            level.remove(999);
            check(level.quantity == 0, "and does not go negative");
        }
        // The book keeps both sides sorted the right way round.
        {
            let mut book = OrderBook::new();
            book.add_bid(Price::from_f64(9.0), 10);
            book.add_bid(Price::from_f64(11.0), 20);
            book.add_bid(Price::from_f64(10.0), 30);
            book.add_ask(Price::from_f64(14.0), 10);
            book.add_ask(Price::from_f64(12.0), 20);
            book.add_ask(Price::from_f64(13.0), 30);
            check(book.best_bid().unwrap().price == Price::from_f64(11.0),
                  "best bid is the highest");
            check(book.best_ask().unwrap().price == Price::from_f64(12.0),
                  "best ask is the lowest");
            check(book.bids.windows(2).all(|w| w[0].price >= w[1].price),
                  "bids run high to low");
            check(book.asks.windows(2).all(|w| w[0].price <= w[1].price),
                  "asks run low to high");
            check(book.spread_ticks() == Some(10000), "one whole unit of spread");
            check(!book.crossed(), "and it is not crossed");
            book.add_bid(Price::from_f64(12.0), 5);
            check(book.crossed(), "a bid at the ask crosses it");
            let mut same = OrderBook::new();
            same.add_bid(Price::from_f64(5.0), 10);
            same.add_bid(Price::from_f64(5.0), 10);
            check(same.bids.len() == 1, "same price is one level");
            check(same.bids[0].quantity == 20, "with the quantities added");
            check(OrderBook::new().best_bid().is_none(), "an empty book has none");
            check(OrderBook::new().spread_ticks().is_none(), "and no spread");
        }
        // Matching eats the book outward from the best price.
        {
            let mut book = OrderBook::new();
            book.add_ask(Price::from_f64(10.0), 50);
            book.add_ask(Price::from_f64(11.0), 50);
            book.add_ask(Price::from_f64(12.0), 50);
            let fills = match_buy(&mut book, Price::from_f64(11.0), 80);
            check(fills.len() == 2, "it took two levels");
            check(fills[0].price == Price::from_f64(10.0), "starting at the best");
            check(fills[0].quantity == 50, "taking all of it");
            check(fills[1].quantity == 30, "and part of the next");
            check(filled_quantity(&fills) == 80, "filled exactly what was asked");
            check(book.asks.len() == 2, "the emptied level is gone");
            check(book.asks[0].quantity == 20, "the partial one is reduced");
            let mut untouched = OrderBook::new();
            untouched.add_ask(Price::from_f64(10.0), 50);
            check(match_buy(&mut untouched, Price::from_f64(9.0), 10).is_empty(),
                  "a limit below the ask fills nothing");
            check(untouched.asks[0].quantity == 50, "and leaves the book alone");
            let mut thin = OrderBook::new();
            thin.add_ask(Price::from_f64(10.0), 5);
            let partial = match_buy(&mut thin, Price::from_f64(99.0), 100);
            check(filled_quantity(&partial) == 5, "an empty book stops the fill");
            check(thin.asks.is_empty(), "and the book is cleared");
        }
        // VWAP weights by size.
        {
            let mut vwap = Vwap::new();
            check(vwap.value().is_none(), "no trades, no VWAP");
            vwap.add(Price::from_f64(10.0), 100);
            vwap.add(Price::from_f64(20.0), 300);
            check(vwap.value() == Some(Price::from_f64(17.5)),
                  "weighted toward the bigger trade");
            check(vwap.value().unwrap().to_f64() != 15.0,
                  "which is not the plain average");
            check(vwap.total_volume() == 400, "volume adds up");
        }
        // Rolling window drops the oldest.
        {
            let mut window = RollingWindow::new(3);
            check(window.mean().is_none(), "an empty window has no mean");
            window.push(10);
            window.push(20);
            window.push(30);
            check(window.len() == 3 && window.sum() == 60, "three in");
            check(window.mean() == Some(20.0), "mean of the three");
            check(window.highest() == Some(30), "and the highest");
            window.push(40);
            check(window.len() == 3 && window.sum() == 90, "the oldest fell out");
            check(window.mean() == Some(30.0), "and out of the mean");
            check(window.highest() == Some(40), "the new value is highest");
        }
        // Histogram answers percentiles without keeping samples.
        {
            let mut hist = Histogram::new(10, 100);
            check(hist.percentile(0.5).is_none(), "no samples, no percentile");
            for _ in 0..99 {
                hist.record(50);
            }
            hist.record(950);
            check(hist.samples() == 100, "every sample counted");
            check(hist.percentile(0.5) == Some(100), "the median is low");
            check(hist.percentile(0.999) == Some(1000), "the tail shows up");
            let mut narrow = Histogram::new(4, 10);
            narrow.record(100000);
            check(narrow.percentile(0.5) == Some(40),
                  "past the last bucket lands in it");
        }
        // Tick parsing, from bytes.
        {
            let tick = parse_tick(b"AAPL,123.45,500").unwrap();
            check(&tick.symbol[..4] == b"AAPL", "the symbol comes through");
            check(tick.symbol[4] == 0, "and is zero-filled after");
            check(tick.price == Price::from_f64(123.45), "the price is exact");
            check(tick.quantity == 500, "and so is the quantity");
            let whole = parse_tick(b"MSFT,7,10").unwrap();
            check(whole.price == Price::from_f64(7.0), "no decimal still scales");
            check(parse_tick(b"AAPL,123.45").is_none(), "a truncated tick fails");
            check(parse_tick(b"").is_none(), "and so does an empty line");
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
    "sys-cache": """
#[repr(align(64))]
struct AlignedBlock([u8; 128]);
""",
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
