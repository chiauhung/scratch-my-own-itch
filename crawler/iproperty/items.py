# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IpropertyItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    link = scrapy.Field()
    address = scrapy.Field()
    lat = scrapy.Field()
    lon = scrapy.Field()
    price = scrapy.Field()
    size = scrapy.Field()
    amenities = scrapy.Field()
    prize_range = scrapy.Field()
    tenure = scrapy.Field()
    pass
