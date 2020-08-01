from flask import Flask
from flask import request
from twilio.twiml.messaging_response import MessagingResponse
import db_utils2


app = Flask(__name__)

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


@app.route("/bot2", methods=['POST'])
def bot2():
    incoming_msg = request.values.get("Body", "").strip().lower()
    remote_number = request.values.get("From", "")
    output_lines = []

    # storing the phone number
    if remote_number.startswith("whatsapp:"):
        remote_number = remote_number.split(":")[1]
    if not remote_number:
        remote_number = "123"

    # look for shopkeeper in shop database
    dir_path = "../admin/shopDb.db"
    conn = db_connect(dir_path)
    sql = """SELECT * FROM shopDb WHERE phone_no=?"""
    cur = conn.cursor()
    cur.execute(sql, (remote_number,))
    rows = cur.fetchall()
    
    dir_path2 = "../userbot/orderDb.db"
    conn2 = db_connect(dir_path2)
    sql2 = """SELECT * FROM orderDb WHERE shop_phone_no=?"""
    cur2 = conn2.cursor()

    if not rows:
        output_lines.append("You're not a valid user!")
    

    if incoming_msg == "check":   
        cur2.execute(sql2, (remote_number,))
        rows2 = cur2.fetchall()
        for row in rows:
            order_data = row[3]
            if order_data == True:
                output_lines.append("Customer has requested the following items: \n")
                output_lines.append(order_data)
                output_lines.append("\n Message 'no' to refuse the order, or quote a price with the following format: 'price 450'")
                return _send_message(output_lines)
            else:
                output_lines.append("No orders!")
                return _send_message(output_lines)

    if incoming_msg == "no":
        cur2.execute(sql2, (remote_number,))
        rows2 = cur2.fetchall()
        for row in rows:
            db_utils2.order_confirm(conn2, ("no", remote_number,))

if __name__ == '__main__':
    app.run()
