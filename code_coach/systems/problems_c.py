"""
Systems and low-level implementations, in C.

C is where none of this is given to you. There is no destructor, so a guard
is a discipline rather than a type; no templates, so a generic container is a
size and a void pointer; no RAII, so every allocation has an owner you have
to name out loud.

That is the lesson. The C++ versions show what the language does for you and
the Rust ones show what the borrow checker was doing — these show the bill
when nobody is doing either.

C11 atomics and C11 threads, so it is standard C rather than POSIX or Win32.
"""

from __future__ import annotations

from code_coach.leetcode.c_common import _p
from code_coach.leetcode.problems import Pattern

STDLIB = "#include <stdlib.h>"
STRING_H = "#include <string.h>"
STDBOOL = "#include <stdbool.h>"
STDINT = "#include <stdint.h>"
STDDEF = "#include <stddef.h>"
ATOMIC = "#include <stdatomic.h>"
THREADS = "#include <threads.h>"


# ── 1. Ownership by hand ────────────────────────────────────

_MEMORY = Pattern(
    id="sys-memory",
    name="Ownership & RAII",
    order=101,
    blurb="No destructor, no template, no borrow checker. Every allocation has an owner you name yourself.",
    tell="Anything about who frees this, and when.",
    preamble=(STDLIB, STRING_H, STDBOOL, STDDEF),
    problems=(
        _p(
            9101, "Owned Buffer", "Medium",
            "The C answer to a smart pointer is a convention: one create, one "
            "destroy, and a comment saying who calls it. Nothing enforces it.",
            "O(1) create and destroy",
            """
            typedef struct {
                int *data;
                size_t length;
            } Buffer;

            /* Caller owns the result and must pass it to buffer_free. */
            static Buffer *buffer_new(size_t length) {
                Buffer *buffer = malloc(sizeof(Buffer));
                if (!buffer) {
                    return NULL;
                }
                buffer->data = calloc(length, sizeof(int));
                if (!buffer->data) {
                    free(buffer);
                    return NULL;
                }
                buffer->length = length;
                return buffer;
            }

            static void buffer_free(Buffer *buffer) {
                if (!buffer) {
                    return;
                }
                free(buffer->data);
                free(buffer);
            }
            """,
        ),
        _p(
            9102, "Reference Count", "Medium",
            "Sharing without a garbage collector: count the holders, and free "
            "when the count reaches zero. Getting a retain wrong leaks; "
            "getting a release wrong is a use-after-free.",
            "O(1) retain and release",
            """
            typedef struct {
                int refs;
                int value;
            } Shared;

            static Shared *shared_new(int value) {
                Shared *shared = malloc(sizeof(Shared));
                shared->refs = 1;
                shared->value = value;
                return shared;
            }

            static Shared *shared_retain(Shared *shared) {
                shared->refs++;
                return shared;
            }

            static bool shared_release(Shared *shared) {
                if (--shared->refs > 0) {
                    return false;
                }
                free(shared);
                return true;
            }
            """,
        ),
        _p(
            9103, "Arena Allocator", "Medium",
            "Bump a pointer to allocate and free the lot at once. No "
            "per-object bookkeeping, which is exactly why it is fast and why "
            "you cannot free one thing out of it.",
            "O(1) allocate, O(1) reset",
            """
            typedef struct {
                unsigned char *base;
                size_t size;
                size_t used;
            } Arena;

            static Arena *arena_new(size_t bytes) {
                Arena *arena = malloc(sizeof(Arena));
                arena->base = malloc(bytes);
                arena->size = bytes;
                arena->used = 0;
                return arena;
            }

            static void *arena_alloc(Arena *arena, size_t bytes, size_t align) {
                size_t at = (arena->used + align - 1) & ~(align - 1);
                if (at + bytes > arena->size) {
                    return NULL;
                }
                arena->used = at + bytes;
                return arena->base + at;
            }

            static void arena_reset(Arena *arena) { arena->used = 0; }

            static void arena_free(Arena *arena) {
                free(arena->base);
                free(arena);
            }
            """,
        ),
        _p(
            9104, "Free List", "Hard",
            "Reuse the freed slots by threading a list through them. The "
            "next-pointer lives in the dead object's own memory, which costs "
            "nothing extra.",
            "O(1) allocate and free",
            """
            typedef struct FreeNode {
                struct FreeNode *next;
            } FreeNode;

            typedef struct {
                unsigned char *base;
                size_t slot_size;
                size_t slots;
                size_t handed_out;
                FreeNode *free_list;
            } Pool;

            static Pool *pool_new(size_t slot_size, size_t slots) {
                if (slot_size < sizeof(FreeNode)) {
                    slot_size = sizeof(FreeNode);
                }
                Pool *pool = malloc(sizeof(Pool));
                pool->base = malloc(slot_size * slots);
                pool->slot_size = slot_size;
                pool->slots = slots;
                pool->handed_out = 0;
                pool->free_list = NULL;
                return pool;
            }

            static void *pool_alloc(Pool *pool) {
                if (pool->free_list) {
                    FreeNode *node = pool->free_list;
                    pool->free_list = node->next;
                    return node;
                }
                if (pool->handed_out == pool->slots) {
                    return NULL;
                }
                return pool->base + pool->slot_size * pool->handed_out++;
            }

            static void pool_release(Pool *pool, void *slot) {
                FreeNode *node = slot;
                node->next = pool->free_list;
                pool->free_list = node;
            }

            static void pool_free(Pool *pool) {
                free(pool->base);
                free(pool);
            }
            """,
        ),
        _p(
            9105, "Generic Vector", "Hard",
            "No templates, so a generic container is an element size and a "
            "void pointer. memcpy does what a copy constructor would.",
            "O(1) amortised push",
            """
            typedef struct {
                unsigned char *items;
                size_t item_size;
                size_t count;
                size_t capacity;
            } Vec;

            static void vec_init(Vec *vec, size_t item_size) {
                vec->items = NULL;
                vec->item_size = item_size;
                vec->count = 0;
                vec->capacity = 0;
            }

            static void vec_push(Vec *vec, const void *item) {
                if (vec->count == vec->capacity) {
                    vec->capacity = vec->capacity ? vec->capacity * 2 : 4;
                    vec->items = realloc(vec->items,
                                         vec->capacity * vec->item_size);
                }
                memcpy(vec->items + vec->count * vec->item_size, item,
                       vec->item_size);
                vec->count++;
            }

            static void *vec_at(Vec *vec, size_t index) {
                return vec->items + index * vec->item_size;
            }

            static void vec_free(Vec *vec) {
                free(vec->items);
                vec->items = NULL;
                vec->count = 0;
                vec->capacity = 0;
            }
            """,
        ),
        _p(
            9106, "Flexible Array Member", "Medium",
            "One allocation for the header and its payload together. The "
            "trailing [] is a real C feature, not a trick, and it saves a "
            "pointer chase.",
            "O(1), one allocation instead of two",
            """
            typedef struct {
                size_t length;
                char text[];
            } Str;

            static Str *str_new(const char *from) {
                size_t length = strlen(from);
                Str *str = malloc(sizeof(Str) + length + 1);
                str->length = length;
                memcpy(str->text, from, length + 1);
                return str;
            }

            static bool str_equals(const Str *a, const Str *b) {
                return a->length == b->length &&
                       memcmp(a->text, b->text, a->length) == 0;
            }
            """,
        ),
        _p(
            9107, "Cleanup Path", "Medium",
            "C has no destructor, so failure partway through has to unwind by "
            "hand. One label per acquired thing, jumped to in reverse.",
            "O(1), and it is where the leaks live",
            """
            typedef struct {
                int *first;
                int *second;
                int *third;
            } Three;

            static bool three_init(Three *three, size_t n) {
                three->first = NULL;
                three->second = NULL;
                three->third = NULL;

                three->first = malloc(n * sizeof(int));
                if (!three->first) {
                    goto fail;
                }
                three->second = malloc(n * sizeof(int));
                if (!three->second) {
                    goto fail_first;
                }
                three->third = malloc(n * sizeof(int));
                if (!three->third) {
                    goto fail_second;
                }
                return true;

            fail_second:
                free(three->second);
                three->second = NULL;
            fail_first:
                free(three->first);
                three->first = NULL;
            fail:
                return false;
            }

            static void three_free(Three *three) {
                free(three->third);
                free(three->second);
                free(three->first);
                three->first = NULL;
                three->second = NULL;
                three->third = NULL;
            }
            """,
        ),
        _p(
            9108, "Aligned Allocation", "Medium",
            "Over-allocate, step up to the alignment, and store the original "
            "pointer just behind so free still knows what to release.",
            "O(1), at the cost of a pointer and the padding",
            """
            static void *aligned_new(size_t bytes, size_t align) {
                if (align < sizeof(void *)) {
                    align = sizeof(void *);
                }
                void *raw = malloc(bytes + align + sizeof(void *));
                if (!raw) {
                    return NULL;
                }
                uintptr_t start = (uintptr_t)raw + sizeof(void *);
                uintptr_t aligned = (start + align - 1) & ~(uintptr_t)(align - 1);
                ((void **)aligned)[-1] = raw;
                return (void *)aligned;
            }

            static void aligned_free(void *pointer) {
                if (pointer) {
                    free(((void **)pointer)[-1]);
                }
            }
            """,
        ),
    ),
)


