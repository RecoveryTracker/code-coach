"""Review pages: bringing earlier material back.

An audit of the Python pages found that two hundred and ten of the three
hundred and forty-seven constructs the book teaches appear on exactly one
page. Twenty repetitions in one sitting and then never again. That is a gap
between pages rather than a fault in any of them, so no check on a single
page could ever have seen it.

These pages close it. Each one draws twenty exercises from a span of
earlier pages, one from each where the span allows, so the constructs come
back mixed rather than blocked. Mixing is the point and not a convenience:
practising one thing until it is smooth feels like learning and fades;
meeting it again among others you have to tell it apart from is what makes
it stick.

Nothing here is new work. Every exercise is one that already exists, with
its shape and its arguments unchanged, which means every one of them
already runs and already agrees with an answer computed independently. A
review page cannot be wrong in a way its source page was not.

These are the only pages in the book that mix shapes. Everything that used
to assume one shape per page has been told about it rather than left to
find out.
"""

from __future__ import annotations

from code_coach.workbook import Exercise, Page

#: How many exercises a review page holds, matching every other page.
PER_PAGE = 20

#: Roughly how many earlier pages one review page reaches back over. The
#: chunking evens out, so the real spans differ by a page or two.
SPAN = 19


def _chunks(items: list, size: int) -> list[list]:
    """Split into chunks of about `size`, evened out so none is tiny.

    A trailing chunk of one page would be a review of a single page, which
    is not a review.
    """
    if len(items) <= size:
        return [items]
    count = max(1, round(len(items) / size))
    base, extra = divmod(len(items), count)
    out, at = [], 0
    for i in range(count):
        take = base + (1 if i < extra else 0)
        out.append(items[at:at + take])
        at += take
    return out


def _pick(sources: list[Page], series: int = 1) -> list[tuple[Page, Exercise]]:
    """Twenty exercises, spread across the span rather than taken in bulk.

    One from each page first, so every page in the span is represented,
    then round again for the remainder. Which exercise moves along with
    each pass, so a second visit to a page is not the same numbers.

    `series` shifts the whole selection, which is what makes a second set
    of review pages worth having: the same spans, different exercises. One
    exercise does not use everything its page teaches, so a single pass
    over a page reaches about six constructs in ten.
    """
    picked: list[tuple[Page, Exercise]] = []
    lap = 0
    shift = (series - 1) * 11
    while len(picked) < PER_PAGE:
        for page in sources:
            if len(picked) >= PER_PAGE:
                break
            at = (shift + lap * 7 + sources.index(page) * 3) % len(page.exercises)
            picked.append((page, page.exercises[at]))
        lap += 1
    return picked


#: What each pass is called, so two pages over the same span do not
#: arrive with the same name.
_TITLES = {1: "Review", 2: "Second look"}


def _review_page(number: int, index: int, sources: list[Page],
                 language: str, series: int = 1) -> Page:
    first, last = sources[0].number, sources[-1].number
    page_id = f"review-{language}-{series}-{index:02d}"
    rows = _pick(sources, series)
    return Page(
        id=page_id,
        number=number,
        name=f"{_TITLES[series]}: pages {first} to {last}",
        teaches=(
            f"Twenty exercises drawn back from pages {first} to {last}, "
            f"mixed rather than grouped. If a page here has gone cold, that "
            f"is the page to go back to — forgetting it once and finding it "
            f"again is what fixes it in place."
        ),
        example=(
            f"Every exercise below already appeared once, somewhere between "
            f"pages {first} and {last}. Nothing here is new, and that is "
            f"the entire idea."
        ),
        exercises=tuple(
            Exercise(
                id=f"{page_id}-{i + 1:02d}",
                prompt=f"[page {src.number}] {ex.prompt}",
                shape=ex.shape,
                args=ex.args,
            )
            for i, (src, ex) in enumerate(rows)
        ),
        languages=(language,),
        tier="review",
    )


def review_pages(base: tuple[Page, ...], language: str = "python",
                 ) -> tuple[Page, ...]:
    """Build the review pages for one language from the pages it already has.

    Takes the assembled pages rather than importing them, because the
    module that assembles them is the one that calls this.
    """
    theirs = sorted(
        (p for p in base if p.applies_to(language) and p.tier != "review"),
        key=lambda p: p.number,
    )
    if not theirs:
        return ()
    chunks = _chunks(theirs, SPAN)
    start = max(p.number for p in theirs) + 1
    # One pass, not two. A second set over the same spans was built and
    # measured: it moved the constructs revisited from fifty-nine per cent
    # to sixty-two, for twice the pages. That is because a page is one
    # shape, so its twenty exercises largely use the same constructs and a
    # different one from the same page reaches nearly the same vocabulary.
    # What is still unrevisited sits in shape variants rather than in
    # different arguments, so more passes will not reach it. Three points
    # for three hundred and sixty exercises is padding.
    return tuple(
        _review_page(start + i, i + 1, chunk, language)
        for i, chunk in enumerate(chunks)
    )
