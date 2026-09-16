import random
from datetime import datetime, timedelta
from faker import Faker
import os
import pandas as pd
import json
import time

faker = Faker()
Faker.seed(42)   
random.seed(42)

CATEGORIES = ["Electronics", "Clothing", "Home & Kitchen", "Books", "Sports", "Beauty"]

def generate_customers(n =500):
    customers = []
    for i in range(1, n + 1):
        customers.append({
            "customer_id": i + 1,
            "name": faker.name(),
            "email": faker.email(),
            "address": faker.address(),
            "signup_date": faker.date_between(start_date="-2y", end_date="-1d"),
            "country": faker.country()
        })
    return customers

def generate_products(n=100):
    products = []
    for i in range(1, n + 1):
        products.append({
            "product_id": i ,
            "name": faker.catch_phrase(),
            "category": random.choice(CATEGORIES),
            "price": round(random.uniform(5, 500), 2),
            "description": faker.paragraph(nb_sentences=3),
        })
    return products

STATUSES = ["completed", "pending", "cancelled", "returned"]

def generate_orders_and_items(customers, products, n_orders=3000):
    orders = []
    order_items = []
    item_id=1
    for i in range(1, n_orders + 1):
        customer = random.choice(customers)
        order_date = faker.date_between(start_date="-1y", end_date="now")
        status = random.choices(STATUSES, weights=[70, 15, 10, 5])[0]
        order_id = i
        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date,
            "status": status
        })
        
        for _ in range(random.randint(1, 4)):
            product = random.choice(products)
            order_items.append({
                "item_id": item_id,
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": random.randint(1, 3),
                "price_at_purchase": product["price"],
            })
            item_id += 1

    return orders, order_items

def generate_reviews(customers, products, n=1000):
    reviews = []
    for i in range(1, n + 1):
        reviews.append({
            "review_id": i,
            "product_id": random.choice(products)["product_id"],
            "customer_id": random.choice(customers)["customer_id"],
            "rating": random.choices([1, 2, 3, 4, 5], weights=[5, 5, 15, 35, 40])[0],
            "review_text": faker.paragraph(nb_sentences=2),
        })
    return reviews

##Batch data processing and saving to CSV files

def export_batch(customers, products, orders, order_items, reviews, out_dir="data/batch"):
    os.makedirs(out_dir, exist_ok=True)
    
    customers_df = pd.DataFrame(customers)
    products_df = pd.DataFrame(products)
    orders_df = pd.DataFrame(orders)
    order_items_df = pd.DataFrame(order_items)
    reviews_df = pd.DataFrame(reviews)

    os.makedirs(out_dir, exist_ok=True)
    pd.DataFrame(customers).to_csv(f"{out_dir}/customers.csv", index=False)
    pd.DataFrame(products).to_csv(f"{out_dir}/products.csv", index=False)
    pd.DataFrame(orders).to_csv(f"{out_dir}/orders.csv", index=False)
    pd.DataFrame(order_items).to_csv(f"{out_dir}/order_items.csv", index=False)
    pd.DataFrame(reviews).to_csv(f"{out_dir}/reviews.csv", index=False)
    print(f"Batch data written to {out_dir}/")


##streaming data
def generate_event(products,cutomers):
    event_type=random.choices(["page_view","add_to_cart","purchase"],weights=[70,20,10])[0]
    return{
        "event_id":faker.uuid4(),
        "timestamp":datetime.now().isoformat(),
        "customer_id":random.choice(cutomers)["customer_id"],
        "product_id":random.choice(products)["product_id"],
        "event_type":event_type
    }

def stream_events(products, customers,out_path="data/stream/events.jsonl",delay=1.0):
    os.makedirs(os.path.dirname(out_path),exist_ok=True)
    print(f"Streaming events to {out_path} (Ctrl+C to stop)...")
    with open(out_path,"a") as f:
        while True:
            event=generate_event(products,customers)
            f.write(json.dumps(event)+"\n")
            f.flush()
            print(event)
            time.sleep(delay)


##main function to generate data

import argparse
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="E-commerce fake data generator")
    parser.add_argument("--mode", choices=["batch", "stream"], required=True)
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between stream events")
    args = parser.parse_args()

    customers=generate_customers()
    products=generate_products()

    if args.mode=="batch":
        orders,order_items=generate_orders_and_items(customers,products)
        reviews=generate_reviews(customers,products)
        export_batch(customers,products,orders,order_items,reviews)

    else:
        stream_events(products, customers, delay=args.delay)
