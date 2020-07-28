from app import db, _update_db, _delete_item

class User(db.Model):
    __tablename__ = "users"

    phone_number = db.Column(db.Text, primary_key=True)
    pincode = db.Column(db.Text())
    orders = db.relationship(
        "Order",
        backref = "user",
        primaryjoin = "User.phone_number == Order.user_id", 
    )
    creating_orders = db.Column(db.Boolean)

    def __init__(self, phone_number, name, pincode):
        self.phone_number = phone_number
        self.creating_orders = False
        self.pincode = pincode


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text(), db.ForeignKey("users.phone_number"))
    content = db.Column(db.Text())

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content
