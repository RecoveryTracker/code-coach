"""How you would arrive at each primitive, rather than the finished one.

The bank hands over a spinlock. That teaches you what a spinlock looks like
and not one thing about why it is shaped that way — which is the half an
interview actually probes. So each of these does what the LeetCode lessons
do: the obvious first attempt, what it costs, the one observation that fixes
it, and then the thing assembled a stage at a time.

The shapes are the LeetCode ones, reused rather than reinvented, so the study
panel renders these without knowing they are different.

The code in the stages is C++, because that is where this material is most at
home. The Rust and C banks solve the same problems, and the reasoning is the
same in all three even where the spelling is not.
"""

from __future__ import annotations

from code_coach.leetcode.worked import Stage, Worked, _s

__all__ = ["Stage", "Worked", "WORKED", "CANONICAL", "worked_for", "worked_for_problem"]


WORKED: dict[int, Worked] = {
    # ── Ownership and RAII ──────────────────────────────────
    9101: Worked(
        problem=9101,
        naive=(
            "Use a raw pointer and remember to delete it before every return."
        ),
        why_not=(
            "Every return is a place to forget, and an exception is a return "
            "you did not write. One early exit added six months later leaks, "
            "and nothing about the code says it should not."
        ),
        insight=(
            "A destructor runs on every exit path, including the exceptional "
            "one. So make the pointer a member of something whose destructor "
            "frees it, and the problem stops being yours to remember."
        ),
        stages=(
            _s(
                "One member, one owner. Everything else follows from this.",
                "template <typename T>\nclass UniquePtr {\npublic:\n"
                "    explicit UniquePtr(T* raw = nullptr) : ptr(raw) {}\n"
                "    ~UniquePtr() { delete ptr; }\n\nprivate:\n    T* ptr;\n};",
            ),
            _s(
                "Copying would give two owners and two deletes of one object. "
                "Deleting the copy operations says that out loud, at compile "
                "time, rather than at three in the morning.",
                "UniquePtr(const UniquePtr&) = delete;\n"
                "UniquePtr& operator=(const UniquePtr&) = delete;",
            ),
            _s(
                "Moving IS allowed — one owner, just a different one. The "
                "source must be left safe to destroy, which means null.",
                "UniquePtr(UniquePtr&& other) noexcept : ptr(other.ptr) {\n"
                "    other.ptr = nullptr;\n}",
            ),
            _s(
                "Move assignment has to free what it already had first, and "
                "guard against being assigned to itself.",
                "UniquePtr& operator=(UniquePtr&& other) noexcept {\n"
                "    if (this != &other) {\n        delete ptr;\n"
                "        ptr = other.ptr;\n        other.ptr = nullptr;\n"
                "    }\n    return *this;\n}",
            ),
            _s(
                "Then the accessors, so it reads like a pointer. release() "
                "is the escape hatch for handing ownership to something else.",
                "T& operator*() const { return *ptr; }\n"
                "T* operator->() const { return ptr; }\n"
                "T* release() {\n    T* out = ptr;\n    ptr = nullptr;\n"
                "    return out;\n}",
            ),
        ),
    ),
    9102: Worked(
        problem=9102,
        naive=(
            "Put a count inside the object and have each copy increment it."
        ),
        why_not=(
            "Then only types you wrote can be shared, and you cannot share "
            "an int or anything from a library. The count has to live "
            "somewhere that does not require the object's cooperation."
        ),
        insight=(
            "Put the count BESIDE the object, in a block both pointers point "
            "at. That is the control block, and it is the entire difference "
            "between shared_ptr and an intrusive count."
        ),
        stages=(
            _s(
                "Two pointers: the object, and a count allocated with it. A "
                "null pointer gets no count, so an empty one costs nothing.",
                "template <typename T>\nclass SharedPtr {\npublic:\n"
                "    explicit SharedPtr(T* raw = nullptr)\n"
                "        : ptr(raw), count(raw ? new long(1) : nullptr) {}\n\n"
                "private:\n    T* ptr;\n    long* count;\n};",
            ),
            _s(
                "A copy takes both pointers and bumps the count. This is the "
                "whole of sharing.",
                "SharedPtr(const SharedPtr& other)\n"
                "    : ptr(other.ptr), count(other.count) {\n"
                "    if (count) {\n        ++*count;\n    }\n}",
            ),
            _s(
                "Dropping one decrements, and only the last one frees — both "
                "the object and the count, or the count leaks instead.",
                "void drop() {\n    if (count && --*count == 0) {\n"
                "        delete ptr;\n        delete count;\n    }\n}\n\n"
                "~SharedPtr() { drop(); }",
            ),
            _s(
                "Assignment is a drop and then a copy. Self-assignment would "
                "otherwise free the thing it is about to point at.",
                "SharedPtr& operator=(const SharedPtr& other) {\n"
                "    if (this != &other) {\n        drop();\n"
                "        ptr = other.ptr;\n        count = other.count;\n"
                "        if (count) {\n            ++*count;\n        }\n"
                "    }\n    return *this;\n}",
            ),
            _s(
                "One thing this version is NOT: thread-safe. Two threads "
                "copying the same SharedPtr race on ++*count. The real one "
                "uses an atomic, which is most of why it is not free.",
                "long use_count() const { return count ? *count : 0; }",
            ),
        ),
    ),
    9103: Worked(
        problem=9103,
        naive=(
            "Hold a T and a bool saying whether it is there."
        ),
        why_not=(
            "That constructs a T whether or not you have one, so the type "
            "must be default-constructible, and an empty optional still pays "
            "for a constructor and a destructor it did not want."
        ),
        insight=(
            "Hold raw bytes big enough and aligned right, and construct into "
            "them only when there is a value. The bool then really means "
            "'has this storage been built into?'."
        ),
        stages=(
            _s(
                "Storage, not a value. alignas is what makes it legal to "
                "build a T there.",
                "template <typename T>\nclass Optional {\nprivate:\n"
                "    alignas(T) unsigned char storage[sizeof(T)];\n"
                "    bool filled;\n};",
            ),
            _s(
                "Placement new builds a T into memory you already own. It "
                "allocates nothing — that is the point.",
                "Optional(const T& value) : filled(true) {\n"
                "    new (storage) T(value);\n}",
            ),
            _s(
                "Reading it back is a cast. Ugly, and it is what every "
                "implementation of this does underneath.",
                "T& value() { return *reinterpret_cast<T*>(storage); }",
            ),
            _s(
                "Emptying it means calling the destructor by hand, because "
                "nothing else will. Guarding on filled stops a double "
                "destroy.",
                "void reset() {\n    if (filled) {\n"
                "        reinterpret_cast<T*>(storage)->~T();\n"
                "        filled = false;\n    }\n}",
            ),
            _s(
                "And the destructor is just that. Forgetting this line makes "
                "an Optional<vector> leak every time.",
                "~Optional() { reset(); }",
            ),
        ),
    ),
    9104: Worked(
        problem=9104,
        naive=(
            "Write the cleanup at the end of the function."
        ),
        why_not=(
            "It only runs if control reaches the end. An early return skips "
            "it, and an exception skips it without even looking like a "
            "return."
        ),
        insight=(
            "A destructor is the only thing that runs on every exit. So put "
            "the cleanup in one, and the scope's closing brace becomes the "
            "guarantee."
        ),
        stages=(
            _s(
                "Hold the action. A template parameter rather than "
                "std::function, so a lambda costs nothing to store.",
                "template <typename Fn>\nclass ScopeGuard {\npublic:\n"
                "    explicit ScopeGuard(Fn action) : run(action), live(true) {}\n\n"
                "private:\n    Fn run;\n    bool live;\n};",
            ),
            _s(
                "The destructor is the whole feature.",
                "~ScopeGuard() {\n    if (live) {\n        run();\n    }\n}",
            ),
            _s(
                "Copying it would run the action twice, which for a cleanup "
                "is exactly the bug. Delete the copy.",
                "ScopeGuard(const ScopeGuard&) = delete;\n"
                "ScopeGuard& operator=(const ScopeGuard&) = delete;",
            ),
            _s(
                "Then a way to say it is no longer needed — the commit case, "
                "where the work succeeded and there is nothing to roll back.",
                "void dismiss() { live = false; }",
            ),
        ),
    ),
    9105: Worked(
        problem=9105,
        naive=(
            "Call malloc for each object and free each one when done."
        ),
        why_not=(
            "The allocator has to search a free list, take a lock, and "
            "maintain per-object headers. For ten thousand short-lived "
            "objects that bookkeeping dwarfs the work, and the memory ends up "
            "scattered across the heap so nothing is in cache."
        ),
        insight=(
            "If everything dies at the same time, nothing needs individual "
            "bookkeeping. Take one block and hand out slices by moving a "
            "pointer; freeing is setting the pointer back to the start."
        ),
        stages=(
            _s(
                "One block, and how far into it you have got.",
                "class Arena {\nprivate:\n    unsigned char* base;\n"
                "    size_t size;\n    size_t used;\n};",
            ),
            _s(
                "Allocating is rounding up to the alignment and moving the "
                "cursor. That bit trick works because alignments are powers "
                "of two.",
                "size_t at = (used + align - 1) & ~(align - 1);",
            ),
            _s(
                "Refuse rather than overrun. An arena that grows would chain "
                "another block here; failing is the honest small version.",
                "if (at + bytes > size) {\n    return nullptr;\n}\n"
                "used = at + bytes;\nreturn base + at;",
            ),
            _s(
                "And freeing everything is one assignment. Note what this "
                "does NOT do: run destructors. An arena of types that own "
                "anything needs more than this.",
                "void reset() { used = 0; }",
            ),
        ),
    ),
    9106: Worked(
        problem=9106,
        naive=(
            "Use a vector and let it allocate."
        ),
        why_not=(
            "Most of these hold two or three items and are destroyed "
            "immediately. Every one costs an allocation and a free, and the "
            "elements land somewhere else in memory rather than beside the "
            "object you already have in cache."
        ),
        insight=(
            "Keep room for the first few INSIDE the object, and only reach "
            "for the heap when it outgrows them. The common case then costs "
            "nothing at all."
        ),
        stages=(
            _s(
                "Storage inside the object, plus a pointer that says where "
                "the elements actually live.",
                "alignas(T) unsigned char buffer[N * sizeof(T)];\nT* data;\n"
                "size_t count;\nsize_t space;",
            ),
            _s(
                "Start pointed at yourself. Comparing data against the "
                "inline buffer is how everything else knows which mode it "
                "is in.",
                "SmallVector() : data(inline_storage()), count(0), space(N) {}\n"
                "bool on_heap() const { return data != inline_storage(); }",
            ),
            _s(
                "Push builds in place. Nothing allocates until space runs "
                "out.",
                "void push_back(const T& value) {\n"
                "    if (count == space) {\n        grow();\n    }\n"
                "    new (data + count) T(value);\n    ++count;\n}",
            ),
            _s(
                "Growing is where the two modes meet: allocate, move "
                "everything across, destroy the originals, and only free the "
                "old block if it was on the heap.",
                "T* fresh = static_cast<T*>(::operator new(wanted * sizeof(T)));\n"
                "for (size_t i = 0; i < count; i++) {\n"
                "    new (fresh + i) T(data[i]);\n    data[i].~T();\n}\n"
                "if (data != inline_storage()) {\n"
                "    ::operator delete(data);\n}",
            ),
            _s(
                "And the destructor has the same fork. Freeing the inline "
                "buffer would be freeing part of yourself.",
                "~SmallVector() {\n    clear();\n"
                "    if (data != inline_storage()) {\n"
                "        ::operator delete(data);\n    }\n}",
            ),
        ),
    ),
    9107: Worked(
        problem=9107,
        naive=(
            "Use shared_ptr everywhere something is shared."
        ),
        why_not=(
            "Every shared_ptr is two words and its control block is a second "
            "allocation, so the pointer no longer fits in a register and "
            "creating one touches the allocator. In a graph of small nodes "
            "that overhead is most of the memory."
        ),
        insight=(
            "If you control the type, put the count inside it. The pointer is "
            "one word again and there is no second allocation — which is why "
            "COM, Qt and most game engines do it this way."
        ),
        stages=(
            _s(
                "The count lives in the object, and the object knows how to "
                "delete itself.",
                "class RefCounted {\npublic:\n    void acquire() { ++refs; }\n\n"
                "protected:\n    RefCounted() : refs(0) {}\n"
                "    virtual ~RefCounted() {}\n\nprivate:\n    long refs;\n};",
            ),
            _s(
                "Release is where 'delete this' earns its reputation. It is "
                "correct here and only here: nothing touches the object "
                "afterwards.",
                "void release() {\n    if (--refs == 0) {\n"
                "        delete this;\n    }\n}",
            ),
            _s(
                "The handle is one pointer. That is the whole saving.",
                "template <typename T>\nclass RefPtr {\npublic:\n"
                "    explicit RefPtr(T* raw = nullptr) : ptr(raw) {\n"
                "        if (ptr) {\n            ptr->acquire();\n        }\n"
                "    }\n\nprivate:\n    T* ptr;\n};",
            ),
            _s(
                "Copy acquires, destruction releases. The virtual destructor "
                "is not optional — delete this through a base pointer needs "
                "it.",
                "~RefPtr() {\n    if (ptr) {\n        ptr->release();\n    }\n}",
            ),
        ),
    ),
    9108: Worked(
        problem=9108,
        naive=(
            "Default-construct the object and assign over it when the real "
            "value arrives."
        ),
        why_not=(
            "It requires a default constructor the type may not have, it "
            "runs one you did not want, and assigning over it is a different "
            "operation from constructing — for some types a more expensive "
            "one."
        ),
        insight=(
            "Separate the memory from the object. Reserve the storage now, "
            "and construct into it when you actually have something to put "
            "there. That separation is exactly what vector::reserve does."
        ),
        stages=(
            _s(
                "Aligned bytes and a flag. No T exists yet.",
                "template <typename T>\nclass Slot {\nprivate:\n"
                "    alignas(T) unsigned char storage[sizeof(T)];\n"
                "    bool filled;\n};",
            ),
            _s(
                "Perfect forwarding so the arguments reach T's constructor "
                "unchanged — this is emplace, and why emplace beats push.",
                "template <typename... Args>\nT& construct(Args&&... args) {\n"
                "    destroy();\n"
                "    T* made = new (storage) T(static_cast<Args&&>(args)...);\n"
                "    filled = true;\n    return *made;\n}",
            ),
            _s(
                "Destroying is an explicit destructor call, guarded so it "
                "cannot happen twice.",
                "void destroy() {\n    if (filled) {\n"
                "        reinterpret_cast<T*>(storage)->~T();\n"
                "        filled = false;\n    }\n}",
            ),
            _s(
                "Constructing over an occupied slot destroys first, which is "
                "why construct() opens with destroy(). Leaving that out "
                "leaks whatever was there.",
                "~Slot() { destroy(); }",
            ),
        ),
    ),
    # ── Concurrency ─────────────────────────────────────────
    9201: Worked(
        problem=9201,
        naive=(
            "Use a bool: check it, and if it is false set it to true."
        ),
        why_not=(
            "Two threads can both read false before either writes true, and "
            "both proceed. The check and the set have to be one indivisible "
            "operation or there is nothing stopping them."
        ),
        insight=(
            "test_and_set does both at once: it sets the flag and tells you "
            "what it was. If it was already set, somebody else is inside."
        ),
        stages=(
            _s(
                "atomic_flag is the one type guaranteed lock-free on every "
                "platform, which is what you want a lock built out of.",
                "class SpinLock {\nprivate:\n"
                "    atomic_flag flag = ATOMIC_FLAG_INIT;\n};",
            ),
            _s(
                "Spin until the flag was clear when you set it. Acquire, "
                "because nothing after this may be reordered before it.",
                "void lock() {\n"
                "    while (flag.test_and_set(memory_order_acquire)) {\n    }\n}",
            ),
            _s(
                "Release on the way out, pairing with the acquire — that "
                "pairing is what makes the next thread see your writes.",
                "void unlock() { flag.clear(memory_order_release); }",
            ),
            _s(
                "try_lock is the same operation without the loop, which is "
                "the whole reason test_and_set returns anything.",
                "bool try_lock() {\n"
                "    return !flag.test_and_set(memory_order_acquire);\n}",
            ),
            _s(
                "What this is bad at: any wait longer than a context switch. "
                "It burns a core, and if the holder gets descheduled it burns "
                "it for a whole time slice.",
                "",
            ),
        ),
    ),
    9202: Worked(
        problem=9202,
        naive=(
            "Use the spinlock. It already excludes."
        ),
        why_not=(
            "It is not fair. Whoever's test_and_set happens to land first "
            "wins, so an unlucky thread can be passed over indefinitely while "
            "others take the lock again and again."
        ),
        insight=(
            "Give each arrival a number and serve them in order. It is the "
            "deli counter, and it makes starvation impossible by "
            "construction."
        ),
        stages=(
            _s(
                "Two counters: the next ticket to hand out, and the one being "
                "served.",
                "class TicketLock {\nprivate:\n    atomic<unsigned> next{0};\n"
                "    atomic<unsigned> serving{0};\n};",
            ),
            _s(
                "Taking a ticket is one atomic add, and it hands back your "
                "number. Relaxed is enough — the ordering comes from the "
                "wait below.",
                "unsigned mine = next.fetch_add(1, memory_order_relaxed);",
            ),
            _s(
                "Then wait for your number. Acquire here is what publishes "
                "the previous holder's writes to you.",
                "while (serving.load(memory_order_acquire) != mine) {\n}",
            ),
            _s(
                "Unlocking serves the next number. Because tickets were "
                "handed out in arrival order, so is service.",
                "void unlock() {\n"
                "    serving.fetch_add(1, memory_order_release);\n}",
            ),
        ),
    ),
    9203: Worked(
        problem=9203,
        naive=(
            "Spin on an atomic counter until it is positive, then decrement."
        ),
        why_not=(
            "A semaphore's wait is usually long — that is what it is for. "
            "Spinning through it burns a core doing nothing, and there may be "
            "more waiters than cores."
        ),
        insight=(
            "When the wait is long, sleep. A condition variable hands the "
            "core back and puts you on a queue the releaser can wake."
        ),
        stages=(
            _s(
                "A count, a mutex to protect it, and something to sleep on.",
                "class Semaphore {\nprivate:\n    mutex guard;\n"
                "    condition_variable ready;\n    int count;\n};",
            ),
            _s(
                "Wait for a permit. The predicate form is the loop — it "
                "re-checks after every wakeup, which you need because a "
                "wakeup does not promise anything.",
                "void acquire() {\n    unique_lock<mutex> lock(guard);\n"
                "    ready.wait(lock, [this] { return count > 0; });\n"
                "    --count;\n}",
            ),
            _s(
                "Releasing bumps the count under the lock, then wakes one "
                "waiter.",
                "void release() {\n    {\n"
                "        lock_guard<mutex> lock(guard);\n        ++count;\n"
                "    }\n    ready.notify_one();\n}",
            ),
            _s(
                "Note the braces: the lock is released BEFORE notifying. "
                "Notifying while holding it wakes a thread that immediately "
                "blocks on the mutex you still hold.",
                "",
            ),
        ),
    ),
    9204: Worked(
        problem=9204,
        naive=(
            "Use one mutex for everything."
        ),
        why_not=(
            "Readers do not conflict with each other, so serialising them "
            "throws away all the parallelism in a read-mostly workload. Ten "
            "threads reading take ten times as long as one for no reason."
        ),
        insight=(
            "The rule is many readers OR one writer. Count the readers and "
            "flag the writer, and let the condition variable enforce it."
        ),
        stages=(
            _s(
                "Three numbers describe the whole state.",
                "int readers = 0;\nint writers = 0;\nint waiting_writers = 0;",
            ),
            _s(
                "A reader waits only for a writer.",
                "void lock_shared() {\n    unique_lock<mutex> lock(guard);\n"
                "    ready.wait(lock, [this] { return writers == 0; });\n"
                "    ++readers;\n}",
            ),
            _s(
                "A writer waits for everyone.",
                "void lock() {\n    unique_lock<mutex> lock(guard);\n"
                "    ready.wait(lock, [this] {\n"
                "        return writers == 0 && readers == 0;\n    });\n"
                "    ++writers;\n}",
            ),
            _s(
                "And now the flaw: with readers arriving steadily, the "
                "condition for a writer is never true. It starves. Counting "
                "WAITING writers and making new readers respect them is the "
                "fix.",
                "ready.wait(lock, [this] {\n"
                "    return writers == 0 && waiting_writers == 0;\n});",
            ),
            _s(
                "Unlocking notifies everyone, because releasing a write lock "
                "may free many readers at once and notify_one would wake "
                "exactly one of them.",
                "void unlock() {\n    {\n"
                "        lock_guard<mutex> lock(guard);\n        --writers;\n"
                "    }\n    ready.notify_all();\n}",
            ),
        ),
    ),
    9205: Worked(
        problem=9205,
        naive=(
            "Count arrivals, and when the count reaches n wake everyone and "
            "set it back to zero."
        ),
        why_not=(
            "A fast thread can come back round and arrive again before the "
            "slow ones have woken. It sees the reset counter, joins the next "
            "round, and the barrier lets it through a phase early."
        ),
        insight=(
            "Number the rounds. A waiter remembers which round it arrived in "
            "and waits for that number to change, so it cannot be confused by "
            "a later one."
        ),
        stages=(
            _s(
                "The count, and which round it belongs to.",
                "int total;\nint waiting;\nint generation;",
            ),
            _s(
                "On arrival, remember your round before touching anything.",
                "unique_lock<mutex> lock(guard);\nint mine = generation;",
            ),
            _s(
                "The last to arrive resets the count, advances the round, and "
                "releases everyone.",
                "if (++waiting == total) {\n    waiting = 0;\n"
                "    ++generation;\n    ready.notify_all();\n    return;\n}",
            ),
            _s(
                "Everyone else waits for the round to change — not for the "
                "count, which is exactly the thing that gets reset underneath "
                "them.",
                "ready.wait(lock, [this, mine] {\n"
                "    return generation != mine;\n});",
            ),
        ),
    ),
    9206: Worked(
        problem=9206,
        naive=(
            "Check a bool; if it is false, run the action and set it true."
        ),
        why_not=(
            "Two threads can both see false and both run it. Worse, a thread "
            "that sees true may see it before the action's writes are "
            "visible, and sail on past a half-initialised thing."
        ),
        insight=(
            "Take a lock and check again inside it. The outer check is the "
            "fast path for the thousands of later calls; the inner one is "
            "what makes it correct."
        ),
        stages=(
            _s(
                "A flag and a lock. The flag is atomic because the fast path "
                "reads it without the lock.",
                "atomic<bool> done{false};\nmutex guard;",
            ),
            _s(
                "The fast path. Acquire, so seeing true also means seeing "
                "everything the action wrote.",
                "if (done.load(memory_order_acquire)) {\n    return;\n}",
            ),
            _s(
                "Then the lock, and the SECOND check. Without this, two "
                "threads that both got past the first check both run the "
                "action.",
                "lock_guard<mutex> lock(guard);\n"
                "if (done.load(memory_order_relaxed)) {\n    return;\n}",
            ),
            _s(
                "Run it, then publish with release — which is what makes the "
                "fast path's acquire meaningful.",
                "action();\ndone.store(true, memory_order_release);",
            ),
            _s(
                "This is double-checked locking, and it is famous for being "
                "wrong when written without the atomic. The orderings are "
                "not decoration.",
                "",
            ),
        ),
    ),
    9207: Worked(
        problem=9207,
        naive=(
            "A queue and a mutex. Consumers take the lock and return nothing "
            "if it is empty."
        ),
        why_not=(
            "Then the consumer has to poll, so it either burns a core asking "
            "or adds latency by sleeping between attempts. Neither is what "
            "you want from a queue that exists to hand work over."
        ),
        insight=(
            "Two different waits are happening — a consumer waiting for "
            "not-empty and a producer waiting for not-full — so they need two "
            "condition variables, or each wakes the wrong side."
        ),
        stages=(
            _s(
                "The state, and one condition per direction.",
                "mutex guard;\ncondition_variable not_full;\n"
                "condition_variable not_empty;\nvector<T> items;\n"
                "size_t capacity;",
            ),
            _s(
                "A producer waits for room.",
                "void push(const T& value) {\n"
                "    unique_lock<mutex> lock(guard);\n"
                "    not_full.wait(lock, [this] {\n"
                "        return items.size() < capacity;\n    });\n"
                "    items.push_back(value);",
            ),
            _s(
                "Then wakes a consumer — after unlocking, so the woken thread "
                "does not immediately block on the mutex it needs.",
                "    lock.unlock();\n    not_empty.notify_one();\n}",
            ),
            _s(
                "The consumer is the mirror image, waiting on not_empty and "
                "notifying not_full.",
                "T pop() {\n    unique_lock<mutex> lock(guard);\n"
                "    not_empty.wait(lock, [this] { return !items.empty(); });\n"
                "    T front = items.front();\n"
                "    items.erase(items.begin());\n    lock.unlock();\n"
                "    not_full.notify_one();\n    return front;\n}",
            ),
        ),
    ),
    9208: Worked(
        problem=9208,
        naive=(
            "Start a thread for each job."
        ),
        why_not=(
            "Creating a thread costs tens of microseconds and a stack, "
            "usually a megabyte of address space. For jobs measured in "
            "microseconds the creation dominates, and ten thousand jobs means "
            "ten thousand threads fighting over however many cores you have."
        ),
        insight=(
            "Create the threads once and feed them. The pool turns 'how many "
            "jobs' into 'how many cores', which is the number that actually "
            "matters."
        ),
        stages=(
            _s(
                "Workers, a queue, and the machinery to wait on it.",
                "vector<thread> threads;\nvector<function<void()>> jobs;\n"
                "mutex guard;\ncondition_variable ready;\nbool stopping;",
            ),
            _s(
                "Each worker loops: wait for a job or for shutdown, take one, "
                "run it outside the lock.",
                "unique_lock<mutex> lock(guard);\n"
                "ready.wait(lock, [this] {\n"
                "    return stopping || !jobs.empty();\n});",
            ),
            _s(
                "The exit condition is stopping AND empty — not stopping "
                "alone, or shutdown throws away queued work.",
                "if (stopping && jobs.empty()) {\n    return;\n}",
            ),
            _s(
                "Take the job, drop the lock, then run it. Running under the "
                "lock would serialise the whole pool into one thread.",
                "job = jobs.front();\njobs.erase(jobs.begin());\n"
                "lock.unlock();\njob();",
            ),
            _s(
                "The destructor sets the flag, wakes everyone, and joins. "
                "Without the join the program can exit while a job is "
                "half-done.",
                "{\n    lock_guard<mutex> lock(guard);\n    stopping = true;\n}\n"
                "ready.notify_all();\nfor (thread& worker : threads) {\n"
                "    worker.join();\n}",
            ),
        ),
    ),
    # ── Lock-free and atomics ───────────────────────────────
    9301: Worked(
        problem=9301,
        naive=(
            "Use a plain int and increment it from every thread."
        ),
        why_not=(
            "An increment is a read, an add and a write. Two threads can read "
            "the same value, add one to it, and write the same result — so "
            "two increments become one. It is not rare under contention; it "
            "is the normal outcome."
        ),
        insight=(
            "fetch_add does the whole read-modify-write indivisibly. And once "
            "you have that, the ordering argument is a SEPARATE question: "
            "atomic says nobody sees a half-done increment, not that anyone "
            "sees your other writes."
        ),
        stages=(
            _s(
                "One atomic, and that alone fixes the lost updates.",
                "class Counter {\nprivate:\n    atomic<long long> value{0};\n};",
            ),
            _s(
                "Relaxed is enough for a counter. It promises the increment "
                "is indivisible and promises nothing about anything else — "
                "which is all a statistic needs.",
                "void bump_relaxed() {\n"
                "    value.fetch_add(1, memory_order_relaxed);\n}",
            ),
            _s(
                "Sequentially consistent additionally puts this operation in "
                "a single global order every thread agrees on. The total is "
                "identical; what differs is what else is guaranteed.",
                "void bump_ordered() {\n"
                "    value.fetch_add(1, memory_order_seq_cst);\n}",
            ),
            _s(
                "So the useful thing to be able to say: if the counter is "
                "the only shared state, relaxed. If seeing the counter tells "
                "you something else is ready, it is not the counter you "
                "needed — it is a release store.",
                "long long get() const {\n"
                "    return value.load(memory_order_relaxed);\n}",
            ),
        ),
    ),
    9302: Worked(
        problem=9302,
        naive=(
            "Read the current best, compare, and store the new one if it is "
            "bigger."
        ),
        why_not=(
            "Between your read and your store somebody else can write a "
            "larger value, and your store overwrites it. The maximum goes "
            "DOWN, which is the one thing it must never do."
        ),
        insight=(
            "compare_exchange only writes if the value is still what you "
            "read. If it changed, it hands you the new one and you try again "
            "with that."
        ),
        stages=(
            _s(
                "Read what is there now. Relaxed: the acquire that matters "
                "comes with the exchange.",
                "long long seen = best.load(memory_order_relaxed);",
            ),
            _s(
                "Only try if you would improve it. That check is also the "
                "loop's exit — somebody beating you is a reason to stop, not "
                "to retry.",
                "while (candidate > seen) {",
            ),
            _s(
                "The exchange writes only if nothing moved. On failure it "
                "updates seen with the value that beat you, which is why the "
                "loop needs no re-read.",
                "    if (best.compare_exchange_weak(seen, candidate,\n"
                "                                   memory_order_release,\n"
                "                                   memory_order_relaxed)) {\n"
                "        return;\n    }\n}",
            ),
            _s(
                "Weak rather than strong because weak may fail spuriously on "
                "some architectures and is cheaper there — and you are in a "
                "loop already, so a spurious failure costs nothing.",
                "",
            ),
        ),
    ),
    9303: Worked(
        problem=9303,
        naive=(
            "A ring buffer with a mutex around push and pop."
        ),
        why_not=(
            "For one producer and one consumer the mutex is pure overhead: "
            "they are almost never in the buffer at the same time, and when "
            "they are they are at opposite ends. You are paying for exclusion "
            "you do not need."
        ),
        insight=(
            "With exactly one of each, the producer only writes the write "
            "index and the consumer only writes the read index. Neither "
            "writes what the other writes — so no exclusion is needed, only "
            "ordering."
        ),
        stages=(
            _s(
                "Storage and two indexes. Which thread owns which index is "
                "the whole design.",
                "T slots[N];\natomic<size_t> write{0};\natomic<size_t> read{0};",
            ),
            _s(
                "The producer reads its own index relaxed — nobody else "
                "writes it — and the consumer's with acquire, to see how far "
                "it has got.",
                "size_t head = write.load(memory_order_relaxed);\n"
                "size_t next = (head + 1) % N;\n"
                "if (next == read.load(memory_order_acquire)) {\n"
                "    return false;\n}",
            ),
            _s(
                "Write the slot, THEN publish the index. This order is the "
                "safety argument: the release store is what makes the slot "
                "visible to whoever sees the new index.",
                "slots[head] = value;\nwrite.store(next, memory_order_release);",
            ),
            _s(
                "The consumer is the mirror image, and the acquire on the "
                "write index is what pairs with that release.",
                "size_t tail = read.load(memory_order_relaxed);\n"
                "if (tail == write.load(memory_order_acquire)) {\n"
                "    return false;\n}\nout = slots[tail];\n"
                "read.store((tail + 1) % N, memory_order_release);",
            ),
            _s(
                "One slot is always left empty — full and empty would "
                "otherwise both be head == tail and be indistinguishable.",
                "",
            ),
        ),
    ),
    9304: Worked(
        problem=9304,
        naive=(
            "A linked stack with a mutex around push and pop."
        ),
        why_not=(
            "Correct, and the lock becomes the bottleneck: every thread "
            "serialises on one word regardless of how briefly it needs it. "
            "And a thread descheduled while holding it blocks everyone."
        ),
        insight=(
            "The whole update is one pointer swap. So do it with "
            "compare-and-swap and retry — no thread can block another, "
            "because nobody holds anything."
        ),
        stages=(
            _s(
                "One atomic pointer is the entire structure.",
                "struct Node {\n    T value;\n    Node* next;\n};\n"
                "atomic<Node*> head{nullptr};",
            ),
            _s(
                "Push: point the new node at the current head, then swap it "
                "in. On failure the exchange refreshes fresh->next for you, "
                "which is why the loop body is empty.",
                "fresh->next = head.load(memory_order_relaxed);\n"
                "while (!head.compare_exchange_weak(fresh->next, fresh,\n"
                "                                   memory_order_release,\n"
                "                                   memory_order_relaxed)) {\n}",
            ),
            _s(
                "Pop: read the head and swap in its next.",
                "Node* top = head.load(memory_order_acquire);\n"
                "while (top && !head.compare_exchange_weak(\n"
                "                  top, top->next, memory_order_acquire,\n"
                "                  memory_order_relaxed)) {\n}",
            ),
            _s(
                "And here is the part that makes this genuinely hard. "
                "Deleting the popped node is unsafe: another thread may be "
                "between reading top and reading top->next, and the memory "
                "would be gone underneath it.",
                "out = top->value;\n"
                "// deliberately not deleted",
            ),
            _s(
                "Worse, freeing and reallocating can produce the SAME address "
                "again, so a compare-and-swap succeeds against a pointer that "
                "means something different. That is the ABA problem, and "
                "solving it is what hazard pointers and epochs are for.",
                "",
            ),
        ),
    ),
    9305: Worked(
        problem=9305,
        naive=(
            "A reader-writer lock. Readers share, the writer excludes."
        ),
        why_not=(
            "The writer still waits for every reader to leave, and on a "
            "market data path the writer is the one that must never wait — "
            "the price is stale the moment it is late. Readers are also "
            "taking a lock on the hot path to read something that changes "
            "constantly anyway."
        ),
        insight=(
            "Let the writer never wait and make the READER detect that it "
            "read mid-update and retry. A counter bumped before and after the "
            "write tells it: odd means a write is in flight, and a changed "
            "value means one happened while it was reading."
        ),
        stages=(
            _s(
                "A version counter beside the data. Even means settled, odd "
                "means being written.",
                "atomic<unsigned> version{0};\nBook held{};",
            ),
            _s(
                "The writer bumps to odd, writes, bumps to even. It never "
                "waits for anybody.",
                "version.fetch_add(1, memory_order_release);\nheld = fresh;\n"
                "version.fetch_add(1, memory_order_release);",
            ),
            _s(
                "The reader takes the version, copies, and takes it again.",
                "before = version.load(memory_order_acquire);\ncopy = held;",
            ),
            _s(
                "Then the two tests. Odd means a write was already in "
                "progress when it started; changed means one began and "
                "finished while it was copying. Either way, go round again.",
                "} while (before != version.load(memory_order_acquire) ||\n"
                "         (before & 1u));",
            ),
            _s(
                "What this costs: the reader may copy a torn value before "
                "discarding it, so the payload must be safe to read "
                "garbage — no pointers to follow, no destructors. A plain "
                "struct of numbers, which market data usually is.",
                "",
            ),
        ),
    ),
    9306: Worked(
        problem=9306,
        naive=(
            "Write the data, then set a flag. The reader checks the flag and "
            "reads the data."
        ),
        why_not=(
            "Nothing stops the compiler or the processor moving the flag's "
            "store before the data's. The reader sees the flag, reads the "
            "data, and gets whatever was there before — with no lock and no "
            "crash to tell it."
        ),
        insight=(
            "A release store publishes everything written before it, and an "
            "acquire load that sees that store receives all of it. The flag "
            "is not just a signal; it is the thing that carries the payload "
            "across."
        ),
        stages=(
            _s(
                "The payload is ordinary. Only the flag is atomic — that is "
                "the whole point.",
                "int first = 0;\nint second = 0;\natomic<bool> ready{false};",
            ),
            _s(
                "Write the payload, then release. Nothing above may be "
                "reordered below this line.",
                "void publish(int a, int b) {\n    first = a;\n"
                "    second = b;\n    ready.store(true, memory_order_release);\n}",
            ),
            _s(
                "Acquire first, and only then read. Nothing below may be "
                "reordered above it.",
                "if (!ready.load(memory_order_acquire)) {\n    return false;\n}\n"
                "a = first;\nb = second;",
            ),
            _s(
                "The pairing is the guarantee, and it only works as a pair. "
                "A release with no matching acquire, or an acquire with no "
                "matching release, promises nothing at all.",
                "",
            ),
        ),
    ),
    9307: Worked(
        problem=9307,
        naive=(
            "Spin as tightly as possible, so you take the lock the instant it "
            "is free."
        ),
        why_not=(
            "A tight spin hammers the cache line the holder needs to write to "
            "release it, so you actively slow down the thread you are waiting "
            "for. With more spinners than cores you can stop it running at "
            "all."
        ),
        insight=(
            "Back off. Wait a little longer each time, and once it is clearly "
            "not a short wait, give the core up — which is the only thing "
            "that helps if the holder is not running."
        ),
        stages=(
            _s(
                "Exchange rather than test-and-set, so the loop reads a plain "
                "bool between attempts rather than writing every time.",
                "atomic<bool> taken{false};\nint spins = 1;",
            ),
            _s(
                "Try once. If it was already true, somebody has it.",
                "while (taken.exchange(true, memory_order_acquire)) {",
            ),
            _s(
                "Then wait, doubling each round. Short waits stay fast; long "
                "ones stop hammering.",
                "    for (int i = 0; i < spins; i++) {\n    }\n"
                "    if (spins < 1024) {\n        spins *= 2;\n    }",
            ),
            _s(
                "And past a threshold, hand the core back. If the holder is "
                "descheduled this is the only thing that lets it run.",
                "    else {\n        this_thread::yield();\n    }\n}",
            ),
        ),
    ),
    9308: Worked(
        problem=9308,
        naive=(
            "Make both the increment and the decrement sequentially "
            "consistent. It is the safe default."
        ),
        why_not=(
            "It is correct and it is the most expensive ordering there is, "
            "paid on every copy of every shared pointer. And it hides the "
            "actually interesting fact: the two directions do not need the "
            "same thing."
        ),
        insight=(
            "An increment can be relaxed, because you already hold a "
            "reference — nobody can free it underneath you. A decrement "
            "cannot, because the thread that takes it to zero must see "
            "everything every other holder did before destroying it."
        ),
        stages=(
            _s(
                "Relaxed on the way up. You are holding one already, so the "
                "object cannot go anywhere.",
                "void acquire() { refs.fetch_add(1, memory_order_relaxed); }",
            ),
            _s(
                "Release on the way down, so your writes are visible to "
                "whoever ends up destroying it.",
                "if (refs.fetch_sub(1, memory_order_release) != 1) {\n"
                "    return false;\n}",
            ),
            _s(
                "And an acquire fence before cleanup. That is what makes the "
                "other threads' releases visible to the one thread that is "
                "about to run the destructor.",
                "atomic_thread_fence(memory_order_acquire);\nreturn true;",
            ),
            _s(
                "fetch_sub returns the value BEFORE the subtraction, so "
                "'!= 1' means 'I was not the last'. Comparing against 0 is "
                "the off-by-one that makes it never free.",
                "",
            ),
        ),
    ),
    # ── Cache and memory hierarchy ──────────────────────────
    9401: Worked(
        problem=9401,
        naive=(
            "Reason about memory in bytes, because that is the unit of "
            "everything else in the language."
        ),
        why_not=(
            "The hardware does not move bytes. Reading one byte fetches "
            "sixty-four, so a byte-by-byte model predicts the wrong cost for "
            "nearly everything — and gets false sharing exactly backwards."
        ),
        insight=(
            "The line is the unit. Once you count lines touched rather than "
            "bytes read, the surprising results — column walks, false "
            "sharing, pointer chasing — all become the obvious ones."
        ),
        stages=(
            _s(
                "The number. C++17 spells it "
                "hardware_destructive_interference_size; it is 64 on every "
                "current x86 and ARM.",
                "constexpr size_t CACHE_LINE = 64;",
            ),
            _s(
                "Which line an address is on is just division. Two addresses "
                "share a line when the quotient matches.",
                "inline bool same_cache_line(const void* a, const void* b) {\n"
                "    uintptr_t x = reinterpret_cast<uintptr_t>(a);\n"
                "    uintptr_t y = reinterpret_cast<uintptr_t>(b);\n"
                "    return (x / CACHE_LINE) == (y / CACHE_LINE);\n}",
            ),
            _s(
                "And how many lines a size spans is a rounding up. Sixty-five "
                "bytes is two lines, which is the whole reason a "
                "sixty-five-byte struct is worth rearranging.",
                "inline size_t lines_spanned(size_t bytes) {\n"
                "    return (bytes + CACHE_LINE - 1) / CACHE_LINE;\n}",
            ),
        ),
    ),
    9402: Worked(
        problem=9402,
        naive=(
            "Give each thread its own counter. They are separate variables, "
            "so there is no sharing and no contention."
        ),
        why_not=(
            "Separate variables can still be on the same cache line, and the "
            "line is what the cores fight over. Two adjacent atomics "
            "ping-pong between caches on every write, and the code that "
            "looks obviously parallel runs slower than one thread."
        ),
        insight=(
            "Nothing is logically shared — the SHARING IS THE LAYOUT. Push "
            "them onto separate lines and the contention disappears, at the "
            "cost of the padding bytes."
        ),
        stages=(
            _s(
                "The version that looks right. Two counters, one per thread, "
                "sixteen bytes apart.",
                "struct Shared {\n    atomic<long long> a{0};\n"
                "    atomic<long long> b{0};\n};",
            ),
            _s(
                "The fix is one keyword. alignas forces each onto its own "
                "line, so the struct grows to 128 bytes.",
                "struct Padded {\n"
                "    alignas(CACHE_LINE) atomic<long long> a{0};\n"
                "    alignas(CACHE_LINE) atomic<long long> b{0};\n};",
            ),
            _s(
                "Both count correctly — this is not a correctness bug, which "
                "is exactly why it survives review. Only the clock knows.",
                "template <typename Pair>\nvoid hammer(Pair& pair, int rounds);",
            ),
            _s(
                "The trade is real: 16 bytes becomes 128. Pad the things two "
                "threads write to, and nothing else, or you spend the memory "
                "bandwidth you were trying to save.",
                "",
            ),
        ),
    ),
    9403: Worked(
        problem=9403,
        naive=(
            "Loop over columns on the outside and rows inside. It reads "
            "naturally and touches every element exactly once."
        ),
        why_not=(
            "Consecutive iterations are a whole row apart in memory, so every "
            "access is a different cache line. You fetch 64 bytes to use 4, "
            "and throw away the rest before coming back for it later."
        ),
        insight=(
            "The array is laid out one row after another. Walking along a row "
            "uses every byte of each line fetched; walking down a column uses "
            "one sixteenth of it."
        ),
        stages=(
            _s(
                "Row-major means index r * cols + c. Adjacent c is adjacent "
                "memory.",
                "total += grid[r * cols + c];",
            ),
            _s(
                "So put c on the inside and consecutive reads are "
                "consecutive addresses — and the prefetcher can see it "
                "coming.",
                "for (size_t r = 0; r < rows; r++) {\n"
                "    for (size_t c = 0; c < cols; c++) {\n"
                "        total += grid[r * cols + c];\n    }\n}",
            ),
            _s(
                "Swapping the loops changes nothing about the work and "
                "everything about the cost.",
                "for (size_t c = 0; c < cols; c++) {\n"
                "    for (size_t r = 0; r < rows; r++) {\n"
                "        total += grid[r * cols + c];\n    }\n}",
            ),
            _s(
                "Both give the same total, which is why this is not caught by "
                "a test. It is caught by knowing the layout.",
                "",
            ),
        ),
    ),
    9404: Worked(
        problem=9404,
        naive=(
            "Declare the fields in whatever order reads best."
        ),
        why_not=(
            "Each field is placed at a multiple of its own alignment, so a "
            "char before a double wastes seven bytes. Interleave small and "
            "large fields and a struct can be half padding — memory you fetch "
            "and never use."
        ),
        insight=(
            "C and C++ never reorder fields, so the size is decided by the "
            "order you wrote. Largest to smallest packs them with almost no "
            "gaps."
        ),
        stages=(
            _s(
                "The natural order, and the expensive one: char, double, "
                "char, int.",
                "struct Loose {\n    char flag;\n    double value;\n"
                "    char other;\n    int count;\n};",
            ),
            _s(
                "The same fields, largest first. Same data, smaller object.",
                "struct Tight {\n    double value;\n    int count;\n"
                "    char flag;\n    char other;\n};",
            ),
            _s(
                "The difference is bytes you were fetching for nothing.",
                "inline size_t wasted_bytes() {\n"
                "    return sizeof(Loose) - sizeof(Tight);\n}",
            ),
            _s(
                "And the reason it matters: how many fit in a line decides "
                "how many lines an array of them touches.",
                "inline size_t per_cache_line(size_t object_size) {\n"
                "    return object_size ? CACHE_LINE / object_size : 0;\n}",
            ),
        ),
    ),
    9405: Worked(
        problem=9405,
        naive=(
            "One struct per thing, in an array. That is what an object is."
        ),
        why_not=(
            "If you only read one field, every fetched line arrives mostly "
            "full of fields you did not want. Summing the mass of particles "
            "with four doubles each means three quarters of the bandwidth is "
            "wasted."
        ),
        insight=(
            "Group by FIELD rather than by object. Then a pass over one field "
            "reads only that field, and every byte fetched is one you asked "
            "for."
        ),
        stages=(
            _s(
                "Array of structs: fields of one object together.",
                "struct Particle {\n    double x;\n    double y;\n"
                "    double z;\n    double mass;\n};",
            ),
            _s(
                "Struct of arrays: values of one field together.",
                "struct Particles {\n    vector<double> x;\n"
                "    vector<double> y;\n    vector<double> z;\n"
                "    vector<double> mass;\n};",
            ),
            _s(
                "Summing the mass now touches a quarter of the memory, and "
                "vectorises, because the values are contiguous.",
                "inline double total_mass(const Particles& items) {\n"
                "    double total = 0;\n    for (double m : items.mass) {\n"
                "        total += m;\n    }\n    return total;\n}",
            ),
            _s(
                "It is not free: if you use every field of one object at a "
                "time, array-of-structs wins, because those fields are then "
                "on one line rather than four.",
                "",
            ),
        ),
    ),
    9406: Worked(
        problem=9406,
        naive=(
            "Use a linked list. Insertion is constant time and you never have "
            "to reallocate."
        ),
        why_not=(
            "Reaching node n means loading node n-1 first, so the processor "
            "cannot start the next fetch until the current one lands. A "
            "hundred-nanosecond miss per node, with no overlap, and the "
            "prefetcher cannot help because the address does not exist yet."
        ),
        insight=(
            "The processor can prefetch what it can predict. An array's next "
            "address is arithmetic; a list's next address is a load. That "
            "dependency is the whole cost."
        ),
        stages=(
            _s(
                "The list walk. Every iteration waits on the previous load.",
                "inline long long walk_links(Link* head) {\n"
                "    long long total = 0;\n    while (head) {\n"
                "        total += head->value;\n        head = head->next;\n"
                "    }\n    return total;\n}",
            ),
            _s(
                "And the reason it is slow is the layout, not the loop: each "
                "node came from its own allocation, so consecutive nodes can "
                "be anywhere. Building them in one array makes the list "
                "itself much faster, which is the tell.",
                "vector<Link> nodes(count);\n"
                "for (size_t i = 0; i + 1 < count; i++) {\n"
                "    nodes[i].next = &nodes[i + 1];\n}",
            ),
            _s(
                "The array walk. Same additions, and the addresses are known "
                "in advance, so the loads overlap.",
                "inline long long walk_array(const vector<int>& items) {\n"
                "    long long total = 0;\n    for (int value : items) {\n"
                "        total += value;\n    }\n    return total;\n}",
            ),
            _s(
                "Same O(n), same answer. The constant is a factor of ten or "
                "more once the data leaves cache — which is why 'linked list "
                "for O(1) insert' is so often the wrong trade.",
                "",
            ),
        ),
    ),
    9407: Worked(
        problem=9407,
        naive=(
            "Write the condition. A branch is one instruction."
        ),
        why_not=(
            "It is one instruction when the processor guesses right. When it "
            "cannot — a condition that is true half the time at random — it "
            "throws away fifteen to twenty cycles of speculative work every "
            "time it is wrong."
        ),
        insight=(
            "You can remove the branch entirely by turning the condition into "
            "arithmetic. A mask of all ones or all zeros, ANDed with the "
            "value, adds it or does not."
        ),
        stages=(
            _s(
                "The branch. Fine when it is predictable.",
                "for (int value : items) {\n"
                "    if (value >= threshold) {\n        total += value;\n"
                "    }\n}",
            ),
            _s(
                "Negating a bool gives all-ones or all-zeros, which is "
                "exactly the mask you want.",
                "long long mask = -(long long)(value >= threshold);",
            ),
            _s(
                "AND it in and add unconditionally. Same answer, no branch to "
                "mispredict.",
                "total += value & mask;",
            ),
            _s(
                "And the twist worth knowing: branchless is SLOWER when the "
                "branch predicts well, because you always pay for the "
                "arithmetic. Sorting the data first can beat both.",
                "",
            ),
        ),
    ),
    9408: Worked(
        problem=9408,
        naive=(
            "Two loops: read along the rows of the source, write down the "
            "columns of the destination."
        ),
        why_not=(
            "One side is always walking columns. The reads are sequential and "
            "the writes stride by a whole row, so every write is a different "
            "line — and for a large matrix, that line is evicted before you "
            "come back to it."
        ),
        insight=(
            "Do it a tile at a time. A small enough tile has both its source "
            "rows and its destination rows in cache at once, so each line is "
            "fetched once and fully used before it leaves."
        ),
        stages=(
            _s(
                "The straightforward version, and the one that misses.",
                "for (size_t r = 0; r < n; r++) {\n"
                "    for (size_t c = 0; c < n; c++) {\n"
                "        dst[c * n + r] = src[r * n + c];\n    }\n}",
            ),
            _s(
                "Add two outer loops that step by a block, so the work is cut "
                "into squares.",
                "for (size_t r0 = 0; r0 < n; r0 += block) {\n"
                "    for (size_t c0 = 0; c0 < n; c0 += block) {",
            ),
            _s(
                "Clamp the ends, so a block size that does not divide n still "
                "works. Forgetting this is the usual bug.",
                "        size_t r_end = r0 + block < n ? r0 + block : n;\n"
                "        size_t c_end = c0 + block < n ? c0 + block : n;",
            ),
            _s(
                "Then the same inner loops, over the tile rather than the "
                "whole matrix.",
                "        for (size_t r = r0; r < r_end; r++) {\n"
                "            for (size_t c = c0; c < c_end; c++) {\n"
                "                dst[c * n + r] = src[r * n + c];\n"
                "            }\n        }",
            ),
            _s(
                "Pick the block so a tile of each matrix fits in L1 — around "
                "8 to 32 for ints. Too big and it misses anyway; too small "
                "and the loop overhead dominates.",
                "",
            ),
        ),
    ),
    # ── Market data and matching ────────────────────────────
    9501: Worked(
        problem=9501,
        naive=(
            "Store the price as a double. It is a decimal number, and double "
            "is the decimal type."
        ),
        why_not=(
            "Binary floating point cannot represent 0.1, so prices are "
            "approximations from the moment they are parsed. Add a hundred of "
            "them and the total is wrong in the last place — which is a "
            "reconciliation break, and the first anyone knows is a report "
            "that does not balance."
        ),
        insight=(
            "A price is not a real number; it is a whole number of ticks. "
            "Store the count of ticks as an integer and every operation is "
            "exact."
        ),
        stages=(
            _s(
                "One integer. The scale says where the point is.",
                "class Price {\npublic:\n"
                "    static constexpr long long SCALE = 10000;\n\n"
                "private:\n    long long ticks;\n};",
            ),
            _s(
                "Converting in rounds explicitly. Adding a half before "
                "truncating is the rounding, and it has to go the other way "
                "for negatives.",
                "static Price from_double(double value) {\n"
                "    double scaled = value * (double)SCALE;\n"
                "    long long rounded =\n"
                "        (long long)(scaled < 0 ? scaled - 0.5 : scaled + 0.5);\n"
                "    return Price(rounded);\n}",
            ),
            _s(
                "Addition and subtraction are now integer operations, so "
                "0.1 + 0.2 really is 0.3.",
                "Price operator+(const Price& other) const {\n"
                "    return Price(ticks + other.ticks);\n}",
            ),
            _s(
                "And comparison is exact, so == means what it says — which is "
                "the thing you can never write against a double.",
                "bool operator==(const Price& other) const {\n"
                "    return ticks == other.ticks;\n}",
            ),
            _s(
                "The care moves to multiplication and division, where you now "
                "choose the rounding yourself instead of having it chosen "
                "for you.",
                "",
            ),
        ),
    ),
    9502: Worked(
        problem=9502,
        naive=(
            "Keep a list of the orders resting at each price."
        ),
        why_not=(
            "Almost everything the book is asked — the best price, the "
            "quantity there, the spread — needs only the total. Walking a "
            "list to add it up on every quote is work you do millions of "
            "times a second for an answer you could have kept."
        ),
        insight=(
            "Aggregate on the way in. Keep the total, and only care about "
            "individual orders when something actually trades."
        ),
        stages=(
            _s(
                "A price, a total, and how many orders make it up.",
                "struct Level {\n    Price price;\n    long long quantity;\n"
                "    int orders;\n};",
            ),
            _s(
                "Adding is arithmetic rather than an insertion.",
                "void add(long long q) {\n    quantity += q;\n    orders++;\n}",
            ),
            _s(
                "Removing clamps at zero. A cancel for more than is there is "
                "a bad message, not a negative quantity.",
                "void remove(long long q) {\n"
                "    quantity -= q < quantity ? q : quantity;\n"
                "    if (orders > 0) {\n        orders--;\n    }\n}",
            ),
            _s(
                "What this gives up: you cannot answer 'whose order is "
                "first'. A real book keeps the queue too, because price-time "
                "priority is exactly that question.",
                "bool empty() const { return quantity <= 0; }",
            ),
        ),
    ),
    9503: Worked(
        problem=9503,
        naive=(
            "Keep the levels in a list and sort it whenever you need the best "
            "price."
        ),
        why_not=(
            "The best price is read on every single message and the book "
            "changes on every single message, so you sort constantly. It is "
            "n log n for an answer that could be a single array read."
        ),
        insight=(
            "Insert in order instead. Then the best is always index zero, and "
            "reading it — the thing you do most — costs nothing."
        ),
        stages=(
            _s(
                "Two sides, sorted opposite ways, so the front is the best of "
                "each.",
                "vector<Level> bids;  // descending\n"
                "vector<Level> asks;  // ascending",
            ),
            _s(
                "Insertion walks to the right spot. Same price joins the "
                "level rather than making a new one — that check must come "
                "first.",
                "for (size_t i = 0; i < side.size(); i++) {\n"
                "    if (side[i].price == price) {\n"
                "        side[i].add(quantity);\n        return;\n    }",
            ),
            _s(
                "Otherwise find where it belongs. The comparison flips "
                "between the two sides, which is the only difference between "
                "them.",
                "    bool before = descending ? side[i].price < price\n"
                "                             : price < side[i].price;\n"
                "    if (before) {\n"
                "        side.insert(side.begin() + i, Level(price, quantity));\n"
                "        return;\n    }\n}",
            ),
            _s(
                "And now the questions are free.",
                "long long spread_ticks() const {\n"
                "    if (bids.empty() || asks.empty()) {\n        return -1;\n"
                "    }\n    return asks.front().price.raw() -\n"
                "           bids.front().price.raw();\n}",
            ),
            _s(
                "Crossed means the best bid is at or above the best ask — "
                "somebody is willing to pay what somebody else will sell for, "
                "so a trade should happen.",
                "bool crossed() const {\n"
                "    return !bids.empty() && !asks.empty() &&\n"
                "           !(bids.front().price < asks.front().price);\n}",
            ),
        ),
    ),
    9504: Worked(
        problem=9504,
        naive=(
            "Find the cheapest ask that can fill the whole order, and trade "
            "there."
        ),
        why_not=(
            "One level often has less than you want. Refusing to trade "
            "because no single level is big enough is not how a market works "
            "— you take the best price, then the next, until you are done."
        ),
        insight=(
            "Walk outward from the best price, taking whatever is at each "
            "level, and stop on two conditions: filled, or the price is no "
            "longer acceptable."
        ),
        stages=(
            _s(
                "Loop while you still want something and there is still a "
                "book.",
                "while (wanted > 0 && !book.asks.empty()) {\n"
                "    Level& best = book.asks.front();",
            ),
            _s(
                "The limit is the other stop. Past it you would rather not "
                "trade at all — which is what a limit order means.",
                "    if (limit < best.price) {\n        break;\n    }",
            ),
            _s(
                "Take the smaller of what you want and what is there.",
                "    long long taken = wanted < best.quantity ? wanted\n"
                "                                             : best.quantity;\n"
                "    fills.push_back(Fill{best.price, taken});\n"
                "    best.quantity -= taken;\n    wanted -= taken;",
            ),
            _s(
                "An emptied level goes, so the next iteration's front is the "
                "next best price. Leaving it would loop forever on a level "
                "with nothing in it.",
                "    if (best.empty()) {\n"
                "        book.asks.erase(book.asks.begin());\n    }\n}",
            ),
            _s(
                "Returning the fills rather than a single price is the point: "
                "a large order gets several, at worsening prices, and that "
                "spread is the market impact.",
                "",
            ),
        ),
    ),
    9505: Worked(
        problem=9505,
        naive=(
            "Keep a running average and update it with each new trade's "
            "price."
        ),
        why_not=(
            "That weights a one-lot trade the same as a ten-thousand-lot "
            "trade. You cannot average averages and get a weighted answer — "
            "the size has to be in the arithmetic, not applied afterwards."
        ),
        insight=(
            "Carry the two totals the answer is made of: the notional and the "
            "volume. The average is their quotient, computed when asked."
        ),
        stages=(
            _s(
                "Two running sums, not an average.",
                "long long notional = 0;\nlong long volume = 0;",
            ),
            _s(
                "Each trade contributes price times quantity to one and "
                "quantity to the other.",
                "void add(Price price, long long quantity) {\n"
                "    notional += price.raw() * quantity;\n"
                "    volume += quantity;\n}",
            ),
            _s(
                "The answer is the division, and it is only meaningful once "
                "something has traded.",
                "bool value(Price& out) const {\n    if (volume == 0) {\n"
                "        return false;\n    }\n"
                "    out = Price(notional / volume);\n    return true;\n}",
            ),
            _s(
                "Watch the width: price times quantity overflows a 32-bit "
                "integer quickly, and on a busy day it will find the edge of "
                "a 64-bit one too.",
                "",
            ),
        ),
    ),
    9506: Worked(
        problem=9506,
        naive=(
            "Keep a list, append to the end, and remove from the front when "
            "it is too long."
        ),
        why_not=(
            "Removing from the front shifts everything, so each update is "
            "linear in the window. And re-summing to get the mean makes it "
            "linear again — twice the work for an answer you could maintain."
        ),
        insight=(
            "The slots do not have to move; the position can. Wrap an index "
            "round a fixed array, and carry the sum so the mean is a "
            "division."
        ),
        stages=(
            _s(
                "Fixed storage, a write position, and the running sum.",
                "vector<long long> slots;\nsize_t next;\nsize_t filled;\n"
                "long long running;",
            ),
            _s(
                "Once full, the slot about to be overwritten leaves the sum. "
                "This is the step the naive version does by re-adding "
                "everything.",
                "if (filled == slots.size()) {\n"
                "    running -= slots[next];\n} else {\n    filled++;\n}",
            ),
            _s(
                "Then write and advance, wrapping round.",
                "slots[next] = value;\nrunning += value;\n"
                "next = (next + 1) % slots.size();",
            ),
            _s(
                "The mean is now O(1). The maximum is not — that still needs "
                "a scan, and keeping it incrementally requires a monotonic "
                "deque.",
                "bool mean(double& out) const {\n    if (filled == 0) {\n"
                "        return false;\n    }\n"
                "    out = (double)running / (double)filled;\n    return true;\n}",
            ),
        ),
    ),
    9507: Worked(
        problem=9507,
        naive=(
            "Keep every latency sample, sort them, and index at the "
            "percentile you want."
        ),
        why_not=(
            "At a million samples a second you are storing eight megabytes "
            "every second and sorting it to answer one question. The "
            "measurement becomes more expensive than the thing measured, "
            "which changes what you are measuring."
        ),
        insight=(
            "You never needed the samples, only the distribution. Count how "
            "many fell in each bucket on the way in, and the percentile is a "
            "scan over a handful of counters."
        ),
        stages=(
            _s(
                "Counters, not samples. Fixed memory whatever the volume.",
                "vector<long long> counts;\nlong long bucket_width;\n"
                "long long total;",
            ),
            _s(
                "Recording is a division and an increment. Anything past the "
                "last bucket lands in it rather than out of bounds.",
                "void record(long long nanos) {\n"
                "    size_t at = (size_t)(nanos / bucket_width);\n"
                "    if (at >= counts.size()) {\n"
                "        at = counts.size() - 1;\n    }\n"
                "    counts[at]++;\n    total++;\n}",
            ),
            _s(
                "The percentile walks the buckets accumulating until it "
                "passes the target.",
                "long long wanted = (long long)(fraction * (double)total);\n"
                "long long seen = 0;\nfor (size_t i = 0; i < counts.size(); i++) {\n"
                "    seen += counts[i];\n    if (seen > wanted) {\n"
                "        return (long long)(i + 1) * bucket_width;\n    }\n}",
            ),
            _s(
                "The answer is the bucket's upper edge, so the resolution IS "
                "the bucket width. Real ones widen the buckets "
                "logarithmically — HdrHistogram — so the relative error stays "
                "bounded from microseconds to seconds.",
                "",
            ),
        ),
    ),
    9508: Worked(
        problem=9508,
        naive=(
            "Split on commas into strings, then parse each piece."
        ),
        why_not=(
            "Every split allocates, and on a feed the allocator's tail "
            "latency becomes your tail latency. You also copy bytes you "
            "already have in a buffer, to look at them and throw the copy "
            "away."
        ),
        insight=(
            "The bytes are already in front of you. Walk them once with an "
            "index, building the values as you go, and never make a second "
            "copy of anything."
        ),
        stages=(
            _s(
                "A fixed symbol field rather than a string, so the whole tick "
                "is one flat struct with no ownership.",
                "struct Tick {\n    char symbol[8];\n    Price price;\n"
                "    long long quantity;\n    bool valid;\n};",
            ),
            _s(
                "Copy the symbol out until the comma, bounded by the field so "
                "a long symbol cannot overrun it.",
                "while (at < length && line[at] != ',' &&\n"
                "       wrote + 1 < sizeof(tick.symbol)) {\n"
                "    tick.symbol[wrote++] = line[at++];\n}",
            ),
            _s(
                "The whole part is the usual digit accumulation.",
                "long long whole = 0;\n"
                "while (at < length && line[at] >= '0' && line[at] <= '9') {\n"
                "    whole = whole * 10 + (line[at++] - '0');\n}",
            ),
            _s(
                "The fraction is the interesting half: divide the scale as "
                "you go, so each digit contributes at the right place and you "
                "never touch a float.",
                "if (at < length && line[at] == '.') {\n    at++;\n"
                "    while (at < length && line[at] >= '0' &&\n"
                "           line[at] <= '9' && scale > 1) {\n"
                "        scale /= 10;\n"
                "        frac += (line[at++] - '0') * scale;\n    }\n}",
            ),
            _s(
                "And only set valid at the very end, so a truncated message "
                "returns something that says so rather than something "
                "half-filled.",
                "tick.price = Price(whole * Price::SCALE + frac);\n"
                "tick.quantity = quantity;\ntick.valid = true;",
            ),
        ),
    ),
}


# The problem a class opens with — the one that teaches the family rather
# than a variation on it.
CANONICAL: dict[str, int] = {
    "sys-memory": 9101,
    "sys-concurrency": 9201,
    "sys-lockfree": 9301,
    "sys-cache": 9401,
    "sys-market": 9501,
}


def worked_for_problem(number: int | None) -> Worked | None:
    if number is None:
        return None
    return WORKED.get(number)


def worked_for(pattern_id: str | None) -> Worked | None:
    if pattern_id is None:
        return None
    return WORKED.get(CANONICAL.get(pattern_id, -1))
