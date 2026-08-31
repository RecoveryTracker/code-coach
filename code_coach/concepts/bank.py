"""The concept questions themselves.

Grouped by what they are really about rather than by difficulty. The answers
are the version you would say in a room: the mechanism first, then the number
or the consequence that shows you have actually met it.
"""

from __future__ import annotations

from code_coach.concepts import Topic, _q

_CPP = Topic(
    id="cpp-semantics",
    name="C++ Semantics",
    order=1,
    blurb="What the language is doing behind the syntax, and where it stops helping.",
    questions=(
        _q(
            "What is the rule of five?",
            "If you write any one of destructor, copy constructor, copy "
            "assignment, move constructor or move assignment, you almost "
            "certainly need to think about all five — because writing one "
            "means the class owns a resource, and the compiler's defaults for "
            "the others will get that wrong. The rule of zero is better where "
            "you can reach it: hold members that manage themselves and write "
            "none of the five.",
            "Why does declaring a destructor suppress the implicit move?",
        ),
        _q(
            "What does std::move actually do?",
            "Nothing at runtime. It is a cast to an rvalue reference, which "
            "tells overload resolution to pick the move overload. The moving "
            "is done by that constructor or assignment operator, not by move "
            "itself — and a moved-from object is left valid but unspecified, "
            "so you may destroy or assign to it and not much else.",
            "What is left in a moved-from std::vector, and is that guaranteed?",
        ),
        _q(
            "Why does a base class need a virtual destructor?",
            "Deleting a derived object through a base pointer is undefined "
            "behaviour unless the base destructor is virtual. Without it the "
            "derived destructor never runs, so the derived members leak. If a "
            "class is meant to be inherited from and deleted polymorphically, "
            "the destructor is virtual; if it is not meant to be deleted that "
            "way, making it protected says so.",
            "What does virtual cost you, in size and in speed?",
        ),
        _q(
            "How is a virtual call dispatched?",
            "Each object with virtual functions carries a pointer to its "
            "class's vtable, and a virtual call loads that pointer, indexes "
            "the table, and calls through it. So the cost is one extra load "
            "and an indirect branch — usually cheap, but it cannot be inlined, "
            "which is often the bigger loss.",
            "When can the compiler devirtualise a call?",
        ),
        _q(
            "What is the difference between a reference and a pointer?",
            "A reference must be bound when it is created and cannot be "
            "rebound; a pointer can be null and can be reseated. In "
            "generated code they are usually the same thing. The real "
            "difference is what they promise the reader: a reference says "
            "there is definitely an object here.",
        ),
        _q(
            "What is undefined behaviour, and why is it worse than a crash?",
            "It is behaviour the standard does not define, so the compiler is "
            "allowed to assume it never happens — and it optimises on that "
            "assumption. That is why UB does not reliably crash: signed "
            "overflow, reading an uninitialised value or a null dereference "
            "can each make the compiler delete a check you wrote, and the "
            "symptom appears somewhere else entirely.",
            "Why can signed overflow make a loop bound disappear?",
        ),
        _q(
            "What does RAII mean in one sentence?",
            "Tie a resource's lifetime to an object's lifetime, so releasing "
            "it is the destructor's job and happens on every exit path, "
            "including an exception. It is the reason well-written C++ has "
            "almost no cleanup code in it.",
        ),
        _q(
            "When is a copy elided?",
            "Returning a prvalue is guaranteed not to copy since C++17 — the "
            "object is constructed directly in the caller's storage. Named "
            "return value optimisation, where you return a local by name, is "
            "permitted but not guaranteed. Writing std::move on a return "
            "statement usually makes it worse, because it turns a prvalue "
            "into an xvalue and blocks the guaranteed elision.",
        ),
        _q(
            "What is the difference between std::vector's size and capacity?",
            "Size is how many elements there are; capacity is how many it has "
            "room for before it must reallocate. push_back past capacity "
            "allocates a bigger block, moves everything across, and "
            "invalidates every pointer, reference and iterator into it. "
            "reserve up front is how you avoid paying that repeatedly.",
            "What does shrink_to_fit actually guarantee?",
        ),
        _q(
            "Why is std::vector<bool> unusual?",
            "It is specialised to pack bits, so it is not a container of bool "
            "in the normal sense: operator[] returns a proxy object rather "
            "than a bool&, and you cannot take a pointer into it. If you want "
            "a container of bools that behaves, use std::vector<char> or "
            "std::deque<bool>.",
        ),
        _q(
            "What does noexcept buy you?",
            "It lets the compiler skip unwinding machinery, and — more "
            "usefully — it changes what the standard library will do. "
            "vector's reallocation moves elements only if the move "
            "constructor is noexcept; otherwise it copies, to keep the strong "
            "exception guarantee. So a missing noexcept on a move constructor "
            "silently turns your moves into copies.",
        ),
        _q(
            "What is the small string optimisation?",
            "std::string keeps short strings inside the object itself rather "
            "than on the heap — typically up to fifteen characters on a "
            "64-bit implementation. So a short string costs no allocation, "
            "and a string that grows past the threshold suddenly does.",
        ),
    ),
)


