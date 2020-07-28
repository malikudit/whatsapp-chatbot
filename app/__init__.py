from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


def _update_db(obj):
    db.session.add(obj)
    db.session.commit()
    return obj

def _delete_item(obj):
    db.session.delete(obj)
    db.session.commit()

from app import routes, models
