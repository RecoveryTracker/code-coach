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


PATTERNS: tuple[Pattern, ...] = (
    _MEMORY,
    _CONCURRENCY,
)
