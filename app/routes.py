from flask import request
from app import app, _update_db, _delete_item
from app.models import User, Order
from twilio.twiml.messaging_response import MessagingResponse


def _send_message(output_lines):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("\n".join(output_lines))
    return str(resp)


@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    remote_number = request.values.get("From", "")
    output_lines = []

    # storing the phone number
    if remote_number.startswith("whatsapp:"):
        remote_number = remote_number.split(":")[1]
    if not remote_number:
        remote_number = "123"

    user = User.query.get(remote_number)

    # generic commands available
    if incoming_msg == "help" or incoming_msg == "hello" or incoming_msg == "hi" or incoming_msg == "hey" or incoming_msg == "namaste":
        output_lines.append("Welcome to the WhyQ chatbot! This is an automated message. Here is what this bot can do:\n")
        output_lines.append("You can create a new account by typing 'create account' followed by your first name and pincode")
        output_lines.append("Format: 'create account Rajesh 110019'\n")
        output_lines.append("'new' - start your order")
        output_lines.append("'end' - end your order")
        return _send_message(output_lines)

    # for a new user
    if not user:
        if incoming_msg.startswith("create account"):
            message_parts = incoming_msg.split(" ")
            count = len(message_parts)
            if count > 4 or count < 4:
                output_lines.append("Wrong format. Try again with the correct format 'create account NAME PINCODE")
                return _send_message(output_lines)
            name = message_parts[2].strip()
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
        # confirmation message
        if incoming_msg == "create account" or incoming_msg.startswith("create account"):
            output_lines.append(f"Account already exists!")
            output_lines.append("If you still want to continue, type 'confirm' to delete your current account.")
            return _send_message(output_lines)

        # account deletion
        if incoming_msg == "delete":
            output_lines.append("Account deleted! You can now create another account by typing the format 'create account NAME PINCODE'")
            _delete_item(user)
            return _send_message(output_lines)


    # creating a new order
    if not user.creating_orders and incoming_msg == "new":
        output_lines.append("Create a new order and send it below!")
        user.creating_orders = True
        _update_db(user)
        return _send_message(output_lines)


    # checking order format
    if user.creating_orders and incoming_msg != "end":
        content = incoming_msg
        new_order = Order(user.phone_number, content)
        _update_db(new_order)
        output_lines.append(
            f"Listening to your order now. Add your items, and when done, type 'end'"
        )
        return _send_message(output_lines)


    # ending a new order
    if user.creating_orders and incoming_msg == "end":
        output_lines.append("Order created successfully.")
        user.creating_orders = False
        _update_db(user)
        return _send_message(output_lines)


    # error handling
    output_lines.append("Sorry, I don't understand, please try again or text 'help'.")
    return _send_message(output_lines)
