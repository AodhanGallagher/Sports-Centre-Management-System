"""Module providing logging functionality and Flask framework"""
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_babel import Babel
from flask_login import LoginManager

logging.basicConfig(filename='flask.log', level=logging.DEBUG)

app = Flask(__name__)

app.config.from_object('config')

db = SQLAlchemy(app)
login = LoginManager(app)

migrate = Migrate(app, db)
app.static_folder ='static'

admin = Admin(app, template_mode='bootstrap4')
babel = Babel(app)

from app import routes, models
