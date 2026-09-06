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


# ── The harder variants ──────────────────────────────────────

_add(
    "O(rows × cols)",
    "Every cell is visited once — once by the outer sweep looking for a "
    "start, and once by the spread that claims it. The seen set is what "
    "guarantees the second of those happens only once, and without it the "
    "walk would go round in circles forever rather than merely slowly.",
    "algo_grid_flood",
)

_add(
    "O(n)",
    "Linear, and this is the page where that is hardest to believe. There "
    "is a while loop inside a for loop, and the deque can hold most of the "
    "list — but each position is pushed exactly once and popped at most "
    "once, so across the whole run there are at most n of each. Taking max "
    "of every window instead is the width times the length.",
    "algo_window_max",
)

_add(
    "O(n log n)",
    "The sort dominates; the greedy pass afterwards is linear. That is the "
    "usual shape of a greedy algorithm — almost all the cost is putting "
    "things in the order that makes the choice obvious.",
    "algo_intervals_pick",
)

_add(
    "O(n × m)",
    "One cell per pair of positions, so the two lengths multiplied — and "
    "the page prints that number beside the answer. Memory is the same "
    "unless you keep only the row before, which is the standard trick once "
    "the strings get long. This is the cost of every two-sequence problem "
    "of this shape.",
    "algo_lcs",
)

_add(
    "O(n log s)",
    "Logarithmic in the range of possible answers, times a linear check "
    "each time — where s is the span between the largest single item and "
    "the total. What is being halved is not the data but the answers, and "
    "the feasibility check is the linear part. Trying every capacity in "
    "turn would be s passes rather than log s.",
    "algo_search_answer",
)

_add(
    "O(log n)",
    "Logarithmic per value that arrives, so n log n over the whole stream "
    "— each push and rebalance is a handful of heap operations. Reading "
    "the middle itself is constant, because it is sitting at the front of "
    "one or both heaps. Sorting after every arrival would be n log n each "
    "time rather than once.",
    "algo_two_heaps",
)

_add(
    "O(α(n))",
    "Very nearly constant per operation. With the flattening on the way up, "
    "the cost is the inverse Ackermann function of n, which is under five "
    "for any number of items that will ever exist — so treat it as "
    "constant and know that the name is doing something. Without the "
    "flattening the chains grow and it degrades to linear.",
    "algo_union_find",
)

_add(
    "O(len(prefix))",
    "The length of the prefix, not the number of words — that is the whole "
    "reason to build one. Counting what is underneath then costs the size "
    "of that subtree. Building the trie is the total length of every word, "
    "paid once, and afterwards no query ever looks at a word that does not "
    "match.",
    "algo_trie",
)

_add(
    "O(rows × cols)",
    "One pass to build, then four lookups for any rectangle however large — "
    "the same trade as the one-dimensional running total, one dimension up. "
    "Ask about one rectangle and building the table was wasted; ask about "
    "thousands and it is the only way.",
    "algo_prefix_matrix",
)

_add(
    "O((n + e) log n)",
    "Each edge can push a place onto the heap, and each heap operation is "
    "logarithmic — so the edges dominate on a well-connected graph. The "
    "difference from a plain breadth-first walk is exactly that log: a "
    "queue hands back whatever arrived first, and a heap has to work out "
    "what is cheapest.",
    "algo_dijkstra",
)


# ── SQL ──────────────────────────────────────────────────────
#
# The letters mean something different here, and saying so is the useful
# part: you are not writing the loop, you are describing the answer and
# letting the planner choose. What follows is what it will choose.

_add(
    "O(n)",
    "A full scan — every row read, where n is the rows in the table. "
    "Naming fewer columns does not change how many rows are read, though it "
    "does change how much is carried back. There is no index that helps "
    "here, because nothing is being looked up.",
    "sql_select",
)

