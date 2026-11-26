"""SQL query patterns: the clauses real queries are built from.

The lines are fragments - one clause each, the way a query is actually
written down the page - covering window functions, CTEs, CASE, subqueries,
EXISTS, set operations, upserts, date and string functions, NULL handling
and the aggregates. A fragment cannot be run on its own, so the lines are
checked only for what they contain.

The blocks are whole statements, and tests/test_typing_sqlquery.py runs
every one in SQLite against the small shop database in SCHEMA below and
holds the rows it returns to an answer worked out by hand.
"""

from __future__ import annotations

from code_coach.typing.texts import Passage


def _s(text: str, note: str) -> Passage:
    return Passage(text, note)


# -- Lines ----------------------------------------------------

SQLQUERY_LINES: tuple[Passage, ...] = (
    # filtering
    _s("WHERE price BETWEEN 10 AND 20", "both ends included"),
    _s("WHERE category IN ('tea', 'coffee')", "any of a list"),
    _s("WHERE name LIKE 'A%' AND name NOT LIKE '%x'", "starts with A, does not end in x"),
    _s("WHERE shipped_at IS NOT NULL", "the only way to test for a value"),
    _s("WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)",
       "customers who never ordered"),
    _s("WHERE price > (SELECT AVG(price) FROM products)", "above the average"),
    _s("WHERE customer_id IN (SELECT id FROM customers WHERE city = 'Leeds')",
       "a subquery as the list"),
    # grouping
    _s("SELECT category, COUNT(*) AS n, AVG(price) AS avg_price", "one row per group"),
    _s("GROUP BY category, strftime('%Y', ordered_at)", "per category per year"),
    _s("HAVING COUNT(*) >= 3", "only groups with at least three"),
    _s("SELECT COUNT(DISTINCT customer_id) FROM orders;", "how many different customers"),
    _s("SUM(CASE WHEN status = 'paid' THEN total ELSE 0 END) AS paid", "a conditional sum"),
    _s("MAX(total) - MIN(total) AS spread", "the range of a group"),
    _s("GROUP_CONCAT(name, ', ') AS names", "a group's names joined into one string"),
    # joins
    _s("FROM orders AS o JOIN customers AS c ON c.id = o.customer_id",
       "short aliases for both tables"),
    _s("LEFT JOIN order_items AS i ON i.order_id = o.id", "orders with no items survive"),
    _s("JOIN products AS p USING (product_id)", "when the column has the same name"),
    _s("CROSS JOIN sizes", "every row with every row"),
    _s("FROM employees AS e LEFT JOIN employees AS m ON m.id = e.manager_id",
       "a table joined to itself"),
    # CASE and NULLs
    _s("CASE WHEN total >= 100 THEN 'big' WHEN total >= 20 THEN 'mid' ELSE 'small' END",
       "first true branch wins"),
    _s("COALESCE(discount, 0) AS discount", "NULL becomes 0 for the arithmetic"),
    _s("NULLIF(quantity, 0)", "turns 0 into NULL, so a division gives NULL not an error"),
    _s("total * 1.0 / NULLIF(items, 0) AS per_item", "safe division"),
    _s("ORDER BY shipped_at IS NULL, shipped_at", "the NULLs last"),
    # window functions
    _s("ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at) AS nth",
       "numbering each customer's orders"),
    _s("RANK() OVER (ORDER BY total DESC) AS place", "ties share a place, then skip"),
    _s("DENSE_RANK() OVER (ORDER BY score DESC)", "ties share a place, no gaps"),
    _s("SUM(total) OVER (ORDER BY ordered_at) AS running_total", "a running total"),
    _s("AVG(price) OVER (PARTITION BY category) AS category_avg", "each row beside its group's average"),
    _s("LAG(total) OVER (ORDER BY ordered_at) AS previous", "the row before"),
    _s("LEAD(ordered_at) OVER (PARTITION BY customer_id ORDER BY ordered_at)",
       "the same customer's next order"),
    _s("ROWS BETWEEN 2 PRECEDING AND CURRENT ROW", "a three-row moving window"),
    # CTEs
    _s("WITH totals AS (SELECT customer_id, SUM(total) AS spent FROM orders GROUP BY 1)",
       "a named subquery to read from"),
    _s("WITH RECURSIVE n(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM n WHERE i < 10)",
       "counting to ten"),
    _s("SELECT * FROM ranked WHERE nth = 1;", "each customer's first order"),
    # set operations
    _s("SELECT email FROM customers UNION SELECT email FROM newsletter;",
       "both lists, duplicates removed"),
    _s("SELECT id FROM products EXCEPT SELECT product_id FROM order_items;",
       "products nobody bought"),
    _s("SELECT city FROM customers INTERSECT SELECT city FROM stores;", "cities with both"),
    _s("UNION ALL", "keeps the duplicates, and is faster for it"),
    # ordering and paging
    _s("ORDER BY total DESC, ordered_at ASC", "biggest first, oldest first among equals"),
    _s("LIMIT 20 OFFSET 40", "the third page of twenty"),
    _s("ORDER BY RANDOM() LIMIT 1;", "one row at random"),
    # changing data
    _s("INSERT INTO products (name, price) VALUES ('tea', 3), ('jam', 4);", "two rows at once"),
    _s("INSERT INTO stock (product_id, qty) VALUES (?, ?) ON CONFLICT (product_id)",
       "an upsert begins"),
    _s("DO UPDATE SET qty = stock.qty + excluded.qty;", "and adds to what is there"),
    _s("UPDATE products SET price = ROUND(price * 1.1, 2) WHERE category = 'tea';",
       "a price rise for one category"),
    _s("DELETE FROM carts WHERE updated_at < date('now', '-30 days');", "abandoned carts"),
    _s("INSERT INTO archive SELECT * FROM orders WHERE status = 'closed';",
       "copying rows from a query"),
    # schema
    _s("CREATE TABLE customers (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE);",
       "a key and a rule"),
    _s("customer_id INTEGER REFERENCES customers (id) ON DELETE CASCADE",
       "a foreign key that tidies up after itself"),
    _s("price REAL NOT NULL CHECK (price >= 0)", "the database refuses bad data"),
    _s("CREATE UNIQUE INDEX idx_one_cart ON carts (customer_id);", "one cart each"),
    _s("ALTER TABLE products ADD COLUMN archived INTEGER DEFAULT 0;", "a new column"),
    _s("CREATE VIEW paid_orders AS SELECT * FROM orders WHERE status = 'paid';",
       "a saved query"),
    # dates and strings
    _s("strftime('%Y-%m', ordered_at) AS month", "the month as text, for grouping"),
    _s("date(ordered_at, '+7 days') AS due", "a week later"),
    _s("julianday(shipped_at) - julianday(ordered_at) AS days_to_ship", "days between"),
    _s("UPPER(SUBSTR(name, 1, 1)) || LOWER(SUBSTR(name, 2))", "capitalising a name"),
    _s("TRIM(email) = LOWER(TRIM(email))", "already lower case"),
    _s("LENGTH(code) = 6 AND code GLOB '[A-Z][A-Z][0-9]*'", "a pattern with GLOB"),
    _s("REPLACE(phone, ' ', '')", "spaces taken out"),
    # transactions
    _s("BEGIN TRANSACTION;", "nothing below is final until COMMIT"),
    _s("ROLLBACK;", "undo everything since BEGIN"),
    _s("SAVEPOINT before_refund;", "a point you can roll back to"),
)


