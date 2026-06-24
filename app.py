'''
Script that runs a website locally using a web framework
'''

from flask import Flask, render_template
from flask import g
import sqlite3
import json

app = Flask(__name__)
#Connecting to Database
path = r"dail-debates.db"
def get_database():
    database = getattr(g, '_database', None)
    if database is None:
        database = g._database = sqlite3.connect(path)
        database.row_factory = sqlite3.Row
    return database

@app.teardown_appcontext
def close_connection(exception):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

#Routes
#Home
@app.route("/")
def home():
    return render_template("home.html")

#Dáil Index Routes
@app.route("/overallstats")
def overallstats():
    stats = get_database().execute("select words, freq, prob from full_text").fetchall()
    return render_template("overallstats.html", full_text = stats)

@app.route("/tds")
def tds():
    return render_template("tdindex.html")

@app.route("/parties")
def parties():
    return render_template("partyindex.html")

@app.route("/votes")
def votes():
    return render_template("voteindex.html")

@app.route("/debates")
def debates():
    debates = get_database().execute("select id, title, date, category from debates").fetchall()
    return render_template("debateindex.html", debates = debates)

@app.route("/debates/<int:debate_id>")
def debatespecific(debate_id):
    debate = get_database().execute("select title, id, date, irish_per from debates where id = ?", (debate_id,)).fetchone()
    speaker_list = get_database().execute("select distinct td, sentiment from contributions where debate_id = ?", (debate_id,)).fetchall()
    prob_dist = get_database().execute(f'select words, freq, prob from "{debate_id}"').fetchall()
    return render_template("debate.html", debate=debate, prob_dist=prob_dist, speaker_list=speaker_list)

@app.route("/debates/<int:debate_id>/speaker/<td_name>")
def debatespeaker(debate_id, td_name):
    debate = get_database().execute(
         "select title, id, date from debates where id = ?", (debate_id,)
    ).fetchone()
    contribution = get_database().execute(
        f'select td, contribution, sentiment from contributions where td = ?',
        (td_name,)
    ).fetchone()
    return render_template("speakercontribution.html", debate=debate, contribution=contribution)

@app.route("/debates/<int:debate_id>/text")
def debatetext(debate_id):
    debate = get_database().execute("select title, id, date, text from debates where id = ?", (debate_id,)).fetchone()
    return render_template("debatetext.html", debate=debate)

@app.route("/info")
def info():
    return render_template("info.html")

if __name__ == '__main__':
    app.run(debug=True)