_OS = Topic(
    id="os-internals",
    name="OS Internals",
    order=2,
    blurb="Processes, memory, and what the kernel is doing while your code waits.",
    questions=(
        _q(
            "What is the difference between a process and a thread?",
            "A process owns an address space; threads share one. So threads "
            "communicate by touching the same memory and processes have to go "
            "through the kernel, and a thread crashing usually takes the whole "
            "process with it while a process crashing does not.",
            "What is actually saved on a context switch between the two?",
        ),
        _q(
            "What happens on a page fault?",
            "The processor finds no valid mapping for the address and traps "
            "into the kernel. A minor fault is resolved from something already "
            "in memory — a page cache hit, or a copy-on-write page needing a "
            "copy — and costs microseconds. A major fault has to read from "
            "disk and costs milliseconds, which is the difference between "
            "slow and catastrophic.",
            "What makes a fault major rather than minor?",
        ),
        _q(
            "What is virtual memory for?",
            "Three things: isolation, so processes cannot see each other; "
            "the illusion of contiguity, so a program can have a flat address "
            "space over scattered physical pages; and overcommit, so a "
            "process can reserve more than exists and only pay when it "
            "touches it.",
        ),
        _q(
            "What does the TLB do?",
            "It caches virtual-to-physical translations, so a memory access "
            "does not have to walk the page tables every time. A TLB miss "
            "costs a page walk, which is several dependent memory accesses. "
            "This is why huge pages help a large working set: they cover the "
            "same memory with far fewer entries.",
        ),
        _q(
            "What does a context switch cost?",
            "Directly, a few microseconds to save and restore registers and "
            "switch page tables. Indirectly, much more: the new thread starts "
            "with a cold cache and a cold TLB, so the first thousands of "
            "accesses are slow. The indirect cost is usually the one that "
            "matters.",
        ),
        _q(
            "What is the difference between a system call and a function call?",
            "A system call crosses into the kernel: it traps, switches "
            "privilege level and stack, and returns. That is hundreds of "
            "nanoseconds rather than a few, which is why hot paths batch "
            "their syscalls and why kernel bypass exists at all.",
        ),
        _q(
            "What is copy-on-write?",
            "Two mappings share the same physical pages read-only, and the "
            "first write traps and makes a private copy. It is why fork is "
            "cheap even for a large process, and why a forked child touching "
            "a lot of memory suddenly is not.",
        ),
        _q(
            "What does mmap give you over read?",
            "The file becomes memory, so access is a load rather than a "
            "syscall, and the page cache is the buffer — no copy into your "
            "own. In exchange you get page faults instead of predictable "
            "read latency, and errors arrive as signals rather than return "
            "values.",
        ),
        _q(
            "What is the difference between blocking, non-blocking and "
            "asynchronous I/O?",
            "Blocking waits for the data. Non-blocking returns immediately "
            "with 'not ready' and you come back — usually via epoll or "
            "kqueue telling you when. Asynchronous hands the kernel a buffer "
            "and it completes the whole operation and tells you, which is "
            "what io_uring and IOCP do.",
        ),
        _q(
            "How does the scheduler decide who runs?",
            "On Linux, CFS picks whichever runnable thread has had the least "
            "weighted CPU time, so it is fair rather than priority-driven. "
            "Real-time policies bypass that entirely and run to completion or "
            "until preempted by something higher. For latency work the "
            "relevant knobs are affinity, isolation and priority, not "
            "yielding.",
        ),
        _q(
            "Why does pinning a thread to a core help latency?",
            "It stops the scheduler migrating you, which would throw away "
            "your L1 and L2 cache and your TLB entries. Combined with keeping "
            "other work off that core, it makes the tail predictable — which "
            "for latency work matters more than the mean.",
        ),
        _q(
            "What is a zombie process?",
            "One that has exited but whose parent has not reaped its exit "
            "status, so the kernel keeps the entry. It costs a process table "
            "slot and nothing else. The fix is for the parent to wait, or to "
            "ignore SIGCHLD so the kernel reaps automatically.",
        ),
    ),
)


