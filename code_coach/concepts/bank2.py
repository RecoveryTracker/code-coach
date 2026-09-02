"""More concept questions: numbers, builds, probability and microstructure.

`bank.py` covers the systems half — the language, the kernel, the machine,
threads and the wire. This is the rest of what a quant desk asks about: why
money is not a double, what happens between your source and a running binary,
the probability questions that get asked in every first round, and how a
market actually works underneath the price.
"""

from __future__ import annotations

from code_coach.concepts import Topic, _q

_FLOAT = Topic(
    id="floating-point",
    name="Floating Point & Numerics",
    order=60,
    blurb="Why 0.1 + 0.2 is not 0.3, and what to do about it when it is money.",
    questions=(
        _q(
            "Why is 0.1 + 0.2 not 0.3?",
            "Binary floating point cannot represent 0.1 exactly, the same way "
            "decimal cannot represent a third. Each is rounded to the nearest "
            "representable double, and the sum of those roundings is not the "
            "rounding of the sum. The error is about 5.5e-17, which is "
            "invisible until you compare for equality.",
            "So how should you compare two doubles?",
        ),
        _q(
            "How do you compare two floating point numbers?",
            "Not with ==. Compare the difference against a tolerance, and "
            "make the tolerance relative to the magnitude for large values — "
            "an absolute epsilon of 1e-9 is meaningless next to 1e12. For "
            "money, do not compare floats at all; use integers.",
        ),
        _q(
            "Why is money stored as an integer?",
            "Because a price is exact and a double is not. Store the number "
            "of ticks or cents as an integer and addition, subtraction and "
            "comparison are exact. You only need care at multiplication and "
            "division, where you decide the rounding yourself rather than "
            "having it decided for you.",
        ),
        _q(
            "What is catastrophic cancellation?",
            "Subtracting two nearly equal numbers destroys the significant "
            "digits: the leading digits cancel and what is left is mostly "
            "the rounding error. It is why the naive variance formula — mean "
            "of squares minus square of the mean — is bad, and why Welford's "
            "online algorithm exists.",
            "How would you compute a variance without it?",
        ),
        _q(
            "How many decimal digits does a double actually give you?",
            "About 15 to 17 significant decimal digits, from 53 bits of "
            "mantissa. A float gives about 7. So a double can hold every "
            "integer up to 2^53 exactly, and beyond that it starts skipping — "
            "which is why large integer ids in JSON are a recurring bug.",
        ),
        _q(
            "What is the difference between NaN and infinity?",
            "Infinity is the result of overflow or dividing a non-zero by "
            "zero, and it still orders sensibly. NaN is the result of an "
            "undefined operation like zero over zero, and it compares false "
            "against everything including itself — which is the standard way "
            "to test for it.",
        ),
        _q(
            "Why does floating point addition not associate?",
            "Because each step rounds. (a + b) + c and a + (b + c) round at "
            "different points, so they can differ. That is why summing a "
            "large array in a different order gives a different answer, and "
            "why the compiler is not allowed to reorder your arithmetic "
            "unless you tell it to with fast-math.",
        ),
        _q(
            "What does -ffast-math actually give up?",
            "Associativity, the special handling of NaN and infinity, and "
            "sometimes denormals. In exchange the compiler can vectorise and "
            "reorder freely. It is a reasonable trade in a graphics kernel "
            "and a bad one anywhere the numbers are somebody's money.",
        ),
        _q(
            "What is a denormal, and why does it matter for latency?",
            "A number too small to be represented in the normal form, so it "
            "loses precision gradually rather than flushing to zero. On some "
            "hardware operating on them is dramatically slower — tens of "
            "cycles instead of one — which shows up as a mysterious slowdown "
            "when a signal decays toward zero.",
        ),
        _q(
            "How do you sum a large array of floats accurately?",
            "Kahan summation carries the lost low-order bits in a "
            "compensation term and adds them back, which keeps the error "
            "roughly constant instead of growing with the count. Pairwise "
            "summation is cheaper and nearly as good. Plain accumulation into "
            "a wider type helps too.",
        ),
        _q(
            "What is the difference between round-half-up and banker's "
            "rounding?",
            "Round-half-up always rounds .5 away from zero; banker's rounding "
            "goes to the nearest even, so half the ties go each way. Banker's "
            "is the IEEE default because it does not bias a long series of "
            "roundings upward — which matters when you are rounding money "
            "millions of times.",
        ),
        _q(
            "Why does converting a float to an int truncate rather than "
            "round?",
            "Because C and most languages inherited truncation toward zero as "
            "the conversion rule. So (int)2.9 is 2 and (int)-2.9 is -2. If "
            "you want rounding you have to ask for it, and adding 0.5 before "
            "truncating is wrong for negatives.",
        ),
    ),
)


