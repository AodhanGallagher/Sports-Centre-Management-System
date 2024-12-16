"""Module containing required form frameworks"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, BooleanField, PasswordField, \
    SubmitField, IntegerField, FloatField, SelectField, TimeField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, InputRequired, Optional, Length
from .models import Account, Location, Session
from app import db


# Design for the flask form that takes in user login data data
class LoginForm(FlaskForm):
    """Design for the flask form that takes in user login data"""
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    remember_me = BooleanField('Remember Me')


class RegistrationForm(FlaskForm):
    """Registration form class"""
    forename = StringField('Forename', validators=[DataRequired(), Length(min=1, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=1, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=500)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=5, max=50)])

    def validate_username(self, username):
        # Takes in the username and checks if it is in the database
        usernames = Account.query.filter_by(username=username.data).first()
        if usernames is not None:
            raise ValidationError('Use a different username!')

    def validate_email(self, email):
        # Takes in the email and checks if it is in the database
        emails = Account.query.filter_by(email=email.data).first()
        if emails is not None:
            raise ValidationError('Use a different email!')


class MembershipForm(FlaskForm):
    # Membership form class
    title = StringField('Title', validators=[DataRequired()])
    name_on_card = StringField('Name On Card', validators=[DataRequired()])
    acc_number = IntegerField('Account Number', validators=[DataRequired()])
    expiry_date = IntegerField('Expiry Date', validators=[DataRequired()])
    sec_number = IntegerField('Security Number', validators=[DataRequired()])
    type = SelectField('Membership Type', choices=[(0, 'Monthly'), (1, 'Annually')], validators=[DataRequired()])


class MembershipCancelButton(FlaskForm):
    # Form that allows for a button to be used to cancel membership
    pass


class CustomerSelectButton(FlaskForm):
    pass


class MembershipEditForm(FlaskForm):
    start_date = DateField('Start Date', validators=[DataRequired()])
    type = SelectField('Membership Type', choices=[(0, 'Monthly'), (1, 'Annually')], validators=[DataRequired()])


class UserForm(FlaskForm):
    id = IntegerField('Id', validators=[Optional()])
    forename = StringField('Forename', validators=[DataRequired(), Length(min=1, max=50)])
    surname = StringField('Surname', validators=[DataRequired(), Length(min=1, max=50)])
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=3, max=500)])
    privilege = SelectField('Privilege', choices=[(0, 'User'), (1, 'Employee'), (2, 'Manager')], validators=[DataRequired()])
    submit = SubmitField('Confirm')


def get_locations():
    return db.session.query(Location).all()


class SessionForm(FlaskForm):
    id = IntegerField('Id', validators=[Optional()])
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=100)])
    price = IntegerField('Price', validators=[DataRequired()])
    duration = IntegerField('Duration', validators=[DataRequired()])
    location = QuerySelectField('Location', query_factory=get_locations, validators=[DataRequired()])
    submit = SubmitField('Confirm')


def get_sessions():
    return db.session.query(Session).all()


class CalendarForm(FlaskForm):
    id = IntegerField('Id', validators=[Optional()])
    weekday = IntegerField('Weekday', validators=[DataRequired()])
    time = TimeField('Time', validators=[DataRequired()])
    session = QuerySelectField('Session', query_factory=get_sessions, validators=[DataRequired()])
    submit = SubmitField('Confirm')


class LocationForm(FlaskForm):
    id = IntegerField('Id', validators=[Optional()])
    name = StringField('Name', validators=[DataRequired()])
    opening_time = TimeField('Opening time', format='%H:%M', validators=[InputRequired()])
    closing_time = TimeField('Closing time', format='%H:%M', validators=[InputRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class DiscountForm(FlaskForm):
    id = IntegerField('Id', validators=[Optional()])
    disc_amount = IntegerField('Discount amount', validators=[DataRequired()])
    submit = SubmitField('Confirm')


class ChangePasswordForm(FlaskForm):
    """Change Passsword form class"""
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=50)])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password'), Length(min=5, max=50)])