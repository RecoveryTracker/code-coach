"""Every C systems implementation is compiled and run.

C gives you nothing back for free: a leak is silent, a double free is silent
until it is not, and an unlocked increment is only sometimes wrong. So these
are executed, under threads where threads are the point, and the memory ones
are checked by counting what was actually released.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import msvc_available, run_code
from code_coach.systems.problems_c import PATTERNS

PATTERNS_BY_ID = {p.id: p for p in PATTERNS}

HAS_C = any(shutil.which(c) for c in ("gcc", "clang")) or msvc_available()

CHECKS = {
    "sys-memory": """
        /* An owned buffer, created and destroyed once. */
        {
            Buffer *buffer = buffer_new(4);
            check(buffer != NULL, "buffer_new returns something");
            check(buffer->length == 4, "with the length asked for");
            check(buffer->data[0] == 0, "and zeroed data");
            buffer->data[2] = 7;
            check(buffer->data[2] == 7, "which can be written");
            buffer_free(buffer);
            buffer_free(NULL);
            check(true, "freeing NULL is allowed");
        }
        /* Refcount: the last release frees, the others do not. */
        {
            Shared *shared = shared_new(42);
            check(shared->refs == 1, "one holder");
            Shared *second = shared_retain(shared);
            check(shared->refs == 2, "retain adds one");
            check(second == shared, "and hands back the same object");
            check(!shared_release(shared), "the first release does not free");
            check(shared->refs == 1, "leaving one holder");
            check(shared_release(shared), "and the last one does");
        }
        /* Arena: bump, then reset the lot. */
        {
            Arena *arena = arena_new(128);
            void *first = arena_alloc(arena, 8, 8);
            void *second = arena_alloc(arena, 8, 8);
            check(first && second, "arena hands out memory");
            check(first != second, "and not the same slot twice");
            check(arena_alloc(arena, 1000, 1) == NULL, "and refuses when full");
            check(arena->used >= 16, "it tracks what it gave away");
            arena_reset(arena);
            check(arena->used == 0, "reset frees everything at once");
            arena_alloc(arena, 1, 1);
            void *aligned = arena_alloc(arena, 8, 8);
            check(((uintptr_t)aligned % 8) == 0, "and honours alignment");
            arena_free(arena);
        }
        /* Free list: a released slot comes back. */
        {
            Pool *pool = pool_new(sizeof(int), 2);
            void *a = pool_alloc(pool);
            void *b = pool_alloc(pool);
            check(a && b && a != b, "two distinct slots");
            check(pool_alloc(pool) == NULL, "and then it is empty");
            pool_release(pool, a);
            void *again = pool_alloc(pool);
            check(again == a, "the released slot is handed back");
            check(pool_alloc(pool) == NULL, "and the pool is empty again");
            pool_free(pool);
        }
        /* Generic vector over void pointers. */
        {
            Vec vec;
            vec_init(&vec, sizeof(int));
            for (int i = 0; i < 10; i++) {
                vec_push(&vec, &i);
            }
            check(vec.count == 10, "ten pushed");
            check(vec.capacity >= 10, "and it grew to fit");
            check(*(int *)vec_at(&vec, 0) == 0, "the first is there");
            check(*(int *)vec_at(&vec, 9) == 9, "and the last");
            vec_free(&vec);
            check(vec.count == 0 && vec.items == NULL, "and freeing clears it");
            /* It really is generic. */
            Vec doubles;
            vec_init(&doubles, sizeof(double));
            double value = 1.5;
            vec_push(&doubles, &value);
            check(*(double *)vec_at(&doubles, 0) == 1.5, "doubles work too");
            vec_free(&doubles);
        }
        /* Flexible array member: one allocation, header and text together. */
        {
            Str *a = str_new("hello");
            Str *b = str_new("hello");
            Str *c = str_new("world");
            check(a->length == 5, "the length is stored");
            check(strcmp(a->text, "hello") == 0, "and the text follows it");
            check(str_equals(a, b), "equal strings compare equal");
            check(!str_equals(a, c), "and different ones do not");
            check((void *)a->text > (void *)a, "the text really is inside");
            free(a);
            free(b);
            free(c);
        }
        /* Cleanup path: all three, or none. */
        {
            Three three;
            check(three_init(&three, 8), "a normal init succeeds");
            check(three.first && three.second && three.third, "all three there");
            three_free(&three);
            check(three.first == NULL && three.third == NULL,
                  "and freeing clears every pointer");
        }
        /* Aligned allocation, and free still knows what to release. */
        {
            for (size_t align = 8; align <= 128; align *= 2) {
                void *block = aligned_new(100, align);
                check(block != NULL, "aligned_new returns something");
                check(((uintptr_t)block % align) == 0, "at the alignment asked");
                memset(block, 0, 100);
                aligned_free(block);
            }
            aligned_free(NULL);
            check(true, "freeing NULL is allowed");
        }
    """,
    "sys-lockfree": """
        /* Atomicity is not ordering: both totals are exact. */
        {
            Counter relaxed;
            counter_init(&relaxed);
            thrd_t workers[4];
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], bump_relaxed_worker, &relaxed);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(counter_get(&relaxed) == 20000,
                  "relaxed increments lose nothing");

            Counter ordered;
            counter_init(&ordered);
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], bump_ordered_worker, &ordered);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(counter_get(&ordered) == 20000,
                  "seq_cst increments lose nothing");
        }
        /* The CAS loop settles on the real maximum. */
        {
            atomic_max_init(&shared_max);
            thrd_t workers[4];
            int factors[4] = {1, 2, 3, 4};
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], offer_worker, &factors[i]);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(atomic_max_get(&shared_max) == 4000,
                  "CAS loop finds the true maximum");
        }
        /* SpinLock excludes. Read, yield, write, or the race never shows. */
        {
            spin_init(&shared_spin);
            shared_counter = 0;
            thrd_t workers[4];
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], spin_worker, NULL);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(shared_counter == 800, "SpinLock excludes");
            check(spin_try_lock(&shared_spin), "try_lock takes a free lock");
            check(!spin_try_lock(&shared_spin), "and refuses a held one");
            spin_unlock(&shared_spin);
        }
        /* TicketLock excludes too. */
        {
            ticket_init(&shared_ticket);
            shared_counter = 0;
            thrd_t workers[4];
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], ticket_worker, NULL);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(shared_counter == 800, "TicketLock excludes");
        }
        /* SPSC: everything across, in order, nothing duplicated. */
        {
            spsc_init(&shared_queue);
            thrd_t consumer;
            thrd_create(&consumer, spsc_consumer, NULL);
            for (int i = 0; i < SPSC_TOTAL; i++) {
                while (!spsc_push(&shared_queue, i)) {
                }
            }
            thrd_join(consumer, NULL);
            check(spsc_received == SPSC_TOTAL, "SPSC moved everything");
            check(spsc_ordered, "in order, and duplicating nothing");
            int spare = 0;
            check(!spsc_pop(&shared_queue, &spare), "an empty queue pops none");
        }
        /* Acquire/release publishes the payload with the flag. */
        {
            for (int round = 0; round < 200; round++) {
                mailbox_init(&shared_box);
                mailbox_mismatch = 0;
                thrd_t reader;
                thrd_create(&reader, mailbox_reader, NULL);
                mailbox_publish(&shared_box, 11, 22);
                thrd_join(reader, NULL);
                check(mailbox_mismatch == 0,
                      "the flag published the payload with it");
            }
        }
        /* Once runs exactly once, however many ask. */
        {
            once_init(&shared_once);
            once_ran = 0;
            thrd_t workers[8];
            for (int i = 0; i < 8; i++) {
                thrd_create(&workers[i], once_worker, NULL);
            }
            for (int i = 0; i < 8; i++) {
                thrd_join(workers[i], NULL);
            }
            check(once_ran == 1, "Once ran exactly once");
            once_destroy(&shared_once);
        }
        /* Exactly one releaser is told it was last. */
        {
            refcount_init(&shared_refs);
            check(refcount_get(&shared_refs) == 1, "starts at one");
            for (int i = 0; i < 7; i++) {
                refcount_acquire(&shared_refs);
            }
            check(refcount_get(&shared_refs) == 8, "acquires add up");
            claimed_last = 0;
            thrd_t workers[8];
            for (int i = 0; i < 8; i++) {
                thrd_create(&workers[i], release_worker, NULL);
            }
            for (int i = 0; i < 8; i++) {
                thrd_join(workers[i], NULL);
            }
            check(claimed_last == 1, "exactly one releaser was last");
            check(refcount_get(&shared_refs) == 0, "and the count reached zero");
        }
    """,
    "sys-concurrency": """
        /* Mutex and condition variable: the waiter really waits. */
        {
            latch_init(&shared_latch);
            latch_reached = 0;
            thrd_t waiter;
            thrd_create(&waiter, latch_waiter, NULL);
            thrd_sleep(&(struct timespec){.tv_nsec = 20000000}, NULL);
            check(latch_reached == 0, "the waiter is still waiting");
            latch_set(&shared_latch, 7);
            thrd_join(waiter, NULL);
            check(latch_reached == 1, "and proceeds once the value arrives");
            latch_destroy(&shared_latch);
        }
        /* Semaphore counts permits. */
        {
            sem_init_with(&shared_sem, 2);
            check(sem_available(&shared_sem) == 2, "starts with its permits");
            sem_acquire(&shared_sem);
            sem_acquire(&shared_sem);
            check(sem_available(&shared_sem) == 0, "permits run out");
            sem_got = 0;
            thrd_t waiter;
            thrd_create(&waiter, sem_waiter, NULL);
            thrd_sleep(&(struct timespec){.tv_nsec = 20000000}, NULL);
            check(sem_got == 0, "a waiter blocks when there are none");
            sem_release(&shared_sem);
            thrd_join(waiter, NULL);
            check(sem_got == 1, "and proceeds once one is released");
            sem_destroy(&shared_sem);
        }
        /* RwLock: readers share, writers exclude. */
        {
            rw_init(&shared_rw);
            rw_peak = 0;
            thrd_t readers[4];
            for (int i = 0; i < 4; i++) {
                thrd_create(&readers[i], rw_reader, NULL);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(readers[i], NULL);
            }
            check(rw_peak > 1, "readers really do share");
            check(rw_readers_now(&shared_rw) == 0, "and all left again");
            shared_counter = 0;
            thrd_t writers[4];
            for (int i = 0; i < 4; i++) {
                thrd_create(&writers[i], rw_writer, NULL);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(writers[i], NULL);
            }
            check(shared_counter == 400, "writers exclude each other");
        }
        /* Barrier: nobody passes early. */
        {
            barrier_init(&shared_barrier, 3);
            barrier_arrived = 0;
            barrier_early = 0;
            thrd_t workers[3];
            for (int i = 0; i < 3; i++) {
                thrd_create(&workers[i], barrier_worker, NULL);
            }
            for (int i = 0; i < 3; i++) {
                thrd_join(workers[i], NULL);
            }
            check(barrier_early == 0, "nobody passed the barrier early");
            barrier_destroy(&shared_barrier);
        }
        /* Blocking queue moves everything across, in order. */
        {
            queue_init(&shared_queue);
            queue_received = 0;
            queue_ordered = true;
            thrd_t consumer;
            thrd_create(&consumer, queue_consumer, NULL);
            for (int i = 0; i < 500; i++) {
                queue_push(&shared_queue, i);
            }
            thrd_join(consumer, NULL);
            check(queue_received == 500, "everything came across");
            check(queue_ordered, "and in the order it was sent");
            queue_destroy(&shared_queue);
        }
        /* Per-worker slots need no lock at all. */
        {
            accumulator_init(&shared_acc, 4);
            thrd_t workers[4];
            int ids[4] = {0, 1, 2, 3};
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], accumulate_worker, &ids[i]);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(accumulator_total(&shared_acc) == 4000,
                  "every worker's slot counted, with no lock");
        }
        /* Lock ordering: transfers both ways round never deadlock. */
        {
            account_init(&account_a, 0, 1000);
            account_init(&account_b, 1, 1000);
            thrd_t workers[4];
            int rounds[4] = {0, 1, 2, 3};
            for (int i = 0; i < 4; i++) {
                thrd_create(&workers[i], transfer_worker, &rounds[i]);
            }
            for (int i = 0; i < 4; i++) {
                thrd_join(workers[i], NULL);
            }
            check(account_a.balance + account_b.balance == 2000,
                  "money is conserved");
            check(!account_transfer(&account_a, &account_b, 100000),
                  "and an overdraft is refused");
            account_destroy(&account_a);
            account_destroy(&account_b);
        }
        /* The pool runs every job before it stops. */
        {
            pool_done = 0;
            pool_start(&shared_pool, 3);
            for (int i = 0; i < 50; i++) {
                pool_submit(&shared_pool, pool_job, NULL);
            }
            pool_stop(&shared_pool);
            check(pool_done == 50, "the pool finished its queue before stopping");
        }
    """,
    "sys-cache": """
        /* Cache line arithmetic. */
        {
            check(CACHE_LINE == 64, "the number worth knowing");
            _Alignas(CACHE_LINE) char block[128];
            check(same_cache_line(&block[0], &block[63]),
                  "bytes inside one line share it");
            check(!same_cache_line(&block[0], &block[64]),
                  "and the next starts a new one");
            check(lines_spanned(1) == 1, "one byte is one line");
            check(lines_spanned(64) == 1, "so is exactly a line");
            check(lines_spanned(65) == 2, "one more is two");
            check(lines_spanned(0) == 0, "nothing spans nothing");
        }
        /* False sharing: same answer either way, different layout. */
        {
            shared_pair_init(&shared_unpadded);
            thrd_t workers[2];
            int which[2] = {0, 1};
            for (int i = 0; i < 2; i++) {
                thrd_create(&workers[i], hammer_shared, &which[i]);
            }
            for (int i = 0; i < 2; i++) {
                thrd_join(workers[i], NULL);
            }
            long long a_total = atomic_load_explicit(&shared_unpadded.a,
                                                      memory_order_relaxed);
            long long b_total = atomic_load_explicit(&shared_unpadded.b,
                                                      memory_order_relaxed);
            check(a_total == 20000 && b_total == 20000,
                  "the shared pair still counts correctly");
            /* The layout is the point, and it needs no timing. */
            check(sizeof(SharedPair) <= CACHE_LINE,
                  "an unpadded pair is small enough to share a line");
            check(sizeof(PaddedPair) >= 2 * CACHE_LINE,
                  "padding really does cost the bytes");
            check(_Alignof(PaddedPair) == CACHE_LINE,
                  "and puts each on its own line");
        }
        /* Row vs column: identical answers, different walks. */
        {
            size_t rows = 64;
            size_t cols = 64;
            static int grid[64 * 64];
            for (size_t i = 0; i < rows * cols; i++) {
                grid[i] = (int)(i % 7);
            }
            long long by_row = sum_by_rows(grid, rows, cols);
            long long by_col = sum_by_columns(grid, rows, cols);
            check(by_row == by_col, "both walks reach the same total");
            check(by_row > 0, "and it is a real total");
        }
        /* Struct packing: field order changes the size. */
        {
            check(sizeof(Tight) < sizeof(Loose),
                  "ordering fields large to small is smaller");
            check(wasted_bytes() > 0, "the loose one really does waste bytes");
            check(per_cache_line(sizeof(Tight)) >= per_cache_line(sizeof(Loose)),
                  "so more of them fit in a line");
            check(per_cache_line(0) == 0, "and nothing divides by zero");
        }
        /* AoS vs SoA: same total. */
        {
            static Particle aos[100];
            static double xs[100], ys[100], zs[100], masses[100];
            for (int i = 0; i < 100; i++) {
                aos[i].x = i;
                aos[i].y = 0;
                aos[i].z = 0;
                aos[i].mass = 2.0;
                xs[i] = i;
                ys[i] = 0;
                zs[i] = 0;
                masses[i] = 2.0;
            }
            Particles soa = {xs, ys, zs, masses, 100};
            check(total_mass_aos(aos, 100) == 200.0, "array of structs sums");
            check(total_mass_soa(&soa) == 200.0, "struct of arrays agrees");
            check(sizeof(Particle) == 4 * sizeof(double),
                  "a particle is its four doubles");
        }
        /* Pointer chasing vs contiguous: same sum. */
        {
            static int items[500];
            static Link nodes[500];
            for (int i = 0; i < 500; i++) {
                items[i] = i;
                nodes[i].value = i;
                nodes[i].next = (i + 1 < 500) ? &nodes[i + 1] : NULL;
            }
            check(walk_links(&nodes[0]) == walk_array(items, 500),
                  "both walks reach the same total");
            check(walk_links(NULL) == 0, "an empty list sums to nothing");
        }
        /* Branchless agrees with branchy. */
        {
            static int items[1000];
            for (int i = 0; i < 1000; i++) {
                items[i] = (i * 37) % 256;
            }
            long long branchy = sum_over(items, 1000, 128);
            check(branchy == sum_over_branchless(items, 1000, 128),
                  "branchless agrees with branchy");
            check(branchy > 0, "and there was something to add");
        }
        /* Blocked transpose: same result as the plain one. */
        {
            size_t n = 64;
            static int src[64 * 64];
            static int plain[64 * 64];
            static int blocked[64 * 64];
            static int odd[64 * 64];
            for (size_t i = 0; i < n * n; i++) {
                src[i] = (int)i;
            }
            transpose_naive(src, plain, n);
            transpose_blocked(src, blocked, n, 8);
            check(memcmp(plain, blocked, sizeof(plain)) == 0,
                  "blocking does not change the answer");
            check(plain[n] == 1, "and the transpose is actually transposed");
            transpose_blocked(src, odd, n, 7);
            check(memcmp(plain, odd, sizeof(plain)) == 0,
                  "a block size that does not divide n is fine");
        }
    """,
    "sys-market": """
        /* Fixed point is exact where a double is not. */
        {
            Price a = price_from_double(0.1);
            Price b = price_from_double(0.2);
            check(price_equal(price_add(a, b), price_from_double(0.3)),
                  "0.1 + 0.2 is exactly 0.3 in ticks");
            check(0.1 + 0.2 != 0.3, "...which is more than a double manages");
            check(price_from_double(1.2345).ticks == 12345, "scaling is exact");
            check(price_from_double(-1.5).ticks == -15000, "negatives round away");
            Price diff = price_sub(price_from_double(1.0),
                                   price_from_double(0.25));
            check(price_to_double(diff) == 0.75, "subtraction comes back right");
        }
        /* A level is a total, not a list. */
        {
            Level level = level_new(price_from_double(10.0), 100);
            check(level.quantity == 100 && level.orders == 1, "one order in");
            level_add(&level, 50);
            check(level.quantity == 150 && level.orders == 2, "two orders in");
            level_remove(&level, 150);
            check(level_empty(&level), "emptied");
            level_remove(&level, 999);
            check(level.quantity == 0, "and does not go negative");
        }
        /* The book keeps both sides sorted the right way round. */
        {
            OrderBook book;
            book_init(&book);
            book_add_bid(&book, price_from_double(9.0), 10);
            book_add_bid(&book, price_from_double(11.0), 20);
            book_add_bid(&book, price_from_double(10.0), 30);
            book_add_ask(&book, price_from_double(14.0), 10);
            book_add_ask(&book, price_from_double(12.0), 20);
            book_add_ask(&book, price_from_double(13.0), 30);
            check(price_equal(book.bids[0].price, price_from_double(11.0)),
                  "best bid is the highest");
            check(price_equal(book.asks[0].price, price_from_double(12.0)),
                  "best ask is the lowest");
            check(book.bid_count == 3 && book.ask_count == 3,
                  "three levels a side");
            bool descending = true;
            for (size_t i = 1; i < book.bid_count; i++) {
                if (book.bids[i - 1].price.ticks < book.bids[i].price.ticks) {
                    descending = false;
                }
            }
            check(descending, "bids run high to low");
            bool ascending = true;
            for (size_t i = 1; i < book.ask_count; i++) {
                if (book.asks[i].price.ticks < book.asks[i - 1].price.ticks) {
                    ascending = false;
                }
            }
            check(ascending, "asks run low to high");
            check(book_spread_ticks(&book) == 10000, "one whole unit of spread");
            check(!book_crossed(&book), "and it is not crossed");
            book_add_bid(&book, price_from_double(12.0), 5);
            check(book_crossed(&book), "a bid at the ask crosses it");

            OrderBook same;
            book_init(&same);
            book_add_bid(&same, price_from_double(5.0), 10);
            book_add_bid(&same, price_from_double(5.0), 10);
            check(same.bid_count == 1, "same price is one level");
            check(same.bids[0].quantity == 20, "with the quantities added");

            OrderBook empty;
            book_init(&empty);
            check(book_spread_ticks(&empty) == -1, "an empty book has no spread");
        }
        /* Matching eats the book outward from the best price. */
        {
            OrderBook book;
            book_init(&book);
            book_add_ask(&book, price_from_double(10.0), 50);
            book_add_ask(&book, price_from_double(11.0), 50);
            book_add_ask(&book, price_from_double(12.0), 50);
            Fill fills[8];
            size_t made = match_buy(&book, price_from_double(11.0), 80, fills, 8);
            check(made == 2, "it took two levels");
            check(price_equal(fills[0].price, price_from_double(10.0)),
                  "starting at the best price");
            check(fills[0].quantity == 50, "taking all of it");
            check(fills[1].quantity == 30, "and part of the next");
            check(filled_quantity(fills, made) == 80, "filled what was asked");
            check(book.ask_count == 2, "the emptied level is gone");
            check(book.asks[0].quantity == 20, "the partial one is reduced");

            OrderBook untouched;
            book_init(&untouched);
            book_add_ask(&untouched, price_from_double(10.0), 50);
            size_t none = match_buy(&untouched, price_from_double(9.0), 10,
                                    fills, 8);
            check(none == 0, "a limit below the ask fills nothing");
            check(untouched.asks[0].quantity == 50, "and leaves the book alone");

            OrderBook thin;
            book_init(&thin);
            book_add_ask(&thin, price_from_double(10.0), 5);
            size_t partial = match_buy(&thin, price_from_double(99.0), 100,
                                       fills, 8);
            check(filled_quantity(fills, partial) == 5,
                  "an empty book stops the fill");
            check(thin.ask_count == 0, "and the book is cleared");
        }
        /* VWAP weights by size. */
        {
            Vwap vwap;
            vwap_init(&vwap);
            Price out;
            check(!vwap_value(&vwap, &out), "no trades, no VWAP");
            vwap_add(&vwap, price_from_double(10.0), 100);
            vwap_add(&vwap, price_from_double(20.0), 300);
            check(vwap_value(&vwap, &out), "two trades, a VWAP");
            check(price_equal(out, price_from_double(17.5)),
                  "weighted toward the bigger trade");
            check(price_to_double(out) != 15.0, "not the plain average");
        }
        /* Rolling window drops the oldest. */
        {
            RollingWindow window;
            window_init(&window, 3);
            double mean = 0;
            check(!window_mean(&window, &mean), "an empty window has no mean");
            window_push(&window, 10);
            window_push(&window, 20);
            window_push(&window, 30);
            check(window.filled == 3 && window.running == 60, "three in");
            check(window_mean(&window, &mean) && mean == 20.0, "mean of three");
            check(window_highest(&window) == 30, "and the highest");
            window_push(&window, 40);
            check(window.filled == 3 && window.running == 90,
                  "the oldest fell out");
            check(window_mean(&window, &mean) && mean == 30.0, "and out of mean");
            check(window_highest(&window) == 40, "the new value is highest");
        }
        /* Histogram answers percentiles without keeping samples. */
        {
            Histogram hist;
            hist_init(&hist, 10, 100);
            check(hist_percentile(&hist, 0.5) == -1, "no samples, no percentile");
            for (int i = 0; i < 99; i++) {
                hist_record(&hist, 50);
            }
            hist_record(&hist, 950);
            check(hist.total == 100, "every sample counted");
            check(hist_percentile(&hist, 0.5) == 100, "the median is low");
            check(hist_percentile(&hist, 0.999) == 1000, "the tail shows up");
            Histogram narrow;
            hist_init(&narrow, 4, 10);
            hist_record(&narrow, 100000);
            check(hist_percentile(&narrow, 0.5) == 40,
                  "past the last bucket lands in it");
        }
        /* Tick parsing, in place. */
        {
            Tick tick = parse_tick("AAPL,123.45,500", 15);
            check(tick.valid, "a well-formed tick parses");
            check(strcmp(tick.symbol, "AAPL") == 0, "the symbol comes through");
            check(price_equal(tick.price, price_from_double(123.45)),
                  "the price is exact");
            check(tick.quantity == 500, "and so is the quantity");
            Tick whole = parse_tick("MSFT,7,10", 9);
            check(whole.valid && price_equal(whole.price, price_from_double(7.0)),
                  "no decimal still scales");
            check(!parse_tick("AAPL,123.45", 11).valid, "a truncated tick fails");
            check(!parse_tick("", 0).valid, "and so does an empty line");
        }
    """,
}

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

# C has no lambdas, so every thread body is a named function with its state
# in a file-scope variable. That is what the language gives you.
EXTRA_HELPERS = {
    "sys-concurrency": """
