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
    "use std::sync::atomic::Ordering;"
)
SYNC = "use std::sync::Arc;\nuse std::sync::Mutex;\nuse std::sync::Condvar;"
THREAD = "use std::thread;"


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


PATTERNS: tuple[Pattern, ...] = (
    _MEMORY,
    _LOCKFREE,
)
