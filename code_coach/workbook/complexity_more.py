"""Complexity notes for the intermediate and advanced tiers.

The beginner and practice shapes live in `complexity`. These are the rest of
Python's pages, and they are kept separate only for size.

Same three rules as the first file. Say what grows rather than only the
letter. Say what n is. Never claim a cost the exercise does not have — a
shape with no entry shows no panel, which is better than a panel that
guesses.

One thing worth writing down, because it nearly caused a batch of wrong
notes. Several of these pages contain a loop that runs over two or three
demonstration values — `for n in (3, -1)` — rather than over any data. That
is not a linear pass and calling it one would be false. The classification
here was cross-checked against the emitted code: every loop was inspected
for what it actually iterates, a literal tuple of demo calls or a variable
holding the data.
"""

from __future__ import annotations

from code_coach.workbook.complexity import Cost

NOTES: dict[str, Cost] = {}


def _add(label: str, note: str, *shapes: str) -> None:
    for shape in shapes:
        NOTES[shape] = Cost(label, note)


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)


# ── Constant: the work does not depend on any size ───────────

_add(
    "O(1)",
    "Constant. This is a piece of language machinery rather than a "
    "calculation — building an object, calling a method, defining a class. "
    "It does the same work whatever numbers you put in it, and the running "
    "time has nothing to grow with.",
    "class_init",
    "class_two",
    "class_method",
    "class_method_arg",
    "class_repr",
    "dataclass_use",
    "class_attr",
    "inherit_use",
    "override",
    "super_call",
    "dataclass_basic",
    "dataclass_method",
    "namedtuple_use",
    "property_use",
    "static_method",
    "class_counter",
    "eq_dunder",
    "dataclass_field_flags",
    "dataclass_kwonly",
    "namedtuple_defaults",
    "metaclass_use",
    "weakref_use",
    "descriptor_use",
    "int_str_enum",
    "enum_named",
    "slots_use",
)

_add(
    "O(1)",
    "Constant, and worth being clear why: a type hint costs nothing at all "
    "at run time. Python does not check them as the program runs — they are "
    "there for you and for the tools. The program would run at exactly this "
    "speed with every annotation deleted.",
    "type_hint_func",
    "type_hint_list",
    "optional_hint",
)

_add(
    "O(1)",
    "Constant. Reaching into a dict by key does not search it — the key is "
    "turned into a position and looked at directly, so a dict of ten and a "
    "dict of ten million cost the same to read. That is the reason a dict "
    "is the answer to so many problems that look like they need a loop.",
    "dict_get",
    "chainmap_use",
    "environ_use",
)

_add(
    "O(1)",
    "Constant. Deciding something, formatting something, taking a value "
    "apart into names — each is a fixed amount of work. Where these pages "
    "loop, they are looping over two or three demonstration values, not "
    "over data, so the loop does not make the operation linear.",
    "fmt_value",
    "tuple_unpack",
    "default_arg",
    "keyword_call",
    "ternary",
    "format_number",
    "number_bases",
    "is_vs_equals",
    "mutable_default",
    "match_stmt",
    "decimal_quantize",
    "uuid5_use",
    "casefold_compare",
)

_add(
    "O(1)",
    "Constant. Raising, catching and re-raising are cheap — building the "
    "exception and unwinding to the handler is a fixed amount of work. "
    "Exceptions are slow only when you use them for ordinary control flow "
    "and raise thousands of them; one is nothing.",
    "try_except",
    "raise_error",
    "custom_error",
    "try_else_finally",
    "error_hierarchy",
    "traceback_only",
    "warnings_use",
    "assert_use",
)

_add(
    "O(1)",
    "Constant. Wrapping a function, or making one that remembers where it "
    "was built, happens once when the definition runs. The wrapper adds a "
    "fixed amount to each later call — one extra function call — and "
    "nothing that grows.",
    "decorator",
    "closure",
    "context_manager",
    "contextmanager_fn",
    "partial_use",
    "wraps_use",
    "callable_obj",
)

_add(
    "O(1)",
    "Constant, and this is the page's point. A path is manipulated as text "
    "and structure — joining, taking the suffix, asking for the parent — "
    "and none of it touches the disk. Nothing here is waiting on a file "
    "system, which is why it is fast and also why it works for paths that "
    "do not exist.",
    "path_parts",
    "path_build",
    "path_parts_more",
)

