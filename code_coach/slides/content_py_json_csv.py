"""JSON and CSV: a passive deck. Every `output` was worked out by hand and
tests/test_slides.py runs each `code` for real and requires the two to agree."""

from __future__ import annotations

from . import Deck, Slide

ORDER = 103

DECK = Deck(
    id="py-json-csv",
    title="JSON and CSV",
    language="python",
    blurb="Turn data into text and back: json.dumps and loads, type changes on the way, and the csv module.",
    slides=(
        Slide(
            title="json.dumps and sort_keys",
            text="json.dumps turns Python data into a JSON string. Keys keep their insertion order unless you pass sort_keys=True.",
            code=r"""import json
d = {"b": 1, "a": [1, 2]}
print(json.dumps(d))
print(json.dumps(d, sort_keys=True))""",
            output='{"b": 1, "a": [1, 2]}\n{"a": [1, 2], "b": 1}',
            point="dumps gives a str; sort_keys=True makes the output the same every time.",
        ),
        Slide(
            title="indent for readable JSON",
            text="Pass indent=2 and dumps lays the data out over several lines, one level of nesting per step. It is the same data, only easier for a person to read.",
            code=r"""import json
data = {"name": "Ann", "tags": ["a", "b"]}
print(json.dumps(data, indent=2))""",
            output='{\n  "name": "Ann",\n  "tags": [\n    "a",\n    "b"\n  ]\n}',
            point="indent=2 is for people; leave it out for the smallest output.",
        ),
        Slide(
            title="json.loads: text to data",
            text="json.loads parses a JSON string back into Python objects. Objects become dicts, arrays become lists, and true, false and null become True, False and None.",
            code=r"""import json
s = '{"n": 3, "ok": true, "x": null}'
d = json.loads(s)
print(d)
print(type(d["n"]).__name__, d["ok"] is True, d["x"])""",
            output="{'n': 3, 'ok': True, 'x': None}\nint True None",
            point="loads reads a string; the s stands for string.",
        ),
        Slide(
            title="Python types vs JSON types",
            text="Going out, a tuple becomes an array, None becomes null, and True becomes true. Text is wrapped in double quotes, and numbers are written plainly.",
            code=r"""import json
print(json.dumps([(1, 2), None, True, False, 1.5]))
print(json.dumps("hi"), json.dumps(3))""",
            output='[[1, 2], null, true, false, 1.5]\n"hi" 3',
            point="JSON has no tuple, no None and no capital True.",
        ),
        Slide(
            title="Keys become strings",
            text="A JSON object can only have text keys. A dict with int keys is written with string keys, and when you load it back the keys stay strings.",
            code=r"""import json
d = {1: "a", 2: "b"}
s = json.dumps(d)
print(s)
print(json.loads(s))
print(json.loads(s) == d)""",
            output='{"1": "a", "2": "b"}\n{\'1\': \'a\', \'2\': \'b\'}\nFalse',
            point="Int keys do not survive a JSON trip; convert them back yourself.",
        ),
        Slide(
            title="Round-tripping is not exact",
            text="Dumping and then loading gives equal data only when every type has a JSON twin. A tuple comes back as a list, so the two are no longer equal.",
            code=r"""import json
orig = {"pt": (1, 2)}
back = json.loads(json.dumps(orig))
print(back)
print(back == orig)
print(back == {"pt": [1, 2]})""",
            output="{'pt': [1, 2]}\nFalse\nTrue",
            point="After a round trip, check what changed: tuples, int keys and sets do.",
        ),
        Slide(
            title="default= for a custom object",
            text="json cannot write your own class and raises TypeError. Give dumps a default function: it is called for anything unknown, and returns something JSON can write.",
            code=r"""import json
class P:
    def __init__(self, x):
        self.x = x
def enc(o):
    return {"x": o.x}
print(json.dumps([P(1), P(2)], default=enc))""",
            output='[{"x": 1}, {"x": 2}]',
            point="default= is the escape hatch for types JSON does not know.",
        ),
        Slide(
            title="Compact JSON with separators",
            text="The default output has a space after every comma and colon. Pass separators=(',', ':') to remove them, which is what you want when sending JSON over a network.",
            code=r"""import json
d = {"a": [1, 2], "b": 3}
print(json.dumps(d))
print(json.dumps(d, separators=(",", ":")))""",
            output='{"a": [1, 2], "b": 3}\n{"a":[1,2],"b":3}',
            point="separators=(',', ':') gives the smallest valid JSON.",
        ),
        Slide(
            title="csv.reader over text",
            text="csv.reader takes any source of lines and gives each row as a list of strings. io.StringIO makes a piece of text behave like a file, so there is no real file to open.",
            code=r"""import csv, io
text = "name,age\nAnn,30\nBo,25\n"
for row in csv.reader(io.StringIO(text)):
    print(row)""",
            output="['name', 'age']\n['Ann', '30']\n['Bo', '25']",
            point="Each row is a list; the first row is the header unless you skip it.",
        ),
        Slide(
            title="csv.DictReader",
            text="DictReader uses the first row as column names and gives every later row as a dict. You then read a field by name instead of by position.",
            code=r"""import csv, io
text = "name,age\nAnn,30\nBo,25\n"
rows = list(csv.DictReader(io.StringIO(text)))
print(rows[0])
print(rows[1]["name"])""",
            output="{'name': 'Ann', 'age': '30'}\nBo",
            point="DictReader rows are plain dicts keyed by the header.",
        ),
        Slide(
            title="CSV numbers come back as text",
            text="A CSV file holds only text, so the reader returns every field as a str, even 30. Convert with int() or float() before you add or compare.",
            code=r"""import csv, io
text = "name,age\nAnn,30\nBo,25\n"
ages = [r["age"] for r in csv.DictReader(io.StringIO(text))]
print(ages, sum(int(a) for a in ages))
print("30" + "25")""",
            output="['30', '25'] 55\n3025",
            point="Everything read from a CSV is a string until you convert it.",
        ),
        Slide(
            title="csv.writer into a string",
            text="csv.writer sends rows to anything with a write method, such as io.StringIO. By default each row ends with the two characters \\r\\n, so repr is the way to see exactly what was written.",
            code=r"""import csv, io
out = io.StringIO()
w = csv.writer(out)
w.writerow(["a", "b"])
w.writerow([1, 2])
print(repr(out.getvalue()))""",
            output="'a,b\\r\\n1,2\\r\\n'",
            point="csv.writer ends rows with \\r\\n unless you set lineterminator.",
        ),
        Slide(
            title="Quoting fields with commas",
            text="When a field holds a comma or a double quote, the writer wraps it in quotes and doubles any quote inside. The reader undoes all of that, so the text is safe both ways.",
            code=r"""import csv, io
out = io.StringIO()
w = csv.writer(out)
w.writerow(["Smith, Ann", 'say "hi"', 5])
print(out.getvalue().strip())""",
            output='"Smith, Ann","say ""hi""",5',
            point="Never join fields with commas by hand; let csv do the quoting.",
        ),
        Slide(
            title="Why not just split on commas?",
            text="A plain split cuts inside a quoted field and leaves stray quote marks. csv.reader understands quotes, so a comma inside a field stays part of that field.",
            code=r"""import csv
line = '"Smith, Ann",30'
print(next(csv.reader([line])))
print(line.split(","))""",
            output="['Smith, Ann', '30']\n['\"Smith', ' Ann\"', '30']",
            point="split(',') breaks on quoted commas; csv.reader does not.",
        ),
        Slide(
            title="csv.DictWriter",
            text="DictWriter writes dicts as rows, in the order of fieldnames. writeheader writes the column names first. Setting lineterminator to a plain newline keeps the output simple.",
            code=r"""import csv, io
out = io.StringIO()
w = csv.DictWriter(out, fieldnames=["n", "v"], lineterminator="\n")
w.writeheader()
w.writerows([{"n": "a", "v": 1}, {"n": "b", "v": 2}])
print(out.getvalue(), end="")""",
            output="n,v\na,1\nb,2",
            point="DictWriter: fieldnames, writeheader(), then writerows().",
        ),
    ),
)
