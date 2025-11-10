# Scrapy settings for yahoo_scraper project

BOT_NAME = "yahoo_scraper"

SPIDER_MODULES = ["yahoo_scraper.spiders"]
NEWSPIDER_MODULE = "yahoo_scraper.spiders"

# Comme yfinance s’occupe de la récupération, inutile d’imiter un navigateur 
# On garde tout de même un user-agent pour cohérence
USER_AGENT = "Mozilla/5.0 (compatible; YahooNewsBot/1.0; +https://finance.yahoo.com/)"

# Pas besoin d’obéir à robots.txt, yfinance gère tout côté API
ROBOTSTXT_OBEY = False

# On désactive les middlewares réseau 
DOWNLOADER_MIDDLEWARES = {}

DOWNLOAD_DELAY = 0
AUTOTHROTTLE_ENABLED = False

# Paramètres Scrapy généraux 
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Logs plus propres 
LOG_LEVEL = "INFO"

# Limiter la concurrence pour éviter les blocages du côté yfinance 
CONCURRENT_REQUESTS = 2