_add(
    "O(n)",
    "A scan, unless the column has an index. That is the whole art of it: "
    "on an indexed column this becomes a lookup rather than a walk, and on "
    "an unindexed one the database has no choice but to read every row and "
    "test it. The query text is identical either way, which is why slow "
    "queries so often look fine.",
    "sql_where",
)

_add(
    "O(n log n)",
    "A sort, which is usually the most expensive thing in a simple query. "
    "If an index already holds the column in order the planner can read it "
    "in order instead and pay nothing — that is what people mean when they "
    "say an index can satisfy an ORDER BY.",
    "sql_order",
    "sql_distinct_in",
)

_add(
    "O(n log n)",
    "The limit does not save you the sort. The database still has to work "
    "out which rows are first, and that means ordering all of them — a "
    "top-ten of a million rows is a million-row sort unless an index "
    "provides the order. What LIMIT saves is what is sent back.",
    "sql_limit",
)

_add(
    "O(n)",
    "One pass, carrying a single running answer — the same shape as the "
    "totals you wrote by hand on page 297, done by the engine. COUNT(*) on "
    "a large table can still be slow for exactly that reason: it really "
    "does look at every row.",
    "sql_aggregate",
)

_add(
    "O(n log n)",
    "Grouping means gathering equal values together, and the two ways to "
    "do that are sorting or hashing — so it costs about what a sort costs, "
    "or about what building a dict costs. HAVING is free by comparison: it "
    "filters groups, and there are far fewer of those than rows.",
    "sql_group",
    "sql_having",
)

_add(
    "O(n × m)",
    "In the worst case, every row against every row — which is what "
    "happens if the join column has no index and the planner falls back to "
    "comparing everything. With an index it is n lookups instead, which is "
    "the difference between a query that returns and one that does not. "
    "Forgetting the ON clause entirely gives you the full product, on "
    "purpose and by definition.",
    "sql_join",
    "sql_left_join",
)


# ── Node objects ─────────────────────────────────────────────
#
# Almost everything here is linear, and saying so is not the useful part.
# The useful part is what linear costs on a chain that it does not cost on
# a list: there is no index, so reaching the middle means walking to it,
# and that is why so many of these answers send two pointers instead of
# doing arithmetic.

_add(
    "O(n)",
    "One node made per value, each linked to the one before. Building is "
    "linear and so is every walk afterwards, but a chain gives up the one "
    "thing a list has: there is no way to jump to position five without "
    "passing one through four. Every cost on these pages follows from "
    "that.",
    "node_build",
    "node_walk",
)

_add(
    "O(n)",
    "One pass, three pointers, and no new nodes — the memory is constant, "
    "which is the reason to do it this way rather than reading the values "
    "into a list and building a new chain. That would also be linear time "
    "and would cost linear space to match.",
    "node_reverse",
)

_add(
    "O(n + m)",
    "Both chains, each node looked at once. Nothing here is re-read, "
    "because every comparison advances one side or the other and neither "
    "side ever goes backwards. The dummy head costs one node and saves the "
    "empty-list check on every append.",
    "node_dummy",
)

_add(
    "O(n)",
    "Still one pass, even though two pointers are moving: the fast one "
    "covers the chain once at double speed while the slow one covers half. "
    "Linear either way, and constant memory. The alternative is to walk "
    "the chain to measure it and walk again to the position you worked "
    "out, which is two passes for the same answer.",
    "node_two_pointers",
)

_add(
    "O(n)",
    "One pass. Removing a node is constant work once you are standing on "
    "the one before it, which is the whole reason the loop looks at "
    "node.next rather than node — you cannot unlink a node you are already "
    "standing on.",
    "node_remove",
)

_add(
    "O(n)",
    "Every value becomes a node once. Depth then costs another full visit, "
    "because a tree will not tell you how deep it is without looking at "
    "all of it. Depth is not the same as the number of nodes: a balanced "
    "tree of n nodes is log n deep, and a tree that has degenerated into a "
    "chain is n deep, which is what turns a fast structure into a slow one.",
    "tree_build",
)