static Latch shared_latch;
static Semaphore shared_sem;
static RwLock shared_rw;
static Barrier shared_barrier;
static BlockingQueue shared_queue;
static Accumulator shared_acc;
static Account account_a;
static Account account_b;
static ThreadPool shared_pool;

static int latch_reached = 0;
static int sem_got = 0;
static int rw_peak = 0;
static long long shared_counter = 0;
static int barrier_arrived = 0;
static int barrier_early = 0;
static int queue_received = 0;
static bool queue_ordered = true;
static int pool_done = 0;
static mtx_t report_guard;

static int latch_waiter(void *arg) {
    (void)arg;
    latch_wait_for(&shared_latch, 7);
    latch_reached = 1;
    return 0;
}

static int sem_waiter(void *arg) {
    (void)arg;
    sem_acquire(&shared_sem);
    sem_got = 1;
    sem_release(&shared_sem);
    return 0;
}

static int rw_reader(void *arg) {
    (void)arg;
    rw_read_lock(&shared_rw);
    int now = rw_readers_now(&shared_rw);
    mtx_lock(&report_guard);
    if (now > rw_peak) {
        rw_peak = now;
    }
    mtx_unlock(&report_guard);
    thrd_sleep(&(struct timespec){.tv_nsec = 10000000}, NULL);
    rw_read_unlock(&shared_rw);
    return 0;
}

