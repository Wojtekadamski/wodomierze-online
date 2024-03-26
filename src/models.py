import string
from datetime import datetime
from random import random

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy.orm import backref
from werkzeug.security import generate_password_hash, check_password_hash


login_manager = LoginManager()

db = SQLAlchemy()


def init_db(app):
    db.init_app(app)

def generate_random_id(length):
    characters = string.ascii_letters + string.digits
    random_id = ''.join(random.choice(characters) for _ in range(length))
    return random_id

def is_random_id_unique(random_id):
    existing_user = User.query.filter_by(random_id=random_id).first()
    return existing_user is None

def get_user_by_random_id(random_id):
    user = User.query.filter_by(random_id=random_id).first()
    return user

class Meter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    radio_number = db.Column(db.String(64), unique=True, index=True)
    device_number = db.Column(db.String(128), nullable=True)
    type = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    readings = db.relationship('MeterReading', backref='meter', lazy='dynamic')
    name = db.Column(db.String(100), nullable=True)
    events = db.relationship('Event', backref='meter', lazy=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    address = db.relationship('Address', backref='meter', lazy=True)
    edit_histories = db.relationship('MeterEditHistory', backref='meter', cascade='all, delete-orphan')
    # Relacja do śledzenia, który superużytkownik posiada licznik
    superuser_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    superuser_owner = db.relationship('User', foreign_keys=[superuser_id], backref='owned_meters')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
   # random_id = generate_random_id(10)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    meters = db.relationship('Meter', foreign_keys=[Meter.user_id], backref='user', lazy='dynamic')
    is_active = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text)
    is_superuser = db.Column(db.Boolean, default=False)
    superuser_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # Relacja do przypisania użytkowników do superużytkownika
    assigned_users = db.relationship('User', backref=db.backref('superuser', remote_side=[id]), lazy='dynamic')
    unread_messages = db.Column(db.Integer, default=0)
    report_months = db.relationship('UserReportMonth', backref='user', lazy='dynamic')




    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)







class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    reading_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    value = db.Column(db.String(20), nullable=True)
    first_occurrence = db.Column(db.DateTime, nullable=True)
    last_occurrence = db.Column(db.DateTime, nullable=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'), nullable=False)
    number_of_occurrences = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=True)
    duration = db.Column(db.DateTime, nullable=True)

class MeterReading(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reading = db.Column(db.Float)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'))

    def __repr__(self):
        return f"Meter(id={self.id}, radio_number='{self.meter_id.radio_number}', type='{self.type}', user_id={self.user_id}, name='{self.name}')"

    def get_reading_for_month(self, month):
        return self.query.filter(db.extract('month', MeterReading.date) == month).first().reading


class UserValidationLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link = db.Column(db.String(64))
    is_used = db.Column(db.Boolean, default=False)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref=backref('sent_messages', lazy=True))
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref=backref('received_messages', lazy=True))


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=True)
    street = db.Column(db.String(100), nullable=True)
    building_number = db.Column(db.String(10), nullable=True)
    apartment_number = db.Column(db.String(32), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)


class MeterEditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meter_id = db.Column(db.Integer, db.ForeignKey('meter.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    edit_type = db.Column(db.String(50), nullable=False)
    edit_details = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MeterEditHistory {self.id}>'


class UserReportMonth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)  # Numer miesiąca (1-12)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_all_users():
    users = User.query.all()
    user_list = []
    for user in users:
        user_dict = {
            'id': user.id,
            'email': user.email,
            'is_admin': user.is_admin,
        }
        user_list.append(user_dict)
    return user_list

