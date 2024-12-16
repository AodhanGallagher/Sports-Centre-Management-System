"""Modules containing required frameworks"""
from flask import render_template, flash, redirect, url_for, request, abort
import logging
from app import app, db, models, admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash
from .forms import LoginForm, RegistrationForm, MembershipForm, MembershipCancelButton, UserForm, SessionForm, \
    LocationForm, DiscountForm, CalendarForm, CustomerSelectButton, MembershipEditForm, ChangePasswordForm
from .models import Account, Booking, Membership, CardDetails, Location, Session, CalendarSlot, MembershipPurchase, BookingPurchase
import json
import datetime
from datetime import timedelta
import time
import stripe
from sqlalchemy import or_, and_
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import babel.numbers
import os

admin.add_view(ModelView(models.Account, db.session))
admin.add_view(ModelView(models.Membership, db.session))
admin.add_view(ModelView(models.CardDetails, db.session))
admin.add_view(ModelView(models.Booking, db.session))
admin.add_view(ModelView(models.CalendarSlot, db.session))
admin.add_view(ModelView(models.Session, db.session))
admin.add_view(ModelView(models.Location, db.session))
admin.add_view(ModelView(models.Discount, db.session))
admin.add_view(ModelView(models.BookingPurchase, db.session))
admin.add_view(ModelView(models.MembershipPurchase, db.session))


app.config['STRIPE_PUBLIC_KEY'] = 'pk_test_51MjrUdGGAQ4C4cfRu1DzjnuG9bM9t5cMR9KBsYJKN4wnws5G5rW4JYr2Td7imZ19W6SEmYnd' \
                                  'FbnM5MrpYdgr6bG900NQCftpeh'

app.config['STRIPE_SECRET_KEY'] = 'sk_test_51MjrUdGGAQ4C4cfRbVuZsjijB4EgEtpxzoOr0VAJVuEfwPOTsiJBrWTayeyAUn11z9HBluee' \
                                  'Iteh6LFFl1iDUtrM00ObN2Bg6Y'

stripe.api_key = 'sk_test_51MjrUdGGAQ4C4cfRbVuZsjijB4EgEtpxzoOr0VAJVuEfwPOTsiJBrWTayeyAUn11z9HBlueeIteh6LFFl1iDUtrM00' \
                 'ObN2Bg6Y'

stripe_webhook_secret = 'whsec_bfcd8b4290dd8da195b70ff216499f7261aecf207fabcd5fc30b576049bfa4ea'


@app.route('/')
def index():
    """Home method"""
    return render_template('home.html', title='GymCorp')


@app.route('/monthly_membership')
def monthly():
    if current_user.is_anonymous:
        return redirect(url_for('index'))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1MkBSyGGAQ4C4cfRS5rIUgC2',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:5000/dashboard',
            cancel_url='http://127.0.0.1:5000/dashboard',
            metadata={"user_id": current_user.id, "price": 35}
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@app.route('/annual_membership')
def annual():
    if current_user.is_anonymous:
        return redirect(url_for('index'))

    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': 'price_1MmJXXGGAQ4C4cfRJ200aSLf',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:5000/dashboard',
            cancel_url='http://127.0.0.1:5000/dashboard',
            metadata={"user_id": current_user.id, "price": 300},
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)

