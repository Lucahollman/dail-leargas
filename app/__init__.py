from flask import Flask, g
from datetime import datetime, date
import sqlite3
from .filters import filters

path = "dail-debates.db"

def get_database():
    database = getattr(g, "_database", None)
    if database is None:
        database = g._database = sqlite3.connect(path)
        database.row_factory = sqlite3.Row
    return database

def init_app():
    app = Flask(__name__)
    filters(app)

    @app.teardown_appcontext
    def close_connection(exception):
        database = getattr(g, "_database", None)
        if database is not None:
            database.close()

    with app.app_context():
        from . import routes

    from .plotlydash.dashboard import create_dashboard
    app = create_dashboard(app)

    return app