static int rw_writer(void *arg) {
    (void)arg;
    for (int i = 0; i < 100; i++) {
        rw_write_lock(&shared_rw);
        long long seen = shared_counter;
        thrd_yield();
        shared_counter = seen + 1;
        rw_write_unlock(&shared_rw);
    }
    return 0;
}

static int barrier_worker(void *arg) {
    (void)arg;
    mtx_lock(&report_guard);
    barrier_arrived++;
    mtx_unlock(&report_guard);
    barrier_wait(&shared_barrier);
    mtx_lock(&report_guard);
    if (barrier_arrived != 3) {
        barrier_early++;
    }
    mtx_unlock(&report_guard);
    return 0;
}

static int queue_consumer(void *arg) {
    (void)arg;
    for (int i = 0; i < 500; i++) {
        int value = queue_pop(&shared_queue);
        if (value != i) {
            queue_ordered = false;
        }
        queue_received++;
    }
    return 0;
}

static int accumulate_worker(void *arg) {
    int id = *(int *)arg;
    for (int i = 0; i < 1000; i++) {
        accumulator_add(&shared_acc, id, 1);
    }
    return 0;
}

static int transfer_worker(void *arg) {
    int round = *(int *)arg;
    for (int i = 0; i < 200; i++) {
        if (round % 2 == 0) {
            account_transfer(&account_a, &account_b, 1);
        } else {
            account_transfer(&account_b, &account_a, 1);
        }
    }
    return 0;
}