@app.route('/booking_nm/<slot_id>/<date>', methods=['GET', 'POST'])
def booking_nm(slot_id, date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

    # double-check the slot is available (not necessary since we have already checked, but its good practice)
    slot = models.CalendarSlot.query.filter_by(id=slot_id).first()
    location = models.Location.query.filter_by(id=slot.session.location_id).first()
    existing_bookings = models.Booking.query.filter_by(calendar_id=slot.id, date=date)

    if existing_bookings.count() >= location.capacity:
        # return an error, since the booking isn't available
        print("Can't book - at capacity!")
        return json.dumps({'status': 'ERROR', 'message': 'Slot booked up'})

    session = models.Session.query.filter(Session.slots.any(id=slot_id)).first()
    one_week_ago = datetime.date.today() - datetime.timedelta(days=6)

    acc = models.Account.query.filter_by(id=current_user.id).first()
    bookings = models.Booking.query.filter_by(account_id=acc.id)
    booking_purchases = []
    for booking in bookings:
        booking_purchase = booking.purchase
        if len(booking_purchase) != 0:
            booking_purchases.append(booking_purchase[0].purchase_date)
    valid_bookings = 0
    discount = 1
    for date in booking_purchases:
        if date >= one_week_ago:
            valid_bookings += 1

    if valid_bookings >= 2:
        discounts = models.Discount.query.first()
        if discounts is not None:
            discount = 1 - discounts.disc_amount/100

    try:
        price = stripe.Price.create(
            unit_amount=int(session.price*100*discount),
            currency="gbp",
            product="prod_NcFmccV53MG7tl",
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': price.id,
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://127.0.0.1:5000/dashboard',
            cancel_url='http://127.0.0.1:5000/dashboard',
            metadata={"user_id": current_user.id, "slot_id": slot_id, "date": date, "price": session.price*discount}
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)



@app.route("/stripe_webhook", methods=["POST"])
def stripe_webhook():
    print('hello world!')
    event = None
    payload = request.data
    signature = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, signature, stripe_webhook_secret)
    except Exception as e:
        # the payload could not be verified
        abort(400)

    if event['type'] == 'checkout.session.completed':
        session = stripe.checkout.Session.retrieve(
            event['data']['object'].id, expand=['line_items'])

        print(f'Sale to {session.customer_details.email}:')
        print(f'User id is {session.metadata.user_id}')
        for item in session.line_items.data:
            if item.description == "membership":
                checkout_session_object = Membership(start_date=datetime.date.today(),
                                                     type=0,
                                                     account=models.Account.query.filter_by(
                                                         id=session.metadata.user_id).first())
                db.session.add(checkout_session_object)
                db.session.commit()

                membership_purchase = MembershipPurchase(total=session.metadata.price, membership_id=checkout_session_object.id,
                                                         purchase_date=datetime.date.today())
                db.session.add(membership_purchase)
                db.session.commit()

            elif item.description == "Annual Membership":
                checkout_session_object = Membership(start_date=datetime.date.today(),
                                                     type=1,
                                                     account=models.Account.query.filter_by(
                                                         id=session.metadata.user_id).first())
                db.session.add(checkout_session_object)
                db.session.commit()

                membership_purchase = MembershipPurchase(total=session.metadata.price,
                                                         membership_id=checkout_session_object.i,
                                                         purchase_date=datetime.date.today())
                db.session.add(membership_purchase)
                db.session.commit()

            elif item.description == "Session":
                date = datetime.datetime.strptime(session.metadata.date, '%Y-%m-%d')
                # create a new entry in the booking table for this user, calendar slot and date
                new_booking = Booking(account_id=session.metadata.user_id, calendar_id=session.metadata.slot_id,
                                      date=date)
                db.session.add(new_booking)
                db.session.commit()
                booking_purchase = BookingPurchase(total=session.metadata.price, booking_id=new_booking.booking_id,
                                                   purchase_date=datetime.date.today())
                db.session.add(booking_purchase)
                db.session.commit()
                return redirect(url_for("dashboard"))

            print(f'  - {item.quantity} {item.description} '
                  f'${item.amount_total / 100:.02f} {item.currency.upper()}')

    return {'success': True}


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login method"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Create form object
    form = LoginForm()
    if form.validate_on_submit():
        # Query for user and store their account record in user
        user = Account.query.filter_by(username=form.username.data).first()
        # Checks if username is not present or password is incorrect
        if user is None or not user.check_password(form.password.data):
            flash('Username or password is invalid!', 'error')
            return redirect(url_for('login'))
        # Logs in the user
        login_user(user, form.remember_me.data)
        return redirect(url_for('dashboard'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Login method"""
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    # Log out user
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    """Registration method"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # Create form object
    form = RegistrationForm()
    if form.validate_on_submit():
        # Creates a row entry in account using the forms data
        # Defaults privilege to 0
        form_entry = Account(username=form.username.data, forename=form.forename.data, surname=form.surname.data,
                             email=form.email.data, privilege=0)
        # Sets the password
        form_entry.set_password(form.password.data)
        # Add the form entry and commit to db
        db.session.add(form_entry)
        db.session.commit()
        flash('You have registered!', 'success')
        return redirect(url_for('login'))
    return render_template('registration.html', title='Registration', form=form)


@app.route('/account')
def account():
    """Account method"""
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    
    return render_template('account.html', title='Account',
                            forename=current_user.forename,
                            surname=current_user.surname,
                            username=current_user.username,
                            email=current_user.email)
    


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if current_user.is_anonymous:
        return redirect(url_for('index'))

    form = ChangePasswordForm()

    user_id = current_user.get_id()
    account_record = Account.query.filter_by(id=user_id).first_or_404()

    if form.validate_on_submit():
        account_record.set_password(form.password.data)
        db.session.add(account_record)
        db.session.commit()
        return redirect(url_for('account'))
    
    return render_template('change_password.html', title='Change Password', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    """Dashboard method"""
    if current_user.is_anonymous:
        return redirect(url_for('index'))

    # Query for the account record for the user and store in user_info
    user_info = Account.query.filter_by(id=current_user.id).first()
    # Query for the membership record for the user and store in membership_info
    membership_info = models.Membership.query.filter(Membership.account.has(id=current_user.id)).first()

    slots = models.CalendarSlot.query.all()
    session_data = []
    for slot in slots:
        session_data.append(slot.id)

    # Lists needed to store info about user booked sessions
    booked_sessions = []
    names = []
    dates = []
    times = []
    durations = []
    locations = []
    ids = []

    # A series of statements to query the database and store relevant data about user booked sessions in lists
    user_sessions = user_info.sessions
    for session in user_sessions:
        if session.date >= datetime.date.today():
            session_calander_slot = models.CalendarSlot.query.filter_by(id=session.calendar_id).first()
            if session_calander_slot.time >= datetime.time():
                dates.append(session.date)

                calendar_info = models.CalendarSlot.query.filter_by(id=session.calendar_id).first()
                times.append(calendar_info.time)

                session_info = models.Session.query.filter_by(id=calendar_info.session_id).first()
                names.append(session_info.name)
                durations.append(session_info.duration)

                location_info = models.Location.query.filter_by(id=session_info.location_id).first()
                locations.append(location_info.name)

                ids.append(session.booking_id)

    # Loop used to store the data for each session in a list of lists
    for i in range(len(names)):
        booked_sessions.append([])
        for j in range(1):
            booked_sessions[i].append(ids[i])
            booked_sessions[i].append(names[i])
            booked_sessions[i].append(dates[i])
            booked_sessions[i].append(locations[i])
            booked_sessions[i].append(durations[i])

    return render_template('dashboard.html', title='Dashboard',
                           user_info=user_info, membership_info=membership_info,
                           booked_sessions=booked_sessions, id=ids, session_data=session_data)


def get_weekly_revenue_axes(date, session_id=None, location_id=None):
    """
    Take a provided date object and return two 7-lists of the past 7 days (including the provided date) and the revenue
    on each day, respectively. These can be fed into MPL for graphing.

    Args:
        date (Date): A Date object representing the date to work back from
        session_id (int): An optional parameter to filter by session - provide EITHER this or location_id
        location_id (int): An optional parameter to filter by location - provide EITHER this or session_id

    Returns:
        dates (list<Date>): A 7-list of Date objects from the past 7 days (including the provided date), and
        daily_revenue (list<float>): A 7-list of floats, or
    """

    dates = []
    for i in range(6, 0, -1):
        # add the previous 6 days' Date objects to the dates array
        dates.append(date - timedelta(days=i))
    # add the given day as the final element
    dates.append(date)

    # build a query to get all membership purchases in the past seven days
    query = or_((MembershipPurchase.purchase_date == dates[0]),
                (MembershipPurchase.purchase_date == dates[1]),
                (MembershipPurchase.purchase_date == dates[2]),
                (MembershipPurchase.purchase_date == dates[3]),
                (MembershipPurchase.purchase_date == dates[4]),
                (MembershipPurchase.purchase_date == dates[5]),
                (MembershipPurchase.purchase_date == dates[6]))

    # run the query that we have built
    membership_purchases = models.MembershipPurchase.query.filter(query).all()

    # now look at booking purchases!
    # build a query to get all booking purchases in the past seven days
    query = or_((BookingPurchase.purchase_date == dates[0]),
                (BookingPurchase.purchase_date == dates[1]),
                (BookingPurchase.purchase_date == dates[2]),
                (BookingPurchase.purchase_date == dates[3]),
                (BookingPurchase.purchase_date == dates[4]),
                (BookingPurchase.purchase_date == dates[5]),
                (BookingPurchase.purchase_date == dates[6]))

    all_booking_purchases = models.BookingPurchase.query.filter(query).all()
    booking_purchases = []

    # handle the filters
    if session_id and location_id:
        # if both a session_id and location_id are provided, we want the previous query AND both IDs to match
        for purchase in all_booking_purchases:
            booking = models.Booking.query.filter_by(booking_id=purchase.booking_id).first()
            calendar = models.CalendarSlot.query.filter_by(id=booking.calendar_id).first()
            session = models.Session.query.filter_by(id=calendar.session_id).first()
            location = models.Location.query.filter_by(id=session.location_id).first()
            if session.id == session_id and location.id == location_id:
                booking_purchases.append(purchase)
    elif session_id and not location_id:
        # if only a session_id is provided, we want the previous query AND the session ID to match
        for purchase in all_booking_purchases:
            booking = models.Booking.query.filter_by(booking_id=purchase.booking_id).first()
            calendar = models.CalendarSlot.query.filter_by(id=booking.calendar_id).first()
            session = models.Session.query.filter_by(id=calendar.session_id).first()
            print(type(session.id))
            print(type(session_id))
            if session.id == session_id:
                print("found a match for", session_id)
                booking_purchases.append(purchase)
    elif not session_id and location_id:
        # if only a session_id is provided, we want the previous query AND the location ID to match
        for purchase in all_booking_purchases:
            print(purchase.booking_id)
            booking = models.Booking.query.filter_by(booking_id=purchase.booking_id).first()
            calendar = models.CalendarSlot.query.filter_by(id=booking.calendar_id).first()
            session = models.Session.query.filter_by(id=calendar.session_id).first()
            location = models.Location.query.filter_by(id=session.location_id).first()

            if location.id == location_id:
                booking_purchases.append(purchase)
    else:
        # otherwise, don't filter - we just want all booking purchases
        booking_purchases = all_booking_purchases

    # set up Y axis list, temp variables and counts
    daily_revenues = [0] * 7
    ptr = daily_count = weekly_count = 0

    # calculate total sales
    for date in dates:
        # for each date
        for purchase in membership_purchases:
            # go over each membership purchase in the week
            if purchase.purchase_date == date:
                # if the purchase date is our current date, add to our daily count
                daily_count += purchase.total
        for purchase in booking_purchases:
            # go over each booking purchase in the week
            if purchase.purchase_date == date:
                print("date match!")
                # if the purchase date is our current date, add to our daily count
                daily_count += purchase.total

        # after getting all the totals we need, we can increment our weekly count
        weekly_count += daily_count
        # format the current revenue as a price string
        daily_revenues[ptr] = babel.numbers.format_currency(daily_count, "GBP", locale='en_UK')
        # increment the pointer and reset daily count
        ptr += 1
        daily_count = 0

    # for i in range(len(dates)):
    #     # convert all dates to strings
    #     dates[i] = dates[i].strftime('%Y-%m-%d')

    name = f"Revenue from {dates[0]} to {dates[6]}"

    return dates, daily_revenues, weekly_count, name


def mpl_plot_revenue_to_dates(dates, daily_revenue, name):
    """
    Use MPL to take two same-length lists of dates and daily revenue (X and Y respectively) and plot to a graph

    Args:
        dates (list<str>): A list of the Date objects that correspond to the daily revenues
        daily_revenue (list<float>): A list of the daily revenues that correspond to the Date objects
        name (str): The name of the graph
    Returns:
        A link to the .PNG graph file that has been created
    """
    # plot using matplotlib
    x = dates
    y = daily_revenue

    plt.plot(x, y)
    plt.gcf().autofmt_xdate()

    # Labels
    plt.xlabel("Dates")
    plt.ylabel("Daily Revenue (£)")

    # Title
    plt.title(name)

    # Style
    plt.style.use("seaborn-talk")

    try:
        # Save figure to directory
        plt.savefig('app/static/figure.png', bbox_inches='tight', facecolor="#f8f9fa", )
        plt.close()
    except FileNotFoundError:
        return ''
    # print the first sale just to check
    # print(sales[0].purchase_date)
    return '../static/figure.png'

@app.route('/management', methods=['GET', 'POST'])
def management():
    """Management method"""
    if current_user.is_anonymous or current_user.privilege < 2:
        return redirect(url_for('index'))

    # set up form objects
    user_form = UserForm()
    session_form = SessionForm()
    calendar_form = CalendarForm()
    location_form = LocationForm()
    discount_form = DiscountForm()

    if request.method == 'POST':
        # user form posted
        if user_form.validate_on_submit():
            if user_form.id.data is None:
                # add the entry
                form_entry = models.Account(username=user_form.username.data, forename=user_form.forename.data,
                                            surname=user_form.surname.data, email=user_form.email.data,
                                            privilege=user_form.privilege.data)
                # set default password a new user (Password123)
                form_entry.set_password('Password123')
                db.session.add(form_entry)
            else:
                # update the entry
                user = models.Account.query.filter_by(id=user_form.id.data).first()
                user.username = user_form.username.data
                user.forename = user_form.forename.data
                user.surname = user_form.surname.data
                user.email = user_form.email.data
                user.privilege = user_form.privilege.data
            db.session.commit()

        # user form posted
        if session_form.validate_on_submit():
            location_name = str(session_form.location.data)
            location = models.Location.query.filter_by(name=location_name).first()
            if session_form.id.data is None:
                # add the entry
                form_entry = models.Session(price=session_form.price.data, duration=session_form.duration.data,
                                            location=location, name=session_form.name.data)
                db.session.add(form_entry)
            else:
                # update the entry
                session = models.Session.query.filter_by(id=session_form.id.data).first()
                session.price = session_form.price.data
                session.duration = session_form.duration.data
                session.location = location
                session.name = session_form.name.data
            db.session.commit()

        # calendar form posted
        if calendar_form.validate_on_submit():
            session_name = str(calendar_form.session.data)
            session = models.Session.query.filter_by(name=session_name).first()
            if calendar_form.id.data is None:
                # add the entry
                form_entry = models.CalendarSlot(weekday=calendar_form.weekday.data, time=calendar_form.time.data,
                                                 session=session)
                db.session.add(form_entry)
            else:
                # update the entry
                calendar_slot = models.CalendarSlot.query.filter_by(id=calendar_form.id.data).first()
                calendar_slot.weekday = calendar_form.weekday.data
                calendar_slot.time = calendar_form.time.data
                calendar_slot.session = session
            db.session.commit()

        # location form posted
        if location_form.validate_on_submit():
            if location_form.id.data is None:
                # add the entry
                form_entry = models.Location(name=location_form.name.data, opening_time=location_form.opening_time.data,
                                             closing_time=location_form.closing_time.data,
                                             capacity=location_form.capacity.data)
                db.session.add(form_entry)
            else:
                # update the entry
                location = models.Location.query.filter_by(id=location_form.id.data).first()
                location.name = location_form.name.data
                location.opening_time = location_form.opening_time.data
                location.closing_time = location_form.closing_time.data
                location.capacity = location_form.capacity.data
            db.session.commit()

        # discount form posted
        if discount_form.validate_on_submit():
            if discount_form.id.data is None:
                # add the entry
                form_entry = models.Discount(disc_amount=discount_form.disc_amount.data)
                db.session.add(form_entry)
            else:
                # update the entry
                discount = models.Discount.query.filter_by(id=discount_form.id.data).first()
                discount.disc_amount = discount_form.disc_amount.data
            db.session.commit()

    # open the management page

    # generate total revenue mpl graph
    # get today's date
    date = datetime.date.today()
    # get arrays of the past 7 days' Date objects and their daily revenues
    dates, daily_revenues, weekly_revenue, name = get_weekly_revenue_axes(date)
    # calculate the total revenue
    total_revenue = babel.numbers.format_currency(weekly_revenue, "GBP", locale='en_UK')
    image_url = mpl_plot_revenue_to_dates(dates, daily_revenues, name)

    return render_template('management.html', title='Manager Dashboard', userForm=user_form, sessionForm=session_form,
                           calendarForm=calendar_form, locationForm=location_form, discountForm=discount_form,
                           revenue=total_revenue, image=image_url)


@app.route('/membership', methods=['GET', 'POST'])
def membership():
    """Membership method"""
    if current_user.is_anonymous:
        return redirect(url_for('index'))
    # Query for the account record for the user and store in user_info
    user_info = Account.query.filter_by(id=current_user.id).first()
    # Create form object
    form = MembershipForm()
    form_cancel = MembershipCancelButton()
    if form_cancel.validate_on_submit():
        # Query for the membership record for the user and store in entry
        entry = models.Membership.query.filter(Membership.account.has(id=current_user.id)).first()
        # Query for the account record for the user and store in update_entry
        update_entry = models.Account.query.filter_by(id=current_user.id).first()
        # Set account record to have no membership id
        update_entry.membership_id = None

        membership_purchase = models.MembershipPurchase.query.filter_by(membership_id=entry.id).first()
        if membership_purchase is not None:
            db.session.delete(membership_purchase)

        # Delete the membership entry
        db.session.delete(entry)
        # Commit changes to db
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('membership.html', title='Membership', form=form, user_info=user_info)

@app.route('/employee', methods=['GET', 'POST'])
def employee():
    """Membership method"""
    if current_user.is_anonymous or current_user.privilege == 0:
        return redirect(url_for('index'))
    user_info = Account.query.filter_by(id=current_user.id).first()
    customer_info = Account.query.filter_by(privilege=0).all()
    button = CustomerSelectButton()
    if button.validate_on_submit():
        i = 0
        for key in request.form.keys():
            i = i + 1
            if i == 2:
                return redirect(url_for('employee_change', customer_id=key))
    return render_template('employee.html', title='Employee', user_info=user_info, customer_info=customer_info, button=button)

@app.route('/employee/<customer_id>', methods=['GET', 'POST'])
def employee_change(customer_id):
    customer_entry = Account.query.filter_by(id=customer_id).filter_by(privilege=0).first()
    if customer_entry is None:
        return redirect(url_for('employee'))
    if current_user.is_anonymous or current_user.privilege == 0:
        return redirect(url_for('index'))
    membership_entry = models.Membership.query.filter(Membership.account.has(id=customer_id)).first()
    membership_edit_form = MembershipEditForm()
    membership_cancel_form = MembershipCancelButton()
    membership_add_form = MembershipEditForm()
    if membership_edit_form.validate_on_submit():
        if 'submitMembership' in request.form:
            membership_entry.start_date = membership_edit_form.start_date.data
            membership_entry.type = membership_edit_form.type.data
            db.session.commit()
            return redirect(url_for('employee_change', customer_id=customer_id))
    if membership_cancel_form.validate_on_submit():
        if 'cancelMembership' in request.form:
            db.session.delete(membership_entry)
            db.session.commit()
            return redirect(url_for('employee_change', customer_id=customer_id))
    if membership_add_form.validate_on_submit():
        if 'addMembership' in request.form:
            form_entry = Membership(start_date=membership_add_form.start_date.data, type=membership_add_form.type.data, account=models.Account.query.filter_by(id=customer_id).first())
            db.session.add(form_entry)
            db.session.commit()
            return redirect(url_for('employee_change', customer_id=customer_id))

    # # Query for the account record for the user and store in user_info
    # user_info = Account.query.filter_by(id=current_user.id).first()
    # # Query for the membership record for the user and store in membership_info
    # membership_info = models.Membership.query.filter(Membership.account.has(id=current_user.id)).first()

    slots = models.CalendarSlot.query.all()
    session_data = []
    for slot in slots:
        session_data.append(slot.id)

    # Lists needed to store info about user booked sessions
    booked_sessions = []
    names = []
    dates = []
    times = []
    durations = []
    locations = []
    ids = []

    # A series of statements to query the database and store relevant data about user booked sessions in lists
    user_sessions = customer_entry.sessions
    for session in user_sessions:
        if session.date >= datetime.date.today():
            session_calander_slot = models.CalendarSlot.query.filter_by(id=session.calendar_id).first()
            if session_calander_slot.time >= datetime.time():
                dates.append(session.date)

                calendar_info = models.CalendarSlot.query.filter_by(id=session.calendar_id).first()
                times.append(calendar_info.time)

                session_info = models.Session.query.filter_by(id=calendar_info.session_id).first()
                names.append(session_info.name)
                durations.append(session_info.duration)

                location_info = models.Location.query.filter_by(id=session_info.location_id).first()
                locations.append(location_info.name)

                ids.append(session.booking_id)

    # Loop used to store the data for each session in a list of lists
    for i in range(len(names)):
        booked_sessions.append([])
        for j in range(1):
            booked_sessions[i].append(ids[i])
            booked_sessions[i].append(names[i])
            booked_sessions[i].append(dates[i])
            booked_sessions[i].append(locations[i])
            booked_sessions[i].append(durations[i])

            # user_info = user_info, membership_info = membership_info,
            # booked_sessions = booked_sessions, id = id)

    return render_template('employee_change.html', title='Employee', id=customer_id, customer_id=customer_id, user_info=customer_entry, membership_entry=membership_entry, booked_sessions=booked_sessions, membership_edit_form=membership_edit_form, membership_cancel_form=membership_cancel_form, membership_add_form=membership_add_form)




# API routes
@app.route('/get-slots', methods=['POST'])
def get_slots():
    """
    API route for getting all slots or a particular day's slots. Note that it returns all slots (available or not)
    but has a boolean field for availability

    POST parameters:
        weekday (optional) - a case-insensitive weekday from 'monday' to 'sunday' TODO: UPDATE THESE
        table_name - the table to filter slots by (optional)
        row_id - the row to filter slots by (optional)
    Returns:
        session-data - sessions and their respective information (id, available, session_name, price, location, time)
    """

    # parse the json data - if we want a particular day, we should have a day set in the request
    row_id = None
    data = json.loads(request.data) or None

    # get table name (None if not provided) and try to parse row ID (default to None also)
    table_name = data.get('table_name')
    try:
        row_id = int(data.get('row_id'))
    except TypeError:
        pass

    # grab date parts from request
    day_num = data.get('weekday')
    year = data.get('year')
    month = data.get('month') + 1
    day = data.get('day')

    date = datetime.datetime(year, month, day).date()
    filteredSlots = []
    # query the sessions in question and put the data in a slots variable
    if 'weekday' in data:
        if table_name == "sessions":
            slots = models.CalendarSlot.query.filter_by(weekday=day_num)
            session = models.Session.query.filter_by(id=row_id).first()
            for slot in slots:
                if slot.session_id == session.id:
                    filteredSlots.append(slot)
        elif table_name == "locations":
            slots = models.CalendarSlot.query.filter_by(weekday=day_num)
            location = models.Location.query.filter_by(id=row_id).first()
            for slot in slots:
                slotSession = models.Session.query.filter_by(id=slot.session_id).first()
                if slotSession.location_id == location.id:
                    filteredSlots.append(slot)

        else:
            filteredSlots = models.CalendarSlot.query.filter_by(weekday=day_num)
    else:
        filteredSlots = models.CalendarSlot.query.all()

    # populate sessions_data with the information from the session variable
    # account for the session not being found in the database
    session_data = []
    for slot in filteredSlots:
        ''' To check if a session is available we want to query bookings for every booking at that time on that day
            Count the results of that query
            Compare this count to the location capacity
            available = (booking_count < capacity) ? true : false '''

        location = models.Location.query.filter_by(id=slot.session.location_id).first()

        existing_bookings = models.Booking.query.filter_by(calendar_id=slot.id, date=date)
        # default available to False
        available = False
        print("EBC: " + str(existing_bookings.count()) + " and capacity: " + str(location.capacity))
        if existing_bookings.count() < location.capacity:
            print("So available = true!")
            available = True

        print("Session available = " + str(available))
        print("EB count (" + str(existing_bookings.count()) + ") < Capacity (" + str(location.capacity) + ")")

        session_data.append({'id': slot.id,
                             'available': available,
                             'session_name': slot.session.name,
                             'price': slot.session.price,
                             'location': location.name,
                             'time': slot.time.strftime("%H:%M:%S")})

    # return a response to the javascript
    return json.dumps({'status': 'OK', 'response': session_data})


@app.route('/book-slot', methods=['POST'])
def book_slot():
    """
    API route for booking a slot for a user on a particular day

    POST parameters:
        slot_id    - the slot to book,
        account_id - the account to book the slot for,
        TODO: date - the date to book the slot for
    Returns:
        response.status = ERROR on booking an unavailable slot,
        response.status = OK on success
    """
    # parse the json data
    data = json.loads(request.data)
    slot_id = data.get('slot_id')
    account_id = data.get('account_id')
    unformatted_date = data.get('date')
    date = datetime.datetime.strptime(unformatted_date, '%Y-%m-%d')
    date = datetime.datetime.strptime(unformatted_date, '%Y-%m-%d').date()

    # date = datetime.datetime(data.get('year'), data.get('month'), data.get('day'))
    # default date to 01/01/22 for now until calendar is sorted!
    # TODO: when calendar is sorted, remove defaulting line below and uncomment POST data line above
    # date = datetime.datetime(2022, 1, 1)

    # double-check the slot is available (not necessary since we have already checked, but its good practice)
    slot = models.CalendarSlot.query.filter_by(id=slot_id).first()
    location = models.Location.query.filter_by(id=slot.session.location_id).first()
    existing_bookings = models.Booking.query.filter_by(calendar_id=slot.id, date=date)

    if existing_bookings.count() >= location.capacity:
        # return an error, since the booking isn't available
        print("Can't book - at capacity!")
        return json.dumps({'status': 'ERROR', 'message': 'Slot booked up'})

    # create a new entry in the booking table for this user, calendar slot and date
    new_booking = Booking(account_id=account_id, calendar_id=slot_id, date=date)
    db.session.add(new_booking)
    db.session.commit()

    print("Slot booked")
    # return confirmation in JSON
    return json.dumps({'status': 'OK', 'message': 'Slot booked'})


@app.route('/cancel-booking', methods=['GET', 'POST', 'DELETE'])
def cancel_booking():
    """
    API route for cancelling a booking (deleting the entry for a particular booking ID)

    POST parameters:
        booking_id - the ID of the booking to cancel
    Returns:
        response.status = ERROR on error,
        response.status = OK on success
    """
    # parse the json data
    data = json.loads(request.data)
    booking_id = data.get('booking_id')

    booking = models.Booking.query.filter_by(booking_id=booking_id).first()

    booking_purchase = models.BookingPurchase.query.filter_by(booking_id=booking_id).first()
    if booking_purchase is not None:
        db.session.delete(booking_purchase)

    db.session.delete(booking)
    db.session.commit()
    return json.dumps({'status': 'OK', 'message': 'Booking deleted'})


@app.route('/get-users', methods=['POST'])
def get_users():
    """
    API route for getting all users

    POST parameters:
        id - the id if a specific user is being queried (optional)
    Returns:
        user_data - users and their information (id, username, email, privilege)
    """
    try:
        data = json.loads(request.data)
        user_id = data.get('id')
    except:
        user_id = None

    users = []

    if user_id:
        user = models.Account.query.filter_by(id=user_id).first()
        users.append(user)
    else:
        # retrieves all users in the database.
        users = models.Account.query.all()

    # creates and then populates user_data with information from the account table,
    # creates a new entry for every account within the account table.
    user_data = []
    for user in users:
        has_membership = 'Yes'
        if not user.membership:
            has_membership = 'No'

        user_data.append({'id': user.id,
                          'username': user.username,
                          'forename': user.forename,
                          'surname': user.surname,
                          'email': user.email,
                          'has_membership': has_membership,
                          'privilege': user.privilege})

    response = {'name': 'users',
                'data': user_data}

    # returns a response to the javascript
    return json.dumps({'status': 'OK', 'response': response})


@app.route('/get-sessions', methods=['POST'])
def get_sessions():
    """
    API route for getting all sessions

    POST parameters:
        id - the id if a specific session is being queried (optional)
    Returns:
        session_data - sessions and their information (id, session_name, price, location, duration)
    """

    try:
        data = json.loads(request.data)
        session_id = data.get('id')
    except:
        session_id = None

    sessions = []

    if session_id:
        session = models.Session.query.filter_by(id=session_id).first()
        sessions.append(session)
    else:
        # retrieves all sessions in the database.
        sessions = models.Session.query.all()

    # creates and then populates session_data with information from the session table,
    # creates a new entry for every session within the session table.
    session_data = []
    for session in sessions:
        location = models.Location.query.filter_by(id=session.location_id).first()
        session_data.append({'id': session.id,
                             'name': session.name,
                             'price': session.price,
                             'location': location.id,
                             'location_name': location.name,
                             'duration': session.duration})

    response = {'name': 'sessions',
                'data': session_data}

    # returns a response to the javascript.
    return json.dumps({'status': 'OK', 'response': response})


@app.route('/get-calendar_slots', methods=['POST'])
def get_calendar_slots():
    """
    API route for getting all calendar slots

    POST parameters:
        id - the id if a specific session is being queried (optional)
    Returns:
        session_data - sessions and their information (id, session_name, price, location, duration)
    """

    try:
        data = json.loads(request.data)
        slot_id = data.get('id')
    except:
        slot_id = None

    slots = []

    if slot_id:
        slot = models.CalendarSlot.query.filter_by(id=slot_id).first()
        slots.append(slot)
    else:
        # retrieves all sessions in the database.
        slots = models.CalendarSlot.query.all()

    # creates and then populates session_data with information from the session table,
    # creates a new entry for every session within the session table.
    slot_data = []
    for slot in slots:
        session = models.Session.query.filter_by(id=slot.session_id).first()
        slot_data.append({'id': slot.id,
                          'weekday': slot.weekday,
                          'session': session.id,
                          'session_name': session.name,
                          'time': slot.time.strftime('%H:%M')})

    response = {'name': 'calendar_slots',
                'data': slot_data}

    # returns a response to the javascript.
    return json.dumps({'status': 'OK', 'response': response})


@app.route('/get-locations', methods=['POST'])
def get_locations():
    """
    API route for getting all locations

    POST parameters:
        id - the id if a specific location is being queried (optional)
    Returns:
        location_data - locations and their information (id, location_name, opening_time, closing_time, capacity)
    """

    try:
        data = json.loads(request.data)
        location_id = data.get('id')
    except:
        location_id = None

    locations = []

    if location_id:
        location = models.Location.query.filter_by(id=location_id).first()
        locations.append(location)
    else:
        # retrieves all locations in the database.
        locations = models.Location.query.all()

    # creates and then populates location_data with information from the location table,
    # creates a new entry for every location within the location table.
    location_data = []
    for location in locations:
        location_data.append({'id': location.id,
                              'name': location.name,
                              'opening_time': location.opening_time.strftime("%H:%M"),
                              'closing_time': location.closing_time.strftime("%H:%M"),
                              'capacity': location.capacity})

    response = {'name': 'locations',
                'data': location_data}
    # returns a response to the javascript
    return json.dumps({'status': 'OK', 'response': response})


@app.route('/get-discounts', methods=['POST'])
def get_discounts():
    """
    API route for getting all discounts

    POST parameters:
        id - the id if a specific discount is being queried (optional)
    Returns:
        discount_data - discounts and their information (id, discount_amount)
    """

    try:
        data = json.loads(request.data)
        discount_id = data.get('id')
    except:
        discount_id = None

    discounts = []

    if discount_id:
        discount = models.Discount.query.filter_by(id=discount_id).first()
        discounts.append(discount)
    else:
        # retrieves all discounts in the database.
        discounts = models.Discount.query.all()

    # creates and then populates discount_data with information from the discount table,
    # creates a new entry for every discount within the discount table.
    discount_data = []
    for discount in discounts:
        discount_data.append({'id': discount.id,
                              'disc_amount': discount.disc_amount})

    response = {'name': 'discounts',
                'data': discount_data}

    # returns a response to the javascript
    return json.dumps({'status': 'OK', 'response': response})


# Update user information from management page
@app.route('/update-user', methods=['POST'])
def update_user():
    # Grab data and print
    data = json.loads(request.data)
    print(data)
    return data


@app.route('/update-graph', methods=['POST'])
def update_graph():
    """
    API route for updating a graph (using filters for session or location)

    POST parameters:
        table_name - the table to filter by (optional)
        row_id - the id of the row to filter by (optional)
    Returns:
        weekly_revenue - the total revenue for that week
        graph_url - the url of the new graph
    """
    row_id = None
    data = json.loads(request.data)
    table_name = data.get('table_name')
    try:
        row_id = int(data.get('row_id'))
    except TypeError:
        pass

    name = ""

    if table_name == "sessions":
        # generate total revenue mpl graph (filter by session)
        # get today's date
        date = datetime.date.today()
        # get arrays of the past 7 days' Date objects and their daily revenues
        dates, daily_revenues, weekly_revenue, name = get_weekly_revenue_axes(date, session_id=row_id)
    elif table_name == "locations":
        # generate total revenue mpl graph (filter by location)
        # get today's date
        date = datetime.date.today()
        # get arrays of the past 7 days' Date objects and their daily revenues
        dates, daily_revenues, weekly_revenue, name = get_weekly_revenue_axes(date, location_id=row_id)
    else:
        # generate total revenue mpl graph (do not filter)
        # get today's date
        date = datetime.date.today()
        # get arrays of the past 7 days' Date objects and their daily revenues
        dates, daily_revenues, weekly_revenue, name = get_weekly_revenue_axes(date)

    # convert total revenue to a currency string
    total_revenue = babel.numbers.format_currency(weekly_revenue, "GBP", locale='en_UK')

    # plot the axes and name to a MLP graph and get a URL back
    graph_url = mpl_plot_revenue_to_dates(dates, daily_revenues, name)

    response = {'weekly_revenue': total_revenue,
                'graph_url': graph_url}

    # returns a response to the javascript
    return json.dumps({'status': 'OK', 'response': response})

