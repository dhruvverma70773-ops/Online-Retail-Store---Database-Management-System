-- Reusable views and MySQL data dictionary examples.
USE retail_store;
CREATE OR REPLACE VIEW v_sales_summary AS
SELECT o.order_id,o.order_date,c.customer_id,c.full_name,
       o.status,o.total_amount
FROM orders o JOIN customers c ON c.customer_id=o.customer_id;

CREATE OR REPLACE VIEW v_customer_orders AS
SELECT c.customer_id,c.full_name,COUNT(o.order_id) order_count,
       COALESCE(SUM(o.total_amount),0) total_spend
FROM customers c LEFT JOIN orders o ON o.customer_id=c.customer_id
GROUP BY c.customer_id,c.full_name;

CREATE OR REPLACE VIEW v_low_stock_products AS
SELECT p.product_id,p.product_name,c.category_name,p.stock_quantity,p.reorder_level
FROM products p JOIN categories c ON c.category_id=p.category_id
WHERE p.stock_quantity < p.reorder_level;

CREATE OR REPLACE VIEW v_product_sales AS
SELECT p.product_id,p.product_name,SUM(oi.quantity) units_sold,
       SUM(oi.quantity*oi.unit_price) revenue
FROM products p LEFT JOIN order_items oi ON oi.product_id=p.product_id
GROUP BY p.product_id,p.product_name;

-- List tables in this database.
SELECT table_name,table_type FROM information_schema.tables
WHERE table_schema='retail_store';
-- List columns and data types.
SELECT table_name,column_name,data_type,is_nullable,column_key
FROM information_schema.columns WHERE table_schema='retail_store'
ORDER BY table_name,ordinal_position;
-- List foreign-key relationships.
SELECT table_name,column_name,referenced_table_name,referenced_column_name
FROM information_schema.key_column_usage
WHERE table_schema='retail_store' AND referenced_table_name IS NOT NULL;
-- EXPLAIN shows whether indexes are used for a common report.
EXPLAIN SELECT * FROM orders WHERE customer_id=1 ORDER BY order_date;
