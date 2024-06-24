import pymysql.cursors
from enum import Enum
import jwt
import bcrypt
import datetime
import platform
import os
from dotenv import load_dotenv
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Frame, Label, messagebox
if platform.system == "Windows":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)


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
    if result == None:
        return {
            "error": "Account doesn't exist!"
        }
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
        try:
            cursor.execute(
                "SELECT * FROM users WHERE username=%s LIMIT 1", (username)
            )
            checking = cursor.fetchone()
            if checking == None:
                salth = bcrypt.gensalt()

                hashpassword = bcrypt.hashpw(
                    password=password.encode('utf-8'), salt=salth)
                cursor.execute(
                    "INSERT INTO users(username, password) values(%s, %s)", (username, hashpassword))
                connection.commit()
            else:
                return {
                    "error": "User already exist!"
                }
        except Exception as e:
            print(e)
            return False
        else:
            return True
    else:
        print("Sorry you are not an admin")
        return


def select_all_item():
    try:
        cursor.execute("SELECT * FROM items")
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(e)
        return False


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


def add_item(item_name, item_description, item_price, item_stock,  expires_date, category_name=None):
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
    date_format = "%Y-%m-%d"
    input_date = datetime.datetime.strptime(expires_date, date_format)
    current_date = datetime.datetime.now()
    if current_date > input_date:
        return {
            "error": "You cannot enter an expire item."
        }

    result = cursor.fetchone()
    try:
        if category_name != None:
            categoryId = cursor.execute(
                "SELECT * FROM category WHERE name=%s LIMIT 1", (category_name))
            cursor.execute(
                "INSERT INTO items(category_id, name, description, price, quantity, expire_date) values(%s,%s,%s,%s,%s,%s)", (result["id"], item_name, item_description, int(item_price), int(item_stock), expires_date))
            connection.commit()
        else:
            cursor.execute(
                "INSERT INTO items( name, description, price, quantity, expire_date) values(%s,%s,%s,%s,%s)", (item_name, item_description, int(item_price), int(item_stock), expires_date))
            connection.commit()
    except Exception as e:
        print(e)
        return False
    else:
        return True


def update_item(item_name, description, price, quantity, expiredate):
    if len(item_name) <= 0:
        return {
            "error": "Please enter your name"
        }
    if len(description) <= 0:
        return {
            "error": "Please enter your description"
        }
    if len(price) <= 0 and int(price) <= 0:
        return {
            "error": "Please enter your price"
        }
    if len(quantity) <= 0 and int(quantity) <= 0:
        return {
            "error": "Please enter your stock"
        }
    date_format = "%Y-%m-%d"
    input_date = datetime.datetime.strptime(expiredate, date_format)
    current_date = datetime.datetime.now()
    if current_date > input_date:
        return {
            "error": "You cannot enter an expire item."
        }
    try:
        cursor.execute("UPDATE items SET name=%s, description=%s, price=%s, quantity=%s, expire_date=%s WHERE name=%s",
                       (item_name, description, float(price.rstrip("$")), int(quantity), expiredate, item_name))
        connection.commit()
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


def isadmin(username):
    cursor.execute("SELECT * FROM users WHERE username=%s LIMIT 1", (username))
    result = cursor.fetchone()
    if result["role"] != Role.Admin.value:
        return False
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


