from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from models.settings import db
from models.Order import Order
from models.Customer import Customer
from models.Invoice import Invoice
from datetime import datetime, timedelta
from datetime import datetime as dt
from sqlalchemy import func
import pytz
from utils.csrf_utils import create_csrf_token, validate_csrf_token

order_handlers = Blueprint("order", __name__)

@order_handlers.route("/order", methods=["GET", "POST"])
def order_page():
    price_map = {
        "VIP Treatment": 36.0,
        "Modern Haircut + Beard Styling": 28.0,
        "Long Haircut": 22.0,
        "Modern Haircut + Hair Wash": 22.0,
        "Modern Haircut": 18.0,
        "Buzz Cut + Beard Styling": 23.0,
        "Buzz Cut": 13.0,
        "Hot Towel Shave": 13.0,
        "Beard Styling": 10.0,
        "Machine Shave": 5.0,
        "Beard Coloring": 7.0
    }

    session_token = request.cookies.get("session_token")
    customer = db.query(Customer).filter_by(session_token=session_token).first()

    if not customer:
        return redirect(url_for("auth.login"))
    if customer.is_admin:
        return redirect(url_for("admin.admin_dashboard"))

    if request.method == "GET":
        csrf_token = create_csrf_token(customer.email_address)
        zagreb_tz = pytz.timezone("Europe/Zagreb")
        now_hr = datetime.now(zagreb_tz)
        return render_template("order.html",
                               customer=customer,
                               current_date=now_hr.strftime("%Y-%m-%d"),
                               csrf_token=csrf_token,
                               current_time=now_hr.strftime("%H:%M"))

    elif request.method == "POST":
        form_csrf_token = request.form.get("csrf_token")
        if not validate_csrf_token(form_csrf_token, customer.email_address):
            return redirect(url_for("auth.login"))

        service = request.form.get("service")
        date = request.form.get("date")
        time = request.form.get("time")

        dt_string = f"{date} {time}"
        order_datetime = dt.strptime(dt_string, "%Y-%m-%d %H:%M")
        price = price_map.get(service)

        new_order = Order(service=service, price=price, datetime=order_datetime, customer_id=customer.id)
        db.add(new_order)
        db.commit()

        zagreb_tz = pytz.timezone("Europe/Zagreb")
        now_hr = datetime.now(zagreb_tz)
        due_date = now_hr + timedelta(days=7)

        new_invoice = Invoice(
            order_id=new_order.id,
            customer_id=customer.id,
            amount=price,
            issue_date=now_hr,
            due_date=due_date,
            status="pending"
        )

        db.add(new_invoice)
        db.commit()

        return redirect(url_for("main.index"))

@order_handlers.route("/full-days")
def full_days():
    MAX_REZERVATIONS_PER_DAY = 5
    zagreb_tz = pytz.timezone("Europe/Zagreb")
    now = datetime.now(zagreb_tz)

    today = now.date()
    current_time = now.time()
    available_times = ["13:00", "14:00", "15:00", "16:00", "17:00"]
    available_time_objs = [datetime.strptime(t, "%H:%M").time() for t in available_times]

    results = (
        db.query(func.date(Order.datetime), func.count(Order.id))
        .group_by(func.date(Order.datetime))
        .having(func.count(Order.id) >= MAX_REZERVATIONS_PER_DAY)
        .all()
    )
    full_dates = [str(r[0]) for r in results]

    today_orders = db.query(Order).filter(func.date(Order.datetime) == today).all()
    taken_times = [order.datetime.strftime("%H:%M") for order in today_orders]

    remaining_times = [
        t.strftime("%H:%M") for t in available_time_objs
        if t > current_time and t.strftime("%H:%M") not in taken_times
    ]

    if not remaining_times:
        full_dates.append(str(today))

    return jsonify(full_dates)

@order_handlers.route("/available-times")
def available_times():
    selected_date_str = request.args.get("date")

    try:
        selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify([])

    AVAILABLE_TIMES = ["13:00", "14:00", "15:00", "16:00", "17:00"]
    orders = db.query(Order).filter(func.date(Order.datetime) == selected_date).all()
    taken_times = [order.datetime.strftime("%H:%M") for order in orders]

    zagreb_tz = pytz.timezone("Europe/Zagreb")
    now = datetime.now(zagreb_tz)

    if selected_date == now.date():
        current_time_str = now.strftime("%H:%M")
        AVAILABLE_TIMES = [t for t in AVAILABLE_TIMES if t > current_time_str]

    free_times = [t for t in AVAILABLE_TIMES if t not in taken_times]
    return jsonify(free_times)