import os
import sqlite3
from sqlite3 import Error


global DEFAULT_PATH
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'orderDb.db')

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
    sql_create_table = """ CREATE TABLE IF NOT EXISTS orderDb (
        cust_phone_no integer PRIMARY KEY,
        shop_phone_no integer NOT NULL,
        order_content text NOT NULL,
        content_bool boolean,
        order_price text,
        price_bool boolean,
        order_confirm text NOT NULL
    ); """

    conn = db_connect(DEFAULT_PATH)

    if conn is not None:
        db_table(conn, sql_create_table)
    else:
        print("Error, couldn't create the database/table.")


def insert_order(conn, item):
    sql = """ INSERT INTO orderDb(cust_phone_no, shop_phone_no, order_content, content_bool, price_bool, order_confirm)
    VALUES(?,?,?,?)
    """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def insert_price(conn, item):
    sql = """ UPDATE orderDb SET order_price=? WHERE shop_phone_no=? """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def order_confirm(conn, item):
    sql = """ UPDATE orderDb SET order_confirm=? WHERE shop_phone_no=? """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def delete_order(conn, item):
    sql = """ DELETE * FROM orderDb WHERE cust_phone_no=? """
    cur = conn.cursor()
    cur.execute(sql, item)
    conn.commit()


def main():
    conn = db_connect(DEFAULT_PATH)
    # make_table()

if __name__ == '__main__':
    main()
