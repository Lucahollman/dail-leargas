from flask import render_template, request, jsonify
from flask import current_app as app
from . import get_database


@app.route("/")
def home():
    return render_template("home.html")

#Dáil Index Routes
@app.route("/overallstats")
def overallstats():
    stats = get_database().execute("select words, freq, prob from full_text").fetchall()
    irish_per = get_database().execute("select irish_per from fulltext_irishper").fetchone()["irish_per"]
    #labels for js chart
    words = [stat["words"] for stat in stats]
    freq = [stat["freq"] for stat in stats]
    prob = [stat["prob"] * 100 for stat in stats]
    return render_template("overallstats.html", full_text=stats, irish_per=irish_per, words=words, freq=freq, prob=prob)

@app.route("/tds")
def tds():
    tds = get_database().execute("select name, party, constituency, id from td_metadata").fetchall()
    return render_template("tdindex.html", tds = tds)

@app.route("/tds/<int:id>")
def tdspecific(id):
    td = get_database().execute("select name, party, constituency, id, photo, sentiment, irish_per from td_metadata where id = ?", (id,)).fetchone()
    prob_dist = get_database().execute(f'select words, freq, prob from "{td['name']}"').fetchall()
    contributions = get_database().execute(
    "select distinct contributions.debate_id, debates.title from contributions join debates on contributions.debate_id = debates.id where contributions.td = ?",
    (td["name"],)).fetchall()
    #labels for js chart
    words = [d["words"] for d in prob_dist]
    freq = [d["freq"] for d in prob_dist]
    return render_template("td.html", td = td, prob_dist = prob_dist, contributions = contributions, words = words, freq = freq)

@app.route("/parties")
def partyindex():
    parties = get_database().execute("select * from parties").fetchall()
    return render_template("partyindex.html", parties = parties)

@app.route("/parties/party/<party_name>")
def party(party_name):
    party = get_database().execute(
        "select * from parties where party_name = ?", [party_name]).fetchone()
    return render_template("party.html", party = party)


@app.route("/words")
def words():
    return render_template("wordindex.html")

@app.route("/words/<word>")
def word(word):
    word_data = get_database().execute("select date, sum(frequency) as frequency from word_freq where word = ? group by date order by date", (word,)).fetchall()
    word_counts = {d["date"]: d["frequency"] for d in word_data}
    all_dates = get_database().execute("select distinct date from contributions where date between ? and ? order by date", (min(word_counts.keys()), max(word_counts.keys()))).fetchall()
    dates = [d["date"] for d in all_dates]
    counts = [word_counts.get(date, 0) for date in dates]
    return render_template("word.html", word=word, dates=dates, counts=counts)

@app.route("/words/search")
def searchwords():
    userquery = request.args.get('q','')
    pattern = userquery + '%'
    search_result = get_database().execute("select distinct word from word_freq where word like ? limit 20", (pattern,)).fetchall()
    words = [row[0] for row in search_result]
    return jsonify(words)


    

@app.route("/debates")
def debates():
    debates = get_database().execute("select id, title, date, category from debates").fetchall()
    return render_template("debateindex.html", debates = debates)

@app.route("/debates/<int:debate_id>")
def debatespecific(debate_id):
    debate = get_database().execute("select title, id, date, irish_per from debates where id = ?", (debate_id,)).fetchone()
    speaker_list = get_database().execute("select  td, avg(sentiment) as average_sentiment  from contributions where debate_id = ? group by td", (debate_id,)).fetchall()
    prob_dist = get_database().execute(f'select words, freq, prob from "{debate_id}"').fetchall()
    #labels for js chart
    words = [d["words"] for d in prob_dist]
    freq = [d["freq"] for d in prob_dist]
    return render_template("debate.html", debate=debate, prob_dist=prob_dist, speaker_list=speaker_list, words=words, freq=freq)

@app.route("/debates/<int:debate_id>/speaker/<td_name>")
def debatespeaker(debate_id, td_name):
    debate = get_database().execute(
         "select title, id, date from debates where id = ?", (debate_id,)
    ).fetchone()
    contributions = get_database().execute(
        "select contributions.td, contributions.contribution, contributions.sentiment, td_metadata.id from contributions join td_metadata on contributions.td = td_metadata.name where contributions.td = ? and contributions.debate_id = ?",
        (td_name, debate_id)
    ).fetchall()
    average_sentiment = get_database().execute(
        "select avg(sentiment) as average_sentiment from contributions where td = ? and debate_id = ?",
        (td_name, debate_id)
    ).fetchone()["average_sentiment"]
    return render_template("speakercontribution.html", debate=debate, contributions=contributions, average_sentiment=average_sentiment)

@app.route("/debates/<int:debate_id>/text")
def debatetext(debate_id):
    debate = get_database().execute("select title, id, date, text from debates where id = ?", (debate_id,)).fetchone()
    contributions = get_database().execute(
        """select contributions.rowid as rowid, contributions.td, contributions.contribution, td_metadata.photo, td_metadata.id as td_id
           from contributions
           left join td_metadata on contributions.td = td_metadata.name
           where contributions.debate_id = ?
           order by contributions.rowid""",
        (debate_id,)
    ).fetchall()
    return render_template("debatetext.html", debate=debate, contributions=contributions)

@app.route("/info")
def info():
    return render_template("info.html")