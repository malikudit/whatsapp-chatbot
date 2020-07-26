from app import db, _update_db
import random


class User(db.Model):
    __tablename__ = "users"

    phone_number = db.Column(db.Text, primary_key=True)
    orders = db.relationship(
        "Order",
        backref="user",
        primaryjoin="User.phone_number == Order.user_id",
    )

    current_order_id = db.Column(db.Integer(), db.ForeignKey("orders.id"))
    current_order = db.relationship("Order", foreign_keys=[current_order_id])
    creating_orders = db.Column(db.Boolean)

    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.creating_orders = True

    def get_new_order(self):
        if not self.orders:
            return None
        new_order = random.choice(self.orders)
        self.current_review_id = new_order.id
        _update_db(self)
        return new_order

    def stop_order(self):
        self.current_order = None
        _update_db(self)
        return self
    

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    front = db.Column(db.Text())
    back = db.Column(db.Text())
    user_id = db.Column(db.Text(), db.ForeignKey("users.phone_number"))

    def __init__(self, user_id, front, back):
        self.user_id = user_id
        self.front = front
        self.back = back
