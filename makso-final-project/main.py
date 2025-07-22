from flask import Flask
from models.settings import db

from handlers.auth import auth_handlers
from handlers.main import main_handlers
from handlers.order import order_handlers
from handlers.admin import admin_handlers
from handlers.static import static_handlers

app = Flask(__name__)
app.register_blueprint(auth_handlers)
app.register_blueprint(main_handlers)
app.register_blueprint(order_handlers)
app.register_blueprint(admin_handlers)
app.register_blueprint(static_handlers)

db.create_all()

if __name__ == "__main__":
    app.run()