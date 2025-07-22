import hashlib
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, make_response
from models.Customer import Customer
from models.settings import db

auth_handlers = Blueprint("auth", __name__)

@auth_handlers.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    
    email_address = request.form.get("email")
    password = request.form.get("password")

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    customer = db.query(Customer).filter_by(email_address=email_address).first()

    if not customer:
        return "Customer does not exist"
    
    if hashed_password != customer.password_hash:
        return "Wrong password"
    
    session_token = str(uuid.uuid4())
    customer.session_token = session_token
    customer.save()

    response = make_response(redirect(url_for("main.index")))
    response.set_cookie("session_token", session_token)
    return response

@auth_handlers.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")
    elif request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email_address = request.form.get("email_address")
        password = request.form.get("password")
        repeated_password = request.form.get("repeatpassword")
        phone = request.form.get("phone")

        if password != repeated_password:
            return "Passwords don't match. Please try again."

        customer = Customer(firstName=firstName, lastName=lastName, email_address=email_address, password_hash=hashlib.sha256(password.encode()).hexdigest(), 
                    session_token=str(uuid.uuid4()), phone=phone)
        
        db.add(customer)
        db.commit()

        response = make_response(redirect(url_for("main.index")))
        response.set_cookie("session_token", customer.session_token)
 
        return response

@auth_handlers.route("/logout")
def logout():
    response = make_response(redirect(url_for("auth.login")))
    response.delete_cookie("session_token")
    return response