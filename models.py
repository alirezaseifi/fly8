from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from config import Config


app = Flask(__name__, static_folder="static")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)
db = SQLAlchemy(app)


class Deal(db.Model):
    id = db.Column('deal_id', db.Integer, primary_key=True)
    guid = db.Column(db.String, unique=True, nullable=False)
    title = db.Column(db.String(60))
    description = db.Column(db.String)
    url = db.Column(db.String)
    parsed_url = db.Column(db.String)
    pubdate = db.Column(db.DateTime)
    price = db.Column(db.String)
    origin = db.Column(db.String)
    to = db.Column(db.String)
    alliance = db.Column(db.String)
    airline = db.Column(db.String)
    instagram = db.Column(db.Boolean)
    scraped = db.Column(db.Boolean)
    source = db.Column(db.String)
    created_at = db.Column(db.DateTime)

    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.url = link
        self.pubdate = pubdate
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return '<Deal Guid %r>' % (self.guid)

class Detail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey(id))
    url = db.Column(db.String)
    url_text = db.Column(db.String)
    departure_on = db.Column(db.String)
    return_on = db.Column(db.String)
    a_tag = db.Column(db.Text)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

    def __init__(self, deal_id, url, url_text, a_tag):
        self.deal_id= deal_id
        self.url = str(url)
        self.url_text = str(url_text)
        self.a_tag = str(a_tag)
        self.created_at = datetime.utcnow()

    def __repr__(self):
        return '<Deal id %r>' % (self.deal_id)