_add(
    "O(n)",
    "Every node visited exactly once, whichever of the three orders you "
    "pick — the order changes what comes out, never how much work it is. "
    "Memory is the depth rather than the node count, because that is how "
    "many calls are stacked up at the deepest point.",
    "tree_walk",
)

_add(
    "O(n)",
    "Linear despite the nesting, and the nesting is what makes it look "
    "otherwise: there is a for loop inside a while loop. It is not "
    "quadratic because the inner loop does not run n times per row — it "
    "runs once per node in that row, and every node is in exactly one "
    "row. Each node enters the queue once and leaves once, so the inner "
    "loop bodies add up to n across the whole walk. Memory is the widest "
    "row rather than the whole tree, which for a balanced tree is about "
    "half the nodes — level order costs the most memory of the "
    "traversals, not the least. Reversing a row is linear in that row, "
    "so the zigzag adds nothing to the total.",
    "tree_levels",
)

_add(
    "O(n)",
    "heapify is the surprise: turning a list into a heap is linear, not n "
    "log n, even though pushing the items one at a time would be n log n. "
    "The popping afterwards costs log n each. isdigit and isalnum are "
    "constant per character, so the scans around them are linear in the "
    "text.",
    "node_toolkit",
)


# ── The last four constructs ─────────────────────────────────

_add(
    "O(n + e)",
    "Nodes plus edges, because a walk looks at every node once and every "
    "edge twice, once from each end. That is the honest way to write it: "
    "quoting only n hides the fact that a graph with the same number of "
    "nodes can have almost none or almost all of the possible edges, and "
    "the walk costs accordingly. Cloning costs the same again, and the map "
    "from old node to new is what keeps a cycle from turning it into an "
    "infinite descent.",
    "graph_nodes",
)

_add(
    "O(n)",
    "Linear, and that is the surprise. remove takes a value rather than a "
    "position, so it has to scan until it finds one — removing in a loop "
    "is quadratic without looking it, which is why peeling leaves is "
    "written to touch only the neighbours of the node going away. The set "
    "versions are the opposite: remove and discard on a set are constant, "
    "because a hash knows where to look.",
    "value_remove",
)

_add(
    "O(log n)",
    "Logarithmic in the size of the range, and nothing to do with how much "
    "data there is, because there is no data. The range of possible "
    "answers halves on every question, so a thousand versions cost ten "
    "questions and a million cost twenty. What binary search needs is not "
    "a sorted list but a question whose answer is False up to a point and "
    "True after it, which is a much weaker thing to require and is why "
    "this trick turns up so far from anything that looks like searching.",
    "predicate_search",
)


# ── C ────────────────────────────────────────────────────────
#
# The letters mean the same thing here, but the constant hidden behind
# them is not the same constant. C does the work you wrote and nothing
# else, which is why a linear pass in C and a linear pass elsewhere can
# differ by a factor nobody writes down.

_add(
    "O(n)",
    "One pass to fill and one to add up. The allocation itself is not the "
    "cost people expect: malloc is roughly constant, and asking for one "
    "block of n ints is very much cheaper than asking n times for one, "
    "because each call has to find space and record that it did.",
    "c_malloc",
)

_add(
    "O(1)",
    "sizeof is answered by the compiler, not at run time. There is no loop "
    "in it and no cost to it, which is exactly why it cannot help once the "
    "array has decayed to a pointer: nothing at compile time knows how many "
    "elements the pointer is pointing at. The total afterwards is the only "
    "linear part.",
    "c_sizeof",
)

_add(
    "O(n)",
    "calloc has to zero what it hands back, so unlike malloc it does work "
    "proportional to the size, though the operating system often has zeroed "
    "pages ready and it comes out faster than a loop would. memcpy is "
    "linear in bytes and about as fast as bytes can be moved.",
    "c_calloc",
)

