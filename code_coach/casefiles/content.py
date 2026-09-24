"""The case files. Easiest first.

Every name, street and event here is made up for this project.
"""

from __future__ import annotations

from code_coach.casefiles import Case, Step

LIBRARY_SETUP = """
CREATE TEMP TABLE people (
    id    integer PRIMARY KEY,
    name  text NOT NULL
);
INSERT INTO people VALUES
    (1, 'Ada Moss'), (2, 'Ben Ortiz'), (3, 'Cleo Park'),
    (4, 'Dan Webb'), (5, 'Eve Lund');

CREATE TEMP TABLE cards (
    id         integer PRIMARY KEY,
    number     text NOT NULL,
    person_id  integer NOT NULL
);
INSERT INTO cards VALUES
    (1, 'LC-1044', 3), (2, 'LC-2291', 1), (3, 'LC-3310', 5),
    (4, 'LC-4127', 2), (5, 'LC-5068', 4);

CREATE TEMP TABLE books (
    id      integer PRIMARY KEY,
    title   text NOT NULL,
    author  text NOT NULL
);
INSERT INTO books VALUES
    (1, 'The Salt Road', 'M. Okoro'),
    (2, 'Night Ferries', 'L. Brandt'),
    (3, 'A Field Guide to Moss', 'H. Ito'),
    (4, 'Clockwork Harbor', 'R. Vance'),
    (5, 'The Quiet Orchard', 'S. Mbeki'),
    (6, 'Paper Lanterns', 'J. Cho'),
    (7, 'North of Nowhere', 'P. Lind'),
    (8, 'Tidewater', 'A. Reyes');

CREATE TEMP TABLE loans (
    id        integer PRIMARY KEY,
    book_id   integer NOT NULL,
    card_id   integer NOT NULL,
    out_day   date NOT NULL,
    back_day  date
);
INSERT INTO loans VALUES
    (1, 1, 3, '2026-02-03', NULL),
    (2, 3, 3, '2026-02-10', NULL),
    (3, 5, 3, '2026-03-01', NULL),
    (4, 6, 3, '2025-11-02', '2025-11-20'),
    (5, 2, 1, '2026-01-20', NULL),
    (6, 7, 1, '2026-02-15', NULL),
    (7, 4, 1, '2025-09-15', '2025-10-01'),
    (8, 6, 1, '2025-12-01', '2025-12-15'),
    (9, 1, 1, '2025-10-05', '2025-10-30'),
    (10, 3, 1, '2025-12-20', '2026-01-10'),
    (11, 8, 5, '2026-02-22', NULL),
    (12, 5, 2, '2025-10-10', '2025-10-24'),
    (13, 2, 4, '2025-11-11', '2025-12-01');
"""