class TkinterApp(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("Inventory Management")
        self.geometry("900x600")
        self.resizable(False, False)
        Login(parent=self).pack(fill="both", expand="true")

    def switch_to_admin(self):
        self.clear()
        Admin(parent=self).pack(fill="both", expand="true")

    def switch_to_employee(self):
        self.clear()
        Employee(parent=self).pack(fill="both", expand="true")

    def switch_to_create(self):
        self.clear()
        Create(parent=self).pack(fill="both", expand="true")

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()


class Admin(Canvas):
    def relative_to_assets(self, path: str) -> Path:
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / \
            Path(r"/home/delta/Desktop/utilities/python/InventoryManagement/assets/frame3")
        return ASSETS_PATH / Path(path)

    def __init__(self, parent: TkinterApp):
        super(Admin, self).__init__()

        self.parent = parent

        canvas = Canvas(
            master=self,
            bg="#FFFFFF",
            height=600,
            width=900,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            0.0,
            0.0,
            900.0,
            79.0,
            fill="#82FB7C",
            outline="")
        openFile = open("token", "r")
        token = openFile.read()
        verify_token = jwt.decode(
            token, os.getenv("SECRET"), algorithms="HS256")
        nameuser = verify_token["username"]
        canvas.create_text(
            35.0,
            28.0,
            anchor="nw",
            text="Welcome back, " + nameuser,
            fill="#000000",
            font=("Inter Bold", 20 * -1)
        )

        canvas.create_rectangle(
            0.0,
            79.0,
            900.0,
            600.0,
            fill="#FFFFFF",
            outline="")

        Search_entry = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0
        )
        Search_entry.insert(0, "Search")

        def on_enter(e):
            if Search_entry.get() == "Search":
                Search_entry.delete(0, 'end')

        def on_leave(e):
            name = Search_entry.get()
            if name == "":
                Search_entry.insert(0, "Search")
        Search_entry.bind('<FocusIn>', on_enter)
        Search_entry.bind('<FocusOut>', on_leave)

        def search():
            search_query = Search_entry.get()
            result = search_items(search_query)
            
        Search_entry.place(
            x=426.0,
            y=18.0,
            width=286.0,
            height=41.0
        )

        self.button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print(Search_entry.get()),
            relief="flat"
        )
        button_1.place(
            x=712.0,
            y=18.0,
            width=43.0,
            height=43.0
        )

        self.button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))

        canvas.create_rectangle(
            35.0,
            150.0,
            867.0,
            577.0,
            fill="#FFFFFF",
            outline="")

        canvas.create_rectangle(
            35.0,
            150.0,
            867.0,
            187.0,
            fill="#F5F5F5",
            outline="")

        canvas.create_text(
            48.0,
            156.0,
            anchor="nw",
            text="Item name",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            222.0,
            156.0,
            anchor="nw",
            text="Item description",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            497.0,
            156.0,
            anchor="nw",
            text="Quantity",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            575.0,
            156.0,
            anchor="nw",
            text="Price",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            653.0,
            156.0,
            anchor="nw",
            text="Expire dates",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        item_select_all = select_all_item()

        canvas.create_text(
            35.0,
            107.0,
            anchor="nw",
            text="All Items: " + str(len(item_select_all)),
            fill="#000000",
            font=("Inter Medium", 16 * -1)
        )
        lastY = 0

        def create_new_item():
            item_name = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            item_name.focus_set()
            item_name.place(
                x=48.0,
                y=lastY,
                width=169.0,
                height=41.0
            )
            description = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            description.place(
                x=217.0,
                y=lastY,
                width=280.0,
                height=41.0
            )
            quantity = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            quantity.place(
                x=497.0,
                y=lastY,
                width=72.0,
                height=41.0
            )
            price = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            price.place(
                x=569.0,
                y=lastY,
                width=78.0,
                height=41.0
            )
            expireDate = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            expireDate.place(
                x=647.0,
                y=lastY,
                width=133.0,
                height=41.0
            )
            button_image_4 = PhotoImage(
                file=self.relative_to_assets("confirm.png"))

            def button_click(item_name_widget, item_description_widget, quantity_widget, price_widget, expire_date_widget):

                def on_click():
                    item_content = item_name_widget.get()
                    description_content = item_description_widget.get()
                    quantity_content = quantity_widget.get()
                    price_content = price_widget.get()
                    expireDate_content = expire_date_widget.get()
                    print(item_content, description_content,
                          quantity_content, price_content, expireDate_content)
                    add_item(item_content, description_content, price_content,
                             quantity_content, expireDate_content)
                    self.parent.switch_to_admin()
                return on_click
            button_4 = Button(
                image=button_image_4,
                borderwidth=0,
                highlightthickness=0,
                command=button_click(item_name, description,
                                     quantity, price, expireDate),
                relief="flat",
            )
            button_4.image = button_image_4
            button_4.place(
                x=799.0,
                y=lastY + 5,
                width=33.0,
                height=33.0
            )
            print("Hello")
        button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=create_new_item,
            relief="flat"
        )
        button_2.place(
            x=832.0,
            y=107.0,
            width=33.0,
            height=33.0
        )

        for index, i in enumerate(item_select_all):
            lastY = 197 + (index * 43) + 43
            item_name = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            item_name.insert(0, i['name'])
            item_name.place(
                x=48.0,
                y=197.0 + (index * 43),
                width=169.0,
                height=41.0
            )
            description = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            description.insert(0, i['description'])
            description.place(
                x=217.0,
                y=197.0 + (index * 43),
                width=280.0,
                height=41.0
            )
            quantity = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            quantity.insert(0, i["quantity"])
            quantity.place(
                x=497.0,
                y=197.0 + (index * 43),
                width=72.0,
                height=41.0
            )
            price = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            price.insert(0, str(i["price"]) + "$")
            price.place(
                x=569.0,
                y=197.0 + (index * 43),
                width=78.0,
                height=41.0
            )
            expireDate = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            expireDate.insert(0, i["expire_date"].strftime('%Y-%m-%d'))
            expireDate.place(
                x=647.0,
                y=197.0 + (index * 43),
                width=133.0,
                height=41.0
            )
            button_image_4 = PhotoImage(
                file=self.relative_to_assets("button_4.png"))

            def button_click(entry_widget):

                def on_click():
                    entry_content = entry_widget.get()
                    print(f"Entry content: {entry_content}")
                    delete_items(entry_content)
                    self.parent.switch_to_admin()
                return on_click

            button_4 = Button(
                image=button_image_4,
                borderwidth=0,
                highlightthickness=0,
                command=button_click(item_name),
                relief="flat",
            )
            button_4.image = button_image_4
            button_4.place(
                x=783.0,
                y=202.0 + (index * 43),
                width=33.0,
                height=33.0
            )

            def update_item_data(item_name_widget, item_description_widget, quantity_widget, price_widget, expire_date_widget):

                def on_click():
                    item_content = item_name_widget.get()
                    description_content = item_description_widget.get()
                    quantity_content = quantity_widget.get()
                    price_content = price_widget.get()
                    expireDate_content = expire_date_widget.get()
                    print(item_content, description_content,
                          quantity_content, price_content, expireDate_content)
                    update_item(item_content, description_content,
                                price_content, quantity_content, expireDate_content)
                    self.parent.switch_to_admin()
                return on_click
            button_image_5 = PhotoImage(
                file=self.relative_to_assets("confirm.png"))
            button_5 = Button(
                image=button_image_5,
                borderwidth=0,
                highlightthickness=0,
                command=update_item_data(
                    item_name, description, quantity, price, expireDate),
                relief="flat",
            )
            button_5.image = button_image_5
            button_5.place(
                x=816.0,
                y=202.0 + (index * 43),
                width=33.0,
                height=33.0
            )

        self.button_image_6 = PhotoImage(
            file=self.relative_to_assets("button_6.png"))

        def create_acc():
            openFile = open("token", "r")
            token = openFile.read()
            verify_token = jwt.decode(
                token, os.getenv("SECRET"), algorithms="HS256")
            admin_id = verify_token['id']
            cursor.execute(
                "SELECT * FROM users WHERE id=%s LIMIT 1", (admin_id))
            result = cursor.fetchone()
            if result["role"] == Role.Admin.value:
                self.parent.switch_to_create()

        button_6 = Button(
            image=self.button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=create_acc,
            relief="flat"
        )
        button_6.place(
            x=765.0,
            y=18.0,
            width=102.0,
            height=43.0
        )


