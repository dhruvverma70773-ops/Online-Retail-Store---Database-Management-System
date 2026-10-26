"""Online Retail Store analytics, CRUD and order management application."""

from datetime import date
from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st
from mysql.connector import Error

from db import get_connection, query_df

st.set_page_config(
    page_title="Retail Store Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #102a43 0%, #163d5c 100%);
    }
    [data-testid="stSidebar"] * { color: #f7fbff; }
    [data-testid="stMetric"] {
        background: #f7fafc;
        border: 1px solid #e2e8f0;
        padding: 14px 16px;
        border-radius: 12px;
    }
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #172b4d !important;
    }
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-weight: 700;
    }
    .hero {
        padding: 1.4rem 1.6rem;
        border-radius: 16px;
        color: white;
        background: linear-gradient(115deg, #0f766e, #2563eb);
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2rem; }
    .hero p { margin: .35rem 0 0; opacity: .9; }
    </style>
    """,
    unsafe_allow_html=True,
)


def run_write(sql: str, params: tuple) -> None:
    """Run a write inside the application's standard error boundary."""
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(sql, params)
        connection.commit()


def load_options(table: str, id_column: str, label_column: str) -> pd.DataFrame:
    """Load safe, fixed table options used by selectboxes."""
    return query_df(f"SELECT {id_column}, {label_column} FROM {table} ORDER BY {label_column}")


def money(value: object) -> str:
    """Format database numeric values consistently in the UI."""
    return f"₹{float(value or 0):,.0f}"


def dashboard() -> None:
    st.markdown(
        '<div class="hero"><h1>🛍️ Retail Store Analytics</h1>'
        "<p>Live sales, customer, order and inventory performance at a glance.</p></div>",
        unsafe_allow_html=True,
    )
    try:
        bounds = query_df(
            "SELECT MIN(DATE(order_date)) AS first_day, MAX(DATE(order_date)) AS last_day "
            "FROM orders"
        ).iloc[0]
        if pd.isna(bounds["first_day"]):
            st.info("No orders found yet. Add data through the Orders page to see analytics.")
            return
        start_default = pd.to_datetime(bounds["first_day"]).date()
        end_default = pd.to_datetime(bounds["last_day"]).date()
        with st.container():
            filter_col, status_col = st.columns([2, 1])
            with filter_col:
                date_range = st.date_input(
                    "Analysis period", (start_default, end_default),
                    min_value=start_default, max_value=end_default,
                )
            with status_col:
                status = st.selectbox(
                    "Order status", ["All", "Placed", "Packed", "Shipped", "Delivered", "Cancelled"]
                )
        if not isinstance(date_range, tuple) or len(date_range) != 2:
            st.warning("Please select a start and end date.")
            return
        start_date, end_date = date_range
        status_filter = "" if status == "All" else " AND o.status = %s"
        params: tuple = (start_date, end_date)
        if status_filter:
            params += (status,)
        metrics = query_df(
            """SELECT
                COUNT(DISTINCT o.customer_id) AS customers,
                COUNT(DISTINCT o.order_id) AS orders,
                COALESCE(SUM(o.total_amount), 0) AS sales,
                COALESCE(AVG(o.total_amount), 0) AS average_order
               FROM orders o
               WHERE DATE(o.order_date) BETWEEN %s AND %s"""
            + status_filter,
            params,
        ).iloc[0]
        low_stock = query_df(
            "SELECT COUNT(*) AS count FROM products WHERE stock_quantity < reorder_level"
        ).iloc[0]["count"]
        a, b, c, d, e = st.columns(5)
        a.metric("Customers", int(metrics["customers"]))
        b.metric("Orders", int(metrics["orders"]))
        c.metric("Revenue", money(metrics["sales"]))
        d.metric("Average order", money(metrics["average_order"]))
        e.metric("Low stock", int(low_stock), delta="Restock soon", delta_color="inverse")

        left, right = st.columns(2)
        with left:
            top = query_df(
                """SELECT p.product_name, SUM(oi.quantity) AS units
                   FROM order_items oi JOIN products p ON p.product_id = oi.product_id
                   JOIN orders o ON o.order_id = oi.order_id
                   WHERE DATE(o.order_date) BETWEEN %s AND %s"""
                + status_filter
                + """ GROUP BY p.product_id, p.product_name
                   ORDER BY units DESC LIMIT 5"""
                , params,
            )
            st.subheader("Top-selling products")
            if top.empty:
                st.info("No product sales for this selection.")
            else:
                chart = px.bar(top, x="units", y="product_name", orientation="h",
                               color="units", color_continuous_scale="teal")
                chart.update_layout(showlegend=False, xaxis_title="Units sold", yaxis_title="")
                st.plotly_chart(chart, width="stretch")
        with right:
            monthly = query_df(
                """SELECT DATE_FORMAT(order_date, '%Y-%m') AS month,
                          SUM(total_amount) AS sales
                   FROM orders o
                   WHERE DATE(o.order_date) BETWEEN %s AND %s"""
                + status_filter
                + " GROUP BY month ORDER BY month",
                params,
            )
            st.subheader("Revenue trend")
            if monthly.empty:
                st.info("No revenue for this selection.")
            else:
                chart = px.area(monthly, x="month", y="sales", markers=True)
                chart.update_traces(line_color="#0f766e", fillcolor="rgba(15,118,110,.18)")
                chart.update_layout(yaxis_title="Revenue (₹)", xaxis_title="")
                st.plotly_chart(chart, width="stretch")

        st.subheader("Inventory watchlist")
        inventory = query_df(
            """SELECT p.product_name, c.category_name, p.stock_quantity, p.reorder_level,
                      CASE WHEN p.stock_quantity = 0 THEN 'Out of stock'
                           ELSE 'Reorder soon' END AS status
               FROM products p JOIN categories c ON c.category_id = p.category_id
               WHERE p.stock_quantity < p.reorder_level
               ORDER BY p.stock_quantity, p.product_name LIMIT 10"""
        )
        if inventory.empty:
            st.success("All products are above their reorder level.")
        else:
            st.dataframe(inventory, width="stretch", hide_index=True)
    except Error as exc:
        st.error(f"Database error: {exc}")


def customers_page() -> None:
    st.title("👥 Customers")
    st.caption("Manage customer records and keep contact information up to date.")
    try:
        data = query_df("SELECT * FROM customers ORDER BY customer_id")
        st.dataframe(data, width="stretch")
        with st.expander("Add customer"):
            with st.form("add_customer"):
                name = st.text_input("Full name")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                city = st.text_input("City")
                if st.form_submit_button("Create"):
                    if not name.strip() or "@" not in email:
                        st.error("Enter a name and a valid email.")
                    else:
                        run_write(
                            """INSERT INTO customers
                               (full_name, email, phone, city) VALUES (%s, %s, %s, %s)""",
                            (name.strip(), email.strip(), phone.strip(), city.strip()),
                        )
                        st.success("Customer created.")
                        st.rerun()
        with st.expander("Update or delete customer"):
            if data.empty:
                st.info("No customers found.")
                return
            selected = st.selectbox("Customer", data["customer_id"].tolist())
            row = data[data.customer_id == selected].iloc[0]
            with st.form("edit_customer"):
                name = st.text_input("Name", value=row.full_name)
                city = st.text_input("City", value=row.city or "")
                col1, col2 = st.columns(2)
                update = col1.form_submit_button("Update")
                delete = col2.form_submit_button("Delete")
                if update:
                    run_write("UPDATE customers SET full_name=%s, city=%s WHERE customer_id=%s",
                              (name.strip(), city.strip(), int(selected)))
                    st.success("Customer updated.")
                    st.rerun()
                if delete:
                    run_write("DELETE FROM customers WHERE customer_id=%s", (int(selected),))
                    st.success("Customer deleted.")
                    st.rerun()
    except Error as exc:
        st.error(f"Database error: {exc}")


def products_page() -> None:
    st.title("📦 Products & Inventory")
    st.caption("Maintain catalog pricing, categories, suppliers and stock levels.")
    try:
        data = query_df(
            """SELECT p.product_id, p.product_name, p.price, p.stock_quantity,
                      c.category_name, s.supplier_name
               FROM products p JOIN categories c ON c.category_id=p.category_id
               JOIN suppliers s ON s.supplier_id=p.supplier_id ORDER BY p.product_id"""
        )
        st.dataframe(data, width="stretch")
        categories = load_options("categories", "category_id", "category_name")
        suppliers = load_options("suppliers", "supplier_id", "supplier_name")
        category_ids = categories["category_id"].tolist()
        supplier_ids = suppliers["supplier_id"].tolist()
        with st.expander("Add product"):
            if not category_ids or not supplier_ids:
                st.warning(
                    "Product add nahi ho sakta: pehle database me category aur supplier records load karein."
                )
            else:
                with st.form("add_product"):
                    name = st.text_input("Product name")
                    price = st.number_input("Price", min_value=0.01, value=100.0)
                    stock = st.number_input("Opening stock", min_value=0, value=10, step=1)
                    category = st.selectbox(
                        "Category", category_ids,
                        format_func=lambda x: categories.loc[
                            categories.category_id == x, "category_name"
                        ].iloc[0],
                    )
                    supplier = st.selectbox(
                        "Supplier", supplier_ids,
                        format_func=lambda x: suppliers.loc[
                            suppliers.supplier_id == x, "supplier_name"
                        ].iloc[0],
                    )
                    if st.form_submit_button("Create"):
                        if not name.strip():
                            st.error("Product name is required.")
                        elif category is None or supplier is None:
                            st.error("Select a category and supplier.")
                        else:
                            run_write("""INSERT INTO products
                                (product_name, category_id, supplier_id, price, stock_quantity)
                                VALUES (%s, %s, %s, %s, %s)""",
                                      (name.strip(), int(category), int(supplier), price, int(stock)))
                            st.success("Product created.")
                            st.rerun()
        with st.expander("Update or delete product"):
            if data.empty:
                st.info("No products found.")
                return
            selected = st.selectbox("Product", data.product_id.tolist())
            row = data[data.product_id == selected].iloc[0]
            with st.form("edit_product"):
                price = st.number_input("Price", min_value=0.01, value=float(row.price))
                stock = st.number_input("Stock", min_value=0, value=int(row.stock_quantity))
                col1, col2 = st.columns(2)
                update = col1.form_submit_button("Update")
                delete = col2.form_submit_button("Delete")
                if update:
                    run_write("UPDATE products SET price=%s, stock_quantity=%s WHERE product_id=%s",
                              (price, stock, int(selected)))
                    st.success("Product updated.")
                    st.rerun()
                if delete:
                    run_write("DELETE FROM products WHERE product_id=%s", (int(selected),))
                    st.success("Product deleted.")
                    st.rerun()
    except Error as exc:
        st.error(f"Database error: {exc}")


def order_page() -> None:
    st.title("🧾 Place an order")
    st.caption("Create an order transaction. Stock is locked and reduced automatically.")
    try:
        customers = load_options("customers", "customer_id", "full_name")
        products = query_df("SELECT product_id, product_name, price, stock_quantity FROM products WHERE stock_quantity > 0 ORDER BY product_name")
        if customers.empty or products.empty:
            st.warning("Customers and in-stock products are required.")
            return
        customer = st.selectbox("Customer", customers.customer_id,
                                format_func=lambda x: customers.loc[customers.customer_id == x, "full_name"].iloc[0])
        selected = st.multiselect("Products", products.product_id,
                                  format_func=lambda x: products.loc[products.product_id == x, "product_name"].iloc[0])
        payment_method = st.selectbox("Payment method", ["UPI", "Card", "Net Banking", "Cash on Delivery"])
        quantities = {
            pid: st.number_input(
                f"Quantity — {products.loc[products.product_id == pid, 'product_name'].iloc[0]}",
                1, int(products.loc[products.product_id == pid, "stock_quantity"].iloc[0]), 1,
                key=f"qty_{pid}",
            )
            for pid in selected
        }
        if selected:
            total_preview = sum(
                products.loc[products.product_id == pid, "price"].iloc[0] * quantity
                for pid, quantity in quantities.items()
            )
            st.info(f"Order total: **{money(total_preview)}**")
        if st.button("Place order", type="primary"):
            if not selected:
                st.error("Select at least one product.")
                return
            with get_connection() as connection:
                cursor = connection.cursor()
                try:
                    total = Decimal("0")
                    for pid, quantity in quantities.items():
                        cursor.execute("SELECT price, stock_quantity FROM products WHERE product_id=%s FOR UPDATE", (pid,))
                        price, stock = cursor.fetchone()
                        if quantity > stock:
                            raise ValueError(f"Insufficient stock for product {pid}.")
                        total += price * quantity
                    cursor.execute("INSERT INTO orders (customer_id, total_amount) VALUES (%s, %s)",
                                   (int(customer), total))
                    order_id = cursor.lastrowid
                    for pid, quantity in quantities.items():
                        cursor.execute("SELECT price FROM products WHERE product_id=%s", (pid,))
                        price = cursor.fetchone()[0]
                        cursor.execute("""INSERT INTO order_items
                            (order_id, product_id, quantity, unit_price) VALUES (%s,%s,%s,%s)""",
                                      (order_id, pid, quantity, price))
                        cursor.execute("UPDATE products SET stock_quantity=stock_quantity-%s WHERE product_id=%s",
                                       (quantity, pid))
                    cursor.execute("""INSERT INTO payments
                        (order_id, payment_method, amount, payment_status)
                        VALUES (%s, %s, %s, 'Completed')""", (order_id, payment_method, total))
                    connection.commit()
                    st.success(f"Order #{order_id} placed.")
                except (Error, ValueError) as exc:
                    connection.rollback()
                    st.error(f"Order was rolled back: {exc}")
    except Error as exc:
        st.error(f"Database error: {exc}")


REPORTS = {
    "Top 5 customers": """SELECT c.full_name, SUM(o.total_amount) AS spend
        FROM customers c JOIN orders o ON o.customer_id=c.customer_id
        GROUP BY c.customer_id, c.full_name ORDER BY spend DESC LIMIT 5""",
    "Monthly sales": """SELECT DATE_FORMAT(order_date, '%Y-%m') month,
        SUM(total_amount) sales FROM orders GROUP BY month ORDER BY month""",
    "Best selling products": """SELECT p.product_name, SUM(oi.quantity) units
        FROM order_items oi JOIN products p ON p.product_id=oi.product_id
        GROUP BY p.product_id, p.product_name ORDER BY units DESC LIMIT 10""",
    "Low stock": "SELECT * FROM v_low_stock_products",
    "Category revenue": """SELECT c.category_name, SUM(oi.quantity*oi.unit_price) revenue
        FROM order_items oi JOIN products p ON p.product_id=oi.product_id
        JOIN categories c ON c.category_id=p.category_id
        GROUP BY c.category_id, c.category_name ORDER BY revenue DESC""",
    "Never ordered": """SELECT c.customer_id, c.full_name FROM customers c
        LEFT JOIN orders o ON o.customer_id=c.customer_id WHERE o.order_id IS NULL""",
    "Payment share": """SELECT payment_method, COUNT(*) payments, SUM(amount) amount
        FROM payments GROUP BY payment_method ORDER BY amount DESC""",
    "Orders by status": "SELECT status, COUNT(*) orders FROM orders GROUP BY status",
}


def reports_page() -> None:
    st.title("📊 Reports")
    st.caption("Ready-made SQL reports for common retail business questions.")
    for label, sql in REPORTS.items():
        with st.expander(label):
            try:
                st.dataframe(query_df(sql), width="stretch")
            except Error as exc:
                st.error(f"Database error: {exc}")


def run_sql_page() -> None:
    st.title("🧪 SQL Playground")
    st.caption("Run SELECT-only queries to explore the store database safely.")
    sql = st.text_area("Enter a SELECT query", "SELECT * FROM v_sales_summary LIMIT 10;", height=140)
    if st.button("Run query"):
        if not sql.strip().lower().startswith("select"):
            st.error("Only SELECT statements are allowed.")
            return
        try:
            st.dataframe(query_df(sql), width="stretch")
        except Error as exc:
            st.error(f"Query error: {exc}")


pages = {
    "📈 Dashboard": dashboard, "👥 Customers": customers_page, "📦 Products": products_page,
    "🧾 Orders": order_page, "📊 Reports": reports_page, "🧪 SQL Playground": run_sql_page,
}
st.sidebar.markdown("## 🛍️ Retail Store")
st.sidebar.caption("Database Management System")
selection = st.sidebar.radio("Navigation", list(pages))
st.sidebar.divider()
st.sidebar.caption("Built with MySQL + Python + Streamlit")
pages[selection]()
