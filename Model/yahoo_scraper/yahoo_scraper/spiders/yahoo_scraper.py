import scrapy
import yfinance as yf
from datetime import datetime

class YahooNewsSpider(scrapy.Spider):
    """
    Spider Scrapy qui utilise yfinance avec la VRAIE structure (2025).
    Les données sont imbriquées dans item['content']
    """
    name = "yahoo_scraper"
    
    # Tickers à surveiller
    tickers = ["TSLA", "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]
    
    def start_requests(self):
        """Point d'entrée du spider"""
        yield scrapy.Request(
            url="https://finance.yahoo.com",
            callback=self.parse_all_tickers,
            dont_filter=True,
            errback=self.handle_error
        )
    
    def parse_all_tickers(self, response):
        """Récupère les news pour tous les tickers via yfinance"""
        self.logger.info(f"Démarrage de la collecte pour {len(self.tickers)} tickers")
        
        total_articles = 0
        
        for ticker in self.tickers:
            try:
                self.logger.info(f"Traitement de {ticker}...")
                
                # Récupération via yfinance
                stock = yf.Ticker(ticker)
                news_items = stock.news
                
                if not news_items:
                    self.logger.warning(f"Aucune news pour {ticker}")
                    continue
                
                self.logger.info(f"Trouvé {len(news_items)} articles pour {ticker}")
                
                # Parse chaque article
                for item in news_items:
                    article = self.parse_news_item(item, ticker)
                    if article:
                        total_articles += 1
                        yield article
                
            except Exception as e:
                self.logger.error(f"Erreur pour {ticker}: {e}")
                continue
        
        self.logger.info(f"Collecte terminée: {total_articles} articles au total")
    
    def parse_news_item(self, item, ticker):
        """
        Parse un item de news yfinance.
        Structure 2025: les données sont dans item['content']
        """
        try:
            # IMPORTANT: Les données sont dans item['content']
            content = item.get("content", {})
            
            if not content:
                self.logger.warning(f"Article sans contenu pour {ticker}")
                return None
            
            # === EXTRACTION DES CHAMPS ===
            
            # Titre
            title = content.get("title", "")
            
            # Publisher/Provider
            provider = content.get("provider", {})
            publisher = provider.get("displayName", "") if isinstance(provider, dict) else ""
            
            # Link/URL
            canonical_url = content.get("canonicalUrl", {})
            link = canonical_url.get("url", "") if isinstance(canonical_url, dict) else ""
            
            # Summary
            summary = content.get("summary", "") or content.get("description", "")
            
            # Date de publication
            pub_date = content.get("pubDate")
            pub_time = None
            if pub_date:
                try:
                    # Format ISO: "2025-12-29T19:58:50Z"
                    dt = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                    pub_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except Exception as e:
                    self.logger.debug(f"Erreur parsing date: {e}")
                    pub_time = pub_date
            
            # UUID (ID au niveau racine)
            uuid = item.get("id", "") or content.get("id", "")
            
            # Thumbnail/Image
            image_url = ""
            thumbnail = content.get("thumbnail", {})
            if thumbnail and isinstance(thumbnail, dict):
                resolutions = thumbnail.get("resolutions", [])
                if resolutions:
                    # Prendre la meilleure résolution
                    best_res = max(resolutions, key=lambda x: x.get("width", 0))
                    image_url = best_res.get("url", "")
            
            # Validation: au moins un titre
            if not title:
                self.logger.warning(f"Article sans titre ignoré: {link}")
                return None
            
            # Construction de l'article
            article = {
                "company": ticker,
                "title": title,
                "publisher": publisher,
                "link": link,
                "summary": summary,
                "time": pub_time,
                "full_text": summary,  # Résumé comme texte complet
                "image_url": image_url,
                "uuid": uuid,
                "related_tickers": [],  # Pas disponible dans la nouvelle structure
            }
            
            return article
            
        except Exception as e:
            self.logger.error(f"Erreur lors du parsing d'un article: {e}", exc_info=True)
            return None
    
    def handle_error(self, failure):
        """Gestion des erreurs de requête"""
        self.logger.error(f"Erreur de requête: {failure.value}")