_add(
    "O(1)",
    "Constant. Building a date, formatting one, or asking how many days "
    "apart two of them are is arithmetic on a number of days — the answer "
    "does not take longer for dates further apart.",
    "date_format",
    "date_delta",
    "strptime_use",
    "calendar_use",
    "timezone_use",
)

# ── Linear: one pass over the data ───────────────────────────

_add(
    "O(n)",
    "Linear in the length of the list. A comprehension is a loop written on "
    "one line — it visits every item once and does the same work per item, "
    "so it costs exactly what the long-hand loop costs. It is shorter to "
    "read, not faster to run.",
    "comprehension",
    "comprehension_if",
    "dict_comp",
    "set_comp_frozen",
    "map_filter",
    "generator",
    "generator_take",
    "gen_expression",
)

_add(
    "O(n)",
    "Linear, where n is the number of items. One pass, one visit each. "
    "Pairing them up with their positions, or walking two lists side by "
    "side, does not change that — it is still one step per item.",
    "enumerate_loop",
    "zip_loop",
    "zip_strict",
    "zip_to_dict",
    "dict_items",
    "chain_use",
    "accumulate_use",
    "reduce_use",
    "star_args",
    "kwargs_use",
    "math_prod",
    "batched_starmap",
    "methodcaller_use",
    "itertools_more",
    "pairwise_use",
    "transpose",
)

_add(
    "O(n)",
    "Linear, and it stops early. any returns the moment something matches "
    "and all returns the moment something does not, so the best case is one "
    "item — but the worst case is still the whole list, and worst case is "
    "what the letter describes.",
    "any_all",
    "list_find_first",
    "next_default",
)

_add(
    "O(n)",
    "Linear in the number of items. Counting as you go touches each item "
    "once and each dict update is constant, so the whole tally is one pass. "
    "The alternative — for each distinct value, count how many match — is "
    "one pass per value, and that is where the quadratic version comes "
    "from.",
    "counter_use",
    "defaultdict_count",
    "defaultdict_group",
    "dict_of_lists",
    "most_common_use",
    "counter_maths",
)

_add(
    "O(n)",
    "Linear in the length of the text, where n is the number of "
    "characters. Searching, replacing, tidying and normalising all have to "
    "look at each character — and the ones that hand back new text are "
    "building a copy that size as well, so a long string is paid for "
    "twice.",
    "text_tidy",
    "strip_affix",
    "normalize_use",
    "template_use",
    "casefold_use",
    "str_translate",
)

_add(
    "O(n)",
    "Linear in the length of the subject text. A regular expression scans "
    "left to right, and for the straightforward patterns here that is one "
    "pass. Be aware that this is the good case: some patterns with nested "
    "repetition can take exponential time on the wrong input, which is a "
    "real class of bug rather than a curiosity.",
    "regex_search",
    "regex_groups",
    "regex_findall",
    "regex_sub",
    "regex_named",
    "regex_lookahead",
    "difflib_use",
)

_add(
    "O(n)",
    "Linear in the amount of data. Reading, writing, encoding and "
    "compressing all touch every byte once. The units here are bytes rather "
    "than items, and the disk or the network is usually costing you far "
    "more than the loop is.",
    "file_write_read",
    "file_lines",
    "json_round",
    "json_default",
    "csv_read",
    "csv_write",
    "zipfile_use",
    "gzip_use",
    "configparser_use",
    "stringio_redirect",
    "struct_use",
    "shutil_copy",
    "path_glob",
    "hashlib_use",
    "base64_use",
)

_add(
    "O(n)",
    "Linear in the number of items, with n being how many there are rather "
    "than how large they are. Building a set from a list touches each item "
    "once, and membership afterwards is constant — which is the whole "
    "reason to build one.",
    "set_maths",
    "set_ops",
    "unique_seen",
)

_add(
    "O(n)",
    "Linear in the size of the slice, not the list. Slicing copies, so "
    "asking for half a million items costs half a million even though the "
    "expression is three characters long. A step or a negative direction "
    "does not change that.",
    "slice_step",
    "copy_depth",
    "deep_copy",
)

# ── Recursion over a structure ───────────────────────────────

_add(
    "O(n)",
    "Linear in the number of nodes, because the recursion visits each "
    "exactly once. The depth of the nesting decides how much call stack is "
    "used, not how much work is done — a deep chain and a wide fan both "
    "cost one visit per node.",
    "recurse_nested",
    "iter_protocol",
    "yield_from",
)

