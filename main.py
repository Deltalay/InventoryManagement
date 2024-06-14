import pymysql.cursors
from dotenv import load_dotenv
import os
import bcrypt
from enum import Enum
load_dotenv()
connection = None
cursor = None

class Role(Enum):
    Admin="admin"
    Employee="employee"

def login(username, password):
    if len(username) < 0:
        return {
            "username": "Please enter your username"
        }
    if len(password) < 0:
        return {
            "password": "Please enter your password"
        }
    searchUser = cursor.execute(
        "SELECT * FROM users WHERE username=%s LIMIT 1", (username))
    result = cursor.fetchone()
    passwordHash = result['password']
    checkPassword = bcrypt.checkpw(password.encode("utf-8", passwordHash))
    if checkPassword:
        print("Login success")
    else:
        return {
            "error": "Wrong username or password."
        }


if __name__ == "__main__":
    load_dotenv()
    connection = None
    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        login("hi", "123")
    except Exception as e:
        print(e)
        print("Something whent wrong")
    else:
        print("Database connected")
