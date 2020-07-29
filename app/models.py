from app import db
from app import _update_db
from app import _delete_item

# database model for each individual user
class User(db.Model):
    __tablename__ = "users"

    phone_number = db.Column(db.Text, primary_key=True)
    pincode = db.Column(db.Text())
    name = db.Column(db.Text())
    creating_orders = db.Column(db.Boolean)
    # relationship because each user can be connected to multiple orders
    orders = db.relationship(
        "Order",
        backref = "user",
        primaryjoin = "User.phone_number == Order.user_id", 
    )
    
    def __init__(self, phone_number, name, pincode):
        self.phone_number = phone_number
        self.creating_orders = False
        self.pincode = pincode
        self.name = name


# database model for each individua order
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Text(), db.ForeignKey("users.phone_number"))
    content = db.Column(db.Text())

    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content
