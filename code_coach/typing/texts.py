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
    _p(
        "Read ahead of your fingers. Good typists are looking at the next few "
        "words while typing the current one, which is why they rarely stall "
        "at the end of a line.",
        "on technique",
    ),
    _p(
        "The space bar is the most frequently pressed key by a wide margin, "
        "and it is the one nobody practises. Use one thumb consistently rather "
        "than whichever is closer.",
        "on technique",
    ),
    _p(
        "Backspace is a key too. If you reach for it with the wrong finger, or "
        "look down to find it, every mistake costs more than the mistake "
        "itself did.",
        "on technique",
    ),
    _p(
        "Typing is not one skill. Prose, code and numbers each have their own "
        "rhythm, and being quick at one says surprisingly little about the "
        "other two.",
        "on getting better",
    ),
    _p(
        "The number row is worse than it looks. It is the longest reach on the "
        "board and the one people most often glance down for, which is why "
        "numeric work is where accuracy quietly collapses.",
        "on technique",
    ),
    _p(
        "Warm up before you measure. The first minute of any session is slower "
        "than the rest, and treating it as your score will tell you that you "
        "are getting worse when you are not.",
        "on practice",
    ),
    _p(
        "Speed tests reward common words. Real writing has names, jargon and "
        "punctuation in it, so the number you get on a test is usually higher "
        "than the speed you actually work at.",
        "on getting better",
    ),
    _p(
        "Shift is held, not tapped. Press it with the opposite hand, hold it "
        "through the letter and release afterwards; tapping it separately is a "
        "habit that costs a whole extra beat on every capital.",
        "on technique",
    ),
    _p(
        "Look at the screen, not the keyboard, and not your hands. The point "
        "is not discipline — it is that reading what you produced is how you "
        "notice a mistake in the second it happens.",
        "on technique",
    ),
    _p(
        "A plateau usually means you stopped making mistakes. If a drill feels "
        "comfortable, it is measuring what you already had; push the pace "
        "until accuracy just starts to slip, and practise there.",
        "on getting better",
    ),
    _p(
        "Punctuation is where most programmers lose time, not letters. The "
        "brace, the pipe, the underscore and the angle bracket are reached for "
        "constantly and drilled almost never.",
        "on practice",
    ),
    _p(
        "Your keyboard matters less than you think and your posture matters "
        "more. A better switch will not fix a wrist resting on the desk or "
        "elbows held at the wrong height.",
        "on technique",
    ),
    _p(
        "Learn the shortcuts for moving, not just for typing. Jumping a word "
        "at a time, or to the start of a line, saves more time over a day than "
        "raising your speed by ten words a minute.",
        "on getting better",
    ),
    _p(
        "Accuracy below about ninety-five per cent is not a speed problem. "
        "Below that, corrections dominate everything, and typing faster makes "
        "the total time worse rather than better.",
        "on practice",
    ),
    _p(
        "Same-finger sequences are the slowest thing you type. Any pair that "
        "asks one finger to move twice in a row costs roughly double, which is "
        "why layouts are judged mostly on how often that happens.",
        "on technique",
    ),
    _p(
        "Alternating hands is fast because the next finger is already "
        "travelling while the current one presses. Rolls within one hand are "
        "the next best thing, and both beat any sequence that stalls.",
        "on technique",
    ),
    _p(
        "Practise the transition, not the word. When a word keeps breaking it "
        "is almost never the whole word — it is one pair of letters inside it, "
        "and drilling that pair fixes every word containing it.",
        "on getting better",
    ),
    _p(
        "Nobody types at their test speed all day. Sustained working pace is "
        "usually about half of a best score, because real writing includes "
        "thinking, and thinking includes stopping.",
        "on getting better",
    ),
    _p(
        "The keys you hit hardest are usually the ones you are least sure of. "
        "Pressure is a tell: where you are confident, you barely touch the "
        "key at all.",
        "on technique",
    ),
    _p(
        "Two weeks is the usual figure for retraining a habit at the keyboard, "
        "and the first of those two weeks is genuinely unpleasant. Knowing the "
        "shape of it in advance is most of what gets people through.",
        "on getting better",
    ),
    _p(
        "Copy typing and composing are different activities. You can read "
        "ahead when copying; when writing your own words, the bottleneck is "
        "upstream of your hands entirely.",
        "on getting better",
    ),
    _p(
        "Stop between lines, not mid-word. Pausing to think in the middle of a "
        "word breaks the motion your hand had already planned, and picking it "
        "up again costs more than the pause saved.",
        "on technique",
    ),
    _p(
        "Most keyboards ignore the third key you press at once, in certain "
        "combinations. It rarely matters when typing prose and matters a great "
        "deal in games, which is why gaming keyboards advertise it.",
        "on keyboards",
    ),
    _p(
        "Key travel is how far a key moves before it registers. Laptop "
        "keyboards use very little, mechanical ones a lot, and which you "
        "prefer is mostly which you learned on.",
        "on keyboards",
    ),
)


