"""The HTML and CSS typing drills.

These are marked character for character against a reference, so the
thing the suite has to protect is the reference. Somebody is going to
type each of these a dozen times and then write it from memory
afterwards — a drill with an unclosed tag, a label pointing at an id
that is not there, or an image with no alt text does not teach a small
mistake, it teaches a habit.

So the checks here are mostly about the markup being exemplary rather
than merely present, and the strictest of them are the accessibility
ones, because those are the mistakes that are invisible to the person
making them.
"""

from __future__ import annotations

import re
import unittest

from code_coach.markup import VOID, drill, drill_families, drills, tidy


def _tags(html: str) -> list[tuple[str, bool]]:
    """Every tag in source order, as (name, is_closing).

    A real parser would be better and is not available; this is enough
    to catch the mistake it is here for, which is a tag nobody closed.
    Comments and the doctype are dropped first so they cannot look like
    tags.
    """
    without = re.sub(r"<!--.*?-->", "", html, flags=re.S)
    without = re.sub(r"<!doctype[^>]*>", "", without, flags=re.I)
    found = []
    for match in re.finditer(r"<\s*(/?)\s*([a-zA-Z][\w-]*)([^>]*)>", without):
        closing, name, rest = match.group(1), match.group(2).lower(), match.group(3)
        if rest.rstrip().endswith("/"):
            continue  # self-closed, which is legal for the void ones
        found.append((name, bool(closing)))
    return found


