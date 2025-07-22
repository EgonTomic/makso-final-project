import os
from sqla_wrapper import SQLAlchemy

db_url = os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite?check_same_thread=False")
db = SQLAlchemy(db_url)