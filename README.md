# Dosa Restaurant API

REST API for a dosa restaurant. Handles customers, menu items, and orders. Built with Python, FastAPI, and SQLite.

## How it works

The API stores everything in a local SQLite file called `db.sqlite`. There are four tables:

- `customers` holds name and phone (phone is unique per customer)
- `items` holds menu items with a name and price
- `orders` tracks who ordered, when, and any notes
- `order_items` connects orders to items (since one order can have multiple dosas)

Foreign keys tie orders back to customers and order_items back to both orders and items. If you try to create an order for a customer that doesn't exist, the API will reject it.

## Getting started

You need Python 3.10+ installed.

```
pip install fastapi uvicorn
```

Set up the database (only need to do this once):

```
python init_db.py
```

Start the server:

```
uvicorn main:app --reload
```

Go to http://127.0.0.1:8000/docs to test endpoints in the browser.

## API routes

Customers: POST /customers, GET /customers/{id}, PUT /customers/{id}, DELETE /customers/{id}

Items: POST /items, GET /items/{id}, PUT /items/{id}, DELETE /items/{id}

Orders: POST /orders, GET /orders/{id}, PUT /orders/{id}, DELETE /orders/{id}

## Quick test with curl

Add a customer:
```
curl -X POST http://127.0.0.1:8000/customers -H "Content-Type: application/json" -d "{\"name\": \"Vamsi\", \"phone\": \"732-555-1234\"}"
```

Add a menu item:
```
curl -X POST http://127.0.0.1:8000/items -H "Content-Type: application/json" -d "{\"name\": \"Masala Dosa\", \"price\": 10.95}"
```

Place an order (customer 1 ordering item 1):
```
curl -X POST http://127.0.0.1:8000/orders -H "Content-Type: application/json" -d "{\"customer_id\": 1, \"item_ids\": [1], \"notes\": \"extra chutney\"}"
```

Fetch that order back:
```
curl http://127.0.0.1:8000/orders/1
```

## Files

- `init_db.py` -- builds the empty database with all four tables
- `main.py` -- the FastAPI server, all 12 endpoints
- `db.sqlite` -- created when you run init_db.py
