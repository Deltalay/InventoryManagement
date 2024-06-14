import pymysql.cursors
from dotenv import load_dotenv
import os
if __name__ == "__main__":
    load_dotenv()
    connection = None
    try:
        connection = pymysql.connect(host=os.getenv("HOST"), port=os.getenv("PORT"), database=os.getenv(
            "DATABASE"), user=os.getenv("USER"), password=os.getenv("PASSWORD"), cursorclass=pymysql.cursors.DictCursor)
    except Exception as e:
        print("Something whent wrong")
    else:
        print("Database connected")
    
