from flask import request
from app import app
from app import _delete_item
from app import _update_db
from app.models import User
from app.models import Order
from twilio.twiml.messaging_response import MessagingResponse
import re
import sqlite3
import os
import db_utils2


# generic function to reply to user
def _send_message(output_lines):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("\n".join(output_lines))
    return str(resp)


# connect to shopDb
def db_connect(db_path):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except Error as e:
        print(e)
    return conn



@app.route("/bot", methods=["POST"])
def bot():
    global i
    global content
    
    incoming_msg = request.values.get("Body", "").strip().lower()
    remote_number = request.values.get("From", "")
    output_lines = []


    # storing the phone number
    if remote_number.startswith("whatsapp:"):
        remote_number = remote_number.split(":")[1]
    if not remote_number:
        remote_number = "123"
    user = User.query.get(remote_number)


    # for a new user
    if not user:
        # generic commands available
        if incoming_msg == "help" or incoming_msg == "hello" or incoming_msg == "hi" or incoming_msg == "hey" or incoming_msg == "namaste":
            output_lines.append("Welcome to the WhyQ chatbot! This is an automated message. Here is what this bot can do:\n")
            output_lines.append("You can create a new account by typing 'create account' followed by your first name and pincode")
            output_lines.append("Format: 'create account Rajesh 110019'\n")
            output_lines.append("'new' - start your order")
            output_lines.append("'end' - end your order")
            return _send_message(output_lines)

        # checking account creation
        if incoming_msg.startswith("create account"):
            message_parts = incoming_msg.split(" ")
            count = len(message_parts)
            if count > 4 or count < 4 or len(message_parts[3]) > 6 or len(message_parts[3]) < 6:
                output_lines.append("Wrong format. Try again with the correct format 'create account NAME PINCODE")
                return _send_message(output_lines)

            name = message_parts[2].strip()
            name = name.capitalize()
            pincode = message_parts[3].strip()
            new_user = User(remote_number, name, pincode)
            _update_db(new_user)
            output_lines.append(
                f"Account successfully created for {name}! Text 'new' to start your order."
            )

        else:
            output_lines.append("Please register first by texting 'create account' followed by your name and pincode.'")
            output_lines.append("Eg format: 'create account Rajesh 110019'")

        return _send_message(output_lines)


    # for an existing user
    if user:
        # generic commands available
        if incoming_msg == "help" or incoming_msg == "hello" or incoming_msg == "hi" or incoming_msg == "hey" or incoming_msg == "namaste":
            output_lines.append(f"Welcome back to WhyQ, {user.name}!")
            output_lines.append("'new' - start your order")
            output_lines.append("'end' - end your order")
            return _send_message(output_lines)

        # confirmation message
        if incoming_msg == "create account" or incoming_msg.startswith("create account"):
            output_lines.append(f"Account already exists!")
            output_lines.append("If you still want to continue, type 'delete' to delete your current account.")
            return _send_message(output_lines)

        # account deletion
        if incoming_msg == "delete":
            output_lines.append("Account deleted! You can now create another account by typing the format 'create account NAME PINCODE'")
            _delete_item(user)
            return _send_message(output_lines)


    # all code below accessible only to a user

    if not user.creating_orders:
        # reinitialising order as being empty
        content = []
        # starting a new order
        if incoming_msg == "new":
            output_lines.append("Create a new order and send it below!")
            user.creating_orders = True
            _update_db(user)
            return _send_message(output_lines)  


    # saving the order contents one by one
    if user.creating_orders:
        # adding items to the order
        content.append(incoming_msg)
        content.append("\n")
        if incoming_msg != "end":
            output_lines.append(
                f"Listening to your order now. Add your items, and when done, type 'end'"
            )
            return _send_message(output_lines)

        #ending the order
        else:
            user.creating_orders = False
            _update_db(user)
            content_string = ''.join(map(str, content))
            new_order = Order(user.phone_number, content_string)
            _update_db(new_order)
            dir_path = "../admin/shopDb.db"
            conn = db_connect(dir_path)

            # connected to the database
            if conn:
                cur = conn.cursor()
                sql = """SELECT * FROM shopDb WHERE shop_pincode=?"""
                cur.execute(sql, (user.pincode,))
                rows = cur.fetchall()
                if not rows:
                    output_lines.append("No shops available in your area, sorry!")
                    i = 0
                    conn.close()
                    return _send_message(output_lines)
                else:
                    i = 0
                    output_lines.append("Order created successfully. Please select your preferred shop now by typing the shop no: \n")
                    for row in rows:
                        i += 1
                        output_lines.append("Shop " + str(i))
                        output_lines.append("Shop Name: " + row[1])
                        output_lines.append("Phone Number: " + str(row[0]))
                        output_lines.append("Shopkeeper: " + row[2])
                        output_lines.append("Pincode: " + row[3])
                        output_lines.append("\n")
                        conn.close()
                    return _send_message(output_lines)    
            
            else:
                output_lines.append("Internal error: couldn't reach the database.")
                return _send_message(output_lines)
    
    
    if i != 0:
        dir_path = "../admin/shopDb.db"
        conn = db_connect(dir_path)
        dir_path2 = "orderDb.db"
        conn2 = db_connect(dir_path2)
        for x in range(i):
            if incoming_msg == str(x):

                # confirming the shop
                if conn:
                    cur2 = conn.cursor()
                    sql = """SELECT * FROM shopDb WHERE shop_pincode=?"""
                    cur2.execute(sql, (user.pincode,))
                    rows = cur2.fetchall()
                    temp = 0
                    for row in rows:
                        temp += 1
                        if temp == x:
                            # shop confirmed, sending data to orderDb
                            output_lines.append("Shop " + row[1] + " selected. Waiting for confirmation. Type 'check' to see order status.")
                            db_utils2.insert_order(conn2, remote_number, row[0], content_string, True, False, "maybe")
                            

    if incoming_msg == "check":
        dir_path2 = "orderDb.db"
        conn2 = db_connect(dir_path2)
        cur2 = conn.cursor()
        sql2 = """SELECT * FROM shopDb WHERE cust_phone_no=?"""
        cur2.execute(sql2, (remote_number,))
        rows = cur2.fetchall()
        for row in rows:
            if row[6] == "maybe":
                output_lines.append("Order hasn't been confirmed yet. Check again in a while!")
                return _send_message(output_lines)
            elif row[6] == "yes":
                output_lines.append("Order confirmed! The price of the order is: " + row[4])
            elif row[6] == "no":
                output_lines.append("Order has been refused by the vendor.")
                db_utils2.delete_order(conn2, (remote_number,))
    


    # error handling
    output_lines.append("Sorry, I don't understand, please try again or text 'help'.")
    return _send_message(output_lines)