TROPHY_SETUP = """
CREATE TEMP TABLE people (
    id      integer PRIMARY KEY,
    name    text NOT NULL,
    street  text NOT NULL,
    house   integer NOT NULL
);
INSERT INTO people VALUES
    (1, 'Harold Pike', 'Maple Street', 88),
    (2, 'June Alvarez', 'Maple Street', 12),
    (3, 'Rosa Marin', 'Elm Street', 5),
    (4, 'Theo Blake', 'Oak Lane', 31),
    (5, 'Priya Nand', 'Birch Road', 7),
    (6, 'Ollie Grant', 'Elm Street', 40),
    (7, 'Mabel Frost', 'Maple Street', 51),
    (8, 'Dev Okafor', 'Oak Lane', 9),
    (9, 'Lena Voss', 'Birch Road', 22),
    (10, 'Sam Ruiz', 'Cedar Court', 3),
    (11, 'Nora Quill', 'Cedar Court', 14),
    (12, 'Felix Hart', 'Maple Street', 70);

CREATE TEMP TABLE reports (
    id       integer PRIMARY KEY,
    day      date NOT NULL,
    place    text NOT NULL,
    kind     text NOT NULL,
    details  text NOT NULL
);
INSERT INTO reports VALUES
    (1, '2026-03-13', 'Town Hall', 'noise',
     'Loud music on the steps after midnight.'),
    (2, '2026-03-14', 'Library', 'theft',
     'A laptop charger went missing from a study desk.'),
    (3, '2026-03-14', 'Town Hall', 'theft',
     'The bake-off trophy vanished from its glass case between 2pm and 3pm. One witness: whoever lives at the highest house number on Maple Street.'),
    (4, '2026-03-15', 'Town Hall', 'vandalism',
     'Chalk drawings all over the front steps.');

CREATE TEMP TABLE interviews (
    person_id  integer NOT NULL,
    said       text NOT NULL
);
INSERT INTO interviews VALUES
    (1, 'I saw someone carry a gold cup out of the side door. They had a Riverside Gym bag, and the membership number on the tag started with 48. They looked like they had come straight from a workout that same day.'),
    (3, 'I was there for the flower show. I did not see a thing.'),
    (4, 'Fine. I took it, but it was not my idea. Someone kept phoning me that week - Monday the 9th to Sunday the 15th - exactly three times, offering money. I never saved the number.');

CREATE TEMP TABLE gym_members (
    id         text PRIMARY KEY,
    person_id  integer NOT NULL
);
INSERT INTO gym_members VALUES
    ('48113', 8), ('48290', 4), ('48507', 9), ('71048', 10), ('20931', 6);

CREATE TEMP TABLE gym_checkins (
    member_id  text NOT NULL,
    day        date NOT NULL,
    check_in   time NOT NULL,
    check_out  time NOT NULL
);
INSERT INTO gym_checkins VALUES
    ('48113', '2026-03-14', '11:00', '12:10'),
    ('48290', '2026-03-14', '12:30', '13:40'),
    ('71048', '2026-03-14', '09:00', '10:00'),
    ('48507', '2026-03-13', '18:00', '19:00'),
    ('20931', '2026-03-14', '13:00', '14:00');

CREATE TEMP TABLE visits (
    person_id  integer NOT NULL,
    place      text NOT NULL,
    day        date NOT NULL,
    arrived    time NOT NULL,
    left_at    time NOT NULL
);
INSERT INTO visits VALUES
    (4, 'Town Hall', '2026-03-14', '14:10', '14:25'),
    (8, 'Town Hall', '2026-03-14', '16:00', '16:30'),
    (3, 'Town Hall', '2026-03-14', '14:30', '15:10'),
    (1, 'Town Hall', '2026-03-14', '13:50', '15:00'),
    (8, 'Library', '2026-03-14', '14:15', '15:00'),
    (9, 'Town Hall', '2026-03-13', '14:20', '14:40');

CREATE TEMP TABLE phone_calls (
    caller    integer NOT NULL,
    receiver  integer NOT NULL,
    day       date NOT NULL,
    seconds   integer NOT NULL
);
INSERT INTO phone_calls VALUES
    (11, 4, '2026-03-10', 95),
    (11, 4, '2026-03-12', 40),
    (11, 4, '2026-03-13', 130),
    (11, 4, '2026-03-02', 60),
    (6, 4, '2026-03-09', 300),
    (6, 4, '2026-03-11', 25),
    (6, 4, '2026-03-12', 410),
    (6, 4, '2026-03-14', 80),
    (2, 4, '2026-03-11', 15),
    (7, 4, '2026-03-01', 50),
    (7, 4, '2026-03-03', 70),
    (7, 4, '2026-03-05', 45),
    (4, 5, '2026-03-10', 200),
    (4, 5, '2026-03-11', 180),
    (4, 5, '2026-03-12', 90);
"""

