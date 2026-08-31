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




# ── 2. Concurrency primitives ───────────────────────────────

_CONCURRENCY = Pattern(
    id="sys-concurrency",
    name="Concurrency Primitives",
    order=102,
    blurb="C11 threads, and every piece of state named at file scope because there are no closures.",
    tell="Threads sharing anything: a counter, a queue, a piece of state.",
    preamble=(STDLIB, STRING_H, STDBOOL, STDDEF, ATOMIC, THREADS),
    problems=(
        _p(
            9201, "Mutex and Condition Variable", "Medium",
            "The pairing C11 gives you. The mutex is released atomically as "
            "you wait, which is what closes the window where a signal could "
            "arrive before you were listening.",
            "O(1) per operation",
            """
            typedef struct {
                mtx_t guard;
                cnd_t ready;
                int value;
            } Latch;

            static void latch_init(Latch *latch) {
                mtx_init(&latch->guard, mtx_plain);
                cnd_init(&latch->ready);
                latch->value = 0;
            }

            static void latch_set(Latch *latch, int value) {
                mtx_lock(&latch->guard);
                latch->value = value;
                mtx_unlock(&latch->guard);
                cnd_broadcast(&latch->ready);
            }

            static void latch_wait_for(Latch *latch, int wanted) {
                mtx_lock(&latch->guard);
                /* A loop, not an if: a wakeup does not promise the predicate. */
                while (latch->value != wanted) {
                    cnd_wait(&latch->ready, &latch->guard);
                }
                mtx_unlock(&latch->guard);
            }

            static void latch_destroy(Latch *latch) {
                cnd_destroy(&latch->ready);
                mtx_destroy(&latch->guard);
            }
            """,
        ),
        _p(
            9202, "Semaphore", "Medium",
            "A count of permits. Waiters sleep rather than spin, which is the "
            "right trade when the wait might be long.",
            "O(1) per acquire",
            """
            typedef struct {
                mtx_t guard;
                cnd_t ready;
                int permits;
            } Semaphore;

            static void sem_init_with(Semaphore *sem, int permits) {
                mtx_init(&sem->guard, mtx_plain);
                cnd_init(&sem->ready);
                sem->permits = permits;
            }

            static void sem_acquire(Semaphore *sem) {
                mtx_lock(&sem->guard);
                while (sem->permits == 0) {
                    cnd_wait(&sem->ready, &sem->guard);
                }
                sem->permits--;
                mtx_unlock(&sem->guard);
            }

            static void sem_release(Semaphore *sem) {
                mtx_lock(&sem->guard);
                sem->permits++;
                mtx_unlock(&sem->guard);
                cnd_signal(&sem->ready);
            }

            static int sem_available(Semaphore *sem) {
                mtx_lock(&sem->guard);
                int now = sem->permits;
                mtx_unlock(&sem->guard);
                return now;
            }

            static void sem_destroy(Semaphore *sem) {
                cnd_destroy(&sem->ready);
                mtx_destroy(&sem->guard);
            }
            """,
        ),
        _p(
            9203, "Reader-Writer Lock", "Hard",
            "Many readers or one writer. Letting waiting writers block new "
            "readers is what stops a steady stream of readers starving them.",
            "O(1) per acquire",
            """
            typedef struct {
                mtx_t guard;
                cnd_t ready;
                int readers;
                int writers;
                int waiting_writers;
            } RwLock;

            static void rw_init(RwLock *lock) {
                mtx_init(&lock->guard, mtx_plain);
                cnd_init(&lock->ready);
                lock->readers = 0;
                lock->writers = 0;
                lock->waiting_writers = 0;
            }

            static void rw_read_lock(RwLock *lock) {
                mtx_lock(&lock->guard);
                while (lock->writers > 0 || lock->waiting_writers > 0) {
                    cnd_wait(&lock->ready, &lock->guard);
                }
                lock->readers++;
                mtx_unlock(&lock->guard);
            }

            static void rw_read_unlock(RwLock *lock) {
                mtx_lock(&lock->guard);
                lock->readers--;
                mtx_unlock(&lock->guard);
                cnd_broadcast(&lock->ready);
            }

            static void rw_write_lock(RwLock *lock) {
                mtx_lock(&lock->guard);
                lock->waiting_writers++;
                while (lock->writers > 0 || lock->readers > 0) {
                    cnd_wait(&lock->ready, &lock->guard);
                }
                lock->waiting_writers--;
                lock->writers++;
                mtx_unlock(&lock->guard);
            }

            static void rw_write_unlock(RwLock *lock) {
                mtx_lock(&lock->guard);
                lock->writers--;
                mtx_unlock(&lock->guard);
                cnd_broadcast(&lock->ready);
            }

            static int rw_readers_now(RwLock *lock) {
                mtx_lock(&lock->guard);
                int now = lock->readers;
                mtx_unlock(&lock->guard);
                return now;
            }
            """,
        ),
        _p(
            9204, "Barrier", "Medium",
            "Nobody leaves until everybody arrives. The generation counter is "
            "what stops a fast thread lapping the others and passing twice.",
            "O(1) per arrival",
            """
            typedef struct {
                mtx_t guard;
                cnd_t ready;
                int total;
                int waiting;
                unsigned generation;
            } Barrier;

            static void barrier_init(Barrier *barrier, int total) {
                mtx_init(&barrier->guard, mtx_plain);
                cnd_init(&barrier->ready);
                barrier->total = total;
                barrier->waiting = 0;
                barrier->generation = 0;
            }

            static void barrier_wait(Barrier *barrier) {
                mtx_lock(&barrier->guard);
                unsigned mine = barrier->generation;
                if (++barrier->waiting == barrier->total) {
                    barrier->waiting = 0;
                    barrier->generation++;
                    mtx_unlock(&barrier->guard);
                    cnd_broadcast(&barrier->ready);
                    return;
                }
                while (barrier->generation == mine) {
                    cnd_wait(&barrier->ready, &barrier->guard);
                }
                mtx_unlock(&barrier->guard);
            }

            static void barrier_destroy(Barrier *barrier) {
                cnd_destroy(&barrier->ready);
                mtx_destroy(&barrier->guard);
            }
            """,
        ),
        _p(
            9205, "Blocking Queue", "Hard",
            "A ring buffer with two condition variables, because full and "
            "empty are different waits and one variable would wake the wrong "
            "side.",
            "O(1) per operation",
            """
            #define QUEUE_CAP 16

            typedef struct {
                mtx_t guard;
                cnd_t not_full;
                cnd_t not_empty;
                int slots[QUEUE_CAP];
                size_t head;
                size_t tail;
                size_t count;
            } BlockingQueue;

            static void queue_init(BlockingQueue *queue) {
                mtx_init(&queue->guard, mtx_plain);
                cnd_init(&queue->not_full);
                cnd_init(&queue->not_empty);
                queue->head = 0;
                queue->tail = 0;
                queue->count = 0;
            }

            static void queue_push(BlockingQueue *queue, int value) {
                mtx_lock(&queue->guard);
                while (queue->count == QUEUE_CAP) {
                    cnd_wait(&queue->not_full, &queue->guard);
                }
                queue->slots[queue->tail] = value;
                queue->tail = (queue->tail + 1) % QUEUE_CAP;
                queue->count++;
                mtx_unlock(&queue->guard);
                cnd_signal(&queue->not_empty);
            }

            static int queue_pop(BlockingQueue *queue) {
                mtx_lock(&queue->guard);
                while (queue->count == 0) {
                    cnd_wait(&queue->not_empty, &queue->guard);
                }
                int value = queue->slots[queue->head];
                queue->head = (queue->head + 1) % QUEUE_CAP;
                queue->count--;
                mtx_unlock(&queue->guard);
                cnd_signal(&queue->not_full);
                return value;
            }

            static void queue_destroy(BlockingQueue *queue) {
                cnd_destroy(&queue->not_empty);
                cnd_destroy(&queue->not_full);
                mtx_destroy(&queue->guard);
            }
            """,
        ),
        _p(
            9206, "Thread-Local Accumulator", "Medium",
            "Give each worker its own slot and add them up at the end. No "
            "lock at all, and no contention — the cheapest way to count.",
            "O(1) per update, O(workers) to total",
            """
            #define MAX_WORKERS 16

            typedef struct {
                /* One slot per worker, each padded to its own cache line so
                   the workers do not fight over one. */
                _Alignas(64) long long slot[MAX_WORKERS][8];
                int workers;
            } Accumulator;

            static void accumulator_init(Accumulator *acc, int workers) {
                acc->workers = workers;
                for (int i = 0; i < workers; i++) {
                    acc->slot[i][0] = 0;
                }
            }

            static void accumulator_add(Accumulator *acc, int worker,
                                        long long amount) {
                acc->slot[worker][0] += amount;
            }

            static long long accumulator_total(const Accumulator *acc) {
                long long total = 0;
                for (int i = 0; i < acc->workers; i++) {
                    total += acc->slot[i][0];
                }
                return total;
            }
            """,
        ),
        _p(
            9207, "Lock Ordering", "Medium",
            "Two locks taken in two orders is a deadlock waiting for the wrong "
            "interleaving. One fixed order everywhere breaks the circular "
            "wait, which is the cheapest of the four conditions to break.",
            "O(1), and it is the difference between working and hanging",
            """
            typedef struct {
                int id;
                mtx_t guard;
                long long balance;
            } Account;

            static void account_init(Account *account, int id,
                                     long long balance) {
                account->id = id;
                mtx_init(&account->guard, mtx_plain);
                account->balance = balance;
            }

            static bool account_transfer(Account *from, Account *to,
                                         long long amount) {
                /* Always lock the lower id first, whichever way the call
                   came in. */
                Account *first = from->id < to->id ? from : to;
                Account *second = from->id < to->id ? to : from;

                mtx_lock(&first->guard);
                mtx_lock(&second->guard);

                bool ok = from->balance >= amount;
                if (ok) {
                    from->balance -= amount;
                    to->balance += amount;
                }

                mtx_unlock(&second->guard);
                mtx_unlock(&first->guard);
                return ok;
            }

            static void account_destroy(Account *account) {
                mtx_destroy(&account->guard);
            }
            """,
        ),
        _p(
            9208, "Thread Pool", "Hard",
            "Workers wait on a queue of jobs. A stopping flag plus a broadcast "
            "is what lets them all wake up and leave rather than waiting "
            "forever on a queue nobody will fill.",
            "O(1) submit, work spread over the workers",
            """
            typedef struct {
                void (*run)(void *);
                void *context;
            } Job;

            typedef struct {
                mtx_t guard;
                cnd_t ready;
                Job jobs[256];
                size_t head;
                size_t tail;
                size_t count;
                bool stopping;
                thrd_t workers[8];
                int worker_count;
            } ThreadPool;

            static int pool_worker(void *arg) {
                ThreadPool *pool = arg;
                for (;;) {
                    mtx_lock(&pool->guard);
                    while (pool->count == 0 && !pool->stopping) {
                        cnd_wait(&pool->ready, &pool->guard);
                    }
                    if (pool->count == 0 && pool->stopping) {
                        mtx_unlock(&pool->guard);
                        return 0;
                    }
                    Job job = pool->jobs[pool->head];
                    pool->head = (pool->head + 1) % 256;
                    pool->count--;
                    mtx_unlock(&pool->guard);
                    job.run(job.context);
                }
            }

            static void pool_start(ThreadPool *pool, int workers) {
                mtx_init(&pool->guard, mtx_plain);
                cnd_init(&pool->ready);
                pool->head = 0;
                pool->tail = 0;
                pool->count = 0;
                pool->stopping = false;
                pool->worker_count = workers;
                for (int i = 0; i < workers; i++) {
                    thrd_create(&pool->workers[i], pool_worker, pool);
                }
            }

            static void pool_submit(ThreadPool *pool, void (*run)(void *),
                                    void *context) {
                mtx_lock(&pool->guard);
                pool->jobs[pool->tail].run = run;
                pool->jobs[pool->tail].context = context;
                pool->tail = (pool->tail + 1) % 256;
                pool->count++;
                mtx_unlock(&pool->guard);
                cnd_signal(&pool->ready);
            }

            static void pool_stop(ThreadPool *pool) {
                mtx_lock(&pool->guard);
                pool->stopping = true;
                mtx_unlock(&pool->guard);
                cnd_broadcast(&pool->ready);
                for (int i = 0; i < pool->worker_count; i++) {
                    thrd_join(pool->workers[i], NULL);
                }
                cnd_destroy(&pool->ready);
                mtx_destroy(&pool->guard);
            }
            """,
        ),
    ),
)


