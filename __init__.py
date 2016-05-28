from flask import Flask, redirect, url_for, request, session, abort
from functools import wraps
from flask_admin import Admin
from playhouse.flask_utils import FlaskDB ### useless
from peewee import SqliteDatabase
from werkzeug.routing import BaseConverter
from flask.ext.bcrypt import Bcrypt
from flask.ext.security.utils import encrypt_password
from datetime import date, timedelta
import logging


def login_required(handler):

    @wraps(handler)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for("login", next=request.url))
        else:
            return handler(*args, **kwargs)
    return decorated_function


def author_required(handler):

    @wraps(handler)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect(url_for("login", next=request.url))
        elif session.get("is_author") is None:
            return abort(403)
        else:
            return handler(*args, **kwargs)
    return decorated_function

def week_day_dates():
    """
    iterates though the current week day dates
    """
    week_day_date = date.today() - timedelta(days=date.today().weekday())
    for _ in range(7):
        yield week_day_date
        week_day_date += timedelta(days=1)

        
app = Flask(__name__)
app.config.from_object("settings")
db = FlaskDB(app)
bcrypt = Bcrypt(app)

admin = Admin(app, name='Time Sheets', template_mode='bootstrap3')


if app.debug:
    # Log all SQL queries:
    logger = logging.getLogger('peewee')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

class DateConverter(BaseConverter):
    """
    Date value converter from a string formated as "YYYY-MM-DD"
    """
    def to_python(self, value):
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()

    def to_url(self, value):
        return value.isoformat()
app.url_map.converters['date'] = DateConverter

import views