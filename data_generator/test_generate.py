from generate import generate_customers, generate_products, generate_orders_and_items


def test_customers_have_required_fields():
    customers = generate_customers(10)
    assert len(customers) == 10
    assert set(customers[0].keys()) == {"customer_id","address" ,"name", "email", "signup_date", "country"}


def test_orders_reference_valid_customers():
    customers = generate_customers(10)
    products = generate_products(10)
    orders, items = generate_orders_and_items(customers, products, n_orders=20)
    valid_customer_ids = {c["customer_id"] for c in customers}
    assert all(o["customer_id"] in valid_customer_ids for o in orders)