static void pool_job(void *context) {
    (void)context;
    mtx_lock(&report_guard);
    pool_done++;
    mtx_unlock(&report_guard);
}
""",
    "sys-cache": """
static SharedPair shared_unpadded;

static int hammer_shared(void *arg) {
    int which = *(int *)arg;
    for (int i = 0; i < 20000; i++) {
        if (which == 0) {
            atomic_fetch_add_explicit(&shared_unpadded.a, 1,
                                      memory_order_relaxed);
        } else {
            atomic_fetch_add_explicit(&shared_unpadded.b, 1,
                                      memory_order_relaxed);
        }
    }
    return 0;
}
""",
    "sys-lockfree": """
static AtomicMax shared_max;
static SpinLock shared_spin;
static TicketLock shared_ticket;
static SpscQueue shared_queue;
static Mailbox shared_box;
static Once shared_once;
static AtomicRefCount shared_refs;
static long long shared_counter = 0;
static int mailbox_mismatch = 0;
static int once_ran = 0;
static int claimed_last = 0;

#define SPSC_TOTAL 20000
static int spsc_received = 0;
static bool spsc_ordered = true;

static int bump_relaxed_worker(void *arg) {
    Counter *counter = arg;
    for (int i = 0; i < 5000; i++) {
        counter_bump_relaxed(counter);
    }
    return 0;
}

