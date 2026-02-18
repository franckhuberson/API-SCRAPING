import requests
import certifi
from bs4 import BeautifulSoup
from newspaper import Article
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
import os
import time

# =====================
# CONFIGURATION
# =====================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsCAFile=certifi.where()
)
db = client["newspulse"]
collection = db["articles"]

# agent pour contourner les sites interdits par les robots

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SITES = [
    "https://www.abidjan.net/",
    "https://www.linfodrome.com/",
    "https://information.tv5monde.com/international",
    "https://www.rfi.fr/fr/afrique/"
]

# =====================
# FONCTIONS
# =====================

def get_article_links(site_url):
    """Récupère tous les liens d'articles d'une page"""
    links = set()

    try:
        response = requests.get(site_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if href.startswith("/"):
                href = site_url.rstrip("/") + href

            if href.startswith("http") and len(href) > 40:
                links.add(href)

    except Exception as e:
        print(f"❌ Site bloqué : {e}")

    return list(links)


def scrape_article(url):
    """Scrape un article individuel"""
    try:
        article = Article(url, language="fr")
        article.download()
        article.parse()

        if not article.text.strip():
            return None

        return {
            "url": url,
            "title": article.title,
            "text": article.text,
            "image_url": article.top_image,
            "created_at": datetime.utcnow()
        }

    except Exception as e:
        print(f"❌ Erreur article {url} : {e}")
        return None


# =====================
# PIPELINE PRINCIPAL
# =====================

print("✅ MongoDB connecté")
print("🚀 Lancement du scraping...\n")

for site in SITES:
    print(f"\n🔹 SITE : {site}")
    article_links = get_article_links(site)

    print(f"➡️ {len(article_links)} liens trouvés")

    for link in article_links:
        if collection.find_one({"url": link}):
            print("⏭️ Doublon ignoré")
            continue

        article_data = scrape_article(link)

        if article_data:
            collection.insert_one(article_data)
            print("✅ Article inséré")
            time.sleep(1)

print("\n🎉 Scraping terminé")