_add(
    "O(n)",
    "Linear in n, once the answers are remembered. Without the cache this "
    "recursion recomputes the same subproblems over and over and the cost "
    "grows exponentially — the cache turns it into one calculation per "
    "distinct input, which is the whole point of both pages.",
    "memo_dict",
    "lru_cache_use",
)

_add(
    "O(n)",
    "Linear in the number of calls, and note what it costs in memory: each "
    "call sits on the stack until it returns, so recursion n deep holds n "
    "frames at once. Python stops you at about a thousand, which is a "
    "limit you will meet on real data.",
    "recursion",
)

# ── Sorting ──────────────────────────────────────────────────

_add(
    "O(n log n)",
    "Sorting, which is the cost that turns up everywhere. Roughly, each "
    "item has to be compared against about log n others — a thousand items "
    "is around ten thousand comparisons, not a million. Handing sorted a "
    "key changes what is compared, never how many comparisons there are.",
    "sorted_key",
    "sorted_lambda",
    "sort_tuple_key",
    "sort_by_value",
    "unique_sorted",
    "lt_dunder",
    "cmp_to_key_use",
    "itemgetter_sort",
    "sort_two_ways",
    "ordered_dataclass",
)

_add(
    "O(n log n)",
    "Sorting dominates. The fold that follows it is one pass, so the sort "
    "is what you are paying for — and it is worth noticing that sorting "
    "first is what makes the second half simple enough to be one pass at "
    "all.",
    "merge_intervals",
    "group_sorted",
)

# ── Better than linear ───────────────────────────────────────

_add(
    "O(log n)",
    "Logarithmic, and that is a remarkable thing. Every step throws away "
    "half of what is left, so doubling the data adds one step rather than "
    "doubling the work: a thousand items take about ten steps, a million "
    "about twenty. It only works on sorted data, which is what you are "
    "paying for elsewhere.",
    "bisect_use",
)

# ── Quadratic and worse ──────────────────────────────────────

_add(
    "O(n²)",
    "Quadratic, because every item is paired with every other. Ten items "
    "give forty-five pairs, a hundred give nearly five thousand, a thousand "
    "give half a million. This is fine for small collections and is the "
    "thing to look at first when something is unexpectedly slow.",
    "combinations_use",
    "product_use",
    "pairs_all",
)

_add(
    "O(2ⁿ)",
    "Exponential. Every item is either in or out, so there are two to the "
    "power n possible answers and the search looks at all of them that are "
    "not cut off early. Twenty items is a million, thirty is a billion — "
    "this is why backtracking problems come with small inputs, and why "
    "pruning early matters so much.",
    "subsets_use",
    "permutations_use",
)


_add(
    "O(n)",
    "Linear in the number of items, and the walrus changes nothing about "
    "that — it names a value in the middle of the test so it is computed "
    "once instead of twice. That is a constant factor saved per item, not a "
    "different growth rate.",
    "walrus",
)

_add(
    "O(n)",
    "Linear in how many contexts you enter, which is the page's point: the "
    "count is not known when the code is written. Each is entered once and "
    "unwound once, so the work is one pair of operations per context.",
    "exitstack_use",
)

_add(
    "O(1)",
    "Constant per value sent. The generator holds a `while True`, but that "
    "loop does not run through anything — it suspends at the yield and "
    "resumes once for each value you hand it, doing a fixed amount of work "
    "each time. The total is therefore linear in how many times you send, "
    "not in any collection.",
    "generator_send",
)


_add(
    "O(n)",
    "Linear in the number of classes in the hierarchy, which is the thing "
    "being walked — not in any data. Python works the order out once when "
    "the class is created and keeps it, so reading __mro__ is just walking "
    "a list that already exists. A deep hierarchy costs more to walk and, "
    "more to the point, more to reason about.",
    "mro_order",
)


# ── The algorithm tier ───────────────────────────────────────
#
# These get their own notes rather than sharing one. The point of those
# pages is which move to reach for, and the cost is usually the reason the
# move exists at all.

_add(
    "O(n)",
    "Linear, and that is the whole argument for the page. One pass over the "
    "items, and each dict update is constant, so counting a million things "
    "costs a million steps. The version people write first asks, for each "
    "distinct value, how many items match it — that is a pass per value, "
    "and it is quadratic.",
    "algo_tally",
)

