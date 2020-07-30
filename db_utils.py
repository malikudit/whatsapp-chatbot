import os
import sqlite3
from sqlite3 import Error

global DEFAULT_PATH
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'shop_data')

def db_connect(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(e)
    return conn


def db_table(conn, create_table_sql):
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def make_table():
    sql_create_table = """ CREATE TABLE IF NOT EXISTS shopDb (
        phone_no integer PRIMARY KEY,
        shop_name text NOT NULL,
        shopkeeper_name text,
        shop_pincode text NOT NULL
    ); """

    conn = db_connect(DEFAULT_PATH)

    if conn is not None:
        db_table(conn, sql_create_table)
    else:
        print("Error, couldn't create the database/table.")


def insert_in_table(conn, item):
    sql = """ INSERT INTO shopDb(phone_no, shop_name, shopkeeper_name, shop_pincode)
    VALUES(?,?,?,?)
    """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()
    return cur.lastrowid


def delete_from_table(conn, item):
    sql = """ DELETE FROM shopDb WHERE phone_no=? """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def show(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM shopDb")
    rows = cur.fetchall()
    for row in rows:
        print(row)


def main():
    conn = db_connect(DEFAULT_PATH)
    with conn:
        resp = "YES"
        resp = resp.strip().lower()
        while resp == "yes":
            decision = input("Type delete, add, or show to decide whether you want to add or delete a shop from the database: ")
            decision = decision.strip().lower()

            if decision == "add":
                phone = input("Enter the shopkeeper's phone number: ")
                shop_name = input("Enter the shop's name: ")
                shopkeeper = input("Enter the shopkeeper's name: ")
                pin = input("Enter the pincode of the shop: ")
                item = (phone, shop_name, shopkeeper, pin)
                insert_in_table(conn, item)

            elif decision == "delete":
                phone = input("Enter the phone number whose shop you want to delete: ")
                phone = phone.strip()
                delete_from_table(conn, phone)

            elif decision == "show":
                show(conn)
                
            else:
                print("Wrong input.")
            resp = input("Do you want to continue today? Type yes/no")

if __name__ == '__main__':
    main()
