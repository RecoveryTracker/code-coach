"""
Systems and low-level implementations, in C++.

The material quant and systems interviews actually ask for: write the
primitive, don't just name it. Each solution is the honest core of the real
thing — short enough to type from memory, complete enough to compile and run.

Where the real standard-library version does more (allocator support, custom
deleters, exception guarantees), the `idea` line says what has been left out
rather than pretending the short version is the whole story.
"""

from __future__ import annotations

from code_coach.leetcode.cpp_common import _p
from code_coach.leetcode.problems import Pattern

# Problem numbers start above anything LeetCode uses. The study panel and the
# worked lessons are keyed by number alone, so a systems problem numbered 1
# would pull Two Sum's brief and show it beside a UniquePtr exercise.
FIRST_NUMBER = 9000

ATOMIC = "#include <atomic>"
THREAD = "#include <thread>"
MUTEX = "#include <mutex>\n#include <condition_variable>"
UTILITY = "#include <utility>"
CSTDDEF = "#include <cstddef>"
CSTDINT = "#include <cstdint>"
NEW = "#include <new>"
VECTOR = "#include <vector>"
FUNCTIONAL = "#include <functional>"
USING = "using namespace std;"


# ── 1. Ownership and RAII ───────────────────────────────────

_MEMORY = Pattern(
    id="sys-memory",
    name="Ownership & RAII",
    order=101,
    blurb="Write the smart pointers yourself, and they stop being magic.",
    tell="Anything about who frees this, when, and what happens on a copy.",
    preamble=(UTILITY, CSTDDEF, NEW, USING),
    problems=(
        _p(
            9101, "UniquePtr", "Medium",
            "One owner. The whole type is a raw pointer plus a destructor, and "
            "a move that leaves the source empty.",
            "O(1) everything, sizeof(T*)",
            """
            template <typename T>
            class UniquePtr {
            public:
                explicit UniquePtr(T* raw = nullptr) : ptr(raw) {}
                ~UniquePtr() { delete ptr; }

                UniquePtr(const UniquePtr&) = delete;
                UniquePtr& operator=(const UniquePtr&) = delete;

                UniquePtr(UniquePtr&& other) noexcept : ptr(other.ptr) {
                    other.ptr = nullptr;
                }

                UniquePtr& operator=(UniquePtr&& other) noexcept {
                    if (this != &other) {
                        delete ptr;
                        ptr = other.ptr;
                        other.ptr = nullptr;
                    }
                    return *this;
                }

                T* get() const { return ptr; }
                T& operator*() const { return *ptr; }
                T* operator->() const { return ptr; }
                explicit operator bool() const { return ptr != nullptr; }

                T* release() {
                    T* out = ptr;
                    ptr = nullptr;
                    return out;
                }

            private:
                T* ptr;
            };
            """,
        ),
        _p(
            9102, "SharedPtr", "Hard",
            "The count lives beside the object, not inside it, so two "
            "SharedPtrs to the same thing share one control block.",
            "O(1) copy, one extra allocation",
            """
            template <typename T>
            class SharedPtr {
            public:
                explicit SharedPtr(T* raw = nullptr)
                    : ptr(raw), count(raw ? new long(1) : nullptr) {}

                SharedPtr(const SharedPtr& other)
                    : ptr(other.ptr), count(other.count) {
                    if (count) {
                        ++*count;
                    }
                }

                SharedPtr& operator=(const SharedPtr& other) {
                    if (this != &other) {
                        drop();
                        ptr = other.ptr;
                        count = other.count;
                        if (count) {
                            ++*count;
                        }
                    }
                    return *this;
                }

                ~SharedPtr() { drop(); }

                long use_count() const { return count ? *count : 0; }
                T* get() const { return ptr; }
                T& operator*() const { return *ptr; }

            private:
                void drop() {
                    if (count && --*count == 0) {
                        delete ptr;
                        delete count;
                    }
                }

                T* ptr;
                long* count;
            };
            """,
        ),
        _p(
            9103, "Optional", "Medium",
            "A value or nothing, without allocating. The storage is raw bytes "
            "and the value is built into them only when there is one.",
            "O(1), sizeof(T) + 1 rounded up",
            """
            template <typename T>
            class Optional {
            public:
                Optional() : filled(false) {}

                Optional(const T& value) : filled(true) {
                    new (storage) T(value);
                }

                ~Optional() { reset(); }

                bool has_value() const { return filled; }
                explicit operator bool() const { return filled; }

                T& value() { return *reinterpret_cast<T*>(storage); }
                const T& value() const {
                    return *reinterpret_cast<const T*>(storage);
                }

                T value_or(const T& fallback) const {
                    return filled ? value() : fallback;
                }

                void reset() {
                    if (filled) {
                        reinterpret_cast<T*>(storage)->~T();
                        filled = false;
                    }
                }

            private:
                alignas(T) unsigned char storage[sizeof(T)];
                bool filled;
            };
            """,
        ),
        _p(
            9104, "ScopeGuard", "Easy",
            "Run something on the way out, whatever happens. The whole idea of "
            "RAII in ten lines.",
            "O(1)",
            """
            template <typename Fn>
            class ScopeGuard {
            public:
                explicit ScopeGuard(Fn action) : run(action), live(true) {}

                ~ScopeGuard() {
                    if (live) {
                        run();
                    }
                }

                ScopeGuard(const ScopeGuard&) = delete;
                ScopeGuard& operator=(const ScopeGuard&) = delete;

                void dismiss() { live = false; }

            private:
                Fn run;
                bool live;
            };

            template <typename Fn>
            ScopeGuard<Fn> guard(Fn action) {
                return ScopeGuard<Fn>(action);
            }
            """,
        ),
        _p(
            9105, "Arena Allocator", "Medium",
            "Bump a pointer to allocate, and free everything at once. No "
            "per-object bookkeeping, which is why it is fast.",
            "O(1) allocate, O(1) reset",
            """
            class Arena {
            public:
                explicit Arena(size_t bytes)
                    : base(new unsigned char[bytes]), size(bytes), used(0) {}

                ~Arena() { delete[] base; }

                Arena(const Arena&) = delete;
                Arena& operator=(const Arena&) = delete;

                void* allocate(size_t bytes, size_t align) {
                    size_t at = (used + align - 1) & ~(align - 1);
                    if (at + bytes > size) {
                        return nullptr;
                    }
                    used = at + bytes;
                    return base + at;
                }

                template <typename T>
                T* make() {
                    void* slot = allocate(sizeof(T), alignof(T));
                    return slot ? new (slot) T() : nullptr;
                }

                void reset() { used = 0; }
                size_t bytes_used() const { return used; }

            private:
                unsigned char* base;
                size_t size;
                size_t used;
            };
            """,
        ),
        _p(
            9106, "SmallVector", "Hard",
            "Keep the first few elements inside the object, and only reach for "
            "the heap when it outgrows them.",
            "O(1) amortised push, no allocation while small",
            """
            template <typename T, size_t N>
            class SmallVector {
            public:
                SmallVector() : data(inline_storage()), count(0), space(N) {}

                ~SmallVector() {
                    clear();
                    if (data != inline_storage()) {
                        ::operator delete(data);
                    }
                }

                void push_back(const T& value) {
                    if (count == space) {
                        grow();
                    }
                    new (data + count) T(value);
                    ++count;
                }

                void clear() {
                    for (size_t i = 0; i < count; i++) {
                        data[i].~T();
                    }
                    count = 0;
                }

                size_t size() const { return count; }
                bool on_heap() const { return data != inline_storage(); }
                T& operator[](size_t i) { return data[i]; }

            private:
                T* inline_storage() {
                    return reinterpret_cast<T*>(buffer);
                }
                const T* inline_storage() const {
                    return reinterpret_cast<const T*>(buffer);
                }

                void grow() {
                    size_t wanted = space * 2;
                    T* fresh = static_cast<T*>(
                        ::operator new(wanted * sizeof(T)));
                    for (size_t i = 0; i < count; i++) {
                        new (fresh + i) T(data[i]);
                        data[i].~T();
                    }
                    if (data != inline_storage()) {
                        ::operator delete(data);
                    }
                    data = fresh;
                    space = wanted;
                }

                alignas(T) unsigned char buffer[N * sizeof(T)];
                T* data;
                size_t count;
                size_t space;
            };
            """,
        ),
        _p(
            9107, "Intrusive Refcount", "Medium",
            "Put the count inside the object and the pointer is one word "
            "again — no control block, and no second allocation.",
            "O(1), sizeof(T*)",
            """
            class RefCounted {
            public:
                void acquire() { ++refs; }

                void release() {
                    if (--refs == 0) {
                        delete this;
                    }
                }

                long references() const { return refs; }

            protected:
                RefCounted() : refs(0) {}
                virtual ~RefCounted() {}

            private:
                long refs;
            };

            template <typename T>
            class RefPtr {
            public:
                explicit RefPtr(T* raw = nullptr) : ptr(raw) {
                    if (ptr) {
                        ptr->acquire();
                    }
                }

                RefPtr(const RefPtr& other) : ptr(other.ptr) {
                    if (ptr) {
                        ptr->acquire();
                    }
                }

                ~RefPtr() {
                    if (ptr) {
                        ptr->release();
                    }
                }

                T* get() const { return ptr; }

            private:
                T* ptr;
            };
            """,
        ),
        _p(
            9108, "Aligned Storage", "Medium",
            "Build an object into memory you already own. This is what a "
            "vector does between reserve and push_back.",
            "O(1)",
            """
            template <typename T>
            class Slot {
            public:
                Slot() : filled(false) {}

                ~Slot() { destroy(); }

                template <typename... Args>
                T& construct(Args&&... args) {
                    destroy();
                    T* made = new (storage) T(static_cast<Args&&>(args)...);
                    filled = true;
                    return *made;
                }

                void destroy() {
                    if (filled) {
                        reinterpret_cast<T*>(storage)->~T();
                        filled = false;
                    }
                }

                bool empty() const { return !filled; }
                T& get() { return *reinterpret_cast<T*>(storage); }

                static size_t alignment() { return alignof(T); }

            private:
                alignas(T) unsigned char storage[sizeof(T)];
                bool filled;
            };
            """,
        ),
    ),
)


