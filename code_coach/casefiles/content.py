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

DELIVERIES_SETUP = """
CREATE TEMP TABLE customers (
    id    integer PRIMARY KEY,
    name  text NOT NULL,
    town  text NOT NULL
);
INSERT INTO customers VALUES
    (1, 'Ana Ruiz', 'Hillford'), (2, 'Bo Chen', 'Hillford'),
    (3, 'Cal Obi', 'Marsh End'), (4, 'Dee Park', 'Marsh End'),
    (6, 'Fay Lin', 'Kettle Cross'), (7, 'Eli Stone', 'Kettle Cross');

CREATE TEMP TABLE orders (
    id           integer PRIMARY KEY,
    customer_id  integer NOT NULL,
    placed       date NOT NULL,
    total        numeric(8, 2) NOT NULL
);
INSERT INTO orders VALUES
    (1, 1, '2026-04-01', 12.00),
    (2, 2, '2026-04-01', 18.50),
    (3, 3, '2026-04-02', 9.00),
    (4, 4, '2026-04-03', 22.00),
    (5, 7, '2026-04-03', 15.00),
    (6, 6, '2026-04-04', 11.50),
    (7, 3, '2026-04-05', 30.00),
    (8, 4, '2026-04-05', 14.00),
    (9, 1, '2026-04-06', 8.00),
    (10, 7, '2026-04-06', 19.00),
    (11, 2, '2026-04-07', 16.00),
    (12, 6, '2026-04-07', 10.00),
    (13, 2, '2026-04-08', 7.00);

CREATE TEMP TABLE drivers (
    id    integer PRIMARY KEY,
    name  text NOT NULL,
    van   text NOT NULL
);
INSERT INTO drivers VALUES
    (1, 'Gus Hale', 'A'), (2, 'Ivy Moss', 'B'),
    (3, 'Jon Reed', 'C'), (4, 'Kit Ash', 'D');

CREATE TEMP TABLE deliveries (
    order_id   integer,
    driver_id  integer NOT NULL,
    delivered  date NOT NULL
);
INSERT INTO deliveries VALUES
    (1, 1, '2026-04-02'), (2, 2, '2026-04-02'), (5, 1, '2026-04-04'),
    (6, 3, '2026-04-05'), (8, 2, '2026-04-06'), (9, 3, '2026-04-07'),
    (11, 1, '2026-04-08'), (13, 2, '2026-04-09'),
    (NULL, 3, '2026-04-06');

CREATE TEMP TABLE shifts (
    driver_id  integer NOT NULL,
    day        date NOT NULL
);
INSERT INTO shifts VALUES
    (1, '2026-04-01'), (1, '2026-04-02'), (1, '2026-04-03'), (1, '2026-04-04'),
    (1, '2026-04-05'), (1, '2026-04-06'), (1, '2026-04-08'), (1, '2026-04-09'),
    (2, '2026-04-01'), (2, '2026-04-02'), (2, '2026-04-04'), (2, '2026-04-06'),
    (2, '2026-04-07'), (2, '2026-04-08'), (2, '2026-04-09'),
    (3, '2026-04-03'), (3, '2026-04-04'), (3, '2026-04-05'), (3, '2026-04-06'),
    (3, '2026-04-07'), (3, '2026-04-08'),
    (4, '2026-04-02'), (4, '2026-04-03'), (4, '2026-04-05'), (4, '2026-04-06'),
    (4, '2026-04-07');
"""

#: The orders nobody delivered, written once for the queries that need it.
_MISSING = (
    "SELECT o.* FROM orders o LEFT JOIN deliveries v ON v.order_id = o.id "
    "WHERE v.order_id IS NULL"
)

