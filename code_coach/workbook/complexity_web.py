"""Complexity notes for the JavaScript and TypeScript pages.

Same three rules as the Python files: say what grows rather than only the
letter, say what n is, and never claim a cost the exercise does not have.

TypeScript needs one thing said before anything else, and most of its notes
say it: types are erased. Nothing in an annotation, an interface, a generic
or a conditional type exists when the program runs — `tsc` deletes all of
it and hands node plain JavaScript. So the run-time cost of a page about
types is the cost of the handful of statements underneath them, which is
usually constant. Where a page's compile-time work is the interesting part,
the note says so instead of pretending there is a run-time cost.
"""

from __future__ import annotations

from code_coach.workbook.complexity import Cost

NOTES: dict[str, Cost] = {}


def _add(label: str, note: str, *shapes: str) -> None:
    for shape in shapes:
        NOTES[shape] = Cost(label, note)


def for_shape(shape: str) -> Cost | None:
    return NOTES.get(shape)


# ── JavaScript: constant ─────────────────────────────────────

_add(
    "O(1)",
    "Constant. This is language machinery rather than a calculation — "
    "naming things, building an object, defining a class or a function. It "
    "does the same work whatever values you give it, and there is nothing "
    "here whose size the running time could follow.",
    "js_template",
    "js_destructure",
    "js_arrow",
    "js_default_params",
    "js_object_method",
    "js_class",
    "js_getter_setter",
    "js_static",
    "js_extends",
    "js_closure",
    "js_curry",
    "js_hoisting",
    "js_error_class",
    "js_finally",
    "js_define_property",
    "js_prototype",
    "js_private_field",
    "js_symbol",
    "js_to_primitive",
    "js_tagged_template",
    "js_logical_assign",
    "js_destructure_rest",
    "js_arguments",
)

_add(
    "O(1)",
    "Constant. Optional chaining short-circuits — the moment something is "
    "null or undefined the rest of the chain is abandoned — so the cost is "
    "the length of the chain you wrote, which is fixed, not the size of any "
    "data.",
    "js_optional_chain",
    "js_null_undefined",
    "js_truthy",
    "js_coercion",
    "js_type_checks",
    "js_epsilon",
    "js_number_checks",
)

_add(
    "O(1)",
    "Constant, on average, and that is the whole reason these exist. A Map "
    "or a Set answers get, set and has by working out where the key "
    "belongs rather than looking through what it holds — so a collection of "
    "ten and one of ten million cost the same per operation. A plain object "
    "does the same, which is why objects have always been used as lookup "
    "tables.",
    "js_map_set",
    "js_weakmap",
    "js_memo_map",
)

_add(
    "O(1)",
    "Constant. Reading or writing one entry by position is direct — the "
    "engine works out where it is rather than counting along — so at(-1) "
    "costs the same as at(0). Note that a hole in an array does not save "
    "anything: the index arithmetic is the same either way.",
    "js_at",
    "js_sparse",
)

_add(
    "O(1)",
    "Constant per step, and note where the time actually goes. Awaiting "
    "something is not work — the function suspends and the engine gets on "
    "with other things. The wall-clock wait is whatever you are waiting "
    "for; the code around it is a fixed handful of operations.",
    "js_async",
    "js_promise_then",
    "js_microtask",
    "js_for_await",
)

_add(
    "O(1)",
    "Constant. Throwing and catching costs a fixed amount — building the "
    "error and unwinding to the handler. It is only expensive if you use "
    "exceptions for ordinary control flow and throw thousands of them.",
    "js_throw_catch",
)

_add(
    "O(1)",
    "Constant. Building a date, or reading a field out of one, is "
    "arithmetic on a single number of milliseconds. Dates far apart do not "
    "cost more than dates close together.",
    "js_date",
)

_add(
    "O(1)",
    "Constant. bind, and the rules about what `this` refers to, are decided "
    "when the call is made — a fixed amount of bookkeeping per call and "
    "nothing that grows with data.",
    "js_bind",
)

_add(
    "O(1)",
    "Constant per property. Freezing and sealing are one level deep, which "
    "is the page's point: the object's own keys are marked and nothing "
    "nested is touched. So the cost follows the number of keys on that one "
    "object, not the size of the tree beneath it.",
    "js_freeze",
    "js_seal",
)

