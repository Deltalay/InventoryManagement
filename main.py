import pymysql.cursors
from dotenv import load_dotenv
import os
import datetime
import bcrypt
import jwt
from enum import Enum
load_dotenv()
connection = None
cursor = None
discount_global = 0


class Role(Enum):
    Admin = "admin"
    Employee = "employee"


def login(username, password):
    if len(username) <= 0:
        return {
            "error": "Please enter your username"
        }
    if len(password) <= 0:
        return {
            "error": "Please enter your password"
        }
    cursor.execute(
        "SELECT * FROM users WHERE username=%s LIMIT 1", (username))
    result = cursor.fetchone()
    passwordHash = result['password']
    checkPassword = bcrypt.checkpw(
        password.encode("utf8"), str.encode(passwordHash))
    if checkPassword:
        token = jwt.encode({
            "id": result['id'],
            "username": result['username']
        }, os.getenv("SECRET"),  algorithm="HS256")
        formatTime = "%Y-%m-%d %H:%M:%S"

        now = datetime.datetime.now() + datetime.timedelta(hours=12)
        now = now.replace(microsecond=0)

        now.strftime(format=formatTime)

        try:
            cursor.execute(
                "UPDATE users SET token_val=%s, token_exp=%s WHERE id=%s", (
                    token, str(now), result['id'])
            )
            connection.commit()
            with open("token", "w") as file:
                file.write(token)

        except Exception as e:
            print(e)
            return False
        else:
            return True

    else:
        return {
            "error": "Wrong username or password."
        }


def create_account(username, password):
    if len(username) <= 0:
        return {
            "username": "Please enter your username"
        }
    if len(password) <= 0:
        return {
            "password": "Please enter your password"
        }
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] == Role.Admin.value:
        salth = bcrypt.gensalt()
        hashpassword = bcrypt.hashpw(password=password, salt=salth)
        try:
            cursor.execute(
                "INSERT INTO users(username, password) values(%s, %s)", (username, hashpassword))
        except Exception as e:
            print(e)
            return False
        else:
            return True
    else:
        print("Sorry you are not an admin")
        return


def search_items(itemName):
    try:
        cursor.execute("SELECT * FROM items WHERE name LIKE %s OR description LIKE %s",
                       (f"%{itemName}%", f"%{itemName}%"))
        results = cursor.fetchall()
        if results:
            return results
        else:
            print('NO RECORDS FOUND')

    except Exception as e:
        print('INPUT ERROR:', e)


def add_item(item_name, item_description, item_price, item_stock, category_name, expires_date):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if len(item_name) <= 0:
        return {
            "error": "Please enter your name"
        }
    if len(item_description) <= 0:
        return {
            "error": "Please enter your description"
        }
    if len(item_price) <= 0 and int(item_price) <= 0:
        return {
            "error": "Please enter your price"
        }
    if len(item_stock) <= 0 and int(item_stock) <= 0:
        return {
            "error": "Please enter your stock"
        }
    if len(category_name) <= 0:
        return {
            "error": "Invalid category"
        }
    date_format = "%Y-%m-%d %H:%M:%S"
    input_date = datetime.datetime.strptime(expires_date, date_format)
    current_date = datetime.datetime.now()
    if current_date > input_date:
        return {
            "error": "You cannot enter an expire item."
        }
    categoryId = cursor.execute(
        "SELECT * FROM category WHERE name=%s LIMIT 1", (category_name))
    result = cursor.fetchone()
    try:
        cursor.execute(
            "INSERT INTO items(category_id, name, description, price, quantity, expire_date) values(%s,%s,%s,%s,%s,%s)", (result["id"], item_name, item_description, int(item_price), int(item_stock), expires_date.replace(microsecond=0)))
    except Exception as e:
        print(e)
        return False
    else:
        return True


def update_stock(item_name, quantity):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if len(item_name) <= 0:
        return {
            "error": "Please enter the item name"
        }
    try:
        cursor.execute("UPDATE items SET quantity=%s WHERE name=",
                       (int(quantity), item_name))
        connection.commit()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def create_category(name):
    if len(name) <= 0:
        return {
            "error": "Invalid name"
        }
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    try:
        cursor.execute("INSERT INTO category(name) VALUES(%s)", (name))
    except Exception as e:
        print(e)
        return False
    else:
        return True


def search_items_filter(item_name="", in_stock=True, price_low=0, price_high=0, category="all"):
    query = """SELECT items.id, items.name, items.description, items.price, items.quantity, category.name AS category_name
                FROM items
                JOIN category ON items.category_id = category.id
                WHERE 1=1"""
    params = []
    if len(item_name) > 0:
        query += " AND (description LIKE %s OR name LIKE %s)"
        params.extend([f"%{item_name}%", f"%{item_name}%"])
    if in_stock:
        query += " AND quantity > 0"
    if price_high > 0:
        query += " AND price <= %s"
        params.append(int(price_high))
    if price_low > 0:
        query += " AND price >= %s"
        params.append(int(price_low))
    if category.lower() != "all":
        query += " AND category.name = %s"
        params.append(category)

    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
        for i in results:
            print(results)
        return results
    except Exception as e:
        print(e)


def update_stock(item_name, price):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if len(item_name) <= 0:
        return {
            "error": "Please enter the item name"
        }
    try:
        cursor.execute("UPDATE items SET price=%s WHERE name=",
                       (int(price), item_name))
        connection.commit()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def delete_items(item_name):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if len(item_name) <= 0:
        return {
            "error": "Please enter the item name"
        }
    try:
        cursor.execute("DELETE FROM items WHERE name=%s", (item_name))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


def set_discount_item(itemName, discount):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if len(itemName) <= 0:
        return {
            "error": "Please enter the item name"
        }
    if int(discount) > 100 or int(discount) < 0:
        return {
            "error": "what are you trying to do?"
        }
    try:
        cursor.execute(
            "UPDATE items SET discount=%s WHERE name=%s", (int(
                discount), itemName)
        )
        connection.commit()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def set_global_discount(discount_amount):
    openFile = open("token", "r")
    token = openFile.read()
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
    if int(discount_amount) > 100 or int(discount_amount) < 0:
        return {
            "error": "What are you trying to do?"
        }
    discount_global = int(discount_amount)


if __name__ == "__main__":
    load_dotenv()
    connection = None
    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        search_items_filter(price_low=20000, in_stock=False, category="Food")
    except Exception as e:
        print(e)
        print("Something whent wrong")
    else:
        print("Database connected")
