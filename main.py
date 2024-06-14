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


def delete_items(item_name):
    try:
        cursor.execute("DELETE FROM items WHERE name=%s", (item_name))
        connection.commit()
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    load_dotenv()
    connection = None
    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        login("delta", "123123123")
        create_account(username="he", password="d")
    except Exception as e:
        print(e)
        print("Something whent wrong")
    else:
        print("Database connected")
