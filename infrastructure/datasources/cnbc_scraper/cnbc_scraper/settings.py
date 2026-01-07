# settings.py

# 1. CONFIGURATION GÉNÉRALE 
BOT_NAME = "cnbc_scraper"
SPIDER_MODULES = ["cnbc_scraper.spiders"]
NEWSPIDER_MODULE = "cnbc_scraper.spiders"
LOG_LEVEL = "INFO"
FEED_EXPORT_ENCODING = "utf-8" 

# 2. IDENTITÉ DU ROBOT 
# User-Agent moderne (Chrome 120 sur Windows 10)
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
ROBOTSTXT_OBEY = False

# 3. VITESSE DE SCRAPING
DOWNLOAD_DELAY = 0.5