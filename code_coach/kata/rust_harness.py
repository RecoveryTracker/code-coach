"""The Rust driver: run a student's function against every case.

Plain rustc has no JSON library, so this works the other way round from the
JavaScript and Dart drivers. Instead of parsing the cases at runtime, each
case is written into the program as Rust literals of the declared types -
`vec![1, 2, 3]`, `"text"`, `String::from("text")` - and the results are
printed as JSON by a small trait defined in the driver. The output is the
same marker line every driver prints, so `judge` reads it without knowing
which language wrote it.

A panic in one case is caught (`catch_unwind`) and reported against that
case, the way an exception is in the other languages. Rust cannot change
what it was handed unless a parameter is `&mut`, and the forms here never
ask for one, so `changed` is always false.
"""

from __future__ import annotations

import json
import re

INTS = ("i8", "i16", "i32", "i64", "isize", "u8", "u16", "u32", "u64", "usize")

DRIVER = r"""

// ── the marker ───────────────────────────────────────────────
#[allow(dead_code)]
trait KataJson {
    fn kata_json(&self) -> String;
}
macro_rules! kata_json_number {
    ($($t:ty),*) => { $(impl KataJson for $t { fn kata_json(&self) -> String { self.to_string() } })* };
}
kata_json_number!(i8, i16, i32, i64, isize, u8, u16, u32, u64, usize);
impl KataJson for f64 {
    fn kata_json(&self) -> String {
        if !self.is_finite() { "null".to_string() }
        else if self.fract() == 0.0 { format!("{:.1}", self) }
        else { format!("{}", self) }
    }
}
impl KataJson for bool {
    fn kata_json(&self) -> String { self.to_string() }
}
impl KataJson for char {
    fn kata_json(&self) -> String { self.to_string().kata_json() }
}
impl KataJson for str {
    fn kata_json(&self) -> String {
        let mut out = String::from("\"");
        for ch in self.chars() {
            match ch {
                '"' => out.push_str("\\\""),
                '\\' => out.push_str("\\\\"),
                '\n' => out.push_str("\\n"),
                '\t' => out.push_str("\\t"),
                c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
                c => out.push(c),
            }
        }
        out.push('"');
        out
    }
}
impl KataJson for String {
    fn kata_json(&self) -> String { self.as_str().kata_json() }
}
impl<T: KataJson> KataJson for [T] {
    fn kata_json(&self) -> String {
        format!("[{}]", self.iter().map(|x| x.kata_json()).collect::<Vec<_>>().join(","))
    }
}
impl<T: KataJson> KataJson for Vec<T> {
    fn kata_json(&self) -> String { self.as_slice().kata_json() }
}
impl<T: KataJson> KataJson for Option<T> {
    fn kata_json(&self) -> String {
        match self { Some(x) => x.kata_json(), None => "null".to_string() }
    }
}
impl<T: KataJson + ?Sized> KataJson for &T {
    fn kata_json(&self) -> String { (**self).kata_json() }
}
impl<A: KataJson, B: KataJson> KataJson for (A, B) {
    fn kata_json(&self) -> String { format!("[{},{}]", self.0.kata_json(), self.1.kata_json()) }
}

fn kata_panic_text(e: Box<dyn std::any::Any + Send>) -> String {
    let text = e.downcast_ref::<&str>().map(|s| s.to_string())
        .or_else(|| e.downcast_ref::<String>().cloned())
        .unwrap_or_else(|| "it panicked".to_string());
    format!("panic: {}", text)
}

fn main() {
    std::panic::set_hook(Box::new(|_| {}));
    let mut kata_results: Vec<String> = Vec::new();
CASES
    println!("<<<KATA>>>[{}]", kata_results.join(","));
}
"""

def _case(call: str) -> str:
    """One case: call it, and push {"got": ...} or {"error": ...}. Built by
    joining rather than str.format, because Rust's own format! braces would
    have to be doubled twice over."""
    return (
        "    match std::panic::catch_unwind(|| " + call + ") {\n"
        '        Ok(got) => kata_results.push(format!("{{\\"got\\":{},\\"changed\\":false}}", got.kata_json())),\n'
        '        Err(e) => kata_results.push(format!("{{\\"error\\":{}}}", kata_panic_text(e).kata_json())),\n'
        "    }"
    )


def _split_top(text: str) -> list[str]:
    """Split "A, B<C, D>" at the commas that are not inside brackets."""
    parts, depth, start = [], 0, 0
    for i, ch in enumerate(text):
        if ch in "<([":
            depth += 1
        elif ch in ">)]":
            depth -= 1
        elif ch == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    parts.append(text[start:].strip())
    return [p for p in parts if p]


def literal(kind: str, value) -> str:
    """A Rust expression of type `kind` holding the JSON-ish Python `value`."""
    kind = kind.strip()
    if kind in INTS:
        return f"{int(value)}_{kind}"
    if kind == "f64":
        return f"{float(value)!r}_f64"
    if kind == "bool":
        return "true" if value else "false"
    if kind == "char":
        return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"
    if kind == "&str":
        return json.dumps(str(value), ensure_ascii=False)
    if kind == "String":
        return f"String::from({json.dumps(str(value), ensure_ascii=False)})"
    if kind.startswith("Vec<") and kind.endswith(">"):
        inner = kind[4:-1]
        return "vec![" + ", ".join(literal(inner, v) for v in value) + "]"
    if kind.startswith("&[") and kind.endswith("]"):
        inner = kind[2:-1]
        if not value:
            return f"&[] as &[{inner}]"
        return "&[" + ", ".join(literal(inner, v) for v in value) + "]"
    if kind.startswith("Option<") and kind.endswith(">"):
        return "None" if value is None else f"Some({literal(kind[7:-1], value)})"
    if kind.startswith("(") and kind.endswith(")"):
        kinds = _split_top(kind[1:-1])
        return "(" + ", ".join(literal(k, v) for k, v in zip(kinds, value)) + ")"
    raise ValueError(f"no Rust literal for type {kind}")


def harness(kata, code: str) -> str:
    calls = []
    for case in kata.cases:
        args = ", ".join(literal(k, v) for k, v in zip(kata.types, case))
        calls.append(_case(f"{kata.name}({args})"))
    return code.rstrip() + "\n" + DRIVER.replace("CASES", "\n".join(calls))


def signature(kata) -> str:
    typed = ", ".join(f"{p}: {t}" for p, t in zip(kata.params, kata.types))
    returns = f" -> {kata.returns}" if kata.returns else ""
    return f"fn {kata.name}({typed}){returns} {{"


def missing(kata, stdout: str, stderr: str) -> bool:
    """rustc's error for calling a function that is not defined."""
    return "<<<KATA>>>" not in (stdout or "") and (
        f"cannot find function `{kata.name}` in this scope" in (stderr or ""))


def tidy(detail: str) -> str:
    """rustc names the temporary file on every error: say "line N" instead."""
    return re.sub(r"-->\s*\S+?\.rs:(\d+):(\d+)", r"--> line \1", detail or "")
