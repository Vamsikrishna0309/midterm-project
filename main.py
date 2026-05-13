# Dosa Restaurant API
# This file contains all the API endpoints for customers, items, and orders.

import sqlite3
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

DB = "db.sqlite"


def connect():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA foreign_keys = ON")
    return c


class NewCustomer(BaseModel):
    name: str
    phone: str

class NewItem(BaseModel):
    name: str
    price: float

class NewOrder(BaseModel):
    customer_id: int
    item_ids: list[int]
    notes: str = ""
    timestamp: int = None


# ---------- customers ----------

@app.post("/customers", status_code=201)
def add_customer(data: NewCustomer):
    if not data.name.strip():
        raise HTTPException(422, "name is required")
    if not data.phone.strip():
        raise HTTPException(422, "phone is required")
    db = connect()
    try:
        cur = db.execute(
            "INSERT INTO customers (name, phone) VALUES (?, ?)",
            (data.name.strip(), data.phone.strip())
        )
        db.commit()
        cid = cur.lastrowid
    except sqlite3.IntegrityError:
        db.close()
        raise HTTPException(409, "that phone number is already in use")
    db.close()
    return {"id": cid, "name": data.name.strip(), "phone": data.phone.strip()}


@app.get("/customers/{cid}")
def read_customer(cid: int):
    db = connect()
    row = db.execute("SELECT * FROM customers WHERE id = ?", (cid,)).fetchone()
    db.close()
    if row is None:
        raise HTTPException(404, f"customer {cid} not found")
    return dict(row)


@app.put("/customers/{cid}")
def edit_customer(cid: int, data: NewCustomer):
    if not data.name.strip():
        raise HTTPException(422, "name is required")
    if not data.phone.strip():
        raise HTTPException(422, "phone is required")
    db = connect()
    check = db.execute("SELECT id FROM customers WHERE id = ?", (cid,)).fetchone()
    if check is None:
        db.close()
        raise HTTPException(404, f"customer {cid} not found")
    try:
        db.execute(
            "UPDATE customers SET name = ?, phone = ? WHERE id = ?",
            (data.name.strip(), data.phone.strip(), cid)
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        raise HTTPException(409, "that phone number is already in use")
    db.close()
    return {"id": cid, "name": data.name.strip(), "phone": data.phone.strip()}


@app.delete("/customers/{cid}")
def remove_customer(cid: int):
    db = connect()
    n = db.execute("DELETE FROM customers WHERE id = ?", (cid,)).rowcount
    db.commit()
    db.close()
    if n == 0:
        raise HTTPException(404, f"customer {cid} not found")
    return {"detail": f"customer {cid} deleted"}


# ---------- items ----------

@app.post("/items", status_code=201)
def add_item(data: NewItem):
    if not data.name.strip():
        raise HTTPException(422, "name is required")
    if data.price < 0:
        raise HTTPException(422, "price must be zero or more")
    db = connect()
    try:
        cur = db.execute(
            "INSERT INTO items (name, price) VALUES (?, ?)",
            (data.name.strip(), data.price)
        )
        db.commit()
        iid = cur.lastrowid
    except sqlite3.IntegrityError:
        db.close()
        raise HTTPException(409, "an item with that name already exists")
    db.close()
    return {"id": iid, "name": data.name.strip(), "price": data.price}


@app.get("/items/{iid}")
def read_item(iid: int):
    db = connect()
    row = db.execute("SELECT * FROM items WHERE id = ?", (iid,)).fetchone()
    db.close()
    if row is None:
        raise HTTPException(404, f"item {iid} not found")
    return dict(row)


@app.put("/items/{iid}")
def edit_item(iid: int, data: NewItem):
    if not data.name.strip():
        raise HTTPException(422, "name is required")
    if data.price < 0:
        raise HTTPException(422, "price must be zero or more")
    db = connect()
    check = db.execute("SELECT id FROM items WHERE id = ?", (iid,)).fetchone()
    if check is None:
        db.close()
        raise HTTPException(404, f"item {iid} not found")
    try:
        db.execute(
            "UPDATE items SET name = ?, price = ? WHERE id = ?",
            (data.name.strip(), data.price, iid)
        )
        db.commit()
    except sqlite3.IntegrityError:
        db.close()
        raise HTTPException(409, "an item with that name already exists")
    db.close()
    return {"id": iid, "name": data.name.strip(), "price": data.price}


@app.delete("/items/{iid}")
def remove_item(iid: int):
    db = connect()
    n = db.execute("DELETE FROM items WHERE id = ?", (iid,)).rowcount
    db.commit()
    db.close()
    if n == 0:
        raise HTTPException(404, f"item {iid} not found")
    return {"detail": f"item {iid} deleted"}


# ---------- orders ----------

@app.post("/orders", status_code=201)
def add_order(data: NewOrder):
    if not data.item_ids:
        raise HTTPException(422, "need at least one item")
    ts = data.timestamp if data.timestamp else int(time.time())
    db = connect()
    cust = db.execute("SELECT id FROM customers WHERE id = ?", (data.customer_id,)).fetchone()
    if cust is None:
        db.close()
        raise HTTPException(404, f"customer {data.customer_id} does not exist")
    for x in data.item_ids:
        found = db.execute("SELECT id FROM items WHERE id = ?", (x,)).fetchone()
        if found is None:
            db.close()
            raise HTTPException(404, f"item {x} does not exist")
    cur = db.execute(
        "INSERT INTO orders (customer_id, timestamp, notes) VALUES (?, ?, ?)",
        (data.customer_id, ts, data.notes)
    )
    oid = cur.lastrowid
    for x in data.item_ids:
        db.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (oid, x))
    db.commit()
    db.close()
    return {"id": oid, "customer_id": data.customer_id, "timestamp": ts, "notes": data.notes, "item_ids": data.item_ids}