_add(
    "O(n)",
    "One pass to decide what to keep. The allocation is sized for the worst "
    "case rather than the answer, which costs memory and saves counting the "
    "matches first: the alternative is two passes, one to count and one to "
    "fill. Both are linear, and which is better depends on whether memory "
    "or time is the thing you are short of.",
    "c_out_param",
)

_add(
    "O(n)",
    "One pass to build, one to walk, one to free, all linear. The free is "
    "the part that does not exist in other languages and it is not optional: "
    "every node came from its own malloc and has to be handed back "
    "individually, which is why freeing a chain is a loop rather than a "
    "single call.",
    "c_list_node",
    "c_list_ops",
)

_add(
    "O(n)",
    "Every node visited once to build, once to measure, once to add up, "
    "once to free. Depth is not the same as node count: a balanced tree of "
    "n nodes is log n deep, and one that has degenerated into a chain is n "
    "deep, which is where the recursion here would run out of stack first.",
    "c_tree_node",
)

_add(
    "O(n log n)",
    "The sort itself, plus one comparator call per comparison, and that "
    "call is not free: it goes through a function pointer, so the compiler "
    "cannot inline it the way a template or a closure would be inlined. "
    "That is most of why the same sort in C++ is usually faster than qsort "
    "despite doing the same number of comparisons.",
    "c_qsort",
)


# ── Rust ─────────────────────────────────────────────────────
#
# Most of what is interesting in Rust is not the time, it is what the
# time buys you. These notes say when a thing is free and when it only
# looks free.

_add(
    "O(n)",
    "find and position both stop at the first match, so the worst case is "
    "the whole sequence and the usual case is less. Option itself costs "
    "nothing at run time: it is a compile-time shape, and for a reference "
    "it does not even cost the extra byte, because there is no such thing "
    "as a null reference to confuse None with.",
    "rust_option",
)

_add(
    "O(n)",
    "One pass, however many steps are chained onto it. map and filter build "
    "no intermediate collection, so a chain of five of them is still a "
    "single walk, and the compiler routinely turns it into the same loop "
    "you would have written. collect is where memory is finally allocated, "
    "which is why it is the step to be careful with.",
    "rust_iter",
)

_add(
    "O(1)",
    "Constant per character, so linear over the text. The point of entry is "
    "that it is one lookup rather than three: contains_key, then get, then "
    "insert, is the same answer for three times the hashing. or_insert "
    "returns a reference into the map, which is why the star is there.",
    "rust_entry",
)

_add(
    "O(1)",
    "push and pop are constant, amortised for push because the Vec doubles "
    "when it fills rather than growing by one. Doubling is what makes n "
    "pushes cost n rather than n squared. clear is constant for numbers and "
    "linear for anything with a destructor to run.",
    "rust_vec_ops",
)

_add(
    "O(1)",
    "Both ends constant, which is the whole reason to reach for this rather "
    "than a Vec. Taking from the front of a Vec is linear because everything "
    "behind it shifts down, so a breadth-first walk written on a Vec is "
    "quadratic and looks perfectly reasonable.",
    "rust_deque",
)

_add(
    "O(n)",
    "clone copies every element, so it is linear and it is the one call on "
    "these pages that is worth avoiding. A borrow is constant and copies "
    "nothing, which is why the function takes a reference. Rust makes the "
    "expensive one loud on purpose: you have to write clone, it never "
    "happens quietly.",
    "rust_clone",
)

_add(
    "O(1)",
    "Rc::clone copies a pointer and adds one to a counter, so it is "
    "constant no matter how large the value is, and it is not the same "
    "operation as clone above despite the name. borrow and borrow_mut are "
    "constant too, but they are checked at run time rather than compile "
    "time, and borrowing mutably twice at once panics instead of failing "
    "to build.",
    "rust_rc_refcell",
)

_add(
    "O(n)",
    "Every node once for the depth and once for the total. The wrapper adds "
    "no walking: Option is free, Rc is a pointer, and borrow is a counter "
    "check. What it adds is noise at the point of use, which is why the "
    "same tree in Python is four lines shorter and why Rust knows it can "
    "never be freed while something is still looking at it.",
    "rust_tree",
)

