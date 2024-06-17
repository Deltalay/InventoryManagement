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
    checkPassword = bcrypt.checkpw(
        password.encode("utf8"), str.encode(passwordHash))
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
        return {
            "token": token
        }
    else:
        return {
            "error": "Wrong username or password."
        }


def create_account(username, password, token):
    verify_token = ""

def search_items(category_id_from_users):
    try:        
        # Define the query
        query = "SELECT * FROM items WHERE category_id = %s AND stock > 0"
        
        # Execute the query
        cursor.execute(query, (category_id_from_users,))
        results = cursor.fetchall()
        
        if results:
            print('ITEMS FOUND:')
            for row in results:
                print(row)
        else:
            print('NO ITEMS FOUND')
        
    except Exception as e:
        print('INPUT ERROR:', e)

def search_items_first_letter(first_letter_from_users):
    try:
        # Define the query
        query = "SELECT * FROM items WHERE name like %s and stock > 0"
        
        # Execute the query
        cursor.execute(query, (first_letter_from_users + '%',))
        results = cursor.fetchall()
        
        if results:
            print('ITEMS FOUND:')
            for row in results:
                print(row)
        else:
            print('NO ITEMS FOUND')
        
    except Exception as e:
        print('INPUT ERROR:', e)

def whole_store_discounted(amount_percentage_from_user):
    try:
        # Define the first query to select items and calculate discounted prices
        select_query = "SELECT id, price, price * (1 - %s/100) as discounted_price FROM items"
        
        # Execute the first query
        cursor.execute(select_query, (amount_percentage_from_user,))
        results = cursor.fetchall()
        
        if results:
            print('DISCOUNTS ADDED SUCCESSFULLY.')
            for row in results:
                print(row)
                # Define the update query to set the discounted price
                update_query = "UPDATE items SET discounted_price = %s WHERE id = %s"
                
                # Execute the update query with the calculated discounted price and item id
                cursor.execute(update_query, (row['discounted_price'], row['id']))
                
                # Commit the transaction to save the changes to the database
                conn.commit()
        else:
            print('DISCOUNTS ADDED UNSUCCESSFULLY.')
        
    except Exception as e:
        print('INPUT ERROR:', e)

def create_product_table():
    try:
        query = """
                   CREATE TABLE IF NOT EXISTS PRODUCT (
                       category_id INT PRIMARY KEY NOT NULL,
                       name VARCHAR(50) NOT NULL,
                       description TEXT,
                       price DECIMAL(10, 2) NOT NULL,
                       quantity INT NOT NULL,
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                       expire_date DATE
                   )"""

        cursor.execute(query)
        print('Table created successfully')
        conn.commit()
    except Exception as ex:
        print('PROBLEM WITH Database Connection:', ex)
    finally:
        conn.close()

def insert_product():
    try:
        with conn.cursor() as cursor:
            category_id = int(input("Enter category ID: "))
            name = input("Enter product name: ")
            description = input("Enter product description: ")
            price = float(input("Enter product price: "))
            quantity = int(input("Enter product quantity: "))
            expire_date = input("Enter product expire date (YYYY-MM-DD): ")

            query = """
                INSERT INTO PRODUCT (category_id, name, description, price, quantity, expire_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

            cursor.execute(query, (category_id, name, description, price, quantity, expire_date))
            conn.commit()
            print("Product inserted successfully")
    except Exception as e:
        print('Error occurred while inserting product:', e)
    finally:
        conn.close()

def delete_product():
    try:
        with conn.cursor() as cursor:
            category_id = int(input("Enter category ID of the product to delete: "))
            query = "DELETE FROM PRODUCT WHERE category_id = %s"

            cursor.execute(query, (category_id,))
            conn.commit()
            print("Product deleted successfully")
    except Exception as e:
        print('Error occurred while deleting product:', e)
    finally:
        conn.close()

def update_product():
    try:
        with conn.cursor() as cursor:
            category_id = int(input("Enter category ID of the product to update: "))
            name = input("Enter new product name (leave blank to keep current): ")
            description = input("Enter new product description (leave blank to keep current): ")
            price = input("Enter new product price (leave blank to keep current): ")
            quantity = input("Enter new product quantity (leave blank to keep current): ")
            expire_date = input("Enter new product expire date (YYYY-MM-DD) (leave blank to keep current): ")

            update_fields = []
            update_values = []

            if name:
                update_fields.append("name = %s")
                update_values.append(name)
            if description:
                update_fields.append("description = %s")
                update_values.append(description)
            if price:
                update_fields.append("price = %s")
                update_values.append(float(price))
            if quantity:
                update_fields.append("quantity = %s")
                update_values.append(int(quantity))
            if expire_date:
                update_fields.append("expire_date = %s")
                update_values.append(expire_date)

            update_values.append(category_id)

            if update_fields:
                query = f"UPDATE PRODUCT SET {', '.join(update_fields)} WHERE category_id = %s"
                cursor.execute(query, update_values)
                conn.commit()
                print("Product updated successfully")
            else:
                print("No updates provided")
    except Exception as e:
        print('Error occurred while updating product:', e)
    finally:
        conn.close()


def specific_items_discounted(amount_percentage_from_user, specific_items_id):
    try:
        # Define the first query to select items and calculate discounted prices
        select_query = "SELECT id, price, price * (1 - %s/100) as discounted_price_specific_items FROM items WHERE id = %s"
        
        # Execute the first query
        cursor.execute(select_query, (amount_percentage_from_user, specific_items_id,))
        results = cursor.fetchall()
        
        if results:
            print('DISCOUNTS ADDED SUCCESSFULLY.')
            for row in results:
                print(row)
                # Define the update query to set the discounted price
                update_query = "UPDATE items SET discounted_price_specific_items = %s WHERE id = %s"
                
                # Execute the update query with the calculated discounted price and item id
                cursor.execute(update_query, (row['discounted_price_specific_items'], row['id']))
                
                # Commit the transaction to save the changes to the database
                conn.commit()
        else:
            print('DISCOUNTS ADDED UNSUCCESSFULLY.')
        
    except Exception as e:
        print('INPUT ERROR:', e)

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
