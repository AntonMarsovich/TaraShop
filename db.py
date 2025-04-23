import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="Taradb",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

def get_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, first_name, last_name, email FROM Users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def get_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT o.order_id, u.first_name, u.last_name, o.order_date, o.status
        FROM Orders o
        JOIN Users u ON o.user_id = u.user_id;
    """)
    orders = cur.fetchall()
    cur.close()
    conn.close()
    return orders

def get_products():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT product_id, name, price, stock_quantity FROM Products;")
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products
def add_user(first_name, last_name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Users (first_name, last_name, email, password_hash)
        VALUES (%s, %s, %s, %s);
    """, (first_name, last_name, email, password_hash))
    conn.commit()
    cur.close()
    conn.close()

def add_product(name, description, price, stock_quantity):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Products (name, description, price, stock_quantity)
        VALUES (%s, %s, %s, %s);
    """, (name, description, price, stock_quantity))
    conn.commit()
    cur.close()
    conn.close()
