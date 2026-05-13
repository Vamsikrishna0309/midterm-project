import sqlite3
import os

DB_NAME = "db.sqlite"

tables = [
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price REAL NOT NULL CHECK(price >= 0)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        notes TEXT DEFAULT '',
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        order_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        PRIMARY KEY (order_id, item_id),
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    )
    """
]

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print(f"Removed old {DB_NAME}")

connection = sqlite3.connect(DB_NAME)
connection.execute("PRAGMA foreign_keys = ON")

for sql in tables:
    connection.execute(sql)

connection.commit()
connection.close()

print(f"Created {DB_NAME} with 4 tables")