_add(
    "O(1)",
    "Constant, and the page is about what the answer is rather than how "
    "long it takes. A proxy adds one indirection to each access — a fixed "
    "cost per operation, paid every time, which is why a proxy in a hot "
    "loop is worth thinking about.",
    "js_proxy",
)

_add(
    "O(1)",
    "Constant per value handed back. A generator suspends at each yield and "
    "resumes when you ask for the next one, doing a fixed amount of work "
    "each time — so the total follows how many values you take, not the "
    "size of anything it could produce. That is the point of a generator "
    "that never ends.",
    "js_generator",
    "js_yield_star",
    "js_iterator",
)

# ── JavaScript: linear ───────────────────────────────────────

_add(
    "O(n)",
    "Linear in the length of the array. map, filter and forEach visit every "
    "item exactly once and do the same work per item — they are loops with "
    "better names, not faster ones. Chaining three of them is three passes: "
    "still linear, but three times the work of doing it in one.",
    "js_map",
    "js_filter",
    "js_flat",
    "js_array_from",
    "js_fill",
    "js_immutable_array",
)

_add(
    "O(n)",
    "Linear. reduce folds the array down to one value with a single pass, "
    "and it stops being obvious what it costs only when the thing you build "
    "up is itself a collection — building an object with reduce is still "
    "one pass, because each insertion is constant.",
    "js_reduce",
    "js_reduce_group",
    "js_reduce_right",
)

_add(
    "O(n)",
    "Linear, and it stops early. find, some and every all give up as soon "
    "as the answer is settled, so the best case is the first item — but the "
    "worst case is the whole array, and the worst case is what the letter "
    "describes.",
    "js_find_some_every",
)

_add(
    "O(n)",
    "Linear in the number of items. Walking with for...of, or over an "
    "object's own keys, visits each once. Object.keys and Object.entries "
    "build a new array first, so they cost a pass and an allocation before "
    "your loop has started.",
    "js_for_of",
    "js_from_entries",
)

_add(
    "O(n)",
    "Linear in the total number of items. Spreading copies everything it "
    "touches — the three dots are cheap to type and not cheap to run — so "
    "spreading inside a loop is the quiet way to turn a linear job into a "
    "quadratic one.",
    "js_spread",
    "js_object_spread",
)

_add(
    "O(n)",
    "Linear in the size of the slice. slice copies the part you asked for, "
    "and splice has to shift everything after the cut along, so removing "
    "from the front of a long array costs its whole length.",
    "js_slice_splice",
)

_add(
    "O(n)",
    "Linear in the length of the text. Padding, trimming and replacing all "
    "have to look at each character, and each hands back new text — strings "
    "cannot be changed in place, so every one of these allocates a copy.",
    "js_string_pad",
    "js_string_raw",
)

_add(
    "O(n)",
    "Linear in the length of the subject. A regular expression scans left "
    "to right, and for the patterns here that is one pass. Worth knowing "
    "that this is the good case: some patterns with nested repetition can "
    "take exponential time on the wrong input.",
    "js_regex",
    "js_matchall",
)

_add(
    "O(n)",
    "Linear in the size of the data. Turning an object into text and back "
    "walks every value once on the way out and every character once on the "
    "way in. It is also a deep copy if you use it as one, with the same "
    "cost.",
    "js_json",
    "js_structured_clone",
    "js_deep_equal",
)

_add(
    "O(n)",
    "Linear in the length of the number, where n is its digits rather than "
    "its value. That is the trade a BigInt makes: a double does its "
    "arithmetic in one machine instruction and silently loses precision, "
    "and a BigInt keeps every digit and pays for the ones it keeps.",
    "js_bigint",
)

_add(
    "O(n)",
    "Linear in the length of the string, since every character has to be "
    "read to work out what number it describes. The base does not change "
    "that — parsing in base 16 costs the same as base 10.",
    "js_number_parse",
    "js_radix",
    "js_url",
)

_add(
    "O(n)",
    "Linear in the number of turns of the loop, and this page is about "
    "correctness rather than cost. `var` makes one binding for the whole "
    "loop and `let` makes a fresh one each time round — the second is not "
    "meaningfully slower, and it is the one that does what you meant.",
    "js_var_let",
)

_add(
    "O(n)",
    "Linear. Labelled break leaves both loops the moment the answer is "
    "found — the nesting is still there, so the worst case is the product "
    "of the two lengths, but breaking out is what stops the average case "
    "being that.",
    "js_labelled_break",
)

