"""
Systems and low-level implementations, in Rust.

Deliberately not a translation of the C++ bank. The C++ versions teach you
what a smart pointer is doing; the Rust versions teach you what the borrow
checker was doing for you, by making you turn it off. `UnsafeCell`, `Drop`,
`Send` and `Sync` are the whole curriculum here, and they have no C++
equivalent worth pretending about.

Every solution compiles and runs under the app's own runner, edition 2021.
"""

from __future__ import annotations

from code_coach.leetcode.problems import Pattern
from code_coach.leetcode.rust_common import _p

# Numbered to match the C++ bank's classes, and still clear of anything
# LeetCode uses.
CELL = "use std::cell::Cell;\nuse std::cell::RefCell;\nuse std::cell::UnsafeCell;"
PTR = "use std::ptr::NonNull;"
MEM = "use std::mem;"
OPS = "use std::ops::Deref;\nuse std::ops::DerefMut;"
ATOMIC = (
    "use std::sync::atomic::AtomicBool;\n"
    "use std::sync::atomic::AtomicPtr;\n"
    "use std::sync::atomic::AtomicUsize;\n"
    "use std::sync::atomic::AtomicU64;\n"
    "use std::sync::atomic::Ordering;"
)
SYNC = "use std::sync::Arc;\nuse std::sync::Mutex;\nuse std::sync::Condvar;"
THREAD = "use std::thread;\nuse std::sync::mpsc;"
COLLECTIONS = "use std::collections::VecDeque;"
ATOMIC_U64 = "use std::sync::atomic::AtomicU64;"


# ── 1. Ownership and RAII ───────────────────────────────────