# ── Things worth reading while you type ─────────────────────
#
# The other half of the default material. Passages about typing run out fast —
# there are only so many true things to say about it — and a drill that keeps
# handing you the same sentence stops being practice and becomes recitation.
# These are short pieces about how things work: enough of them that a session
# rarely repeats one, and each worth the twenty seconds it takes to type.

_PROSE_ONE: tuple[Passage, ...] = (
    _p(
        "A honeybee dances to say where the flowers are. The angle of the "
        "dance gives the direction relative to the sun, and its length gives "
        "the distance — a map, performed in the dark, to an audience that "
        "reads it by touch.",
        "bees",
    ),
    _p(
        "The deepest part of the ocean is further down than Everest is up. "
        "Sunlight gives out after about a thousand feet, so almost all of that "
        "space has never been lit by anything but the animals living in it.",
        "the sea",
    ),
    _p(
        "Bridges are built to move. A span that could not flex would tear "
        "itself apart in the first cold snap, so engineers leave gaps and let "
        "the whole thing breathe with the weather.",
        "engineering",
    ),
    _p(
        "Sourdough is a bargain between two organisms: yeast makes the bread "
        "rise and bacteria make it sour, and each produces conditions the "
        "other prefers. Left alone in flour and water, they find each other.",
        "bread",
    ),
    _p(
        "The Great Wall is not one wall. It is centuries of separate walls, "
        "built by different dynasties for different reasons, joined up later "
        "by mapmakers and by the way we like our stories.",
        "history",
    ),
    _p(
        "A photograph is a measurement of light over time. Everything a camera "
        "does — aperture, shutter, film speed — is three ways of arguing about "
        "how much of it to let in.",
        "photography",
    ),
    _p(
        "Trees talk through fungus. Threads finer than root hairs link one "
        "tree to another underground, and sugar moves along them from trees "
        "with plenty to trees in shade.",
        "forests",
    ),
    _p(
        "The metre began as one ten-millionth of the distance from the equator "
        "to the North Pole. We have since defined it by the speed of light, "
        "which is more precise and much less romantic.",
        "measurement",
    ),
    _p(
        "Volcanic soil is the most fertile there is, which is why people keep "
        "farming the slopes of volcanoes. The thing that will eventually "
        "destroy the farm is the reason the farm is there.",
        "geology",
    ),
    _p(
        "Every language has a word order it treats as normal and every one "
        "breaks it for emphasis. What counts as poetic in one is merely "
        "grammatical in another.",
        "language",
    ),
    _p(
        "Concrete keeps getting stronger for decades after it is poured. Roman "
        "harbour concrete is stronger now than the day it set, because "
        "seawater has been quietly growing crystals in it for two thousand "
        "years.",
        "materials",
    ),
    _p(
        "Birds navigate partly by magnetism, and the current guess is that "
        "they see it. A protein in the eye responds to the field, which would "
        "mean north is something a robin looks at rather than senses.",
        "birds",
    ),
    _p(
        "A violin is mostly air. The wood shapes and drives the cavity inside, "
        "and it is the shape of that space, more than the wood, that makes one "
        "instrument sound like itself.",
        "music",
    ),
    _p(
        "Salt was once valuable enough to pay soldiers with, which is where "
        "the word salary comes from. It preserved food, and preserved food "
        "meant surviving winter.",
        "history",
    ),
    _p(
        "Glass is a liquid that has forgotten how to flow. The old story about "
        "cathedral windows being thicker at the bottom is wrong, though — that "
        "is just how the glass was made.",
        "materials",
    ),
    _p(
        "Octopus arms are largely independent. Most of the neurons are in the "
        "arms rather than the head, so an arm can solve a small problem while "
        "the animal attends to something else.",
        "the sea",
    ),
    _p(
        "Compound interest is the same mathematics as an epidemic and as a "
        "nuclear chain reaction: a quantity that grows in proportion to itself "
        "does nothing for a long time and then does everything at once.",
        "mathematics",
    ),
    _p(
        "A map has to lie. The Earth is curved and paper is not, so every "
        "projection distorts area or angle or distance, and the mapmaker's "
        "only real choice is which lie is least trouble.",
        "maps",
    ),
    _p(
        "Coffee is a fruit seed, roasted. The plant makes caffeine to poison "
        "insects, and we drink it on purpose — one of many cases where a "
        "plant's chemical warfare turned out to be a selling point.",
        "plants",
    ),
    _p(
        "The first computer bug was a moth. It was found in a relay of the "
        "Harvard Mark II in 1947, taped into the logbook, and the entry reads "
        "\"first actual case of bug being found\".",
        "computing",
    ),
    _p(
        "Wind turbines turn slowly on purpose. The tips are already moving at "
        "well over a hundred miles an hour, and past that the blades start "
        "losing more to drag than they gain from speed.",
        "engineering",
    ),
    _p(
        "The colour of a flame tells you what is burning. Sodium gives orange, "
        "copper gives green, potassium a pale violet — the same trick "
        "astronomers use to read the composition of a star.",
        "chemistry",
    ),
    _p(
        "Paper folds in half about seven times before it stops. Each fold "
        "doubles the thickness and halves the width, so the shape runs out of "
        "room long before the material runs out of strength.",
        "mathematics",
    ),
    _p(
        "Antarctica is a desert. It holds most of the world's fresh water and "
        "almost none of it falls as new snow, which is the definition — a "
        "desert is about rainfall, not heat.",
        "geography",
    ),
    _p(
        "Sharpening does not add anything. It removes metal until two surfaces "
        "meet at a line, and a dull edge is simply one where that line has "
        "become a small flat surface.",
        "craft",
    ),
    _p(
        "The word robot comes from a 1920 play, from a Czech word for forced "
        "labour. The robots in it rebel — the idea arrived in the language "
        "already worried about itself.",
        "language",
    ),
    _p(
        "A cast-iron pan is seasoned with polymerised oil, not grease. Heat "
        "turns a thin film of oil into a hard plastic layer bonded to the "
        "metal, which is why washing it with soap does no harm.",
        "cooking",
    ),
    _p(
        "Lightning heats the air around it to several times the surface "
        "temperature of the sun. Thunder is that air exploding outward and "
        "then collapsing back into the space it left.",
        "weather",
    ),
    _p(
        "Sailing upwind works the way a wing does. The sail is a vertical "
        "aerofoil, and the boat goes forward because the keel refuses to let "
        "it go sideways.",
        "sailing",
    ),
    _p(
        "The QWERTY layout was not designed to slow you down. It separated "
        "common letter pairs so the typebars of a mechanical typewriter would "
        "not collide, which is a different problem with a similar answer.",
        "typing",
    ),
    _p(
        "Bamboo can grow a metre in a day. It is a grass, and it spends years "
        "building a root system before any of that happens, which is the part "
        "nobody photographs.",
        "plants",
    ),
    _p(
        "Rivers meander because they must. Any slight bend makes the outer "
        "bank faster and the inner bank slower, so the bend deepens itself "
        "until the river doubles back and cuts it off.",
        "rivers",
    ),
    _p(
        "A day on Venus is longer than its year. It turns so slowly, and "
        "backwards, that the sun rises in the west roughly twice per orbit.",
        "space",
    ),
    _p(
        "Most of the mass of an atom is in a nucleus that occupies almost none "
        "of its volume. Solid matter is mostly the electrical objection of "
        "electrons to being in the same place.",
        "physics",
    ),
    _p(
        "The oldest known musical instrument is a flute carved from bone, "
        "about forty thousand years old. Whoever made it had already worked "
        "out where to put the holes.",
        "music",
    ),
    _p(
        "Spider silk is stronger than steel by weight and far tougher, because "
        "toughness is about how much energy something absorbs before breaking, "
        "not how much force it resists.",
        "materials",
    ),
    _p(
        "Nautical charts still mark depths in fathoms in places, a fathom "
        "being the span of a man's outstretched arms. Plenty of measurement "
        "started as a body and stayed after the body was replaced.",
        "measurement",
    ),
    _p(
        "Sleep is when the brain washes itself. Channels between cells widen "
        "at night and fluid flushes through, clearing waste that accumulates "
        "during the day.",
        "the body",
    ),
    _p(
        "The Rosetta Stone was useful because it was boring. It is a routine "
        "decree, repeated in three scripts, and the repetition was worth more "
        "than anything the text actually said.",
        "history",
    ),
    _p(
        "Aeroplane windows are round because square ones failed. Stress "
        "concentrates at a corner, and early jets tore open along the corners "
        "of their windows.",
        "engineering",
    ),
    _p(
        "Honey does not spoil. It is too acidic and too dry for bacteria, and "
        "jars of it found in ancient tombs were still edible thousands of "
        "years later.",
        "food",
    ),
    _p(
        "The eye has a blind spot where the optic nerve leaves the retina. You "
        "never notice it because the brain fills the gap with whatever is "
        "around it, confidently and without asking.",
        "the body",
    ),
    _p(
        "Chess has more possible games than there are atoms in the observable "
        "universe, which is why no computer plays it by looking at all of "
        "them. They look at a few and guess well about the rest.",
        "games",
    ),
    _p(
        "Tuning a piano perfectly is impossible. The mathematics of pure "
        "intervals does not close into an octave, so every piano is a "
        "compromise spread thinly across all twelve keys.",
        "music",
    ),
    _p(
        "Icebergs are fresh water. Sea ice pushes salt out as it freezes, so "
        "even ice formed from the ocean melts into something you could drink.",
        "the sea",
    ),
    _p(
        "Roman roads were built in layers, with the top cambered so water ran "
        "off the sides. Most road failure is water, and it was water they were "
        "really building against.",
        "engineering",
    ),
    _p(
        "Cats cannot taste sweetness. The gene for the sweet receptor is "
        "broken in every cat we have looked at, which fits an animal that has "
        "eaten nothing but meat for a very long time.",
        "animals",
    ),
    _p(
        "The printing press did not simply spread ideas, it standardised them. "
        "Once a text could be copied identically, disagreements about what it "
        "said became disagreements about what it meant.",
        "history",
    ),
    _p(
        "Bicycles stay upright mostly by steering. Lean left and the front "
        "wheel turns left, which brings the wheels back under the falling "
        "rider — the bike catches you before you know you fell.",
        "physics",
    ),
    _p(
        "A rainbow is a circle. You only see an arc because the ground is in "
        "the way, and from an aeroplane at the right moment you can see the "
        "whole ring.",
        "weather",
    ),
    _p(
        "Ravens can hold a grudge. They recognise individual human faces and "
        "treat people differently for years afterwards, and other ravens "
        "appear to take their word for it.",
        "birds",
    ),
    _p(
        "Steel is iron with a little carbon in it. That small amount changes "
        "everything, and most of metallurgy is arguing about how much and "
        "what else to add.",
        "materials",
    ),
    _p(
        "The library at Alexandria was not destroyed in a single fire. It "
        "declined over centuries through funding cuts and neglect, which is "
        "how most libraries are actually lost.",
        "history",
    ),
    _p(
        "A calorie is the energy needed to warm a gram of water by one degree. "
        "The one on food labels is a thousand of those, which is why the "
        "number looks so large.",
        "measurement",
    ),
    _p(
        "Migrating birds sleep on the wing, one half of the brain at a time. "
        "The open eye is on the side of the wakeful half, watching where the "
        "flock is going.",
        "birds",
    ),
    _p(
        "Zero arrived late. Counting works without it, and it only becomes "
        "necessary once you write numbers by position and need a way to say "
        "that a column is empty.",
        "mathematics",
    ),
    _p(
        "Sand from different beaches looks entirely different under a lens: "
        "ground shell, volcanic glass, worn quartz, the skeletons of small "
        "animals. It is a summary of everything upstream.",
        "geology",
    ),
    _p(
        "Fire needs three things and you only have to remove one. Fuel, heat "
        "and oxygen — every method of putting a fire out is an argument about "
        "which is easiest to take away.",
        "safety",
    ),
    _p(
        "Wood is strong along the grain and weak across it, which is why a "
        "joiner thinks about direction before thickness. Working with the "
        "grain is not a metaphor first.",
        "craft",
    ),
    _p(
        "The moon is moving away from us at about the rate fingernails grow. "
        "Eventually total solar eclipses will stop happening, and we are alive "
        "during the window when they fit exactly.",
        "space",
    ),
    _p(
        "Bread staling is not drying out. The starch reorganises into a firmer "
        "structure, which is why warming a stale loaf briefly makes it soft "
        "again.",
        "cooking",
    ),
)

