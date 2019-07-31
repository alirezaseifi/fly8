# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.spiders import BaseSpider
from scrapy.http import Request
from models import *
# from .flight_deals.model import *

# app.config.from_pyfile('../../../db.cfg')
# db = SQLAlchemy(app)


# DOMAIN = 'airfarespot.com/2019/03/14/san-francisco-to-reykjavik-iceland-from-443-round-trip/'
# URL = 'https://' +str(DOMAIN)
booking_websites = ["momondo","priceline","skyscanner"]

class WebsiteSpider(scrapy.Spider):
    name = "booking_crawler"
    # allowed_domains = [DOMAIN]
    # start_urls = [
    #     "https://www.fly4free.com/flight-deals/usa/cheap-fly-from-california-to-exotic-vanuatu-from-only-472/",
    # ]
    start_urls = [r.url for r in Deal.query.filter_by(parsed_url=None).all()]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        for url in hxs.select('//a/@href').extract():
            if any(booking_website in url for booking_website in booking_websites):
                print(url)
                if not ( url.startswith('http://') or url.startswith('https://') ):
                    url = URL + url
                deal = Deal.query.filter_by(url=response.request.url).first()
                # deal.parsed_url = url
                booking_url = BookingLink(deal.id, url)
                db.session.add(booking_url)
                db.session.commit()
                # print(url)
                yield Request(url, callback=self.parse)
