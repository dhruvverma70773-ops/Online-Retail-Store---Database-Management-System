-- Basic SELECT practice: every query answers one small business question.
USE retail_store;
-- 1. Show all customers.
SELECT * FROM customers;
-- 2. Customers from one city.
SELECT full_name, email FROM customers WHERE city = 'Mumbai';
-- 3. Highest-priced products first.
SELECT product_name, price FROM products ORDER BY price DESC LIMIT 10;
-- 4. Search names with LIKE.
SELECT * FROM products WHERE product_name LIKE '%Tea%';
-- 5. Filter a list with IN.
SELECT * FROM customers WHERE city IN ('Delhi','Mumbai','Pune');
-- 6. Find products in a price range.
SELECT product_name, price FROM products WHERE price BETWEEN 100 AND 300;
-- 7. Find employees without a manager.
SELECT employee_name FROM employees WHERE manager_id IS NULL;
-- 8. UPPER, LOWER and CONCAT format names.
SELECT UPPER(full_name) AS upper_name, LOWER(email) AS lower_email,
       CONCAT(full_name, ' - ', city) AS customer_label FROM customers LIMIT 5;
-- 9. SUBSTRING extracts the first three characters.
SELECT product_name, SUBSTRING(product_name,1,3) AS code FROM products LIMIT 10;
-- 10. ROUND makes calculated values readable.
SELECT product_name, ROUND(price * 1.18, 2) AS price_with_tax FROM products LIMIT 10;
-- 11. Date functions extract useful order information.
SELECT order_id, YEAR(order_date) year, MONTH(order_date) month,
       DAYNAME(order_date) weekday FROM orders LIMIT 10;
-- 12. CAST converts an integer to a character value.
SELECT order_id, CAST(total_amount AS CHAR) AS amount_text FROM orders LIMIT 5;
-- 13. CONVERT changes a date to a DATE value.
SELECT order_id, CONVERT(order_date, DATE) AS order_day FROM orders LIMIT 5;
-- 14. DATE_FORMAT creates a report-friendly date.
SELECT order_id, DATE_FORMAT(order_date,'%d-%b-%Y') AS formatted_date FROM orders LIMIT 5;
-- 15. CASE classifies stock.
SELECT product_name, stock_quantity,
       CASE WHEN stock_quantity < reorder_level THEN 'Reorder'
            WHEN stock_quantity < reorder_level*2 THEN 'Watch' ELSE 'Healthy' END stock_status
FROM products;
-- 16. IF classifies order size.
SELECT order_id, IF(total_amount >= 1000,'Large','Regular') AS order_size FROM orders;
-- 17. IFNULL displays a substitute for a missing manager.
SELECT employee_name, IFNULL(manager_id,'Top level') AS manager FROM employees;
-- 18. COALESCE finds the first non-null value.
SELECT full_name, COALESCE(phone,'Phone not supplied') AS contact FROM customers;
-- 19. Count customers by city.
SELECT city, COUNT(*) customer_count FROM customers GROUP BY city;
-- 20. Total and average order value.
SELECT SUM(total_amount) total_sales, AVG(total_amount) average_order,
       MIN(total_amount) smallest_order, MAX(total_amount) largest_order FROM orders;
-- 21. Revenue by order status with HAVING.
SELECT status, COUNT(*) orders, SUM(total_amount) revenue
FROM orders GROUP BY status HAVING SUM(total_amount) > 10000;
-- 22. Average product price by category.
SELECT category_id, COUNT(*) products, AVG(price) average_price
FROM products GROUP BY category_id;
-- 23. Total units sold by product.
SELECT product_id, SUM(quantity) units_sold FROM order_items
GROUP BY product_id ORDER BY units_sold DESC;
-- 24. Payment totals by method.
SELECT payment_method, COUNT(*) payments, SUM(amount) amount
FROM payments GROUP BY payment_method;
-- 25. Monthly order count and sales.
SELECT DATE_FORMAT(order_date,'%Y-%m') month, COUNT(*) orders, SUM(total_amount) sales
FROM orders GROUP BY month ORDER BY month;