# ── 3. Lock-free and atomics ────────────────────────────────

_LOCKFREE = Pattern(
    id="sys-lockfree",
    name="Lock-free & Atomics",
    order=103,
    blurb="C11 atomics: the same orderings, spelled out with no type system helping.",
    tell="A hot path where even an uncontended lock is too much.",
    preamble=(STDLIB, STDBOOL, STDDEF, ATOMIC, THREADS),
    problems=(
        _p(
            9301, "Relaxed vs Sequential Counter", "Medium",
            "Both totals are exact — atomicity is not ordering. Relaxed only "
            "gives up the promise about what else you see around it.",
            "O(1) per increment, relaxed is cheaper",
            """
            typedef struct {
                atomic_llong value;
            } Counter;

            static void counter_init(Counter *counter) {
                atomic_init(&counter->value, 0);
            }

            static void counter_bump_relaxed(Counter *counter) {
                atomic_fetch_add_explicit(&counter->value, 1,
                                          memory_order_relaxed);
            }

            static void counter_bump_ordered(Counter *counter) {
                atomic_fetch_add_explicit(&counter->value, 1,
                                          memory_order_seq_cst);
            }

            static long long counter_get(const Counter *counter) {
                return atomic_load_explicit(&counter->value,
                                            memory_order_relaxed);
            }
            """,
        ),
        _p(
            9302, "CAS Loop", "Medium",
            "compare_exchange_weak may fail for no reason, so it lives in a "
            "loop — and it writes the value that beat you back into expected.",
            "O(1) uncontended, retries under contention",
            """
            typedef struct {
                atomic_llong best;
            } AtomicMax;

            static void atomic_max_init(AtomicMax *max) {
                atomic_init(&max->best, 0);
            }

            static void atomic_max_offer(AtomicMax *max, long long candidate) {
                long long seen = atomic_load_explicit(&max->best,
                                                      memory_order_relaxed);
                while (candidate > seen) {
                    if (atomic_compare_exchange_weak_explicit(
                            &max->best, &seen, candidate, memory_order_release,
                            memory_order_relaxed)) {
                        return;
                    }
                    /* seen now holds whatever beat us. */
                }
            }

            static long long atomic_max_get(const AtomicMax *max) {
                return atomic_load_explicit(&max->best, memory_order_acquire);
            }
            """,
        ),
        _p(
            9303, "SpinLock", "Medium",
            "An atomic flag and a loop. Fast when the wait is nanoseconds and "
            "terrible when it is not — it burns a core to wait.",
            "O(1) uncontended",
            """
            typedef struct {
                atomic_flag taken;
            } SpinLock;

            static void spin_init(SpinLock *lock) {
                atomic_flag_clear(&lock->taken);
            }

            static void spin_lock(SpinLock *lock) {
                while (atomic_flag_test_and_set_explicit(
                    &lock->taken, memory_order_acquire)) {
                    /* Nothing here but waiting. */
                }
            }

            static bool spin_try_lock(SpinLock *lock) {
                return !atomic_flag_test_and_set_explicit(&lock->taken,
                                                          memory_order_acquire);
            }

            static void spin_unlock(SpinLock *lock) {
                atomic_flag_clear_explicit(&lock->taken, memory_order_release);
            }
            """,
        ),
        _p(
            9304, "Ticket Lock", "Medium",
            "Take a number and wait for it. Unlike a spinlock this is fair: "
            "threads are served in the order they arrived.",
            "O(1) uncontended, first-come-first-served",
            """
            typedef struct {
                atomic_uint next;
                atomic_uint serving;
            } TicketLock;

            static void ticket_init(TicketLock *lock) {
                atomic_init(&lock->next, 0);
                atomic_init(&lock->serving, 0);
            }

            static void ticket_lock(TicketLock *lock) {
                unsigned mine = atomic_fetch_add_explicit(&lock->next, 1,
                                                          memory_order_relaxed);
                while (atomic_load_explicit(&lock->serving,
                                            memory_order_acquire) != mine) {
                }
            }

            static void ticket_unlock(TicketLock *lock) {
                atomic_fetch_add_explicit(&lock->serving, 1,
                                          memory_order_release);
            }
            """,
        ),
        _p(
            9305, "SPSC Ring Buffer", "Hard",
            "One producer, one consumer, no lock. The release on the write "
            "index pairs with the acquire on the read, and that pairing is the "
            "whole safety argument.",
            "O(1) per item, wait-free both sides",
            """
            #define RING_SIZE 64

            typedef struct {
                int slots[RING_SIZE];
                atomic_size_t write;
                atomic_size_t read;
            } SpscQueue;

            static void spsc_init(SpscQueue *queue) {
                atomic_init(&queue->write, 0);
                atomic_init(&queue->read, 0);
            }

            static bool spsc_push(SpscQueue *queue, int value) {
                size_t head = atomic_load_explicit(&queue->write,
                                                   memory_order_relaxed);
                size_t next = (head + 1) % RING_SIZE;
                if (next == atomic_load_explicit(&queue->read,
                                                 memory_order_acquire)) {
                    return false;
                }
                queue->slots[head] = value;
                atomic_store_explicit(&queue->write, next,
                                      memory_order_release);
                return true;
            }

            static bool spsc_pop(SpscQueue *queue, int *out) {
                size_t tail = atomic_load_explicit(&queue->read,
                                                   memory_order_relaxed);
                if (tail == atomic_load_explicit(&queue->write,
                                                 memory_order_acquire)) {
                    return false;
                }
                *out = queue->slots[tail];
                atomic_store_explicit(&queue->read, (tail + 1) % RING_SIZE,
                                      memory_order_release);
                return true;
            }
            """,
        ),
        _p(
            9306, "Acquire-Release Message Passing", "Medium",
            "The flag publishes the payload. A reader that sees the flag with "
            "acquire must also see everything written before the release.",
            "O(1), no lock",
            """
            typedef struct {
                int first;
                int second;
                atomic_bool ready;
            } Mailbox;

            static void mailbox_init(Mailbox *box) {
                box->first = 0;
                box->second = 0;
                atomic_init(&box->ready, false);
            }

            static void mailbox_publish(Mailbox *box, int a, int b) {
                box->first = a;
                box->second = b;
                atomic_store_explicit(&box->ready, true, memory_order_release);
            }

            static bool mailbox_collect(Mailbox *box, int *a, int *b) {
                if (!atomic_load_explicit(&box->ready, memory_order_acquire)) {
                    return false;
                }
                *a = box->first;
                *b = box->second;
                return true;
            }
            """,
        ),
        _p(
            9307, "Once", "Medium",
            "Exactly one caller runs it, and the rest wait rather than sailing "
            "past a half-built thing. C11 gives you call_once for this.",
            "O(1) after the first call",
            """
            typedef struct {
                atomic_bool done;
                mtx_t guard;
            } Once;

            static void once_init(Once *once) {
                atomic_init(&once->done, false);
                mtx_init(&once->guard, mtx_plain);
            }

            static void once_call(Once *once, void (*action)(void *),
                                  void *context) {
                if (atomic_load_explicit(&once->done, memory_order_acquire)) {
                    return;
                }
                mtx_lock(&once->guard);
                if (!atomic_load_explicit(&once->done, memory_order_relaxed)) {
                    action(context);
                    atomic_store_explicit(&once->done, true,
                                          memory_order_release);
                }
                mtx_unlock(&once->guard);
            }

            static void once_destroy(Once *once) { mtx_destroy(&once->guard); }
            """,
        ),
        _p(
            9308, "Atomic Reference Count", "Hard",
            "The increment can be relaxed; the decrement cannot. Release on "
            "the way down and an acquire fence before cleaning up is what "
            "stops the free racing another thread's last use.",
            "O(1) per retain",
            """
            typedef struct {
                atomic_long refs;
            } AtomicRefCount;

            static void refcount_init(AtomicRefCount *count) {
                atomic_init(&count->refs, 1);
            }

            static void refcount_acquire(AtomicRefCount *count) {
                atomic_fetch_add_explicit(&count->refs, 1, memory_order_relaxed);
            }

            static bool refcount_release(AtomicRefCount *count) {
                if (atomic_fetch_sub_explicit(&count->refs, 1,
                                              memory_order_release) != 1) {
                    return false;
                }
                atomic_thread_fence(memory_order_acquire);
                return true;
            }

            static long refcount_get(const AtomicRefCount *count) {
                return atomic_load_explicit(&count->refs, memory_order_relaxed);
            }
            """,
        ),
    ),
)


PATTERNS: tuple[Pattern, ...] = (
    _MEMORY,
    _LOCKFREE,
)