_add(
    "O(n + m)",
    "Linear in the two sets added together. Union and intersection by hand "
    "walk one set and ask the other whether it has each item — and because "
    "that question is constant for a Set, the whole thing is one pass. Do "
    "the same with arrays and includes and it is quadratic.",
    "js_set_ops",
)

_add(
    "O(n)",
    "Linear per call, with the results kept so the second call is free. "
    "That is the trade a memo makes: memory for time, and it only pays when "
    "the same arguments come round again.",
    "js_chaining",
)

# ── JavaScript: sorting ──────────────────────────────────────

_add(
    "O(n log n)",
    "Sorting. Roughly, each item is compared against about log n others — a "
    "thousand items is around ten thousand comparisons rather than a "
    "million. The comparator changes what is compared, never how many "
    "comparisons there are, so sorting numbers properly costs no more than "
    "sorting them wrongly did.",
    "js_sort_numbers",
    "js_sort_objects",
)

# ── TypeScript: the types cost nothing at run time ───────────

_add(
    "O(1)",
    "Constant, and the types cost nothing at all. Every annotation, "
    "interface and generic on this page is deleted by the compiler — node "
    "never sees them. What runs is the handful of statements underneath, "
    "which is a fixed amount of work. The checking happened once, before "
    "the program started.",
    "ts_annotate",
    "ts_interface",
    "ts_optional",
    "ts_tuple",
    "ts_generic_fn",
    "ts_generic_class",
    "ts_literal",
    "ts_utility",
    "ts_readonly",
    "ts_strict_null",
    "ts_implements",
    "ts_keyof_generic",
    "ts_branded",
    "ts_key_remap",
    "ts_as_const",
    "ts_template_type",
    "ts_indexed_access",
    "ts_record_type",
    "ts_function_type",
    "ts_abstract_class",
    "ts_generic_default",
    "ts_awaited",
    "ts_variadic_tuple",
    "ts_this_return",
    "ts_accessor",
    "ts_rest_params",
    "ts_two_generics",
    "ts_extract_exclude",
    "ts_non_nullable",
    "ts_private_field",
    "ts_declaration_merge",
    "ts_parameters",
    "ts_omit_override",
    "ts_template_keys",
    "ts_generic_impl",
    "ts_class_typeof",
    "ts_keyof",
    "ts_constraint",
    "ts_mapped",
    "ts_conditional",
    "ts_enum",
    "ts_overload",
    "ts_satisfies",
    "ts_double_assert",
    "ts_result_type",
)

_add(
    "O(1)",
    "Constant at run time, and the narrowing costs nothing. A type guard, "
    "an `in` check and an instanceof are all one comparison — the compiler "
    "uses them to work out what the type is, but what executes is a single "
    "test. The knowledge is free; the check is one operation.",
    "ts_union_narrow",
    "ts_discriminated",
    "ts_narrow_in",
    "ts_type_guard",
    "ts_unknown",
    "ts_instanceof",
    "ts_assert_fn",
    "ts_optional_chain",
    "ts_never_exhaustive",
)

_add(
    "O(n)",
    "Linear at run time, in the length of the array — the filter visits "
    "each item once. The type predicate costs nothing: it changes what the "
    "compiler believes about the result, and the generated JavaScript is "
    "the same filter it would have written anyway.",
    "ts_filter_guard",
)

_add(
    "O(n)",
    "Linear in the number of keys, since walking an object means visiting "
    "each one. The cast that makes the keys typed is erased — the run-time "
    "code is a plain Object.keys and a loop.",
    "ts_typed_entries",
)

_add(
    "O(n)",
    "Linear in the number of nodes, because the recursion visits each "
    "exactly once. The recursive *type* costs nothing at run time, but it "
    "is worth knowing it is not free at compile time: deeply recursive "
    "types are what make a large project slow to type-check.",
    "ts_recursive_type",
    "ts_deep_conditional",
)

_add(
    "O(1)",
    "Constant per action. The reducer does a fixed amount of work for each "
    "action it is handed — the switch picks a branch and builds one new "
    "state object — so the cost follows how many actions you dispatch, not "
    "the size of any collection.",
    "ts_reducer",
)

_add(
    "O(n)",
    "Linear in the length of the array. A readonly array is exactly the "
    "same array at run time — readonly is a compile-time promise and is "
    "erased — so building a longer one with a spread copies every item, "
    "just as it would without the annotation.",
    "ts_readonly_array",
)