_BUILD = Topic(
    id="build-linking",
    name="Builds & Linking",
    order=70,
    blurb="What happens between your source file and something that runs.",
    questions=(
        _q(
            "What are the stages between a .cpp file and an executable?",
            "The preprocessor expands includes and macros into one "
            "translation unit; the compiler turns that into an object file "
            "with unresolved symbols; the linker matches those symbols across "
            "object files and libraries and produces the binary. Most "
            "confusing errors are the linker's, and they mean a symbol was "
            "declared but never defined, or defined twice.",
        ),
        _q(
            "What is the one definition rule?",
            "A symbol may be declared many times but defined exactly once "
            "across the whole program. Inline functions and templates are the "
            "exception: they may be defined in every translation unit as long "
            "as the definitions are identical, and the linker folds them "
            "together.",
        ),
        _q(
            "Why does a header need include guards?",
            "Because a translation unit can reach the same header by more "
            "than one path, and defining the same type twice is an error. A "
            "guard or #pragma once makes the second inclusion a no-op.",
        ),
        _q(
            "What is the difference between static and dynamic linking?",
            "Static copies the library into your binary at link time: bigger "
            "file, no runtime dependency, and a rebuild to pick up a fix. "
            "Dynamic resolves at load time from a shared object: smaller "
            "binary, shared pages across processes, and a version to get "
            "wrong.",
        ),
        _q(
            "What does inline actually mean in C++?",
            "Not 'please inline this'. It means the symbol may be defined in "
            "several translation units without breaking the one definition "
            "rule. Whether the call is inlined is entirely the compiler's "
            "decision, based on size and its own heuristics.",
        ),
        _q(
            "Why can a template's definition not usually live in a .cpp file?",
            "Because the compiler must see the definition to instantiate it "
            "for a given type, and it only sees one translation unit at a "
            "time. Hence templates live in headers, or you explicitly "
            "instantiate the types you need.",
        ),
        _q(
            "What is name mangling for?",
            "C++ encodes the parameter types and namespace into the symbol "
            "name so overloads can coexist in one object file. It is also why "
            "calling C from C++ needs an extern C block — to turn the "
            "mangling off so the names match.",
        ),
        _q(
            "What is a translation unit?",
            "One source file after preprocessing — so the file plus "
            "everything it included, expanded. The compiler works on exactly "
            "one at a time, which is why it cannot see across files and why "
            "link-time optimisation exists.",
        ),
        _q(
            "What does link-time optimisation buy you?",
            "It defers real code generation to the link, when the whole "
            "program is visible, so calls across translation units can be "
            "inlined and dead code across the whole binary can be dropped. "
            "The cost is link time, which can go from seconds to minutes.",
        ),
        _q(
            "Why is the order of libraries on the link line significant?",
            "With traditional Unix linkers, each library is scanned once for "
            "the symbols still unresolved at that point. So a library must "
            "come after the thing that uses it, and a circular dependency "
            "needs the library listed twice or wrapped in a group.",
        ),
        _q(
            "What is the difference between a debug and a release build, "
            "beyond speed?",
            "Optimisation reorders and eliminates code, so a debugger's line "
            "numbers and variable values stop matching what you wrote. "
            "Release also usually drops assertions, which means a bug that "
            "an assert would have caught now runs on. Debug builds can also "
            "hide races by being slow enough not to interleave.",
        ),
        _q(
            "What are debug symbols, and can you keep them in production?",
            "A table mapping addresses back to function names, files and "
            "lines. You can and should keep them — build with them, then "
            "split them into a separate file and ship the stripped binary. "
            "Without them a production stack trace is a list of hex "
            "addresses.",
        ),
    ),
)


