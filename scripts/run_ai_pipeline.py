import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)

from database.mongo_manager import MongoManager
from ai.ai_summarizer import summarize_text

print("🚀 Démarrage du pipeline IA")

mongo = MongoManager()

articles = list(mongo.get_articles_without_summary(limit=300))
print("Nombre d'articles récupérés :", len(articles))

count = 0

for article in articles:
    title = article.get("title", "Sans titre")
    content = article.get("content") or article.get("text")

    print(f"🧠 Résumé en cours : {title}")

    if not content or len(content) < 100:
        print("⚠️ Contenu trop court — ignoré\n")
        continue

    try:
        summary = summarize_text(content)
        mongo.save_summary(article["_id"], summary)
        print("✅ Résumé sauvegardé\n")
        count += 1

    except Exception as e:
        print("❌ Erreur IA :", e)

print(f"🎉 Pipeline terminé — {count} articles résumés")


