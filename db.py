import psycopg2
import hashlib
import redis
import json

def get_connection():
    return psycopg2.connect(
        dbname="Taradb",
        user="postgres",
        password="123",
        host="localhost",
        port="5432"
    )

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

def get_registered_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT username, password_hash FROM Reg_users;")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def add_registered_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Reg_users (username, password_hash)
        VALUES (%s, %s);
    """, (username, password_hash))
    conn.commit()
    cur.close()
    conn.close()

def get_users():
    cached = r.get("users")
    if cached:
        return json.loads(cached)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT user_id, first_name, last_name, email, phone_number, registration_date
        FROM Users;
    """)
    rows = cur.fetchall()
    users = [
        {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "email": row[3],
            "phone_number": row[4],
            "registration_date": str(row[5])
        }
        for row in rows
    ]
    cur.close()
    conn.close()

    r.setex("users", 3600, json.dumps(users))
    return users

def add_user(first_name, last_name, email, phone_number=None, password=None):
    password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (first_name, last_name, email, phone_number, password_hash, registration_date)
        VALUES (%s, %s, %s, %s, %s, CURRENT_DATE);
    """, (first_name, last_name, email, phone_number, password_hash))
    conn.commit()
    cur.close()
    conn.close()

def update_user(user_id, first_name, last_name, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE Users
        SET first_name = %s, last_name = %s, email = %s
        WHERE user_id = %s;
    """, (first_name, last_name, email, user_id))
    conn.commit()
    cur.close()
    conn.close()

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
    cur.execute("""
        SELECT product_id, name, price, stock_quantity
        FROM Products;
    """)
    products = cur.fetchall()
    cur.close()
    conn.close()
    return products

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
