-- Sample Indian retail data. Run after 01_schema_ddl.sql.
USE retail_store;

INSERT INTO categories (category_name, description) VALUES
('Groceries','Staples and packaged food'),('Beverages','Tea, coffee and drinks'),
('Personal Care','Bath and grooming'),('Home Care','Cleaning and household'),
('Electronics','Small consumer electronics'),('Stationery','School and office supplies'),
('Kitchen','Cookware and kitchen tools'),('Snacks','Packaged snacks'),
('Baby Care','Products for infants'),('Apparel','Everyday clothing');

INSERT INTO suppliers (supplier_name, contact_email, city) VALUES
('Mumbai Fresh Distributors','mumbai@suppliers.in','Mumbai'),
('Delhi Daily Needs','delhi@suppliers.in','New Delhi'),
('Bengaluru Tech Hub','blr@suppliers.in','Bengaluru'),
('Chennai Home Mart','chennai@suppliers.in','Chennai'),
('Hyderabad Wholesale','hyd@suppliers.in','Hyderabad'),
('Pune Consumer Goods','pune@suppliers.in','Pune'),
('Kolkata Essentials','kolkata@suppliers.in','Kolkata'),
('Jaipur Traders','jaipur@suppliers.in','Jaipur');

INSERT INTO customers (full_name,email,phone,city) VALUES
('Aarav Sharma','aarav.sharma@example.in','9000000001','Delhi'),
('Aditi Iyer','aditi.iyer@example.in','9000000002','Chennai'),
('Arjun Mehta','arjun.mehta@example.in','9000000003','Mumbai'),
('Ananya Rao','ananya.rao@example.in','9000000004','Bengaluru'),
('Kabir Singh','kabir.singh@example.in','9000000005','Jaipur'),
('Diya Patel','diya.patel@example.in','9000000006','Ahmedabad'),
('Rohan Das','rohan.das@example.in','9000000007','Kolkata'),
('Meera Nair','meera.nair@example.in','9000000008','Kochi'),
('Vivaan Gupta','vivaan.gupta@example.in','9000000009','Lucknow'),
('Ishita Joshi','ishita.joshi@example.in','9000000010','Pune'),
('Advik Shah','advik.shah@example.in','9000000011','Surat'),
('Saanvi Kapoor','saanvi.kapoor@example.in','9000000012','Delhi'),
('Reyansh Verma','reyansh.verma@example.in','9000000013','Noida'),
('Myra Bansal','myra.bansal@example.in','9000000014','Chandigarh'),
('Vihaan Kulkarni','vihaan.kulkarni@example.in','9000000015','Pune'),
('Navya Menon','navya.menon@example.in','9000000016','Kochi'),
('Atharv Sethi','atharv.sethi@example.in','9000000017','Gurugram'),
('Sara Khan','sara.khan@example.in','9000000018','Hyderabad'),
('Dhruv Malhotra','dhruv.malhotra@example.in','9000000019','Mumbai'),
('Tara Roy','tara.roy@example.in','9000000020','Kolkata'),
('Yash Thakur','yash.thakur@example.in','9000000021','Shimla'),
('Kiara Sood','kiara.sood@example.in','9000000022','Amritsar'),
('Ayaan Chawla','ayaan.chawla@example.in','9000000023','Indore'),
('Riya Ghosh','riya.ghosh@example.in','9000000024','Kolkata'),
('Kunal Reddy','kunal.reddy@example.in','9000000025','Hyderabad'),
('Nisha Pillai','nisha.pillai@example.in','9000000026','Bengaluru'),
('Manav Jain','manav.jain@example.in','9000000027','Jaipur'),
('Pihu Agrawal','pihu.agrawal@example.in','9000000028','Bhopal'),
('Om Prakash','om.prakash@example.in','9000000029','Patna'),
('Ira Bose','ira.bose@example.in','9000000030','Bhubaneswar');

-- Recursive sequences keep the teaching script short while producing 50 products.
INSERT INTO products (product_name,category_id,supplier_id,price,stock_quantity,reorder_level)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i+1 FROM n WHERE i < 50)
SELECT CONCAT(CASE MOD(i-1,10)
 WHEN 0 THEN 'Basmati Rice' WHEN 1 THEN 'Assam Tea' WHEN 2 THEN 'Neem Face Wash'
 WHEN 3 THEN 'Liquid Detergent' WHEN 4 THEN 'Bluetooth Speaker' WHEN 5 THEN 'Notebook'
 WHEN 6 THEN 'Steel Cookware' WHEN 7 THEN 'Masala Chips' WHEN 8 THEN 'Baby Lotion'
 ELSE 'Cotton T-Shirt' END, ' ', i),
MOD(i-1,10)+1, MOD(i-1,8)+1, ROUND(45 + i*13.75,2), 20 + MOD(i*7,81), 10 FROM n;

INSERT INTO employees (employee_name,role_name,email,hire_date) VALUES
('Neha Joshi','Manager','neha.joshi@retail.in','2022-04-01'),
('Sameer Khan','Sales Executive','sameer.khan@retail.in','2023-06-15'),
('Lakshmi Rao','Sales Executive','lakshmi.rao@retail.in','2024-01-10');
UPDATE employees SET manager_id=1 WHERE employee_id IN (2,3);

-- Generate exactly 100 orders, each with a realistic date and status.
INSERT INTO orders (customer_id,employee_id,order_date,status,total_amount)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i+1 FROM n WHERE i < 100)
SELECT MOD(i-1,30)+1, MOD(i-1,3)+1,
       DATE_ADD('2025-01-01', INTERVAL MOD(i*3,365) DAY) + INTERVAL 10 HOUR,
       CASE MOD(i,5) WHEN 0 THEN 'Delivered' WHEN 1 THEN 'Shipped'
       WHEN 2 THEN 'Packed' WHEN 3 THEN 'Placed' ELSE 'Delivered' END, 0 FROM n;

-- Generate 250 order lines (2 or 3 different products per order).
INSERT INTO order_items (order_id,product_id,quantity,unit_price)
WITH RECURSIVE n AS (SELECT 1 AS i UNION ALL SELECT i+1 FROM n WHERE i < 250)
SELECT MOD(i-1,100)+1, MOD((i-1)*7 + FLOOR((i-1)/100)*11,50)+1, MOD(i,4)+1,
       (SELECT price FROM products WHERE product_id=MOD((i-1)*7 + FLOOR((i-1)/100)*11,50)+1) FROM n;
UPDATE orders o SET total_amount = (SELECT SUM(quantity*unit_price) FROM order_items oi WHERE oi.order_id=o.order_id);

INSERT INTO payments (order_id,payment_method,amount,payment_status)
SELECT order_id, CASE MOD(order_id,4) WHEN 0 THEN 'UPI' WHEN 1 THEN 'Card'
       WHEN 2 THEN 'Net Banking' ELSE 'Cash on Delivery' END,
       total_amount, 'Completed' FROM orders;

-- DML examples (shown as comments so rerunning seed data stays safe).
-- UPDATE products SET price = price * 1.05 WHERE category_id = 1;
-- DELETE FROM customers WHERE customer_id = 9999;