_add(
    "O(n log n)",
    "The sort dominates and dedup is a single linear pass afterwards, which "
    "is why dedup only removes every repeat if the sort came first. sort is "
    "stable and sort_unstable is faster when you do not need that. The "
    "comparator is a closure, so it inlines, unlike the function pointer C "
    "has to pass.",
    "rust_sort",
)

_add(
    "O(n)",
    "Linear in bytes for building, linear in characters for walking. Those "
    "are two different numbers: chars decodes UTF-8 as it goes, so it costs "
    "more than indexing would, and indexing by byte is not offered because "
    "it could land in the middle of a character. push_str is amortised "
    "constant, the same doubling as a Vec.",
    "rust_string",
)


# ── Dart ─────────────────────────────────────────────────────

_add(
    "O(n)",
    "The search is linear and the null handling costs nothing at all. int? "
    "is not a box around an int: nullability is a compile-time fact, "
    "checked and then erased, so ?? and ??= are a branch and nothing more. "
    "What they buy is that the branch cannot be forgotten.",
    "dart_null",
)

_add(
    "O(1)",
    "Constant to read and write, because a Dart Map hashes the key. keys "
    "is a lazy view rather than a copy, so asking for it costs nothing and "
    "walking it costs the length — but toList does copy, and the sort "
    "afterwards is the n log n on this page.",
    "dart_map",
)

_add(
    "O(1)",
    "contains on a Set is constant where the same question of a List is a "
    "scan. Building the Set from a List is linear and pays for itself the "
    "moment you ask more than a couple of questions. Sorting what comes "
    "out is n log n and is there because a Set has no order to rely on.",
    "dart_set",
    "cpp_set",
)

_add(
    "O(n)",
    "Linear either way, one element produced per position. filled makes n "
    "copies of one value; generate calls the function once per index. "
    "Neither grows afterwards unless asked, which is why a literal list "
    "here has to go through toList before anything is added to it.",
    "dart_list_make",
)

_add(
    "O(n)",
    "add and removeLast are constant, amortised for add because the list "
    "grows in jumps. removeAt and insert are linear: everything after the "
    "position moves along by one. Inserting at the front of a long list in "
    "a loop is the quadratic mistake this page exists to make visible.",
    "dart_list_ops",
)

_add(
    "O(n)",
    "One pass, and the interesting part is when. map and where are lazy: "
    "they return an Iterable that has done nothing yet, and the work "
    "happens at toList or at the loop that consumes it. reduce is not "
    "lazy, and on an empty list it throws rather than returning a zero, "
    "which is why fold exists.",
    "dart_iter",
)

_add(
    "O(n log n)",
    "The sort, with the comparison called once per comparison. sort "
    "returns void and reorders in place, so the cost is in the list you "
    "already had rather than a new one — and that is also why the cascade "
    "is needed to get the list back as an expression.",
    "dart_sort",
    "cpp_sort",
)

_add(
    "O(n)",
    "Linear in what comes out. The multiply operator builds the whole "
    "result, so a short unit times a large number is expensive in exactly "
    "the way it looks cheap. split allocates the parts, join walks them "
    "again, and substring copies because strings do not change.",
    "dart_string",
)

_add(
    "O(n)",
    "One node made per value and one pass to walk it. The nullable link is "
    "free at run time: ListNode? and ListNode are the same pointer, and "
    "the difference is entirely in what the compiler will let you write "
    "without a check. Building backwards through the list is what lets "
    "each node be made already pointing at the rest.",
    "dart_node",
)

_add(
    "O(n)",
    "Every node once for depth and once for the total. Depth is not the "
    "node count: balanced it is log n, and a tree that has degenerated "
    "into a chain is n, which is the case that overflows the stack. "
    "Accepting TreeNode? rather than TreeNode is what removes the null "
    "check from every call site and puts it in one place.",
    "dart_tree",
)