# -- Blocks ---------------------------------------------------

#: The shop the blocks run against. Kept tiny so the answers can be worked
#: out by hand.
SCHEMA = """
CREATE TABLE customers (id INTEGER PRIMARY KEY, name TEXT, city TEXT);
CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, price REAL);
CREATE TABLE orders (id INTEGER PRIMARY KEY, customer_id INTEGER, product_id INTEGER,
                     qty INTEGER, ordered_at TEXT, status TEXT);
INSERT INTO customers VALUES (1, 'Ada', 'Leeds'), (2, 'Bo', 'York'), (3, 'Cy', 'Leeds'),
                             (4, 'Di', 'Bath');
INSERT INTO products VALUES (1, 'green tea', 'tea', 4.0), (2, 'black tea', 'tea', 3.0),
                            (3, 'espresso', 'coffee', 5.0), (4, 'mug', 'kit', 8.0);
INSERT INTO orders VALUES
  (1, 1, 1, 2, '2026-01-05', 'paid'),
  (2, 1, 3, 1, '2026-01-20', 'paid'),
  (3, 2, 2, 3, '2026-02-02', 'paid'),
  (4, 3, 4, 1, '2026-02-10', 'open'),
  (5, 2, 1, 1, '2026-03-01', 'paid'),
  (6, 1, 4, 2, '2026-03-15', 'open');
"""


