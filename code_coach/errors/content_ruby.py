"""Ruby crashes.

Same rules as `content.py`: every message and line was copied from what
Ruby 4.0 printed, and tests/test_errors_ruby.py holds them to a real
run. They make one family of their own, "Ruby", the way the Dart set
did.

Ruby's first line of red says three things at once:

    x.rb:3:in '<main>': undefined method 'upcase' for nil (NoMethodError)

the line, the method it was in, and the message with the class of the
error at the end, in brackets. The message recorded here is the part
after the method - the sentence, and the class - because the line is a
question of its own. `nil` in that sentence is the clue most people
skip: the method exists, the value it was called on did not.

Ruby 4 does not freeze string literals by default (it can warn, but
"abc" << "d" still works), so the frozen one here freezes an array on
purpose, which is where people meet FrozenError in practice.
"""

from __future__ import annotations

from code_coach.errors import Crash, _c

RUBY = "Ruby"


RUBY_CRASHES: tuple[Crash, ...] = (
    _c(
        id="err-rb-nil-from-missing-key",
        level=1,
        name="A key the hash does not have",
        family=RUBY,
        language="ruby",
        code=(
            "user = { \"name\" => \"Ada\", \"city\" => \"London\" }\n"
            "puts user[\"name\"].upcase\n"
            "puts user[\"email\"].upcase"
        ),
        message="undefined method 'upcase' for nil (NoMethodError)",
        line=3,
        meaning="user[\"email\"] was nil, and nil has no upcase",
        decoys=(
            "upcase does not exist for strings in Ruby 4",
            "user was nil by the time line 3 ran",
            "The email is stored in lower case already",
        ),
        fix=(
            "'for nil' is the part to read: the method is real, the value "
            "it was called on was nothing. A Hash answers nil for a key it "
            "does not have rather than raising, so the crash lands one "
            "step later, on the method. Line 2 worked, so user was fine. "
            "Either make sure the key is there, use user.fetch(\"email\") "
            "to fail right at the lookup, or write "
            "user[\"email\"]&.upcase to get nil instead of a crash."
        ),
    ),
    _c(
        id="err-rb-method-typo",
        level=1,
        name="A method name spelled wrong",
        family=RUBY,
        language="ruby",
        code=(
            "names = [\"ada\", \"lin\", \"grace\"]\n"
            "puts \"Team of #{names.lenght}\""
        ),
        message=(
            "undefined method 'lenght' for an instance of Array "
            "(NoMethodError)"
        ),
        line=2,
        meaning="Arrays have no method called lenght",
        decoys=(
            "names is nil, so nothing can be called on it",
            "Methods cannot be called inside #{} interpolation",
            "The array has to be converted to a string first",
        ),
        fix=(
            "'for an instance of Array' says the value was fine - a real "
            "array - and the problem is the name asked of it. Compare "
            "with 'for nil' in the one before, where the value was the "
            "problem. Ruby usually prints a 'Did you mean?' line under "
            "the message; here it suggests length. Spell it the way the "
            "class does: names.length (or size, or count)."
        ),
    ),
    _c(
        id="err-rb-undefined-local",
        level=2,
        name="A variable that was never made",
        family=RUBY,
        language="ruby",
        code=(
            "prices = [4, 10, 6]\n"
            "total = 0\n"
            "prices.each { |p| total += p }\n"
            "puts \"Total: #{total}, most: #{price.max}\""
        ),
        message=(
            "undefined local variable or method 'price' for main (NameError)"
        ),
        line=4,
        meaning="No variable or method named price exists there",
        decoys=(
            "max cannot be used on an array of numbers",
            "total was not finished adding up when line 4 ran",
            "The block variable p is gone after line 3",
        ),
        fix=(
            "NameError means Ruby could not find the name at all - not "
            "that the value was wrong. It says 'local variable or method' "
            "because a bare word could be either, and it was neither. "
            "The variable is prices, plural; price was never assigned. "
            "'for main' only means the code was at the top of the file, "
            "outside any class. Use the name you defined: prices.max."
        ),
    ),
    _c(
        id="err-rb-string-plus-integer",
        level=2,
        name="Adding a number to text",
        family=RUBY,
        language="ruby",
        code=(
            "count = 3\n"
            "label = \"Items: \" + count\n"
            "puts label"
        ),
        message="no implicit conversion of Integer into String (TypeError)",
        line=2,
        meaning="String#+ only takes another String, and count is an Integer",
        decoys=(
            "count was nil, so there was nothing to add",
            "Strings cannot be joined with + in Ruby, only with <<",
            "The number 3 is too large to fit into a label",
        ),
        fix=(
            "Ruby will not turn a number into text behind your back the "
            "way JavaScript does. The + here is the String's, and it "
            "wants a String on the right; 'no implicit conversion' means "
            "it refused to guess. Say what you mean: "
            "\"Items: #{count}\" with interpolation, which is the usual "
            "Ruby way, or \"Items: \" + count.to_s."
        ),
    ),
    _c(
        id="err-rb-fetch-missing-key",
        level=3,
        name="fetch with no fallback",
        family=RUBY,
        language="ruby",
        code=(
            "config = { \"port\" => 8080, \"debug\" => false }\n"
            "port = config.fetch(\"port\")\n"
            "host = config.fetch(\"host\")\n"
            "puts \"#{host}:#{port}\""
        ),
        message="key not found: \"host\" (KeyError)",
        line=3,
        meaning="The hash has no \"host\" key, and fetch raises when a key is missing",
        decoys=(
            "fetch reads settings from a file that could not be found",
            "Keys must be symbols, so \"port\" failed on line 2",
            "host is a reserved word and cannot be used as a key",
        ),
        fix=(
            "This is fetch doing its job. config[\"host\"] would have "
            "handed back nil and crashed somewhere later; fetch stops at "
            "the lookup and names the key. Line 2 worked, so the hash and "
            "its string keys are fine - only host is missing. Add it to "
            "the config, or give fetch a fallback: "
            "config.fetch(\"host\", \"localhost\")."
        ),
    ),
    _c(
        id="err-rb-frozen-constant",
        level=4,
        name="Adding to a frozen list",
        family=RUBY,
        language="ruby",
        code=(
            "SIZES = [\"S\", \"M\", \"L\"].freeze\n"
            "\n"
            "def with_extra(size)\n"
            "  SIZES << size\n"
            "end\n"
            "\n"
            "puts with_extra(\"XL\").join(\", \")"
        ),
        message="can't modify frozen Array: [\"S\", \"M\", \"L\"] (FrozenError)",
        line=4,
        meaning="SIZES was frozen, so << cannot change it",
        decoys=(
            "Constants can never be used inside a method",
            "<< only works on strings, not on arrays",
            "The error is on line 7, where with_extra is called",
        ),
        fix=(
            "freeze on line 1 promised nobody would change SIZES, and "
            "<< on line 4 tried to - Ruby blames the line that broke the "
            "promise, inside the method, not the call on line 7. Freezing "
            "a shared list is often right; the helper should build a new "
            "array instead of changing it: SIZES + [size] leaves SIZES "
            "alone and hands back a longer copy."
        ),
    ),
)