_PROSE_TWO: tuple[Passage, ...] = (
    _p(
        "Giraffes have the same number of neck bones as you do. Seven, each "
        "one enormous — the count is fixed across almost every mammal, from "
        "the whale to the mouse.",
        "animals",
    ),
    _p(
        "The shipping container did more for global trade than any treaty. "
        "Standardising the box meant a crane could move cargo without anyone "
        "opening it, and the cost of sending things fell through the floor.",
        "trade",
    ),
    _p(
        "Ice floats, which is unusual. Most substances are denser as solids, "
        "and if water behaved normally, lakes would freeze from the bottom up "
        "and very little would survive a winter.",
        "chemistry",
    ),
    _p(
        "The word muscle comes from the Latin for little mouse, because "
        "someone thought a flexing bicep looked like one moving under the "
        "skin. Anatomy is full of people describing what things reminded them "
        "of.",
        "language",
    ),
    _p(
        "A grand piano's strings pull with a total force of about twenty "
        "tonnes. The iron frame exists entirely to argue with them, and the "
        "wooden case would fold in an instant without it.",
        "music",
    ),
    _p(
        "Nothing in the sky moves as slowly as it looks. A cloud drifting "
        "lazily overhead is usually doing thirty miles an hour; it just "
        "happens to be a mile away and the size of a village.",
        "weather",
    ),
    _p(
        "The pencil is a composite material. Graphite alone is too soft to "
        "hold a point, so it is mixed with clay — more clay makes a harder "
        "pencil, and the number on the side is that ratio.",
        "everyday things",
    ),
    _p(
        "Bacteria outnumber your own cells, though not by as much as the "
        "popular figure suggests. The honest estimate is roughly one to one, "
        "which is still a strange thing to be.",
        "the body",
    ),
    _p(
        "Rubber was a curiosity until someone worked out vulcanisation. Raw "
        "latex goes sticky in heat and brittle in cold; adding sulphur and "
        "cooking it produces something that behaves in both.",
        "materials",
    ),
    _p(
        "The Sahara was green within human memory. Cave paintings there show "
        "swimmers, and the desert has cycled between grassland and sand "
        "roughly every twenty thousand years.",
        "climate",
    ),
    _p(
        "Sound travels about four times faster in water than in air, which is "
        "why whales can call across an ocean basin and why it is so hard to "
        "tell where an underwater noise came from.",
        "the sea",
    ),
    _p(
        "A tuning fork is deliberately useless at everything except one note. "
        "Its shape suppresses the overtones that make other objects ring "
        "complicatedly, leaving something almost purely one frequency.",
        "music",
    ),
    _p(
        "Aluminium was once more precious than gold. It is the most abundant "
        "metal in the crust but bonds so tightly to oxygen that nobody could "
        "get it out until electricity arrived.",
        "materials",
    ),
    _p(
        "You cannot tickle yourself, because the part of the brain that plans "
        "the movement warns the part that feels it. The surprise is the whole "
        "sensation.",
        "the body",
    ),
    _p(
        "The Pacific is big enough to hold every continent with room left "
        "over. On a globe it is the hemisphere that is almost entirely water, "
        "and no flat map has ever made that look right.",
        "geography",
    ),
    _p(
        "Fireflies flash in code. Each species has its own rhythm, and in some "
        "the females mimic another species' pattern to lure in males and eat "
        "them.",
        "animals",
    ),
    _p(
        "Standardised time was invented by railways. Before them every town "
        "kept its own noon, and it stopped being charming the moment a "
        "timetable had to be right in two places at once.",
        "history",
    ),
    _p(
        "Diamonds are not rare, particularly. They are well marketed and "
        "tightly supplied, and the idea that an engagement ring should cost "
        "two months' salary came from an advertising campaign.",
        "economics",
    ),
    _p(
        "Cats land on their feet by conservation of angular momentum, not by "
        "pushing off anything. They twist the front half one way and the back "
        "half the other, then swap.",
        "physics",
    ),
    _p(
        "The chilli's heat is a defence against mammals, which chew seeds and "
        "destroy them. Birds swallow them whole and cannot taste capsaicin at "
        "all, which is exactly the arrangement the plant wants.",
        "plants",
    ),
    _p(
        "A ship's hull speed is set by the wave it makes. Past a certain "
        "point the boat is climbing its own bow wave, and more power mostly "
        "buys a bigger wave.",
        "sailing",
    ),
    _p(
        "Penicillin was found because a plate was left out. What made it "
        "matter was noticing that the mould had cleared a ring around itself "
        "rather than simply throwing the plate away.",
        "medicine",
    ),
    _p(
        "There are more possible shuffles of a deck of cards than seconds "
        "since the universe began. Any well-shuffled deck has almost certainly "
        "never existed in that order before.",
        "mathematics",
    ),
    _p(
        "The reason old films flicker is that they were shot at sixteen frames "
        "a second and are usually played at twenty-four. Everyone in them was "
        "moving at a perfectly ordinary speed.",
        "film",
    ),
    _p(
        "Owls fly silently because of the edges of their feathers. A comb-like "
        "fringe on the leading edge breaks up the air that would otherwise "
        "make the rush of a wingbeat.",
        "birds",
    ),
    _p(
        "Mount Everest is not the furthest point from the centre of the Earth. "
        "The planet bulges at the equator, so a peak in Ecuador wins on that "
        "measure by over two kilometres.",
        "geography",
    ),
    _p(
        "Bubble wrap was invented as wallpaper. It failed, was sold as "
        "greenhouse insulation, failed again, and only found its purpose when "
        "a computer company needed to ship something fragile.",
        "invention",
    ),
    _p(
        "Your stomach lining replaces itself every few days. It has to: the "
        "acid inside is strong enough to dissolve the tissue holding it, and "
        "the only defence is building faster than it destroys.",
        "the body",
    ),
    _p(
        "The dot over a lowercase i is called a tittle. It exists because "
        "medieval scribes kept losing the letter among the strokes of m and "
        "n, and added a mark to keep it visible.",
        "language",
    ),
    _p(
        "A pearl is a defence. The oyster coats an irritant in the same "
        "material it lines its shell with, layer after layer, and the shine "
        "is light bouncing between those layers.",
        "the sea",
    ),
    _p(
        "Windmills were the first factories. Before steam, anywhere with "
        "reliable wind could grind grain, saw wood or pump water without a "
        "single animal or person doing the turning.",
        "engineering",
    ),
    _p(
        "Snow is not white. Ice is clear, and a snowbank looks white for the "
        "same reason crushed glass does — countless surfaces scattering every "
        "colour equally.",
        "weather",
    ),
    _p(
        "Ants find the shortest route by accident. Each one lays a trail and "
        "prefers strong trails, and the shortest path gets walked more often "
        "per unit time, so its scent builds fastest.",
        "animals",
    ),
    _p(
        "The keyboard shortcut for undo is next to the ones for cut, copy and "
        "paste because they were chosen together, on an early Apple keyboard, "
        "to sit under the left hand while the right held the mouse.",
        "computing",
    ),
    _p(
        "Sugar was a luxury spice before it was a staple. It appears in "
        "medieval recipes in the quantities we now use saffron, and the "
        "collapse in price rewrote European cooking entirely.",
        "food",
    ),
    _p(
        "A rainbow has no fixed position. It is an angle, not an object, so "
        "everyone standing near you sees a different one made of different "
        "raindrops.",
        "weather",
    ),
    _p(
        "Solder does not glue metal together. It melts and flows into the "
        "surface of both parts, forming a thin alloy at each boundary, which "
        "is why a clean surface matters more than a hot iron.",
        "craft",
    ),
    _p(
        "Bananas are clones. Almost every one sold is genetically identical, "
        "which makes the whole crop equally vulnerable to anything that learns "
        "to attack it — and one disease already wiped out the previous "
        "variety.",
        "plants",
    ),
    _p(
        "Latitude was easy and longitude was murder. You can read latitude "
        "off the noon sun in an afternoon; longitude needed a clock that would "
        "keep time on a rolling ship, and that took decades.",
        "navigation",
    ),
    _p(
        "Hummingbirds cannot walk. Their feet are for perching only, and "
        "everything else in the body has been given over to a shoulder joint "
        "that lets the wing swivel and generate lift in both directions.",
        "birds",
    ),
    _p(
        "A microwave heats unevenly because it makes standing waves. There are "
        "fixed hot and cold spots inside the box, which is the entire reason "
        "for the turntable.",
        "everyday things",
    ),
    _p(
        "The Dead Sea is not dead so much as extremely salty. Nothing much "
        "lives in it, you float without effort, and it is dropping by about a "
        "metre a year as the rivers feeding it are diverted.",
        "geography",
    ),
    _p(
        "Cement production accounts for a startling share of global carbon "
        "emissions, most of it from the chemistry rather than the heat: making "
        "lime from limestone releases carbon dioxide whatever you burn.",
        "climate",
    ),
    _p(
        "Frogs drink through their skin. They also breathe through it, which "
        "is why a frog is such a good early warning about what is in the "
        "water.",
        "animals",
    ),
    _p(
        "Every colour on a screen is three. Red, green and blue dots too small "
        "to separate, and a yellow pixel is simply red and green at once with "
        "nothing yellow anywhere in the device.",
        "computing",
    ),
    _p(
        "The oldest living things are trees that grow almost imperceptibly. A "
        "bristlecone pine adds a fraction of a millimetre a year, and the wood "
        "is so dense and resinous that almost nothing can rot it.",
        "plants",
    ),
    _p(
        "A key is a code you can hold. The bumps set each pin to exactly the "
        "height where the cylinder can turn, and picking a lock is finding "
        "those heights one at a time by feel.",
        "everyday things",
    ),
    _p(
        "Sea level is not level. Gravity varies with what is under the crust, "
        "so the ocean stands tens of metres higher over some places than "
        "others, and the shape of that surface is what we mean by sea level.",
        "geography",
    ),
    _p(
        "Whales evolved from land mammals that went back to the water. Their "
        "closest living relative is the hippopotamus, and a whale's flipper "
        "still contains the bones of a hand.",
        "animals",
    ),
    _p(
        "Fahrenheit set zero at the coldest temperature he could reliably "
        "reproduce, using a mixture of ice and salt. Celsius picked water "
        "instead, which is why one scale looks arbitrary and the other does "
        "not.",
        "measurement",
    ),
    _p(
        "Bread, beer and yoghurt are all the same idea: let a microbe you like "
        "eat the food first, so that nothing you dislike gets the chance. "
        "Preservation came before flavour, and flavour came along anyway.",
        "food",
    ),
    _p(
        "The width of a railway is a decision nobody ever finished making. "
        "Different countries chose differently, and where two gauges meet "
        "everything has to be unloaded and loaded again.",
        "trade",
    ),
    _p(
        "Static electricity is not really static. Rubbing two materials moves "
        "electrons from one to the other, and the shock is them all going back "
        "at once through whatever you touched next.",
        "physics",
    ),
    _p(
        "Coral reefs are built by animals and fed by algae living inside them. "
        "Bleaching is the coral expelling those algae under stress, which is "
        "why a bleached reef is starving rather than dead.",
        "the sea",
    ),
    _p(
        "Hand-washing was rejected before it was accepted. The doctor who "
        "showed it saved lives could not explain why it worked, and germ "
        "theory arrived too late for anyone to take his word for it.",
        "medicine",
    ),
    _p(
        "A compass points to magnetic north, which wanders. It has moved "
        "hundreds of miles in the last century, and every serious chart has to "
        "note the difference and the year it was measured.",
        "navigation",
    ),
    _p(
        "Popcorn works because the kernel is a pressure vessel. Moisture "
        "inside turns to steam, the hull holds until it cannot, and the starch "
        "expands into foam in the instant it lets go.",
        "cooking",
    ),
    _p(
        "Most of a tree is made from air. The carbon in the wood came out of "
        "the atmosphere, not the soil, which is a genuinely odd thing to think "
        "about while standing under one.",
        "plants",
    ),
    _p(
        "Fingerprints may not be for grip. The current thinking is that they "
        "improve touch, by amplifying the vibrations that let you feel fine "
        "texture with your fingertips.",
        "the body",
    ),
    _p(
        "The reason a phone screen ignores a gloved hand is that it is "
        "measuring capacitance, not pressure. It is not feeling you push; it "
        "is noticing that something conductive came close.",
        "computing",
    ),
    _p(
        "Mountains have roots. A range floats on the mantle like an iceberg, "
        "and the taller it stands the deeper the crust reaches beneath it to "
        "hold it up.",
        "geology",
    ),
    _p(
        "The mantis shrimp punches fast enough to boil water. The claw moves "
        "so quickly that the water behind it cavitates, and the collapsing "
        "bubble delivers a second blow after the first.",
        "the sea",
    ),
    _p(
        "Dough is kneaded to organise it. The proteins in flour link into "
        "sheets that trap gas, and the difference between bread and a biscuit "
        "is largely how much you encouraged that.",
        "cooking",
    ),
    _p(
        "Airline seats face forward even though rear-facing is safer. Nobody "
        "much likes flying backwards, and that preference has outweighed the "
        "engineering for the whole history of the industry.",
        "engineering",
    ),
    _p(
        "There is no such thing as cold, only less heat. Cold does not come "
        "into a house; heat leaves it, and every insulating material is an "
        "attempt to slow that departure.",
        "physics",
    ),
    _p(
        "Wolves were domesticated by scavenging, most likely. The animals bold "
        "enough to approach a camp and calm enough to stay ate better, and "
        "that is a selection pressure whether or not anyone intended it.",
        "animals",
    ),
    _p(
        "A magnifying glass makes fire by turning a wide beam of sunlight into "
        "a narrow one. It adds nothing; it only insists that everything "
        "arriving over a hand's width leaves through a pinpoint.",
        "physics",
    ),
    _p(
        "Silk was a state secret for centuries. Exporting a silkworm carried a "
        "death sentence, and the technique escaped anyway — as techniques "
        "generally do, eventually.",
        "history",
    ),
    _p(
        "Your sense of balance lives in your ears. Three fluid-filled loops at "
        "right angles to one another report rotation in every direction, which "
        "is why an ear infection can make the floor tilt.",
        "the body",
    ),
    _p(
        "Rust is iron returning to the state it was mined in. Ore is iron "
        "already combined with oxygen, and smelting is the act of separating "
        "them; corrosion is simply that work coming undone.",
        "materials",
    ),
    _p(
        "Nobody has ever seen the far side of the moon from Earth. It turns "
        "exactly once per orbit, so the same face is always toward us, and the "
        "other one was a mystery until 1959.",
        "space",
    ),
)

PROSE: tuple[Passage, ...] = _PROSE_ONE + _PROSE_TWO


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