_CPU = Topic(
    id="cpu-memory",
    name="CPU & Memory Hierarchy",
    order=3,
    blurb="Why the same instruction count runs at wildly different speeds.",
    questions=(
        _q(
            "What are the rough latencies of the memory hierarchy?",
            "Register is free. L1 is about four cycles, L2 about twelve, L3 "
            "about forty, and main memory two to three hundred — call it a "
            "hundred nanoseconds. An SSD is tens of microseconds and a spinning "
            "disk is milliseconds. The shape matters more than the exact "
            "numbers: each level is roughly an order of magnitude worse.",
            "How many cycles of work can you do while waiting on main memory?",
        ),
        _q(
            "What is a cache line, and why does the size matter?",
            "Sixty-four bytes on essentially every current x86 and ARM. It is "
            "the unit of transfer, so reading one byte costs the same as "
            "reading the whole line — which is why walking an array is fast "
            "and pointer chasing is not, and why two threads writing to the "
            "same line fight over it.",
        ),
        _q(
            "What is false sharing?",
            "Two threads writing to different variables that happen to sit on "
            "the same cache line. Nothing is logically shared, but the line "
            "ping-pongs between cores and both threads stall. The fix is "
            "padding each to its own line, at the cost of the bytes.",
            "How would you detect it without reading the source?",
        ),
        _q(
            "What does a branch misprediction cost?",
            "Fifteen to twenty cycles on a modern deep pipeline, because "
            "everything speculatively executed has to be thrown away. A "
            "well-predicted branch is nearly free, which is why sorting data "
            "before a branchy loop can make it several times faster without "
            "changing the work done.",
        ),
        _q(
            "When is branchless code faster?",
            "When the branch is unpredictable. A conditional move or an "
            "arithmetic mask has a fixed cost with no misprediction, so it "
            "wins on random data and loses on predictable data, where the "
            "predictor was already right and free.",
        ),
        _q(
            "What is the difference between latency and throughput for an "
            "instruction?",
            "Latency is how long before the result is usable; throughput is "
            "how many can be started per cycle. A multiply might have five "
            "cycles of latency and one per cycle of throughput, so a chain of "
            "dependent multiplies runs five times slower than independent "
            "ones — which is why unrolling and breaking dependency chains "
            "helps.",
        ),
        _q(
            "What does the prefetcher do, and how do you help it?",
            "It spots access patterns — sequential and fixed-stride — and "
            "pulls lines in before you ask. You help it by being predictable: "
            "walk arrays forwards, keep strides small and constant, and "
            "prefer contiguous layouts. It cannot follow pointers, which is "
            "the whole problem with a linked list.",
        ),
        _q(
            "What is NUMA, and when does it bite?",
            "On a multi-socket machine each socket has memory that is closer "
            "to it. Accessing another socket's memory costs perhaps twice as "
            "much. It bites when a thread is allocated memory on one node and "
            "then scheduled on another — which is why you pin threads and "
            "allocate locally.",
        ),
        _q(
            "What is the difference between structure of arrays and array of "
            "structures?",
            "Array of structures keeps each object's fields together; "
            "structure of arrays keeps each field's values together. If you "
            "iterate reading one field, SoA touches only the lines you need "
            "while AoS drags the other fields along. If you use every field of "
            "one object at a time, AoS wins.",
        ),
        _q(
            "Why can alignment matter for correctness, not just speed?",
            "Some instructions require it — an aligned SIMD load will fault on "
            "an unaligned address — and on some architectures any unaligned "
            "access traps. On x86 unaligned scalar access is merely slower, "
            "and slower still when it straddles a cache line.",
        ),
        _q(
            "What is a store buffer, and what does it have to do with memory "
            "ordering?",
            "Stores are buffered before reaching cache so the core does not "
            "stall. That means your own stores can become visible to you "
            "before they are visible to others, which is exactly the "
            "reordering a memory fence exists to constrain. It is why the "
            "store-load case is the one x86 does not give you for free.",
        ),
        _q(
            "How would you find out whether a loop is memory-bound or "
            "compute-bound?",
            "Measure. Look at instructions per cycle and cache miss rates "
            "with perf or VTune: low IPC with high miss rates is memory-bound, "
            "high IPC is compute-bound. Failing that, halve the data and see "
            "whether the time halves — if it does not, you were waiting on "
            "memory.",
        ),
    ),
)


