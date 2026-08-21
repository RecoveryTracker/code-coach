"""Longer passages to type: scripture, affirmations, and conscious vocabulary.

Typing drills are repetition, and repetition sinks in whether you meant it to
or not. What you repeat for twenty minutes is worth choosing on purpose, so
these are passages people actually want in their head.

Scripture is King James Version — published 1611, public domain worldwide, so
it can ship with the app. Modern translations (NIV, ESV, NLT and the rest) are
under copyright and are not included.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Passage:
    text: str
    source: str  # shown under the line, so you learn the reference too


def _p(text: str, source: str) -> Passage:
    return Passage(text, source)


# ── Scripture (KJV, public domain) ──────────────────────────
# Short enough to type in one go; the reference is the note, so the drill
# teaches where it comes from as well as the words.

VERSES: tuple[Passage, ...] = (
    _p("The LORD is my shepherd; I shall not want.", "Psalm 23:1"),
    _p(
        "He maketh me to lie down in green pastures: he leadeth me beside the "
        "still waters.",
        "Psalm 23:2",
    ),
    _p("Be still, and know that I am God.", "Psalm 46:10"),
    _p(
        "Thy word is a lamp unto my feet, and a light unto my path.",
        "Psalm 119:105",
    ),
    _p(
        "This is the day which the LORD hath made; we will rejoice and be glad "
        "in it.",
        "Psalm 118:24",
    ),
    _p(
        "Trust in the LORD with all thine heart; and lean not unto thine own "
        "understanding.",
        "Proverbs 3:5",
    ),
    _p(
        "A soft answer turneth away wrath: but grievous words stir up anger.",
        "Proverbs 15:1",
    ),
    _p(
        "Iron sharpeneth iron; so a man sharpeneth the countenance of his "
        "friend.",
        "Proverbs 27:17",
    ),
    _p(
        "To every thing there is a season, and a time to every purpose under "
        "the heaven.",
        "Ecclesiastes 3:1",
    ),
    _p(
        "They that wait upon the LORD shall renew their strength; they shall "
        "mount up with wings as eagles.",
        "Isaiah 40:31",
    ),
    _p(
        "Let your light so shine before men, that they may see your good "
        "works.",
        "Matthew 5:16",
    ),
    _p(
        "Ask, and it shall be given you; seek, and ye shall find; knock, and "
        "it shall be opened unto you.",
        "Matthew 7:7",
    ),
    _p(
        "Come unto me, all ye that labour and are heavy laden, and I will give "
        "you rest.",
        "Matthew 11:28",
    ),
    _p("Jesus wept.", "John 11:35"),
    _p(
        "And ye shall know the truth, and the truth shall make you free.",
        "John 8:32",
    ),
    _p(
        "A new commandment I give unto you, That ye love one another.",
        "John 13:34",
    ),
    _p(
        "And we know that all things work together for good to them that love "
        "God.",
        "Romans 8:28",
    ),
    _p(
        "Charity suffereth long, and is kind; charity envieth not; charity "
        "vaunteth not itself, is not puffed up.",
        "1 Corinthians 13:4",
    ),
    _p(
        "But the fruit of the Spirit is love, joy, peace, longsuffering, "
        "gentleness, goodness, faith.",
        "Galatians 5:22",
    ),
    _p(
        "I can do all things through Christ which strengtheneth me.",
        "Philippians 4:13",
    ),
    _p(
        "Let us not be weary in well doing: for in due season we shall reap, "
        "if we faint not.",
        "Galatians 6:9",
    ),
    _p(
        "Every good gift and every perfect gift is from above.",
        "James 1:17",
    ),
)

# A few longer runs, for a real speed test rather than a single line.
CHAPTERS: tuple[Passage, ...] = (
    _p(
        "The LORD is my shepherd; I shall not want. He maketh me to lie down "
        "in green pastures: he leadeth me beside the still waters. He "
        "restoreth my soul: he leadeth me in the paths of righteousness for "
        "his name's sake.",
        "Psalm 23:1-3",
    ),
    _p(
        "To every thing there is a season, and a time to every purpose under "
        "the heaven: a time to be born, and a time to die; a time to plant, "
        "and a time to pluck up that which is planted.",
        "Ecclesiastes 3:1-2",
    ),
    _p(
        "Though I speak with the tongues of men and of angels, and have not "
        "charity, I am become as sounding brass, or a tinkling cymbal.",
        "1 Corinthians 13:1",
    ),
    _p(
        "Finally, brethren, whatsoever things are true, whatsoever things are "
        "honest, whatsoever things are just, whatsoever things are pure, "
        "whatsoever things are lovely, think on these things.",
        "Philippians 4:8",
    ),
)


# Passages keyed to the reading themes in the Jesus App — Mercy, Courage,
# Peace, Wisdom — so the two apps cover the same ground. That app carries the
# references and its own reflections but no Bible text on purpose; the KJV text
# here is public domain, so it can sit alongside them.

THEMED: tuple[Passage, ...] = (
    _p(
        "And who is my neighbour? ... Go, and do thou likewise.",
        "Luke 10:29,37 · Mercy",
    ),
    _p(
        "But when he was yet a great way off, his father saw him, and had "
        "compassion, and ran, and fell on his neck, and kissed him.",
        "Luke 15:20 · Mercy",
    ),
    _p(
        "Be of good cheer; it is I; be not afraid.",
        "Matthew 14:27 · Courage",
    ),
    _p(
        "Daughter, thy faith hath made thee whole; go in peace.",
        "Mark 5:34 · Courage",
    ),
    _p(
        "Blessed are the meek: for they shall inherit the earth.",
        "Matthew 5:5 · Peace",
    ),
    _p(
        "Peace I leave with you, my peace I give unto you: not as the world "
        "giveth, give I unto you.",
        "John 14:27 · Peace",
    ),
    _p(
        "Whosoever heareth these sayings of mine, and doeth them, I will liken "
        "him unto a wise man, which built his house upon a rock.",
        "Matthew 7:24 · Wisdom",
    ),
    _p(
        "Thou shalt love thy neighbour as thyself. There is none other "
        "commandment greater than these.",
        "Mark 12:31 · Wisdom",
    ),
)


# ── On typing, and on getting better at things ──────────────
# The default material. Typing practice is twenty minutes of reading a line
# and reproducing it, so the line may as well be about what you're doing —
# these say the useful things a typing course would otherwise bury in a help
# page nobody opens.

TYPING_LINES: tuple[Passage, ...] = (
    _p(
        "Accuracy comes first and speed arrives on its own. Every mistake "
        "costs you three things: noticing it, deleting it, and typing it "
        "again — which is slower than having typed it carefully.",
        "on practice",
    ),
    _p(
        "The whole trick is returning to the home row. After a reach, the "
        "finger comes back, so your hands always know where they are and the "
        "next key is a known distance away instead of a fresh search.",
        "on technique",
    ),
    _p(
        "Looking down is the habit that caps your speed, because your eyes "
        "leave the text and have to find their place again when they return. "
        "It feels slower not to look, for about a week.",
        "on technique",
    ),
    _p(
        "Ten minutes a day beats an hour on Sunday. This is motor learning, "
        "and motor learning consolidates between sessions rather than during "
        "them — the rest is part of the practice.",
        "on practice",
    ),
    _p(
        "Most people are fluent across the letters and hunt for a brace, a "
        "pipe or a tilde. That is where the time actually goes, so that is "
        "what is worth drilling.",
        "on practice",
    ),
    _p(
        "Your speed will get worse when you stop looking down, and that is "
        "the usual reason people give up. You are trading a technique with a "
        "low ceiling for one with a high ceiling, and the new one starts "
        "slower.",
        "on getting better",
    ),
    _p(
        "Any consistent finger assignment beats an inconsistent one. The "
        "standard one is worth learning because it minimises how far each "
        "finger travels, and retraining costs a couple of weeks and then pays "
        "out for the rest of your life.",
        "on technique",
    ),
    _p(
        "Fast typing is not produced one key at a time. The hand learns "
        "combinations, and the combinations that stay slow are the ones you "
        "never drilled apart from the words around them.",
        "on technique",
    ),
    _p(
        "Keep your wrists off the desk. Resting them anchors your hands, so "
        "reaches become finger stretches instead of small movements of the "
        "whole hand.",
        "on technique",
    ),
    _p(
        "Practise the thing you are bad at, not the thing you enjoy. It is "
        "less pleasant and it is most of the improvement, which is why almost "
        "everyone plateaus at the level where practice stopped being "
        "uncomfortable.",
        "on getting better",
    ),
    _p(
        "Slow down until you stop making mistakes, then let the speed come "
        "back on its own. Typing fast and wrong trains typing fast and wrong.",
        "on practice",
    ),
    _p(
        "The keys do not move. Your hands can learn where they are and leave "
        "your eyes free to read what you are actually writing, which is the "
        "entire point of learning this.",
        "on technique",
    ),
    _p(
        "Measure something. A number you check occasionally tells you whether "
        "the last month of practice did anything, and without one you will "
        "assume it did.",
        "on getting better",
    ),
    _p(
        "Comfort is not the goal and neither is speed. The goal is that "
        "typing stops taking up any of your attention, so that all of it is "
        "available for the thing you are writing.",
        "on getting better",
    ),
    _p(
        "Capital A uses the right Shift and capital L uses the left. Reaching "
        "for the near Shift with the same hand contorts it and costs more "
        "than the reach saves.",
        "on technique",
    ),
    _p(
        "The bumps on F and J are there so you can find home position without "
        "looking. Put your index fingers on them, let the rest fall into "
        "place, and you are ready to start.",
        "on technique",
    ),
    _p(
        "Difficulty is the point. A drill you sail through is a drill that is "
        "measuring something you already had, and a run of small failures is "
        "what learning actually looks like from the inside.",
        "on getting better",
    ),
    _p(
        "Errors cluster. If a word keeps breaking, it is almost never the "
        "whole word — it is one transition inside it, and finding that "
        "transition is worth more than another hundred repetitions.",
        "on getting better",
    ),
    _p(
        "You will be typing for the rest of your working life. Almost nothing "
        "else you could spend two weeks learning gets used quite that often.",
        "on getting better",
    ),
    _p(
        "Rhythm matters more than bursts. A steady pace with even gaps between "
        "keystrokes is faster over a paragraph than sprinting between pauses, "
        "and it is far easier to keep accurate.",
        "on technique",
    ),
)


# ── Affirmations ────────────────────────────────────────────
# Written in the second person rather than the first: you are typing them to
# yourself, and "you" reads as encouragement where "I" reads as a script.

AFFIRMATIONS: tuple[Passage, ...] = (
    _p("You are allowed to be a work in progress and still be enough.", "steady"),
    _p("Progress over perfection, every single time.", "steady"),
    _p("The effort you put in today is not wasted, even if it is not finished.", "steady"),
    _p("You can begin again as many times as you need to.", "steady"),
    _p("Slow is smooth, and smooth is fast.", "craft"),
    _p("Do the next right thing, and then the one after that.", "craft"),
    _p("Ask for help before you need it, not after.", "community"),
    _p("Somebody is glad you are here today.", "community"),
    _p("Be the person who makes the room feel easier to be in.", "community"),
    _p("Give people the version of the truth that helps them.", "community"),
    _p("You do not have to earn rest.", "steady"),
    _p("Comparison is a poor measure of your own progress.", "steady"),
    _p("Your pace is your pace, and it is enough.", "steady"),
    _p("Kindness costs nothing and compounds like interest.", "community"),
    _p("Small consistent effort beats occasional heroics.", "craft"),
    _p("You have survived every hard day so far.", "steady"),
    _p("Learning in public is braver than pretending in private.", "craft"),
    _p("Leave things a little better than you found them.", "community"),
    _p("The work you do quietly still counts.", "craft"),
    _p("Rest is part of the practice, not a break from it.", "steady"),
)


# ── Conscious / festival / roots vocabulary ─────────────────
# Words and phrases from reggae, Rastafari and festival culture. Definitions
# are plain-language and respectful — several are ordinary English words used
# with a specific meaning in that context, which is the interesting part.

CONSCIOUS_WORDS: tuple[tuple[str, str], ...] = (
    ("irie", "feeling good, at peace, everything as it should be"),
    ("livity", "living in a way that respects life and keeps you whole"),
    ("overstanding", "understanding, said upward — you rise to it, not under it"),
    ("reasoning", "unhurried conversation to work something out together"),
    ("ital", "food and living kept natural and unprocessed"),
    ("roots", "staying connected to where you and your people come from"),
    ("zion", "the place of peace you are heading toward"),
    ("groundation", "a gathering to reason, drum and stay rooted"),
    ("upliftment", "raising people rather than competing with them"),
    ("vibration", "the feeling a person or place gives off"),
    ("gratitude", "noticing what you already have"),
    ("presence", "being fully in the moment you are actually in"),
    ("stillness", "quiet enough to hear yourself think"),
    ("intention", "deciding why before you decide what"),
    ("awareness", "noticing your own state as it happens"),
    ("communal", "shared, belonging to everyone present"),
    ("abundance", "trusting there is enough to go round"),
    ("resonance", "when something lands because it is already true for you"),
    ("meditation", "sitting with your attention on purpose"),
    ("harmony", "different parts sounding good together"),
    ("solidarity", "standing with people because it is right"),
    ("reverence", "treating something as worth your respect"),
    ("kinship", "closeness that is chosen, not inherited"),
    ("stewardship", "looking after what you did not make"),
    ("balance", "holding several true things at once"),
    ("humility", "knowing the size of what you do not know"),
    ("generosity", "giving without keeping score"),
    ("belonging", "being somewhere you do not have to explain yourself"),
)

CONSCIOUS_LINES: tuple[Passage, ...] = (
    _p("One love, one heart, let's get together and feel all right.", "roots"),
    _p("Every little thing is gonna be all right.", "roots"),
    _p("Emancipate yourselves from mental slavery.", "roots"),
    _p("None but ourselves can free our minds.", "roots"),
    _p("The stone that the builder refuse will always be the head cornerstone.", "roots"),
    _p("Open your eyes, look within: are you satisfied with the life you're living?", "roots"),
    _p("Live for yourself and you will live in vain; live for others and you will live again.", "roots"),
    _p("In this bright future you can't forget your past.", "roots"),
    _p("Sun is shining, the weather is sweet.", "roots"),
    _p("Wake up and live.", "roots"),
)