class ShapeTests(unittest.TestCase):
    def test_there_are_some_in_every_family(self) -> None:
        self.assertGreaterEqual(len(drills()), 16)
        for family in drill_families():
            with self.subTest(family=family):
                self.assertGreaterEqual(len(drills(family)), 4)

    def test_ids_are_unique(self) -> None:
        ids = [d.id for d in drills()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_drill_is_findable_by_id(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertIs(drill(d.id), d)

    def test_they_are_short_enough_to_do_twelve_times(self) -> None:
        """The whole premise is repetition. A drill long enough to be a
        chore gets done once, which is the same as not existing."""
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertLessEqual(
                    d.lines, 16, f"{d.id} is {d.lines} lines")
                self.assertTrue(d.code.strip())

    def test_the_code_is_already_tidy(self) -> None:
        """What is typed is compared against this after tidying, so a
        reference that is not itself tidy is one nobody can match: it
        would demand a trailing space that cannot be seen."""
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertEqual(d.code, tidy(d.code))

    def test_the_ranking_was_done(self) -> None:
        for family in drill_families():
            with self.subTest(family=family):
                levels = [d.level for d in drills(family)]
                self.assertEqual(levels, sorted(levels))
                self.assertGreater(len(set(levels)), 1)
                for level in levels:
                    self.assertIn(level, range(1, 6))

    def test_every_drill_says_what_it_is_for(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertGreater(
                    len(d.note), 80, f"{d.id}'s note explains nothing")
                self.assertTrue(d.name.strip())


class DocumentTests(unittest.TestCase):
    """What gets rendered has to be a page, whichever kind of drill it
    is — a piece on its own renders as nothing much, and the render is
    the reason this mode exists."""

    def test_every_drill_renders_as_a_whole_document(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                page = d.document()
                self.assertIn("<!doctype html>", page.lower())
                self.assertIn("<html", page)
                self.assertIn("</html>", page)
                self.assertIn("<body", page)

    def test_the_piece_reaches_the_page_intact(self) -> None:
        """Indentation included. The wrapper used to re-indent what it
        was given, which stripped the first line and doubled the rest."""
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertIn(d.code, d.document())

    def test_the_placeholder_is_replaced(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                self.assertNotIn("{{drill}}", d.document())

    def test_what_you_typed_is_what_renders(self) -> None:
        """Not the reference. A preview of the right answer while you
        are typing the wrong one is a preview of somebody else's work,
        and watching your own mistake render is the point."""
        for d in drills():
            with self.subTest(drill=d.id):
                page = d.document("<p>WHAT I TYPED</p>")
                self.assertIn("WHAT I TYPED", page)
                self.assertNotIn(d.code, page)


class MarkupQualityTests(unittest.TestCase):
    """Typed a dozen times and written from memory afterwards. These
    are the habits that would be learned."""

    def test_every_tag_that_opens_is_closed(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                stack: list[str] = []
                for name, closing in _tags(d.document()):
                    if name in VOID:
                        self.assertFalse(
                            closing, f"{d.id} closes <{name}>, which is void")
                        continue
                    if closing:
                        self.assertTrue(
                            stack, f"{d.id} closes </{name}> with nothing open")
                        self.assertEqual(
                            stack.pop(), name,
                            f"{d.id} closes </{name}> out of order")
                    else:
                        stack.append(name)
                self.assertEqual(stack, [], f"{d.id} leaves {stack} open")

    def test_every_image_has_alt_text(self) -> None:
        """The one that is invisible to the person leaving it out."""
        for d in drills():
            for tag in re.findall(r"<img[^>]*>", d.document()):
                with self.subTest(drill=d.id):
                    self.assertIn(
                        "alt=", tag, f"{d.id} has an img with no alt")

    def test_every_label_points_at_something_real(self) -> None:
        """A `for` naming an id that is not in the document is a label
        that looks wired up and is not — which is exactly the bug the
        Forms family exists to stop somebody writing."""
        for d in drills():
            page = d.document()
            ids = set(re.findall(r'\bid="([^"]+)"', page))
            for target in re.findall(r'<label[^>]*\bfor="([^"]+)"', page):
                with self.subTest(drill=d.id, label=target):
                    self.assertIn(
                        target, ids,
                        f"{d.id}: a label points at #{target}, which is "
                        f"not in the page")

    def test_aria_describedby_points_at_something_real(self) -> None:
        for d in drills():
            page = d.document()
            ids = set(re.findall(r'\bid="([^"]+)"', page))
            for target in re.findall(r'aria-describedby="([^"]+)"', page):
                for one in target.split():
                    with self.subTest(drill=d.id, describedby=one):
                        self.assertIn(one, ids)

    def test_every_button_says_which_kind_it_is(self) -> None:
        """A button in a form with no type is a submit button, which is
        how a 'Cancel' ends up submitting the form."""
        for d in drills():
            for tag in re.findall(r"<button[^>]*>", d.document()):
                with self.subTest(drill=d.id):
                    self.assertIn("type=", tag, f"{d.id}: {tag} has no type")

    def test_no_id_is_used_twice(self) -> None:
        for d in drills():
            with self.subTest(drill=d.id):
                ids = re.findall(r'\bid="([^"]+)"', d.document())
                self.assertEqual(
                    len(ids), len(set(ids)), f"{d.id} repeats an id")


class TidyTests(unittest.TestCase):
    """What the marker forgives, and what it does not."""

    def test_trailing_whitespace_is_forgiven(self) -> None:
        self.assertEqual(tidy("<p>a</p>   \n<p>b</p>"), "<p>a</p>\n<p>b</p>")

    def test_windows_line_endings_are_forgiven(self) -> None:
        self.assertEqual(tidy("<p>a</p>\r\n<p>b</p>"), "<p>a</p>\n<p>b</p>")

    def test_blank_lines_at_the_ends_are_forgiven(self) -> None:
        self.assertEqual(tidy("\n\n<p>a</p>\n\n"), "<p>a</p>")

    def test_indentation_is_not_forgiven(self) -> None:
        """It is half of what makes markup readable, and it is a real
        part of what is being practised."""
        self.assertNotEqual(tidy("  <p>a</p>"), tidy("<p>a</p>"))

    def test_a_blank_line_in_the_middle_is_not_forgiven(self) -> None:
        """Several drills use one to separate two rules, and that
        spacing is deliberate."""
        self.assertNotEqual(tidy("a\n\nb"), tidy("a\nb"))


if __name__ == "__main__":
    unittest.main()
