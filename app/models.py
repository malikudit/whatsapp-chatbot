from app import db
from app import _update_db


class User(db.Model):
    __tablename__ = "users"

    phone_number = db.Column(db.Text, primary_key=True)
    orders = db.relationship(
        "Order",
        backref = "user",
        primaryjoin = "User.phone_number == Order.user_id", 
    )

    creating_orders = db.Column(db.Boolean)

    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.creating_orders = True


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text(), db.ForeignKey("users.phone_number"))
    content = db.Column(db.Text())
    pincode = db.Column(db.Text()) 

    def __init__(self, user_id, content, pincode):
        self.user_id = user_id
        self.content = content
        self.pincode = pincode
