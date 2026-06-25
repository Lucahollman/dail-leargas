from flask import Flask, g
import sqlite3

path = "dail-debates.db"

def get_database():
    database = getattr(g, "_database", None)
    if database is None:
        database = g._database = sqlite3.connect(path)
        database.row_factory = sqlite3.Row
    return database

def init_app():
    app = Flask(__name__)

    @app.teardown_appcontext
    def close_connection(exception):
        database = getattr(g, "_database", None)
        if database is not None:
            database.close()

    with app.app_context():
        from . import routes

    return app