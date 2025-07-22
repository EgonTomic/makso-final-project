from flask import Blueprint, render_template, request, redirect, url_for
from models.settings import db
from models.Order import Order
from models.Customer import Customer

admin_handlers = Blueprint("admin", __name__)

@admin_handlers.route("/admin")
def admin_dashboard():
    session_token = request.cookies.get("session_token")
    customer = db.query(Customer).filter_by(session_token=session_token).first()

    if not customer or not customer.is_admin:
        return redirect(url_for("auth.login"))

    all_orders = db.query(Order).order_by(Order.datetime.desc()).all()
    return render_template("admin.html", orders=all_orders)