@app.get("/orders/{oid}")
def read_order(oid: int):
    db = connect()
    row = db.execute("SELECT * FROM orders WHERE id = ?", (oid,)).fetchone()
    if row is None:
        db.close()
        raise HTTPException(404, f"order {oid} not found")
    linked = db.execute("SELECT item_id FROM order_items WHERE order_id = ?", (oid,)).fetchall()
    db.close()
    return {
        "id": row["id"],
        "customer_id": row["customer_id"],
        "timestamp": row["timestamp"],
        "notes": row["notes"],
        "item_ids": [r["item_id"] for r in linked]
    }


@app.put("/orders/{oid}")
def edit_order(oid: int, data: NewOrder):
    if not data.item_ids:
        raise HTTPException(422, "need at least one item")
    ts = data.timestamp if data.timestamp else int(time.time())
    db = connect()
    existing = db.execute("SELECT id FROM orders WHERE id = ?", (oid,)).fetchone()
    if existing is None:
        db.close()
        raise HTTPException(404, f"order {oid} not found")
    cust = db.execute("SELECT id FROM customers WHERE id = ?", (data.customer_id,)).fetchone()
    if cust is None:
        db.close()
        raise HTTPException(404, f"customer {data.customer_id} does not exist")
    for x in data.item_ids:
        found = db.execute("SELECT id FROM items WHERE id = ?", (x,)).fetchone()
        if found is None:
            db.close()
            raise HTTPException(404, f"item {x} does not exist")
    db.execute(
        "UPDATE orders SET customer_id = ?, timestamp = ?, notes = ? WHERE id = ?",
        (data.customer_id, ts, data.notes, oid)
    )
    db.execute("DELETE FROM order_items WHERE order_id = ?", (oid,))
    for x in data.item_ids:
        db.execute("INSERT INTO order_items (order_id, item_id) VALUES (?, ?)", (oid, x))
    db.commit()
    db.close()
    return {"id": oid, "customer_id": data.customer_id, "timestamp": ts, "notes": data.notes, "item_ids": data.item_ids}


@app.delete("/orders/{oid}")
def remove_order(oid: int):
    db = connect()
    existing = db.execute("SELECT id FROM orders WHERE id = ?", (oid,)).fetchone()
    if existing is None:
        db.close()
        raise HTTPException(404, f"order {oid} not found")
    db.execute("DELETE FROM order_items WHERE order_id = ?", (oid,))
    db.execute("DELETE FROM orders WHERE id = ?", (oid,))
    db.commit()
    db.close()
    return {"detail": f"order {oid} deleted"}
