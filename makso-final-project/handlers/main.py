from flask import Blueprint, render_template, redirect, request, url_for
from models.Customer import Customer
from models.Order import Order
from models.settings import db

main_handlers = Blueprint("main", __name__)

@main_handlers.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")
    customer = db.query(Customer).filter_by(session_token=session_token).first()

    if not customer:
        return redirect(url_for("auth.login"))
    
    if customer.is_admin:
        return redirect(url_for("admin.admin_dashboard"))

    customer_have_order = db.query(Order).filter_by(customer_id=customer.id).first()
    if not customer_have_order:
        return redirect(url_for("order.order_page"))

    orders = db.query(Order).filter_by(customer_id=customer.id).order_by(Order.datetime.desc()).all()
    return render_template("index.html", customer=customer, orders=orders)