_add(
    "O(n)",
    "Linear, and it stops at the first repeat. The set is what buys that: "
    "asking whether you have seen something is constant, so the scan is one "
    "pass. Without it you would compare each item against everything before "
    "it, which is quadratic. The set trades a little memory for that.",
    "algo_seen",
)

_add(
    "O(n)",
    "Linear — one pass, with the dict answering each lookup in constant "
    "time. This is where that trade becomes obvious: checking every pair "
    "against every other is n squared, and asking instead what would "
    "complete this number and whether you have passed it is n. Two Sum is "
    "exactly this.",
    "algo_complement",
)

_add(
    "O(n)",
    "Linear, and the step count printed beside the answer is the proof. The "
    "two pointers only ever move towards each other, so between them they "
    "take at most n steps; checking every pair would be n squared. The list "
    "has to be sorted, and if you had to sort it first that would cost "
    "n log n.",
    "algo_pair_inward",
)

_add(
    "O(n)",
    "Linear in time and constant in extra memory, which is the part worth "
    "having. The fast pointer reads every item once, the slow one advances "
    "only on a keeper, and nothing is visited twice. The obvious version "
    "builds a second list — also linear in time, but it costs n in space.",
    "algo_two_pointer_same",
)

_add(
    "O(n)",
    "Linear, and this is the page that shows why sliding beats recomputing. "
    "Re-adding the whole window at every position costs the width times the "
    "length. Adding the one entering and subtracting the one leaving costs "
    "two operations per step, however wide the window is.",
    "algo_window_fixed",
)

_add(
    "O(n)",
    "Linear, and it surprises people. There is a while loop inside a for "
    "loop, which looks quadratic — but the left edge only ever moves "
    "forward, and across the whole run it can move at most n times. Each "
    "item is added once and removed once. Count the moves, not the nesting.",
    "algo_window_grow",
)

_add(
    "O(n)",
    "Linear, carrying two numbers and keeping nothing else. Any prefix that "
    "has stopped helping is forgotten the moment it does, so there is never "
    "a need to look back — which is what beats checking every start and end "
    "pair, and that is n squared.",
    "algo_running_best",
)

_add(
    "O(n)",
    "Linear to build, then constant for every question afterwards. That is "
    "the trade: one pass up front so any range total becomes a single "
    "subtraction. Answer one range and the effort was wasted; answer "
    "thousands and it is the difference between usable and not.",
    "algo_prefix_sum",
)

_add(
    "O(n)",
    "Linear. Each character is pushed at most once and popped at most once, "
    "so the work is bounded by twice the length however deeply the brackets "
    "nest. The memory is the depth of the nesting rather than the length of "
    "the text.",
    "algo_stack_match",
)

_add(
    "O(log n)",
    "Logarithmic, and the page prints the step count against the length so "
    "you can watch it. Half the remaining range is thrown away every step: "
    "twenty items take about five steps, a thousand about ten, a million "
    "about twenty. Doubling the data adds one step. This is what sorted "
    "data buys you.",
    "algo_binary_search",
    "algo_search_boundary",
)

_add(
    "O(n)",
    "Linear in the number of nodes — each is visited exactly once. The "
    "memory is the depth of the tree, since that is how many calls are on "
    "the stack at the deepest point: a balanced tree costs log n, and a "
    "tree that is really a straight line costs n.",
    "algo_tree_dfs",
)

_add(
    "O(n)",
    "Linear in the number of nodes. The memory differs from depth first, "
    "though: the queue holds a whole level at once, so the widest level is "
    "what it costs — and in a balanced tree the bottom level is about half "
    "of every node in it.",
    "algo_tree_bfs",
)

_add(
    "O(n + e)",
    "Linear in the nodes plus the edges, and both terms matter. Each node "
    "is marked seen once; each edge is looked at once, when its node is "
    "expanded. A graph can have far more edges than nodes, which is why the "
    "edge count is written down rather than folded into n.",
    "algo_graph_reach",
    "algo_graph_hops",
)

_add(
    "O(2ⁿ)",
    "Exponential, because every item is either chosen or not — two to the "
    "power n paths through the decisions. Putting the choice back is what "
    "lets one list serve every branch, so the memory is only the depth. "
    "Twenty items is a million paths, which is why these problems always "
    "come with small inputs.",
    "algo_backtrack",
)

