# Schema description

The design is in third normal form (3NF): each table stores one subject, non-key
columns depend on the whole primary key, and categories/suppliers are not repeated
inside products. `orders` is the order header and `order_items` is the bridge table
between orders and products. A payment belongs to one order.

| Table | Purpose | Important relationships |
|---|---|---|
| customers | Shopper identity and contact | one customer has many orders |
| categories | Product classification | one category has many products |
| suppliers | Product vendors | one supplier has many products |
| products | Sellable items and stock | belongs to category and supplier |
| employees | Staff and manager hierarchy | self-referencing manager_id |
| orders | Order header, customer and total | belongs to customer and employee |
| order_items | Quantity and price at purchase time | belongs to order and product |
| payments | Payment status and method | one payment per order |

The application uses parameterized statements for user-entered values. The SQL
scripts are intentionally separated into DDL, DML, queries, access control, and
views so a student can demonstrate each topic independently.
