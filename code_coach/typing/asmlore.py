"""Assembly: where it came from, and where it is still the answer.

Same standard as langhistory.py, and it matters more here. Assembly
attracts folklore - stories about hand-written machine code that get
better each retelling - so every person, date and product below was
checked against a public source rather than recalled, and the ones
that turned out to be embroidered were left out.

Where a number would drift it is pinned to the year it was true, and
where attribution is genuinely disputed the line says so instead of
picking a side. The fast inverse square root is the example: it
appeared in Quake III Arena in 1999 and who wrote it first is argued
about to this day, so that is what the line says.

The dialect
-----------
The code lines here are x86-64, Intel syntax, NASM, on Linux, which
is what the existing Assembly Code theme already uses. Mixing AT&T
syntax in would be teaching two languages under one name - the operand
order is reversed between them, so a line that reads correctly in one
is backwards in the other.
"""

from __future__ import annotations

from code_coach.typing.langlore2 import Passage, _p

# -- The history ---------------------------------------------

ASSEMBLY_STORY: tuple[Passage, ...] = (
    _p("Kathleen Booth wrote the first assembly language in the late 1940s at "
       "Birkbeck College in London, along with the assembler that turned it "
       "into machine code.", "Assembly history"),
    _p("She called the idea contracted notation: let a person write a short "
       "word like MOV, and have a program do the translating. Every "
       "assembler since is that idea.", "Assembly history"),
    _p("Before the assembler, a program was numbers. The whole profession of "
       "writing software in words rather than digits starts at this one "
       "invention.", "Assembly history"),
    _p("There is no single assembly language. Each processor family has its "
       "own, because the instructions are the chip's, not a committee's.",
       "Assembly design"),
    _p("Intel syntax puts the destination first and AT&T syntax puts it last. "
       "The same instruction reads backwards between them, which is why "
       "mixing the two is so painful.", "Assembly dialects"),
    _p("An assembler is close to a one-to-one naming of machine instructions, "
       "which is what separates it from a compiler: almost nothing is "
       "invented on your behalf.", "Assembly design"),
    _p("A label is just a name for an address. The processor has no idea your "
       "loop is called .loop; by the time it runs, that is a number.",
       "Assembly internals"),
    _p("Registers are the only truly fast storage there is. Everything else, "
       "cache included, is a negotiation.", "Assembly internals"),
    _p("Flags are the hidden state. cmp does a subtraction and throws the "
       "answer away, keeping only what it said about the two operands.",
       "Assembly internals"),
    _p("The calling convention is an agreement, not a rule the hardware "
       "enforces. Break it and nothing stops you until something far away "
       "crashes.", "Assembly design"),
    _p("A syscall is how a program asks the kernel for something it is not "
       "allowed to do itself. Every file read you have ever written bottoms "
       "out in one.", "Assembly internals"),
    _p("xor rax, rax sets a register to zero and is shorter than writing the "
       "zero. Decades of that kind of trade are why assembly reads the way "
       "it does.", "Assembly idioms"),
)

# -- What it is actually used for ----------------------------