# ── C++ ──────────────────────────────────────────────────────

_add(
    "O(1)",
    "push_back and pop_back are constant, amortised for push_back because "
    "capacity doubles rather than growing by one. empty, size, front and "
    "back are all constant. None of the four checks anything: front on an "
    "empty vector is undefined behaviour, which is worse than a crash "
    "because it may not be one.",
    "cpp_vector",
)

_add(
    "O(1)",
    "Constant on average, linear in the worst case when hashes collide. "
    "count is the safe question; operator[] on a missing key inserts a "
    "default and returns it, so a read written with brackets is a write, "
    "and a map that mysteriously grows while being searched is this bug.",
    "cpp_map",
)

_add(
    "O(n)",
    "Walking with an explicit iterator is the same linear pass a range-for "
    "compiles into. find is linear and returns end on a miss, which costs "
    "nothing to compare. Subtracting two iterators is constant here because "
    "a vector has random access; on a list it would not compile.",
    "cpp_iterators",
)

_add(
    "O(1)",
    "Every operation on both adapters is constant. Neither is a container "
    "in its own right: each wraps one and hides everything except the "
    "operations that make sense, which is why there is no way to walk "
    "either. pop returns void so that removing an element cannot throw "
    "part way through handing it back.",
    "cpp_adapters",
)

_add(
    "O(n)",
    "One pass each. max_element and min_element hand back iterators rather "
    "than values, and return end on an empty range, so the star is not "
    "optional and neither is checking. accumulate takes its starting value "
    "and that value fixes the arithmetic type: pass 0 over doubles and the "
    "sum is done in integers.",
    "cpp_algorithms",
)

_add(
    "O(n)",
    "substr copies, so it is linear in the piece taken and allocates. find "
    "is linear and returns npos, which is the largest size_t rather than "
    "-1 — comparing it against a signed number does the wrong thing "
    "silently. Building with += is amortised constant per character.",
    "cpp_string",
)

_add(
    "O(n)",
    "One new per node, one pass to walk, one to delete. new and delete are "
    "the same duty malloc and free were, with a constructor attached. The "
    "delete loop still has to save the next pointer first: after delete "
    "the node is gone and so is the way onward.",
    "cpp_node",
)

_add(
    "O(n)",
    "Every node once. The free has to run bottom up, and that is the whole "
    "content of freeTree: delete the node before recursing and the "
    "pointers to its children have gone with it, so the children leak and "
    "nothing reports it.",
    "cpp_tree",
)


# ── SQL, past the fundamentals ───────────────────────────────
#
# The same warning as the first ten SQL pages applies harder here. You are
# describing an answer, not writing a loop, and the planner decides what it
# costs. What follows is what it will usually decide.

_add(
    "O(n)",
    "A scan, and LIKE is the reason to say so. A pattern anchored at the "
    "start can use an index, because the rows it wants sit together in "
    "order; a pattern beginning with a wildcard cannot, and no index will "
    "ever help it. The two look almost identical and differ by everything.",
    "sql_like",
)

_add(
    "O(n)",
    "One pass, constant per row. CASE is evaluated per row and cannot use "
    "an index, so filtering on a CASE result rather than on the underlying "
    "column turns a lookup into a scan. Computing it in the select list, "
    "as here, costs nothing worth counting.",
    "sql_case",
)

_add(
    "O(n)",
    "A scan. NULL is the part that costs correctness rather than time: "
    "equality against NULL is never true, so a filter written that way "
    "silently returns nothing, and NOT IN against a set containing one "
    "returns nothing either, which is the same bug wearing a hat.",
    "sql_null",
)

_add(
    "O(n)",
    "Two passes, not n passes. Nothing inside this subquery mentions the "
    "outer row, so it is uncorrelated: the planner runs it once, keeps the "
    "number, and scans with it. Written so that it does refer to the outer "
    "row it becomes correlated and runs per row, and the same query is "
    "suddenly quadratic.",
    "sql_subquery",
)