# ── 4. Cache and memory hierarchy ───────────────────────────

_CACHE = Pattern(
    id="sys-cache",
    name="Cache & Memory Hierarchy",
    order=104,
    blurb="The same work, laid out two ways, running an order of magnitude apart.",
    tell="It should be fast and it is not, and the algorithm is already right.",
    preamble=(STDLIB, STRING_H, STDBOOL, STDINT, STDDEF, ATOMIC, THREADS),
    problems=(
        _p(
            9401, "Cache Line", "Easy",
            "Memory moves in lines, not bytes. Sixty-four is the number to "
            "have in your head.",
            "O(1) — this is a fact, not an algorithm",
            """
            #define CACHE_LINE 64

            static bool same_cache_line(const void *a, const void *b) {
                uintptr_t x = (uintptr_t)a;
                uintptr_t y = (uintptr_t)b;
                return (x / CACHE_LINE) == (y / CACHE_LINE);
            }

            static size_t lines_spanned(size_t bytes) {
                return (bytes + CACHE_LINE - 1) / CACHE_LINE;
            }
            """,
        ),
        _p(
            9402, "False Sharing", "Hard",
            "Two threads writing different variables on the SAME line fight "
            "over it. _Alignas pushes them apart, at the cost of the bytes.",
            "Same instruction count, wildly different time",
            """
            typedef struct {
                atomic_llong a;
                atomic_llong b;
            } SharedPair;

            typedef struct {
                _Alignas(CACHE_LINE) atomic_llong a;
                _Alignas(CACHE_LINE) atomic_llong b;
            } PaddedPair;

            static void shared_pair_init(SharedPair *pair) {
                atomic_init(&pair->a, 0);
                atomic_init(&pair->b, 0);
            }

            static void padded_pair_init(PaddedPair *pair) {
                atomic_init(&pair->a, 0);
                atomic_init(&pair->b, 0);
            }
            """,
        ),
        _p(
            9403, "Row Major vs Column Major", "Medium",
            "The array is the same; the walk is not. Along a row uses every "
            "byte of each line fetched; down a column throws most away.",
            "Same O(n*n), an order of magnitude apart in practice",
            """
            static long long sum_by_rows(const int *grid, size_t rows,
                                         size_t cols) {
                long long total = 0;
                for (size_t r = 0; r < rows; r++) {
                    for (size_t c = 0; c < cols; c++) {
                        total += grid[r * cols + c];
                    }
                }
                return total;
            }

            static long long sum_by_columns(const int *grid, size_t rows,
                                            size_t cols) {
                long long total = 0;
                for (size_t c = 0; c < cols; c++) {
                    for (size_t r = 0; r < rows; r++) {
                        total += grid[r * cols + c];
                    }
                }
                return total;
            }
            """,
        ),
        _p(
            9404, "Struct Packing", "Medium",
            "Field order changes the size, because each field is padded to its "
            "own alignment. C never reorders for you — what you write is what "
            "you get.",
            "O(1) — but it decides how many fit in a line",
            """
            typedef struct {
                char flag;
                double value;
                char other;
                int count;
            } Loose;

            typedef struct {
                double value;
                int count;
                char flag;
                char other;
            } Tight;

            static size_t wasted_bytes(void) {
                return sizeof(Loose) - sizeof(Tight);
            }

            static size_t per_cache_line(size_t object_size) {
                return object_size ? CACHE_LINE / object_size : 0;
            }
            """,
        ),
        _p(
            9405, "Array of Structs vs Struct of Arrays", "Medium",
            "Reading one field out of an array of structs drags the rest along "
            "for the ride. Splitting the fields means every byte fetched is "
            "one you wanted.",
            "Same work, far fewer lines touched",
            """
            typedef struct {
                double x;
                double y;
                double z;
                double mass;
            } Particle;

            typedef struct {
                double *x;
                double *y;
                double *z;
                double *mass;
                size_t count;
            } Particles;

            static double total_mass_aos(const Particle *items, size_t count) {
                double total = 0;
                for (size_t i = 0; i < count; i++) {
                    total += items[i].mass;
                }
                return total;
            }

            static double total_mass_soa(const Particles *items) {
                double total = 0;
                for (size_t i = 0; i < items->count; i++) {
                    total += items->mass[i];
                }
                return total;
            }
            """,
        ),
        _p(
            9406, "Pointer Chasing vs Contiguous", "Medium",
            "A linked list makes the processor wait for each node before it "
            "knows where the next one is. An array it can prefetch.",
            "Same O(n), and the constant is what gets you",
            """
            typedef struct Link {
                int value;
                struct Link *next;
            } Link;

            static long long walk_links(const Link *head) {
                long long total = 0;
                while (head) {
                    total += head->value;
                    head = head->next;
                }
                return total;
            }

            static long long walk_array(const int *items, size_t count) {
                long long total = 0;
                for (size_t i = 0; i < count; i++) {
                    total += items[i];
                }
                return total;
            }
            """,
        ),
        _p(
            9407, "Branch Prediction", "Medium",
            "A branch the processor can guess is nearly free; one it cannot is "
            "a stall. Sorting first makes the SAME branch predictable.",
            "Same comparisons, very different cost",
            """
            static long long sum_over(const int *items, size_t count,
                                      int threshold) {
                long long total = 0;
                for (size_t i = 0; i < count; i++) {
                    if (items[i] >= threshold) {
                        total += items[i];
                    }
                }
                return total;
            }

            static long long sum_over_branchless(const int *items, size_t count,
                                                 int threshold) {
                long long total = 0;
                for (size_t i = 0; i < count; i++) {
                    long long mask = -(long long)(items[i] >= threshold);
                    total += items[i] & mask;
                }
                return total;
            }
            """,
        ),
        _p(
            9408, "Blocked Transpose", "Hard",
            "Transposing straight through misses on one side or the other. A "
            "tile at a time keeps both source and destination in cache.",
            "Same O(n*n), far fewer misses",
            """
            static void transpose_naive(const int *src, int *dst, size_t n) {
                for (size_t r = 0; r < n; r++) {
                    for (size_t c = 0; c < n; c++) {
                        dst[c * n + r] = src[r * n + c];
                    }
                }
            }

            static void transpose_blocked(const int *src, int *dst, size_t n,
                                          size_t block) {
                for (size_t r0 = 0; r0 < n; r0 += block) {
                    for (size_t c0 = 0; c0 < n; c0 += block) {
                        size_t r_end = r0 + block < n ? r0 + block : n;
                        size_t c_end = c0 + block < n ? c0 + block : n;
                        for (size_t r = r0; r < r_end; r++) {
                            for (size_t c = c0; c < c_end; c++) {
                                dst[c * n + r] = src[r * n + c];
                            }
                        }
                    }
                }
            }
            """,
        ),
    ),
)