_CONCURRENCY = Topic(
    id="concurrency",
    name="Concurrency",
    order=4,
    blurb="Races, orderings, and the difference between a lock and no lock.",
    questions=(
        _q(
            "What exactly is a data race?",
            "Two threads accessing the same memory, at least one of them "
            "writing, with no synchronisation ordering them. In C++ and Rust "
            "that is undefined behaviour, not merely a wrong answer — the "
            "compiler is allowed to assume it does not happen.",
            "How is a data race different from a race condition?",
        ),
        _q(
            "What is the difference between a mutex and a spinlock?",
            "A mutex sleeps when it cannot acquire, handing the core to "
            "someone else; a spinlock burns the core waiting. Spinning wins "
            "when the wait is shorter than a context switch — tens of "
            "nanoseconds — and loses badly when it is not, especially if the "
            "holder gets descheduled.",
        ),
        _q(
            "What are the four conditions for deadlock?",
            "Mutual exclusion, hold-and-wait, no preemption, and circular "
            "wait. Break any one and you cannot deadlock. In practice the "
            "cheapest to break is circular wait: take locks in a fixed global "
            "order.",
        ),
        _q(
            "What do acquire and release actually mean?",
            "A release store guarantees everything you wrote before it is "
            "visible to anyone who does an acquire load that sees that store. "
            "They come in pairs — an acquire with no matching release "
            "guarantees nothing. That pairing is how you publish data with a "
            "flag and know the data is really there.",
            "Why is relaxed enough for a reference count increment but not a "
            "decrement?",
        ),
        _q(
            "When is relaxed ordering enough?",
            "When you only need the operation to be atomic and do not care "
            "what else is visible around it. A statistics counter is the "
            "classic case: the total must be exact, but nothing else depends "
            "on when it became visible.",
        ),
        _q(
            "What does lock-free actually guarantee?",
            "That some thread makes progress, always — so the system cannot "
            "stall because one thread was descheduled holding something. It "
            "does not promise every thread makes progress, which is "
            "wait-free, and it does not promise it is faster.",
        ),
        _q(
            "What is the ABA problem?",
            "A compare-and-swap sees the value it expected, but the value got "
            "there by changing to something else and back, so the world moved "
            "underneath it. It bites lock-free stacks when a node is freed "
            "and reallocated. The fixes are a tag counter alongside the "
            "pointer, or not reclaiming until it is safe — hazard pointers or "
            "epochs.",
        ),
        _q(
            "Why is reclaiming memory the hard part of a lock-free structure?",
            "Because another thread may still be reading the node you want to "
            "free, and there is no lock to tell you it has finished. That is "
            "what hazard pointers, epoch-based reclamation and RCU all exist "
            "to solve, and it is why toy lock-free stacks leak.",
        ),
        _q(
            "What is a condition variable for, and why the loop?",
            "To wait for a predicate without spinning. The loop is because of "
            "spurious wakeups and because another thread may have taken the "
            "thing between the signal and your waking — so you re-check the "
            "predicate rather than trusting the wakeup.",
        ),
        _q(
            "Why does the mutex have to be held while checking the predicate?",
            "Otherwise the predicate can change between your check and your "
            "wait, and the notification lands before you are waiting — a lost "
            "wakeup, and you sleep forever. The condition variable releases "
            "the mutex atomically as it waits, which closes that window.",
        ),
        _q(
            "What is priority inversion?",
            "A low-priority thread holds a lock a high-priority thread wants, "
            "and a medium-priority thread preempts the low one — so the "
            "high-priority thread waits on the medium one. Priority "
            "inheritance fixes it by temporarily raising the holder.",
        ),
        _q(
            "Why is x86 a comparatively forgiving memory model?",
            "It is total store order: loads are not reordered with loads, "
            "stores are not reordered with stores, and stores are not "
            "reordered with earlier loads. Only the store-load case is "
            "reordered. ARM and POWER reorder much more, which is why code "
            "that happens to work on x86 fails there.",
        ),
    ),
)