_add(
    "O(n log k)",
    "Linear in the items and logarithmic in the heap — and k is not n. Each "
    "item is pushed and possibly popped, each of those costing log k, "
    "because the heap never grows past k. Sorting everything to take the "
    "top k is n log n, which for a small k is far more work than the "
    "question needs.",
    "algo_top_k",
)

_add(
    "O(rows × cols)",
    "One calculation per square, because the dict makes sure each square is "
    "worked out once and looked up thereafter — the count of stored entries "
    "printed at the end is exactly that number. Without the cache the same "
    "squares are recomputed down every path and the cost is exponential.",
    "algo_memo_grid",
)

_add(
    "O(n)",
    "Linear, one entry per step and constant work at each. These are the "
    "same answers as the memoised recursion on the page before, built "
    "forwards instead of found backwards — no call stack, no dictionary, "
    "and no recursion limit to run into.",
    "algo_dp_table",
)

_add(
    "O(n)",
    "Linear in the number of nodes, because walking is the only way to "
    "reach anything. Note what a linked list does not give you: there is no "
    "index, so reaching the middle costs the same as reaching the end, and "
    "asking for the length means walking all of it.",
    "algo_list_walk",
    "algo_list_reverse",
    "algo_list_middle",
    "algo_list_gap",
)

_add(
    "O(n)",
    "Linear in time and constant in memory, which is the reason to prefer "
    "it. The obvious way to spot a loop is a set of every node seen, and "
    "that costs n in memory. Two pointers cost two references however long "
    "the chain is.",
    "algo_list_cycle",
)

_add(
    "O(n + m)",
    "Linear in the two lengths added together — each node is looked at once "
    "and then linked into place. Nothing is copied and nothing is compared "
    "twice, and it is both inputs already being sorted that makes one pass "
    "enough.",
    "algo_list_merge",
)

_add(
    "O(n + e)",
    "Linear in the jobs plus the rules between them. Each job is queued and "
    "dequeued once, and each rule is looked at once, when the job before it "
    "finishes. Detecting the cycle costs the same, because it is the same "
    "algorithm — it only reads the count at the end.",
    "algo_topo_order",
    "algo_topo_cycle",
)

_add(
    "O(n)",
    "Linear, and this is the one that looks wrong. There is a while loop "
    "inside a for loop, but each position is pushed exactly once and popped "
    "at most once, so across the entire run there are at most n pops. The "
    "nested-loop version of this question is n squared. Count the pushes, "
    "not the nesting.",
    "algo_monotonic",
)

_add(
    "O(n log n)",
    "The sort dominates; the fold after it is a single pass. That is the "
    "shape of most interval problems — sorting is what turns a tangle of "
    "cases into one comparison against the last thing you kept.",
    "algo_merge_spans",
)


# ── The remainder of the Python intermediate pages ───────────
#
# Classified the same way: the emitted program's loop structure was
# measured, counting only loops that walk data rather than a literal tuple
# of demonstration values.

_add(
    "O(1)",
    "Constant. Defining a class, a protocol, a dataclass or a dunder is "
    "machinery rather than calculation — it happens once and does the same "
    "work regardless of any size. What the dunder makes possible may cost "
    "something later; declaring it does not.",
    "hash_dunder",
    "repr_vs_str",
    "call_dunder",
    "getitem_len",
    "property_setter",
    "total_ordering",
    "abstract_base",
    "protocol_shape",
    "frozen_dataclass",
    "dataclass_tools",
    "dataclass_order",
    "enum_auto",
    "typevar_generic",
    "generic_class",
    "typed_dict",
    "cached_property",
    "init_subclass",
    "singledispatch_use",
    "name_main",
    "nonlocal_global",
    "signature_use",
)

_add(
    "O(1)",
    "Constant. Arithmetic on a fixed number of values — rounding, dividing "
    "with a remainder, building a fraction, comparing floats. These pages "
    "are about what the answer *is* rather than how long it takes to get, "
    "and the time is the same whatever the numbers are.",
    "float_trap",
    "decimal_money",
    "math_basics",
    "round_bankers",
    "divmod_base",
    "fraction_use",
    "random_seed",
)

_add(
    "O(1)",
    "Constant. Raising with a cause, suppressing an expected error, or "
    "grouping several — building the exception and unwinding to the handler "
    "is a fixed amount of work.",
    "raise_from",
    "suppress_use",
    "exception_group",
    "test_function",
)

