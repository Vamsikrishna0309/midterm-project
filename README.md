# Dosa Restaurant Order Analyzer

## What this does
This script reads a JSON file of restaurant orders and creates two summary files:
- `customers.json` — a list of customers with their phone number and name
- `items.json` — a list of menu items with their price and how many times they were ordered

## How to run it
```bash
python dosa_orders.py example_orders.json
```

Just pass in the orders file as the argument and it will generate both output files automatically.

## What we get
After running the script we will see two new files in our folder:

`customers.json` looks like this:
```json
{
    "609-555-0124": "Karl",
    "732-555-1234": "Mike"
}
```

`items.json` looks like this:
```json
{
    "Butter Masala Dosa": {
        "price": 12.95,
        "orders": 52
    }
}
```

## Requirements
- Python 3
- No extra libraries needed, everything used is built into Python
