import os
import time
from datetime import datetime

os.makedirs(f"outputs", exist_ok=True)

i = 0

while True:
    i += 1
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"outputs/news_{i}.json"
    
    print(f"=== SCRAPING YAHOO FINANCE ({timestamp}) ===")
    os.system(f"scrapy crawl yahoo_news -O {output_file}")
    
    print("Waiting 1 hour...")
    time.sleep(3600)  
