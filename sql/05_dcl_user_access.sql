-- DCL demo. Run as a MySQL administrator, not as the application user.
USE retail_store;
-- The Streamlit app connects through Docker's published port, so MySQL sees
-- the client as a Docker-network host rather than as localhost.
CREATE USER IF NOT EXISTS 'retail_app'@'%' IDENTIFIED BY 'retail_app_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON retail_store.* TO 'retail_app'@'%';
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Admin@12345';
CREATE USER IF NOT EXISTS 'sales_user'@'localhost' IDENTIFIED BY 'Sales@12345';
CREATE USER IF NOT EXISTS 'readonly_user'@'localhost' IDENTIFIED BY 'ReadOnly@12345';
GRANT ALL PRIVILEGES ON retail_store.* TO 'admin_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON retail_store.customers TO 'sales_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON retail_store.orders TO 'sales_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON retail_store.order_items TO 'sales_user'@'localhost';
GRANT SELECT, INSERT ON retail_store.payments TO 'sales_user'@'localhost';
GRANT SELECT ON retail_store.* TO 'readonly_user'@'localhost';
GRANT DELETE ON retail_store.customers TO 'sales_user'@'localhost';
FLUSH PRIVILEGES;
-- Expected: admin has ALL; sales_user can sell but cannot DELETE customers;
-- readonly_user can SELECT only. Run these to demonstrate the result:
SHOW GRANTS FOR 'admin_user'@'localhost';
SHOW GRANTS FOR 'sales_user'@'localhost';
SHOW GRANTS FOR 'readonly_user'@'localhost';