_add(
    "O(1)",
    "Constant. Building an aware datetime, parsing a URL, or configuring a "
    "logger is a fixed piece of setup. Note that logging's real cost is the "
    "writing — a call that is filtered out before it formats anything is "
    "very cheap, which is why the level check comes first.",
    "aware_datetime",
    "urlparse_use",
    "logging_use",
    "argparse_use",
)

_add(
    "O(1)",
    "Constant per operation, and that is exactly why a deque exists. "
    "Appending or popping at either end is a fixed cost, where a list has "
    "to shift every item along to remove from the front — which makes the "
    "obvious queue quadratic and the deque linear.",
    "deque_use",
)

_add(
    "O(log n)",
    "Logarithmic per push and per pop, where n is how many are in the heap. "
    "Only the smallest is cheap to reach — that is the trade. A heap does "
    "not keep everything in order, it keeps just enough order that the "
    "front is always right, and that is why it costs log n rather than n.",
    "heapq_use",
    "heapq_real",
)

_add(
    "O(n)",
    "Linear in the number of items. One pass, comparing each against the "
    "best so far — and handing it a key changes what is compared, not how "
    "many comparisons there are. Sorting to take the largest would be "
    "n log n for an answer one pass already had.",
    "min_max_key",
    "statistics_use",
    "counter_math",
)

_add(
    "O(n)",
    "Linear in the number of items. Walking two sequences at once, taking a "
    "slice of an endless one, or stopping partway all visit each item they "
    "reach exactly once — and the ones that stop early do less, never more.",
    "zip_longest_use",
    "islice_cycle",
    "takewhile_drop",
    "dict_views",
    "dict_merge",
)

_add(
    "O(n)",
    "Linear in the length of the text. Wrapping and formatting into columns "
    "look at every character to decide where the breaks go, and build new "
    "text as they go.",
    "textwrap_use",
    "format_row",
)

_add(
    "O(n)",
    "Linear in the size of the data. Encoding to bytes, pickling and "
    "unpickling all walk every value once on the way out and every byte "
    "once on the way back.",
    "bytes_use",
    "pickle_round",
)

_add(
    "O(n)",
    "Linear in the size of the structure, because a deep copy visits every "
    "value in it — that is what makes it different from the shallow one, "
    "which copies the top level and shares everything underneath.",
    "deepcopy_use",
)

_add(
    "O(n)",
    "Linear in the number of tasks, and the wall clock is a different "
    "question entirely. Gathering ten things that each wait a second takes "
    "about a second, not ten — the work is linear, the waiting overlaps. "
    "That is the whole reason to use it.",
    "async_basic",
    "async_gather",
    "threadpool_map",
)

_add(
    "O(n + e)",
    "Linear in the items plus the dependencies between them. Each is "
    "readied once and each rule is looked at once, when the thing before it "
    "is done — the same cost as doing the topological sort by hand, which "
    "is what this is.",
    "graphlib_use",
)

_add(
    "O(n log n)",
    "Sorting dominates, and on this page it is required rather than "
    "incidental: groupby only groups items that are already next to each "
    "other, so the sort is what makes the grouping correct rather than just "
    "tidy. Forgetting it is the classic bug with this function.",
    "groupby_use",
)

_add(
    "O(n log n)",
    "Sorting. Roughly log n comparisons per item — a thousand items is "
    "around ten thousand comparisons rather than a million. sort in place "
    "and sorted into a new list cost the same time; the difference is the "
    "copy, which is n in memory.",
    "sort_vs_sorted",
    "attrgetter_use",
)

_add(
    "O(n²)",
    "Quadratic. A comprehension inside a comprehension runs the inner one "
    "in full for every item of the outer, so the work is the two lengths "
    "multiplied — 3 by 3 is nine, 100 by 100 is ten thousand. Writing it on "
    "one line makes it shorter, not cheaper.",
    "nested_comp",
)

_add(
    "O(n log n)",
    "The database does the work, and what it costs depends on the query. A "
    "lookup on an indexed column is logarithmic, a scan of the table is "
    "linear, and a sort or a join is usually n log n. The point of the page "
    "is that this is not your loop any more — it is the query planner's.",
    "sqlite_memory",
)

_add(
    "O(1)",
    "Constant. Matching a value against a set of patterns tests them in "
    "order until one fits, which is a fixed number of comparisons for a "
    "fixed number of cases — it does not grow with any data.",
    "match_structure",
)