class Login(Canvas):
    def relative_to_assets(self, path: str) -> Path:
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / \
            Path(r"/home/delta/Desktop/utilities/python/InventoryManagement/assets/frame0")
        return ASSETS_PATH / Path(path)

    def __init__(self, parent: TkinterApp):
        super(Login, self).__init__()

        self.parent = parent
        self.image_image_1 = PhotoImage(
            file=self.relative_to_assets("image_1.png"))
        self.entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_1.png"))
        self.entry_image_2 = PhotoImage(
            file=self.relative_to_assets("entry_2.png"))
        self.button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))

        canvas = Canvas(
            master=self,
            bg="#FFFFFF",
            height=600,
            width=900,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            446.0,
            2.0,
            900.0,
            602.0,
            fill="#FFFFFF",
            outline="")

        image_1 = canvas.create_image(
            242.0,
            302.0,
            image=self.image_image_1
        )

        entry_bg_1 = canvas.create_image(
            657.5,
            295.5,
            image=self.entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            show="*",
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0
        )
        entry_1.place(
            x=446.0,
            y=269.0,
            width=423.0,
            height=51.0
        )

        canvas.create_text(
            446.0,
            252.0,
            anchor="nw",
            text="Password:",
            fill="#000000",
            font=("Inter Medium", 16 * -1)
        )

        canvas.create_text(
            602.0,
            52.0,
            anchor="nw",
            text="LOGIN",
            fill="#000000",
            font=("Inter Bold", 36 * -1)
        )

        entry_bg_2 = canvas.create_image(
            657.5,
            203.5,
            image=self.entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
        )
        entry_2.place(
            x=446.0,
            y=177.0,
            width=423.0,
            height=51.0
        )

        canvas.create_text(
            446.0,
            158.0,
            anchor="nw",
            text="Username:",
            fill="#000000",
            font=("Inter Medium", 17 * -1)
        )

        def logUser():
            password = entry_1.get()
            username = entry_2.get()
            testingLog = login(username=username, password=password)

            if (isinstance(testingLog, bool) and testingLog == False) or (type(testingLog) is dict and testingLog["error"] != None):
                messagebox.showerror(title="Fail to connect to database",
                                     message="Please make sure to enter the username and password correctly.")
            if isinstance(testingLog, bool) and testingLog == True:
                is_admin = isadmin(username=username)
                if is_admin:
                    self.parent.switch_to_admin()
                else:
                    self.parent.switch_to_employee()

        button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=logUser,
            relief="flat"
        )
        button_1.place(
            x=468.0,
            y=407.0,
            width=379.0,
            height=51.0
        )


