# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class RymChart(Item):
    # define the fields for your item here like:
    title = Field()
    artists = Field()
    year = Field()
    genres = Field()
    average_rating = Field()
    number_ratings = Field()
    ranking = Field()