CASES: tuple[Case, ...] = (
    Case(
        id="case-library",
        title="The Overdue Shelf",
        level=1,
        story=(
            "The town library is missing books. Not stolen, exactly - "
            "borrowed and never brought back. The librarian wants to know "
            "how bad it is, and who is holding on to the most. A loan with "
            "no back_day has not been returned."
        ),
        setup=LIBRARY_SETUP,
        steps=(
            Step(
                question="How many loans are still out - never returned?",
                answer="6",
                reference="SELECT count(*) FROM loans WHERE back_day IS NULL",
                decoy="SELECT count(*) FROM loans WHERE back_day = NULL",
                hint=(
                    "A missing back_day is NULL. Try WHERE back_day = NULL "
                    "and look closely at what comes back."
                ),
                lesson=(
                    "NULL means unknown, so NULL = NULL is not true - it is "
                    "unknown too, and WHERE drops the row. IS NULL is the "
                    "only way to ask whether something is missing."
                ),
            ),
            Step(
                question=(
                    "Which library card has the most books still out? Give "
                    "its number, like LC-0000."
                ),
                answer="LC-3310",
                reference=(
                    "SELECT c.number FROM loans l JOIN cards c ON c.id = l.card_id "
                    "WHERE l.back_day IS NULL GROUP BY c.number "
                    "ORDER BY count(*) DESC LIMIT 1"
                ),
                decoy=(
                    "SELECT c.number FROM loans l JOIN cards c ON c.id = l.card_id "
                    "GROUP BY c.number ORDER BY count(*) DESC LIMIT 1"
                ),
                hint=(
                    "GROUP BY the card and count, largest first. Keep the "
                    "still-out filter from the last step, or you are counting "
                    "every loan ever."
                ),
                lesson=(
                    "WHERE picks the rows before GROUP BY counts them. Leave "
                    "the filter off and you get the busiest borrower, which "
                    "is a different person from the worst one."
                ),
            ),
            Step(
                question="Whose card is it?",
                answer="Eve Lund",
                reference=(
                    "SELECT p.name FROM cards c JOIN people p ON p.id = c.person_id "
                    "WHERE c.number = 'LC-3310'"
                ),
                decoy=(
                    "SELECT p.name FROM cards c JOIN people p ON p.id = c.id "
                    "WHERE c.number = 'LC-3310'"
                ),
                hint=(
                    "cards has its own id and a person_id. Only one of those "
                    "is a person."
                ),
                lesson=(
                    "A join is only as right as the columns it matches. "
                    "p.id = c.id runs without a complaint and pairs the card "
                    "with whoever happens to share its row number."
                ),
            ),
            Step(
                question=(
                    "Eve says she only joined this year and never borrowed a "
                    "thing before 2026. When was her first loan? Give the date "
                    "as YYYY-MM-DD."
                ),
                answer="2025-11-02",
                reference=(
                    "SELECT min(l.out_day) FROM loans l JOIN cards c ON c.id = l.card_id "
                    "WHERE c.number = 'LC-3310'"
                ),
                decoy=(
                    "SELECT min(l.out_day) FROM loans l JOIN cards c ON c.id = l.card_id "
                    "WHERE c.number = 'LC-3310' AND l.back_day IS NULL"
                ),
                hint=(
                    "Every loan counts this time, returned or not. MIN gives "
                    "the earliest date."
                ),
                lesson=(
                    "Filters carried over from the last question answer the "
                    "last question. Each question gets its own WHERE."
                ),
            ),
        ),
        ending=(
            "Eve has had a card since November 2025, and three books out. "
            "The librarian sends a polite letter. The Quiet Orchard comes "
            "back the next day."
        ),
    ),
    Case(
        id="case-trophy",
        title="The Bake-off Trophy",
        level=2,
        story=(
            "On 14 March 2026 the bake-off trophy disappeared from Town "
            "Hall. Start with the reports table: find the theft, read what "
            "it says, and follow it. Dates are written 'YYYY-MM-DD' and "
            "times '14:00'."
        ),
        setup=TROPHY_SETUP,
        steps=(
            Step(
                question=(
                    "Find the theft report for Town Hall on 2026-03-14. It "
                    "points at a witness. Who is the witness?"
                ),
                answer="Harold Pike",
                reference=(
                    "SELECT name FROM people WHERE street = 'Maple Street' "
                    "ORDER BY house DESC LIMIT 1"
                ),
                decoy=(
                    "SELECT name FROM people WHERE street = 'Maple Street' "
                    "ORDER BY house LIMIT 1"
                ),
                hint=(
                    "Read the report's details first. Then sort the people on "
                    "that street by house number - which end do you want?"
                ),
                lesson=(
                    "ORDER BY is smallest first unless told otherwise. "
                    "ORDER BY ... DESC LIMIT 1 is how SQL says 'the biggest'."
                ),
            ),
            Step(
                question=(
                    "Read the witness's interview. How many gym members fit "
                    "what they saw - a number starting 48, and a check-in on "
                    "the day of the theft?"
                ),
                answer="2",
                reference=(
                    "SELECT count(DISTINCT m.id) FROM gym_members m "
                    "JOIN gym_checkins c ON c.member_id = m.id "
                    "WHERE m.id LIKE '48%' AND c.day = '2026-03-14'"
                ),
                decoy=(
                    "SELECT count(DISTINCT m.id) FROM gym_members m "
                    "JOIN gym_checkins c ON c.member_id = m.id "
                    "WHERE m.id LIKE '%48%' AND c.day = '2026-03-14'"
                ),
                hint=(
                    "interviews.person_id is the witness's id. For the "
                    "members, LIKE with % matches any run of characters - "
                    "where does the % go if the number starts with 48?"
                ),
                lesson=(
                    "In LIKE, % stands for anything, including nothing. "
                    "'48%' is starts-with; '%48%' is contains, and 71048 "
                    "contains 48."
                ),
            ),
            Step(
                question=(
                    "Of those members, who was at Town Hall between 2pm and "
                    "3pm on the day?"
                ),
                answer="Theo Blake",
                reference=(
                    "SELECT DISTINCT p.name FROM people p "
                    "JOIN gym_members m ON m.person_id = p.id "
                    "JOIN gym_checkins c ON c.member_id = m.id "
                    "JOIN visits v ON v.person_id = p.id "
                    "WHERE m.id LIKE '48%' AND c.day = '2026-03-14' "
                    "AND v.place = 'Town Hall' AND v.day = '2026-03-14' "
                    "AND v.arrived < '15:00' AND v.left_at > '14:00'"
                ),
                decoy=(
                    "SELECT DISTINCT p.name FROM people p "
                    "JOIN gym_members m ON m.person_id = p.id "
                    "JOIN gym_checkins c ON c.member_id = m.id "
                    "JOIN visits v ON v.person_id = p.id "
                    "WHERE m.id LIKE '48%' AND c.day = '2026-03-14' "
                    "AND v.place = 'Town Hall' AND v.day = '2026-03-14'"
                ),
                hint=(
                    "Join the members to their visits. Being there that day "
                    "is not enough - the visit has to overlap 14:00 to 15:00."
                ),
                lesson=(
                    "Two time ranges overlap when each starts before the "
                    "other ends: arrived < '15:00' AND left_at > '14:00'. "
                    "Leave the times out and an alibi looks like a suspect."
                ),
            ),
            Step(
                question=(
                    "Read Theo's interview. Who put him up to it?"
                ),
                answer="Nora Quill",
                reference=(
                    "SELECT p.name FROM phone_calls c JOIN people p ON p.id = c.caller "
                    "WHERE c.receiver = 4 "
                    "AND c.day BETWEEN '2026-03-09' AND '2026-03-15' "
                    "GROUP BY p.name HAVING count(*) = 3"
                ),
                decoy=(
                    "SELECT p.name FROM phone_calls c JOIN people p ON p.id = c.caller "
                    "WHERE c.receiver = 4 "
                    "GROUP BY p.name HAVING count(*) = 3"
                ),
                hint=(
                    "Calls to Theo, inside that week, counted per caller. "
                    "HAVING filters groups the way WHERE filters rows."
                ),
                lesson=(
                    "WHERE narrows the rows, then GROUP BY counts, then "
                    "HAVING keeps the groups you want. Skip the date and "
                    "someone who called three times the week before looks "
                    "exactly as guilty."
                ),
            ),
        ),
        ending=(
            "Nora Quill came second in last year's bake-off. The trophy turns "
            "up in her shed, polished."
        ),
    ),
)