# ── 5. Market data and matching ─────────────────────────────

_MARKET = Pattern(
    id="sys-market",
    name="Market Data & Matching",
    order=105,
    blurb="The pieces a trading system is made of, small enough to write out.",
    tell="Prices, quantities, a book, and a latency number somebody cares about.",
    preamble=(STDLIB, STRING_H, STDBOOL, STDINT, STDDEF),
    problems=(
        _p(
            9501, "Fixed-Point Price", "Medium",
            "Money is not a double. Store it as an integer number of ticks and "
            "the arithmetic is exact.",
            "O(1), and exactly representable",
            """
            #define PRICE_SCALE 10000

            typedef struct {
                long long ticks;
            } Price;

            static Price price_from_double(double value) {
                double scaled = value * PRICE_SCALE;
                long long rounded =
                    (long long)(scaled < 0 ? scaled - 0.5 : scaled + 0.5);
                Price price = {rounded};
                return price;
            }

            static double price_to_double(Price price) {
                return (double)price.ticks / PRICE_SCALE;
            }

            static Price price_add(Price a, Price b) {
                Price out = {a.ticks + b.ticks};
                return out;
            }

            static Price price_sub(Price a, Price b) {
                Price out = {a.ticks - b.ticks};
                return out;
            }

            static bool price_equal(Price a, Price b) {
                return a.ticks == b.ticks;
            }
            """,
        ),
        _p(
            9502, "Price Level", "Easy",
            "Everything resting at one price, kept as a total rather than a "
            "list. The book only needs the sum until something trades.",
            "O(1) add and remove",
            """
            typedef struct {
                Price price;
                long long quantity;
                int orders;
            } Level;

            static Level level_new(Price price, long long quantity) {
                Level level = {price, quantity, 1};
                return level;
            }

            static void level_add(Level *level, long long quantity) {
                level->quantity += quantity;
                level->orders++;
            }

            static void level_remove(Level *level, long long quantity) {
                level->quantity -=
                    quantity < level->quantity ? quantity : level->quantity;
                if (level->orders > 0) {
                    level->orders--;
                }
            }

            static bool level_empty(const Level *level) {
                return level->quantity <= 0;
            }
            """,
        ),
        _p(
            9503, "Order Book", "Hard",
            "Bids sorted high to low, asks low to high, so the best of each is "
            "the front. Fixed arrays, because a feed does not want an "
            "allocator in the path.",
            "O(levels) insert, O(1) best",
            """
            #define MAX_LEVELS 64

            typedef struct {
                Level bids[MAX_LEVELS];
                size_t bid_count;
                Level asks[MAX_LEVELS];
                size_t ask_count;
            } OrderBook;

            static void book_init(OrderBook *book) {
                book->bid_count = 0;
                book->ask_count = 0;
            }

            static void side_insert(Level *side, size_t *count, Price price,
                                    long long quantity, bool descending) {
                for (size_t i = 0; i < *count; i++) {
                    if (price_equal(side[i].price, price)) {
                        level_add(&side[i], quantity);
                        return;
                    }
                    bool before = descending
                                      ? side[i].price.ticks < price.ticks
                                      : price.ticks < side[i].price.ticks;
                    if (before) {
                        for (size_t j = *count; j > i; j--) {
                            side[j] = side[j - 1];
                        }
                        side[i] = level_new(price, quantity);
                        (*count)++;
                        return;
                    }
                }
                side[*count] = level_new(price, quantity);
                (*count)++;
            }

            static void book_add_bid(OrderBook *book, Price price,
                                     long long quantity) {
                side_insert(book->bids, &book->bid_count, price, quantity, true);
            }

            static void book_add_ask(OrderBook *book, Price price,
                                     long long quantity) {
                side_insert(book->asks, &book->ask_count, price, quantity, false);
            }

            static long long book_spread_ticks(const OrderBook *book) {
                if (book->bid_count == 0 || book->ask_count == 0) {
                    return -1;
                }
                return book->asks[0].price.ticks - book->bids[0].price.ticks;
            }

            static bool book_crossed(const OrderBook *book) {
                return book->bid_count > 0 && book->ask_count > 0 &&
                       book->bids[0].price.ticks >= book->asks[0].price.ticks;
            }
            """,
        ),
        _p(
            9504, "Matching Step", "Hard",
            "An aggressive order eats the book from the best price outward and "
            "stops when it is filled or the price stops being acceptable.",
            "O(levels touched)",
            """
            typedef struct {
                Price price;
                long long quantity;
            } Fill;

            static size_t match_buy(OrderBook *book, Price limit,
                                    long long wanted, Fill *fills,
                                    size_t max_fills) {
                size_t made = 0;
                while (wanted > 0 && book->ask_count > 0 && made < max_fills) {
                    Level *best = &book->asks[0];
                    if (limit.ticks < best->price.ticks) {
                        break;
                    }
                    long long taken =
                        wanted < best->quantity ? wanted : best->quantity;
                    fills[made].price = best->price;
                    fills[made].quantity = taken;
                    made++;
                    best->quantity -= taken;
                    wanted -= taken;
                    if (level_empty(best)) {
                        for (size_t i = 0; i + 1 < book->ask_count; i++) {
                            book->asks[i] = book->asks[i + 1];
                        }
                        book->ask_count--;
                    }
                }
                return made;
            }

            static long long filled_quantity(const Fill *fills, size_t count) {
                long long total = 0;
                for (size_t i = 0; i < count; i++) {
                    total += fills[i].quantity;
                }
                return total;
            }
            """,
        ),
        _p(
            9505, "VWAP", "Medium",
            "Volume-weighted, so a big trade counts for more. Carry the two "
            "running totals — you cannot average averages.",
            "O(1) per trade",
            """
            typedef struct {
                long long notional;
                long long volume;
            } Vwap;

            static void vwap_init(Vwap *vwap) {
                vwap->notional = 0;
                vwap->volume = 0;
            }

            static void vwap_add(Vwap *vwap, Price price, long long quantity) {
                vwap->notional += price.ticks * quantity;
                vwap->volume += quantity;
            }

            static bool vwap_value(const Vwap *vwap, Price *out) {
                if (vwap->volume == 0) {
                    return false;
                }
                out->ticks = vwap->notional / vwap->volume;
                return true;
            }
            """,
        ),
        _p(
            9506, "Rolling Window", "Medium",
            "A fixed-size ring of the last n values. Nothing shifts and nothing "
            "is allocated after construction.",
            "O(1) push, O(n) statistics",
            """
            #define WINDOW_CAP 64

            typedef struct {
                long long slots[WINDOW_CAP];
                size_t capacity;
                size_t next;
                size_t filled;
                long long running;
            } RollingWindow;

            static void window_init(RollingWindow *window, size_t capacity) {
                window->capacity = capacity < WINDOW_CAP ? capacity : WINDOW_CAP;
                window->next = 0;
                window->filled = 0;
                window->running = 0;
            }

            static void window_push(RollingWindow *window, long long value) {
                if (window->filled == window->capacity) {
                    window->running -= window->slots[window->next];
                } else {
                    window->filled++;
                }
                window->slots[window->next] = value;
                window->running += value;
                window->next = (window->next + 1) % window->capacity;
            }

            static bool window_mean(const RollingWindow *window, double *out) {
                if (window->filled == 0) {
                    return false;
                }
                *out = (double)window->running / (double)window->filled;
                return true;
            }

            static long long window_highest(const RollingWindow *window) {
                long long best = 0;
                for (size_t i = 0; i < window->filled; i++) {
                    if (i == 0 || window->slots[i] > best) {
                        best = window->slots[i];
                    }
                }
                return best;
            }
            """,
        ),
        _p(
            9507, "Latency Histogram", "Medium",
            "Keeping every sample to find the 99th percentile is the wrong "
            "trade. Bucket on the way in and the answer is a scan.",
            "O(1) record, O(buckets) percentile",
            """
            #define MAX_BUCKETS 64

            typedef struct {
                long long counts[MAX_BUCKETS];
                size_t buckets;
                long long width;
                long long total;
            } Histogram;

            static void hist_init(Histogram *hist, size_t buckets,
                                  long long width) {
                hist->buckets = buckets < MAX_BUCKETS ? buckets : MAX_BUCKETS;
                hist->width = width;
                hist->total = 0;
                memset(hist->counts, 0, sizeof(hist->counts));
            }

            static void hist_record(Histogram *hist, long long nanos) {
                size_t at = (size_t)(nanos / hist->width);
                if (at >= hist->buckets) {
                    at = hist->buckets - 1;
                }
                hist->counts[at]++;
                hist->total++;
            }

            static long long hist_percentile(const Histogram *hist,
                                             double fraction) {
                if (hist->total == 0) {
                    return -1;
                }
                long long wanted = (long long)(fraction * (double)hist->total);
                long long seen = 0;
                for (size_t i = 0; i < hist->buckets; i++) {
                    seen += hist->counts[i];
                    if (seen > wanted) {
                        return (long long)(i + 1) * hist->width;
                    }
                }
                return (long long)hist->buckets * hist->width;
            }
            """,
        ),
        _p(
            9508, "Tick Parsing", "Medium",
            "Parse the wire format in place. No strtok, no allocation — on a "
            "feed, the allocator is the latency.",
            "O(length), no allocation",
            """
            typedef struct {
                char symbol[8];
                Price price;
                long long quantity;
                bool valid;
            } Tick;

            static Tick parse_tick(const char *line, size_t length) {
                Tick tick;
                memset(&tick, 0, sizeof(tick));

                size_t at = 0;
                size_t wrote = 0;
                while (at < length && line[at] != ',') {
                    if (wrote + 1 < sizeof(tick.symbol)) {
                        tick.symbol[wrote++] = line[at];
                    }
                    at++;
                }
                if (at >= length) {
                    return tick;
                }
                at++;

                long long whole = 0;
                while (at < length && line[at] >= '0' && line[at] <= '9') {
                    whole = whole * 10 + (line[at++] - '0');
                }
                long long frac = 0;
                long long scale = PRICE_SCALE;
                if (at < length && line[at] == '.') {
                    at++;
                    while (at < length && line[at] >= '0' && line[at] <= '9' &&
                           scale > 1) {
                        scale /= 10;
                        frac += (line[at++] - '0') * scale;
                    }
                }
                if (at >= length || line[at] != ',') {
                    return tick;
                }
                at++;

                long long quantity = 0;
                bool any = false;
                while (at < length && line[at] >= '0' && line[at] <= '9') {
                    quantity = quantity * 10 + (line[at++] - '0');
                    any = true;
                }
                if (!any) {
                    return tick;
                }

                tick.price.ticks = whole * PRICE_SCALE + frac;
                tick.quantity = quantity;
                tick.valid = true;
                return tick;
            }
            """,
        ),
    ),
)


PATTERNS: tuple[Pattern, ...] = (
    _MEMORY,
    _CONCURRENCY,
    _LOCKFREE,
    _CACHE,
    _MARKET,
)