class Create(Canvas):
    def relative_to_assets(self, path: str) -> Path:
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / \
            Path(r"/home/delta/Desktop/utilities/python/InventoryManagement/assets/frame1")
        return ASSETS_PATH / Path(path)

    def __init__(self, parent: TkinterApp):
        super(Create, self).__init__()
        self.parent = parent
        canvas = Canvas(
            self,
            bg="#FFFFFF",
            height=600,
            width=900,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        self.image_image_1 = PhotoImage(
            file=self.relative_to_assets("image_1.png"))
        image_1 = canvas.create_image(
            675.0,
            300.0,
            image=self.image_image_1
        )

        canvas.create_rectangle(
            0.0,
            0.0,
            454.0,
            600.0,
            fill="#FFFFFF",
            outline="")

        self.entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            242.5,
            293.5,
            image=self.entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0,
            show="*"
        )
        entry_1.place(
            x=31.0,
            y=267.0,
            width=423.0,
            height=51.0
        )

        canvas.create_text(
            31.0,
            250.0,
            anchor="nw",
            text="Password:",
            fill="#000000",
            font=("Inter Medium", 16 * -1)
        )

        self.entry_image_2 = PhotoImage(
            file=self.relative_to_assets("entry_2.png"))
        entry_bg_2 = canvas.create_image(
            242.5,
            385.5,
            image=self.entry_image_2
        )
        entry_2 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            show="*",
            highlightthickness=0
        )
        entry_2.place(
            x=31.0,
            y=359.0,
            width=423.0,
            height=51.0
        )

        canvas.create_text(
            31.0,
            342.0,
            anchor="nw",
            text="Confirm Password:",
            fill="#000000",
            font=("Inter Medium", 16 * -1)
        )

        canvas.create_text(
            104.0,
            50.0,
            anchor="nw",
            text="Create Account",
            fill="#000000",
            font=("Inter Bold", 36 * -1)
        )

        self.entry_image_3 = PhotoImage(
            file=self.relative_to_assets("entry_3.png"))
        entry_bg_3 = canvas.create_image(
            242.5,
            201.5,
            image=self.entry_image_3
        )
        entry_3 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0
        )
        entry_3.place(
            x=31.0,
            y=175.0,
            width=423.0,
            height=51.0
        )

        canvas.create_text(
            31.0,
            156.0,
            anchor="nw",
            text="Username:",
            fill="#000000",
            font=("Inter Medium", 17 * -1)
        )

        self.button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))

        def create_account_():
            password = entry_1.get()
            confirm_password = entry_2.get()
            username = entry_3.get()
            if password != confirm_password:
                return messagebox.showerror(title="Error",
                                            message="Your confirm password and password is not the same please check again.")
            testingCreate = create_account(
                username=username, password=password)
            if type(testingCreate) is dict and testingCreate["error"]:
                return messagebox.showerror(title="Error",
                                            message=testingCreate["error"])
            if (isinstance(testingCreate, bool) and testingCreate == False):
                messagebox.showerror(title="Something went wrong",
                                     message="Well you have to debug your code to find this error.")
            if isinstance(testingCreate, bool) and testingCreate == True:
                is_admin = isadmin(username=username)
                if is_admin:
                    self.parent.switch_to_admin()
                else:
                    self.parent.switch_to_employee()
        button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=create_account_,
            relief="flat"
        )
        button_1.place(
            x=53.0,
            y=433.0,
            width=379.0,
            height=51.0
        )

        self.button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))

        def cancel_creation():
            self.parent.switch_to_admin()
        button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=cancel_creation,
            relief="flat"
        )
        button_2.place(
            x=53.0,
            y=493.0,
            width=379.0,
            height=51.0
        )