# ── 2. Concurrency primitives ───────────────────────────────

_CONCURRENCY = Pattern(
    id="sys-concurrency",
    name="Concurrency Primitives",
    order=102,
    blurb="Build the lock before you use it, and its costs become obvious.",
    tell="Threads sharing anything: a counter, a queue, a piece of state.",
    preamble=(ATOMIC, THREAD, MUTEX, VECTOR, FUNCTIONAL, USING),
    problems=(
        _p(
            9201, "SpinLock", "Medium",
            "Spin on an atomic flag. Fast when the wait is nanoseconds, "
            "terrible when it is longer — it burns a core to wait.",
            "O(1) uncontended",
            """
            class SpinLock {
            public:
                void lock() {
                    while (flag.test_and_set(memory_order_acquire)) {
                        // Nothing here but waiting. On a real one this is
                        // where a pause instruction goes.
                    }
                }

                bool try_lock() {
                    return !flag.test_and_set(memory_order_acquire);
                }

                void unlock() { flag.clear(memory_order_release); }

            private:
                atomic_flag flag = ATOMIC_FLAG_INIT;
            };
            """,
        ),
        _p(
            9202, "TicketLock", "Medium",
            "Take a number and wait for it. Unlike a spinlock this is FAIR — "
            "threads are served in the order they arrived.",
            "O(1) uncontended, first-come-first-served",
            """
            class TicketLock {
            public:
                void lock() {
                    unsigned mine = next.fetch_add(1, memory_order_relaxed);
                    while (serving.load(memory_order_acquire) != mine) {
                    }
                }

                void unlock() {
                    serving.fetch_add(1, memory_order_release);
                }

            private:
                atomic<unsigned> next{0};
                atomic<unsigned> serving{0};
            };
            """,
        ),
        _p(
            9203, "Semaphore", "Medium",
            "A count of permits. Waiters sleep rather than spin, which is the "
            "right trade when the wait might be long.",
            "O(1) per acquire",
            """
            class Semaphore {
            public:
                explicit Semaphore(int permits) : count(permits) {}

                void acquire() {
                    unique_lock<mutex> lock(guard);
                    ready.wait(lock, [this] { return count > 0; });
                    --count;
                }

                void release() {
                    {
                        lock_guard<mutex> lock(guard);
                        ++count;
                    }
                    ready.notify_one();
                }

                int available() {
                    lock_guard<mutex> lock(guard);
                    return count;
                }

            private:
                mutex guard;
                condition_variable ready;
                int count;
            };
            """,
        ),
        _p(
            9204, "Reader-Writer Lock", "Hard",
            "Many readers or one writer. This version lets writers in ahead of "
            "new readers, or a steady stream of readers would starve them.",
            "O(1) per acquire",
            """
            class RWLock {
            public:
                void lock_shared() {
                    unique_lock<mutex> lock(guard);
                    ready.wait(lock, [this] {
                        return writers == 0 && waiting_writers == 0;
                    });
                    ++readers;
                }

                void unlock_shared() {
                    {
                        lock_guard<mutex> lock(guard);
                        --readers;
                    }
                    ready.notify_all();
                }

                void lock() {
                    unique_lock<mutex> lock(guard);
                    ++waiting_writers;
                    ready.wait(lock, [this] {
                        return writers == 0 && readers == 0;
                    });
                    --waiting_writers;
                    ++writers;
                }

                void unlock() {
                    {
                        lock_guard<mutex> lock(guard);
                        --writers;
                    }
                    ready.notify_all();
                }

            private:
                mutex guard;
                condition_variable ready;
                int readers = 0;
                int writers = 0;
                int waiting_writers = 0;
            };
            """,
        ),
        _p(
            9205, "Barrier", "Medium",
            "Nobody leaves until everybody arrives. The generation counter is "
            "what stops a fast thread lapping the others.",
            "O(1) per arrival",
            """
            class Barrier {
            public:
                explicit Barrier(int parties)
                    : total(parties), waiting(0), generation(0) {}

                void arrive_and_wait() {
                    unique_lock<mutex> lock(guard);
                    int mine = generation;
                    if (++waiting == total) {
                        waiting = 0;
                        ++generation;
                        ready.notify_all();
                        return;
                    }
                    ready.wait(lock, [this, mine] {
                        return generation != mine;
                    });
                }

            private:
                mutex guard;
                condition_variable ready;
                int total;
                int waiting;
                int generation;
            };
            """,
        ),
        _p(
            9206, "CallOnce", "Medium",
            "Exactly one thread runs it, and the rest wait for that to finish "
            "rather than sailing past a half-built thing.",
            "O(1) after the first call",
            """
            class OnceFlag {
            public:
                template <typename Fn>
                void call(Fn action) {
                    if (done.load(memory_order_acquire)) {
                        return;
                    }
                    lock_guard<mutex> lock(guard);
                    if (done.load(memory_order_relaxed)) {
                        return;
                    }
                    action();
                    done.store(true, memory_order_release);
                }

                bool finished() const {
                    return done.load(memory_order_acquire);
                }

            private:
                mutex guard;
                atomic<bool> done{false};
            };
            """,
        ),
        _p(
            9207, "Blocking Queue", "Medium",
            "A queue that makes consumers wait when it is empty. Two condition "
            "variables, because full and empty are different waits.",
            "O(1) per operation",
            """
            template <typename T>
            class BlockingQueue {
            public:
                explicit BlockingQueue(size_t cap) : capacity(cap) {}

                void push(const T& value) {
                    unique_lock<mutex> lock(guard);
                    not_full.wait(lock, [this] {
                        return items.size() < capacity;
                    });
                    items.push_back(value);
                    lock.unlock();
                    not_empty.notify_one();
                }

                T pop() {
                    unique_lock<mutex> lock(guard);
                    not_empty.wait(lock, [this] { return !items.empty(); });
                    T front = items.front();
                    items.erase(items.begin());
                    lock.unlock();
                    not_full.notify_one();
                    return front;
                }

            private:
                mutex guard;
                condition_variable not_full;
                condition_variable not_empty;
                vector<T> items;
                size_t capacity;
            };
            """,
        ),
        _p(
            9208, "Thread Pool", "Hard",
            "Workers wait on a queue of jobs. Joining in the destructor is "
            "what stops the program ending while work is still running.",
            "O(1) submit, work spread over the workers",
            """
            class ThreadPool {
            public:
                explicit ThreadPool(int workers) : stopping(false) {
                    for (int i = 0; i < workers; i++) {
                        threads.emplace_back([this] { run(); });
                    }
                }

                ~ThreadPool() {
                    {
                        lock_guard<mutex> lock(guard);
                        stopping = true;
                    }
                    ready.notify_all();
                    for (thread& worker : threads) {
                        worker.join();
                    }
                }

                void submit(function<void()> job) {
                    {
                        lock_guard<mutex> lock(guard);
                        jobs.push_back(job);
                    }
                    ready.notify_one();
                }

            private:
                void run() {
                    while (true) {
                        function<void()> job;
                        {
                            unique_lock<mutex> lock(guard);
                            ready.wait(lock, [this] {
                                return stopping || !jobs.empty();
                            });
                            if (stopping && jobs.empty()) {
                                return;
                            }
                            job = jobs.front();
                            jobs.erase(jobs.begin());
                        }
                        job();
                    }
                }

                mutex guard;
                condition_variable ready;
                vector<thread> threads;
                vector<function<void()>> jobs;
                bool stopping;
            };
            """,
        ),
    ),
)




