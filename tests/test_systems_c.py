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
        parts.append("int main(void) {\n" + CHECKS[pattern_id] + REPORT + "\n}")
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
