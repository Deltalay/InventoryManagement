import pymysql.cursors
import uuid  # Import uuid module for generating UUIDs


# Function to establish MySQL database connection
def connect_to_mysql():
    conn = None
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            user='root',
            password='neath1272006!',
            db='Categories'
        )
    except pymysql.Error as ex:
        print(f"PROBLEM WITH Database Connection: {ex}")
    else:
        print('Database Connection SUCCESS')

    return conn


# Function to setup database (create tables: ctg and item)
def setup_database(conn):
    try:
        with conn.cursor() as cursor:
            create_category_query = """
                CREATE TABLE IF NOT EXISTS ctg (
                    id CHAR(36) PRIMARY KEY NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            create_item_query = """
                CREATE TABLE IF NOT EXISTS item (
                    id CHAR(36) PRIMARY KEY NOT NULL,
                    category_id CHAR(36) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price VARCHAR(25) NOT NULL,
                    quantity INT NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expire_date TIMESTAMP,
                    update_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES ctg(id)
                )
            """
            cursor.execute(create_category_query)
            cursor.execute(create_item_query)

        print('Database setup completed successfully!')
    except pymysql.Error as e:
        print(f"Error setting up database: {e}")
    finally:
        conn.commit()


# Function to create a new category based on user input
def create_category(conn):
    try:
        while True:
            with conn.cursor() as cursor:
                print("\n*** Press 'x' to Exit ***\n")
                name = input("Enter category name: ")
                if name.lower() == 'x':
                    break

                category_id = str(uuid.uuid4())  # Generate UUID for category id
                query = "INSERT INTO ctg (id, name) VALUES (%s, %s)"
                cursor.execute(query, (category_id, name))
                conn.commit()

                print(f'Category "{name}" created successfully!')

                # Add items to the current category
                add_items_to_category(conn, category_id)

    except pymysql.Error as e:
        print(f"Error creating category: {e}")


# Function to add items to a specific category based on user input
def add_items_to_category(conn, category_id):
    try:
        while True:
            with conn.cursor() as cursor:
                item_id = input("Enter item ID: ")
                if item_id.lower() == 'x':
                    break

                name = input("Enter item name: ")
                if name.lower() == 'x':
                    break

                description = input("Enter item description: ")
                if description.lower() == 'x':
                    break

                price = input("Enter item price: ")
                if price.lower() == 'x':
                    break

                query = """
                    INSERT INTO item (id, category_id, name, description, price, quantity)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE quantity = quantity + 1
                """
                cursor.execute(query, (item_id, category_id, name, description, price, 1))  # Quantity defaulting to 1
                conn.commit()

                print(f'Item "{name}" added successfully to category ID {category_id}')

    except pymysql.Error as e:
        print(f"Error adding item: {e}")


# # Function to fetch all items
# def fetch_items(conn):
#     try:
#         with conn.cursor() as cursor:
#             query = """
#                 SELECT i.id, c.name as category_name, i.name, i.description, i.price, i.quantity
#                 FROM item i
#                 INNER JOIN ctg c ON i.category_id = c.id
#             """
#             cursor.execute(query)
#
#             for record in cursor:
#                 print("---------------- ")
#                 print("Item ID: ", record[0])
#                 print("Category: ", record[1])
#                 print("Name: ", record[2])
#                 print("Description: ", record[3])
#                 print("Price: ", record[4])
#                 print("Quantity: ", record[5])
#                 print()
#     except pymysql.Error as e:
#         print(f"Error fetching items: {e}")


# Main function to orchestrate the script
def main():
    conn = connect_to_mysql()

    if conn:
        try:
            setup_database(conn)

            # Create categories and add items
            create_category(conn)

            # # Fetch items after all categories and items are added
            # fetch_items(conn)

        finally:
            conn.close()
            print("Items successfully saved to category!")
            print("MySQL connection closed.")


if __name__ == "__main__":
    main()