RECEIPTS_SETUP = """
CREATE TEMP TABLE staff (
    name  text PRIMARY KEY,
    dept  text NOT NULL
);
INSERT INTO staff VALUES
    ('Ada Brook', 'Sales'), ('Ben Cole', 'Sales'),
    ('Cara Dunn', 'Design'), ('Dev Ellis', 'Operations');

CREATE TEMP TABLE vendors (
    name  text PRIMARY KEY,
    city  text NOT NULL
);
INSERT INTO vendors VALUES
    ('Paper Mill', 'Hillford'), ('Swift Cabs', 'Hillford'),
    ('Green Cafe', 'Marsh End'), ('Byte Store', 'Kettle Cross');

CREATE TEMP TABLE expenses (
    id          integer PRIMARY KEY,
    staff       text NOT NULL,
    claimed_on  date NOT NULL,
    vendor      text NOT NULL,
    amount      numeric(8, 2)
);
INSERT INTO expenses VALUES
    (1, 'Ada Brook', '2026-05-01', 'Paper Mill', 24.00),
    (2, 'Ben Cole', '2026-05-02', 'paper mill ', 18.00),
    (3, 'Cara Dunn', '2026-05-03', 'Swift Cabs', 32.00),
    (4, 'Dev Ellis', '2026-05-04', 'SWIFT CABS', 27.50),
    (5, 'Ada Brook', '2026-05-05', 'Green Cafe', 12.00),
    (6, 'Dev Ellis', '2026-05-06', 'Byte Store', 60.00),
    (7, 'Dev Ellis', '2026-05-08', 'Quick Print', 45.00),
    (8, 'Dev Ellis', '2026-05-09', 'byte store', 60.00),
    (9, 'Cara Dunn', '2026-05-10', ' Green Cafe', 15.00),
    (10, 'Ben Cole', '2026-05-01', 'Swift Cabs', 40.00),
    (11, 'Ben Cole', '2026-06-01', 'Swift Cabs', 40.00),
    (12, 'Dev Ellis', '2026-05-12', 'Green Cafe', NULL),
    (13, 'Dev Ellis', '2026-05-14', 'Paper Mill', NULL);
"""

