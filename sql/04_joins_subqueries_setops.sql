-- Joins, subqueries and set operators: business questions for viva practice.
USE retail_store;
-- 1. INNER JOIN products to categories.
SELECT p.product_name, c.category_name FROM products p
INNER JOIN categories c ON c.category_id=p.category_id;
-- 2. LEFT JOIN keeps customers even when they have no orders.
SELECT c.full_name, o.order_id FROM customers c
LEFT JOIN orders o ON o.customer_id=c.customer_id;
-- 3. RIGHT JOIN keeps every category.
SELECT p.product_name, c.category_name FROM products p
RIGHT JOIN categories c ON c.category_id=p.category_id;
-- 4. SELF JOIN shows employees and their managers.
SELECT e.employee_name employee, m.employee_name manager FROM employees e
LEFT JOIN employees m ON m.employee_id=e.manager_id;
-- 5. Four-table join creates a sales detail report.
SELECT o.order_id,c.full_name,p.product_name,oi.quantity,oi.unit_price
FROM orders o JOIN customers c ON c.customer_id=o.customer_id
JOIN order_items oi ON oi.order_id=o.order_id
JOIN products p ON p.product_id=oi.product_id;
-- 6. Top five customers by spend.
SELECT c.full_name,SUM(o.total_amount) spend FROM customers c JOIN orders o
ON o.customer_id=c.customer_id GROUP BY c.customer_id,c.full_name
ORDER BY spend DESC LIMIT 5;
-- 7. Monthly sales.
SELECT DATE_FORMAT(order_date,'%Y-%m') month,SUM(total_amount) sales
FROM orders GROUP BY month ORDER BY month;
-- 8. Best-selling products.
SELECT p.product_name,SUM(oi.quantity) units FROM products p JOIN order_items oi
ON oi.product_id=p.product_id GROUP BY p.product_id,p.product_name ORDER BY units DESC;
-- 9. Low-stock products using a WHERE subquery.
SELECT product_name,stock_quantity FROM products
WHERE stock_quantity < (SELECT AVG(stock_quantity) FROM products);
-- 10. Products priced above the overall average (IN subquery).
SELECT product_name,price FROM products
WHERE product_id IN (SELECT product_id FROM products WHERE price > (SELECT AVG(price) FROM products));
-- 11. Correlated subquery: products above their category average.
SELECT p.product_name,p.price FROM products p
WHERE p.price > (SELECT AVG(p2.price) FROM products p2 WHERE p2.category_id=p.category_id);
-- 12. EXISTS finds customers who have at least one order.
SELECT c.full_name FROM customers c
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id);
-- 13. Customers who never ordered.
SELECT c.full_name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id=c.customer_id);
-- 14. Derived table (subquery in FROM) finds busy customers.
SELECT x.full_name,x.order_count FROM
(SELECT c.full_name,COUNT(o.order_id) order_count FROM customers c
JOIN orders o ON o.customer_id=c.customer_id GROUP BY c.customer_id,c.full_name) x
WHERE x.order_count >= 3;
-- 15. UNION returns customers and employees in one contact list.
SELECT full_name AS person FROM customers
UNION
SELECT employee_name FROM employees;
-- 16. UNION ALL deliberately preserves duplicate names.
SELECT city FROM customers WHERE city IN ('Delhi','Mumbai')
UNION ALL SELECT city FROM suppliers WHERE city IN ('Delhi','Mumbai');
-- 17. MySQL 8 has no INTERSECT in older installations: emulate it with EXISTS.
SELECT DISTINCT c.city FROM customers c
WHERE EXISTS (SELECT 1 FROM suppliers s WHERE s.city=c.city);
-- 18. MySQL 8 has no EXCEPT in older installations: emulate with NOT EXISTS.
SELECT DISTINCT c.city FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM suppliers s WHERE s.city=c.city);
-- 19. Category-wise revenue.
SELECT c.category_name,SUM(oi.quantity*oi.unit_price) revenue
FROM categories c JOIN products p ON p.category_id=c.category_id
JOIN order_items oi ON oi.product_id=p.product_id
GROUP BY c.category_id,c.category_name ORDER BY revenue DESC;
-- 20. Payment method share as a percentage.
SELECT payment_method,COUNT(*) payments,
ROUND(COUNT(*)*100/(SELECT COUNT(*) FROM payments),2) percentage
FROM payments GROUP BY payment_method;
