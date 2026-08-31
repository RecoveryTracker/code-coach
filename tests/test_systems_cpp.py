"""Every systems implementation is compiled and run against real cases.

These are primitives, so a plausible-looking one that is subtly wrong is the
normal failure — a spinlock that does not actually exclude, a refcount that
double-frees, a barrier a fast thread can lap. Reading does not catch that.
So each pattern is built into one program and exercised, threads and all.

The source compiled is the exact string the student is asked to type, read
out of the bank rather than a copy beside it.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import msvc_available, run_code
from code_coach.systems.problems_cpp import PATTERNS

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_CPP = any(shutil.which(c) for c in ("g++", "clang++")) or msvc_available()

CHECKS = {
    "sys-memory": """
        // UniquePtr: one owner, and moving empties the source.
        {
            UniquePtr<int> a(new int(7));
            check(*a == 7, "UniquePtr reads through");
            UniquePtr<int> b(static_cast<UniquePtr<int>&&>(a));
            check(!a, "UniquePtr move empties the source");
            check(*b == 7, "UniquePtr move keeps the value");
            int* raw = b.release();
            check(!b, "release empties it");
            delete raw;
        }
        // The destructor really runs.
        {
            Counted::alive = 0;
            {
                UniquePtr<Counted> owner(new Counted());
                check(Counted::alive == 1, "UniquePtr holds one alive");
            }
            check(Counted::alive == 0, "UniquePtr frees on scope exit");
        }
        // SharedPtr: the count is shared, and the last one frees.
        {
            Counted::alive = 0;
            {
                SharedPtr<Counted> a(new Counted());
                check(a.use_count() == 1, "SharedPtr starts at one");
                {
                    SharedPtr<Counted> b = a;
                    check(a.use_count() == 2, "copy bumps the count");
                    check(b.get() == a.get(), "copy points at the same object");
                }
                check(a.use_count() == 1, "the copy going away drops it");
                check(Counted::alive == 1, "still alive while one holds it");
            }
            check(Counted::alive == 0, "the last one frees");
        }
        // Optional: no value until there is one, and it destroys what it held.
        {
            Counted::alive = 0;
            Optional<int> nothing;
            check(!nothing.has_value(), "empty Optional");
            check(nothing.value_or(5) == 5, "value_or falls back");
            Optional<int> something(3);
            check(something.has_value(), "filled Optional");
            check(something.value() == 3, "Optional holds the value");
            check(something.value_or(5) == 3, "value_or prefers the value");
            something.reset();
            check(!something.has_value(), "reset empties it");
            {
                Optional<Counted> held = Optional<Counted>(Counted());
                check(Counted::alive >= 1, "Optional holds one alive");
            }
            check(Counted::alive == 0, "Optional destroys what it held");
        }
        // ScopeGuard: runs on the way out, unless dismissed.
        {
            int ran = 0;
            {
                auto g = guard([&ran] { ran++; });
            }
            check(ran == 1, "ScopeGuard runs on scope exit");
            {
                auto g = guard([&ran] { ran++; });
                g.dismiss();
            }
            check(ran == 1, "a dismissed guard does not run");
        }
        // Arena: bump allocate, reset frees everything at once.
        {
            Arena arena(128);
            void* first = arena.allocate(8, 8);
            void* second = arena.allocate(8, 8);
            check(first != nullptr && second != nullptr, "arena hands out memory");
            check(first != second, "arena does not hand out the same slot twice");
            check(arena.bytes_used() >= 16, "arena tracks what it gave away");
            check(arena.allocate(1000, 1) == nullptr, "arena refuses when full");
            arena.reset();
            check(arena.bytes_used() == 0, "reset frees everything");
            // Alignment is honoured.
            Arena tight(128);
            tight.allocate(1, 1);
            void* aligned = tight.allocate(8, 8);
            check(reinterpret_cast<size_t>(aligned) % 8 == 0,
                  "arena honours alignment");
        }
        // SmallVector: no heap while it is small.
        {
            SmallVector<int, 4> v;
            v.push_back(1);
            v.push_back(2);
            check(v.size() == 2, "SmallVector counts");
            check(!v.on_heap(), "SmallVector stays inline while it fits");
            check(v[0] == 1 && v[1] == 2, "SmallVector keeps the values");
            v.push_back(3);
            v.push_back(4);
            check(!v.on_heap(), "still inline at capacity");
            v.push_back(5);
            check(v.on_heap(), "SmallVector moves to the heap when it outgrows");
            check(v.size() == 5 && v[4] == 5, "values survive the move");
            check(v[0] == 1, "and so do the earlier ones");
        }
        // Intrusive refcount.
        {
            Counted::alive = 0;
            {
                Tracked* raw = new Tracked();
                check(Counted::alive == 1, "one alive");
                {
                    RefPtr<Tracked> a(raw);
                    check(raw->references() == 1, "one reference");
                    {
                        RefPtr<Tracked> b = a;
                        check(raw->references() == 2, "copy bumps it");
                    }
                    check(raw->references() == 1, "and drops it again");
                }
                check(Counted::alive == 0, "the last RefPtr frees it");
            }
        }
        // Slot: construct into storage you already own.
        {
            Counted::alive = 0;
            {
                Slot<Counted> slot;
                check(slot.empty(), "Slot starts empty");
                slot.construct();
                check(!slot.empty(), "Slot is filled after construct");
                check(Counted::alive == 1, "constructing really made one");
                slot.destroy();
                check(Counted::alive == 0, "destroy really destroyed it");
                check(slot.empty(), "Slot is empty again");
            }
            Slot<double> aligned;
            check(Slot<double>::alignment() == alignof(double),
                  "Slot reports the right alignment");
        }
    """,
    "sys-concurrency": """
        // SpinLock actually excludes.
        {
            SpinLock lock;
            long long counter = 0;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&lock, &counter] {
                    for (int n = 0; n < 200; n++) {
                        lock.lock();
                        long long seen = counter;
                        this_thread::yield();
                        counter = seen + 1;
                        lock.unlock();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(counter == 800, "SpinLock excludes: no lost updates");
            check(lock.try_lock(), "try_lock takes a free lock");
            check(!lock.try_lock(), "try_lock refuses a held lock");
            lock.unlock();
        }
        // TicketLock excludes too, and is fair.
        {
            TicketLock lock;
            long long counter = 0;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&lock, &counter] {
                    for (int n = 0; n < 200; n++) {
                        lock.lock();
                        long long seen = counter;
                        this_thread::yield();
                        counter = seen + 1;
                        lock.unlock();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(counter == 800, "TicketLock excludes");
        }
        // Semaphore counts permits.
        {
            Semaphore sem(2);
            check(sem.available() == 2, "semaphore starts with its permits");
            sem.acquire();
            sem.acquire();
            check(sem.available() == 0, "permits run out");
            atomic<bool> got{false};
            thread waiter([&sem, &got] {
                sem.acquire();
                got.store(true);
                sem.release();
            });
            this_thread::sleep_for(chrono::milliseconds(20));
            check(!got.load(), "a waiter blocks when there are no permits");
            sem.release();
            waiter.join();
            check(got.load(), "and proceeds once one is released");
        }
        // RWLock lets readers share and writers exclude.
        {
            RWLock lock;
            atomic<int> readers_inside{0};
            atomic<int> most_at_once{0};
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&] {
                    lock.lock_shared();
                    int now = ++readers_inside;
                    int seen = most_at_once.load();
                    while (now > seen &&
                           !most_at_once.compare_exchange_weak(seen, now)) {
                    }
                    this_thread::sleep_for(chrono::milliseconds(10));
                    --readers_inside;
                    lock.unlock_shared();
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(most_at_once.load() > 1, "readers really do share");
            long long counter = 0;
            workers.clear();
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&lock, &counter] {
                    for (int n = 0; n < 100; n++) {
                        lock.lock();
                        long long seen = counter;
                        this_thread::yield();
                        counter = seen + 1;
                        lock.unlock();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(counter == 400, "writers exclude each other");
        }
        // Barrier holds everyone until the last arrives.
        {
            Barrier barrier(3);
            atomic<int> before{0};
            atomic<int> after{0};
            vector<thread> workers;
            for (int i = 0; i < 3; i++) {
                workers.emplace_back([&] {
                    before++;
                    barrier.arrive_and_wait();
                    check(before.load() == 3,
                          "nobody passes the barrier early");
                    after++;
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(after.load() == 3, "everyone passes once the last arrives");
        }
        // CallOnce runs exactly once, however many ask.
        {
            OnceFlag once;
            atomic<int> ran{0};
            vector<thread> workers;
            for (int i = 0; i < 8; i++) {
                workers.emplace_back([&] {
                    once.call([&ran] { ran++; });
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(ran.load() == 1, "CallOnce runs exactly once");
            check(once.finished(), "and says so afterwards");
        }
        // BlockingQueue moves everything across, in order.
        {
            BlockingQueue<int> queue(4);
            vector<int> got;
            thread consumer([&queue, &got] {
                for (int i = 0; i < 20; i++) {
                    got.push_back(queue.pop());
                }
            });
            for (int i = 0; i < 20; i++) {
                queue.push(i);
            }
            consumer.join();
            check(got.size() == 20, "everything came across");
            bool ordered = true;
            for (int i = 0; i < 20; i++) {
                if (got[i] != i) {
                    ordered = false;
                }
            }
            check(ordered, "and in the order it was sent");
        }
        // ThreadPool runs every job before it shuts down.
        {
            atomic<int> done{0};
            {
                ThreadPool pool(3);
                for (int i = 0; i < 50; i++) {
                    pool.submit([&done] { done++; });
                }
            }
            check(done.load() == 50,
                  "the pool finishes its queue before destructing");
        }
    """,
    "sys-lockfree": """
        // Atomicity is not ordering: both counts are exact.
        {
            Counter counter;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&counter] {
                    for (int n = 0; n < 5000; n++) {
                        counter.bump_relaxed();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(counter.get() == 20000, "relaxed increments lose nothing");
            Counter ordered;
            workers.clear();
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&ordered] {
                    for (int n = 0; n < 5000; n++) {
                        ordered.bump_ordered();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(ordered.get() == 20000, "seq_cst increments lose nothing");
        }
        // CAS loop settles on the real maximum.
        {
            AtomicMax best;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&best, i] {
                    for (int n = 1; n <= 1000; n++) {
                        best.offer((long long)n * (i + 1));
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(best.get() == 4000, "CAS loop finds the true maximum");
        }
        // SPSC queue: everything across, in order, nothing duplicated.
        {
            SpscQueue<int, 64> queue;
            const int total = 20000;
            vector<int> got;
            got.reserve(total);
            thread consumer([&queue, &got, total] {
                int value = 0;
                while ((int)got.size() < total) {
                    if (queue.pop(value)) {
                        got.push_back(value);
                    }
                }
            });
            for (int i = 0; i < total; i++) {
                while (!queue.push(i)) {
                }
            }
            consumer.join();
            check((int)got.size() == total, "SPSC moved everything");
            bool ordered = true;
            for (int i = 0; i < total; i++) {
                if (got[i] != i) {
                    ordered = false;
                    break;
                }
            }
            check(ordered, "SPSC kept the order and duplicated nothing");
            int spare = 0;
            check(!queue.pop(spare), "an empty SPSC queue pops nothing");
        }
        // Treiber stack conserves what was pushed.
        {
            TreiberStack<int> stack;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&stack] {
                    for (int n = 0; n < 500; n++) {
                        stack.push(1);
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            long long total = 0;
            int value = 0;
            while (stack.pop(value)) {
                total += value;
            }
            check(total == 2000, "Treiber stack kept every push");
            check(!stack.pop(value), "and is empty afterwards");
        }
        // Seqlock: a reader never sees half of a write.
        {
            Seqlock book;
            atomic<bool> stop{false};
            atomic<long long> torn{0};
            atomic<long long> reads{0};
            // Every entry is written to the same number, so any reader that
            // catches a write half-done sees two different numbers in one
            // book — which is exactly what a torn read is.
            thread writer([&book, &stop] {
                long long n = 1;
                while (!stop.load(memory_order_relaxed)) {
                    Book fresh;
                    for (int i = 0; i < 4; i++) {
                        fresh.bid[i] = n;
                        fresh.ask[i] = n;
                    }
                    book.write(fresh);
                    n++;
                }
            });
            thread reader([&book, &stop, &torn, &reads] {
                while (!stop.load(memory_order_relaxed)) {
                    Book seen = book.read();
                    reads.fetch_add(1, memory_order_relaxed);
                    long long first = seen.bid[0];
                    bool consistent = true;
                    for (int i = 0; i < 4; i++) {
                        if (seen.bid[i] != first || seen.ask[i] != first) {
                            consistent = false;
                        }
                    }
                    if (!consistent) {
                        torn.fetch_add(1, memory_order_relaxed);
                    }
                }
            });
            this_thread::sleep_for(chrono::milliseconds(60));
            stop.store(true);
            writer.join();
            reader.join();
            check(reads.load() > 0, "the seqlock reader actually ran");
            check(torn.load() == 0, "no reader ever saw a torn pair");
        }
        // Acquire/release publishes the payload with the flag.
        {
            for (int round = 0; round < 200; round++) {
                Mailbox box;
                atomic<int> mismatches{0};
                thread reader([&box, &mismatches] {
                    int a = 0;
                    int b = 0;
                    while (!box.collect(a, b)) {
                    }
                    if (a != 11 || b != 22) {
                        mismatches++;
                    }
                });
                box.publish(11, 22);
                reader.join();
                check(mismatches.load() == 0,
                      "the flag published the payload with it");
            }
        }
        // Backoff lock still excludes.
        {
            BackoffLock lock;
            long long counter = 0;
            vector<thread> workers;
            for (int i = 0; i < 4; i++) {
                workers.emplace_back([&lock, &counter] {
                    for (int n = 0; n < 200; n++) {
                        lock.lock();
                        long long seen = counter;
                        this_thread::yield();
                        counter = seen + 1;
                        lock.unlock();
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(counter == 800, "BackoffLock excludes");
        }
        // Atomic refcount: exactly one release reports last.
        {
            AtomicRefCount refs;
            check(refs.count() == 1, "starts at one");
            for (int i = 0; i < 7; i++) {
                refs.acquire();
            }
            check(refs.count() == 8, "acquires add up");
            atomic<int> claimed_last{0};
            vector<thread> workers;
            for (int i = 0; i < 8; i++) {
                workers.emplace_back([&refs, &claimed_last] {
                    if (refs.release()) {
                        claimed_last++;
                    }
                });
            }
            for (thread& w : workers) {
                w.join();
            }
            check(claimed_last.load() == 1,
                  "exactly one releaser is told it was last");
            check(refs.count() == 0, "and the count reached zero");
        }
    """,
    "sys-cache": """
        // Cache line arithmetic.
        {
            check(CACHE_LINE == 64, "the number worth knowing");
            alignas(CACHE_LINE) char block[128];
            check(same_cache_line(&block[0], &block[63]),
                  "bytes inside one line share it");
            check(!same_cache_line(&block[0], &block[64]),
                  "and the next byte starts a new one");
            check(lines_spanned(1) == 1, "one byte is one line");
            check(lines_spanned(64) == 1, "so is exactly a line");
            check(lines_spanned(65) == 2, "one more byte is two");
            check(lines_spanned(0) == 0, "nothing spans nothing");
        }
        // False sharing: same answer either way, different layout.
        {
            Shared shared;
            hammer(shared, 20000);
            check(shared.a.load() == 20000 && shared.b.load() == 20000,
                  "the shared pair still counts correctly");
            Padded padded;
            hammer(padded, 20000);
            check(padded.a.load() == 20000 && padded.b.load() == 20000,
                  "and so does the padded one");
            // The layout is the point, and it is checkable without timing.
            // Whether these two actually land on one line depends on where
            // the struct fell, so the checkable fact is that they are small
            // enough to — and that the padded pair cannot possibly.
            check(sizeof(Shared) <= CACHE_LINE,
                  "unpadded counters are small enough to share a line");
            check(sizeof(Padded) >= 2 * CACHE_LINE,
                  "padding really does cost the bytes");
            check(alignof(Padded) == CACHE_LINE,
                  "and puts each counter on its own line");
        }
        // Row vs column: identical answers, different walks.
        {
            size_t rows = 64;
            size_t cols = 64;
            vector<int> grid(rows * cols);
            for (size_t i = 0; i < grid.size(); i++) {
                grid[i] = (int)(i % 7);
            }
            long long by_row = sum_by_rows(grid, rows, cols);
            long long by_col = sum_by_columns(grid, rows, cols);
            check(by_row == by_col, "both walks reach the same total");
            check(by_row > 0, "and it is a real total");
        }
        // Struct packing: field order changes the size.
        {
            check(sizeof(Tight) < sizeof(Loose),
                  "ordering fields large to small is smaller");
            check(wasted_bytes() > 0, "the loose one really does waste bytes");
            check(per_cache_line(sizeof(Tight)) >=
                      per_cache_line(sizeof(Loose)),
                  "so more of them fit in a line");
            check(per_cache_line(0) == 0, "and nothing divides by zero");
        }
        // AoS vs SoA: same total, different bytes touched.
        {
            vector<Particle> aos;
            Particles soa;
            for (int i = 0; i < 100; i++) {
                aos.push_back(Particle{(double)i, 0.0, 0.0, 2.0});
                soa.add((double)i, 0.0, 0.0, 2.0);
            }
            check(total_mass(aos) == 200.0, "array of structs sums the mass");
            check(total_mass(soa) == 200.0, "struct of arrays agrees");
            check(sizeof(Particle) == 4 * sizeof(double),
                  "a particle is its four doubles");
        }
        // Pointer chasing vs contiguous: same sum.
        {
            vector<int> items;
            for (int i = 0; i < 500; i++) {
                items.push_back(i);
            }
            vector<Link> nodes(items.size());
            for (size_t i = 0; i < items.size(); i++) {
                nodes[i].value = items[i];
                nodes[i].next = (i + 1 < items.size()) ? &nodes[i + 1] : nullptr;
            }
            check(walk_links(&nodes[0]) == walk_array(items),
                  "both walks reach the same total");
            check(walk_links(nullptr) == 0, "an empty list sums to nothing");
        }
        // Branch prediction: branchless agrees with branchy.
        {
            vector<int> items;
            for (int i = 0; i < 1000; i++) {
                items.push_back((i * 37) % 256);
            }
            long long branchy = sum_over(items, 128);
            long long branchless = sum_over_branchless(items, 128);
            check(branchy == branchless, "branchless agrees with branchy");
            check(branchy > 0, "and there was something to add");
            // Sorting does not change the answer, only the cost.
            vector<int> sorted = items;
            for (size_t i = 1; i < sorted.size(); i++) {
                int value = sorted[i];
                size_t j = i;
                while (j > 0 && sorted[j - 1] > value) {
                    sorted[j] = sorted[j - 1];
                    j--;
                }
                sorted[j] = value;
            }
            check(sum_over(sorted, 128) == branchy,
                  "sorting changes the speed, not the answer");
        }
        // Blocked transpose: same result as the plain one.
        {
            size_t n = 64;
            vector<int> src(n * n);
            for (size_t i = 0; i < src.size(); i++) {
                src[i] = (int)i;
            }
            vector<int> plain(n * n, 0);
            vector<int> blocked(n * n, 0);
            transpose_naive(src, plain, n);
            transpose_blocked(src, blocked, n, 8);
            check(plain == blocked, "blocking does not change the answer");
            check(plain[1 * n + 0] == (int)(0 * n + 1),
                  "and the transpose is actually transposed");
            // A block size that does not divide n must still be right.
            vector<int> odd(n * n, 0);
            transpose_blocked(src, odd, n, 7);
            check(plain == odd, "a block size that does not divide n is fine");
        }
    """,
    "sys-market": """
        // Fixed point is exact where a double is not.
        {
            Price a = Price::from_double(0.1);
            Price b = Price::from_double(0.2);
            Price sum = a + b;
            check(sum == Price::from_double(0.3),
                  "0.1 + 0.2 is exactly 0.3 in ticks");
            check(0.1 + 0.2 != 0.3, "...which is more than a double manages");
            check(Price::from_double(1.2345).raw() == 12345, "scaling is exact");
            check(Price::from_double(-1.5).raw() == -15000,
                  "and rounds negatives away from zero too");
            Price diff = Price::from_double(1.0) - Price::from_double(0.25);
            check(diff.to_double() == 0.75, "subtraction comes back out right");
            check(Price(1) < Price(2), "prices order by ticks");
        }
        // A level is a total, not a list.
        {
            Level level(Price::from_double(10.0), 100);
            check(level.quantity == 100 && level.orders == 1, "one order in");
            level.add(50);
            check(level.quantity == 150 && level.orders == 2, "two orders in");
            level.remove(150);
            check(level.empty(), "emptied");
            level.remove(999);
            check(level.quantity == 0, "removing past empty does not go negative");
        }
        // The book keeps both sides sorted the right way round.
        {
            OrderBook book;
            book.add_bid(Price::from_double(9.0), 10);
            book.add_bid(Price::from_double(11.0), 20);
            book.add_bid(Price::from_double(10.0), 30);
            book.add_ask(Price::from_double(14.0), 10);
            book.add_ask(Price::from_double(12.0), 20);
            book.add_ask(Price::from_double(13.0), 30);
            Level bid;
            Level ask;
            check(book.best_bid(bid) && bid.price == Price::from_double(11.0),
                  "best bid is the highest");
            check(book.best_ask(ask) && ask.price == Price::from_double(12.0),
                  "best ask is the lowest");
            check(book.bids.size() == 3 && book.asks.size() == 3,
                  "three levels a side");
            bool bids_descend = true;
            for (size_t i = 1; i < book.bids.size(); i++) {
                if (book.bids[i - 1].price < book.bids[i].price) {
                    bids_descend = false;
                }
            }
            check(bids_descend, "bids run high to low");
            bool asks_ascend = true;
            for (size_t i = 1; i < book.asks.size(); i++) {
                if (book.asks[i].price < book.asks[i - 1].price) {
                    asks_ascend = false;
                }
            }
            check(asks_ascend, "asks run low to high");
            check(book.spread_ticks() == 10000, "spread is one whole unit");
            check(!book.crossed(), "and the book is not crossed");
            book.add_bid(Price::from_double(12.0), 5);
            check(book.crossed(), "a bid at the ask crosses it");
            // Same price twice joins the level rather than making a new one.
            OrderBook second;
            second.add_bid(Price::from_double(5.0), 10);
            second.add_bid(Price::from_double(5.0), 10);
            check(second.bids.size() == 1, "same price is one level");
            check(second.bids[0].quantity == 20, "with the quantities added");
            Level none;
            check(!OrderBook().best_bid(none), "an empty book has no best bid");
            check(OrderBook().spread_ticks() == -1, "and no spread");
        }
        // Matching eats the book from the best price outward.
        {
            OrderBook book;
            book.add_ask(Price::from_double(10.0), 50);
            book.add_ask(Price::from_double(11.0), 50);
            book.add_ask(Price::from_double(12.0), 50);
            vector<Fill> fills = match_buy(book, Price::from_double(11.0), 80);
            check(fills.size() == 2, "it took two levels");
            check(fills[0].price == Price::from_double(10.0),
                  "starting at the best price");
            check(fills[0].quantity == 50, "taking all of it");
            check(fills[1].quantity == 30, "and part of the next");
            check(filled_quantity(fills) == 80, "filled exactly what was asked");
            check(book.asks.size() == 2, "the emptied level is gone");
            check(book.asks[0].quantity == 20, "and the partial one is reduced");
            // A limit below the book fills nothing.
            OrderBook untouched;
            untouched.add_ask(Price::from_double(10.0), 50);
            vector<Fill> nothing =
                match_buy(untouched, Price::from_double(9.0), 10);
            check(nothing.empty(), "a limit below the ask fills nothing");
            check(untouched.asks[0].quantity == 50, "and leaves the book alone");
            // Wanting more than the book has takes what there is.
            OrderBook thin;
            thin.add_ask(Price::from_double(10.0), 5);
            vector<Fill> partial =
                match_buy(thin, Price::from_double(99.0), 100);
            check(filled_quantity(partial) == 5, "an empty book stops the fill");
            check(thin.asks.empty(), "and the book is cleared out");
        }
        // VWAP weights by size, and cannot be got by averaging averages.
        {
            Vwap vwap;
            Price out;
            check(!vwap.value(out), "no trades, no VWAP");
            vwap.add(Price::from_double(10.0), 100);
            vwap.add(Price::from_double(20.0), 300);
            check(vwap.value(out), "two trades, a VWAP");
            check(out == Price::from_double(17.5),
                  "weighted toward the bigger trade");
            check(out.to_double() != 15.0,
                  "which is not the plain average of the prices");
            check(vwap.total_volume() == 400, "volume adds up");
        }
        // Rolling window drops the oldest.
        {
            RollingWindow window(3);
            double mean = 0;
            check(!window.mean(mean), "an empty window has no mean");
            window.push(10);
            window.push(20);
            window.push(30);
            check(window.size() == 3 && window.sum() == 60, "three in");
            check(window.mean(mean) && mean == 20.0, "mean of the three");
            check(window.highest() == 30, "and the highest of them");
            window.push(40);
            check(window.size() == 3, "still three");
            check(window.sum() == 90, "the oldest fell out of the sum");
            check(window.mean(mean) && mean == 30.0, "and out of the mean");
            check(window.highest() == 40, "the new value is the highest");
        }
        // Histogram answers percentiles without keeping the samples.
        {
            Histogram hist(10, 100);
            check(hist.percentile(0.5) == -1, "no samples, no percentile");
            for (int i = 0; i < 99; i++) {
                hist.record(50);
            }
            hist.record(950);
            check(hist.samples() == 100, "every sample counted");
            check(hist.percentile(0.5) == 100, "the median is in the low bucket");
            check(hist.percentile(0.999) == 1000,
                  "the tail shows up at the top");
            Histogram narrow(4, 10);
            narrow.record(100000);
            check(narrow.percentile(0.5) == 40,
                  "anything past the last bucket lands in it");
        }
        // Tick parsing, in place.
        {
            const char* line = "AAPL,123.45,500";
            Tick tick = parse_tick(line, 15);
            check(tick.valid, "a well-formed tick parses");
            check(tick.symbol[0] == 'A' && tick.symbol[3] == 'L',
                  "the symbol comes through");
            check(tick.symbol[4] == 0, "and is terminated");
            check(tick.price == Price::from_double(123.45),
                  "the price is exact");
            check(tick.quantity == 500, "and so is the quantity");
            const char* whole = "MSFT,7,10";
            Tick no_fraction = parse_tick(whole, 9);
            check(no_fraction.valid, "a price with no decimal parses");
            check(no_fraction.price == Price::from_double(7.0),
                  "and scales correctly");
            Tick truncated = parse_tick("AAPL,123.45", 11);
            check(!truncated.valid, "a tick missing its quantity is rejected");
            Tick empty = parse_tick("", 0);
            check(!empty.valid, "and so is an empty line");
        }
    """,
}

# Types the checks need. A destructor that counts is the only honest way to
# ask whether a smart pointer actually freed anything.
HELPERS = """
#include <iostream>
#include <chrono>

struct Counted {
    static int alive;
    Counted() { alive++; }
    Counted(const Counted&) { alive++; }
    ~Counted() { alive--; }
};
int Counted::alive = 0;

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

# Tracked derives from RefCounted, which only the memory pattern defines, so
# it cannot live in the helpers every pattern gets.
EXTRA_HELPERS = {
    "sys-memory": """
struct Tracked : RefCounted {
    Tracked() { Counted::alive++; }
    ~Tracked() override { Counted::alive--; }
};
""",
}


@unittest.skipUnless(HAS_CPP, "needs g++, clang++, or an MSVC install")
class SystemsSolutionTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.extend(p.code for p in pattern.problems)
        # After the solutions: Tracked derives from RefCounted, which the
        # bank defines, so the helpers cannot come first.
        parts.append(HELPERS)
        if pattern_id in EXTRA_HELPERS:
            parts.append(EXTRA_HELPERS[pattern_id])
        parts.append("int main() {\n" + CHECKS[pattern_id] + REPORT + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="cpp")
        self.assertEqual(code, 0, (err or out)[:3000])
        self.assertEqual(out.strip(), "ok", out[:3000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class ShapeTests(unittest.TestCase):
    """These run with or without a compiler."""

    def test_every_pattern_has_checks(self) -> None:
        """A pattern with no assertions compiles and proves nothing."""
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_every_pattern_is_a_full_class(self) -> None:
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertEqual(len(pattern.problems), 8)
                self.assertTrue(pattern.blurb)
                self.assertTrue(pattern.tell)

    def test_ids_are_namespaced(self) -> None:
        """So is_systems_class can tell them from a LeetCode class."""
        from code_coach.systems import SYSTEMS_PREFIX, is_systems_class

        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertTrue(pattern.id.startswith(SYSTEMS_PREFIX))
                self.assertTrue(is_systems_class(pattern.id))

    def test_they_do_not_collide_with_the_leetcode_classes(self) -> None:
        from code_coach.leetcode.bank import LEETCODE_CLASS_IDS

        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertNotIn(pattern.id, LEETCODE_CLASS_IDS)

    def test_numbers_cannot_collide_with_a_leetcode_problem(self) -> None:
        """The study panel and the worked lessons are keyed by number alone.

        A systems problem numbered 1 would pull Two Sum's brief and show it
        beside a UniquePtr exercise — the same "wrong content next to the
        problem" failure the draft stamping was written to stop.
        """
        from code_coach.leetcode.problems import all_problems
        from code_coach.leetcode.study import BRIEFS
        from code_coach.leetcode.worked import WORKED
        from code_coach.systems.problems_cpp import FIRST_NUMBER

        taken = {p.number for p in all_problems()} | set(BRIEFS) | set(WORKED)
        for pattern in PATTERNS:
            for problem in pattern.problems:
                with self.subTest(problem=problem.number):
                    self.assertGreater(problem.number, FIRST_NUMBER)
                    self.assertNotIn(problem.number, taken)

    def test_the_curriculum_offers_them_only_where_they_exist(self) -> None:
        from code_coach.curriculum.catalog import classes_for_language

        ours = {p.id for p in PATTERNS}
        offered = {c.id for c in classes_for_language("cpp")}
        self.assertTrue(ours <= offered, "C++ should be offered all of them")
        for language in ("python", "c", "rust", "javascript", "sql"):
            with self.subTest(language=language):
                theirs = {c.id for c in classes_for_language(language)}
                self.assertFalse(ours & theirs)

    def test_no_language_gets_them_by_accident(self) -> None:
        """Unlike the LeetCode bank this must NOT fall back — there is no
        sensible Python answer to 'write a lock-free queue'."""
        from code_coach.systems import has_systems

        self.assertTrue(has_systems("cpp"))
        for language in ("python", "javascript", "typescript", "dart", "sql"):
            with self.subTest(language=language):
                self.assertFalse(has_systems(language))


if __name__ == "__main__":
    unittest.main()
