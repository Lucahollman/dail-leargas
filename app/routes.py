from flask import render_template, request, jsonify
from flask import current_app as app
from . import get_database

def _build_sparkline_points(counts, width=220, height=40, padding=4):
    if not counts:
        return ""
    if len(counts) == 1:
        counts = counts * 2
    n = len(counts)
    max_c = max(counts)
    min_c = min(counts)
    range_c = (max_c - min_c) or 1
    step = (width - 2 * padding) / (n - 1)
    points = []
    for i, c in enumerate(counts):
        x = padding + i * step
        y = height - padding - ((c - min_c) / range_c) * (height - 2 * padding)
        points.append(f"{x:.1f},{y:.1f}")
    return " ".join(points)


@app.route("/")
def home():
    recent_debates = get_database().execute("""
        select debates.id, debates.title, debates.date, debates.category,
               count(contributions.rowid) as contribution_count
        from debates
        left join contributions on contributions.debate_id = debates.id
        group by debates.id
        order by debates.date desc
        limit 10
        """).fetchall()
    leaderboard = get_database().execute(
        """select id, name, party, constituency, irish_per
           from td_metadata
           where irish_per is not null
           order by irish_per desc"""
    ).fetchall()
    top_words = get_database().execute(
        "select words, freq from full_text order by freq desc limit 3"
    ).fetchall()
    word_trends = []
    for row in top_words:
        w = row["words"]
        history = get_database().execute(
            "select date, sum(frequency) as frequency from word_freq where word = ? group by date order by date",
            (w,)
        ).fetchall()
        counts = [h["frequency"] for h in history]
        word_trends.append({
            "word": w,
            "total": row["freq"],
            "points": _build_sparkline_points(counts)
        })
    return render_template(
        "home.html",
        recent_debates=recent_debates,
        leaderboard=leaderboard,
        word_trends=word_trends
    )

#Dáil Index Routes
@app.route("/overallstats")
def overallstats():
    stats = get_database().execute("select words, freq, prob from full_text").fetchall()
    irish_per = get_database().execute("select irish_per from fulltext_irishper").fetchone()["irish_per"]
    debates_num = get_database().execute("select count(id) from debates").fetchone()[0]
    words_num = get_database().execute("select sum(wordsnum) from debates").fetchone()[0]
    contributions_num = get_database().execute("select sum(contributionsnum) from debates").fetchone()[0]
    #labels for js chart
    words = [stat["words"] for stat in stats]
    freq = [stat["freq"] for stat in stats]
    prob = [stat["prob"] * 100 for stat in stats]
    return render_template("overallstats.html", full_text=stats, irish_per=irish_per, debates_num = debates_num, words_num = words_num, contributions_num = contributions_num, words=words, freq=freq, prob=prob)

@app.route("/tds")
def tds():
    tds = get_database().execute("select name, party, constituency, id from td_metadata order by name").fetchall()
    return render_template("tdindex.html", tds = tds)

@app.route("/tds/<int:id>")
def tdspecific(id):
    td = get_database().execute("select name, party, constituency, id, photo, sentiment, irish_per from td_metadata where id = ?", (id,)).fetchone()
    prob_dist = get_database().execute("select words, freq, prob from td_frequency_tables where name = ?", (td["name"],)).fetchall()
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
    prob_dist = get_database().execute("select words, freq, prob from party_freq_tables where name = ?", (party["party_name"],)).fetchall()
    #Labels for js chart
    words = [d["words"] for d in prob_dist]
    freq = [d["freq"] for d in prob_dist]
    return render_template("party.html", party = party, prob_dist = prob_dist, words = words, freq = freq)


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
    debates = get_database().execute(
        "select id, title, date, category from debates order by date desc, title"
    ).fetchall()
    categories = [
        row["category"]
        for row in get_database().execute("select distinct category from debates order by category").fetchall()]
    return render_template("debateindex.html", debates=debates, categories=categories)

@app.route("/debates/<int:debate_id>")
def debatespecific(debate_id):
    debate = get_database().execute("select title, id, date, irish_per from debates where id = ?", (debate_id,)).fetchone()
    speaker_list = get_database().execute("""
        select contributions.td,
               avg(contributions.sentiment) as average_sentiment,
               td_metadata.party,
               td_metadata.constituency,
               td_metadata.photo
        from contributions
        join td_metadata on contributions.td = td_metadata.name
        where contributions.debate_id = ?
            and contributions.td is not null
        group by contributions.td
        """,
        (debate_id,)
    ).fetchall()
    prob_dist = get_database().execute("select words, freq, prob from debate_frequency_tables where id = ?", (debate_id,)).fetchall()
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
        """select contributions.rowid as rowid, contributions.td, contributions.contribution, contributions.section_title, td_metadata.photo, td_metadata.id as td_id
           from contributions
           left join td_metadata on contributions.td = td_metadata.name
           where contributions.debate_id = ? 
           order by contributions.rowid""",
        (debate_id,)
    ).fetchall()
    distinct_sections = {c["section_title"] for c in contributions}
    show_headers = len(distinct_sections) > 1
    return render_template("debatetext.html", debate=debate, contributions=contributions, show_headers=show_headers)

@app.route("/info")
def info():
    return render_template("info.html")