_PROBABILITY = Topic(
    id="probability",
    name="Probability & Expectation",
    order=80,
    blurb="The questions every quant first round asks, and the reasoning behind them.",
    questions=(
        _q(
            "What is the expected number of coin flips to get two heads in a "
            "row?",
            "Six. Set up states by how far along you are: from zero heads "
            "E0 = 1 + half E1 + half E0, and from one head E1 = 1 + half of "
            "zero + half E0. Solving gives E0 = 6. The method matters more "
            "than the number — almost every version of this question is a "
            "small system of state equations.",
            "And for three in a row?",
        ),
        _q(
            "You have 100 doors and open one at random until you find the "
            "prize. What is the expected number opened?",
            "50.5. By symmetry the prize is equally likely in any position, "
            "so the expected position is the average of 1 to 100. Linearity "
            "of expectation gets you there without summing a series.",
        ),
        _q(
            "What is Bayes' theorem, and when does it surprise people?",
            "The probability of A given B is the probability of B given A, "
            "times the probability of A, over the probability of B. It "
            "surprises people when the base rate is small: a test that is 99 "
            "per cent accurate for a condition affecting one in ten thousand "
            "still means a positive result is usually wrong.",
        ),
        _q(
            "Why is linearity of expectation so useful?",
            "Because it holds whether or not the variables are independent. "
            "So you can break a complicated count into indicator variables, "
            "add up their individual probabilities, and never touch the joint "
            "distribution. Most hard-looking counting questions collapse this "
            "way.",
        ),
        _q(
            "What is the difference between expectation and median, and when "
            "does it matter?",
            "The mean is pulled by the tail; the median is not. For anything "
            "with a heavy tail — latency, returns, loss — the mean can be a "
            "number that almost never happens. That is why latency is quoted "
            "at percentiles rather than as an average.",
        ),
        _q(
            "You draw from a fair coin until the first head. What is the "
            "expected number of draws?",
            "Two. It is geometric with p one half, and the expectation of a "
            "geometric is one over p. The one-line derivation is E = 1 + half "
            "E, since a tail puts you back where you started.",
        ),
        _q(
            "What is a martingale, in plain terms?",
            "A process whose expected next value, given everything so far, is "
            "exactly where it is now. A fair game. It is the formalisation of "
            "'no strategy based on the past can give you an edge', which is "
            "why efficient-market arguments reach for it.",
        ),
        _q(
            "What is the birthday problem, and why is the answer so small?",
            "With 23 people the chance two share a birthday passes a half. It "
            "feels wrong because you instinctively count people rather than "
            "pairs — 23 people make 253 pairs, and each pair is a chance.",
        ),
        _q(
            "What is the variance of a sum of independent variables?",
            "The sum of the variances. Not of the standard deviations — those "
            "add in quadrature. It is why the standard deviation of an n-step "
            "random walk grows with the square root of n, not with n.",
        ),
        _q(
            "How would you simulate a fair coin from a biased one?",
            "Von Neumann's trick: flip twice. Heads-tails and tails-heads are "
            "equally likely whatever the bias, so call the first heads and "
            "the second tails, and discard the two matching outcomes. It "
            "costs you flips but needs no knowledge of the bias.",
        ),
        _q(
            "What does the central limit theorem actually say?",
            "That the sum of many independent variables with finite variance "
            "tends to a normal distribution, whatever the individual "
            "distributions were. The catch is 'finite variance' — for heavy "
            "tailed distributions it does not apply, which is exactly the "
            "case financial returns keep turning out to be.",
        ),
        _q(
            "Two players flip a fair coin; the first to lead by two wins. "
            "What is the probability the first player wins?",
            "A half, by symmetry — the rules treat both players identically. "
            "Recognising a symmetry argument saves a page of algebra, and "
            "spotting when it does not apply is the actual skill.",
        ),
    ),
)


