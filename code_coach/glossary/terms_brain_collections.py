"""Words the Brain Drills collection, loop and list packs teach: sets and their operations, defaults, min/max/sum,
sorting (stable, key function, comparator), swapping, accumulators, negative indexes, steps, map/filter/reduce in
Python, and looping with an index in JavaScript."""

from __future__ import annotations

from .entry import Entry, both, js, py

TERMS: list[Entry] = [
    *both(
        "set-operations",
        "Union, intersection and difference",
        "Combining two sets: union is everything in either, intersection is only what is in both, difference is what is in the first but not the second.",
        priority=50,
        aka=("union", "intersection", "difference", "symmetric difference", "set operations", "set operation"),
        python=dict(
            see=("set", "in-operator"),
            rules=(
                "a | b is the union, a & b the intersection, a - b the difference and a ^ b what is in exactly one of them.",
                "The methods do the same: a.union(b), a.intersection(b), a.difference(b).",
                "Order matters for difference: {1, 2, 3} - {2} is {1, 3} but {2} - {1, 2, 3} is empty.",
                "A set has no order, so print sorted(result) when you need a stable look.",
            ),
            detect=(r"\bset\([^)]*\)\s*[|&^-]\s*set\(", r"\.(?:union|intersection|difference|symmetric_difference)\("),
            example="""
                a = {1, 2, 3}
                b = {2, 3, 4}
                print(sorted(a | b), sorted(a & b), sorted(a - b), sorted(b - a))
            """,
            out="[1, 2, 3, 4] [2, 3] [1] [4]",
        ),
        javascript=dict(
            see=("set", "filter"),
            rules=(
                "The older way to combine sets: union is new Set([...a, ...b]).",
                "Intersection keeps the items of a that b has: [...a].filter((x) => b.has(x)).",
                "Difference keeps the items of a that b does not have: [...a].filter((x) => !b.has(x)).",
                "Order matters for difference: a minus b is not b minus a.",
            ),
            detect=(r"\.has\(", r"\bnew\s+Set\(\[\s*\.\.\."),
            example="""
                const a = new Set([1, 2, 3]);
                const b = new Set([2, 3, 4]);
                const union = [...new Set([...a, ...b])];
                const inter = [...a].filter((x) => b.has(x));
                const diff = [...a].filter((x) => !b.has(x));
                console.log(union, inter, diff);
            """,
            out="[ 1, 2, 3, 4 ] [ 2, 3 ] [ 1 ]",
        ),
    ),
    *js(
        "membership",
        "Membership",
        "Asking whether something is among a collection's items (or keys). The answer is true or false.",
        see=("array", "set", "object"),
        priority=40,
        aka=("contains", "includes", "has", "in operator"),
        detect=(r"\.(?:includes|has)\(", r"\bin\s+[\w$]+\s*\)"),
        rules=(
            "arr.includes(x) asks about the items of an array; set.has(x) asks about a set (and is fast).",
            "'key' in obj asks about KEYS, not values: 'a' in {a: 1} is true but 1 in {a: 1} is false.",
            "On an array, in looks at the positions: 1 in [5, 6] is true (position 1 exists) but 6 in [5, 6] is false.",
        ),
        example="""
            console.log([1, 2].includes(2), new Set([1]).has(2), "a" in { a: 1 }, 1 in [5, 6], 6 in [5, 6]);
        """,
        out="true false true true false",
    ),
    *both(
        "default-value",
        "Default value",
        "The value used when nothing better was given: a missing key, an argument left out, an empty result.",
        see=("short-circuit", "falsy", "default-parameter"),
        priority=40,
        aka=("default", "fallback", "default values"),
        python=dict(
            see=("short-circuit", "falsy", "dict", "default-parameter"),
            rules=(
                "d.get(key, 0) gives 0 when the key is missing. It only checks the key: {'a': None}.get('a', 0) is None, not 0.",
                "x or 'anon' falls back for ANY falsy x, including 0 and '', so 0 or 5 is 5.",
                "d.setdefault(key, []) fetches the value and stores the default when the key was missing.",
            ),
            detect=(r"\.(?:get|setdefault)\([^,()]+,",),
            example="""
                d = {"a": 1}
                print(d.get("a", 0), d.get("b", 0), None or "anon", 0 or 5)
            """,
            out="1 0 anon 5",
        ),
        javascript=dict(
            see=("nullish", "short-circuit", "falsy", "default-parameter"),
            rules=(
                "x ?? 'anon' falls back only for null and undefined, so 0 ?? 5 is 0.",
                "x || 'anon' falls back for ANY falsy x, including 0 and '', so 0 || 5 is 5.",
                "A destructuring default only applies to undefined: const { x = 9 } = { x: null } leaves x as null.",
            ),
            detect=(r"\?\?|\|\|", r"[{,]\s*[\w$]+\s*=\s*[^=,}]+[,}]\s*=\s*"),
            example="""
                const o = { a: 1 };
                console.log(o.a ?? 0, o.b ?? 0, undefined ?? "anon", 0 || 5, 0 ?? 5);
            """,
            out="1 0 anon 5 0",
        ),
    ),
    *both(
        "min-max",
        "Minimum and maximum",
        "The smallest and the largest item of a collection.",
        see=("sum", "sorting", "negative-number"),
        priority=40,
        aka=("minimum", "maximum", "min", "max", "smallest", "largest", "biggest", "lowest", "highest"),
        python=dict(
            see=("sum", "sorting", "key-function"),
            rules=(
                "min(nums) and max(nums) take a list; min(3, 1, 2) takes the values directly.",
                "key= says what to compare by: max(words, key=len) is the longest word, and the first one wins a tie.",
                "On an empty list they raise a ValueError, unless you give a default: max([], default=0) is 0.",
            ),
            detect=(r"\b(?:min|max)\(",),
            example="""
                nums = [3, -1, 7]
                print(min(nums), max(nums), min("pear", "apple"), max([], default=0))
            """,
            out="-1 7 apple 0",
        ),
        javascript=dict(
            see=("sum", "sorting", "spread-rest"),
            rules=(
                "Math.min and Math.max take separate values, not an array: Math.max(...nums) spreads the array into values.",
                "Math.max([1, 2]) is NaN, because an array with two items is not a number.",
                "With no values they give the identity: Math.max() is -Infinity and Math.min() is Infinity.",
            ),
            detect=(r"\bMath\.(?:min|max)\(",),
            example="""
                const nums = [3, -1, 7];
                console.log(Math.min(...nums), Math.max(...nums), Math.max(), Math.max(...[]));
            """,
            out="-1 7 -Infinity -Infinity",
        ),
    ),
    *both(
        "sum",
        "Sum (total)",
        "Adding up all the numbers in a collection.",
        see=("accumulator", "min-max", "reduce"),
        priority=40,
        aka=("total", "add up", "adding up", "summing"),
        python=dict(
            rules=(
                "sum(nums) adds the items; sum([]) is 0.",
                "The second argument is where to start: sum(nums, 10) adds 10 to the total.",
                "sum does not join strings (sum(['a', 'b']) is a TypeError): use ''.join(...) for that.",
            ),
            detect=(r"\bsum\(",),
            example="""
                print(sum([1, 2, 3]), sum([]), sum([[1], [2]], []), sum([0.5, 0.25]))
            """,
            out="6 0 [1, 2] 0.75",
        ),
        javascript=dict(
            rules=(
                "There is no built-in sum: use reduce, starting from 0: nums.reduce((t, x) => t + x, 0).",
                "Leave the starting 0 out and an empty array throws a TypeError: [].reduce((a, b) => a + b) fails.",
                "If the items are strings, + joins them instead of adding: ['1', '2'].reduce((t, x) => t + x, 0) is '012'.",
            ),
            detect=(r"\.reduce\(",),
            example="""
                const sum = (a) => a.reduce((t, x) => t + x, 0);
                console.log(sum([1, 2, 3]), sum([]), [1, 2, 3].reduce((t, x) => t + x));
            """,
            out="6 0 6",
        ),
    ),
    *both(
        "negative-number",
        "Negative numbers",
        "Numbers below zero. They behave in surprising ways with division, remainders, rounding and 'smallest'.",
        see=("modulo", "floor-division", "rounding"),
        priority=30,
        aka=("negative", "negatives", "minus", "below zero", "abs", "absolute value", "sign"),
        python=dict(
            rules=(
                "-7 // 2 is -4, not -3: floor division rounds toward the smaller number.",
                "-7 % 2 is 1: the remainder takes the sign of the right side, so it is never negative here.",
                "int(-3.9) cuts the decimals and gives -3, abs(-7) is 7, and min(-3, -10) is -10: more minus means smaller.",
            ),
            example="""
                print(-7 // 2, -7 % 2, abs(-7), int(-3.9), min(-3, -10))
            """,
            out="-4 1 7 -3 -10",
        ),
        javascript=dict(
            rules=(
                "Math.floor(-7 / 2) is -4: Math.floor rounds toward the smaller number.",
                "-7 % 2 is -1: the remainder takes the sign of the LEFT side, unlike Python.",
                "Math.trunc(-3.9) cuts the decimals and gives -3, Math.abs(-7) is 7, and Math.min(-3, -10) is -10: more minus means smaller.",
            ),
            example="""
                console.log(Math.floor(-7 / 2), -7 % 2, Math.abs(-7), Math.trunc(-3.9), Math.min(-3, -10));
            """,
            out="-4 -1 7 -3 -10",
        ),
    ),
    *both(
        "sorting",
        "Sorting",
        "Putting the items of a collection in order, smallest to largest by default.",
        see=("stable-sort", "string-comparison", "mutable"),
        priority=45,
        aka=("sort", "sorted", "order", "ordering", "sort order", "ascending", "descending"),
        python=dict(
            see=("stable-sort", "key-function", "string-comparison", "mutable"),
            rules=(
                "sorted(x) gives a NEW sorted list and leaves x alone; x.sort() sorts x itself and returns None.",
                "reverse=True sorts from largest to smallest; key= says what to sort by.",
                "Strings sort by character code, so capitals come first: sorted(['b', 'A', 'a']) is ['A', 'a', 'b'].",
                "Mixing types such as numbers and text is a TypeError.",
            ),
            detect=(r"\bsorted\(|\.sort\(",),
            example="""
                a = [3, 1, 2]
                print(sorted(a), a)
                print(a.sort(), a)
            """,
            out="[1, 2, 3] [3, 1, 2]\nNone [1, 2, 3]",
        ),
        javascript=dict(
            see=("stable-sort", "comparator", "string-comparison", "mutable"),
            rules=(
                "arr.sort() sorts the array itself AND returns that same array; copy first with [...arr].sort() to keep the original.",
                "With no comparator it sorts as TEXT: [10, 9, 1].sort() is [1, 10, 9]. Numbers need (a, b) => a - b.",
                "Capitals sort before lower case, as in any string comparison.",
            ),
            detect=(r"\.(?:sort|toSorted)\(",),
            example="""
                const a = [10, 9, 1];
                console.log([...a].sort(), [...a].sort((x, y) => x - y), a);
            """,
            out="[ 1, 10, 9 ] [ 1, 9, 10 ] [ 10, 9, 1 ]",
        ),
    ),
    *both(
        "reverse",
        "Reverse",
        "Turning a collection around so the last item comes first.",
        see=("sorting", "slice", "mutable"),
        priority=40,
        aka=("reversed", "reversing", "backwards"),
        python=dict(
            see=("sorting", "slice", "mutable"),
            rules=(
                "a.reverse() flips the list in place and returns None.",
                "a[::-1] and list(reversed(a)) make a reversed copy and leave a alone.",
                "sorted(a, reverse=True) is not the same: it sorts, largest first.",
            ),
            detect=(r"\breversed\(|\.reverse\(|\[::-1\]",),
            example="""
                a = [1, 2, 3]
                print(a[::-1], list(reversed(a)), a)
                a.reverse()
                print(a)
            """,
            out="[3, 2, 1] [3, 2, 1] [1, 2, 3]\n[3, 2, 1]",
        ),
        javascript=dict(
            see=("sorting", "slice", "mutable"),
            rules=(
                "a.reverse() flips the array in place AND returns that same array.",
                "To keep the original, copy first: [...a].reverse().",
                "Strings have no reverse: turn one into an array of characters, reverse, and join: [...s].reverse().join('').",
            ),
            detect=(r"\.(?:reverse|toReversed)\(",),
            example="""
                const a = [1, 2, 3];
                const b = [...a].reverse();
                console.log(b, a);
                a.reverse();
                console.log(a);
            """,
            out="[ 3, 2, 1 ] [ 1, 2, 3 ]\n[ 3, 2, 1 ]",
        ),
    ),
    *both(
        "stable-sort",
        "Stable sort",
        "A sort that keeps items which compare as equal in the order they already had.",
        see=("sorting",),
        priority=45,
        aka=("stability", "stable", "sort stability", "equal items keep their order"),
        python=dict(
            see=("sorting", "key-function"),
            rules=(
                "Python's sort and sorted are guaranteed stable.",
                "So sorting by a key leaves ties in their original order: sorted(['bb', 'a', 'cc', 'd'], key=len) puts 'a' before 'd', and 'bb' before 'cc'.",
                "reverse=True keeps ties in their original order too (it does not flip them).",
            ),
            example="""
                words = ["bb", "a", "cc", "d"]
                print(sorted(words, key=len))
            """,
            out="['a', 'd', 'bb', 'cc']",
        ),
        javascript=dict(
            see=("sorting", "comparator"),
            rules=(
                "Array sort is guaranteed stable in current JavaScript.",
                "So ties keep their original order: ['bb', 'a', 'cc', 'd'] sorted by length gives 'a' before 'd', and 'bb' before 'cc'.",
                "Sort twice to sort by two things: sort by the less important one first, then by the main one.",
            ),
            example="""
                console.log(["bb", "a", "cc", "d"].sort((x, y) => x.length - y.length));
            """,
            out="[ 'a', 'd', 'bb', 'cc' ]",
        ),
    ),
    *py(
        "key-function",
        "Key function",
        "A function you hand to sorted, min or max that turns each item into the thing to compare by, such as len or str.lower.",
        see=("sorting", "stable-sort", "lambda", "min-max"),
        priority=50,
        aka=("key", "sort key", "key=", "comparator", "cmp_to_key", "sort by"),
        detect=(r"\bkey\s*=\s*[A-Za-z_]",),
        rules=(
            "sorted(words, key=len) sorts by length. The function gets one item and returns what to compare.",
            "Pass the function itself, with no brackets: key=len, not key=len().",
            "min and max take key= too: max(words, key=len) is the longest word.",
            "The key decides the order only; the items stay as they were.",
        ),
        example="""
            words = ["pear", "Fig", "apple"]
            print(sorted(words), sorted(words, key=str.lower), max(words, key=len))
        """,
        out="['Fig', 'apple', 'pear'] ['apple', 'Fig', 'pear'] apple",
    ),
    *js(
        "comparator",
        "Comparator",
        "The function you give sort to say which of two items comes first: it returns a negative number, zero or a positive number.",
        see=("sorting", "stable-sort", "arrow-function", "callback"),
        priority=50,
        aka=("compare function", "key function", "sort callback", "comparison function"),
        detect=(r"\.sort\(\s*(?:\(|function|[\w$]+\s*=>|[\w$]+\s*\))",),
        rules=(
            "(a, b) => a - b sorts numbers smallest first; (a, b) => b - a sorts largest first.",
            "To sort by a key, compare the keys: (a, b) => a.age - b.age. For text use a.name.localeCompare(b.name).",
            "It must return a number: (a, b) => a > b returns true or false, which is a bug.",
        ),
        example="""
            const byLen = (a, b) => a.length - b.length;
            console.log(["pear", "fig", "apple"].sort(byLen), [3, 1, 2].sort((a, b) => b - a));
        """,
        out="[ 'fig', 'pear', 'apple' ] [ 3, 2, 1 ]",
    ),
    *both(
        "swap",
        "Swap",
        "Exchanging the values of two variables, so a holds what b held and b holds what a held.",
        see=("unpacking", "assignment", "reassign"),
        priority=40,
        aka=("swapping", "exchange", "swap variables", "temp variable"),
        python=dict(
            rules=(
                "a, b = b, a swaps in one line: the right side is worked out completely first.",
                "a = b followed by b = a does NOT swap: after the first line both hold the old b.",
                "The same trick swaps items of a list: nums[0], nums[1] = nums[1], nums[0].",
            ),
            example="""
                a, b = 1, 2
                a, b = b, a
                print(a, b)
            """,
            out="2 1",
        ),
        javascript=dict(
            rules=(
                "[a, b] = [b, a] swaps in one line: the right side is built completely first.",
                "a = b followed by b = a does NOT swap: after the first line both hold the old b (a third variable is needed).",
                "End the line before it with a semicolon: without one JavaScript reads the [ as indexing the previous line.",
            ),
            example="""
                let a = 1, b = 2;
                [a, b] = [b, a];
                console.log(a, b);
            """,
            out="2 1",
        ),
    ),
    *both(
        "accumulator",
        "Accumulator",
        "A variable that builds up a result as a loop goes round: a running total, a product, a growing list or string.",
        see=("loop", "augmented-assignment", "sum"),
        priority=45,
        aka=("running total", "total", "running sum", "accumulate", "accumulating"),
        python=dict(
            rules=(
                "Start it with a neutral value BEFORE the loop: 0 for a total, 1 for a product, '' for text, [] for a list.",
                "Create it inside the loop and it is reset on every pass, so only the last item survives.",
                "total += n is short for total = total + n.",
            ),
            example="""
                product = 1
                for n in [2, 3, 4]:
                    product *= n
                print(product)
            """,
            out="24",
        ),
        javascript=dict(
            rules=(
                "Start it with a neutral value BEFORE the loop: 0 for a total, 1 for a product, '' for text, [] for an array.",
                "Create it inside the loop and it is reset on every pass, so only the last item survives.",
                "reduce is the same idea in one call: its first argument to the callback is the accumulator.",
            ),
            example="""
                let product = 1;
                for (const n of [2, 3, 4]) {
                  product *= n;
                }
                console.log(product);
            """,
            out="24",
        ),
    ),
    *both(
        "negative-index",
        "Negative index",
        "Counting positions from the end instead of the start: -1 is the last item, -2 the one before it.",
        see=("index", "slice", "length"),
        priority=50,
        aka=("negative indexes", "negative indices", "last item", "index from the end", "at"),
        python=dict(
            see=("index", "slice", "len"),
            rules=(
                "a[-1] is the last item and a[-len(a)] is the first, so a[-1] is the same as a[len(a) - 1].",
                "It works on strings and tuples too: 'hello'[-1] is 'o'.",
                "Past the start it is an IndexError: a three-item list has no a[-4]. Slices never raise.",
            ),
            detect=(r"\[\s*-\d+\s*\]",),
            example="""
                a = [10, 20, 30]
                print(a[-1], a[-2], "hello"[-1], a[len(a) - 1])
            """,
            out="30 20 o 30",
        ),
        javascript=dict(
            rules=(
                "arr[-1] does NOT count from the end: it looks for a property named '-1' and gives undefined.",
                "Use arr.at(-1) for the last item and arr.at(-2) for the one before; strings have at() too.",
                "Past the start at() gives undefined (no error): [1, 2, 3].at(-4) is undefined.",
            ),
            detect=(r"\[\s*-\d+\s*\]", r"\.at\(\s*-"),
            example="""
                const a = [10, 20, 30];
                console.log(a[-1], a.at(-1), a.at(-3), "hello".at(-1));
            """,
            out="undefined 30 10 o",
        ),
    ),
    *both(
        "step",
        "Step",
        "How far a loop or a slice jumps each time: a step of 2 takes every other item, a negative step goes backwards.",
        priority=40,
        aka=("stride", "step size", "increment by", "every other"),
        python=dict(
            see=("range", "slice", "loop"),
            rules=(
                "range(start, stop, step): range(0, 10, 3) is 0, 3, 6, 9. The stop is never included.",
                "A negative step counts down, and then the start must be the bigger number: range(5, 0, -2) is 5, 3, 1.",
                "A slice has the same third part: 'abcdef'[::2] is 'ace' and 'abcdef'[::-2] is 'fdb'. A step of 0 is a ValueError.",
            ),
            detect=(r"\brange\([^()]*,[^()]*,[^()]*\)", r"\[[^\[\]\n]*:[^\[\]\n]*:[^\[\]\n]*\]"),
            example="""
                print(list(range(0, 10, 3)), list(range(5, 0, -2)), "abcdef"[::2], "abcdef"[::-2])
            """,
            out="[0, 3, 6, 9] [5, 3, 1] ace fdb",
        ),
        javascript=dict(
            see=("slice", "loop", "for-loop"),
            rules=(
                "A step is the part of the for loop that runs after each pass: i += 2 takes every other number, i -= 1 counts down.",
                "JavaScript slice has no step (slice(0, 10, 3) ignores the 3): to take every other item, filter on the position.",
                "Counting down starts at the big number and tests with > or >=: for (let i = 5; i > 0; i -= 2).",
            ),
            detect=(r"\b[a-z_$]\w*\s*[-+]=\s*\d+\s*\)",),
            example="""
                const out = [];
                for (let i = 0; i < 10; i += 3) out.push(i);
                for (let i = 5; i > 0; i -= 2) out.push(i);
                console.log(out.join(" "));
            """,
            out="0 3 6 9 5 3 1",
        ),
    ),
    *py(
        "map",
        "map()",
        "A built-in that applies a function to every item and gives back the results, one for one.",
        see=("filter", "reduce", "lambda", "comprehension"),
        priority=50,
        aka=("map()", "map function"),
        detect=(r"\bmap\(",),
        rules=(
            "map(f, items) gives a lazy map object, not a list: wrap it in list(...) to see the results.",
            "It never changes the items: list(map(f, nums)) is a new list as long as nums.",
            "A list comprehension says the same thing: [f(x) for x in nums].",
        ),
        example="""
            nums = [1, 2, 3]
            print(list(map(lambda x: x * 2, nums)), nums)
        """,
        out="[2, 4, 6] [1, 2, 3]",
    ),
    *py(
        "filter",
        "filter()",
        "A built-in that keeps only the items for which a function says yes (gives something truthy).",
        see=("map", "reduce", "lambda", "comprehension"),
        priority=50,
        aka=("filter()", "filter function"),
        detect=(r"\bfilter\(",),
        rules=(
            "filter(f, items) gives a lazy filter object: wrap it in list(...) to see the items kept.",
            "The items themselves are kept, not f's answers: filter(lambda x: x > 1, [1, 2, 3]) keeps 2 and 3.",
            "filter(None, items) drops every falsy item (0, '', None...).",
            "A list comprehension with an if does the same: [x for x in nums if x > 1].",
        ),
        example="""
            print(list(filter(lambda x: x % 2 == 0, [1, 2, 3, 4])), list(filter(None, [0, 1, "", "a"])))
        """,
        out="[2, 4] [1, 'a']",
    ),
    *py(
        "reduce",
        "reduce()",
        "A function from functools that folds a whole list into one value by combining the items two at a time.",
        see=("map", "filter", "accumulator", "sum"),
        priority=50,
        aka=("reduce()", "functools.reduce", "fold", "fold left"),
        detect=(r"\breduce\(",),
        rules=(
            "It must be imported: from functools import reduce.",
            "reduce(f, items, start): f(total, item) is called for each item and returns the new total; start is the first total.",
            "Without a start, the first item is the first total, and an empty list is a TypeError.",
        ),
        example="""
            from functools import reduce
            print(reduce(lambda total, x: total + x, [1, 2, 3], 0), reduce(lambda a, b: a * b, [2, 3, 4]))
        """,
        out="6 24",
    ),
    *js(
        "enumerate-zip",
        "Looping with an index (enumerate and zip)",
        "JavaScript has no enumerate or zip: you get the position from entries() or the callback's second argument, and pair two arrays by position yourself.",
        see=("for-loop", "index", "map", "unpacking"),
        priority=40,
        aka=("enumerate", "zip", "entries", "loop with index", "index in a loop"),
        detect=(r"\.entries\(\)", r"\.(?:map|forEach|filter)\(\s*\(\s*[\w$]+\s*,\s*[\w$]+\s*\)\s*=>"),
        rules=(
            "for (const [i, v] of arr.entries()) gives the position and the item together.",
            "forEach and map call back with (item, index, array): arr.map((v, i) => ...).",
            "To pair two arrays, use the position: a.map((x, i) => [x, b[i]]).",
        ),
        example="""
            const a = ["x", "y"];
            const b = [1, 2];
            for (const [i, v] of a.entries()) console.log(i, v);
            console.log(a.map((v, i) => v + b[i]));
        """,
        out="0 x\n1 y\n[ 'x1', 'y2' ]",
    ),
    *js(
        "equality",
        "Equality",
        "Asking whether two values are 'the same'. JavaScript has more than one way to ask, and the answers differ.",
        see=("strict-equality", "loose-equality", "reference", "nan"),
        priority=55,
        aka=("equal", "equals", "same value", "object.is", "same"),
        detect=(r"\bObject\.is\(",),
        rules=(
            "=== is true when the type and the value are both the same; == converts first (1 == '1' is true), so prefer ===.",
            "Objects and arrays are equal only if they are the very same object: [1] === [1] is false.",
            "NaN === NaN is false; Object.is(NaN, NaN) is true.",
        ),
        example="""
            console.log(1 === 1, "1" == 1, [1] === [1], NaN === NaN, Object.is(NaN, NaN));
        """,
        out="true true false false true",
    ),
]
