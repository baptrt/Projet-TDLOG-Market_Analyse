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
                summary_data = item.get("summary") or item.get("content") or {}

                # Récupération sécurisée
                title = summary_data.get("title")
                publisher = summary_data.get("provider", {}).get("displayName") \
                            or summary_data.get("publisher")
                link = summary_data.get("canonicalUrl", {}).get("url") \
                    or summary_data.get("link")
                summary_text = summary_data.get("summary") \
                            or summary_data.get("description") \
                            or ""
                pub_date = summary_data.get("pubDate") or summary_data.get("providerPublishTime")

                # Conversion de date si nécessaire
                if pub_date:
                    try:
                        # pubDate peut être ISO ou timestamp Unix
                        if isinstance(pub_date, int):
                            pub_time = datetime.fromtimestamp(pub_date).strftime("%Y-%m-%d %H:%M:%S")
                        else:
                            pub_time = datetime.fromisoformat(pub_date.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        pub_time = None
                else:
                    pub_time = None

                yield {
                    "company": ticker,
                    "title": title,
                    "publisher": publisher,
                    "link": link,
                    "summary": summary_text,
                    "time": pub_time,
                }


        except Exception as e:
            self.logger.error(f"Erreur lors du traitement de {ticker} : {e}")
