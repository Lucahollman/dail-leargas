'''
File that generates filters used when rendering html
'''

from datetime import datetime, date
 

SENTIMENT_NEGATIVE_MAX = -0.06
SENTIMENT_POSITIVE_MIN = 0.06
 
 
def _parse_date(value):
    if isinstance(value, (datetime, date)):
        return value
    for fmt in ("%Y-%m-%d", "%d %b %Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None
 
 
def weekday_date(value):
    d = _parse_date(value)
    if d is None:
        return value  # couldn't parse, show original
    return d.strftime("%A, %d %B %Y")
 
 
def short_date(value):
    d = _parse_date(value)
    if d is None:
        return value
    return d.strftime("%a %d %b")


def card_date(value):
    d = _parse_date(value)
    if d is None:
        return value
    return d.strftime("%d %b %Y").lstrip("0")
 
 
def year_of(value):
    d = _parse_date(value)
    return d.year if d is not None else ""
  
def sentiment_stance(value):
    try:
        v = float(value)
    except (TypeError, ValueError):
        return {"label": "Unknown", "css_class": "stance-neutral"}
    if v <= SENTIMENT_NEGATIVE_MAX:
        return {"label": "Negative", "css_class": "stance-negative"}
    if v >= SENTIMENT_POSITIVE_MIN:
        return {"label": "Positive", "css_class": "stance-positive"}
    return {"label": "Neutral", "css_class": "stance-neutral"}
 
 
def filters(app):
    app.jinja_env.filters['weekday_date'] = weekday_date
    app.jinja_env.filters['short_date'] = short_date
    app.jinja_env.filters['card_date'] = card_date
    app.jinja_env.filters['year_of'] = year_of
    app.jinja_env.filters['sentiment_stance'] = sentiment_stance