static int bump_ordered_worker(void *arg) {
    Counter *counter = arg;
    for (int i = 0; i < 5000; i++) {
        counter_bump_ordered(counter);
    }
    return 0;
}

static int offer_worker(void *arg) {
    int factor = *(int *)arg;
    for (int n = 1; n <= 1000; n++) {
        atomic_max_offer(&shared_max, (long long)n * factor);
    }
    return 0;
}

static int spin_worker(void *arg) {
    (void)arg;
    for (int i = 0; i < 200; i++) {
        spin_lock(&shared_spin);
        long long seen = shared_counter;
        thrd_yield();
        shared_counter = seen + 1;
        spin_unlock(&shared_spin);
    }
    return 0;
}

static int ticket_worker(void *arg) {
    (void)arg;
    for (int i = 0; i < 200; i++) {
        ticket_lock(&shared_ticket);
        long long seen = shared_counter;
        thrd_yield();
        shared_counter = seen + 1;
        ticket_unlock(&shared_ticket);
    }
    return 0;
}

static int spsc_consumer(void *arg) {
    (void)arg;
    spsc_received = 0;
    spsc_ordered = true;
    int value = 0;
    while (spsc_received < SPSC_TOTAL) {
        if (spsc_pop(&shared_queue, &value)) {
            if (value != spsc_received) {
                spsc_ordered = false;
            }
            spsc_received++;
        }
    }
    return 0;
}

