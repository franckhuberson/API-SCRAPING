from pymongo import MongoClient
from datetime import datetime
from settings import MONGO_URI, DB_NAME, COLLECTION


class MongoManager:
    def __init__(self):
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        self.collection = self.db[COLLECTION]

    def get_articles_without_summary(self, limit=300):
        """
        Récupère les articles sans résumé
        """
        cursor = self.collection.find(
            {
                "$or": [
                    {"summary": {"$exists": False}},
                    {"summary": ""},
                    {"summary": None}
                ]
            },
            {
                "title": 1,
                "content": 1,
                "text": 1
            }
        )

        if limit:
            cursor = cursor.limit(limit)

        return cursor

    def save_summary(self, article_id, summary):
        """
        Sauvegarde le résumé généré par l'IA
        """
        result = self.collection.update_one(
            {"_id": article_id},
            {
                "$set": {
                    "summary": summary,
                    "summary_generated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count