ARCADE_SETUP = """
CREATE TEMP TABLE players (
    id      integer PRIMARY KEY,
    handle  text NOT NULL
);
INSERT INTO players VALUES
    (1, 'ZAP'), (2, 'MOTH'), (3, 'KIRA'), (4, 'BOLT'), (5, 'NOVA'), (6, 'VEX');

CREATE TEMP TABLE scores (
    player_id  integer NOT NULL,
    game       text NOT NULL,
    points     integer NOT NULL,
    played     timestamp NOT NULL
);
INSERT INTO scores VALUES
    (1, 'Comet Run', 41200, '2026-04-01 10:00'),
    (3, 'Comet Run', 30500, '2026-04-01 11:00'),
    (4, 'Comet Run', 29000, '2026-04-02 09:00'),
    (2, 'Comet Run', 12000, '2026-04-02 15:00'),
    (1, 'Comet Run', 40100, '2026-04-03 12:00'),
    (3, 'Comet Run', 39000, '2026-04-04 13:00'),
    (2, 'Comet Run', 13500, '2026-04-05 16:00'),
    (2, 'Comet Run', 36000, '2026-04-06 18:00'),
    (5, 'Comet Run', 30000, '2026-04-06 19:00'),
    (1, 'Tunnel Fox', 820, '2026-04-01 12:00'),
    (2, 'Tunnel Fox', 640, '2026-04-02 16:00'),
    (3, 'Tunnel Fox', 900, '2026-04-03 10:00'),
    (4, 'Tunnel Fox', 510, '2026-04-03 11:00'),
    (5, 'Tunnel Fox', 770, '2026-04-05 14:00'),
    (6, 'Tunnel Fox', 880, '2026-04-06 20:00'),
    (1, 'Hex Drop', 2000, '2026-04-02 10:00'),
    (3, 'Hex Drop', 2100, '2026-04-04 15:00'),
    (4, 'Hex Drop', 1900, '2026-04-05 12:00');
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
    Case(
        id="case-deliveries",
        title="The Missing Deliveries",
        level=2,
        story=(
            "A small coffee roaster takes orders all week and its drivers "
            "deliver them. Some customers paid and never got their coffee. "
            "An order with no row in deliveries was never delivered. The "
            "deliveries table has one slip with no order number on it - a "
            "driver forgot to fill it in."
        ),
        setup=DELIVERIES_SETUP,
        steps=(
            Step(
                question="How many orders were never delivered?",
                answer="5",
                reference="SELECT count(*) FROM (" + _MISSING + ") m",
                decoy=(
                    "SELECT count(*) FROM orders "
                    "WHERE id NOT IN (SELECT order_id FROM deliveries)"
                ),
                hint=(
                    "Match every order to its delivery with a LEFT JOIN, and "
                    "keep the orders where the delivery side came back empty. "
                    "If you tried NOT IN and got 0, look at that slip."
                ),
                lesson=(
                    "NOT IN against a list holding a NULL finds nothing: "
                    "'is 3 not in (1, 2, NULL)?' is unknown, because the "
                    "NULL might be 3. LEFT JOIN ... IS NULL, or NOT EXISTS, "
                    "asks the question you meant."
                ),
            ),
            Step(
                question="Which town lost the most orders?",
                answer="Marsh End",
                reference=(
                    "SELECT c.town FROM (" + _MISSING + ") m "
                    "JOIN customers c ON c.id = m.customer_id "
                    "GROUP BY c.town ORDER BY count(*) DESC LIMIT 1"
                ),
                decoy=(
                    "SELECT c.town FROM orders o JOIN customers c ON c.id = o.customer_id "
                    "GROUP BY c.town ORDER BY count(*) DESC LIMIT 1"
                ),
                hint=(
                    "Start from the undelivered orders, join them to customers, "
                    "then count per town."
                ),
                lesson=(
                    "The town that orders the most is not the town that "
                    "loses the most. Filter first, then group."
                ),
            ),
            Step(
                question=(
                    "The missing orders were placed on several different days. "
                    "One driver was on shift on every one of those days. Who?"
                ),
                answer="Kit Ash",
                reference=(
                    "SELECT d.name FROM shifts s JOIN drivers d ON d.id = s.driver_id "
                    "WHERE s.day IN (SELECT placed FROM (" + _MISSING + ") m) "
                    "GROUP BY d.name "
                    "HAVING count(DISTINCT s.day) = "
                    "(SELECT count(DISTINCT placed) FROM (" + _MISSING + ") m)"
                ),
                decoy=(
                    "SELECT d.name FROM shifts s JOIN drivers d ON d.id = s.driver_id "
                    "GROUP BY d.name ORDER BY count(*) DESC LIMIT 1"
                ),
                hint=(
                    "Count how many of the missing-order days each driver "
                    "worked, and keep the driver whose count equals the number "
                    "of those days. A subquery can give you that number."
                ),
                lesson=(
                    "'On every one of these' is a count that has to match: "
                    "keep the rows that are in the set, count them per "
                    "person, and compare with the size of the set. The "
                    "busiest driver is not the same thing."
                ),
            ),
            Step(
                question=(
                    "The driver says it was a quiet week and nothing much went "
                    "missing. What were the missing orders worth altogether?"
                ),
                answer="90.00",
                reference="SELECT sum(total) FROM (" + _MISSING + ") m",
                decoy=(
                    "SELECT sum(o.total) FROM orders o "
                    "JOIN shifts s ON s.day = o.placed WHERE s.driver_id = 4"
                ),
                hint=(
                    "Only the undelivered orders - not every order placed on "
                    "that driver's shifts."
                ),
                lesson=(
                    "A join can bring in rows you did not mean to count. "
                    "Before summing, ask which rows are in the result and "
                    "whether each one belongs."
                ),
            ),
        ),
        ending=(
            "Kit had been keeping the orders and selling the coffee at the "
            "Sunday market. Ninety pounds of beans, give or take."
        ),
    ),
    Case(
        id="case-receipts",
        title="The Doubled Receipts",
        level=2,
        story=(
            "Finance has a pile of expense claims and a list of approved "
            "vendors. The vendor names on the claims were typed by hand, so "
            "the same shop is spelled several ways. Something in the pile "
            "is not right."
        ),
        setup=RECEIPTS_SETUP,
        steps=(
            Step(
                question=(
                    "How many different vendors appear in the claims, once "
                    "capital letters and stray spaces are ignored?"
                ),
                answer="5",
                reference="SELECT count(DISTINCT lower(trim(vendor))) FROM expenses",
                decoy="SELECT count(DISTINCT vendor) FROM expenses",
                hint=(
                    "DISTINCT compares text exactly. lower() and trim() make "
                    "'paper mill ' and 'Paper Mill' the same before it looks."
                ),
                lesson=(
                    "To the database, 'Paper Mill' and 'paper mill ' are "
                    "different strings. Clean text up before comparing, "
                    "grouping or counting it."
                ),
            ),
            Step(
                question=(
                    "One claim is from a vendor that is not on the approved "
                    "list at all. Who made that claim?"
                ),
                answer="Dev Ellis",
                reference=(
                    "SELECT e.staff FROM expenses e LEFT JOIN vendors v "
                    "ON lower(v.name) = lower(trim(e.vendor)) WHERE v.name IS NULL"
                ),
                decoy=(
                    "SELECT e.staff FROM expenses e LEFT JOIN vendors v "
                    "ON v.name = e.vendor WHERE v.name IS NULL"
                ),
                hint=(
                    "A LEFT JOIN to vendors, keeping the claims with no match. "
                    "The join has to compare cleaned-up names, or every typo "
                    "looks like a stranger."
                ),
                lesson=(
                    "A join condition is a comparison like any other, and it "
                    "is just as fussy about case and spaces. Clean both sides "
                    "the same way."
                ),
            ),
            Step(
                question=(
                    "Someone claimed the same amount from the same vendor twice "
                    "within a week. How much was it?"
                ),
                answer="60.00",
                reference=(
                    "SELECT DISTINCT a.amount FROM expenses a JOIN expenses b "
                    "ON a.staff = b.staff "
                    "AND lower(trim(a.vendor)) = lower(trim(b.vendor)) "
                    "AND a.amount = b.amount AND a.id < b.id "
                    "WHERE b.claimed_on - a.claimed_on BETWEEN -7 AND 7"
                ),
                decoy=(
                    "SELECT DISTINCT a.amount FROM expenses a JOIN expenses b "
                    "ON a.staff = b.staff "
                    "AND lower(trim(a.vendor)) = lower(trim(b.vendor)) "
                    "AND a.amount = b.amount AND a.id < b.id"
                ),
                hint=(
                    "Join expenses to itself, so each claim can be compared "
                    "with every other. Subtracting two dates gives the days "
                    "between them."
                ),
                lesson=(
                    "A self-join pairs each row with the others in the same "
                    "table. a.id < b.id keeps each pair once, and a monthly "
                    "cab to the same office is not a duplicate - the week "
                    "limit is what tells them apart."
                ),
            ),
            Step(
                question=(
                    "The person from step two has two claims with no amount "
                    "filled in yet. Finance counts a missing amount as zero. "
                    "What is their average claim, to two decimal places?"
                ),
                answer="32.08",
                reference=(
                    "SELECT round(avg(coalesce(amount, 0)), 2) FROM expenses "
                    "WHERE staff = 'Dev Ellis'"
                ),
                decoy=(
                    "SELECT round(avg(amount), 2) FROM expenses "
                    "WHERE staff = 'Dev Ellis'"
                ),
                hint=(
                    "avg skips NULLs entirely. coalesce(amount, 0) turns a "
                    "missing amount into a zero before avg sees it."
                ),
                lesson=(
                    "Aggregates ignore NULL: avg of 10, 20 and NULL is 15, "
                    "not 10. When a missing value should count as something, "
                    "coalesce says what."
                ),
            ),
        ),
        ending=(
            "Quick Print turned out to be Dev's cousin's printer, and the "
            "second Byte Store receipt was a photocopy of the first."
        ),
    ),
    Case(
        id="case-arcade",
        title="The Rigged Leaderboard",
        level=3,
        story=(
            "The Pixel Palace arcade keeps every score ever played. The "
            "owner thinks someone has been cheating on the most popular "
            "machine: a score that jumped far too much in one go. Each "
            "player is known only by their handle."
        ),
        setup=ARCADE_SETUP,
        steps=(
            Step(
                question="Which game has been played the most times?",
                answer="Comet Run",
                reference=(
                    "SELECT game FROM scores GROUP BY game "
                    "ORDER BY count(*) DESC LIMIT 1"
                ),
                decoy=(
                    "SELECT game FROM scores GROUP BY game "
                    "ORDER BY count(DISTINCT player_id) DESC LIMIT 1"
                ),
                hint="One row per go. Count rows per game, not players.",
                lesson=(
                    "count(*) counts rows; count(DISTINCT x) counts different "
                    "values of x. 'Played the most' is goes, not people."
                ),
            ),
            Step(
                question=(
                    "On that game, who is in second place? Each player's best "
                    "score counts once."
                ),
                answer="KIRA",
                reference=(
                    "SELECT p.handle FROM scores s JOIN players p ON p.id = s.player_id "
                    "WHERE s.game = 'Comet Run' GROUP BY p.handle "
                    "ORDER BY max(s.points) DESC OFFSET 1 LIMIT 1"
                ),
                decoy=(
                    "SELECT p.handle FROM scores s JOIN players p ON p.id = s.player_id "
                    "WHERE s.game = 'Comet Run' "
                    "ORDER BY s.points DESC OFFSET 1 LIMIT 1"
                ),
                hint=(
                    "Sort the raw scores and the top two might both belong to "
                    "one player. Take each player's max first, then sort."
                ),
                lesson=(
                    "A leaderboard ranks players, not goes. GROUP BY the "
                    "player and take max() so each one appears once, then "
                    "OFFSET 1 skips first place."
                ),
            ),
            Step(
                question=(
                    "On that game, one player's score went up by more than "
                    "10000 from their own previous go. Who?"
                ),
                answer="MOTH",
                reference=(
                    "SELECT DISTINCT p.handle FROM ("
                    "SELECT player_id, points - lag(points) OVER "
                    "(PARTITION BY player_id ORDER BY played) AS jump "
                    "FROM scores WHERE game = 'Comet Run') s "
                    "JOIN players p ON p.id = s.player_id WHERE s.jump > 10000"
                ),
                decoy=(
                    "SELECT DISTINCT p.handle FROM ("
                    "SELECT player_id, points - lag(points) OVER "
                    "(ORDER BY played) AS jump "
                    "FROM scores WHERE game = 'Comet Run') s "
                    "JOIN players p ON p.id = s.player_id WHERE s.jump > 10000"
                ),
                hint=(
                    "lag(points) OVER (... ORDER BY played) gives the score "
                    "from the go before. Without PARTITION BY, 'the go before' "
                    "is whoever played last - not the same player."
                ),
                lesson=(
                    "A window function looks at neighbouring rows. PARTITION "
                    "BY says whose rows are neighbours; leave it out and "
                    "every player is compared with a stranger."
                ),
            ),
            Step(
                question="What did the cheat score on the go just before the jump?",
                answer="13500",
                reference=(
                    "SELECT before FROM ("
                    "SELECT points, lag(points) OVER "
                    "(PARTITION BY player_id ORDER BY played) AS before "
                    "FROM scores WHERE game = 'Comet Run') s "
                    "WHERE points - before > 10000"
                ),
                decoy=(
                    "SELECT min(points) FROM scores "
                    "WHERE game = 'Comet Run' AND player_id = 2"
                ),
                hint=(
                    "The same lag() as before, but select the previous score "
                    "itself rather than the difference."
                ),
                lesson=(
                    "The go before is not the lowest go. lag() gives the row "
                    "next door in the order you chose, which is what "
                    "'just before' means."
                ),
            ),
        ),
        ending=(
            "MOTH had found that holding two buttons during the bonus stage "
            "doubled every coin. The machine has been patched, and MOTH's "
            "score has been quietly removed."
        ),
    ),
)
