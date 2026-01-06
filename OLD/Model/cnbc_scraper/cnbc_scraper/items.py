import scrapy

class CnbcScraperItem(scrapy.Item):
    company = scrapy.Field()
    title = scrapy.Field()
    link = scrapy.Field()
    summary = scrapy.Field()
    full_text = scrapy.Field()
    time = scrapy.Field()
    publisher = scrapy.Field()
    uuid = scrapy.Field()