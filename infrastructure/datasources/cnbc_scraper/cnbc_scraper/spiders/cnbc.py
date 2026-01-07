import scrapy
from datetime import datetime

class CnbcSpider(scrapy.Spider):
    name = "cnbc"
    
    tickers = ["TSLA", "AAPL", "GOOGL", "MSFT", "AMZN", "NVDA", "META"]

    def start_requests(self):
        for ticker in self.tickers:
            # URL plus générique qui contient souvent plus de résultats mixtes
            url = f"https://www.cnbc.com/quotes/{ticker}?tab=news"
            yield scrapy.Request(url=url, callback=self.parse_list, meta={'ticker': ticker})

    def parse_list(self, response):
        ticker = response.meta['ticker']
        
        # 1. STRATÉGIE POUR TROUVER TOUS LES LIENS D'ARTICLES
        all_hrefs = response.css('a::attr(href)').getall()
        
        links_to_scrape = []
        
        # Pour le filtrage temporel
        current_year = str(datetime.now().year)
        last_year = str(datetime.now().year - 1)

        for link in all_hrefs:
            # Nettoyage URL
            if link.startswith("//"): link = "https:" + link
            elif link.startswith("/"): link = "https://www.cnbc.com" + link
            
            # 2. FILTRE TECHNIQUE (On garde les articles, on jette le reste)
            exclusions = ["/video/", "/pro/", "/select/", "/quotes/", "investingclub", "users/", "earnings-transcript"]
            if any(ex in link for ex in exclusions):
                continue
            
            # 3. FILTRE DE FRAÎCHEUR SOUPLE
            is_news = (
                f"/{current_year}/" in link or 
                f"/{last_year}/" in link or 
                "/investing/" in link or 
                "/tech/" in link or 
                "/business/" in link or
                "/markets/" in link
            )
            
            if is_news and len(link) > 50: # Un lien d'article est généralement long
                links_to_scrape.append(link)

        # On dédoublonne
        unique_links = list(set(links_to_scrape))
        
        target_links = unique_links[:20]
        
        self.logger.info(f"[{ticker}] 🔍 {len(target_links)} articles potentiels détectés.")

        for link in target_links:
            yield scrapy.Request(
                url=link, 
                callback=self.parse_article, 
                meta={'ticker': ticker},
                dont_filter=True 
            )

    def parse_article(self, response):
        ticker = response.meta['ticker']
        url = response.url
        
        # --- EXTRACTION ---
        # On essaie plusieurs endroits pour le titre
        title = response.css('h1.ArticleHeader-headline::text').get() or \
                response.css('h1.LiveBlogHeader-headline::text').get() or \
                response.css('h1::text').get()
        
        # On prend tout le texte possible
        paragraphs = response.css('.ArticleBody-articleBody p::text').getall() or \
                     response.css('.group p::text').getall() or \
                     response.css('article p::text').getall() or \
                     response.css('.RenderNodeWrapper p::text').getall()
                     
        full_text = " ".join(paragraphs).strip()
        
        # Date
        pub_time = response.css('time::attr(datetime)').get() or \
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- VALIDATION MINIMALE ---
        if not title or not full_text or len(full_text) < 100:
            self.logger.warning(f"[{ticker}] Contenu vide ou trop court : {url}")
            return

        title_lower = title.lower()

        # 1. FILTRE ANTI-BRUIT 
        blacklist = ["cramer", "mad money", "morning squawk", "5 things to know"]
        if any(bad in title_lower for bad in blacklist):
            return
        
        self.logger.info(f"[{ticker}] Récupéré : {title[:40]}...")
        
        yield {
            'company': ticker,
            'title': title.strip(),
            'link': url,
            'summary': full_text[:200] + "...",
            'full_text': full_text,
            'source': 'CNBC',
            'publisher': 'CNBC',
            'published_date': pub_time,
            'time': pub_time,
            'uuid': url + "_" + ticker
        }