_NETWORKING = Topic(
    id="networking",
    name="Networking & Latency",
    order=5,
    blurb="Where the microseconds go between two machines.",
    questions=(
        _q(
            "When would you choose UDP over TCP?",
            "When you would rather have the newest data than all of it. "
            "Market data multicast is the standard example: a retransmitted "
            "quote from 200 milliseconds ago is worthless, and TCP's "
            "in-order guarantee means one lost packet stalls everything "
            "behind it — head-of-line blocking.",
        ),
        _q(
            "What is Nagle's algorithm, and why is it turned off?",
            "It holds small writes until the previous data is acknowledged, "
            "to avoid flooding the network with tiny packets. For anything "
            "latency-sensitive that is a delay of up to a round trip for no "
            "benefit, so you set TCP_NODELAY. It interacts especially badly "
            "with delayed ACK.",
        ),
        _q(
            "What is head-of-line blocking?",
            "One lost or slow item holding up everything queued behind it, "
            "even though those are fine. TCP has it because it delivers in "
            "order; HTTP/1.1 had it per connection; QUIC exists partly to "
            "avoid it by keeping streams independent.",
        ),
        _q(
            "What does the TCP three-way handshake cost you?",
            "A full round trip before any data moves, and another for TLS "
            "unless you use session resumption or TLS 1.3's zero round trip. "
            "Over a 30ms link that is 60 to 90 milliseconds before the first "
            "byte, which is why connection reuse matters so much.",
        ),
        _q(
            "What is kernel bypass, and what does it buy?",
            "Talking to the network card from user space — DPDK, Solarflare's "
            "onload, RDMA — so a packet does not cross into the kernel or get "
            "copied. It turns single-digit microseconds of stack into "
            "hundreds of nanoseconds, at the cost of doing everything "
            "yourself and usually burning a core polling.",
        ),
        _q(
            "Why is polling used instead of interrupts on a latency-critical "
            "path?",
            "An interrupt costs a context switch and arrives when the kernel "
            "gets round to it; a busy poll sees the packet the moment it "
            "lands. You pay a whole core for it, which is a trade you only "
            "make when the microseconds are worth more than the core.",
        ),
        _q(
            "What is the difference between bandwidth and latency, and which "
            "can you buy?",
            "Bandwidth is how much per second; latency is how long for the "
            "first bit. You can buy bandwidth — add links. You cannot buy "
            "much latency, because a large part of it is the speed of light "
            "in fibre, about 5 microseconds per kilometre. That is why "
            "colocation exists.",
        ),
        _q(
            "What is a jumbo frame and when does it help?",
            "An MTU of around 9000 bytes rather than 1500, so fewer packets "
            "and fewer per-packet costs for bulk transfer. It does nothing "
            "for small-message latency, and it breaks if anything in the path "
            "does not agree.",
        ),
        _q(
            "How would you measure network latency honestly?",
            "Round trip at the application, at high percentiles, under the "
            "load you actually run at. Means hide everything that matters; "
            "the 99th and 99.9th are where the pain is. Hardware timestamps "
            "at the card remove your own stack from the measurement.",
        ),
        _q(
            "What is multicast, and why does market data use it?",
            "One sender, many receivers, with the network doing the "
            "duplication rather than the sender. A feed goes out once and "
            "every subscriber sees it at the same time, which is both "
            "efficient and fair — nobody is later because they are further "
            "down a list.",
        ),
        _q(
            "What causes bufferbloat?",
            "Oversized buffers in the path filling up, so packets are queued "
            "rather than dropped. Throughput looks fine and latency collapses, "
            "because TCP only backs off when it sees loss. Active queue "
            "management — CoDel, fq_codel — drops early to keep the queue "
            "short.",
        ),
        _q(
            "What does TCP_QUICKACK do, and when would you want it?",
            "It disables delayed acknowledgement, which normally waits up to "
            "40 milliseconds hoping to piggyback the ACK on outgoing data. "
            "On a request-response path with nothing to piggyback on, that "
            "delay is pure latency.",
        ),
    ),
)


TOPICS: tuple[Topic, ...] = (
    _CPP,
    _OS,
    _CPU,
    _CONCURRENCY,
    _NETWORKING,
)
