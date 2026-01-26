# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YahooScraperItem(scrapy.Item):
    company = scrapy.Field()
    title = scrapy.Field()
    publisher = scrapy.Field()
    link = scrapy.Field()
    summary = scrapy.Field()
    time = scrapy.Field()
    full_text = scrapy.Field()
    uuid = scrapy.Field()
    image_url = scrapy.Field()
