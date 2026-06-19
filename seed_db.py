"""
seed_db.py — Creates demo tables and inserts sample data.
Run once: python seed_db.py
Works with both SQLite (default) and PostgreSQL.
"""

from sqlalchemy import create_engine, text
from app.core.config import ACTIVE_DB_URL

engine = create_engine(ACTIVE_DB_URL)

SEED_SQL = """
-- Customers
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    email       TEXT UNIQUE NOT NULL,
    city        TEXT,
    country     TEXT,
    joined_date DATE
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    category    TEXT,
    price       REAL NOT NULL,
    stock       INTEGER DEFAULT 0
);

-- Orders
CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    order_date  DATE,
    status      TEXT,
    total       REAL
);

-- Order Items
CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY,
    order_id    INTEGER REFERENCES orders(id),
    product_id  INTEGER REFERENCES products(id),
    quantity    INTEGER,
    unit_price  REAL
);
"""

CUSTOMERS = [
    (1, "Alice Johnson",  "alice@email.com",  "New York",    "USA",   "2022-01-15"),
    (2, "Bob Smith",      "bob@email.com",    "London",      "UK",    "2022-03-20"),
    (3, "Carol White",    "carol@email.com",  "Mumbai",      "India", "2022-06-10"),
    (4, "David Lee",      "david@email.com",  "Toronto",     "Canada","2023-01-05"),
    (5, "Eva Martinez",   "eva@email.com",    "Barcelona",   "Spain", "2023-04-18"),
    (6, "Frank Brown",    "frank@email.com",  "Sydney",      "AUS",   "2023-07-22"),
    (7, "Grace Kim",      "grace@email.com",  "Seoul",       "Korea", "2024-01-09"),
    (8, "Henry Wilson",   "henry@email.com",  "Chicago",     "USA",   "2024-02-14"),
]

PRODUCTS = [
    (1, "Laptop Pro",       "Electronics",  1299.99, 50),
    (2, "Wireless Mouse",   "Electronics",    29.99, 200),
    (3, "Mechanical Keyboard","Electronics", 89.99, 150),
    (4, "Standing Desk",    "Furniture",    499.99,  30),
    (5, "Ergonomic Chair",  "Furniture",    349.99,  40),
    (6, "Monitor 27inch",   "Electronics",  399.99,  80),
    (7, "USB-C Hub",        "Electronics",   49.99, 300),
    (8, "Notebook Set",     "Stationery",    12.99, 500),
]

ORDERS = [
    (1,  1, "2024-01-10", "completed", 1329.98),
    (2,  2, "2024-01-15", "completed",  399.99),
    (3,  3, "2024-02-01", "completed",  539.98),
    (4,  4, "2024-02-14", "shipped",    849.98),
    (5,  5, "2024-03-05", "completed", 1299.99),
    (6,  1, "2024-03-20", "completed",   89.99),
    (7,  6, "2024-04-01", "pending",    499.99),
    (8,  7, "2024-04-15", "completed",   79.97),
    (9,  8, "2024-05-01", "completed",  449.98),
    (10, 2, "2024-05-18", "shipped",   1699.98),
]

ORDER_ITEMS = [
    (1,  1, 1, 1, 1299.99), (2,  1, 2, 1,   29.99),
    (3,  2, 6, 1,  399.99),
    (4,  3, 4, 1,  499.99), (5,  3, 2, 2,   29.99),
    (6,  4, 5, 1,  349.99), (7,  4, 3, 1,   89.99), (8,  4, 7, 1, 49.99),
    (9,  5, 1, 1, 1299.99),
    (10, 6, 3, 1,   89.99),
    (11, 7, 4, 1,  499.99),
    (12, 8, 8, 3,   12.99), (13, 8, 2, 1,   29.99), (14, 8, 7, 1, 49.99),
    (15, 9, 5, 1,  349.99), (16, 9, 7, 2,   49.99),
    (17,10, 1, 1, 1299.99), (18,10, 6, 1,  399.99),
]


def seed():
    with engine.connect() as conn:
        # Create tables
        for stmt in SEED_SQL.strip().split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))

        # Clear existing data
        for t in ["order_items", "orders", "products", "customers"]:
            conn.execute(text(f"DELETE FROM {t}"))

        # Insert
        conn.execute(text("INSERT INTO customers VALUES (:a,:b,:c,:d,:e,:f)"),
                     [{"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4],"f":r[5]} for r in CUSTOMERS])
        conn.execute(text("INSERT INTO products VALUES (:a,:b,:c,:d,:e)"),
                     [{"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4]} for r in PRODUCTS])
        conn.execute(text("INSERT INTO orders VALUES (:a,:b,:c,:d,:e)"),
                     [{"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4]} for r in ORDERS])
        conn.execute(text("INSERT INTO order_items VALUES (:a,:b,:c,:d,:e)"),
                     [{"a":r[0],"b":r[1],"c":r[2],"d":r[3],"e":r[4]} for r in ORDER_ITEMS])

        conn.commit()
    print("✅ Database seeded successfully!")
    print(f"   • {len(CUSTOMERS)} customers")
    print(f"   • {len(PRODUCTS)} products")
    print(f"   • {len(ORDERS)} orders")
    print(f"   • {len(ORDER_ITEMS)} order items")


if __name__ == "__main__":
    seed()
