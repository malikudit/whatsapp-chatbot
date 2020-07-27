from flask import request
from app import app, _update_db
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
    if incoming_msg == "help":
        output_lines.append("'create account' - create a new account")
        output_lines.append("'new order' - start your order")
        output_lines.append("'end order' - end your order")

        return _send_message(output_lines)


    # for a new user
    if not user:
        if incoming_msg == "create account":
            new_user = User(remote_number)
            _update_db(new_user)
            output_lines.append(
                f"Account successfully created for number {remote_number}!"
            )
            output_lines.append(
                "To get started, text 'new order' to start a new order. Add your pincode at the end of the order after a /"
            )
            output_lines.append(
                "When you're done, text 'finish order'."
            )
            output_lines.append(
                "Text 'help' at any time to see available commands."
            )
        else:
            output_lines.append("Please register first by texting 'create account'")
        
        return _send_message(output_lines)
    
    # for an existing user
    else:
        if incoming_msg == "create account":
            output_lines.append(f"You have already registered {remote_number}. Text help for available options, or 'new order'.")
            return _send_message(output_lines)
    

    # creating a new order
    if not user.creating_orders and incoming_msg == "new order":
        output_lines.append("Create a new order and send it as one single text below, with the pincode at the end after a /")
        user.creating_orders = True
        _update_db(user)
        return _send_message(output_lines)


    # ending a new order
    if user.creating_orders and incoming_msg == "finish order":
        output_lines.append("Order created.")
        user.creating_orders = False
        _update_db(user)
        return _send_message(output_lines)


    # checking order format
    if user.creating_orders:
        if "/" not in incoming_msg:
            output_lines.append(
                "Please include your pincode after a / at the end of your order."
            )
            output_lines.append("Text 'finish order' to end your order.")
            return _send_message(output_lines)
        else:
            message_parts = incoming_msg.split
            if len(message_parts) > 2:
                output_lines.append("More than one / was sent. Please use only one / in message.")
                return _send_message(output_lines)
            content = message_parts[0].strip()
            pincode = message_parts[1].strip()
            new_order = Order(user.phone_number, content, pincode)
            _update_db(new_order)
            output_lines.append(
                f"Order for pincode {pincode} created successfully."
            )
            return _send_message(output_lines)

    # error handling
    output_lines.append("Sorry, I don't understand, please try again or text 'help'.")
    return _send_message(output_lines)
