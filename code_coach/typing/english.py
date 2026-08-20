"""Ordinary English, for the modes that measure everyday typing speed.

The vocabulary and passage sections are chosen to be worth reading. This one
isn't — it's the plain, high-frequency material a speed test needs, because a
number only means something if it was measured on the words you actually type.

The pairs and triples matter more than they look. Fast typing isn't produced
one key at a time; the hand learns combinations, and the combinations that
stay slow are the ones you never drilled apart from the words around them.
"""

from __future__ import annotations

# The words that make up most of written English, roughly by frequency. A
# minute spent on these is a minute spent on what you'll actually type.
COMMON_WORDS: tuple[str, ...] = (
    "the", "of", "and", "a", "to", "in", "is", "you", "that", "it",
    "he", "was", "for", "on", "are", "as", "with", "his", "they", "I",
    "at", "be", "this", "have", "from", "or", "one", "had", "by", "word",
    "but", "not", "what", "all", "were", "we", "when", "your", "can", "said",
    "there", "use", "an", "each", "which", "she", "do", "how", "their", "if",
    "will", "up", "other", "about", "out", "many", "then", "them", "these",
    "so", "some", "her", "would", "make", "like", "him", "into", "time",
    "has", "look", "two", "more", "write", "go", "see", "number", "no",
    "way", "could", "people", "my", "than", "first", "water", "been", "call",
    "who", "oil", "its", "now", "find", "long", "down", "day", "did", "get",
    "come", "made", "may", "part", "over", "new", "sound", "take", "only",
    "little", "work", "know", "place", "year", "live", "me", "back", "give",
    "most", "very", "after", "thing", "our", "just", "name", "good",
    "sentence", "man", "think", "say", "great", "where", "help", "through",
    "much", "before", "line", "right", "too", "mean", "old", "any", "same",
    "tell", "boy", "follow", "came", "want", "show", "also", "around",
    "form", "three", "small", "set", "put", "end", "does", "another", "well",
    "large", "must", "big", "even", "such", "because", "turn", "here", "why",
    "ask", "went", "men", "read", "need", "land", "different", "home", "us",
    "move", "try", "kind", "hand", "picture", "again", "change", "off",
    "play", "spell", "air", "away", "animal", "house", "point", "page",
    "letter", "mother", "answer", "found", "study", "still", "learn",
    "should", "world", "high", "every", "near", "add", "food", "between",
    "own", "below", "country", "plant", "last", "school", "father", "keep",
    "tree", "never", "start", "city", "earth", "eye", "light", "thought",
    "head", "under", "story", "saw", "left", "few", "while", "along",
    "might", "close", "something", "seem", "next", "hard", "open", "example",
)

# The two-letter combinations English is mostly made of, most common first.
BIGRAMS: tuple[str, ...] = (
    "th", "he", "in", "er", "an", "re", "on", "at", "en", "nd",
    "ti", "es", "or", "te", "of", "ed", "is", "it", "al", "ar",
    "st", "to", "nt", "ng", "se", "ha", "as", "ou", "io", "le",
    "ve", "co", "me", "de", "hi", "ri", "ro", "ic", "ne", "ea",
    "ra", "ce", "li", "ch", "ll", "be", "ma", "si", "om", "ur",
)

# Three-letter runs. These are where a hand either flows or stumbles.
TRIGRAMS: tuple[str, ...] = (
    "the", "and", "ing", "her", "hat", "his", "tha", "ere", "for", "ent",
    "ion", "ter", "was", "you", "ith", "ver", "all", "wit", "thi", "tio",
    "nde", "has", "nce", "edt", "tis", "oft", "sth", "men", "ain", "est",
)

# The symbol pairs that carry the same weight in code that bigrams do in
# prose — reached for constantly, drilled almost never.
CODE_PAIRS: tuple[str, ...] = (
    "=>", "->", "!=", "==", "<=", ">=", "&&", "||", "??", "::",
    ":=", "+=", "-=", "*=", "/=", "**", "//", "/*", "*/", "()",
    "{}", "[]", "();", "{};", "[];", "<>", "</", "/>", "&&!", "||!",
)

ALL_WORDS = COMMON_WORDS


def words_typeable_from(chars: tuple[str, ...]) -> tuple[str, ...]:
    """Common words that need no key outside the given set."""
    allowed = set(chars)
    return tuple(w for w in COMMON_WORDS if set(w.lower()) <= allowed)
