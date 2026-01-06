import scrapy
from datetime import datetime

class CnbcSpider(scrapy.Spider):
    name = "cnbc"
    
    # Liste des tickers
    tickers = ["TSLA", "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'INFO'
    }

    def start_requests(self):
        for ticker in self.tickers:
            # On cible l'onglet News spécifique
            url = f"https://www.cnbc.com/quotes/{ticker}?tab=news"
            yield scrapy.Request(url=url, callback=self.parse_list, meta={'ticker': ticker, 'article_count': 0})

    def parse_list(self, response):
        ticker = response.meta['ticker']
        current_count = response.meta.get('article_count', 0)
        
        # OBJECTIF : Au moins 5 articles par entreprise
        MIN_ARTICLES = 5

        self.logger.info(f"[{ticker}] Recherche d'articles... (Actuel: {current_count})")

        # 1. On récupère TOUS les liens de la page
        all_links = response.css('a::attr(href)').getall()
        
        # Années pour filtrer (Année courante + 2 années précédentes pour être sûr d'avoir du volume)
        valid_years = [str(datetime.now().year), str(datetime.now().year - 1), str(datetime.now().year - 2)]
        
        links_to_scrape = []

        for link in all_links:
            # Nettoyage
            if link.startswith("//"): link = "https:" + link
            elif link.startswith("/"): link = "https://www.cnbc.com" + link
            
            # Filtres techniques
            if "/video/" in link or "/pro/" in link or "/select/" in link or "cnbc.com" not in link:
                continue

            # LOGIQUE DE SELECTION :
            # Si on a déjà 5 articles, on ne prend que les très récents (Année en cours)
            # Si on a MOINS de 5 articles, on prend tout ce qui contient une année valide (2024, 2025, 2026...)
            is_recent = any(year in link for year in valid_years)
            
            if is_recent:
                links_to_scrape.append(link)

        # On dédoublonne
        links_to_scrape = list(set(links_to_scrape))
        
        # Si on n'a rien trouvé avec les liens d'années, on prend les liens génériques de news
        if len(links_to_scrape) == 0:
             self.logger.warning(f"[{ticker}] Pas de liens datés trouvés, passage en mode large.")
             # Sélecteur de secours pour les news items
             links_to_scrape = response.css('.QuotePageTabs-newsItem a::attr(href)').getall()

        # On limite le nombre de requêtes pour ne pas spammer, mais on s'assure d'en avoir assez
        # On en prend un peu plus que le min pour compenser les échecs éventuels
        target_links = links_to_scrape[:MIN_ARTICLES + 5]

        if not target_links:
            self.logger.error(f"[{ticker}] AUCUN LIEN TROUVÉ. La structure de la page a peut-être changé.")
        
        for link in target_links:
            yield scrapy.Request(
                url=link, 
                callback=self.parse_article, 
                meta={'ticker': ticker},
                dont_filter=True 
            )

    def parse_article(self, response):
        ticker = response.meta['ticker']
        
        # Titre
        title = response.css('h1.ArticleHeader-headline::text').get() or \
                response.css('h1::text').get()
            
        # Texte
        paragraphs = response.css('.ArticleBody-articleBody p::text').getall()
        if not paragraphs:
            paragraphs = response.css('.group p::text').getall()
        
        full_text = " ".join(paragraphs).strip()
        
        # Date (Essentiel pour le tri plus tard)
        pub_time = response.css('time[itemprop="datePublished"]::attr(datetime)').get()
        if not pub_time:
             pub_time = response.css('time::text').get()

        if full_text and title:
            self.logger.info(f"[{ticker}] Article scrapé : {title[:30]}...")
            yield {
                'company': ticker,
                'title': title,
                'link': response.url,
                'summary': full_text[:200] + "...",
                'full_text': full_text,
                'publisher': 'CNBC',
                'time': pub_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'uuid': response.url + "_" + ticker
            }