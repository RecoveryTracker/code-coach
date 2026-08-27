"""Which compiler gets used, and which language version it is told to accept.

Two things here had no coverage and both had already caused a real problem.

The C and C++ runners only looked for gcc and clang, so on a Windows machine
with Visual Studio and no GNU toolchain — which is the common case — Run
simply refused, even though the machine compiles perfectly well.

The Rust runner passed no --edition, so rustc defaulted to 2015. That is not
a detail: array .into_iter() yields references in 2015 and values in 2021, so
a bank solution that had been checked by hand under 2021 failed through the
app. The check that caught it went through run_code; the one that missed it
did not.
"""

from __future__ import annotations

import shutil
import unittest

from code_coach.engine import _COMPILERS, msvc_available, run_code

HAS_RUSTC = shutil.which("rustc") is not None
HAS_GNU_C = any(shutil.which(c) for c in ("gcc", "clang"))
HAS_GNU_CPP = any(shutil.which(c) for c in ("g++", "clang++"))


class EditionTests(unittest.TestCase):
    def test_rust_is_pinned_to_a_modern_edition(self) -> None:
        """Stated in the flags, so it fails here rather than in a snippet."""
        _, extra = _COMPILERS[".rs"]
        self.assertIn("--edition", extra)
        self.assertIn("2021", extra)

    def test_every_compiled_language_pins_its_version(self) -> None:
        """Rust was the odd one out; C and C++ already did this."""
        for suffix, expect in (
            (".c", "-std=c17"),
            (".cpp", "-std=c++17"),
        ):
            with self.subTest(suffix=suffix):
                self.assertIn(expect, _COMPILERS[suffix][1])

    @unittest.skipUnless(HAS_RUSTC, "needs rustc on PATH")
    def test_the_edition_actually_reaches_the_compiler(self) -> None:
        """The exact difference that broke a bank solution.

        Under edition 2015 this yields &(i32, &str) and does not compile as
        written; under 2021 it yields the tuple itself.
        """
        source = (
            "fn main() {\n"
            '    let pairs = [(1, "a"), (2, "b")];\n'
            "    let out: Vec<i32> = pairs.into_iter().map(|(n, _)| n).collect();\n"
            '    println!("{:?}", out);\n'
            "}\n"
        )
        out, err, code = run_code(source, language="rust")
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out.strip(), "[1, 2]")


@unittest.skipUnless(msvc_available(), "needs a Visual Studio C++ toolchain")
class MsvcTests(unittest.TestCase):
    """The fallback for a Windows machine with no GNU compiler.

    These run wherever MSVC exists, including alongside gcc — the point is
    that the toolchain works, and _run_msvc is reached directly rather than
    through the PATH lookup so the test does not depend on gcc being absent.
    """

    def _msvc(self, source: str, suffix: str) -> tuple[str, str, int]:
        import tempfile
        from pathlib import Path

        from code_coach.engine import _run_msvc

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / f"program{suffix}"
            path.write_text(source, encoding="utf-8")
            return _run_msvc(path, timeout=120.0)

    def test_it_compiles_and_runs_c(self) -> None:
        source = (
            "#include <stdio.h>\n\n"
            "int main(void) {\n"
            '    printf("c ok\\n");\n'
            "    return 0;\n"
            "}\n"
        )
        out, err, code = self._msvc(source, ".c")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "c ok")

    def test_it_compiles_and_runs_cpp(self) -> None:
        source = (
            "#include <iostream>\n\n"
            "int main() {\n"
            '    std::cout << "cpp ok\\n";\n'
            "    return 0;\n"
            "}\n"
        )
        out, err, code = self._msvc(source, ".cpp")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "cpp ok")

    def test_it_accepts_cpp17(self) -> None:
        """The standard the cheat sheet teaches against."""
        source = (
            "#include <iostream>\n#include <optional>\n\n"
            "std::optional<int> find_one() { return 7; }\n\n"
            "int main() {\n"
            "    if (auto r = find_one(); r) {\n"
            '        std::cout << *r << "\\n";\n'
            "    }\n"
            "    return 0;\n"
            "}\n"
        )
        out, err, code = self._msvc(source, ".cpp")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), "7")

    def test_a_compile_error_reaches_the_student(self) -> None:
        """cl reports diagnostics on stdout, so a naive reader of stderr would
        hand back a failure with nothing in it."""
        source = "#include <stdio.h>\n\nint main(void) {\n    return oops;\n}\n"
        out, err, code = self._msvc(source, ".c")
        self.assertNotEqual(code, 0)
        self.assertIn("oops", err)

    def test_the_build_chatter_is_not_treated_as_output(self) -> None:
        """cl prints the source file name on success. The student did not
        write a program that says that."""
        source = (
            "#include <stdio.h>\n\n"
            "int main(void) {\n"
            '    printf("only this\\n");\n'
            "    return 0;\n"
            "}\n"
        )
        out, _, code = self._msvc(source, ".c")
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), "only this")
        self.assertNotIn("program.c", out)


class RunnerChoiceTests(unittest.TestCase):
    def test_c_and_cpp_can_be_built_on_this_machine(self) -> None:
        """Either toolchain will do. This fails only if neither is present,
        which is worth saying out loud rather than skipping past."""
        if not (HAS_GNU_C or msvc_available()):
            self.skipTest("no C toolchain at all")
        out, err, code = run_code(
            '#include <stdio.h>\n\nint main(void) {\n    printf("ok\\n");\n'
            "    return 0;\n}\n",
            language="c",
        )
        self.assertEqual(code, 0, err or out)
        self.assertEqual(out.strip(), "ok")

    def test_the_refusal_still_names_what_is_missing(self) -> None:
        """When nothing is installed the message has to be useful."""
        if HAS_GNU_CPP or msvc_available():
            self.skipTest("a C++ toolchain is present, so nothing refuses")
        _, err, code = run_code("int main() { return 0; }\n", language="cpp")
        self.assertEqual(code, 127)
        self.assertIn("PATH", err)


if __name__ == "__main__":
    unittest.main()
