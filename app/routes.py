from flask import request
from app import app, _update_db
from app.models import User, Order
from twilio.twiml.messaging_response import MessagingResponse

def _send_message(output_lines):
    resp = MessagingResponse()
    msg = resp.message()
    msg.body = ("\n".join(output_lines))
    return str(resp)

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.values.get("Body", "").strip().lower()
    remote_number = request.values.get("From", "")
    output_lines = []

    if remote_number.startswith("whatsapp:"):
        remote_number = remote_number.split(":")[1]
    
    if not remote_number:
        remote_number = "123"
    
    user = User.query.get(remote_number)

    if incoming_msg == "help":
        output_lines.append("'create account' - create a new account")
        output_lines.append("'new order' - start creating your order")
        output_lines.append("'finish order' - finish your order")
        output_lines.append("'past orders' - begin seeing your past orders")
        output_lines.append("'stop past orders' - stop seeing your past orders")
        return _send_message(output_lines)
    
    if not user:
        if incoming_msg == "create account":
            new_user = User(remote_number)
            _update_db(new_user)
            output_lines.append(
                f"Account successfully created for number {remote_number}!"
            )
            
        else:
            output_lines.append("Please register a new account by typing 'create account' first!")
        return _send_message(output_lines)
    else:
        if incoming_msg == "create account":
            output_lines.append("This number is already registered. Send 'help' for available options.")
            return _send_message(output_lines)
