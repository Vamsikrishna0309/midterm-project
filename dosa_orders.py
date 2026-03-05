import json
import argparse

parser = argparse.ArgumentParser(description="Read dosa restaurant orders and summarize them.")
parser.add_argument("orders_file", help="The JSON file with all the orders")
args = parser.parse_args()

with open(args.orders_file) as f:
    all_orders = json.load(f)

phone_to_name = {order["phone"]: order["name"] for order in all_orders}

with open("customers.json", "w") as f:
    json.dump(phone_to_name, f, indent=4)

print(f"customers.json created with {len(phone_to_name)} customers")

food_summary = {}
for order in all_orders:
    for food_item in order["items"]:
        food_name = food_item["name"]
        food_price = food_item["price"]
        if food_name not in food_summary:
            food_summary[food_name] = {"price": food_price, "orders": 0}
        food_summary[food_name]["orders"] += 1

with open("items.json", "w") as f:
    json.dump(food_summary, f, indent=4)

print(f"items.json created with {len(food_summary)} items")

top_item = max(food_summary, key=lambda x: food_summary[x]["orders"])
print(f"Most popular item: {top_item} with {food_summary[top_item]['orders']} orders")