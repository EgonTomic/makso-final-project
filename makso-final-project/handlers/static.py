from flask import Blueprint, render_template

static_handlers = Blueprint("static_pages", __name__)

@static_handlers.route("/about-me")
def about_me():
    return render_template("about-me.html")