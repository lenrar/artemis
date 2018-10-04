# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PetFood(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    weight = scrapy.Field()
    cans = scrapy.Field()
    url = scrapy.Field()
    protein = scrapy.Field()
    fat = scrapy.Field()
    moisture = scrapy.Field()
    carbs = scrapy.Field()
    score = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    price_per_oz = scrapy.Field()
    pass