ASSEMBLY_IN_USE: tuple[Passage, ...] = (
    _p("The software that landed Apollo on the Moon was assembly, written at "
       "MIT under Margaret Hamilton and stored in memory that had to be woven "
       "by hand.", "Apollo Guidance Computer"),
    _p("That memory was core rope: a wire threaded through a magnetic ring "
       "for a one and around it for a zero, so the program was physically a "
       "textile.", "Apollo Guidance Computer"),
    _p("The Apollo computer had about four kilobytes of writable memory and "
       "ran near one megahertz. The constraint is the reason the code is "
       "studied rather than the achievement.", "Apollo Guidance Computer"),
    _p("RollerCoaster Tycoon was written almost entirely in x86 assembly by "
       "Chris Sawyer, with a little C only where Windows and DirectX had to "
       "be spoken to.", "Assembly in industry"),
    _p("It was the best-selling PC game of 1999. One person wrote the code, "
       "which is the part that still gets brought up whenever assembly comes "
       "up.", "Assembly in industry"),
    _p("Quake III Arena shipped the fast inverse square root in 1999, a "
       "bit-level trick with a magic constant. Who wrote it first is still "
       "argued about.", "Assembly in industry"),
    _p("That trick is obsolete now, and the reason is instructive: the "
       "processor grew an instruction that does the same job. Hand "
       "optimisation gets absorbed into hardware.", "Assembly in industry"),
    _p("Almost nobody writes whole programs in assembly any more. People do "
       "write it for the innermost loop of a video codec, a cryptographic "
       "routine, or a driver.", "Assembly in industry"),
    _p("Reading it is the commoner skill. A debugger, a profiler and a crash "
       "dump all eventually show you instructions, and being able to follow "
       "them is the difference between a guess and a diagnosis.",
       "Assembly in practice"),
    _p("Compilers now out-optimise people at nearly everything, because they "
       "will happily consider a thousand orderings of the same instructions "
       "and a person will not.", "Assembly in practice"),
    _p("The places a person still wins are the ones the compiler is not "
       "allowed to reach: SIMD hand-tuning, constant-time crypto, and "
       "anything where the exact instruction matters.", "Assembly in practice"),
    _p("Every language you use ends up here. Python, JavaScript and Rust all "
       "become instructions, and this is the language that names them.",
       "Assembly design"),
)

# -- More lines to type, matching the existing dialect --------
# x86-64, Intel syntax, NASM, Linux. See the module docstring.

ASSEMBLY_CODE_MORE: tuple[Passage, ...] = (
    _p("mov rsi, msg", "the address to write from"),
    _p("mov rdx, len", "and how many bytes"),
    _p("mov eax, dword [rbx]", "load four bytes, zeroing the top half"),
    _p("mov qword [rsp + 8], rax", "store a register into a local"),
    _p("movzx eax, byte [rsi]", "one byte, zero extended"),
    _p("add rsp, 32", "give the local space back"),
    _p("sub rax, rdx", "subtract, and keep the answer"),
    _p("and rax, 0x0f", "keep only the low four bits"),
    _p("or rax, rbx", "set every bit either one has"),
    _p("not rax", "flip all sixty-four"),
    _p("neg rax", "the two's complement"),
    _p("shl rax, 3", "multiply by eight, the cheap way"),
    _p("shr rax, 1", "and halve it"),
    _p("sar rax, 1", "halve it, keeping the sign"),
    _p("dec rcx", "one fewer"),
    _p("idiv rbx", "signed divide, with the remainder in rdx"),
    _p("cqo", "sign extend rax into rdx, which idiv needs first"),
    _p("cmp byte [rsi], 0", "is this the end of the string"),
    _p("je .done", "jump if they were equal"),
    _p("jl .smaller", "jump if the first was less"),
    _p("jg .bigger", "and if it was greater"),
    _p("jmp .loop", "go back, no question asked"),
    _p("loop .again", "decrement rcx and jump while it is not zero"),
    _p("sete al", "turn the flag into a 0 or a 1"),
    _p("cmovg rax, rbx", "move only if greater, with no branch to mispredict"),
    _p("push rbx", "save a register the caller expects back"),
    _p("pop rbx", "and give it back"),
    _p("call strlen", "push the return address and go"),
    _p("leave", "undo the frame in one instruction"),
    _p("nop", "does nothing, on purpose"),
    _p("db 0x0a", "one raw byte"),
    _p("dq 0", "eight of them"),
    _p("resq 8", "reserve eight quadwords, uninitialised"),
    _p("times 16 db 0", "sixteen zero bytes, written once"),
    _p("global main", "let the linker see it"),
    _p("default rel", "address things relative to rip"),
    _p(".loop:", "somewhere to jump back to"),
    _p(".done:", "and somewhere to fall out"),
    _p("xor rdx, rdx", "clear the high half before dividing"),
    _p("mov rax, [rbp - 8]", "read a local back"),
)