def _b(code: str, note: str) -> Passage:
    return Passage(code, f"SQL · {note}")


SQLQUERY_BLOCKS: tuple[Passage, ...] = (
    _b("""SELECT c.name, COUNT(o.id) AS orders
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.id
GROUP BY c.id
ORDER BY orders DESC, c.name;""",
       "orders per customer, including none"),
    _b("""SELECT p.category, SUM(o.qty * p.price) AS revenue
FROM orders AS o
JOIN products AS p ON p.id = o.product_id
WHERE o.status = 'paid'
GROUP BY p.category
ORDER BY revenue DESC;""",
       "paid revenue by category"),
    _b("""SELECT name
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1 FROM orders AS o WHERE o.customer_id = c.id
);""",
       "customers who never ordered"),
    _b("""SELECT name, price,
    CASE WHEN price >= 5 THEN 'dear'
         WHEN price >= 4 THEN 'fair'
         ELSE 'cheap' END AS band
FROM products
ORDER BY price;""",
       "banding prices with CASE"),
    _b("""SELECT id, customer_id, ordered_at,
    ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY ordered_at) AS nth
FROM orders
WHERE customer_id = 1
ORDER BY nth;""",
       "numbering one customer's orders"),
    _b("""WITH spent AS (
    SELECT o.customer_id, SUM(o.qty * p.price) AS total
    FROM orders AS o JOIN products AS p ON p.id = o.product_id
    GROUP BY o.customer_id
)
SELECT c.name, s.total, RANK() OVER (ORDER BY s.total DESC) AS place
FROM spent AS s JOIN customers AS c ON c.id = s.customer_id
ORDER BY place;""",
       "ranking customers by spend with a CTE"),
    _b("""SELECT strftime('%Y-%m', ordered_at) AS month,
    COUNT(*) AS orders,
    SUM(COUNT(*)) OVER (ORDER BY strftime('%Y-%m', ordered_at)) AS running
FROM orders
GROUP BY month
ORDER BY month;""",
       "orders per month with a running total"),
    _b("""WITH RECURSIVE n(i) AS (
    SELECT 1
    UNION ALL
    SELECT i + 1 FROM n WHERE i < 5
)
SELECT group_concat(i * i, ' ') FROM n;""",
       "the first five squares with a recursive CTE"),
    _b("""SELECT city, COUNT(*) AS people, group_concat(name, '+') AS names
FROM customers
GROUP BY city
HAVING COUNT(*) > 1;""",
       "cities with more than one customer"),
    _b("""SELECT name FROM products
EXCEPT
SELECT p.name FROM products AS p JOIN orders AS o ON o.product_id = p.id
                WHERE o.status = 'paid'
ORDER BY name;""",
       "products with no paid order"),
)

#: The rows each block returns, by its note, as Python would print the
#: list SQLite gives back - worked out by hand from SCHEMA.
SQLQUERY_ROWS: dict[str, str] = {
    "orders per customer, including none":
        "[('Ada', 3), ('Bo', 2), ('Cy', 1), ('Di', 0)]",
    "paid revenue by category":
        "[('tea', 21.0), ('coffee', 5.0)]",
    "customers who never ordered": "[('Di',)]",
    "banding prices with CASE":
        "[('black tea', 3.0, 'cheap'), ('green tea', 4.0, 'fair'), ('espresso', 5.0, 'dear'), "
        "('mug', 8.0, 'dear')]",
    "numbering one customer's orders":
        "[(1, 1, '2026-01-05', 1), (2, 1, '2026-01-20', 2), (6, 1, '2026-03-15', 3)]",
    "ranking customers by spend with a CTE":
        "[('Ada', 29.0, 1), ('Bo', 13.0, 2), ('Cy', 8.0, 3)]",
    "orders per month with a running total":
        "[('2026-01', 2, 2), ('2026-02', 2, 4), ('2026-03', 2, 6)]",
    "the first five squares with a recursive CTE": "[('1 4 9 16 25',)]",
    "cities with more than one customer": "[('Leeds', 2, 'Ada+Cy')]",
    "products with no paid order": "[('mug',)]",
}