_MEMORY = Pattern(
    id="sys-memory",
    name="Ownership & RAII",
    order=101,
    blurb="Turn the borrow checker off for a moment and you find out what it was doing.",
    tell="Anything about who owns this, when it drops, and why Rust said no.",
    preamble=(CELL, PTR, MEM, OPS),
    problems=(
        _p(
            9101, "MyBox", "Medium",
            "A heap allocation you own. Deref is what makes *b work and why "
            "&MyBox<T> coerces to &T; Drop is what makes it not leak.",
            "O(1) everything, one word",
            """
            pub struct MyBox<T> {
                ptr: NonNull<T>,
            }

            impl<T> MyBox<T> {
                pub fn new(value: T) -> Self {
                    let boxed = Box::new(value);
                    let ptr = NonNull::new(Box::into_raw(boxed)).unwrap();
                    MyBox { ptr }
                }

                pub fn into_inner(self) -> T {
                    let ptr = self.ptr;
                    mem::forget(self);
                    unsafe { *Box::from_raw(ptr.as_ptr()) }
                }
            }

            impl<T> Deref for MyBox<T> {
                type Target = T;
                fn deref(&self) -> &T {
                    unsafe { self.ptr.as_ref() }
                }
            }

            impl<T> DerefMut for MyBox<T> {
                fn deref_mut(&mut self) -> &mut T {
                    unsafe { self.ptr.as_mut() }
                }
            }

            impl<T> Drop for MyBox<T> {
                fn drop(&mut self) {
                    unsafe {
                        drop(Box::from_raw(self.ptr.as_ptr()));
                    }
                }
            }
            """,
        ),
        _p(
            9102, "MyRc", "Hard",
            "A shared owner with a Cell count. Cell and not an atomic is "
            "exactly why Rc is not Send — two threads would race the count.",
            "O(1) clone, one allocation for the whole group",
            """
            struct RcInner<T> {
                count: Cell<usize>,
                value: T,
            }

            pub struct MyRc<T> {
                inner: NonNull<RcInner<T>>,
            }

            impl<T> MyRc<T> {
                pub fn new(value: T) -> Self {
                    let inner = Box::new(RcInner {
                        count: Cell::new(1),
                        value,
                    });
                    MyRc {
                        inner: NonNull::new(Box::into_raw(inner)).unwrap(),
                    }
                }

                pub fn strong_count(&self) -> usize {
                    unsafe { self.inner.as_ref().count.get() }
                }
            }

            impl<T> Clone for MyRc<T> {
                fn clone(&self) -> Self {
                    let inner = unsafe { self.inner.as_ref() };
                    inner.count.set(inner.count.get() + 1);
                    MyRc { inner: self.inner }
                }
            }

            impl<T> Deref for MyRc<T> {
                type Target = T;
                fn deref(&self) -> &T {
                    unsafe { &self.inner.as_ref().value }
                }
            }

            impl<T> Drop for MyRc<T> {
                fn drop(&mut self) {
                    let inner = unsafe { self.inner.as_ref() };
                    let left = inner.count.get() - 1;
                    inner.count.set(left);
                    if left == 0 {
                        unsafe {
                            drop(Box::from_raw(self.inner.as_ptr()));
                        }
                    }
                }
            }
            """,
        ),
        _p(
            9103, "Borrow Flag", "Medium",
            "What RefCell actually holds: one number saying how it is "
            "borrowed. This is the check the compiler does for free elsewhere, "
            "moved to runtime.",
            "O(1), and it panics instead of failing to compile",
            """
            const UNBORROWED: isize = 0;
            const WRITING: isize = -1;

            pub struct BorrowFlag {
                state: Cell<isize>,
            }

            impl BorrowFlag {
                pub fn new() -> Self {
                    BorrowFlag {
                        state: Cell::new(UNBORROWED),
                    }
                }

                pub fn try_read(&self) -> bool {
                    let now = self.state.get();
                    if now == WRITING {
                        return false;
                    }
                    self.state.set(now + 1);
                    true
                }

                pub fn try_write(&self) -> bool {
                    if self.state.get() != UNBORROWED {
                        return false;
                    }
                    self.state.set(WRITING);
                    true
                }

                pub fn release_read(&self) {
                    self.state.set(self.state.get() - 1);
                }

                pub fn release_write(&self) {
                    self.state.set(UNBORROWED);
                }

                pub fn readers(&self) -> isize {
                    let now = self.state.get();
                    if now > 0 {
                        now
                    } else {
                        0
                    }
                }
            }
            """,
        ),
        _p(
            9104, "ScopeGuard", "Easy",
            "Drop is the whole of RAII in Rust. Cancelling means forgetting it "
            "so the destructor never runs.",
            "O(1)",
            """
            pub struct ScopeGuard<F: FnMut()> {
                action: F,
                live: bool,
            }

            impl<F: FnMut()> ScopeGuard<F> {
                pub fn new(action: F) -> Self {
                    ScopeGuard { action, live: true }
                }

                pub fn dismiss(&mut self) {
                    self.live = false;
                }
            }

            impl<F: FnMut()> Drop for ScopeGuard<F> {
                fn drop(&mut self) {
                    if self.live {
                        (self.action)();
                    }
                }
            }
            """,
        ),
        _p(
            9105, "Index Arena", "Medium",
            "Rust's answer to a graph. Store the nodes in a Vec and refer to "
            "them by index, and the borrow checker stops being the problem — "
            "an index is not a borrow.",
            "O(1) push, O(1) lookup",
            """
            pub struct Arena<T> {
                items: Vec<T>,
            }

            #[derive(Copy, Clone, PartialEq, Eq, Debug)]
            pub struct Id(usize);

            impl<T> Arena<T> {
                pub fn new() -> Self {
                    Arena { items: Vec::new() }
                }

                pub fn add(&mut self, value: T) -> Id {
                    self.items.push(value);
                    Id(self.items.len() - 1)
                }

                pub fn get(&self, id: Id) -> Option<&T> {
                    self.items.get(id.0)
                }

                pub fn get_mut(&mut self, id: Id) -> Option<&mut T> {
                    self.items.get_mut(id.0)
                }

                pub fn len(&self) -> usize {
                    self.items.len()
                }

                pub fn is_empty(&self) -> bool {
                    self.items.is_empty()
                }
            }
            """,
        ),
        _p(
            9106, "SmallVec", "Medium",
            "An enum, not a pointer trick. Small stays on the stack, and the "
            "spill to the heap is a variant change the compiler checks.",
            "O(1) amortised push, no allocation while small",
            """
            pub enum SmallVec<T> {
                Inline { items: [Option<T>; 4], len: usize },
                Spilled(Vec<T>),
            }

            impl<T: Clone> SmallVec<T> {
                pub fn new() -> Self {
                    SmallVec::Inline {
                        items: [None, None, None, None],
                        len: 0,
                    }
                }

                pub fn push(&mut self, value: T) {
                    match self {
                        SmallVec::Spilled(items) => items.push(value),
                        SmallVec::Inline { items, len } => {
                            if *len < 4 {
                                items[*len] = Some(value);
                                *len += 1;
                            } else {
                                let mut spilled: Vec<T> = items
                                    .iter()
                                    .filter_map(|slot| slot.clone())
                                    .collect();
                                spilled.push(value);
                                *self = SmallVec::Spilled(spilled);
                            }
                        }
                    }
                }

                pub fn len(&self) -> usize {
                    match self {
                        SmallVec::Inline { len, .. } => *len,
                        SmallVec::Spilled(items) => items.len(),
                    }
                }

                pub fn on_heap(&self) -> bool {
                    matches!(self, SmallVec::Spilled(_))
                }
            }
            """,
        ),
        _p(
            9107, "Drop Order", "Medium",
            "Locals drop in reverse order of declaration; struct fields drop "
            "in the order they are written. Knowing which is which is what "
            "makes a guard release before the thing it guards.",
            "O(1), and it decides correctness",
            """
            pub struct Recorder {
                pub order: RefCell<Vec<&'static str>>,
            }

            pub struct Noisy<'a> {
                name: &'static str,
                log: &'a Recorder,
            }

            impl<'a> Noisy<'a> {
                pub fn new(name: &'static str, log: &'a Recorder) -> Self {
                    Noisy { name, log }
                }
            }

            impl<'a> Drop for Noisy<'a> {
                fn drop(&mut self) {
                    self.log.order.borrow_mut().push(self.name);
                }
            }

            pub struct Pair<'a> {
                pub first: Noisy<'a>,
                pub second: Noisy<'a>,
            }
            """,
        ),
        _p(
            9108, "Taking Without Cloning", "Medium",
            "You cannot move a field out of &mut self, but you can swap "
            "something in its place. mem::take leaves the default behind.",
            "O(1), and no clone",
            """
            pub struct Buffer {
                items: Vec<i32>,
            }

            impl Buffer {
                pub fn new(items: Vec<i32>) -> Self {
                    Buffer { items }
                }

                pub fn drain(&mut self) -> Vec<i32> {
                    mem::take(&mut self.items)
                }

                pub fn swap_in(&mut self, fresh: Vec<i32>) -> Vec<i32> {
                    mem::replace(&mut self.items, fresh)
                }

                pub fn len(&self) -> usize {
                    self.items.len()
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
    blurb="Atomics, orderings, and the unsafe you need to promise it is sound.",
    tell="A hot path where even an uncontended lock is too much.",
    preamble=(ATOMIC, CELL, SYNC, THREAD),
    problems=(
        _p(
            9301, "Relaxed vs Sequential Counter", "Medium",
            "Both totals are exact — atomicity is not ordering. Relaxed only "
            "gives up the promise about what else you see around it.",
            "O(1) per increment, relaxed is cheaper",
            """
            pub struct Counter {
                value: AtomicUsize,
            }

            impl Counter {
                pub fn new() -> Self {
                    Counter {
                        value: AtomicUsize::new(0),
                    }
                }

                pub fn bump_relaxed(&self) {
                    self.value.fetch_add(1, Ordering::Relaxed);
                }

                pub fn bump_ordered(&self) {
                    self.value.fetch_add(1, Ordering::SeqCst);
                }

                pub fn get(&self) -> usize {
                    self.value.load(Ordering::Relaxed)
                }
            }
            """,
        ),
        _p(
            9302, "CAS Loop", "Medium",
            "compare_exchange_weak can fail for no reason, so it lives in a "
            "loop — and the Err gives you back the value that beat you.",
            "O(1) uncontended, retries under contention",
            """
            pub struct AtomicMax {
                best: AtomicUsize,
            }

            impl AtomicMax {
                pub fn new() -> Self {
                    AtomicMax {
                        best: AtomicUsize::new(0),
                    }
                }

                pub fn offer(&self, candidate: usize) {
                    let mut seen = self.best.load(Ordering::Relaxed);
                    while candidate > seen {
                        match self.best.compare_exchange_weak(
                            seen,
                            candidate,
                            Ordering::Release,
                            Ordering::Relaxed,
                        ) {
                            Ok(_) => return,
                            Err(actual) => seen = actual,
                        }
                    }
                }

                pub fn get(&self) -> usize {
                    self.best.load(Ordering::Acquire)
                }
            }
            """,
        ),
        _p(
            9303, "Spin Lock", "Hard",
            "UnsafeCell is what lets you hand out &mut from &self, and the "
            "unsafe impl Sync is you promising the lock makes that sound.",
            "O(1) uncontended",
            """
            pub struct SpinLock<T> {
                taken: AtomicBool,
                value: UnsafeCell<T>,
            }

            unsafe impl<T: Send> Sync for SpinLock<T> {}

            impl<T> SpinLock<T> {
                pub fn new(value: T) -> Self {
                    SpinLock {
                        taken: AtomicBool::new(false),
                        value: UnsafeCell::new(value),
                    }
                }

                pub fn with<R>(&self, action: impl FnOnce(&mut T) -> R) -> R {
                    while self
                        .taken
                        .compare_exchange_weak(
                            false,
                            true,
                            Ordering::Acquire,
                            Ordering::Relaxed,
                        )
                        .is_err()
                    {
                        std::hint::spin_loop();
                    }
                    let out = action(unsafe { &mut *self.value.get() });
                    self.taken.store(false, Ordering::Release);
                    out
                }
            }
            """,
        ),
        _p(
            9304, "Treiber Stack", "Hard",
            "AtomicPtr and a CAS on the head. It leaks on purpose: reclaiming "
            "a popped node safely needs hazard pointers or epochs, and that is "
            "the hard half.",
            "O(1) uncontended",
            """
            struct Node<T> {
                value: T,
                next: *mut Node<T>,
            }

            pub struct TreiberStack<T> {
                head: AtomicPtr<Node<T>>,
            }

            unsafe impl<T: Send> Sync for TreiberStack<T> {}
            unsafe impl<T: Send> Send for TreiberStack<T> {}

            impl<T> TreiberStack<T> {
                pub fn new() -> Self {
                    TreiberStack {
                        head: AtomicPtr::new(std::ptr::null_mut()),
                    }
                }

                pub fn push(&self, value: T) {
                    let fresh = Box::into_raw(Box::new(Node {
                        value,
                        next: std::ptr::null_mut(),
                    }));
                    loop {
                        let head = self.head.load(Ordering::Relaxed);
                        unsafe {
                            (*fresh).next = head;
                        }
                        if self
                            .head
                            .compare_exchange_weak(
                                head,
                                fresh,
                                Ordering::Release,
                                Ordering::Relaxed,
                            )
                            .is_ok()
                        {
                            return;
                        }
                    }
                }

                pub fn pop(&self) -> Option<T> {
                    loop {
                        let head = self.head.load(Ordering::Acquire);
                        if head.is_null() {
                            return None;
                        }
                        let next = unsafe { (*head).next };
                        if self
                            .head
                            .compare_exchange_weak(
                                head,
                                next,
                                Ordering::Acquire,
                                Ordering::Relaxed,
                            )
                            .is_ok()
                        {
                            return Some(unsafe { std::ptr::read(&(*head).value) });
                        }
                    }
                }
            }
            """,
        ),
        _p(
            9305, "SPSC Ring Buffer", "Hard",
            "One producer, one consumer, no lock. The release on the write "
            "index pairs with the acquire on the read, and that pairing is the "
            "entire safety argument.",
            "O(1) per item, wait-free both sides",
            """
            pub struct SpscQueue<T> {
                slots: UnsafeCell<Vec<Option<T>>>,
                capacity: usize,
                write: AtomicUsize,
                read: AtomicUsize,
            }

            unsafe impl<T: Send> Sync for SpscQueue<T> {}

            impl<T> SpscQueue<T> {
                pub fn new(capacity: usize) -> Self {
                    let mut slots = Vec::with_capacity(capacity);
                    for _ in 0..capacity {
                        slots.push(None);
                    }
                    SpscQueue {
                        slots: UnsafeCell::new(slots),
                        capacity,
                        write: AtomicUsize::new(0),
                        read: AtomicUsize::new(0),
                    }
                }

                pub fn push(&self, value: T) -> bool {
                    let head = self.write.load(Ordering::Relaxed);
                    let next = (head + 1) % self.capacity;
                    if next == self.read.load(Ordering::Acquire) {
                        return false;
                    }
                    unsafe {
                        let slots = &mut *self.slots.get();
                        slots[head] = Some(value);
                    }
                    self.write.store(next, Ordering::Release);
                    true
                }

                pub fn pop(&self) -> Option<T> {
                    let tail = self.read.load(Ordering::Relaxed);
                    if tail == self.write.load(Ordering::Acquire) {
                        return None;
                    }
                    let value = unsafe {
                        let slots = &mut *self.slots.get();
                        slots[tail].take()
                    };
                    self.read.store((tail + 1) % self.capacity, Ordering::Release);
                    value
                }
            }
            """,
        ),
        _p(
            9306, "Acquire-Release Message Passing", "Medium",
            "The flag publishes the payload. A reader that sees the flag with "
            "Acquire must also see everything written before the Release.",
            "O(1), no lock",
            """
            pub struct Mailbox {
                payload: UnsafeCell<(i32, i32)>,
                ready: AtomicBool,
            }

            unsafe impl Sync for Mailbox {}

            impl Mailbox {
                pub fn new() -> Self {
                    Mailbox {
                        payload: UnsafeCell::new((0, 0)),
                        ready: AtomicBool::new(false),
                    }
                }

                pub fn publish(&self, a: i32, b: i32) {
                    unsafe {
                        *self.payload.get() = (a, b);
                    }
                    self.ready.store(true, Ordering::Release);
                }

                pub fn collect(&self) -> Option<(i32, i32)> {
                    if !self.ready.load(Ordering::Acquire) {
                        return None;
                    }
                    Some(unsafe { *self.payload.get() })
                }
            }
            """,
        ),
        _p(
            9307, "Once", "Medium",
            "Exactly one caller runs it, and the rest wait rather than sailing "
            "past a half-built thing.",
            "O(1) after the first call",
            """
            pub struct Once {
                done: AtomicBool,
                guard: Mutex<bool>,
            }

            impl Once {
                pub fn new() -> Self {
                    Once {
                        done: AtomicBool::new(false),
                        guard: Mutex::new(false),
                    }
                }

                pub fn call(&self, action: impl FnOnce()) {
                    if self.done.load(Ordering::Acquire) {
                        return;
                    }
                    let mut ran = self.guard.lock().unwrap();
                    if *ran {
                        return;
                    }
                    action();
                    *ran = true;
                    self.done.store(true, Ordering::Release);
                }

                pub fn finished(&self) -> bool {
                    self.done.load(Ordering::Acquire)
                }
            }
            """,
        ),
        _p(
            9308, "Atomic Reference Count", "Hard",
            "The increment can be Relaxed; the decrement cannot. Release on "
            "the way down and Acquire before cleaning up is what stops the "
            "drop racing another thread's last use.",
            "O(1) per clone",
            """
            pub struct AtomicRefCount {
                refs: AtomicUsize,
            }

            impl AtomicRefCount {
                pub fn new() -> Self {
                    AtomicRefCount {
                        refs: AtomicUsize::new(1),
                    }
                }

                pub fn acquire(&self) {
                    self.refs.fetch_add(1, Ordering::Relaxed);
                }

                pub fn release(&self) -> bool {
                    if self.refs.fetch_sub(1, Ordering::Release) != 1 {
                        return false;
                    }
                    std::sync::atomic::fence(Ordering::Acquire);
                    true
                }

                pub fn count(&self) -> usize {
                    self.refs.load(Ordering::Relaxed)
                }
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
    blurb="Guards, channels and scopes — Rust's answer to 'who is allowed to touch this'.",
    tell="Threads sharing anything, and the compiler asking who owns it.",
    preamble=(CELL, ATOMIC, SYNC, THREAD, COLLECTIONS, OPS),
    problems=(
        _p(
            9201, "Mutex Guard", "Hard",
            "The guard is the whole idea: locking hands back a value that "
            "unlocks when it drops. You cannot forget to unlock because there "
            "is no unlock to call.",
            "O(1) uncontended",
            """
            pub struct Lock<T> {
                taken: AtomicBool,
                value: UnsafeCell<T>,
            }

            unsafe impl<T: Send> Sync for Lock<T> {}

            pub struct Guard<'a, T> {
                lock: &'a Lock<T>,
            }

            impl<T> Lock<T> {
                pub fn new(value: T) -> Self {
                    Lock {
                        taken: AtomicBool::new(false),
                        value: UnsafeCell::new(value),
                    }
                }

                pub fn lock(&self) -> Guard<'_, T> {
                    while self
                        .taken
                        .compare_exchange_weak(
                            false,
                            true,
                            Ordering::Acquire,
                            Ordering::Relaxed,
                        )
                        .is_err()
                    {
                        std::hint::spin_loop();
                    }
                    Guard { lock: self }
                }
            }

            impl<'a, T> Deref for Guard<'a, T> {
                type Target = T;
                fn deref(&self) -> &T {
                    unsafe { &*self.lock.value.get() }
                }
            }

            impl<'a, T> DerefMut for Guard<'a, T> {
                fn deref_mut(&mut self) -> &mut T {
                    unsafe { &mut *self.lock.value.get() }
                }
            }

            impl<'a, T> Drop for Guard<'a, T> {
                fn drop(&mut self) {
                    self.lock.taken.store(false, Ordering::Release);
                }
            }
            """,
        ),
        _p(
            9202, "Semaphore", "Medium",
            "A count of permits. Waiters sleep on a Condvar rather than spin, "
            "which is the right trade when the wait might be long.",
            "O(1) per acquire",
            """
            pub struct Semaphore {
                permits: Mutex<usize>,
                ready: Condvar,
            }

            impl Semaphore {
                pub fn new(permits: usize) -> Self {
                    Semaphore {
                        permits: Mutex::new(permits),
                        ready: Condvar::new(),
                    }
                }

                pub fn acquire(&self) {
                    let mut left = self.permits.lock().unwrap();
                    while *left == 0 {
                        left = self.ready.wait(left).unwrap();
                    }
                    *left -= 1;
                }

                pub fn release(&self) {
                    let mut left = self.permits.lock().unwrap();
                    *left += 1;
                    drop(left);
                    self.ready.notify_one();
                }

                pub fn available(&self) -> usize {
                    *self.permits.lock().unwrap()
                }
            }
            """,
        ),
        _p(
            9203, "Reader-Writer Lock", "Hard",
            "Many readers or one writer. Letting waiting writers block new "
            "readers is what stops a steady stream of readers starving them.",
            "O(1) per acquire",
            """
            struct RwState {
                readers: usize,
                writing: bool,
                waiting_writers: usize,
            }

            pub struct RwLock {
                state: Mutex<RwState>,
                ready: Condvar,
            }

            impl RwLock {
                pub fn new() -> Self {
                    RwLock {
                        state: Mutex::new(RwState {
                            readers: 0,
                            writing: false,
                            waiting_writers: 0,
                        }),
                        ready: Condvar::new(),
                    }
                }

                pub fn read(&self) {
                    let mut state = self.state.lock().unwrap();
                    while state.writing || state.waiting_writers > 0 {
                        state = self.ready.wait(state).unwrap();
                    }
                    state.readers += 1;
                }

                pub fn read_done(&self) {
                    let mut state = self.state.lock().unwrap();
                    state.readers -= 1;
                    drop(state);
                    self.ready.notify_all();
                }

                pub fn write(&self) {
                    let mut state = self.state.lock().unwrap();
                    state.waiting_writers += 1;
                    while state.writing || state.readers > 0 {
                        state = self.ready.wait(state).unwrap();
                    }
                    state.waiting_writers -= 1;
                    state.writing = true;
                }

                pub fn write_done(&self) {
                    let mut state = self.state.lock().unwrap();
                    state.writing = false;
                    drop(state);
                    self.ready.notify_all();
                }

                pub fn readers_now(&self) -> usize {
                    self.state.lock().unwrap().readers
                }
            }
            """,
        ),
        _p(
            9204, "Barrier", "Medium",
            "Nobody leaves until everybody arrives. The generation counter is "
            "what stops a fast thread lapping the others and passing twice.",
            "O(1) per arrival",
            """
            struct BarrierState {
                waiting: usize,
                generation: usize,
            }

            pub struct Barrier {
                total: usize,
                state: Mutex<BarrierState>,
                ready: Condvar,
            }

            impl Barrier {
                pub fn new(total: usize) -> Self {
                    Barrier {
                        total,
                        state: Mutex::new(BarrierState {
                            waiting: 0,
                            generation: 0,
                        }),
                        ready: Condvar::new(),
                    }
                }

                pub fn wait(&self) {
                    let mut state = self.state.lock().unwrap();
                    let mine = state.generation;
                    state.waiting += 1;
                    if state.waiting == self.total {
                        state.waiting = 0;
                        state.generation += 1;
                        drop(state);
                        self.ready.notify_all();
                        return;
                    }
                    while state.generation == mine {
                        state = self.ready.wait(state).unwrap();
                    }
                }
            }
            """,
        ),
        _p(
            9205, "Channel", "Hard",
            "A queue plus a Condvar is the whole of an mpsc channel. Senders "
            "push and notify, the receiver waits on not-empty.",
            "O(1) per message",
            """
            pub struct Channel<T> {
                queue: Mutex<VecDeque<T>>,
                ready: Condvar,
            }

            impl<T> Channel<T> {
                pub fn new() -> Self {
                    Channel {
                        queue: Mutex::new(VecDeque::new()),
                        ready: Condvar::new(),
                    }
                }

                pub fn send(&self, value: T) {
                    self.queue.lock().unwrap().push_back(value);
                    self.ready.notify_one();
                }

                pub fn recv(&self) -> T {
                    let mut queue = self.queue.lock().unwrap();
                    loop {
                        if let Some(value) = queue.pop_front() {
                            return value;
                        }
                        queue = self.ready.wait(queue).unwrap();
                    }
                }

                pub fn try_recv(&self) -> Option<T> {
                    self.queue.lock().unwrap().pop_front()
                }
            }
            """,
        ),
        _p(
            9206, "Sharing Without Arc", "Medium",
            "Scoped threads borrow the stack instead of owning a copy. The "
            "scope guarantees they finish first, which is what makes the "
            "borrow sound.",
            "O(1), and no allocation to share",
            """
            pub fn sum_in_parallel(items: &[i64], workers: usize) -> i64 {
                let chunk = items.len().div_ceil(workers.max(1));
                let mut totals = vec![0i64; workers];

                thread::scope(|scope| {
                    for (index, slot) in totals.iter_mut().enumerate() {
                        let start = index * chunk;
                        let end = ((index + 1) * chunk).min(items.len());
                        let piece = if start < end {
                            &items[start..end]
                        } else {
                            &items[0..0]
                        };
                        scope.spawn(move || {
                            *slot = piece.iter().sum();
                        });
                    }
                });

                totals.iter().sum()
            }
            """,
        ),
        _p(
            9207, "Lock Ordering", "Medium",
            "Two locks taken in two orders is a deadlock waiting for the wrong "
            "interleaving. Taking them in one fixed order everywhere breaks "
            "the circular wait, which is the cheapest of the four conditions "
            "to break.",
            "O(1), and it is the difference between working and hanging",
            """
            pub struct Account {
                pub id: usize,
                pub balance: Mutex<i64>,
            }

            pub fn transfer(from: &Account, to: &Account, amount: i64) -> bool {
                // Always lock the lower id first, whichever way round the
                // call came in.
                let (first, second) = if from.id < to.id {
                    (from, to)
                } else {
                    (to, from)
                };

                let mut first_balance = first.balance.lock().unwrap();
                let mut second_balance = second.balance.lock().unwrap();

                let (source, target) = if from.id < to.id {
                    (&mut first_balance, &mut second_balance)
                } else {
                    (&mut second_balance, &mut first_balance)
                };

                if **source < amount {
                    return false;
                }
                **source -= amount;
                **target += amount;
                true
            }
            """,
        ),
        _p(
            9208, "Thread Pool", "Hard",
            "Workers wait on a channel of jobs. Dropping the sender is what "
            "tells them to stop, and joining in the destructor is what stops "
            "the program ending mid-job.",
            "O(1) submit, work spread over the workers",
            """
            pub struct ThreadPool {
                jobs: Option<mpsc::Sender<Box<dyn FnOnce() + Send>>>,
                workers: Vec<thread::JoinHandle<()>>,
            }

            impl ThreadPool {
                pub fn new(count: usize) -> Self {
                    let (sender, receiver) = mpsc::channel::<Box<dyn FnOnce() + Send>>();
                    let shared = Arc::new(Mutex::new(receiver));
                    let mut workers = Vec::new();
                    for _ in 0..count {
                        let mine = Arc::clone(&shared);
                        workers.push(thread::spawn(move || loop {
                            let job = mine.lock().unwrap().recv();
                            match job {
                                Ok(job) => job(),
                                Err(_) => return,
                            }
                        }));
                    }
                    ThreadPool {
                        jobs: Some(sender),
                        workers,
                    }
                }

                pub fn submit(&self, job: impl FnOnce() + Send + 'static) {
                    if let Some(sender) = &self.jobs {
                        let _ = sender.send(Box::new(job));
                    }
                }
            }

            impl Drop for ThreadPool {
                fn drop(&mut self) {
                    self.jobs.take();
                    for worker in self.workers.drain(..) {
                        let _ = worker.join();
                    }
                }
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
    preamble=(ATOMIC, SYNC, THREAD, MEM),
    problems=(
        _p(
            9401, "Cache Line", "Easy",
            "Memory moves in lines, not bytes. Sixty-four is the number to "
            "have in your head.",
            "O(1) — this is a fact, not an algorithm",
            """
            pub const CACHE_LINE: usize = 64;

            pub fn same_cache_line<T>(a: &T, b: &T) -> bool {
                let x = a as *const T as usize;
                let y = b as *const T as usize;
                x / CACHE_LINE == y / CACHE_LINE
            }

            pub fn lines_spanned(bytes: usize) -> usize {
                bytes.div_ceil(CACHE_LINE)
            }
            """,
        ),
        _p(
            9402, "False Sharing", "Hard",
            "Two threads writing different values on the SAME line fight over "
            "it. repr(align) pushes them apart, at the cost of the bytes.",
            "Same instruction count, wildly different time",
            """
            pub struct Shared {
                pub a: AtomicU64,
                pub b: AtomicU64,
            }

            #[repr(align(64))]
            pub struct Padded {
                pub value: AtomicU64,
            }

            pub struct PaddedPair {
                pub a: Padded,
                pub b: Padded,
            }

            impl Shared {
                pub fn new() -> Self {
                    Shared {
                        a: AtomicU64::new(0),
                        b: AtomicU64::new(0),
                    }
                }
            }

            impl PaddedPair {
                pub fn new() -> Self {
                    PaddedPair {
                        a: Padded { value: AtomicU64::new(0) },
                        b: Padded { value: AtomicU64::new(0) },
                    }
                }
            }
            """,
        ),
        _p(
            9403, "Row Major vs Column Major", "Medium",
            "The data is the same; the walk is not. Along a row uses every "
            "byte of each line fetched; down a column throws most away.",
            "Same O(n*n), an order of magnitude apart in practice",
            """
            pub fn sum_by_rows(grid: &[i64], rows: usize, cols: usize) -> i64 {
                let mut total = 0;
                for r in 0..rows {
                    for c in 0..cols {
                        total += grid[r * cols + c];
                    }
                }
                total
            }

            pub fn sum_by_columns(grid: &[i64], rows: usize, cols: usize) -> i64 {
                let mut total = 0;
                for c in 0..cols {
                    for r in 0..rows {
                        total += grid[r * cols + c];
                    }
                }
                total
            }
            """,
        ),
        _p(
            9404, "Struct Layout", "Medium",
            "Rust reorders fields by default to pack them; repr(C) stops it "
            "and you get the C layout, padding and all. That is the trade "
            "when something else has to read your bytes.",
            "O(1) — but it decides how many fit in a line",
            """
            pub struct Reordered {
                pub flag: u8,
                pub value: f64,
                pub other: u8,
                pub count: u32,
            }

            #[repr(C)]
            pub struct AsWritten {
                pub flag: u8,
                pub value: f64,
                pub other: u8,
                pub count: u32,
            }

            pub fn size_of_reordered() -> usize {
                mem::size_of::<Reordered>()
            }

            pub fn size_of_as_written() -> usize {
                mem::size_of::<AsWritten>()
            }

            pub fn per_cache_line(object: usize) -> usize {
                if object == 0 {
                    0
                } else {
                    CACHE_LINE / object
                }
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
            pub struct Particle {
                pub x: f64,
                pub y: f64,
                pub z: f64,
                pub mass: f64,
            }

            pub struct Particles {
                pub x: Vec<f64>,
                pub y: Vec<f64>,
                pub z: Vec<f64>,
                pub mass: Vec<f64>,
            }

            impl Particles {
                pub fn new() -> Self {
                    Particles {
                        x: Vec::new(),
                        y: Vec::new(),
                        z: Vec::new(),
                        mass: Vec::new(),
                    }
                }

                pub fn add(&mut self, x: f64, y: f64, z: f64, mass: f64) {
                    self.x.push(x);
                    self.y.push(y);
                    self.z.push(z);
                    self.mass.push(mass);
                }

                pub fn total_mass(&self) -> f64 {
                    self.mass.iter().sum()
                }
            }

            pub fn total_mass_aos(items: &[Particle]) -> f64 {
                items.iter().map(|p| p.mass).sum()
            }
            """,
        ),
        _p(
            9406, "Pointer Chasing vs Contiguous", "Medium",
            "A boxed list makes the processor wait for each node before it "
            "knows where the next one is. A Vec it can prefetch.",
            "Same O(n), and the constant is what gets you",
            """
            pub struct Link {
                pub value: i64,
                pub next: Option<Box<Link>>,
            }

            pub fn build_links(values: &[i64]) -> Option<Box<Link>> {
                let mut head: Option<Box<Link>> = None;
                for value in values.iter().rev() {
                    head = Some(Box::new(Link {
                        value: *value,
                        next: head,
                    }));
                }
                head
            }

            pub fn walk_links(head: &Option<Box<Link>>) -> i64 {
                let mut total = 0;
                let mut cursor = head;
                while let Some(node) = cursor {
                    total += node.value;
                    cursor = &node.next;
                }
                total
            }

            pub fn walk_slice(items: &[i64]) -> i64 {
                items.iter().sum()
            }
            """,
        ),
        _p(
            9407, "Branch Prediction", "Medium",
            "A branch the processor can guess is nearly free; one it cannot is "
            "a stall. Sorting first makes the SAME branch predictable.",
            "Same comparisons, very different cost",
            """
            pub fn sum_over(items: &[i64], threshold: i64) -> i64 {
                let mut total = 0;
                for value in items {
                    if *value >= threshold {
                        total += value;
                    }
                }
                total
            }

            pub fn sum_over_branchless(items: &[i64], threshold: i64) -> i64 {
                let mut total = 0;
                for value in items {
                    let mask = -((*value >= threshold) as i64);
                    total += value & mask;
                }
                total
            }
            """,
        ),
        _p(
            9408, "Blocked Transpose", "Hard",
            "Transposing straight through misses on one side or the other. A "
            "tile at a time keeps both source and destination in cache.",
            "Same O(n*n), far fewer misses",
            """
            pub fn transpose_naive(src: &[i64], dst: &mut [i64], n: usize) {
                for r in 0..n {
                    for c in 0..n {
                        dst[c * n + r] = src[r * n + c];
                    }
                }
            }

            pub fn transpose_blocked(
                src: &[i64],
                dst: &mut [i64],
                n: usize,
                block: usize,
            ) {
                let mut r0 = 0;
                while r0 < n {
                    let mut c0 = 0;
                    while c0 < n {
                        let r_end = (r0 + block).min(n);
                        let c_end = (c0 + block).min(n);
                        for r in r0..r_end {
                            for c in c0..c_end {
                                dst[c * n + r] = src[r * n + c];
                            }
                        }
                        c0 += block;
                    }
                    r0 += block;
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
    preamble=(OPS,),
    problems=(
        _p(
            9501, "Fixed-Point Price", "Medium",
            "Money is not an f64. A newtype over i64 ticks makes the "
            "arithmetic exact and stops you accidentally adding a price to a "
            "quantity.",
            "O(1), and exactly representable",
            """
            #[derive(Copy, Clone, PartialEq, Eq, PartialOrd, Ord, Debug)]
            pub struct Price(pub i64);

            impl Price {
                pub const SCALE: i64 = 10_000;

                pub fn from_f64(value: f64) -> Self {
                    let scaled = value * Self::SCALE as f64;
                    Price(if scaled < 0.0 {
                        (scaled - 0.5) as i64
                    } else {
                        (scaled + 0.5) as i64
                    })
                }

                pub fn to_f64(self) -> f64 {
                    self.0 as f64 / Self::SCALE as f64
                }
            }

            impl std::ops::Add for Price {
                type Output = Price;
                fn add(self, other: Price) -> Price {
                    Price(self.0 + other.0)
                }
            }

            impl std::ops::Sub for Price {
                type Output = Price;
                fn sub(self, other: Price) -> Price {
                    Price(self.0 - other.0)
                }
            }
            """,
        ),
        _p(
            9502, "Price Level", "Easy",
            "Everything resting at one price, kept as a total rather than a "
            "list. The book only needs the sum until something trades.",
            "O(1) add and remove",
            """
            #[derive(Copy, Clone, Debug)]
            pub struct Level {
                pub price: Price,
                pub quantity: i64,
                pub orders: u32,
            }

            impl Level {
                pub fn new(price: Price, quantity: i64) -> Self {
                    Level {
                        price,
                        quantity,
                        orders: 1,
                    }
                }

                pub fn add(&mut self, quantity: i64) {
                    self.quantity += quantity;
                    self.orders += 1;
                }

                pub fn remove(&mut self, quantity: i64) {
                    self.quantity -= quantity.min(self.quantity);
                    self.orders = self.orders.saturating_sub(1);
                }

                pub fn is_empty(&self) -> bool {
                    self.quantity <= 0
                }
            }
            """,
        ),
        _p(
            9503, "Order Book", "Hard",
            "Bids sorted high to low, asks low to high, so the best of each is "
            "the front. Keeping them that way on insert beats sorting on every "
            "read.",
            "O(levels) insert, O(1) best",
            """
            pub struct OrderBook {
                pub bids: Vec<Level>,
                pub asks: Vec<Level>,
            }

            impl OrderBook {
                pub fn new() -> Self {
                    OrderBook {
                        bids: Vec::new(),
                        asks: Vec::new(),
                    }
                }

                pub fn add_bid(&mut self, price: Price, quantity: i64) {
                    let at = Self::place(&self.bids, price, true);
                    Self::insert(&mut self.bids, at, price, quantity);
                }

                pub fn add_ask(&mut self, price: Price, quantity: i64) {
                    let at = Self::place(&self.asks, price, false);
                    Self::insert(&mut self.asks, at, price, quantity);
                }

                pub fn best_bid(&self) -> Option<Level> {
                    self.bids.first().copied()
                }

                pub fn best_ask(&self) -> Option<Level> {
                    self.asks.first().copied()
                }

                pub fn spread_ticks(&self) -> Option<i64> {
                    match (self.best_bid(), self.best_ask()) {
                        (Some(bid), Some(ask)) => Some(ask.price.0 - bid.price.0),
                        _ => None,
                    }
                }

                pub fn crossed(&self) -> bool {
                    match (self.best_bid(), self.best_ask()) {
                        (Some(bid), Some(ask)) => bid.price >= ask.price,
                        _ => false,
                    }
                }

                fn place(side: &[Level], price: Price, descending: bool) -> usize {
                    for (i, level) in side.iter().enumerate() {
                        if level.price == price {
                            return i;
                        }
                        let before = if descending {
                            level.price < price
                        } else {
                            price < level.price
                        };
                        if before {
                            return i;
                        }
                    }
                    side.len()
                }

                fn insert(side: &mut Vec<Level>, at: usize, price: Price, quantity: i64) {
                    if at < side.len() && side[at].price == price {
                        side[at].add(quantity);
                    } else {
                        side.insert(at, Level::new(price, quantity));
                    }
                }
            }
            """,
        ),
        _p(
            9504, "Matching Step", "Hard",
            "An aggressive order eats the book from the best price outward and "
            "stops when it is filled or the price stops being acceptable.",
            "O(levels touched)",
            """
            #[derive(Copy, Clone, Debug)]
            pub struct Fill {
                pub price: Price,
                pub quantity: i64,
            }

            pub fn match_buy(book: &mut OrderBook, limit: Price, wanted: i64) -> Vec<Fill> {
                let mut fills = Vec::new();
                let mut left = wanted;
                while left > 0 {
                    let best = match book.asks.first().copied() {
                        Some(level) => level,
                        None => break,
                    };
                    if best.price > limit {
                        break;
                    }
                    let taken = left.min(best.quantity);
                    fills.push(Fill {
                        price: best.price,
                        quantity: taken,
                    });
                    left -= taken;
                    book.asks[0].quantity -= taken;
                    if book.asks[0].is_empty() {
                        book.asks.remove(0);
                    }
                }
                fills
            }

            pub fn filled_quantity(fills: &[Fill]) -> i64 {
                fills.iter().map(|f| f.quantity).sum()
            }
            """,
        ),
        _p(
            9505, "VWAP", "Medium",
            "Volume-weighted, so a big trade counts for more. Carry the two "
            "running totals — you cannot average averages.",
            "O(1) per trade",
            """
            pub struct Vwap {
                notional: i128,
                volume: i64,
            }

            impl Vwap {
                pub fn new() -> Self {
                    Vwap {
                        notional: 0,
                        volume: 0,
                    }
                }

                pub fn add(&mut self, price: Price, quantity: i64) {
                    self.notional += price.0 as i128 * quantity as i128;
                    self.volume += quantity;
                }

                pub fn value(&self) -> Option<Price> {
                    if self.volume == 0 {
                        None
                    } else {
                        Some(Price((self.notional / self.volume as i128) as i64))
                    }
                }

                pub fn total_volume(&self) -> i64 {
                    self.volume
                }
            }
            """,
        ),
        _p(
            9506, "Rolling Window", "Medium",
            "A fixed-size ring of the last n values. Nothing shifts and nothing "
            "allocates after construction.",
            "O(1) push, O(n) statistics",
            """
            pub struct RollingWindow {
                slots: Vec<i64>,
                next: usize,
                filled: usize,
                running: i64,
            }

            impl RollingWindow {
                pub fn new(capacity: usize) -> Self {
                    RollingWindow {
                        slots: vec![0; capacity],
                        next: 0,
                        filled: 0,
                        running: 0,
                    }
                }

                pub fn push(&mut self, value: i64) {
                    if self.filled == self.slots.len() {
                        self.running -= self.slots[self.next];
                    } else {
                        self.filled += 1;
                    }
                    self.slots[self.next] = value;
                    self.running += value;
                    self.next = (self.next + 1) % self.slots.len();
                }

                pub fn len(&self) -> usize {
                    self.filled
                }

                pub fn sum(&self) -> i64 {
                    self.running
                }

                pub fn mean(&self) -> Option<f64> {
                    if self.filled == 0 {
                        None
                    } else {
                        Some(self.running as f64 / self.filled as f64)
                    }
                }

                pub fn highest(&self) -> Option<i64> {
                    self.slots[..self.filled].iter().copied().max()
                }
            }
            """,
        ),
        _p(
            9507, "Latency Histogram", "Medium",
            "Keeping every sample to find the 99th percentile is the wrong "
            "trade. Bucket on the way in and the answer is a scan.",
            "O(1) record, O(buckets) percentile",
            """
            pub struct Histogram {
                counts: Vec<u64>,
                width: u64,
                total: u64,
            }

            impl Histogram {
                pub fn new(buckets: usize, width: u64) -> Self {
                    Histogram {
                        counts: vec![0; buckets],
                        width,
                        total: 0,
                    }
                }

                pub fn record(&mut self, nanos: u64) {
                    let at = ((nanos / self.width) as usize).min(self.counts.len() - 1);
                    self.counts[at] += 1;
                    self.total += 1;
                }

                pub fn percentile(&self, fraction: f64) -> Option<u64> {
                    if self.total == 0 {
                        return None;
                    }
                    let wanted = (fraction * self.total as f64) as u64;
                    let mut seen = 0;
                    for (i, count) in self.counts.iter().enumerate() {
                        seen += count;
                        if seen > wanted {
                            return Some((i as u64 + 1) * self.width);
                        }
                    }
                    Some(self.counts.len() as u64 * self.width)
                }

                pub fn samples(&self) -> u64 {
                    self.total
                }
            }
            """,
        ),
        _p(
            9508, "Tick Parsing", "Medium",
            "Parse the wire format from bytes. No String, no allocation — on a "
            "feed, the allocator is the latency.",
            "O(length), no allocation",
            """
            #[derive(Debug)]
            pub struct Tick {
                pub symbol: [u8; 8],
                pub price: Price,
                pub quantity: i64,
            }

            pub fn parse_tick(line: &[u8]) -> Option<Tick> {
                let mut symbol = [0u8; 8];
                let mut at = 0;
                let mut wrote = 0;
                while at < line.len() && line[at] != b',' {
                    if wrote < symbol.len() {
                        symbol[wrote] = line[at];
                        wrote += 1;
                    }
                    at += 1;
                }
                if at >= line.len() {
                    return None;
                }
                at += 1;

                let mut whole: i64 = 0;
                while at < line.len() && line[at].is_ascii_digit() {
                    whole = whole * 10 + (line[at] - b'0') as i64;
                    at += 1;
                }
                let mut frac: i64 = 0;
                let mut scale = Price::SCALE;
                if at < line.len() && line[at] == b'.' {
                    at += 1;
                    while at < line.len() && line[at].is_ascii_digit() && scale > 1 {
                        scale /= 10;
                        frac += (line[at] - b'0') as i64 * scale;
                        at += 1;
                    }
                }
                if at >= line.len() || line[at] != b',' {
                    return None;
                }
                at += 1;

                let mut quantity: i64 = 0;
                let mut any = false;
                while at < line.len() && line[at].is_ascii_digit() {
                    quantity = quantity * 10 + (line[at] - b'0') as i64;
                    any = true;
                    at += 1;
                }
                if !any {
                    return None;
                }

                Some(Tick {
                    symbol,
                    price: Price(whole * Price::SCALE + frac),
                    quantity,
                })
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