_MICROSTRUCTURE = Topic(
    id="microstructure",
    name="Market Microstructure",
    order=90,
    blurb="How a market actually works underneath the price.",
    questions=(
        _q(
            "What is the bid-ask spread, and what is a market maker being "
            "paid for?",
            "The gap between the best price someone will buy at and the best "
            "someone will sell at. A market maker quotes both sides and earns "
            "the spread for providing immediacy — you can trade now rather "
            "than waiting for a natural counterparty. The spread is the price "
            "of that immediacy, and it compensates for inventory and adverse "
            "selection risk.",
        ),
        _q(
            "What is adverse selection?",
            "The people most eager to trade against your quote are the ones "
            "who know something you do not. So a market maker's fills are "
            "biased toward the trades they would rather not have had, and the "
            "spread has to be wide enough to cover that.",
            "How does that change when the market is moving fast?",
        ),
        _q(
            "What is the difference between a limit order and a market order?",
            "A limit order names a price and waits, so you control the price "
            "and not whether you trade. A market order takes whatever is "
            "there, so you control that you trade and not at what price. "
            "Limit orders provide liquidity; market orders take it.",
        ),
        _q(
            "What does price-time priority mean?",
            "Orders at a better price are filled first, and within the same "
            "price the earlier order goes first. It is why latency matters "
            "for a passive strategy: being first in the queue at a price is "
            "worth something real.",
        ),
        _q(
            "What is slippage?",
            "The difference between the price you expected and the price you "
            "got. It comes from the market moving between your decision and "
            "your fill, and from your own order walking up the book when it "
            "is bigger than the top level.",
        ),
        _q(
            "What is market impact, and why is it not linear?",
            "The price moves against you as you trade, because you are "
            "consuming liquidity and revealing information. Impact tends to "
            "grow roughly with the square root of size rather than linearly, "
            "which is why large orders are split up and worked over time.",
        ),
        _q(
            "What is VWAP used for?",
            "As a benchmark. If you have to buy a large amount over a day, "
            "beating the volume-weighted average price means you did better "
            "than trading uniformly with the market. It is also the target "
            "for execution algorithms that slice an order to match the "
            "volume profile.",
        ),
        _q(
            "Why does an exchange feed use multicast?",
            "So every subscriber gets the same message at the same time, from "
            "one send. It is efficient, and it is fair — nobody is later "
            "because they are further down a list of recipients.",
        ),
        _q(
            "What is the difference between top of book and full depth?",
            "Top of book is just the best bid and ask; full depth is every "
            "resting order level. Depth is far more data and tells you where "
            "the liquidity actually is — but it costs bandwidth and "
            "processing you may not be able to afford in the hot path.",
        ),
        _q(
            "What is a fill-or-kill order, and why would you use one?",
            "It executes completely and immediately or not at all. You use it "
            "when a partial fill is worse than no fill — because it leaves "
            "you with unwanted inventory or reveals your intent without "
            "getting the position on.",
        ),
        _q(
            "Why is the tick size significant?",
            "It sets the minimum spread and therefore how much queue position "
            "is worth. A large tick relative to the price means the spread "
            "cannot narrow, so competition happens in the queue rather than "
            "on price — and being early matters more.",
        ),
        _q(
            "What is latency arbitrage?",
            "Acting on a price change on one venue before another venue's "
            "quotes have updated. It is a race, which is why the arms race in "
            "colocation and microwave links exists, and why some venues have "
            "introduced speed bumps to defuse it.",
        ),
    ),
)


MORE_TOPICS: tuple[Topic, ...] = (
    _FLOAT,
    _BUILD,
    _PROBABILITY,
    _MICROSTRUCTURE,
)
