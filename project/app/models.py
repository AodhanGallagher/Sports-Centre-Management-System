from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

day_nums = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday"
}

# Creates the Discount table, which holds the discount amount.
class Discount(db.Model):
    __tablename__ = 'discount'

    id = db.Column(db.Integer, primary_key=True)
    disc_amount = db.Column(db.Integer)

# Creates the Location table, which holds a location which many sessions can be linked to.
class Location(db.Model):
    __tablename__ = 'location'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    capacity = db.Column(db.Integer)
    sessions = db.relationship('Session', backref='location', lazy=True)

    def __repr__(self):
        return self.name

# Creates the Session table, which holds a session that booking slots can refer to.
class Session(db.Model):
    __tablename__ = 'session'

    id = db.Column(db.Integer, primary_key=True)
    price = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    slots = db.relationship('CalendarSlot', backref='session', lazy=True)
    name = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return self.name


# Creates the CalendarSlot table, which holds slots which sessions can be booked into by users.
class CalendarSlot(db.Model):
    __tablename__ = 'calendar'

    id = db.Column(db.Integer, primary_key=True)
    weekday = db.Column(db.Integer, nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    bookings = db.relationship('Booking', backref='calendar', lazy=True)
    time = db.Column(db.Time, nullable=False)

    # Returns username
    def __repr__(self):
        return "Session " + str(self.session_id) + " - " + day_nums.get(self.weekday) + " " + self.time.strftime("%H:%M")

# Creates the Booking table, which holds a session that users can book to at a specific time.
class Booking(db.Model):
    __tablename__ = 'booking'

    booking_id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    calendar_id = db.Column(db.Integer, db.ForeignKey('calendar.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    purchase = db.relationship('BookingPurchase', backref='booking', lazy=True)

# Creates the CardDetails table, which holds card details that users can use.
class CardDetails(db.Model):
    __tablename__ = 'card'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10))
    name_on_card = db.Column(db.String(100))
    acc_number = db.Column(db.Integer, unique=True)
    expiry_date = db.Column(db.Integer)
    sec_number = db.Column(db.Integer)
    accounts = db.relationship('Account', backref='card', lazy=True)

# Creates the Membership table, which holds details about a users membership.
class Membership(db.Model):
    __tablename__ = 'membership'
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.Date)
    type = db.Column(db.Integer)
    account = db.relationship('Account', backref='membership', uselist=False, lazy=True)
    purchase = db.relationship('MembershipPurchase', backref='membership', lazy=True)

# Creates the Account table, which can have card details and can refer to many bookings.
class Account(UserMixin, db.Model):
    __tablename__ = 'account'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    forename = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(500), unique=True)
    password_hash = db.Column(db.String(128))
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=True)
    sessions = db.relationship('Booking', backref='account', lazy=True)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=True)
    privilege = db.Column(db.Integer)

    # Returns username
    def __repr__(self):
        return self.username

    # Returns id
    def get_id(self):
        return self.id
    
    # Function to generate password hashes from a password
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # Function to check password against the hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Function that returns and loads the user account
    @login.user_loader
    def load_user(id):
        return Account.query.get(int(id))


# Creates Sales table, which holds information about booking sales
class BookingPurchase(db.Model):
    __tablename__ = 'booking_purchase'

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.booking_id'), nullable=False)
    purchase_date = db.Column(db.Date(), nullable=False)


# Creates MembershipSale table, which holds information about membership sales
class MembershipPurchase(db.Model):
    __tablename__ = 'membership_purchase'

    id = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    purchase_date = db.Column(db.Date(), nullable=False)
