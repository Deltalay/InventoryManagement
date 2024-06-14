import pymysql.cursors
from dotenv import load_dotenv
import os
import bcrypt
from enum import Enum
import datetime
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
    checkPassword = bcrypt.checkpw(password.encode("utf8"), str.encode(passwordHash))
    if checkPassword:
        salt = bcrypt.gensalt()
        verifyString = "id:" + result["id"] + "name:"+result["username"]
        token = bcrypt.hashpw(verifyString.encode("utf8"), salt)
        formatTime = '%Y-%m-%d %H:%M:%S'
        now = datetime.datetime.now().strftime(format=formatTime)
        cursor.execute(
            "UPDATE users SET token=%s, token_exp=%s WHERE id=%s", (
                token, now, result['id'])
        )

        resultToken = cursor.fetchone()
        for i in resultToken:
            print(resultToken[i])
    else:
        return {
            "error": "Wrong username or password."
        }


def create_account(username, password, token):
    verify_token = ""


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
