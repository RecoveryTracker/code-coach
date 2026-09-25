"""The kata driver for Ruby.

The same shape as the Python and JavaScript drivers: the cases arrive
as JSON, the method is called once per case, and one marker line of
JSON comes back - the same marker, the same entry per case, the same
before-and-after check on the arguments - so `judge` reads it without
knowing which language wrote it.

Two things are Ruby's own. A method defined at the top of a file is a
private method of Object, so the driver looks for it with
private_method_defined? rather than respond_to?. And Ruby names the
temporary file in every error and backtrace, which `tidy` turns back
into the line numbers of the box.
"""

from __future__ import annotations

import json
import re

DRIVER = '''

# ── the marker ───────────────────────────────────────────────
require "json"

unless Object.private_method_defined?(:{name}) || Object.method_defined?(:{name})
  puts "<<<KATANAME>>>"
  exit 0
end
_kata_results = JSON.parse({cases}).map do |args|
  before = JSON.generate(args)
  begin
    got = send(:{name}, *args)
    changed = JSON.generate(args) != before
    begin
      JSON.generate([got])
    rescue StandardError
      got = got.inspect
    end
    {{ "got" => got, "changed" => changed }}
  rescue StandardError, SystemStackError => e
    {{ "error" => "#{{e.class}}: #{{e.message}}" }}
  end
end
puts "<<<KATA>>>" + JSON.generate(_kata_results)
'''


def signature(kata) -> str:
    return f"def {kata.name}({', '.join(kata.params)})"


def harness(kata, code: str) -> str:
    """The student's code with the driver appended, so its line numbers
    are the interpreter's."""
    cases = json.dumps(json.dumps([list(case) for case in kata.cases]))
    return code.rstrip() + "\n" + DRIVER.format(cases=cases, name=kata.name)


def tidy(detail: str) -> str:
    """Ruby's errors with the temporary file taken out.

    `/tmp/x.rb:3:in 'total': undefined method ...` becomes
    `Line 3: in 'total': undefined method ...`, and the backtrace lines
    below it (`from /tmp/x.rb:9:in ...`) go, because they are about the
    driver's call rather than the student's code.
    """
    out: list[str] = []
    for line in (detail or "").splitlines():
        if re.match(r"\s*from \S+\.rb:\d+", line):
            continue
        # The syntax checker's header: "<path>.rb: --> <path>.rb".
        if re.match(r"\s*\S+\.rb: -->", line):
            continue
        found = re.search(r"\S*\.rb:(\d+):\s?(.*)", line)
        if found:
            line = f"Line {found.group(1)}: {found.group(2)}".rstrip()
        out.append(line)
    return "\n".join(out).strip()
