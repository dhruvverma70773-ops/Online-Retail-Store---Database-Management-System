"""Export joined datasets for Tableau or Excel."""

from pathlib import Path

from db import query_df


OUTPUT = Path(__file__).parents[1] / "data" / "export"
OUTPUT.mkdir(parents=True, exist_ok=True)

query_df("""SELECT o.order_id, o.order_date, c.customer_id, c.full_name, c.city,
                   p.product_id, p.product_name, cat.category_name, oi.quantity,
                   oi.unit_price, oi.quantity * oi.unit_price AS line_total
            FROM orders o JOIN customers c ON c.customer_id=o.customer_id
            JOIN order_items oi ON oi.order_id=o.order_id
            JOIN products p ON p.product_id=oi.product_id
            JOIN categories cat ON cat.category_id=p.category_id""").to_csv(
                OUTPUT / "sales_data.csv", index=False
            )
query_df("SELECT * FROM customers").to_csv(OUTPUT / "customers.csv", index=False)
query_df("SELECT * FROM products").to_csv(OUTPUT / "products.csv", index=False)
print(f"Exports written to {OUTPUT}")
