"""More x86-64 to type, grouped by instruction family.

Assembly had 72 lines against Python's 854, and the consequence was
visible rather than theoretical: Same Shape could offer exactly one
drill for it, because a shape needs eight real examples before it is
worth ten in a row and only `mov` had eight. Forty-three shapes
existed and forty-two of them had one or two lines each.

So this fills out the families rather than adding more one-offs. The
families are the ones a person actually meets: moves, the compare and
the jumps that read its flags, the arithmetic, the stack, the calls,
and the assembler's own directives.

The line that is not worth writing
----------------------------------
There is an obvious way to cheat here, which is to emit eight
variations of everything and watch the shape count go up. That would
be optimising the number rather than the practice, and the lines would
be recognisably filler the first time somebody typed them.

The rule used instead: every line has to be one a person would really
write in a real program. `jne .not_found` is a line; `jne .label8` is
padding. Where a family genuinely does not come up eight times in
ordinary code, it stays short and stays out of Same Shape, which is
the honest outcome.

Dialect
-------
x86-64, Intel syntax, NASM, Linux — matching the existing theme
exactly. Registers are the 64-bit names except where a narrower one is
the point, memory operands are in brackets, and the destination comes
first. AT&T syntax reverses that, so mixing it in would teach two
languages under one name and would make every derived description
backwards.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# -- Moves ---------------------------------------------------
# The commonest instruction there is, and the one whose addressing
# modes are the real lesson: a register, a literal, an address, and
# the contents of an address are four different things that look
# alike.

MOVES: tuple[Passage, ...] = (
    _p("mov rcx, rax", "copy one register to another"),
    _p("mov rbx, 0", "a literal, the obvious way"),
    _p("mov rdx, rsi", "the third argument, from the second"),
    _p("mov r8, rdi", "the registers past the named ones"),
    _p("mov rax, [rsi]", "eight bytes from where rsi points"),
    _p("mov [rdi], rax", "and the other direction"),
    _p("mov rax, [rsi + 8]", "the next quadword along"),
    _p("mov rax, [rsi + rcx * 8]", "an indexed load, which is one instruction"),
    _p("mov al, [rsi + rcx]", "one byte out of a string"),
    _p("mov [rdi + rcx], al", "and one byte into another"),
    _p("mov eax, edi", "thirty-two bits, which zeroes the top half"),
    _p("mov dword [rbp - 4], 0", "a four-byte local, set to zero"),
    _p("mov byte [rdi], 0", "the terminator on a C string"),
    _p("mov rsp, rbp", "unwind the frame by hand"),
    _p("movsx rax, eax", "widen, keeping the sign"),
    _p("movzx ecx, word [rsi]", "two bytes, zero extended"),
)

# -- Compare and the jumps that read it ----------------------
# Deliberately together, because that is how they are written: the
# comparison produces nothing except flags, and the jump on the next
# line is what reads them. Neither line makes sense alone.

COMPARISONS: tuple[Passage, ...] = (
    _p("cmp rax, rbx", "two registers"),
    _p("cmp rax, 0", "against zero, the long way"),
    _p("cmp rcx, rdx", "the counter against the limit"),
    _p("cmp al, 'a'", "one character"),
    _p("cmp qword [rsi], 0", "is the pointer null"),
    _p("cmp dword [rbp - 4], 10", "a local against a literal"),
    _p("cmp rax, rcx", "which of the two is larger"),
    _p("test rcx, rcx", "the fast way to ask whether it is zero"),
    _p("test al, al", "the same question, one byte wide"),
    _p("test rax, 1", "is the low bit set, which is odd or even"),
    _p("test rdi, rdi", "check an argument before using it"),
    _p("test rsi, rsi", "and the second one"),
    _p("test rdx, rdx", "is the length zero"),
)

JUMPS: tuple[Passage, ...] = (
    _p("je .found", "equal, so we are done"),
    _p("je .skip", "equal, so there is nothing to do"),
    _p("je .same", "the two matched"),
    _p("je .empty", "nothing in it"),
    _p("je .match", "this is the one"),
    _p("je .end", "out of the loop"),
    _p("je .next", "on to the following one"),

    _p("jne .not_found", "not equal, and that is the answer"),
    _p("jne .retry", "not what we wanted, try again"),
    _p("jne .mismatch", "the strings differ here"),
    _p("jne .continue", "carry on down the list"),
    _p("jne .error", "not the value expected"),
    _p("jne .skip", "nothing to do for this one"),
    _p("jne .again", "round the loop once more"),

    _p("jl .left", "go down the left branch"),
    _p("jl .below", "under the threshold"),
    _p("jl .shrink", "the window is too big"),
    _p("jl .loop", "still under the limit"),
    _p("jl .swap", "out of order, so swap them"),
    _p("jl .before", "earlier in the array"),
    _p("jl .lower", "take the lower half"),

    _p("jg .right", "go down the right branch"),
    _p("jg .above", "over the threshold"),
    _p("jg .update", "a new best"),
    _p("jg .higher", "take the upper half"),
    _p("jg .overflowed", "past what fits"),
    _p("jg .after", "later in the array"),
    _p("jg .grow", "the window is too small"),

    _p("jge .in_range", "at or above the floor"),
    _p("jge .keep", "good enough to keep"),
    _p("jge .valid", "within bounds"),
    _p("jge .next", "on to the next"),
    _p("jge .done", "we have reached the end"),
    _p("jge .skip", "nothing below this one"),
    _p("jge .above", "at or over the mark"),

    _p("jle .loop", "less or equal, keep going"),
    _p("jle .small", "no bigger than the limit"),
    _p("jle .done", "the counter has run out"),
    _p("jle .base", "small enough to answer directly"),

    _p("jz .empty", "the zero flag, which cmp with zero sets"),
    _p("jz .null", "the pointer was zero"),
    _p("jz .even", "the low bit was clear"),
    _p("jz .finished", "nothing left"),
    _p("jz .skip", "nothing there"),
    _p("jz .base_case", "the recursion bottoms out"),
    _p("jz .no_more", "the count reached zero"),

    _p("jnz .loop", "not zero, so round again"),
    _p("jnz .odd", "the low bit was set"),
    _p("jnz .has_bits", "something is still set"),
    _p("jnz .again", "keep going while it is not zero"),

    _p("jmp .done", "straight out"),
    _p("jmp .end", "skip the else branch"),
    _p("jmp .next", "on to the next case"),
    _p("jmp .cleanup", "jump to the exit path"),
    _p("jmp .check", "back to the test"),
    _p("jmp .print", "into the output routine"),
    _p("jmp .return", "out to the epilogue"),
)

# -- Arithmetic and bits -------------------------------------

ARITHMETIC: tuple[Passage, ...] = (
    _p("add rax, rbx", "two registers"),
    _p("add rax, 1", "the long way to increment"),
    _p("add rsi, 8", "walk a pointer on by one quadword"),
    _p("add rcx, rdx", "accumulate into the counter"),
    _p("add rax, [rsi]", "add what is in memory"),
    _p("add rsp, 16", "release two quadwords of locals"),
    _p("add rdi, rcx", "advance the destination"),
    _p("add r9, 1", "count one more"),

    _p("sub rax, rbx", "one register from another"),
    _p("sub rsp, 8", "make room for one local"),
    _p("sub rcx, 1", "the long way to decrement"),
    _p("sub rsi, 8", "step a pointer back"),
    _p("sub rdi, rax", "close the gap"),
    _p("sub r10, rcx", "how far is left to go"),

    _p("inc rax", "one more, in one byte of encoding"),
    _p("inc rsi", "step the source pointer"),
    _p("inc rdi", "and the destination"),
    _p("inc rdx", "count another"),
    _p("inc r8", "and another"),
    _p("inc qword [rbp - 8]", "a counter held in memory"),
    _p("inc rbx", "one along"),

    _p("dec rax", "one fewer"),
    _p("dec rsi", "back up a byte"),
    _p("dec rdx", "one off the count"),
    _p("dec r9", "and one off this one"),
    _p("dec qword [rbp - 8]", "a counter in memory, downwards"),
    _p("dec rbx", "one back"),
    _p("dec rdi", "step the end pointer in"),

    _p("imul rax, rcx", "signed multiply"),
    _p("imul rax, 10", "times ten, for reading digits"),
    _p("imul rdx, rsi", "the area of two sides"),
    _p("imul rcx, 4", "scale an index to bytes"),
    _p("imul r8, r9", "two of the numbered registers"),
    _p("imul rax, 31", "the multiplier in a string hash"),
    _p("imul rcx, rdx", "two counters multiplied"),

    _p("idiv rcx", "signed divide, remainder in rdx"),
    _p("idiv r8", "divide by whatever is in r8"),
    _p("div rcx", "the unsigned version"),
    _p("div rsi", "unsigned, by a pointer-sized value"),
)

BITS: tuple[Passage, ...] = (
    _p("xor rax, rax", "set it to zero, the short way"),
    _p("xor rcx, rcx", "clear the counter"),
    _p("xor r8, r8", "start this one at zero"),
    _p("xor rsi, rsi", "no source yet"),
    _p("xor rbx, rbx", "clear the accumulator"),
    _p("xor rax, rcx", "the actual exclusive-or, not the idiom"),

    _p("and rax, rbx", "the bits both have"),
    _p("and rax, 1", "keep the low bit"),
    _p("and rcx, 7", "the remainder of a divide by eight"),
    _p("and al, 0xdf", "clear one bit, which upper-cases a letter"),
    _p("and rdx, rsi", "mask by another register"),
    _p("and rax, 0xff", "keep the low byte"),
    _p("and r9, rax", "narrow what is left"),

    _p("or al, 0x20", "set one bit, which lower-cases a letter"),
    _p("or rcx, rdx", "merge two sets of flags"),
    _p("or rax, 1", "make sure the low bit is set"),
    _p("or r8, r9", "combine them"),
    _p("or rdi, rsi", "either of the two"),
    _p("or rbx, rax", "fold this one in"),
    _p("or rcx, 0x20", "set the bit that lower-cases"),

    _p("shl rax, 1", "double it"),
    _p("shl rcx, 4", "times sixteen"),
    _p("shl rdx, 8", "move a byte up into place"),
    _p("shl rax, 2", "times four, for a four-byte index"),
    _p("shl r8, 1", "one place left"),
    _p("shl rbx, 3", "times eight"),
    _p("shl rsi, 5", "the shift in a hash"),

    _p("shr rcx, 8", "bring the next byte down"),
    _p("shr rdx, 4", "one nibble right"),
    _p("shr rax, 3", "divide by eight"),
    _p("shr r9, 1", "one place right"),
    _p("shr rbx, 16", "take the high half of a word"),
    _p("shr rsi, 2", "divide by four"),
    _p("shr rax, 32", "bring the high half down"),

    _p("sar rcx, 2", "signed divide by four"),
    _p("sar rdx, 63", "smear the sign across all sixty-four bits"),
    _p("sar r8, 1", "signed, one place"),

    _p("not rcx", "the complement"),
    _p("not rdx", "every bit the other way"),
    _p("not rbx", "invert it"),

    _p("neg rcx", "make it negative"),
    _p("neg rdx", "flip the sign"),
    _p("neg r8", "and this one"),
)

# -- The stack and calls -------------------------------------

STACK: tuple[Passage, ...] = (
    _p("push r12", "another callee-saved one"),
    _p("push r13", "and another"),
    _p("push rdi", "save an argument across a call"),
    _p("push rsi", "and the second"),
    _p("push rax", "keep the result while we do something else"),
    _p("push rcx", "the counter, over a call that clobbers it"),
    _p("push qword [rsi]", "push what is in memory, not the address"),

    _p("pop rcx", "take the top back"),
    _p("pop rsi", "restore the second argument"),
    _p("pop rdi", "and the first"),
    _p("pop r13", "unwind in the opposite order"),
    _p("pop r12", "which is why the order matters"),
    _p("pop rax", "the value we parked"),
)

CALLS: tuple[Passage, ...] = (
    _p("call malloc", "ask for memory"),
    _p("call free", "and give it back"),
    _p("call puts", "print a string and a newline"),
    _p("call memcpy", "copy a block"),
    _p("call exit", "leave, through libc"),
    _p("call .helper", "a local routine"),
    _p("call factorial", "recursion, which is a call like any other"),
    _p("call read_line", "into another routine of ours"),
)

# -- Labels --------------------------------------------------
# Real programs are full of them, and typing the colon in the right
# place is its own small habit.

LABELS: tuple[Passage, ...] = (
    _p("main:", "where a C runtime starts you"),
    _p(".next:", "the following step"),
    _p(".found:", "we got what we came for"),
    _p(".not_found:", "and the case where we did not"),
    _p(".cleanup:", "the common exit path"),
    _p(".error:", "where the failures go"),
    _p(".skip:", "past the part that did not apply"),
    _p(".end:", "the last one"),
    _p(".base_case:", "where the recursion stops"),
    _p("strlen:", "a routine worth writing once by hand"),
)

# -- Addresses -----------------------------------------------

ADDRESSES: tuple[Passage, ...] = (
    _p("lea rax, [rsi + 1]", "the address one along, without touching memory"),
    _p("lea rdi, [rel msg]", "a string's address, relative to rip"),
    _p("lea rdx, [rax + rax * 2]", "times three, done by the address unit"),
    _p("lea rsi, [rbp - 32]", "the address of a local"),
    _p("lea rcx, [rax + 8]", "arithmetic that leaves the flags alone"),
    _p("lea r8, [rdi + rcx]", "one past the end"),
    _p("lea rax, [rsp + 16]", "into the caller's arguments"),
    _p("lea rdi, [rel buffer]", "where to write"),
)

# -- Directives ----------------------------------------------
# Instructions to the assembler, not to the processor. They never run,
# which is the thing worth knowing about them.

DIRECTIVES: tuple[Passage, ...] = (
    _p("section .rodata", "bytes that must not be written"),
    _p("global strlen", "export a routine"),
    _p("global compute", "and another"),
    _p("extern malloc", "defined in libc, not here"),
    _p("extern free", "likewise"),
    _p("extern puts", "and this one"),
    _p("extern memcpy", "somebody else's"),
    _p("extern exit", "the last one we borrow"),
    _p("extern strlen", "borrowed rather than written"),
    _p("extern calloc", "zeroed memory, from libc"),

    _p("db 0", "one byte"),
    _p("db 10", "a newline"),
    _p("db \"error\", 0", "a C string, terminator and all"),
    _p("db 1, 2, 3, 4", "four bytes in a row"),
    _p("dw 1024", "two bytes"),
    _p("dd 0x7fffffff", "four"),
    _p("dq 1", "and eight"),

    _p("resb 256", "reserve bytes, filled in at run time"),
    _p("resb 1024", "a kilobyte of room"),
    _p("resd 16", "sixteen doublewords"),
    _p("resq 4", "four quadwords"),
    _p("resw 8", "eight words"),
    _p("resb 4096", "a page of it"),
    _p("resq 64", "sixty-four quadwords"),

    _p("align 8", "pad to an eight-byte boundary"),
    _p("align 32", "and to thirty-two"),
)

#: Everything above, in the order a program would meet it.
ASSEMBLY_DRILLS: tuple[Passage, ...] = (
    MOVES
    + COMPARISONS
    + JUMPS
    + ARITHMETIC
    + BITS
    + STACK
    + CALLS
    + LABELS
    + ADDRESSES
    + DIRECTIVES
)