_add(
    "O(n × m)",
    "Correlated, so the inner query runs once per outer row — that is what "
    "referring to u.id costs. EXISTS stops at the first match rather than "
    "counting them, which is why it beats COUNT(*) > 0 on a table where "
    "the answer is usually yes. With an index on the joined column each "
    "inner run is a lookup and the whole thing is n log m.",
    "sql_exists",
)

_add(
    "O(n²)",
    "Every row against every row in the worst case, because both sides of "
    "the join are the same table. The a.id < b.id is not only about "
    "removing duplicates: it halves the work. An index on the joined "
    "column turns each side into a lookup, and without one a self join on "
    "a large table is the query that never comes back.",
    "sql_self_join",
)

_add(
    "O(n log n)",
    "UNION has to remove duplicates, and removing duplicates means sorting "
    "or hashing everything both halves produced. UNION ALL does not, and "
    "is linear. That is the entire difference between them and the reason "
    "to reach for ALL whenever you know the halves cannot overlap.",
    "sql_union",
)

_add(
    "O(n)",
    "A CTE costs what the query inside it costs and nothing extra, at "
    "least here: SQLite may materialise it once or may fold it into the "
    "outer query, and either way this one is a grouped scan. The value is "
    "readability, not speed, and a CTE referred to twice is the case where "
    "materialising actually saves work.",
    "sql_cte",
)

_add(
    "O(n log n)",
    "A sort per partition, which together is a sort of the table. That is "
    "the cost of every window function with an ORDER BY inside the OVER, "
    "and it is the price of the thing GROUP BY cannot do: keeping every "
    "row while still answering a question about the group it belongs to. "
    "An index matching the partition and order can remove the sort.",
    "sql_window",
    "sql_running",
)


# ── Node objects on the web, and the last few calls ──────────

_add(
    "O(n)",
    "One node made per value and one walk to read them back. Building "
    "backwards through the array is what lets each node be created already "
    "pointing at the rest, so it is one pass rather than two. The types "
    "cost nothing at run time: TypeScript erases them, and the JavaScript "
    "on the facing page is the same program with the proofs deleted.",
    "web_list_node",
)

_add(
    "O(n + m)",
    "Reversing is one pass and no allocation, which is the reason to do it "
    "in place rather than read the values into an array. Merging looks at "
    "each node of both chains once, because every comparison advances one "
    "side and neither ever goes back. The dummy costs one node and removes "
    "the empty-list check from every append.",
    "web_list_ops",
)

_add(
    "O(n)",
    "realloc is linear when it has to move and constant when it can extend "
    "in place, and you do not get to know which — so growing one element at "
    "a time is quadratic in the worst case and fine in the best, which is "
    "why the usual answer is to double. memcmp and atoi are both linear in "
    "what they read.",
    "c_more",
)

_add(
    "O(n)",
    "insert in the middle is linear, because everything after it shifts "
    "along, and that is the cost push_back does not have. clear is linear "
    "for anything with a destructor and constant for plain numbers, but it "
    "keeps the capacity either way, so the memory is still held after the "
    "size reads zero. append and compare are linear in the string.",
    "cpp_more",
)

_add(
    "O(n)",
    "The walk is linear and take makes it shorter, because the chain is "
    "lazy and stops when asked. get is constant and hands back an Option "
    "rather than panicking, which is the whole difference from indexing. "
    "The clone is the expensive line on the page and it is there only "
    "because into_iter consumes what it walks.",
    "rust_more",
)

_add(
    "O(1)",
    "The lookup is constant and ! costs nothing at all — it is a claim "
    "rather than a check, compiled to the same code as no claim, and the "
    "run-time cost only arrives when it turns out to be wrong. take is "
    "lazy, so it costs what it yields rather than what it walked, and "
    "List.from copies and is linear.",
    "dart_more",
)
