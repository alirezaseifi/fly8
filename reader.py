import feedparser
from datetime import datetime
from flask import Flask, request, Response, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from models import *
from config import Config

import os
import scrapy
from future import Future
import time
from time import mktime
from sqlalchemy.exc import IntegrityError
from instapy_cli import client
from celery import Celery
import re
from bs4 import BeautifulSoup
import requests
import base64



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)
db = SQLAlchemy(app)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['CELERY_IGNORE_RESULT'] = False

# This line is what I needed
app.config['CELERY_TRACK_STARTED'] = True


celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# db.create_all()

# RSS_FEEDS = {
#     'https://www.secretflying.com/posts/category/san-francisco/feed/',
#     'https://www.secretflying.com/posts/category/oakland/feed/',
#     # 'http://www.theflightdeal.com/category/flight-deals/SFO/feed/',
#     'https://www.fly4free.com/flights/flight-deals/usa/feed?s=san+francisco',
#     'https://airfarespot.com/category/north-america/san-francisco/feed/',
# }

def rss_feeds(departure_city):
    # geoname = requests.get('http://api.geonames.org/searchJSON?username=ksuhiyp&country=us&q=san francisco&maxRows=1')
    # if geoname.status_code == 200:
    #     geoname_id = geoname.json()['geonames'][0]['geonameId']
    return {
        "https://www.secretflying.com/posts/category/{0}/feed/".format(departure_city.replace(" ", "-")),
        "https://www.fly4free.com/flights/flight-deals/usa/feed?s={0}".format(departure_city.replace(" ", "+")),
        "https://airfarespot.com/category/north-america/{0}/feed/".format(departure_city.replace(" ", "-")),
        # "https://www.travelpirates.com/feed?filter[origin]={0}".format(geoname_id)
    }

KEY = 'BOOOOOOOOObabaKiramdahanet'
def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


@celery.task
def post_to_insta(entry, departure_city):
    # some long running task here
    username = 'flyfordeals'
    password = 'M136911m'
    pattern = r'\-*(\d+)x(\d+)\.(.*)$'
    replacement = r'.\3'
    print(entry)
    cookie_file = 'flyfordeals.json' # default: `USERNAME_ig.json`
    with client(username, password, cookie_file=cookie_file) as cli:
        no_ratio_image_url = re.sub(pattern, replacement, entry['media_content'][0]['url'])
        try:
            # cli.upload(no_ratio_image_url, entry["title"], story=True)
            cli.upload(no_ratio_image_url, entry["title"] + ' #{0} #flycheap #cheapflights #flyfordeals #flycheap #flymoreforless #vacation'.format(departure_city.replace(" ", "")))
        except IOError:
            pass

@app.template_filter()
def base64_encode(guid):
    return encode(KEY, guid)


@app.template_filter()
def remove_hrefs(text):
    soup = BeautifulSoup(text)
    for a in soup.findAll('a'):
        del a['href']
    return soup

@app.route("/", methods=['GET', 'POST'])
def default():
    return get_news()


# @app.route("/scrape")
def scrape(guid):
    booking_websites = ["momondo","priceline","skyscanner","google.com/flights/","kiwi",'cheapoair','jetblue.com','southwest.com','alaskaair.com','expedia']
    # start_urls = [r.url for r in Deal.query.filter_by(parsed_url=None).order_by(desc(Deal.created_at)).limit(2)]
    response  = requests.get(guid)
    data = response.text
    soup = BeautifulSoup(data)
    a_tag = []
    for link in soup.find_all('a'):
        if link.get('href') and any(booking_website in link.get('href') for booking_website in booking_websites):
            a_tag.append(str(link))
            # detail = Detail(deal.id,link.get('href'), link.contents[0],link)
            # db.session.add(detail)
            # db.session.commit()
            #print(link.get('href'))
    return a_tag

@app.route("/fetch")
def lists ():
    #Display the all Tasks
    os.system("scrapy crawl booking_crawler > booking_urls.csv")
    return 'ok'

@app.route("/list")
def deals ():
    #Display the all Tasks
    deals = Deal.query.order_by(Deal.pubdate.desc()).all()
    # booking_urls = BookingLink.squery.order_by(BookingLink.created_at.desc()).all()
    # for deal in deals:
    #     print(deal)
    return render_template("list.html", deals = deals)


@app.route("/detail/<deal_id>")
def detail(deal_id):
    #Display the all Tasks
    guid = decode(KEY, deal_id)
    deal = Deal.query.filter_by(guid= str(guid)).first()
    # details = Detail.query.filter_by(deal_id= deal_id).all()
    # # booking_urls = BookingLink.squery.order_by(BookingLink.created_at.desc()).all()
    # # for deal in deals:
    # #     print(deal)
    # print(details)
    return render_template("detail.html", links= scrape(guid), deal= deal)

# @app.route("/wired")
# def wired():
#   return get_news('wired')

# @app.route("/bbc")
# def bbc():
#   return get_news('bbc')

def get_news():
    # pull down all feeds
    departure_city = request.args.get('from')
    if departure_city is None:
        departure_city = 'san francisco'
    future_calls = [Future(feedparser.parse,rss_url) for rss_url in rss_feeds(departure_city)]
    # block until they are all in
    feeds = [future_obj() for future_obj in future_calls]

    entries = []
    for feed in feeds:
        entries.extend( feed[ "items" ] )


    for entry in entries:
        if Deal.query.filter_by(guid= entry["id"]).count() < 1:
            if 'media_content' in entry:
                task = post_to_insta.delay(entry, departure_city)
            deal = Deal(entry["id"], entry["title"], entry["summary"], entry["link"], datetime.fromtimestamp(mktime(entry["published_parsed"])))
            db.session.add(deal)
            db.session.commit()
    sorted_entries = sorted(entries,reverse=True, key=lambda entry: entry["published_parsed"])
    # print(sorted_entries) # for most recent entries firsts

    return render_template("home.html", articles=sorted_entries, departure_city=departure_city.title())

if __name__ == "__main__":
    app.run(port=5000, debug=True)