class Employee(Canvas):
    def relative_to_assets(self, path: str) -> Path:
        OUTPUT_PATH = Path(__file__).parent
        ASSETS_PATH = OUTPUT_PATH / \
            Path(r"/home/delta/Desktop/utilities/python/InventoryManagement/assets/frame2")
        return ASSETS_PATH / Path(path)

    def __init__(self, parent: TkinterApp):
        super(Employee, self).__init__()

        self.parent = parent

        canvas = Canvas(
            master=self,
            bg="#FFFFFF",
            height=600,
            width=900,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

        canvas.place(x=0, y=0)
        canvas.create_rectangle(
            0.0,
            0.0,
            900.0,
            79.0,
            fill="#82FB7C",
            outline="")
        openFile = open("token", "r")
        token = openFile.read()
        verify_token = jwt.decode(
            token, os.getenv("SECRET"), algorithms="HS256")
        nameuser = verify_token["username"]
        canvas.create_text(
            35.0,
            28.0,
            anchor="nw",
            text="Welcome back, " + nameuser,
            fill="#000000",
            font=("Inter Bold", 20 * -1)
        )

        canvas.create_rectangle(
            0.0,
            79.0,
            900.0,
            600.0,
            fill="#FFFFFF",
            outline="")

        self.entry_image_1 = PhotoImage(
            file=self.relative_to_assets("entry_1.png"))
        entry_bg_1 = canvas.create_image(
            705.0,
            39.5,
            image=self.entry_image_1
        )
        entry_1 = Entry(
            bd=0,
            bg="#FFFFFF",
            fg="#000716",
            highlightthickness=0
        )
        entry_1.place(
            x=562.0,
            y=18.0,
            width=286.0,
            height=41.0
        )

        self.button_image_1 = PhotoImage(
            file=self.relative_to_assets("button_1.png"))
        button_1 = Button(
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_1 clicked"),
            relief="flat"
        )
        button_1.place(
            x=848.0,
            y=18.0,
            width=43.0,
            height=43.0
        )

        self.button_image_2 = PhotoImage(
            file=self.relative_to_assets("button_2.png"))
        button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_2 clicked"),
            relief="flat"
        )
        button_2.place(
            x=832.0,
            y=107.0,
            width=33.0,
            height=33.0
        )
        canvas.create_rectangle(
            35.0,
            150.0,
            867.0,
            577.0,
            fill="#FFFFFF",
            outline="")

        canvas.create_rectangle(
            35.0,
            150.0,
            867.0,
            187.0,
            fill="#F5F5F5",
            outline="")

        canvas.create_text(
            48.0,
            156.0,
            anchor="nw",
            text="Item name",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            222.0,
            156.0,
            anchor="nw",
            text="Item description",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            497.0,
            156.0,
            anchor="nw",
            text="Quantity",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            575.0,
            156.0,
            anchor="nw",
            text="Price",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        canvas.create_text(
            653.0,
            156.0,
            anchor="nw",
            text="Expire dates",
            fill="#000000",
            font=("Inter Bold", 14 * -1)
        )

        item_select_all = select_all_item()

        canvas.create_text(
            35.0,
            107.0,
            anchor="nw",
            text="All Items: " + str(len(item_select_all)),
            fill="#000000",
            font=("Inter Medium", 16 * -1)
        )

        lastY = 0

        def create_new_item():
            item_name = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            item_name.focus_set()
            item_name.place(
                x=48.0,
                y=lastY,
                width=169.0,
                height=41.0
            )
            description = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            description.place(
                x=217.0,
                y=lastY,
                width=280.0,
                height=41.0
            )
            quantity = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            quantity.place(
                x=497.0,
                y=lastY,
                width=72.0,
                height=41.0
            )
            price = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            price.place(
                x=569.0,
                y=lastY,
                width=78.0,
                height=41.0
            )
            expireDate = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            expireDate.place(
                x=647.0,
                y=lastY,
                width=133.0,
                height=41.0
            )
            button_image_4 = PhotoImage(
                file=self.relative_to_assets("confirm.png"))

            def button_click(item_name_widget, item_description_widget, quantity_widget, price_widget, expire_date_widget):

                def on_click():
                    item_content = item_name_widget.get()
                    description_content = item_description_widget.get()
                    quantity_content = quantity_widget.get()
                    price_content = price_widget.get()
                    expireDate_content = expire_date_widget.get()
                    print(item_content, description_content,
                          quantity_content, price_content, expireDate_content)
                    add_item(item_content, description_content, price_content,
                             quantity_content, expireDate_content)
                    self.parent.switch_to_admin()
                return on_click
            button_4 = Button(
                image=button_image_4,
                borderwidth=0,
                highlightthickness=0,
                command=button_click(item_name, description,
                                     quantity, price, expireDate),
                relief="flat",
            )
            button_4.image = button_image_4
            button_4.place(
                x=799.0,
                y=lastY + 5,
                width=33.0,
                height=33.0
            )
            print("Hello")
        button_2 = Button(
            image=self.button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=create_new_item,
            relief="flat"
        )
        button_2.place(
            x=832.0,
            y=107.0,
            width=33.0,
            height=33.0
        )
        for index, i in enumerate(item_select_all):
            lastY = 197 + (index * 43) + 43
            item_name = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0,
            )
            item_name.insert(0, i['name'])
            item_name.place(
                x=48.0,
                y=197.0 + (index * 43),
                width=169.0,
                height=41.0
            )
            description = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            description.insert(0, i['description'])
            description.place(
                x=217.0,
                y=197.0 + (index * 43),
                width=280.0,
                height=41.0
            )
            quantity = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            quantity.insert(0, i["quantity"])
            quantity.place(
                x=497.0,
                y=197.0 + (index * 43),
                width=72.0,
                height=41.0
            )
            price = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            price.insert(0, str(i["price"]) + "$")
            price.place(
                x=569.0,
                y=197.0 + (index * 43),
                width=78.0,
                height=41.0
            )
            expireDate = Entry(
                bd=0,

                fg="#000716",
                highlightthickness=0
            )
            expireDate.insert(0, i["expire_date"].strftime('%Y-%m-%d'))
            expireDate.place(
                x=647.0,
                y=197.0 + (index * 43),
                width=133.0,
                height=41.0
            )
            button_image_4 = PhotoImage(
                file=self.relative_to_assets("confirm.png"))

            def update_item_data(item_name_widget, item_description_widget, quantity_widget, price_widget, expire_date_widget):

                def on_click():
                    item_content = item_name_widget.get()
                    description_content = item_description_widget.get()
                    quantity_content = quantity_widget.get()
                    price_content = price_widget.get()
                    expireDate_content = expire_date_widget.get()
                    print(item_content, description_content,
                          quantity_content, price_content, expireDate_content)
                    update_item(item_content, description_content,
                                price_content, quantity_content, expireDate_content)
                    self.parent.switch_to_admin()
                return on_click
            button_4 = Button(
                image=button_image_4,
                borderwidth=0,
                highlightthickness=0,
                command=update_item_data(
                    item_name, description, quantity, price, expireDate),
                relief="flat",
            )
            button_4.image = button_image_4
            button_4.place(
                x=799.0,
                y=202.0 + (index * 43),
                width=33.0,
                height=33.0
            )

        canvas.create_text(
            510.0,
            197.0,
            anchor="nw",
            text="23",
            fill="#000000",
            font=("Inter", 16 * -1)
        )

        canvas.create_text(
            510.0,
            240.0,
            anchor="nw",
            text="23",
            fill="#000000",
            font=("Inter", 16 * -1)
        )


if __name__ == "__main__":
    load_dotenv()
    connection = None

    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=int(os.getenv("PORT")), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
        cursor = connection.cursor()
        app = TkinterApp()
        app.mainloop()
    except Exception as e:
        print(e)
        print("Something whent wrong")
    else:
        print("Database connected")