# ── 3. Lock-free and atomics ────────────────────────────────

_LOCKFREE = Pattern(
    id="sys-lockfree",
    name="Lock-free & Atomics",
    order=103,
    blurb="No lock at all: atomics, compare-and-swap, and the orderings that make it safe.",
    tell="A hot path where even an uncontended mutex is too much.",
    preamble=(ATOMIC, THREAD, CSTDDEF, VECTOR, USING),
    problems=(
        _p(
            9301, "Relaxed vs Sequential Counter", "Medium",
            "Both counts are exact — atomicity is not ordering. Relaxed only "
            "gives up the guarantee about what OTHER writes you see around it.",
            "O(1) per increment, relaxed is markedly cheaper",
            """
            class Counter {
            public:
                void bump_relaxed() {
                    value.fetch_add(1, memory_order_relaxed);
                }

                void bump_ordered() {
                    value.fetch_add(1, memory_order_seq_cst);
                }

                long long get() const {
                    return value.load(memory_order_relaxed);
                }

            private:
                atomic<long long> value{0};
            };
            """,
        ),
        _p(
            9302, "CAS Loop", "Medium",
            "Read, compute, swap it in if nothing moved. compare_exchange_weak "
            "may fail spuriously, which is why it always lives in a loop.",
            "O(1) uncontended, retries under contention",
            """
            class AtomicMax {
            public:
                void offer(long long candidate) {
                    long long seen = best.load(memory_order_relaxed);
                    while (candidate > seen &&
                           !best.compare_exchange_weak(seen, candidate,
                                                       memory_order_release,
                                                       memory_order_relaxed)) {
                        // seen was refreshed by the failed exchange, so the
                        // next comparison uses the value that beat us.
                    }
                }

                long long get() const {
                    return best.load(memory_order_acquire);
                }

            private:
                atomic<long long> best{0};
            };
            """,
        ),
        _p(
            9303, "SPSC Ring Buffer", "Hard",
            "One producer, one consumer, no lock. The release on write pairs "
            "with the acquire on read, and that pairing is the whole safety "
            "argument.",
            "O(1) per item, wait-free for both sides",
            """
            template <typename T, size_t N>
            class SpscQueue {
            public:
                bool push(const T& value) {
                    size_t head = write.load(memory_order_relaxed);
                    size_t next = (head + 1) % N;
                    if (next == read.load(memory_order_acquire)) {
                        return false;
                    }
                    slots[head] = value;
                    write.store(next, memory_order_release);
                    return true;
                }

                bool pop(T& out) {
                    size_t tail = read.load(memory_order_relaxed);
                    if (tail == write.load(memory_order_acquire)) {
                        return false;
                    }
                    out = slots[tail];
                    read.store((tail + 1) % N, memory_order_release);
                    return true;
                }

            private:
                T slots[N];
                atomic<size_t> write{0};
                atomic<size_t> read{0};
            };
            """,
        ),
        _p(
            9304, "Treiber Stack", "Hard",
            "Push and pop by swapping the head. Lock-free, and it leaks on "
            "purpose here — reclaiming a popped node safely is the hard part, "
            "and it needs hazard pointers or epochs.",
            "O(1) uncontended, retries under contention",
            """
            template <typename T>
            class TreiberStack {
            public:
                void push(const T& value) {
                    Node* fresh = new Node{value, nullptr};
                    fresh->next = head.load(memory_order_relaxed);
                    while (!head.compare_exchange_weak(fresh->next, fresh,
                                                       memory_order_release,
                                                       memory_order_relaxed)) {
                    }
                }

                bool pop(T& out) {
                    Node* top = head.load(memory_order_acquire);
                    while (top && !head.compare_exchange_weak(
                                      top, top->next, memory_order_acquire,
                                      memory_order_relaxed)) {
                    }
                    if (!top) {
                        return false;
                    }
                    out = top->value;
                    // Deliberately not deleted: another thread may still be
                    // reading top->next. This is the ABA problem's home.
                    return true;
                }

            private:
                struct Node {
                    T value;
                    Node* next;
                };

                atomic<Node*> head{nullptr};
            };
            """,
        ),
        _p(
            9305, "Seqlock", "Hard",
            "Writers never wait, readers retry. An odd counter means a write "
            "is in flight, so a reader that sees one just goes round again.",
            "O(1) write, readers retry under contention",
            """
            // A seqlock earns its keep when the payload is too big to copy
            // in one atomic step. Two words would not need one; a book of
            // levels does, and that is the realistic case.
            struct Book {
                long long bid[4];
                long long ask[4];
            };

            class Seqlock {
            public:
                void write(const Book& fresh) {
                    version.fetch_add(1, memory_order_release);
                    atomic_thread_fence(memory_order_release);
                    held = fresh;
                    atomic_thread_fence(memory_order_release);
                    version.fetch_add(1, memory_order_release);
                }

                Book read() const {
                    Book copy;
                    unsigned before;
                    do {
                        before = version.load(memory_order_acquire);
                        if (before & 1u) {
                            continue;
                        }
                        copy = held;
                        atomic_thread_fence(memory_order_acquire);
                    } while (before != version.load(memory_order_acquire) ||
                             (before & 1u));
                    return copy;
                }

            private:
                atomic<unsigned> version{0};
                Book held{};
            };
            """,
        ),
        _p(
            9306, "Acquire-Release Message Passing", "Medium",
            "The flag is what publishes the payload. Release on the store and "
            "acquire on the load means a reader seeing the flag must also see "
            "everything written before it.",
            "O(1), and no lock anywhere",
            """
            class Mailbox {
            public:
                void publish(int a, int b) {
                    first = a;
                    second = b;
                    ready.store(true, memory_order_release);
                }

                bool collect(int& a, int& b) const {
                    if (!ready.load(memory_order_acquire)) {
                        return false;
                    }
                    a = first;
                    b = second;
                    return true;
                }

            private:
                int first = 0;
                int second = 0;
                atomic<bool> ready{false};
            };
            """,
        ),
        _p(
            9307, "Spin With Backoff", "Medium",
            "Spinning flat out starves the thread holding the lock. Backing "
            "off, then yielding, gets out of its way.",
            "O(1) uncontended, far kinder under contention",
            """
            class BackoffLock {
            public:
                void lock() {
                    int spins = 1;
                    while (taken.exchange(true, memory_order_acquire)) {
                        for (int i = 0; i < spins; i++) {
                            // Burn a little, then look again.
                        }
                        if (spins < 1024) {
                            spins *= 2;
                        } else {
                            this_thread::yield();
                        }
                    }
                }

                void unlock() { taken.store(false, memory_order_release); }

            private:
                atomic<bool> taken{false};
            };
            """,
        ),
        _p(
            9308, "Atomic Reference Count", "Hard",
            "The increment can be relaxed; the decrement cannot. The release "
            "on the way down and the acquire before deleting are what stop "
            "the destructor racing another thread's last use.",
            "O(1) per copy",
            """
            class AtomicRefCount {
            public:
                void acquire() { refs.fetch_add(1, memory_order_relaxed); }

                bool release() {
                    if (refs.fetch_sub(1, memory_order_release) != 1) {
                        return false;
                    }
                    // Last one out. Acquire so everything the other threads
                    // did is visible before whatever cleans up runs.
                    atomic_thread_fence(memory_order_acquire);
                    return true;
                }

                long count() const { return refs.load(memory_order_relaxed); }

            private:
                atomic<long> refs{1};
            };
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
    preamble=(ATOMIC, THREAD, CSTDDEF, CSTDINT, VECTOR, USING),
    problems=(
        _p(
            9401, "Cache Line", "Easy",
            "Memory moves in lines, not bytes. Sixty-four is the number to "
            "have in your head; C++17 spells it "
            "hardware_destructive_interference_size.",
            "O(1) — this is a fact, not an algorithm",
            """
            constexpr size_t CACHE_LINE = 64;

            inline bool same_cache_line(const void* a, const void* b) {
                uintptr_t x = reinterpret_cast<uintptr_t>(a);
                uintptr_t y = reinterpret_cast<uintptr_t>(b);
                return (x / CACHE_LINE) == (y / CACHE_LINE);
            }

            inline size_t lines_spanned(size_t bytes) {
                return (bytes + CACHE_LINE - 1) / CACHE_LINE;
            }
            """,
        ),
        _p(
            9402, "False Sharing", "Hard",
            "Two threads writing different variables on the SAME line fight "
            "over it. Padding them apart costs bytes and buys back the "
            "bandwidth.",
            "Same instruction count, wildly different time",
            """
            struct Shared {
                atomic<long long> a{0};
                atomic<long long> b{0};
            };

            struct Padded {
                alignas(CACHE_LINE) atomic<long long> a{0};
                alignas(CACHE_LINE) atomic<long long> b{0};
            };

            template <typename Pair>
            void hammer(Pair& pair, int rounds) {
                thread first([&pair, rounds] {
                    for (int i = 0; i < rounds; i++) {
                        pair.a.fetch_add(1, memory_order_relaxed);
                    }
                });
                thread second([&pair, rounds] {
                    for (int i = 0; i < rounds; i++) {
                        pair.b.fetch_add(1, memory_order_relaxed);
                    }
                });
                first.join();
                second.join();
            }
            """,
        ),
        _p(
            9403, "Row Major vs Column Major", "Medium",
            "The array is the same; the walk is not. Going along a row uses "
            "every byte of each line fetched, going down a column throws most "
            "of it away.",
            "Same O(n*n), an order of magnitude apart in practice",
            """
            long long sum_by_rows(const vector<int>& grid, size_t rows,
                                  size_t cols) {
                long long total = 0;
                for (size_t r = 0; r < rows; r++) {
                    for (size_t c = 0; c < cols; c++) {
                        total += grid[r * cols + c];
                    }
                }
                return total;
            }

            long long sum_by_columns(const vector<int>& grid, size_t rows,
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
            "Field order changes the size. The compiler pads each field to its "
            "own alignment, so scattering small ones between large ones wastes "
            "space you then have to fetch.",
            "O(1) — but it decides how many objects fit in a line",
            """
            struct Loose {
                char flag;
                double value;
                char other;
                int count;
            };

            struct Tight {
                double value;
                int count;
                char flag;
                char other;
            };

            inline size_t wasted_bytes() {
                return sizeof(Loose) - sizeof(Tight);
            }

            inline size_t per_cache_line(size_t object_size) {
                return object_size ? CACHE_LINE / object_size : 0;
            }
            """,
        ),
        _p(
            9405, "Array of Structs vs Struct of Arrays", "Medium",
            "If you only read one field, an array of structs drags the rest "
            "along for the ride. Splitting the fields means every byte "
            "fetched is one you wanted.",
            "Same work, far fewer lines touched",
            """
            struct Particle {
                double x;
                double y;
                double z;
                double mass;
            };

            struct Particles {
                vector<double> x;
                vector<double> y;
                vector<double> z;
                vector<double> mass;

                void add(double px, double py, double pz, double m) {
                    x.push_back(px);
                    y.push_back(py);
                    z.push_back(pz);
                    mass.push_back(m);
                }
            };

            inline double total_mass(const vector<Particle>& items) {
                double total = 0;
                for (const Particle& p : items) {
                    total += p.mass;
                }
                return total;
            }

            inline double total_mass(const Particles& items) {
                double total = 0;
                for (double m : items.mass) {
                    total += m;
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
            struct Link {
                int value;
                Link* next;
            };

            inline long long walk_links(Link* head) {
                long long total = 0;
                while (head) {
                    total += head->value;
                    head = head->next;
                }
                return total;
            }

            inline long long walk_array(const vector<int>& items) {
                long long total = 0;
                for (int value : items) {
                    total += value;
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
            inline long long sum_over(const vector<int>& items, int threshold) {
                long long total = 0;
                for (int value : items) {
                    if (value >= threshold) {
                        total += value;
                    }
                }
                return total;
            }

            // No branch at all: build a mask and multiply. Slower when the
            // branch predicts well, faster when it cannot.
            inline long long sum_over_branchless(const vector<int>& items,
                                                 int threshold) {
                long long total = 0;
                for (int value : items) {
                    long long mask = -(long long)(value >= threshold);
                    total += value & mask;
                }
                return total;
            }
            """,
        ),
        _p(
            9408, "Blocked Transpose", "Hard",
            "Transposing straight through misses on one side or the other. "
            "Working a tile at a time keeps both the source and the "
            "destination in cache.",
            "Same O(n*n), far fewer misses",
            """
            void transpose_naive(const vector<int>& src, vector<int>& dst,
                                 size_t n) {
                for (size_t r = 0; r < n; r++) {
                    for (size_t c = 0; c < n; c++) {
                        dst[c * n + r] = src[r * n + c];
                    }
                }
            }

            void transpose_blocked(const vector<int>& src, vector<int>& dst,
                                   size_t n, size_t block) {
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


PATTERNS: tuple[Pattern, ...] = (
    _MEMORY,
    _CONCURRENCY,
    _LOCKFREE,
    _CACHE,
)
