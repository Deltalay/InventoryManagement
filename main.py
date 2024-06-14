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
    if len(username) < 0:
        return {
            "username": "Please enter your username"
        }
    if len(password) < 0:
        return {
            "password": "Please enter your password"
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

        cursor.execute(
            "UPDATE users SET token_val=%s, token_exp=%s WHERE id=%s", (
                token, str(now), result['id'])
        )
        connection.commit()
        return {
            "token": token
        }
    else:
        return {
            "error": "Wrong username or password."
        }


def create_account(username, password, token):
    verify_token = jwt.decode(token, os.getenv("SECRET"), algorithms="HS256")
    admin_id = verify_token['id']
    cursor.execute("SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
    result = cursor.fetchone()
    if result["role"] == Role.Admin.value:
        print("You are an admin")
    else:
        print("Sorry you are not an admin")
    


def search_items(category_id_from_users):
    try:
        # Define the query
        query = "SELECT * FROM items WHERE category_id = %s AND stock > 0"

        # Execute the query
        cursor.execute(query, (category_id_from_users,))
        results = cursor.fetchall()

        if results:
            print('RECORD FOUND:')
            for row in results:
                print(row)
        else:
            print('NO RECORDS FOUND')

    except Exception as e:
        print('INPUT ERROR:', e)


if __name__ == "__main__":
    load_dotenv()
    connection = None
    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        logda = login("delta", "123123123")
    
        print(logda['token'])
        create_account(token=logda["token"], username="he", password="d")
    except Exception as e:
        print(e)
        print("Something whent wrong")
    else:
        print("Database connected")
