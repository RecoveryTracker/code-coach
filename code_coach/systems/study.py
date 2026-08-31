"""What to read while you are typing a systems implementation.

Two kinds of reading, matching the LeetCode side. A pattern lesson says what
the family is for and where it goes wrong; a brief says what this particular
primitive has to do, in the way a specification would rather than the way the
finished code does.

These are deliberately not LeetCode problems, so a brief carries no URL —
there is nowhere to send you. The place to check your answer is the standard
library's own version, and where that differs from ours the brief says how.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PatternLesson:
    """The reading that makes a family of primitives make sense."""

    summary: str
    when: str
    template: str
    steps: tuple[str, ...] = ()
    pitfalls: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Brief:
    """What this primitive has to do, and what the real one also does."""

    statement: str
    note: str = ""
    examples: tuple[str, ...] = ()


LESSONS: dict[str, PatternLesson] = {
    "sys-memory": PatternLesson(
        summary=(
            "Every resource has exactly one owner, and the owner's lifetime "
            "decides when it is released. Write that down as a type and the "
            "cleanup stops being something you can forget."
        ),
        when=(
            "Anything acquired that must be given back: memory, a file, a "
            "lock, a socket. If you can ask 'who frees this?', this is the "
            "family."
        ),
        template=(
            "acquire in the constructor\n"
            "release in the destructor\n"
            "decide what a copy means — forbid it, share it, or duplicate it\n"
            "make a move leave the source safe to destroy"
        ),
        steps=(
            "Name the resource and its one owner.",
            "Release it in the destructor, so every exit path frees it.",
            "Decide whether copying is even meaningful; forbid it if not.",
            "If it is shared, put the count beside the object, not in it.",
            "Leave a moved-from object valid — destroying it must be safe.",
        ),
        pitfalls=(
            "A raw pointer member with no rule of five is a double free "
            "waiting for someone to copy the object.",
            "Forgetting that an exception is an exit path too. That is the "
            "whole reason the destructor does the work.",
            "Counting references without making the count atomic, then "
            "sharing across threads.",
        ),
    ),
    "sys-concurrency": PatternLesson(
        summary=(
            "A lock is a promise that only one thread is inside at a time. "
            "Everything else in this family is that promise with different "
            "trade-offs about who waits, how, and for how long."
        ),
        when=(
            "Two threads touch the same state and at least one writes. That "
            "is a data race, and no amount of care about ordering the "
            "statements fixes it."
        ),
        template=(
            "state the invariant the lock protects\n"
            "acquire, do the smallest possible amount, release\n"
            "wait on a condition in a LOOP, never an if\n"
            "release on every path, including the exceptional one"
        ),
        steps=(
            "Write down what must be true when nobody holds the lock.",
            "Make the critical section as short as it can be.",
            "If waiting, wait on a predicate — and re-check it on waking.",
            "Decide whether to spin or sleep by how long the wait is.",
            "Take multiple locks in one fixed order, everywhere.",
        ),
        pitfalls=(
            "Waiting with an if instead of a while. A wakeup does not "
            "promise the predicate is true.",
            "Checking the predicate outside the lock, so a notification "
            "lands in the gap and is lost.",
            "Spinning on a lock whose holder may be descheduled — you burn "
            "a core waiting for a thread that is not running.",
        ),
    ),
    "sys-lockfree": PatternLesson(
        summary=(
            "No lock at all: a single atomic operation moves the structure "
            "from one consistent state to the next, and a thread that loses "
            "the race retries. The hard part is not the algorithm, it is "
            "knowing when it is safe to free anything."
        ),
        when=(
            "A hot path where even an uncontended lock is too much, or where "
            "a thread being descheduled while holding a lock would be "
            "unacceptable."
        ),
        template=(
            "read the current state\n"
            "compute the next state from it\n"
            "compare-and-swap it in; if it failed, start again\n"
            "pair every release with an acquire, or the data is not published"
        ),
        steps=(
            "Find the single word whose change commits the whole update.",
            "Loop: read, compute, compare-and-swap, retry on failure.",
            "Use the failed exchange's result rather than re-reading.",
            "Pair release stores with acquire loads to publish the payload.",
            "Decide who frees a node, and when it is provably unreachable.",
        ),
        pitfalls=(
            "Assuming atomic means ordered. It does not — relaxed operations "
            "are atomic and say nothing about anything else.",
            "Freeing a node another thread may still be reading. This is the "
            "whole reason hazard pointers and epochs exist.",
            "The ABA problem: the value you expected is back, but the world "
            "moved and came back while you were not looking.",
        ),
    ),
    "sys-cache": PatternLesson(
        summary=(
            "The algorithm is already right and it is still slow. Memory "
            "moves in 64-byte lines, the processor guesses branches, and "
            "layout decides how much of what you fetch you actually use."
        ),
        when=(
            "The complexity says it should be fast and the clock disagrees, "
            "or two threads got slower rather than faster."
        ),
        template=(
            "count the cache lines the work touches, not the operations\n"
            "walk memory in the order it is laid out\n"
            "put the fields you use together, together\n"
            "measure — every claim here is checkable"
        ),
        steps=(
            "Work out how many bytes of each fetched line you actually use.",
            "Reorder the traversal to match the layout, or the layout to "
            "match the traversal.",
            "Split hot fields from cold ones if you only read some of them.",
            "Pad anything two threads write to onto separate lines.",
            "Measure before and after — the guesses here are often wrong.",
        ),
        pitfalls=(
            "Optimising a branch that was already predicted perfectly. "
            "Branchless is slower when the predictor was right.",
            "Padding everything. It costs memory, and memory is the thing "
            "you were trying to save.",
            "Trusting a microbenchmark whose working set fits in L1 when "
            "the real one does not.",
        ),
    ),
    "sys-market": PatternLesson(
        summary=(
            "The pieces a trading system is made of. Prices are exact "
            "integers, the book is sorted so the best price is free to read, "
            "and nothing on the hot path allocates."
        ),
        when=(
            "Anything handling prices, quantities, or a feed — and anywhere "
            "somebody is going to ask what the 99th percentile latency is."
        ),
        template=(
            "represent money as an integer number of ticks\n"
            "keep each side of the book sorted on insert\n"
            "carry running totals rather than recomputing\n"
            "parse in place; on a feed the allocator is the latency"
        ),
        steps=(
            "Pick the tick size and store prices as integers of it.",
            "Keep bids descending and asks ascending, so the best is index 0.",
            "Aggregate a level to a total; you only need the orders when "
            "something trades.",
            "For statistics, carry the running sums the answer needs.",
            "For latency, bucket on the way in rather than keeping samples.",
        ),
        pitfalls=(
            "A double for a price. It is exact until it is not, and the "
            "first time you notice is a reconciliation break.",
            "Averaging averages. VWAP needs the two running totals.",
            "Allocating in the parse path, which puts the allocator's tail "
            "latency into your feed handler's.",
        ),
    ),
}


BRIEFS: dict[int, Brief] = {
    # ── Ownership and RAII ──────────────────────────────────
    9101: Brief(
        "Write a type that owns one heap allocation: it frees on destruction, "
        "cannot be copied, and can be moved so that the source is left empty.",
        note="The real unique_ptr also takes a custom deleter and specialises "
        "for arrays.",
    ),
    9102: Brief(
        "Write a shared owner: copies share one object and one count, and the "
        "last one to go frees it.",
        note="The real shared_ptr's count is atomic, supports weak_ptr, and "
        "make_shared puts the count and the object in one allocation.",
    ),
    9103: Brief(
        "Write a type holding either a value or nothing, without allocating "
        "and without requiring the value to be default-constructible.",
        note="The real optional also has monadic operations and constexpr "
        "support.",
    ),
    9104: Brief(
        "Write something that runs an action when it goes out of scope, "
        "whatever the exit path, and can be told not to.",
    ),
    9105: Brief(
        "Write an allocator that hands out memory by bumping a pointer and "
        "frees everything at once. Honour alignment; refuse when full.",
        note="Real arenas chain blocks rather than failing, and often keep a "
        "list of destructors to run at reset.",
    ),
    9106: Brief(
        "Write a container that keeps its first few elements inside itself "
        "and only allocates once it outgrows them.",
    ),
    9107: Brief(
        "Put the reference count inside the object rather than beside it, so "
        "the pointer stays one word and there is no second allocation.",
    ),
    9108: Brief(
        "Write a slot that can hold a T without constructing one until asked, "
        "and destroys it when told. This is what a vector does between "
        "reserve and push_back.",
    ),
    # ── Concurrency ─────────────────────────────────────────
    9201: Brief(
        "Write a lock that spins rather than sleeping. Add try_lock, and be "
        "clear about which memory ordering each operation needs.",
        note="A production spinlock also emits a pause instruction and backs "
        "off, because spinning flat out starves the holder.",
    ),
    9202: Brief(
        "Write a lock that serves threads in the order they arrived, so no "
        "thread can be starved by luckier ones.",
    ),
    9203: Brief(
        "Write a counting semaphore whose waiters sleep rather than spin.",
    ),
    9204: Brief(
        "Write a lock allowing many readers or one writer, and make sure a "
        "steady stream of readers cannot starve a waiting writer.",
    ),
    9205: Brief(
        "Write a barrier that releases all n threads only once all n have "
        "arrived, and that can be used more than once.",
    ),
    9206: Brief(
        "Make an action run exactly once however many threads ask, with the "
        "others waiting rather than proceeding past a half-built thing.",
    ),
    9207: Brief(
        "Write a bounded queue where consumers wait when it is empty and "
        "producers wait when it is full.",
    ),
    9208: Brief(
        "Write a pool of worker threads that take jobs from a queue, and that "
        "finishes its queue before shutting down.",
    ),
    # ── Lock-free ───────────────────────────────────────────
    9301: Brief(
        "Increment a counter from several threads two ways — relaxed and "
        "sequentially consistent — and be able to say what differs.",
        note="The totals are identical. What differs is what else is "
        "guaranteed visible around the increment.",
    ),
    9302: Brief(
        "Keep the maximum value ever offered, from any number of threads, "
        "without a lock.",
    ),
    9303: Brief(
        "Write a fixed-capacity queue for exactly one producer and one "
        "consumer, with no lock and no waiting on either side.",
        note="One producer and one consumer is what makes this simple; the "
        "multi-producer version needs considerably more care.",
    ),
    9304: Brief(
        "Write a lock-free stack: push and pop by swapping the head with "
        "compare-and-swap.",
        note="Ours leaks on purpose. Freeing a popped node safely is the hard "
        "half and needs hazard pointers or epoch reclamation.",
    ),
    9305: Brief(
        "Let a writer update a value without ever waiting, and readers detect "
        "that they read it mid-update and try again.",
        note="Only sound for a payload you can copy freely — the reader may "
        "read a torn value before discarding it.",
    ),
    9306: Brief(
        "Publish a payload to another thread using a flag, so that a reader "
        "seeing the flag is guaranteed to see the payload.",
    ),
    9307: Brief(
        "Take a spinlock and stop it starving the thread it is waiting for.",
    ),
    9308: Brief(
        "Write a reference count safe across threads, and be able to justify "
        "the memory ordering on the increment and the decrement separately.",
    ),
    # ── Cache ───────────────────────────────────────────────
    9401: Brief(
        "Write down the cache line size and two helpers: whether two "
        "addresses share a line, and how many lines a size spans.",
    ),
    9402: Brief(
        "Show two counters written by two threads, once sharing a cache line "
        "and once padded apart, and be able to say why the second is faster.",
    ),
    9403: Brief(
        "Sum a two-dimensional array both ways round and be able to say why "
        "one is far faster despite identical work.",
    ),
    9404: Brief(
        "Show that the order of a struct's fields changes its size, and work "
        "out how many of each fit in a cache line.",
    ),
    9405: Brief(
        "Hold the same data as an array of structs and as a struct of arrays, "
        "and say which is better for reading one field of many.",
    ),
    9406: Brief(
        "Sum the same values through a linked list and through an array, and "
        "say why the list cannot be prefetched.",
    ),
    9407: Brief(
        "Sum the values over a threshold with a branch and without one, and "
        "say when each is faster.",
    ),
    9408: Brief(
        "Transpose a square matrix a tile at a time rather than straight "
        "through, and say which cache misses that avoids.",
    ),
    # ── Market data ─────────────────────────────────────────
    9501: Brief(
        "Represent a price exactly. Support construction from a decimal, "
        "addition, subtraction and comparison.",
        note="Real systems also carry the instrument's tick size and reject "
        "prices that are not a multiple of it.",
    ),
    9502: Brief(
        "Represent everything resting at one price as a total rather than a "
        "list of orders.",
    ),
    9503: Brief(
        "Keep both sides of a book sorted so the best price is free to read, "
        "and answer the spread and whether the book is crossed.",
        note="A real book also tracks order ids so a cancel can find its "
        "order, which is what makes the data structure interesting.",
    ),
    9504: Brief(
        "Match an aggressive buy against the book: take from the best price "
        "outward, stop at the limit or when filled, and report the fills.",
    ),
    9505: Brief(
        "Compute the volume-weighted average price of a stream of trades.",
    ),
    9506: Brief(
        "Keep the last n values with a running sum, without shifting anything "
        "or allocating after construction.",
    ),
    9507: Brief(
        "Answer percentile questions about latency without keeping every "
        "sample.",
        note="Real ones use exponentially widening buckets — HdrHistogram is "
        "the standard — so the relative error is bounded across the range.",
    ),
    9508: Brief(
        "Parse a comma-separated tick into a symbol, an exact price and a "
        "quantity, without allocating.",
    ),
}


def lesson_for(pattern_id: str | None) -> PatternLesson | None:
    if pattern_id is None:
        return None
    return LESSONS.get(pattern_id)


def brief_for(number: int | None) -> Brief | None:
    if number is None:
        return None
    return BRIEFS.get(number)