static int mailbox_reader(void *arg) {
    (void)arg;
    int a = 0;
    int b = 0;
    while (!mailbox_collect(&shared_box, &a, &b)) {
    }
    if (a != 11 || b != 22) {
        mailbox_mismatch++;
    }
    return 0;
}

static void once_action(void *context) {
    (void)context;
    once_ran++;
}

static int once_worker(void *arg) {
    (void)arg;
    once_call(&shared_once, once_action, NULL);
    return 0;
}

static int release_worker(void *arg) {
    (void)arg;
    if (refcount_release(&shared_refs)) {
        claimed_last++;
    }
    return 0;
}
""",
}

REPORT = """
    if (failures) {
        return 1;
    }
    printf("ok\\n");
    return 0;
"""


@unittest.skipUnless(HAS_C, "needs gcc, clang, or an MSVC install")
class CSystemsTests(unittest.TestCase):
    def _run_pattern(self, pattern_id: str) -> None:
        pattern = PATTERNS_BY_ID[pattern_id]
        parts = list(pattern.preamble)
        parts.append("#include <stdint.h>")
        parts.append(HARNESS)
        parts.extend(p.code for p in pattern.problems)
        if pattern_id in EXTRA_HELPERS:
            parts.append(EXTRA_HELPERS[pattern_id])
        opener = "int main(void) {\n"
        if pattern_id == "sys-concurrency":
            # The checks report from several threads, so the reporting mutex
            # has to exist before any of them run.
            opener += "    mtx_init(&report_guard, mtx_plain);\n"
        parts.append(opener + CHECKS[pattern_id] + REPORT + "\n}")
        out, err, code = run_code("\n\n".join(parts), language="c")
        self.assertEqual(code, 0, (err or out)[:3000])
        self.assertEqual(out.strip(), "ok", out[:3000])

    def test_every_pattern_compiles_and_holds(self) -> None:
        for pattern_id in CHECKS:
            with self.subTest(pattern=pattern_id):
                self._run_pattern(pattern_id)


class ShapeTests(unittest.TestCase):
    def test_every_pattern_has_checks(self) -> None:
        self.assertEqual(sorted(CHECKS), sorted(p.id for p in PATTERNS))

    def test_every_pattern_is_a_full_class(self) -> None:
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern.id):
                self.assertEqual(len(pattern.problems), 8)

    def test_the_curriculum_offers_exactly_these(self) -> None:
        from code_coach.curriculum.catalog import classes_for_language

        offered = {
            c.id for c in classes_for_language("c") if c.id.startswith("sys-")
        }
        self.assertEqual(offered, {p.id for p in PATTERNS})


if __name__ == "__main__":
    unittest.main()
