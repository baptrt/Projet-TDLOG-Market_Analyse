import scrapy
import yfinance as yf
import time
import random
from datetime import datetime

class YahooNewsSpider(scrapy.Spider):
    name = "yahoo_news"
    allowed_domains = ["finance.yahoo.com"]
    tickers = ["TSLA", "AAPL"]

    def start_requests(self):
        for ticker in self.tickers:
            yield scrapy.Request(
                url=f"https://finance.yahoo.com/quote/{ticker}/news",
                callback=self.parse_yfinance,
                cb_kwargs={"ticker": ticker},
                dont_filter=True,
            )

    def parse_yfinance(self, response, ticker):
        try:
            # Pause aléatoire entre les requêtes
            time.sleep(random.uniform(1.5, 3.0))

            data = yf.Ticker(ticker)
            news_items = getattr(data, "news", [])

            if not news_items:
                self.logger.warning(f"Aucune news trouvée pour {ticker}")
                return

            for item in news_items:
                # extraction sécurisée avec .get()
                title = item.get("title")
                publisher = item.get("publisher")
                link = item.get("link")
                summary = item.get("summary") or item.get("content", "")
                timestamp = item.get("providerPublishTime")

                # Conversion de la date si disponible
                if timestamp:
                    pub_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    pub_time = None

                yield {
                    "company": ticker,
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "summary": summary,
                    "time": pub_time,
                }

        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {ticker} : {e}")
